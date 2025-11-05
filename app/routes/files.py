"""
Rotas para gerenciamento de arquivos
"""
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId
from app.models.file_storage import FileStorage, FileType
from app.services import file_storage as storage_service
from app.core.security import get_current_user, require_admin
from app.core.logging import get_logger
from pathlib import Path

router = APIRouter(prefix="/files", tags=["Files"])
logger = get_logger(__name__)


# Schemas
class FileUploadResponse(BaseModel):
    """Resposta de upload de arquivo"""
    id: str
    filename: str
    original_name: str
    file_type: str
    size: int
    url: str
    expires_at: Optional[datetime] = None


class FileListResponse(BaseModel):
    """Resposta de listagem de arquivos"""
    total: int
    limit: int
    skip: int
    data: List[FileStorage]


class CleanupResponse(BaseModel):
    """Resposta de limpeza de arquivos"""
    deleted: int
    failed: Optional[int] = 0
    freed_mb: float


# 1️⃣ Upload de arquivo
@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    expires_in_days: Optional[int] = Query(None, description="Dias até expiração (None = usar padrão)"),
    is_public: bool = Query(False, description="Se o arquivo é público"),
    related_to: Optional[str] = Query(None, description="ID de recurso relacionado"),
    related_type: Optional[str] = Query(None, description="Tipo do recurso relacionado"),
    tags: Optional[str] = Query(None, description="Tags separadas por vírgula"),
    description: Optional[str] = Query(None, description="Descrição do arquivo"),
    current_user = Depends(get_current_user)
):
    """
    Upload de arquivo com validação e organização automática
    
    - **file**: Arquivo a ser enviado
    - **expires_in_days**: Dias até expiração automática (opcional)
    - **is_public**: Se o arquivo pode ser acessado publicamente
    - **related_to**: ID de oferta, post ou outro recurso relacionado
    - **related_type**: Tipo do recurso (offer, post, etc)
    - **tags**: Tags para organização (ex: "produto,imagem,destaque")
    - **description**: Descrição do arquivo
    
    **Limites:**
    - Tamanho máximo: 10MB (configurável)
    - Extensões permitidas: jpg, jpeg, png, gif, pdf, doc, docx, xls, xlsx, txt, mp4, mp3
    """
    try:
        # Processar tags
        tags_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        # Salvar arquivo
        file_storage = await storage_service.save_upload_file(
            file=file,
            uploaded_by=str(current_user.id),
            expires_in_days=expires_in_days,
            is_public=is_public,
            related_to=related_to,
            related_type=related_type,
            tags=tags_list,
            description=description
        )
        
        logger.info(
            "file_uploaded",
            file_id=str(file_storage.id),
            user_id=str(current_user.id),
            filename=file_storage.filename
        )
        
        return FileUploadResponse(
            id=str(file_storage.id),
            filename=file_storage.filename,
            original_name=file_storage.original_name,
            file_type=file_storage.file_type.value,
            size=file_storage.size,
            url=file_storage.get_url("/api"),
            expires_at=file_storage.expires_at
        )
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error("file_upload_failed", error=str(e))
        raise HTTPException(500, f"Erro ao fazer upload: {str(e)}")


