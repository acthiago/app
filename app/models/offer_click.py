from beanie import Document
from datetime import datetime
from typing import Optional
from pydantic import Field

class OfferClick(Document):
    """Modelo para rastreamento de cliques em ofertas"""
    
    offer_id: str = Field(..., description="ID da oferta clicada")
    source: str = Field(default="web", description="Origem do clique (home, ofertas, dashboard, etc)")
    ip_address: Optional[str] = Field(None, description="Endereço IP do usuário")
    user_agent: Optional[str] = Field(None, description="User agent do navegador")
    clicked_at: datetime = Field(default_factory=datetime.utcnow, description="Data e hora do clique")
    
    class Settings:
        name = "offer_clicks"
        indexes = [
            [("offer_id", 1), ("clicked_at", -1)],  # Buscar cliques por oferta ordenados por data
            [("source", 1)],  # Buscar por origem
            [("clicked_at", -1)],  # Ordenar por data recente
        ]
