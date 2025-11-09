from fastapi import APIRouter, HTTPException, Depends
from app.models.post import Post
from beanie import PydanticObjectId
from datetime import datetime
from typing import Optional
from app.core.security import require_moderator

router = APIRouter(prefix="/posts", tags=["Posts"])


async def update_channel_statistics(channel_name: str):
    """
    Atualiza as estatísticas de um canal (total_posts e success_rate)
    """
    from app.models.channel import Channel
    
    channel = await Channel.find_one({"name": channel_name})
    if not channel:
        return
    
    # Contar total de posts com status="success"
    success_count = await Post.find({"channel": channel_name, "status": "success"}).count()
    
    # Contar total de posts (tentativas)
    total_attempts = await Post.find({"channel": channel_name}).count()
    
    # Calcular success_rate
    success_rate = (success_count / total_attempts * 100) if total_attempts > 0 else 0.0
    
    # Atualizar canal
    channel.total_posts = success_count  # Apenas posts com sucesso
    channel.success_rate = round(success_rate, 2)
    channel.updated_at = datetime.utcnow()
    await channel.save()

@router.get("/")
async def list_posts(
    enviado: Optional[bool] = None, 
    status: Optional[str] = None, 
    offer_id: Optional[str] = None,
    channel: Optional[str] = None
):
    from app.models.offer import Offer
    from pymongo import DESCENDING
    
    # Construir match stage para filtros
    match_stage = {}
    if enviado is not None:
        match_stage["enviado"] = enviado
    if status:
        match_stage["status"] = status
    if offer_id:
        match_stage["offer_id"] = offer_id
    if channel:
        match_stage["channel"] = channel
    
    # Pipeline de agregação com lookup para pegar título da oferta
    pipeline = []
    
    # Adicionar filtros se existirem
    if match_stage:
        pipeline.append({"$match": match_stage})
    
    # Fazer lookup com a collection de ofertas
    pipeline.extend([
        {
            "$addFields": {
                "offer_id_obj": {"$toObjectId": "$offer_id"}
            }
        },
        {
            "$lookup": {
                "from": "offers",
                "localField": "offer_id_obj",
                "foreignField": "_id",
                "as": "offer_data"
            }
        },
        # Extrair apenas o título da oferta
        {
            "$addFields": {
                "offer_title": {
                    "$arrayElemAt": ["$offer_data.title", 0]
                }
            }
        },
        # Remover campos temporários
        {
            "$project": {
                "offer_data": 0,
                "offer_id_obj": 0
            }
        },
        # Ordenar por data de criação (mais recente primeiro)
        {
            "$sort": {"created_at": -1}
        }
    ])
    
    # Executar aggregation
    posts = await Post.get_pymongo_collection().aggregate(pipeline).to_list(length=None)
    
    # Converter ObjectId para string no resultado
    for post in posts:
        post["_id"] = str(post["_id"])
    
    return posts


@router.patch("/{post_id}")
async def update_post(post_id: PydanticObjectId, data: dict, moderator = Depends(require_moderator)):
    """Atualiza um post existente (requer permissão de moderador)"""
    post = await Post.get(post_id)
    if not post:
        raise HTTPException(404, "Post não encontrado")

    old_status = post.status
    update_data = {**data, "updated_at": datetime.utcnow()}
    await post.set(update_data)
    
    new_status = data.get("status", old_status)
    
    # Auto-aprovar oferta se o canal tiver auto_approve=True e o status for "success"
    if new_status == "success":
        from app.models.channel import Channel
        from app.models.offer import Offer
        
        channel = await Channel.find_one({"name": post.channel})
        if channel and channel.auto_approve:
            # Buscar e aprovar a oferta
            offer = await Offer.get(post.offer_id)
            if offer and offer.status != "approved":
                offer.status = "approved"
                offer.updated_at = datetime.utcnow()
                await offer.save()
    
    # Atualizar estatísticas do canal se o status mudou
    if old_status != new_status:
        await update_channel_statistics(post.channel)
    
    return {"status": "updated", "id": str(post.id)}


@router.delete("/{post_id}")
async def delete_post(post_id: PydanticObjectId, moderator = Depends(require_moderator)):
    """Remove um post específico por ID (requer permissão de moderador)"""
    post = await Post.get(post_id)
    if not post:
        raise HTTPException(404, "Post não encontrado")

    await post.delete()
    return {"status": "deleted", "id": str(post_id)}


@router.delete("/offer/{offer_id}")
async def delete_posts_by_offer(offer_id: str, moderator = Depends(require_moderator)):
    """Remove todos os posts associados a uma oferta (requer permissão de moderador)

    Recebe `offer_id` como string (id do Mongo/Beanie salvo em `Post.offer_id`).
    """
    # Buscar posts relacionados
    posts = await Post.find({"offer_id": offer_id}).to_list()

    if not posts:
        return {"status": "no_content", "message": "Nenhum post encontrado para essa oferta", "offer_id": offer_id}

    deleted_ids = []
    for p in posts:
        deleted_ids.append(str(p.id))
        await p.delete()

    return {"status": "deleted", "offer_id": offer_id, "deleted_count": len(deleted_ids), "deleted_ids": deleted_ids}
