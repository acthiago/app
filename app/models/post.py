from beanie import Document
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import Field

class Post(Document):
    offer_id: str = Field(..., description="ID da oferta relacionada")
    channel: str = Field(..., description="Canal (telegram, whatsapp, site, instagram, etc.)")
    enviado: bool = Field(default=False, description="True se já foi enviado com sucesso")
    status: str = Field(default="pending", description="pending, success, failed")
    responses: Optional[Dict[str, Any]] = Field(default_factory=dict)
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "posts"