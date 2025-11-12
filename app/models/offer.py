from beanie import Document, Indexed
from datetime import datetime, date
from typing import List, Optional
from pymongo import IndexModel, ASCENDING

class Offer(Document):
    source: str
    url: Indexed(str, unique=False)  # URL final após redirecionamento
    extract_url: Optional[str] = None  # URL original usada no extract
    title: Indexed(str)  # Indexado para busca rápida
    price_original: Optional[float] = None
    price_discounted: Optional[float] = None
    discount: Optional[str] = None  # Ex: "50% OFF"
    installments: Optional[str] = None  # Ex: "6x R$33 sem juros"
    currency: str = "BRL"
    image: Optional[str] = None  # Imagem principal (compatibilidade retroativa)
    images: List[str] = []  # Lista de todas as imagens do produto
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    optimized_message: Optional[str] = None
    note: Optional[str] = None  # Avisos sobre limitações da extração
    status: str = "pending"
    total_clicks: int = 0  # Contador de cliques na oferta
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "offers"
        indexes = [
            # Índice composto para evitar duplicatas no mesmo dia
            IndexModel(
                [
                    ("title", ASCENDING),
                    ("price_discounted", ASCENDING),
                    ("created_at", ASCENDING)
                ],
                name="unique_offer_per_day"
            ),
        ]
    
    @classmethod
    async def check_duplicate(cls, title: str, price: Optional[float], url: Optional[str] = None) -> Optional["Offer"]:
        """
        Verifica se já existe uma oferta duplicada:
        1. Mesmo título + mesmo preço criada hoje
        2. Mesma URL (independente da data)
        """
        # Verificar por URL primeiro (mais específico)
        if url:
            existing_by_url = await cls.find_one({"url": url})
            if existing_by_url:
                return existing_by_url
        
        # Verificar por título + preço no mesmo dia
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        
        query = {
            "title": title,
            "price_discounted": price,
            "created_at": {"$gte": today_start, "$lte": today_end}
        }
        
        return await cls.find_one(query)
