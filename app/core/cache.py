"""
Módulo de cache com Redis
"""
import json
import redis.asyncio as redis
from typing import Optional, Any
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Inicializa conexão com Redis"""
    global redis_client
    try:
        redis_client = redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        print("✅ Redis conectado com sucesso")
    except Exception as e:
        print(f"⚠️  Redis não disponível: {e}")
        redis_client = None


async def close_redis():
    """Fecha conexão com Redis"""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("Redis desconectado")


async def get_cached(key: str) -> Optional[Any]:
    """Busca valor no cache"""
    if not redis_client:
        return None
    
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        print(f"Erro ao buscar cache: {e}")
        return None


async def set_cached(key: str, value: Any, ttl: int = 3600):
    """Salva valor no cache com TTL em segundos"""
    if not redis_client:
        return False
    
    try:
        await redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
        return True
    except Exception as e:
        print(f"Erro ao salvar cache: {e}")
        return False


async def delete_cached(key: str):
    """Remove valor do cache"""
    if not redis_client:
        return False
    
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Erro ao deletar cache: {e}")
        return False


async def is_redis_available() -> bool:
    """Verifica se Redis está disponível"""
    if not redis_client:
        return False
    
    try:
        await redis_client.ping()
        return True
    except:
        return False
