from beanie import Document
from datetime import datetime
from typing import Optional
from pydantic import Field

class PageView(Document):
    """Modelo para rastreamento de visualizações de páginas"""
    
    page: str = Field(..., description="Nome da página visualizada (home, ofertas, cupons, etc)")
    ip_address: Optional[str] = Field(None, description="Endereço IP do usuário")
    user_agent: Optional[str] = Field(None, description="User agent do navegador")
    viewed_at: datetime = Field(default_factory=datetime.utcnow, description="Data e hora da visualização")
    
    class Settings:
        name = "page_views"
        indexes = [
            [("page", 1), ("viewed_at", -1)],  # Buscar views por página ordenados por data
            [("viewed_at", -1)],  # Ordenar por data recente
        ]
