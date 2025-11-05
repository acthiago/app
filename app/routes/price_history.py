"""
Rotas de histórico de preços
"""
from fastapi import APIRouter, HTTPException, Depends
from beanie import PydanticObjectId
from typing import Optional
from app.models.price_history import PriceHistory
from app.models.offer import Offer
from app.core.security import get_current_user, require_moderator

router = APIRouter(prefix="/price-history", tags=["Price History"])

@router.get("/offer/{offer_id}")
async def get_offer_price_history(
    offer_id: str,
    days: int = 30
):
    """
    Retorna histórico de preços de uma oferta nos últimos N dias
    """
    try:
        history = await PriceHistory.get_price_history(offer_id, days)
        
        if not history:
            return {
                "offer_id": offer_id,
                "message": "Nenhum histórico encontrado",
                "history": []
            }
        
        return {
            "offer_id": offer_id,
            "total_records": len(history),
            "days": days,
            "history": [
                {
                    "price_original": h.price_original,
                    "price_discounted": h.price_discounted,
                    "discount": h.discount,
                    "currency": h.currency,
                    "timestamp": h.timestamp,
                    "source": h.source
                }
                for h in history
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Erro ao buscar histórico: {e}")


@router.get("/offer/{offer_id}/variation")
async def get_price_variation(offer_id: str):
    """
    Retorna a variação de preço de uma oferta
    """
    try:
        variation = await PriceHistory.get_price_variation(offer_id)
        
        if not variation:
            return {
                "offer_id": offer_id,
                "message": "Dados insuficientes para calcular variação"
            }
        
        return {
            "offer_id": offer_id,
            **variation
        }
    except Exception as e:
        raise HTTPException(500, f"Erro ao calcular variação: {e}")


@router.get("/offer/{offer_id}/lowest")
async def get_lowest_price(offer_id: str):
    """
    Retorna o menor preço já registrado de uma oferta
    """
    try:
        lowest = await PriceHistory.get_lowest_price(offer_id)
        
        if not lowest:
            return {
                "offer_id": offer_id,
                "message": "Nenhum histórico de preço encontrado"
            }
        
        return {
            "offer_id": offer_id,
            "lowest_price": lowest.price_discounted,
            "recorded_at": lowest.timestamp,
            "discount": lowest.discount
        }
    except Exception as e:
        raise HTTPException(500, f"Erro ao buscar menor preço: {e}")


@router.post("/offer/{offer_id}/record")
async def record_price(
    offer_id: str,
    current_user = Depends(require_moderator)
):
    """
    Registra o preço atual de uma oferta no histórico (requer moderador)
    """
    try:
        # Buscar oferta
        offer = await Offer.get(offer_id)
        if not offer:
            raise HTTPException(404, "Oferta não encontrada")
        
        # Criar registro no histórico
        price_record = PriceHistory(
            offer_id=str(offer.id),
            price_original=offer.price_original,
            price_discounted=offer.price_discounted,
            discount=offer.discount,
            currency=offer.currency,
            source="manual"
        )
        await price_record.insert()
        
        return {
            "status": "success",
            "message": "Preço registrado no histórico",
            "record_id": str(price_record.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao registrar preço: {e}")
