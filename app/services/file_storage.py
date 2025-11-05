"""
Serviço para gerenciamento de armazenamento de arquivos
"""
import os
import hashlib
import uuid
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, BinaryIO, List
from fastapi import UploadFile
from app.models.file_storage import FileStorage, FileType
from app.core.logging import get_logger

logger = get_logger(__name__)

# Configurações
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB padrão
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx,txt,mp4,mp3").split(",")
DEFAULT_EXPIRY_DAYS = int(os.getenv("FILE_EXPIRY_DAYS", 30))  # 30 dias padrão


def get_upload_path() -> Path:
    """Retorna o diretório base de uploads"""
    path = Path(UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_unique_filename(original_filename: str) -> str:
    """Gera nome único para arquivo mantendo extensão"""
    ext = Path(original_filename).suffix
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{ext}"


def get_organized_path(file_type: FileType) -> Path:
    """
    Cria estrutura organizada por tipo e data
    Exemplo: uploads/images/2024/11/04/
    """
    now = datetime.utcnow()
    base = get_upload_path()
    
    # Organizar por tipo
    type_folder = f"{file_type.value}s" if file_type != FileType.OTHER else "other"
    
    # Organizar por data (ano/mês/dia)
    organized_path = base / type_folder / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
    organized_path.mkdir(parents=True, exist_ok=True)
    
    return organized_path


def calculate_checksum(file_path: Path) -> str:
    """Calcula MD5 checksum do arquivo"""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def validate_file_size(file: UploadFile) -> tuple[bool, Optional[str]]:
    """Valida tamanho do arquivo"""
    # Pegar tamanho do arquivo
    file.file.seek(0, 2)  # Ir para o final
    size = file.file.tell()
    file.file.seek(0)  # Voltar para o início
    
    if size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"Arquivo excede tamanho máximo de {max_mb:.1f}MB"
    
    if size == 0:
        return False, "Arquivo vazio"
    
    return True, None


def validate_file_extension(filename: str) -> tuple[bool, Optional[str]]:
    """Valida extensão do arquivo"""
    ext = Path(filename).suffix.lower().lstrip('.')
    
    if not ext:
        return False, "Arquivo sem extensão"
    
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Extensão '{ext}' não permitida. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, None


async def save_upload_file(
    file: UploadFile,
    uploaded_by: Optional[str] = None,
    expires_in_days: Optional[int] = None,
    is_public: bool = False,
    related_to: Optional[str] = None,
    related_type: Optional[str] = None,
    tags: List[str] = None,
    description: Optional[str] = None
) -> FileStorage:
    """
    Salva arquivo enviado e cria registro no banco
    
    Args:
        file: Arquivo enviado via FastAPI
        uploaded_by: ID do usuário que fez upload
        expires_in_days: Dias até expiração (None = nunca expira)
        is_public: Se arquivo é público
        related_to: ID de recurso relacionado
        related_type: Tipo do recurso relacionado
        tags: Tags para organização
        description: Descrição do arquivo
    
    Returns:
        FileStorage: Registro do arquivo salvo
    """
    try:
        # Validações
        is_valid, error = validate_file_extension(file.filename)
        if not is_valid:
            raise ValueError(error)
        
        is_valid, error = validate_file_size(file)
        if not is_valid:
            raise ValueError(error)
        
        # Determinar tipo de arquivo
        mime_type = file.content_type or "application/octet-stream"
        file_type = FileStorage.get_file_type_from_mime(mime_type)
        
        # Gerar nome único e path organizado
        unique_filename = generate_unique_filename(file.filename)
        organized_dir = get_organized_path(file_type)
        full_path = organized_dir / unique_filename
        
        # Salvar arquivo
        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info("file_saved", filename=unique_filename, size=full_path.stat().st_size)
        
        # Calcular checksum
        checksum = calculate_checksum(full_path)
        
        # Calcular data de expiração
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        elif DEFAULT_EXPIRY_DAYS > 0:
            expires_at = datetime.utcnow() + timedelta(days=DEFAULT_EXPIRY_DAYS)
        
        # Criar registro no banco
        file_storage = FileStorage(
            filename=unique_filename,
            original_name=file.filename,
            file_type=file_type,
            mime_type=mime_type,
            path=str(full_path.relative_to(get_upload_path())),
            full_path=str(full_path.absolute()),
            size=full_path.stat().st_size,
            checksum=checksum,
            uploaded_by=uploaded_by,
            expires_at=expires_at,
            is_public=is_public,
            related_to=related_to,
            related_type=related_type,
            tags=tags or [],
            description=description
        )
        
        await file_storage.insert()
        logger.info("file_record_created", file_id=str(file_storage.id))
        
        return file_storage
        
    except Exception as e:
        logger.error("file_save_failed", error=str(e))
        # Limpar arquivo se foi salvo mas falhou no banco
        if full_path and full_path.exists():
            full_path.unlink()
        raise


async def delete_file(file_storage: FileStorage) -> bool:
    """
    Deleta arquivo do sistema e registro do banco
    
    Args:
        file_storage: Registro do arquivo
    
    Returns:
        bool: True se deletado com sucesso
    """
    try:
        # Deletar arquivo físico
        file_path = Path(file_storage.full_path)
        if file_path.exists():
            file_path.unlink()
            logger.info("file_deleted", filename=file_storage.filename)
        else:
            logger.warning("file_not_found", path=str(file_path))
        
        # Deletar registro do banco
        await file_storage.delete()
        logger.info("file_record_deleted", file_id=str(file_storage.id))
        
        return True
        
    except Exception as e:
        logger.error("file_delete_failed", error=str(e), file_id=str(file_storage.id))
        raise


async def cleanup_expired_files() -> dict:
    """
    Remove arquivos expirados do sistema
    
    Returns:
        dict: Estatísticas da limpeza
    """
    try:
        now = datetime.utcnow()
        
        # Buscar arquivos expirados
        expired_files = await FileStorage.find(
            FileStorage.expires_at <= now
        ).to_list()
        
        deleted_count = 0
        failed_count = 0
        freed_bytes = 0
        
        for file_storage in expired_files:
            try:
                freed_bytes += file_storage.size
                await delete_file(file_storage)
                deleted_count += 1
            except Exception as e:
                logger.error("cleanup_file_failed", file_id=str(file_storage.id), error=str(e))
                failed_count += 1
        
        logger.info(
            "cleanup_completed",
            deleted=deleted_count,
            failed=failed_count,
            freed_mb=round(freed_bytes / (1024 * 1024), 2)
        )
        
        return {
            "deleted": deleted_count,
            "failed": failed_count,
            "freed_bytes": freed_bytes,
            "freed_mb": round(freed_bytes / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error("cleanup_failed", error=str(e))
        raise


async def cleanup_orphan_files() -> dict:
    """
    Remove arquivos físicos sem registro no banco
    
    Returns:
        dict: Estatísticas da limpeza
    """
    try:
        upload_dir = get_upload_path()
        deleted_count = 0
        freed_bytes = 0
        
        # Listar todos os arquivos físicos
        for file_path in upload_dir.rglob("*"):
            if file_path.is_file():
                # Verificar se existe no banco
                filename = file_path.name
                file_record = await FileStorage.find_one(FileStorage.filename == filename)
                
                if not file_record:
                    # Arquivo órfão
                    size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    freed_bytes += size
                    logger.info("orphan_file_deleted", filename=filename)
        
        logger.info(
            "orphan_cleanup_completed",
            deleted=deleted_count,
            freed_mb=round(freed_bytes / (1024 * 1024), 2)
        )
        
        return {
            "deleted": deleted_count,
            "freed_bytes": freed_bytes,
            "freed_mb": round(freed_bytes / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error("orphan_cleanup_failed", error=str(e))
        raise


def get_storage_stats() -> dict:
    """Retorna estatísticas do armazenamento"""
    try:
        upload_dir = get_upload_path()
        total_size = 0
        file_count = 0
        
        for file_path in upload_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        return {
            "total_files": file_count,
            "total_bytes": total_size,
            "total_mb": round(total_size / (1024 * 1024), 2),
            "total_gb": round(total_size / (1024 * 1024 * 1024), 2),
            "upload_dir": str(upload_dir.absolute())
        }
        
    except Exception as e:
        logger.error("storage_stats_failed", error=str(e))
        return {}
