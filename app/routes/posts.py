from fastapi import APIRouter, HTTPException, Depends
from app.models.post import Post
from beanie import PydanticObjectId
from datetime import datetime
from typing import Optional
from app.core.security import require_moderator

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/")
async def list_posts(
    enviado: Optional[bool] = None, 
    status: Optional[str] = None, 
    offer_id: Optional[str] = None,
    channel: Optional[str] = None
):
    query = {}
    if enviado is not None:
        query["enviado"] = enviado
    if status:
        query["status"] = status
    if offer_id:
        query["offer_id"] = offer_id
    if channel:
        query["channel"] = channel
    
    posts = await Post.find(query).to_list()
    return posts


@router.patch("/{post_id}")
async def update_post(post_id: PydanticObjectId, data: dict, moderator = Depends(require_moderator)):
    """Atualiza um post existente (requer permissão de moderador)"""
    post = await Post.get(post_id)
    if not post:
        raise HTTPException(404, "Post não encontrado")

    update_data = {**data, "updated_at": datetime.utcnow()}
    await post.set(update_data)
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
