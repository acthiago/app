from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from beanie import PydanticObjectId
from tenacity import retry, stop_after_attempt, wait_exponential
from app.services.offer_extractor.factory import get_extractor
from app.models.offer import Offer
from app.models.post import Post
from app.models.price_history import PriceHistory
from app.core.cache import get_cached, set_cached
from app.core.security import get_current_user, require_admin, require_moderator
from app.core.logging import get_logger
from app.services.ai_categorization import categorize_offer, categorize_by_keywords, generate_tags, generate_tags_by_keywords
import hashlib

router = APIRouter(prefix="/offers", tags=["Offers"])
logger = get_logger(__name__)



CHANNELS_DEFAULT = ["telegram", "whatsapp", "site", "instagram"]

def convert_price_to_float(price_str: str) -> float:
    """
    Converte string de preço para float, tratando formatos brasileiros.
    Exemplos:
    - "5.950" -> 5950.0
    - "3.254,99" -> 3254.99
    - "1.000" -> 1000.0
    - "10,50" -> 10.5
    """
    if not price_str:
        return None
    
    try:
        # Remove espaços
        price_str = price_str.strip()
        
        # Se tem vírgula, é separador decimal (ex: 3.254,99)
        if "," in price_str:
            price_str = price_str.replace(".", "").replace(",", ".")
        # Se tem apenas ponto, pode ser milhar (5.950) ou decimal (10.5)
        elif "." in price_str:
            # Contar quantos dígitos após o último ponto
            parts = price_str.split(".")
            last_part = parts[-1]
            
            # Se tem 3 dígitos após o ponto, é separador de milhar
            if len(last_part) == 3 and len(parts) > 1:
                price_str = price_str.replace(".", "")
            # Caso contrário, é separador decimal
        
        return float(price_str)
    except:
        return None

class ExtractRequest(BaseModel):
    url: str

class OfferCreate(BaseModel):
    source: str
    url: str
    extract_url: Optional[str] = None
    title: str
    price_original: Optional[float] = None
    price_discounted: Optional[float] = None
    discount: Optional[str] = None
    installments: Optional[str] = None
    currency: str = "BRL"
    image: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    optimized_message: Optional[str] = None
    note: Optional[str] = None
    status: str = "pending"

class OfferUpdate(BaseModel):
    title: Optional[str] = None
    price_original: Optional[float] = None
    price_discounted: Optional[float] = None
    discount: Optional[str] = None
    installments: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    optimized_message: Optional[str] = None
    note: Optional[str] = None
    status: Optional[str] = None
    extract_url: Optional[str] = None

# 1️⃣ Extrair dados de uma URL (com cache e retry)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def extract_with_retry(url: str):
    """Extrai dados com retry e backoff exponencial"""
    extractor = get_extractor(url)
    return extractor.extract()


@router.post("/extract")
async def extract_offer(data: ExtractRequest, current_user = Depends(get_current_user)):
    """Extrai informações de uma URL (requer autenticação)"""
    url = data.url
    if not url:
        raise HTTPException(400, "Campo 'url' é obrigatório.")

    try:
        # Gerar chave de cache baseada na URL
        cache_key = f"extract:{hashlib.md5(url.encode()).hexdigest()}"
        
        # Tentar buscar do cache
        cached_data = await get_cached(cache_key)
        if cached_data:
            logger.info("extraction_cache_hit", url=url)
            return {"status": "success", "data": cached_data, "from_cache": True}
        
        # Extrair com retry
        logger.info("extraction_started", url=url)
        result = await extract_with_retry(url)
        
        # Salvar no cache (TTL 1 hora)
        await set_cached(cache_key, result, ttl=3600)
        logger.info("extraction_completed", url=url)
        
        return {"status": "success", "data": result, "from_cache": False}
    except ValueError as e:
        logger.error("extraction_validation_error", url=url, error=str(e))
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error("extraction_failed", url=url, error=str(e))
        raise HTTPException(500, f"Erro ao processar oferta: {e}")


