"""
Rotas de health check e monitoramento
"""
from fastapi import APIRouter
from app.core.database import get_db_status
from app.core.cache import is_redis_available
from datetime import datetime
import sys

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """
    Health check básico
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.2.2"
    }


@router.get("/detailed")
async def detailed_health_check():
    """
    Health check detalhado com status de todos os serviços
    """
    # Verificar MongoDB
    db_status = await get_db_status()
    
    # Verificar Redis
    redis_available = await is_redis_available()
    redis_status = {
        "status": "connected" if redis_available else "disconnected",
        "message": "Cache operacional" if redis_available else "Cache não disponível (funcionalidade degradada)"
    }
    
    # Status geral
    overall_healthy = db_status["status"] == "connected"
    
    return {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.2.2",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "services": {
            "mongodb": db_status,
            "redis": redis_status
        },
        "features": {
            "jwt_auth": True,
            "rate_limiting": True,
            "structured_logging": True,
            "ai_categorization": True,
            "ai_tags_generation": True,
            "price_history": True,
            "file_management": True,
            "multi_image_extraction": True,
            "auto_cleanup_scheduler": True,
            "amazon_extractor": True
        }
    }
