from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId
from app.models.affiliate import Affiliate
from app.core.security import require_moderator, require_admin

router = APIRouter(prefix="/affiliates", tags=["Affiliates"])

class AffiliateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    url: HttpUrl
    logo: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    affiliate_id: Optional[str] = None
    description: Optional[str] = None
    terms_url: Optional[str] = None
    priority: int = Field(default=0)

class AffiliateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=50)
    url: Optional[HttpUrl] = None
    logo: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    affiliate_id: Optional[str] = None
    description: Optional[str] = None
    terms_url: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

# 1️⃣ Criar afiliado (requer moderador)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_affiliate(data: AffiliateCreate, moderator = Depends(require_moderator)):
    """Cria um novo site afiliado (requer permissão de moderador)"""
    try:
        # Verificar se slug já existe
        existing = await Affiliate.get_by_slug(data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug já existe"
            )
        
        affiliate = Affiliate(
            name=data.name,
            slug=data.slug.lower(),
            url=str(data.url),
            logo=data.logo,
            api_key=data.api_key,
            api_secret=data.api_secret,
            commission_rate=data.commission_rate,
            affiliate_id=data.affiliate_id,
            description=data.description,
            terms_url=data.terms_url,
            priority=data.priority,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await affiliate.insert()
        
        return {
            "status": "success",
            "message": "Afiliado criado com sucesso",
            "id": str(affiliate.id),
            "data": affiliate
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar afiliado: {str(e)}"
        )

# 2️⃣ Listar afiliados
@router.get("/")
async def list_affiliates(
    is_active: Optional[bool] = None,
    limit: int = 50,
    skip: int = 0
):
    """Lista todos os afiliados com filtros opcionais"""
    try:
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        affiliates = await Affiliate.find(query).sort("-priority").skip(skip).limit(limit).to_list()
        total = await Affiliate.find(query).count()
        
        return {
            "total": total,
            "limit": limit,
            "skip": skip,
            "data": affiliates
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar afiliados: {str(e)}"
        )

# 3️⃣ Buscar afiliado por ID
@router.get("/{affiliate_id}")
async def get_affiliate(affiliate_id: PydanticObjectId):
    """Busca um afiliado específico por ID"""
    try:
        affiliate = await Affiliate.get(affiliate_id)
        if not affiliate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Afiliado não encontrado"
            )
        return affiliate
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar afiliado: {str(e)}"
        )

# 4️⃣ Buscar afiliado por slug
@router.get("/slug/{slug}")
async def get_affiliate_by_slug(slug: str):
    """Busca um afiliado por slug"""
    try:
        affiliate = await Affiliate.get_by_slug(slug.lower())
        if not affiliate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Afiliado não encontrado"
            )
        return affiliate
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar afiliado: {str(e)}"
        )

# 4️⃣ Atualizar afiliado (requer moderador)
@router.put("/{affiliate_id}")
async def update_affiliate(affiliate_id: PydanticObjectId, data: AffiliateUpdate, moderator = Depends(require_moderator)):
    """Atualiza um afiliado existente (requer permissão de moderador)"""
    try:
        affiliate = await Affiliate.get(affiliate_id)
        if not affiliate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Afiliado não encontrado"
            )
        
        update_data = data.dict(exclude_unset=True)
        
        # Verificar slug único se estiver sendo alterado
        if "slug" in update_data and update_data["slug"] != affiliate.slug:
            existing = await Affiliate.get_by_slug(update_data["slug"].lower())
            if existing and str(existing.id) != str(affiliate_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Slug já está em uso"
                )
            update_data["slug"] = update_data["slug"].lower()
        
        update_data["updated_at"] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(affiliate, key, value)
        
        await affiliate.save()
        
        return {
            "status": "success",
            "message": "Afiliado atualizado com sucesso",
            "data": affiliate
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar afiliado: {str(e)}"
        )

# 5️⃣ Excluir afiliado (requer admin)
@router.delete("/{affiliate_id}")
async def delete_affiliate(affiliate_id: PydanticObjectId, admin = Depends(require_admin)):
    """Remove um afiliado do sistema (requer permissão de admin)"""
    try:
        affiliate = await Affiliate.get(affiliate_id)
        if not affiliate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Afiliado não encontrado"
            )
        
        await affiliate.delete()
        
        return {
            "status": "success",
            "message": "Afiliado excluído com sucesso",
            "id": str(affiliate_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir afiliado: {str(e)}"
        )

# 6️⃣ Ativar/Desativar afiliado (requer admin)
@router.patch("/{affiliate_id}/toggle-active")
async def toggle_affiliate_active(affiliate_id: PydanticObjectId, admin = Depends(require_admin)):
    """Ativa ou desativa um afiliado (requer permissão de admin)"""
    try:
        affiliate = await Affiliate.get(affiliate_id)
        if not affiliate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Afiliado não encontrado"
            )
        
        affiliate.is_active = not affiliate.is_active
        affiliate.updated_at = datetime.utcnow()
        await affiliate.save()
        
        return {
            "status": "success",
            "message": f"Afiliado {'ativado' if affiliate.is_active else 'desativado'} com sucesso",
            "is_active": affiliate.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar status do afiliado: {str(e)}"
        )
