from beanie import Document, Indexed
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import Field

class Channel(Document):
    """Modelo para canais de publicação (Telegram, WhatsApp, Instagram, Site, etc)"""
    
    name: str = Field(..., min_length=2, max_length=100, description="Nome do canal")
    slug: Indexed(str, unique=True) = Field(..., description="Identificador único (ex: telegram, whatsapp)")
    type: str = Field(..., description="Tipo: telegram | whatsapp | instagram | site | email | discord")
    description: Optional[str] = Field(None, description="Descrição do canal")
    
    # Credenciais e configurações específicas do canal
    api_token: Optional[str] = Field(None, description="Token de API (ex: bot token do Telegram)")
    api_key: Optional[str] = Field(None, description="Chave de API")
    api_secret: Optional[str] = Field(None, description="Secret da API")
    webhook_url: Optional[str] = Field(None, description="URL do webhook")
    channel_id: Optional[str] = Field(None, description="ID do canal/grupo")
    phone_number: Optional[str] = Field(None, description="Número de telefone (WhatsApp)")
    
    # Configurações adicionais (flexível para cada tipo de canal)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configurações adicionais em JSON")
    
    # Estatísticas
    total_posts: int = Field(default=0, description="Total de posts enviados")
    success_rate: float = Field(default=0.0, ge=0, le=100, description="Taxa de sucesso (%)")
    
    is_active: bool = Field(default=True, description="Se o canal está ativo")
    priority: int = Field(default=0, description="Prioridade de envio (maior = mais prioritário)")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_post_at: Optional[datetime] = Field(None, description="Data do último post enviado")
    
    class Settings:
        name = "channels"
        
    @classmethod
    async def get_by_slug(cls, slug: str) -> Optional["Channel"]:
        """Busca canal por slug"""
        return await cls.find_one({"slug": slug})
    
    @classmethod
    async def get_active_channels(cls) -> list["Channel"]:
        """Retorna apenas canais ativos ordenados por prioridade"""
        return await cls.find({"is_active": True}).sort("-priority").to_list()
