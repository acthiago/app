"""
Modelo de histórico de preços
"""
from beanie import Document
from datetime import datetime
from typing import Optional
from pydantic import Field

class PriceHistory(Document):
    """Armazena histórico de variação de preços de ofertas"""
    
    offer_id: str  # ID da oferta
    price_original: Optional[float] = None
    price_discounted: Optional[float] = None
    discount: Optional[str] = None
    currency: str = "BRL"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = ""  # Origem da coleta (manual, scraping, etc)
    
    class Settings:
        name = "price_history"
        indexes = [
            "offer_id",
            "timestamp"
        ]
    
    @classmethod
    async def get_price_history(cls, offer_id: str, days: int = 30):
        """Retorna histórico de preços de uma oferta nos últimos N dias"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        history = await cls.find(
            cls.offer_id == offer_id,
            cls.timestamp >= start_date
        ).sort("-timestamp").to_list()
        
        return history
    
    @classmethod
    async def get_lowest_price(cls, offer_id: str):
        """Retorna o menor preço registrado de uma oferta"""
        history = await cls.find(
            cls.offer_id == offer_id,
            cls.price_discounted != None
        ).sort("price_discounted").first_or_none()
        
        return history
    
    @classmethod
    async def get_price_variation(cls, offer_id: str):
        """Calcula a variação de preço (%) em relação ao histórico"""
        history = await cls.find(
            cls.offer_id == offer_id
        ).sort("-timestamp").to_list()
        
        if len(history) < 2:
            return None
        
        latest = history[0]
        oldest = history[-1]
        
        if not latest.price_discounted or not oldest.price_discounted:
            return None
        
        variation = ((latest.price_discounted - oldest.price_discounted) / oldest.price_discounted) * 100
        
        return {
            "current_price": latest.price_discounted,
            "initial_price": oldest.price_discounted,
            "variation_percent": round(variation, 2),
            "trend": "up" if variation > 0 else "down" if variation < 0 else "stable"
        }
