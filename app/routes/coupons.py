from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId
from app.models.coupon import Coupon
from app.core.security import require_moderator, require_admin, get_current_user

router = APIRouter(prefix="/coupons", tags=["Coupons"])

class CouponCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    discount_type: str = Field(..., description="percentage | fixed | free_shipping")
    discount_value: float = Field(..., ge=0)
    min_purchase_value: Optional[float] = Field(None, ge=0)
    max_discount_value: Optional[float] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, ge=1)
    usage_limit_per_user: Optional[int] = Field(None, ge=1)
    applicable_to: Optional[List[str]] = Field(default_factory=list)
    excluded_items: Optional[List[str]] = Field(default_factory=list)
    affiliate_slug: Optional[str] = None
    is_public: bool = Field(default=True)

class CouponUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = Field(None, ge=0)
    min_purchase_value: Optional[float] = Field(None, ge=0)
    max_discount_value: Optional[float] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, ge=1)
    usage_limit_per_user: Optional[int] = Field(None, ge=1)
    applicable_to: Optional[List[str]] = None
    excluded_items: Optional[List[str]] = None
    affiliate_slug: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None

class ValidateCouponRequest(BaseModel):
    code: str
    purchase_value: Optional[float] = Field(None, ge=0)
    user_id: Optional[str] = None

