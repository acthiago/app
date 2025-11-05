from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routes import offers, posts, users, affiliates, channels, site_config, coupons, health, price_history, files
from app.core.database import init_db
from app.core.cache import init_redis, close_redis
from app.core.logging import configure_logging, get_logger
from app.services.ai_categorization import init_ai
from app.core.scheduler import init_scheduler, shutdown_scheduler

# Configurar logs estruturados
configure_logging()
logger = get_logger(__name__)

# Configurar rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Ecosystem Backend",
    version="2.2.0",
    description="Backend completo com JWT, cache Redis, rate limiting, logs estruturados, IA e gerenciamento de arquivos."
)

# Adicionar rate limiter ao app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    logger.info("Inicializando aplicação...")
    await init_db()
    await init_redis()
    init_ai()
    init_scheduler()
    logger.info("Aplicação inicializada com sucesso")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Encerrando aplicação...")
    await close_redis()
    shutdown_scheduler()
    logger.info("Aplicação encerrada")

# Registrar rotas
app.include_router(health.router)
app.include_router(offers.router)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(affiliates.router)
app.include_router(channels.router)
app.include_router(site_config.router)
app.include_router(coupons.router)
app.include_router(price_history.router)
app.include_router(files.router)

@app.get("/")
def root():
    return {"message": "Ecosystem API Online 🚀", "version": "2.2.0"}


