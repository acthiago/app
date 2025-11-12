"""
Rotas de Analytics - Rastreamento de cliques e visualizações
"""
from fastapi import APIRouter, HTTPException, Request
from app.models.offer_click import OfferClick
from app.models.page_view import PageView
from app.models.offer import Offer
from beanie import PydanticObjectId
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/click")
async def track_offer_click(data: dict, request: Request):
    """
    Registra um clique em uma oferta
    
    Body:
    - offer_id: ID da oferta
    - source: origem do clique (home, ofertas, dashboard, etc) - opcional
    """
    try:
        offer_id = data.get("offer_id")
        if not offer_id:
            raise HTTPException(400, "Campo 'offer_id' é obrigatório")
        
        # Verificar se oferta existe
        offer = await Offer.get(offer_id)
        if not offer:
            raise HTTPException(404, "Oferta não encontrada")
        
        # Criar registro de clique
        click = OfferClick(
            offer_id=str(offer_id),
            source=data.get("source", "web"),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            clicked_at=datetime.utcnow()
        )
        await click.save()
        
        # Incrementar contador na oferta
        offer.total_clicks += 1
        offer.updated_at = datetime.utcnow()
        await offer.save()
        
        return {"status": "success", "message": "Click registrado"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao registrar click: {str(e)}")


@router.post("/pageview")
async def track_page_view(data: dict, request: Request):
    """
    Registra uma visualização de página
    
    Body:
    - page: nome da página (home, ofertas, cupons, etc)
    """
    try:
        page = data.get("page")
        if not page:
            raise HTTPException(400, "Campo 'page' é obrigatório")
        
        # Criar registro de visualização
        pageview = PageView(
            page=page,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            viewed_at=datetime.utcnow()
        )
        await pageview.save()
        
        return {"status": "success"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao registrar pageview: {str(e)}")


@router.get("/offer/{offer_id}")
async def get_offer_metrics(offer_id: str):
    """
    Obtém métricas de uma oferta específica
    
    Retorna:
    - offer_id, offer_title
    - total_clicks
    - clicks_by_source (dicionário com contagem por origem)
    - clicks_by_day (array com cliques por dia nos últimos 30 dias)
    - last_30_days (total de cliques nos últimos 30 dias)
    """
    try:
        # Buscar oferta
        offer = await Offer.get(offer_id)
        if not offer:
            raise HTTPException(404, "Oferta não encontrada")
        
        # Total de cliques
        total_clicks = await OfferClick.find({"offer_id": offer_id}).count()
        
        # Cliques por fonte
        pipeline_source = [
            {"$match": {"offer_id": offer_id}},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        clicks_by_source_raw = await OfferClick.get_pymongo_collection().aggregate(pipeline_source).to_list(length=None)
        clicks_by_source = {item["_id"]: item["count"] for item in clicks_by_source_raw}
        
        # Cliques por dia (últimos 30 dias)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        pipeline_day = [
            {
                "$match": {
                    "offer_id": offer_id,
                    "clicked_at": {"$gte": thirty_days_ago}
                }
            },
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$clicked_at"}},
                    "clicks": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        clicks_by_day_raw = await OfferClick.get_pymongo_collection().aggregate(pipeline_day).to_list(length=None)
        clicks_by_day = [{"date": item["_id"], "clicks": item["clicks"]} for item in clicks_by_day_raw]
        
        # Total últimos 30 dias
        last_30_days = await OfferClick.find({
            "offer_id": offer_id,
            "clicked_at": {"$gte": thirty_days_ago}
        }).count()
        
        return {
            "offer_id": str(offer.id),
            "offer_title": offer.title,
            "total_clicks": total_clicks,
            "clicks_by_source": clicks_by_source,
            "clicks_by_day": clicks_by_day,
            "last_30_days": last_30_days
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erro ao buscar métricas da oferta: {str(e)}")


@router.get("/summary")
async def get_analytics_summary():
    """
    Obtém resumo geral de métricas
    
    Retorna:
    - total_offer_clicks
    - total_page_views
    - most_clicked_offers (top 10)
    - most_viewed_pages
    - clicks_last_7_days
    - views_last_7_days
    """
    try:
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # Total de cliques
        total_clicks = await OfferClick.find({}).count()
        
        # Total de visualizações
        total_views = await PageView.find({}).count()
        
        # Ofertas mais clicadas (top 10)
        pipeline_most_clicked = [
            {"$group": {"_id": "$offer_id", "clicks": {"$sum": 1}}},
            {"$sort": {"clicks": -1}},
            {"$limit": 10}
        ]
        most_clicked_raw = await OfferClick.get_pymongo_collection().aggregate(pipeline_most_clicked).to_list(length=None)
        
        # Enriquecer com dados das ofertas
        most_clicked_offers = []
        for item in most_clicked_raw:
            try:
                offer = await Offer.get(item["_id"])
                if offer:
                    most_clicked_offers.append({
                        "offer_id": item["_id"],
                        "title": offer.title,
                        "clicks": item["clicks"]
                    })
            except:
                # Se oferta não existir mais, pular
                continue
        
        # Páginas mais visualizadas
        pipeline_pages = [
            {"$group": {"_id": "$page", "views": {"$sum": 1}}},
            {"$sort": {"views": -1}}
        ]
        most_viewed_pages_raw = await PageView.get_pymongo_collection().aggregate(pipeline_pages).to_list(length=None)
        most_viewed_pages = {item["_id"]: item["views"] for item in most_viewed_pages_raw}
        
        # Cliques últimos 7 dias
        clicks_last_7_days = await OfferClick.find({
            "clicked_at": {"$gte": seven_days_ago}
        }).count()
        
        # Views últimos 7 dias
        views_last_7_days = await PageView.find({
            "viewed_at": {"$gte": seven_days_ago}
        }).count()
        
        return {
            "total_offer_clicks": total_clicks,
            "total_page_views": total_views,
            "most_clicked_offers": most_clicked_offers,
            "most_viewed_pages": most_viewed_pages,
            "clicks_last_7_days": clicks_last_7_days,
            "views_last_7_days": views_last_7_days
        }
    
    except Exception as e:
        raise HTTPException(500, f"Erro ao buscar resumo de analytics: {str(e)}")