# 1️⃣ Criar cupom (requer moderador)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_coupon(data: CouponCreate, moderator = Depends(require_moderator)):
    """Cria um novo cupom de desconto (requer permissão de moderador)"""
    try:
        # Verificar se código já existe
        code_upper = data.code.upper()
        existing = await Coupon.get_by_code(code_upper)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de cupom já existe"
            )
        
        coupon = Coupon(
            code=code_upper,
            description=data.description,
            discount_type=data.discount_type.lower(),
            discount_value=data.discount_value,
            min_purchase_value=data.min_purchase_value,
            max_discount_value=data.max_discount_value,
            start_date=data.start_date,
            expiry_date=data.expiry_date,
            usage_limit=data.usage_limit,
            usage_limit_per_user=data.usage_limit_per_user,
            applicable_to=data.applicable_to,
            excluded_items=data.excluded_items,
            affiliate_slug=data.affiliate_slug,
            is_public=data.is_public,
            is_active=True,
            current_usage=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await coupon.insert()
        
        return {
            "status": "success",
            "message": "Cupom criado com sucesso",
            "id": str(coupon.id),
            "data": coupon
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cupom: {str(e)}"
        )

# 2️⃣ Listar cupons
@router.get("/")
async def list_coupons(
    is_active: Optional[bool] = None,
    is_public: Optional[bool] = None,
    discount_type: Optional[str] = None,
    affiliate_slug: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """Lista todos os cupons com filtros opcionais"""
    try:
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        if is_public is not None:
            query["is_public"] = is_public
        if discount_type:
            query["discount_type"] = discount_type.lower()
        if affiliate_slug:
            query["affiliate_slug"] = affiliate_slug
        
        coupons = await Coupon.find(query).skip(skip).limit(limit).to_list()
        total = await Coupon.find(query).count()
        
        return {
            "total": total,
            "limit": limit,
            "skip": skip,
            "data": coupons
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar cupons: {str(e)}"
        )

# 3️⃣ Buscar cupom por ID
@router.get("/{coupon_id}")
async def get_coupon(coupon_id: PydanticObjectId):
    """Busca um cupom específico por ID"""
    try:
        coupon = await Coupon.get(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        return coupon
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar cupom: {str(e)}"
        )

# 4️⃣ Buscar cupom por código
@router.get("/code/{code}")
async def get_coupon_by_code(code: str):
    """Busca um cupom por código"""
    try:
        coupon = await Coupon.get_by_code(code)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        return coupon
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar cupom: {str(e)}"
        )

# 5️⃣ Validar cupom
@router.post("/validate")
async def validate_coupon(data: ValidateCouponRequest):
    """Valida se um cupom pode ser usado"""
    try:
        coupon = await Coupon.get_by_code(data.code)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        
        # Verificar validade
        is_valid, message = coupon.is_valid()
        if not is_valid:
            return {
                "valid": False,
                "message": message,
                "coupon": None
            }
        
        # Verificar valor mínimo de compra
        if coupon.min_purchase_value and data.purchase_value:
            if data.purchase_value < coupon.min_purchase_value:
                return {
                    "valid": False,
                    "message": f"Valor mínimo de compra: R$ {coupon.min_purchase_value:.2f}",
                    "coupon": None
                }
        
        # Calcular desconto
        discount_amount = 0
        if data.purchase_value:
            if coupon.discount_type == "percentage":
                discount_amount = (data.purchase_value * coupon.discount_value) / 100
                if coupon.max_discount_value:
                    discount_amount = min(discount_amount, coupon.max_discount_value)
            elif coupon.discount_type == "fixed":
                discount_amount = coupon.discount_value
        
        return {
            "valid": True,
            "message": "Cupom válido",
            "coupon": {
                "code": coupon.code,
                "description": coupon.description,
                "discount_type": coupon.discount_type,
                "discount_value": coupon.discount_value,
                "discount_amount": discount_amount,
                "expiry_date": coupon.expiry_date,
                "usage_remaining": coupon.usage_limit - coupon.current_usage if coupon.usage_limit else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao validar cupom: {str(e)}"
        )

# 6️⃣ Aplicar/usar cupom (requer autenticação)
@router.post("/{coupon_id}/use")
async def use_coupon(coupon_id: PydanticObjectId, current_user = Depends(get_current_user)):
    """Incrementa o contador de uso do cupom (requer autenticação para rastreamento)"""
    try:
        coupon = await Coupon.get(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        
        # Verificar validade
        is_valid, message = coupon.is_valid()
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        await coupon.increment_usage()
        
        return {
            "status": "success",
            "message": "Cupom usado com sucesso",
            "current_usage": coupon.current_usage,
            "remaining": coupon.usage_limit - coupon.current_usage if coupon.usage_limit else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao usar cupom: {str(e)}"
        )

# 7️⃣ Atualizar cupom (requer moderador)
@router.put("/{coupon_id}")
async def update_coupon(coupon_id: PydanticObjectId, data: CouponUpdate, moderator = Depends(require_moderator)):
    """Atualiza um cupom existente (requer permissão de moderador)"""
    try:
        coupon = await Coupon.get(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        
        update_data = data.dict(exclude_unset=True)
        
        # Verificar código único se estiver sendo alterado
        if "code" in update_data and update_data["code"].upper() != coupon.code:
            existing = await Coupon.get_by_code(update_data["code"])
            if existing and str(existing.id) != str(coupon_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código de cupom já está em uso"
                )
            update_data["code"] = update_data["code"].upper()
        
        if "discount_type" in update_data:
            update_data["discount_type"] = update_data["discount_type"].lower()
        
        update_data["updated_at"] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(coupon, key, value)
        
        await coupon.save()
        
        return {
            "status": "success",
            "message": "Cupom atualizado com sucesso",
            "data": coupon
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar cupom: {str(e)}"
        )

# 8️⃣ Excluir cupom (requer admin)
@router.delete("/{coupon_id}")
async def delete_coupon(coupon_id: PydanticObjectId, admin = Depends(require_admin)):
    """Remove um cupom do sistema (requer permissão de admin)"""
    try:
        coupon = await Coupon.get(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        
        await coupon.delete()
        
        return {
            "status": "success",
            "message": "Cupom excluído com sucesso",
            "id": str(coupon_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir cupom: {str(e)}"
        )

# 9️⃣ Ativar/Desativar cupom (requer admin)
@router.patch("/{coupon_id}/toggle-active")
async def toggle_coupon_active(coupon_id: PydanticObjectId, admin = Depends(require_admin)):
    """Ativa ou desativa um cupom (requer permissão de admin)"""
    try:
        coupon = await Coupon.get(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        
        coupon.is_active = not coupon.is_active
        coupon.updated_at = datetime.utcnow()
        await coupon.save()
        
        return {
            "status": "success",
            "message": f"Cupom {'ativado' if coupon.is_active else 'desativado'} com sucesso",
            "is_active": coupon.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar status do cupom: {str(e)}"
        )