# 2️⃣ Listar arquivos
@router.get("/", response_model=FileListResponse)
async def list_files(
    file_type: Optional[FileType] = Query(None, description="Filtrar por tipo"),
    uploaded_by: Optional[str] = Query(None, description="Filtrar por usuário"),
    related_to: Optional[str] = Query(None, description="Filtrar por recurso relacionado"),
    is_public: Optional[bool] = Query(None, description="Filtrar por públicos/privados"),
    tags: Optional[str] = Query(None, description="Filtrar por tags (separadas por vírgula)"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user = Depends(get_current_user)
):
    """
    Lista arquivos com filtros opcionais
    
    - **file_type**: Filtrar por tipo (image, document, video, audio, other)
    - **uploaded_by**: ID do usuário que fez upload
    - **related_to**: ID do recurso relacionado
    - **is_public**: true = públicos, false = privados
    - **tags**: Tags para filtrar (ex: "produto,imagem")
    - **limit**: Máximo de resultados
    - **skip**: Pular N resultados
    """
    try:
        query = {}
        
        # Filtros
        if file_type:
            query["file_type"] = file_type
        
        if uploaded_by:
            query["uploaded_by"] = uploaded_by
        
        if related_to:
            query["related_to"] = related_to
        
        if is_public is not None:
            query["is_public"] = is_public
        
        # Filtro por tags
        if tags:
            tags_list = [tag.strip() for tag in tags.split(",")]
            query["tags"] = {"$in": tags_list}
        
        # Se não for admin, só mostrar arquivos próprios ou públicos
        user_role = current_user.role
        if user_role != "admin":
            query["$or"] = [
                {"uploaded_by": str(current_user.id)},
                {"is_public": True}
            ]
        
        # Buscar arquivos
        files = await FileStorage.find(query).skip(skip).limit(limit).to_list()
        total = await FileStorage.find(query).count()
        
        return FileListResponse(
            total=total,
            limit=limit,
            skip=skip,
            data=files
        )
        
    except Exception as e:
        logger.error("file_list_failed", error=str(e))
        raise HTTPException(500, f"Erro ao listar arquivos: {str(e)}")


# 3️⃣ Buscar arquivo por ID
@router.get("/{file_id}", response_model=FileStorage)
async def get_file(
    file_id: PydanticObjectId,
    current_user = Depends(get_current_user)
):
    """Busca informações de um arquivo específico"""
    try:
        file_storage = await FileStorage.get(file_id)
        
        if not file_storage:
            raise HTTPException(404, "Arquivo não encontrado")
        
        # Verificar permissão
        user_role = current_user.role
        user_id = str(current_user.id)
        
        if not file_storage.is_public:
            if user_role != "admin" and file_storage.uploaded_by != user_id:
                raise HTTPException(403, "Acesso negado")
        
        # Verificar se expirou
        if file_storage.is_expired():
            raise HTTPException(410, "Arquivo expirado")
        
        return file_storage
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("file_get_failed", error=str(e), file_id=str(file_id))
        raise HTTPException(500, f"Erro ao buscar arquivo: {str(e)}")


# 4️⃣ Download de arquivo
@router.get("/{file_id}/download")
async def download_file(
    file_id: PydanticObjectId,
    current_user = Depends(get_current_user)
):
    """
    Faz download de um arquivo
    
    - Incrementa contador de downloads
    - Atualiza data de último acesso
    - Verifica permissões e expiração
    """
    try:
        file_storage = await FileStorage.get(file_id)
        
        if not file_storage:
            raise HTTPException(404, "Arquivo não encontrado")
        
        # Verificar permissão
        user_role = current_user.role
        user_id = str(current_user.id)
        
        if not file_storage.is_public:
            if user_role != "admin" and file_storage.uploaded_by != user_id:
                raise HTTPException(403, "Acesso negado")
        
        # Verificar se expirou
        if file_storage.is_expired():
            raise HTTPException(410, "Arquivo expirado")
        
        # Verificar se arquivo existe fisicamente
        file_path = Path(file_storage.full_path)
        if not file_path.exists():
            logger.error("physical_file_not_found", file_id=str(file_id), path=str(file_path))
            raise HTTPException(404, "Arquivo físico não encontrado")
        
        # Incrementar contador e atualizar último acesso
        file_storage.increment_download()
        await file_storage.save()
        
        logger.info(
            "file_downloaded",
            file_id=str(file_id),
            user_id=user_id,
            download_count=file_storage.download_count
        )
        
        # Retornar arquivo
        return FileResponse(
            path=file_path,
            filename=file_storage.original_name,
            media_type=file_storage.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("file_download_failed", error=str(e), file_id=str(file_id))
        raise HTTPException(500, f"Erro ao baixar arquivo: {str(e)}")


# 5️⃣ Deletar arquivo
@router.delete("/{file_id}")
async def delete_file_endpoint(
    file_id: PydanticObjectId,
    current_user = Depends(get_current_user)
):
    """
    Deleta um arquivo (física e registro)
    
    - Usuários podem deletar seus próprios arquivos
    - Admins podem deletar qualquer arquivo
    """
    try:
        file_storage = await FileStorage.get(file_id)
        
        if not file_storage:
            raise HTTPException(404, "Arquivo não encontrado")
        
        # Verificar permissão
        user_role = current_user.role
        user_id = str(current_user.id)
        
        if user_role != "admin" and file_storage.uploaded_by != user_id:
            raise HTTPException(403, "Você só pode deletar seus próprios arquivos")
        
        # Deletar
        await storage_service.delete_file(file_storage)
        
        logger.info(
            "file_deleted",
            file_id=str(file_id),
            user_id=user_id
        )
        
        return {
            "status": "success",
            "message": "Arquivo deletado com sucesso",
            "file_id": str(file_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("file_delete_failed", error=str(e), file_id=str(file_id))
        raise HTTPException(500, f"Erro ao deletar arquivo: {str(e)}")


# 6️⃣ Limpeza de arquivos expirados (admin)
@router.post("/cleanup/expired", response_model=CleanupResponse)
async def cleanup_expired(admin = Depends(require_admin)):
    """
    Remove arquivos expirados do sistema (requer admin)
    
    - Deleta arquivos físicos e registros
    - Retorna estatísticas da limpeza
    """
    try:
        result = await storage_service.cleanup_expired_files()
        
        logger.info(
            "cleanup_expired_executed",
            admin_id=admin.get("user_id"),
            deleted=result["deleted"]
        )
        
        return CleanupResponse(**result)
        
    except Exception as e:
        logger.error("cleanup_expired_failed", error=str(e))
        raise HTTPException(500, f"Erro na limpeza: {str(e)}")


# 7️⃣ Limpeza de arquivos órfãos (admin)
@router.post("/cleanup/orphans", response_model=CleanupResponse)
async def cleanup_orphans(admin = Depends(require_admin)):
    """
    Remove arquivos físicos sem registro no banco (requer admin)
    
    - Varre diretório de uploads
    - Remove arquivos sem correspondência no banco
    """
    try:
        result = await storage_service.cleanup_orphan_files()
        
        logger.info(
            "cleanup_orphans_executed",
            admin_id=admin.get("user_id"),
            deleted=result["deleted"]
        )
        
        return CleanupResponse(**result)
        
    except Exception as e:
        logger.error("cleanup_orphans_failed", error=str(e))
        raise HTTPException(500, f"Erro na limpeza: {str(e)}")


# 8️⃣ Estatísticas de armazenamento (admin)
@router.get("/stats/storage")
async def storage_stats(admin = Depends(require_admin)):
    """
    Retorna estatísticas do armazenamento (requer admin)
    
    - Total de arquivos
    - Espaço utilizado
    - Diretório de uploads
    """
    try:
        stats = storage_service.get_storage_stats()
        
        # Adicionar estatísticas do banco
        total_db = await FileStorage.count()
        by_type = {}
        
        for file_type in FileType:
            count = await FileStorage.find(FileStorage.file_type == file_type).count()
            by_type[file_type.value] = count
        
        stats["total_db_records"] = total_db
        stats["by_type"] = by_type
        
        return stats
        
    except Exception as e:
        logger.error("storage_stats_failed", error=str(e))
        raise HTTPException(500, f"Erro ao obter estatísticas: {str(e)}")


# 9️⃣ Health check
@router.get("/health/check")
def health_check():
    """Verifica se o serviço de arquivos está operacional"""
    upload_dir = storage_service.get_upload_path()
    return {
        "status": "ok",
        "upload_dir": str(upload_dir),
        "upload_dir_exists": upload_dir.exists(),
        "upload_dir_writable": os.access(upload_dir, os.W_OK)
    }
