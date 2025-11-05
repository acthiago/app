from beanie import Document, Indexed
from datetime import datetime
from typing import Optional, List
from pydantic import Field

class Coupon(Document):
    """Modelo para cupons de desconto"""
    
    code: Indexed(str, unique=True) = Field(..., min_length=3, max_length=50, description="Código único do cupom")
    description: Optional[str] = Field(None, description="Descrição do cupom")
    
    # Tipo e valor do desconto
    discount_type: str = Field(..., description="Tipo: percentage | fixed | free_shipping")
    discount_value: float = Field(..., ge=0, description="Valor do desconto (% ou valor fixo)")
    
    # Restrições
    min_purchase_value: Optional[float] = Field(None, ge=0, description="Valor mínimo de compra para usar o cupom")
    max_discount_value: Optional[float] = Field(None, ge=0, description="Valor máximo de desconto (cap)")
    
    # Validade
    start_date: Optional[datetime] = Field(None, description="Data de início da validade")
    expiry_date: Optional[datetime] = Field(None, description="Data de expiração")
    
    # Limites de uso
    usage_limit: Optional[int] = Field(None, ge=1, description="Limite total de usos")
    usage_limit_per_user: Optional[int] = Field(None, ge=1, description="Limite de usos por usuário")
    current_usage: int = Field(default=0, ge=0, description="Número atual de usos")
    
    # Aplicabilidade
    applicable_to: Optional[List[str]] = Field(
        default_factory=list,
        description="Lista de categorias/produtos aplicáveis"
    )
    excluded_items: Optional[List[str]] = Field(
        default_factory=list,
        description="Lista de itens excluídos"
    )
    
    # Afiliados relacionados (opcional)
    affiliate_slug: Optional[str] = Field(None, description="Slug do afiliado relacionado")
    
    is_active: bool = Field(default=True, description="Se o cupom está ativo")
    is_public: bool = Field(default=True, description="Se o cupom é público ou exclusivo")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="ID do usuário que criou")
    
    class Settings:
        name = "coupons"
        
    @classmethod
    async def get_by_code(cls, code: str) -> Optional["Coupon"]:
        """Busca cupom por código (case-insensitive)"""
        return await cls.find_one({"code": code.upper()})
    
    def is_valid(self) -> tuple[bool, str]:
        """Verifica se o cupom é válido no momento atual"""
        now = datetime.utcnow()
        
        if not self.is_active:
            return False, "Cupom inativo"
        
        if self.start_date and now < self.start_date:
            return False, "Cupom ainda não iniciou"
        
        if self.expiry_date and now > self.expiry_date:
            return False, "Cupom expirado"
        
        if self.usage_limit and self.current_usage >= self.usage_limit:
            return False, "Limite de uso atingido"
        
        return True, "Cupom válido"
    
    async def increment_usage(self):
        """Incrementa o contador de uso do cupom"""
        self.current_usage += 1
        self.updated_at = datetime.utcnow()
        await self.save()
