from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId
from app.models.channel import Channel
from app.core.security import require_moderator, require_admin

router = APIRouter(prefix="/channels", tags=["Channels"])

class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    type: str = Field(..., description="telegram | whatsapp | instagram | site | email | discord")
    description: Optional[str] = None
    api_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    webhook_url: Optional[str] = None
    channel_id: Optional[str] = None
    phone_number: Optional[str] = None
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    priority: int = Field(default=0)

class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=50)
    type: Optional[str] = None
    description: Optional[str] = None
    api_token: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    webhook_url: Optional[str] = None
    channel_id: Optional[str] = None
    phone_number: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

# 1️⃣ Criar canal (requer moderador)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_channel(data: ChannelCreate, moderator = Depends(require_moderator)):
    """Cria um novo canal de publicação (requer permissão de moderador)"""
    try:
        # Verificar se slug já existe
        existing = await Channel.get_by_slug(data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug já existe"
            )
        
        channel = Channel(
            name=data.name,
            slug=data.slug.lower(),
            type=data.type.lower(),
            description=data.description,
            api_token=data.api_token,
            api_key=data.api_key,
            api_secret=data.api_secret,
            webhook_url=data.webhook_url,
            channel_id=data.channel_id,
            phone_number=data.phone_number,
            config=data.config,
            priority=data.priority,
            is_active=True,
            total_posts=0,
            success_rate=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await channel.insert()
        
        return {
            "status": "success",
            "message": "Canal criado com sucesso",
            "id": str(channel.id),
            "data": channel
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar canal: {str(e)}"
        )

# 2️⃣ Listar canais
@router.get("/")
async def list_channels(
    type: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 50,
    skip: int = 0
):
    """Lista todos os canais com filtros opcionais"""
    try:
        query = {}
        if type:
            query["type"] = type.lower()
        if is_active is not None:
            query["is_active"] = is_active
        
        channels = await Channel.find(query).sort("-priority").skip(skip).limit(limit).to_list()
        total = await Channel.find(query).count()
        
        return {
            "total": total,
            "limit": limit,
            "skip": skip,
            "data": channels
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar canais: {str(e)}"
        )

# 3️⃣ Listar apenas canais ativos
@router.get("/active")
async def list_active_channels():
    """Lista apenas canais ativos ordenados por prioridade"""
    try:
        channels = await Channel.get_active_channels()
        return {
            "total": len(channels),
            "data": channels
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar canais ativos: {str(e)}"
        )

# 4️⃣ Buscar canal por ID
@router.get("/{channel_id}")
async def get_channel(channel_id: PydanticObjectId):
    """Busca um canal específico por ID"""
    try:
        channel = await Channel.get(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canal não encontrado"
            )
        return channel
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar canal: {str(e)}"
        )

# 5️⃣ Buscar canal por slug
@router.get("/slug/{slug}")
async def get_channel_by_slug(slug: str):
    """Busca um canal por slug"""
    try:
        channel = await Channel.get_by_slug(slug.lower())
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canal não encontrado"
            )
        return channel
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar canal: {str(e)}"
        )

# 4️⃣ Atualizar canal (requer moderador)
@router.put("/{channel_id}")
async def update_channel(channel_id: PydanticObjectId, data: ChannelUpdate, moderator = Depends(require_moderator)):
    """Atualiza um canal existente (requer permissão de moderador)"""
    try:
        channel = await Channel.get(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canal não encontrado"
            )
        
        update_data = data.dict(exclude_unset=True)
        
        # Verificar slug único se estiver sendo alterado
        if "slug" in update_data and update_data["slug"] != channel.slug:
            existing = await Channel.get_by_slug(update_data["slug"].lower())
            if existing and str(existing.id) != str(channel_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Slug já está em uso"
                )
            update_data["slug"] = update_data["slug"].lower()
        
        if "type" in update_data:
            update_data["type"] = update_data["type"].lower()
        
        update_data["updated_at"] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(channel, key, value)
        
        await channel.save()
        
        return {
            "status": "success",
            "message": "Canal atualizado com sucesso",
            "data": channel
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar canal: {str(e)}"
        )

# 5️⃣ Excluir canal (requer admin)
@router.delete("/{channel_id}")
async def delete_channel(channel_id: PydanticObjectId, admin = Depends(require_admin)):
    """Remove um canal do sistema (requer permissão de admin)"""
    try:
        channel = await Channel.get(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canal não encontrado"
            )
        
        await channel.delete()
        
        return {
            "status": "success",
            "message": "Canal excluído com sucesso",
            "id": str(channel_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir canal: {str(e)}"
        )

# 6️⃣ Ativar/Desativar canal (requer admin)
@router.patch("/{channel_id}/toggle-active")
async def toggle_channel_active(channel_id: PydanticObjectId, admin = Depends(require_admin)):
    """Ativa ou desativa um canal (requer permissão de admin)"""
    try:
        channel = await Channel.get(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canal não encontrado"
            )
        
        channel.is_active = not channel.is_active
        channel.updated_at = datetime.utcnow()
        await channel.save()
        
        return {
            "status": "success",
            "message": f"Canal {'ativado' if channel.is_active else 'desativado'} com sucesso",
            "is_active": channel.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar status do canal: {str(e)}"
        )

# 9️⃣ Atualizar estatísticas do canal
@router.patch("/{channel_id}/stats")
async def update_channel_stats(
    channel_id: PydanticObjectId,
    total_posts: Optional[int] = None,
    success_rate: Optional[float] = None
):
    """Atualiza estatísticas de um canal (usado por integrações)"""
    try:
        channel = await Channel.get(channel_id)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Canal não encontrado"
            )
        
        if total_posts is not None:
            channel.total_posts = total_posts
        if success_rate is not None:
            channel.success_rate = min(100.0, max(0.0, success_rate))
        
        channel.last_post_at = datetime.utcnow()
        channel.updated_at = datetime.utcnow()
        await channel.save()
        
        return {
            "status": "success",
            "message": "Estatísticas atualizadas com sucesso",
            "data": {
                "total_posts": channel.total_posts,
                "success_rate": channel.success_rate,
                "last_post_at": channel.last_post_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar estatísticas: {str(e)}"
        )
