import motor.motor_asyncio
from beanie import init_beanie
from app.models.offer import Offer
from app.models.post import Post
from app.models.user import User
from app.models.affiliate import Affiliate
from app.models.channel import Channel
from app.models.site_config import SiteConfig
from app.models.coupon import Coupon
from app.models.price_history import PriceHistory
from app.models.file_storage import FileStorage
from app.models.offer_click import OfferClick
from app.models.page_view import PageView
import os
from dotenv import load_dotenv

load_dotenv()

async def init_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db = os.getenv("MONGO_DB", "ecosystem_db")
    
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    await init_beanie(
        database=db, 
        document_models=[
            Offer, Post, User, Affiliate, Channel, SiteConfig, 
            Coupon, PriceHistory, FileStorage, OfferClick, PageView
        ]
    )
    print("✅ MongoDB conectado com sucesso")


async def get_db_status():
    """Retorna status da conexão com MongoDB"""
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        await client.admin.command('ping')
        return {"status": "connected", "database": os.getenv("MONGO_DB", "ecosystem_db")}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

