from beanie import Document
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import Field, HttpUrl

class SiteConfig(Document):
    """Configurações gerais do site (singleton - apenas um documento)"""
    
    # Informações básicas
    site_name: str = Field(default="Ecosystem", description="Nome do site")
    site_description: Optional[str] = Field(None, description="Descrição do site")
    site_url: Optional[HttpUrl] = Field(None, description="URL principal do site")
    logo: Optional[str] = Field(None, description="URL do logo")
    favicon: Optional[str] = Field(None, description="URL do favicon")
    
    # Redes sociais
    social_media: Dict[str, str] = Field(
        default_factory=dict,
        description="Links das redes sociais: {facebook, instagram, twitter, youtube, tiktok, etc}"
    )
    
    # Links de grupos
    group_links: Dict[str, str] = Field(
        default_factory=dict,
        description="Links para grupos: {telegram, whatsapp, discord, etc}"
    )
    
    # Sobre nós
    about_us: Optional[str] = Field(None, description="Texto 'Sobre Nós' do site")
    mission: Optional[str] = Field(None, description="Missão da empresa")
    vision: Optional[str] = Field(None, description="Visão da empresa")
    values: Optional[List[str]] = Field(default_factory=list, description="Valores da empresa")
    
    # Políticas e Termos
    privacy_policy: Optional[str] = Field(None, description="Política de Privacidade (Markdown/HTML)")
    terms_of_service: Optional[str] = Field(None, description="Termos de Serviço (Markdown/HTML)")
    
    # Contato
    contact_email: Optional[str] = Field(None, description="Email de contato")
    contact_phone: Optional[str] = Field(None, description="Telefone de contato")
    contact_address: Optional[str] = Field(None, description="Endereço físico")
    
    # SEO e Analytics
    meta_keywords: Optional[List[str]] = Field(default_factory=list, description="Palavras-chave para SEO")
    google_analytics_id: Optional[str] = Field(None, description="ID do Google Analytics")
    facebook_pixel_id: Optional[str] = Field(None, description="ID do Facebook Pixel")
    
    # Configurações gerais
    maintenance_mode: bool = Field(default=False, description="Modo de manutenção ativo")
    maintenance_message: Optional[str] = Field(None, description="Mensagem exibida no modo manutenção")
    
    # Configurações adicionais flexíveis
    custom_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Configurações customizadas em JSON"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "site_config"
        
    @classmethod
    async def get_config(cls) -> Optional["SiteConfig"]:
        """Retorna a configuração do site (sempre único)"""
        config = await cls.find_one()
        if not config:
            # Criar configuração padrão se não existir
            config = cls()
            await config.insert()
        return config
