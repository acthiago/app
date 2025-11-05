from beanie import Document, Indexed
from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
import bcrypt

class User(Document):
    name: str = Field(..., min_length=3, max_length=100)
    email: Indexed(EmailStr, unique=True)
    password_hash: str
    role: str = Field(default="user", description="user | admin | moderator")
    is_active: bool = Field(default=True)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Settings:
        name = "users"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash da senha"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verifica se a senha está correta"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        """Busca usuário por email"""
        return await cls.find_one({"email": email})