# 1.5️⃣ Extrair e salvar oferta automaticamente (com validação de duplicata)
@router.post("/extract-and-save")
async def extract_and_save_offer(data: ExtractRequest):
    url = data.url
    if not url:
        raise HTTPException(400, "Campo 'url' é obrigatório.")

    try:
        # Extrair dados com retry
        extracted_data = await extract_with_retry(url)
        
        # Preparar dados para salvar
        title = extracted_data.get("title", "")
        description = extracted_data.get("description", "")
        price_str = extracted_data.get("price", "")
        
        # Converter preço para float
        price = convert_price_to_float(price_str)
        
        # Verificar duplicata
        if title and price:
            existing_offer = await Offer.check_duplicate(title=title, price=price, url=extracted_data.get("url", url))
            if existing_offer:
                logger.info("offer_duplicate_found", offer_id=str(existing_offer.id))
                return {
                    "status": "duplicate",
                    "message": "Oferta duplicada: já existe uma oferta com mesmo título e preço criada hoje ou mesma URL",
                    "existing_offer_id": str(existing_offer.id),
                    "extracted_data": extracted_data,
                    "existing_offer": existing_offer
                }
        
        # Categorização automática com IA
        category = "Outros"
        tags = []
        try:
            category = await categorize_offer(title, description)
            logger.info("offer_categorized", category=category, method="ai")
            
            # Gerar tags com IA
            tags = await generate_tags(title, description, category)
            logger.info("tags_generated", tags=tags, method="ai")
        except Exception as e:
            # Fallback para categorização por keywords
            category = categorize_by_keywords(title)
            tags = generate_tags_by_keywords(title)
            logger.info("offer_categorized", category=category, method="keywords")
            logger.info("tags_generated", tags=tags, method="keywords")
        
        # Criar oferta
        original_price_str = extracted_data.get("original_price", "")
        original_price = convert_price_to_float(original_price_str)
        
        offer = Offer(
            source=extracted_data.get("source", ""),
            url=extracted_data.get("url", url),
            extract_url=url,  # URL original do extract
            title=title,
            price_original=original_price,
            price_discounted=price,
            discount=extracted_data.get("discount", ""),
            installments=extracted_data.get("installments", ""),
            currency=extracted_data.get("currency", "BRL"),
            image=extracted_data.get("image", ""),  # Imagem principal
            images=extracted_data.get("images", []),  # Lista de todas as imagens
            description=description,
            note=extracted_data.get("note", ""),
            category=category,  # Categoria automática
            tags=tags,  # Tags geradas por IA
            optimized_message=None,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await offer.insert()
        logger.info("offer_created", offer_id=str(offer.id), category=category, images_count=len(extracted_data.get("images", [])))
        
        # Registrar no histórico de preços
        price_history = PriceHistory(
            offer_id=str(offer.id),
            price_original=original_price,
            price_discounted=price,
            discount=extracted_data.get("discount", ""),
            currency="BRL",
            source="scraping"
        )
        await price_history.insert()
        logger.info("price_history_recorded", offer_id=str(offer.id))
        
        # Criar posts para cada canal
        for channel in CHANNELS_DEFAULT:
            post = Post(
                offer_id=str(offer.id),
                channel=channel,
                status="pending",
                enviado=False
            )
            await post.insert()
        
        return {
            "status": "success",
            "message": "Oferta extraída e salva com sucesso",
            "id": str(offer.id),
            "extracted_data": extracted_data,
            "offer": offer
        }
        
    except ValueError as e:
        logger.error("offer_creation_validation_error", error=str(e))
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error("offer_creation_failed", error=str(e))
        raise HTTPException(500, f"Erro ao processar oferta: {e}")


# 2️⃣ Criar uma nova oferta no banco de dados (requer moderador)
@router.post("/")
async def create_offer(data: OfferCreate, moderator = Depends(require_moderator)):
    """Cria uma nova oferta manualmente (requer permissão de moderador)"""
    try:
        # Verificar se já existe oferta duplicada hoje
        existing_offer = await Offer.check_duplicate(
            title=data.title,
            price=data.price_discounted,
            url=data.url
        )
        
        if existing_offer:
            return {
                "status": "duplicate",
                "message": "Oferta duplicada: já existe uma oferta com mesmo título e preço criada hoje ou mesma URL",
                "existing_offer_id": str(existing_offer.id),
                "data": existing_offer
            }
        
        offer = Offer(
            source=data.source,
            url=data.url,
            extract_url=data.extract_url or data.url,  # Se não informado, usa url
            title=data.title,
            price_original=data.price_original,
            price_discounted=data.price_discounted,
            discount=data.discount,
            installments=data.installments,
            currency=data.currency,
            image=data.image,
            description=data.description,
            category=data.category,
            tags=data.tags,
            optimized_message=data.optimized_message,
            note=data.note,
            status=data.status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await offer.insert()
        
        # Criar posts para cada canal
        for channel in CHANNELS_DEFAULT:
            post = Post(
                offer_id=str(offer.id),
                channel=channel,
                status="pending",
                enviado=False
            )
            await post.insert()

        return {"status": "success", "id": str(offer.id), "data": offer}
    except Exception as e:
        raise HTTPException(500, f"Erro ao salvar oferta: {e}")


# 3️⃣ Listar todas as ofertas com filtros opcionais
@router.get("/")
async def list_offers(
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    try:
        query = {}
        if status:
            query["status"] = status
        if source:
            query["source"] = source
        
        offers = await Offer.find(query).skip(skip).limit(limit).to_list()
        total = await Offer.find(query).count()
        
        return {
            "total": total,
            "limit": limit,
            "skip": skip,
            "data": offers
        }
    except Exception as e:
        raise HTTPException(500, f"Erro ao listar ofertas: {e}")


# 3.1️⃣ Atualizar tags de todas as ofertas em lote (deve vir antes de /{offer_id})
@router.post("/batch/generate-tags")
async def batch_generate_tags(admin = Depends(require_admin)):
    """Gera tags para todas as ofertas que não possuem tags"""
    try:
        # Buscar ofertas sem tags ou com tags vazias
        offers = await Offer.find({"$or": [{"tags": []}, {"tags": None}]}).to_list()
        
        updated_count = 0
        errors = []
        
        for offer in offers:
            try:
                # Gerar tags
                tags = await generate_tags(offer.title, offer.description, offer.category)
                
                # Atualizar oferta
                offer.tags = tags
                offer.updated_at = datetime.utcnow()
                await offer.save()
                
                updated_count += 1
                logger.info("batch_tags_generated", offer_id=str(offer.id), tags=tags)
                
            except Exception as e:
                errors.append({"offer_id": str(offer.id), "error": str(e)})
                logger.error("batch_tags_generation_failed", offer_id=str(offer.id), error=str(e))
        
        return {
            "status": "completed",
            "total_offers": len(offers),
            "updated": updated_count,
            "errors": len(errors),
            "error_details": errors[:10]  # Primeiros 10 erros
        }
    except Exception as e:
        logger.error("batch_tags_generation_error", error=str(e))
        raise HTTPException(500, f"Erro no processamento em lote: {e}")


# 4️⃣ Buscar oferta específica por ID
@router.get("/{offer_id}")
async def get_offer(offer_id: PydanticObjectId):
    try:
        offer = await Offer.get(offer_id)
        if not offer:
            raise HTTPException(404, "Oferta não encontrada")
        return offer
    except Exception as e:
        raise HTTPException(500, f"Erro ao buscar oferta: {e}")


# 5️⃣ Atualizar uma oferta existente (requer moderador)
@router.put("/{offer_id}")
async def update_offer(
    offer_id: PydanticObjectId, 
    data: OfferUpdate,
    current_user = Depends(require_moderator)
):
    try:
        offer = await Offer.get(offer_id)
        if not offer:
            raise HTTPException(404, "Oferta não encontrada")
        
        # Guardar preços antigos
        old_price_original = offer.price_original
        old_price_discounted = offer.price_discounted
        
        update_data = data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(offer, key, value)
        
        await offer.save()
        
        # Se preço mudou, registrar no histórico
        if (data.price_original and data.price_original != old_price_original) or \
           (data.price_discounted and data.price_discounted != old_price_discounted):
            price_history = PriceHistory(
                offer_id=str(offer.id),
                price_original=offer.price_original,
                price_discounted=offer.price_discounted,
                discount=offer.discount,
                currency=offer.currency,
                source="manual_update"
            )
            await price_history.insert()
            logger.info("price_history_updated", offer_id=str(offer.id))
        
        return {"status": "updated", "data": offer}
    except Exception as e:
        logger.error("offer_update_failed", offer_id=str(offer_id), error=str(e))
        raise HTTPException(500, f"Erro ao atualizar oferta: {e}")


# 6️⃣ Excluir uma oferta (requer admin)
@router.delete("/{offer_id}")
async def delete_offer(offer_id: PydanticObjectId, admin = Depends(require_admin)):
    try:
        offer = await Offer.get(offer_id)
        if not offer:
            raise HTTPException(404, "Oferta não encontrada")
        
        # Remover posts associados
        try:
            posts = await Post.find({"offer_id": str(offer_id)}).to_list()
            for p in posts:
                await p.delete()
            logger.info("posts_deleted", offer_id=str(offer_id), count=len(posts))
        except Exception as e:
            logger.warning("posts_deletion_partial_failure", error=str(e))

        await offer.delete()
        logger.info("offer_deleted", offer_id=str(offer_id))
        return {"status": "deleted", "id": str(offer_id)}
    except Exception as e:
        logger.error("offer_deletion_failed", offer_id=str(offer_id), error=str(e))
        raise HTTPException(500, f"Erro ao excluir oferta: {e}")


# 7️⃣ Atualizar tags de uma oferta com IA
@router.post("/{offer_id}/generate-tags")
async def generate_offer_tags(offer_id: PydanticObjectId, moderator = Depends(require_moderator)):
    """Gera tags automaticamente para uma oferta usando IA"""
    try:
        offer = await Offer.get(offer_id)
        if not offer:
            raise HTTPException(404, "Oferta não encontrada")
        
        # Gerar tags com IA
        try:
            tags = await generate_tags(offer.title, offer.description, offer.category)
            method = "ai"
            logger.info("tags_generated", offer_id=str(offer_id), tags=tags, method="ai")
        except Exception as e:
            # Fallback para keywords
            tags = generate_tags_by_keywords(offer.title)
            method = "keywords"
            logger.warning("tags_generation_fallback", offer_id=str(offer_id), error=str(e))
        
        # Atualizar oferta
        offer.tags = tags
        offer.updated_at = datetime.utcnow()
        await offer.save()
        
        return {
            "status": "success", 
            "offer_id": str(offer_id),
            "tags": tags,
            "method": method
        }
    except Exception as e:
        logger.error("tags_generation_failed", offer_id=str(offer_id), error=str(e))
        raise HTTPException(500, f"Erro ao gerar tags: {e}")


# 9️⃣ Health check
@router.get("/health/check")
def health_check():
    return {"status": "ok"}

