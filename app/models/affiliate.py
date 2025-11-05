from beanie import Document, Indexed
from datetime import datetime
from typing import Optional
from pydantic import HttpUrl, Field

class Affiliate(Document):
    """Modelo para sites afiliados (Shopee, Mercado Livre, AliExpress, Amazon, etc)"""
    
    name: str = Field(..., min_length=2, max_length=100, description="Nome do site afiliado")
    slug: Indexed(str, unique=True) = Field(..., description="Identificador único (ex: shopee, mercadolivre)")
    url: HttpUrl = Field(..., description="URL do site afiliado")
    logo: Optional[str] = Field(None, description="URL do logo do afiliado")
    api_key: Optional[str] = Field(None, description="Chave de API se houver integração")
    api_secret: Optional[str] = Field(None, description="Secret da API se houver")
    commission_rate: Optional[float] = Field(None, ge=0, le=100, description="Taxa de comissão (%)")
    affiliate_id: Optional[str] = Field(None, description="ID de afiliado no site")
    description: Optional[str] = Field(None, description="Descrição do programa de afiliados")
    terms_url: Optional[str] = Field(None, description="URL dos termos do programa")
    is_active: bool = Field(default=True, description="Se o afiliado está ativo")
    priority: int = Field(default=0, description="Prioridade de exibição (maior = mais prioritário)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "affiliates"
        
    @classmethod
    async def get_by_slug(cls, slug: str) -> Optional["Affiliate"]:
        """Busca afiliado por slug"""
        return await cls.find_one({"slug": slug})
