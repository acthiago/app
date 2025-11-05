"""
Modelo para armazenamento e gerenciamento de arquivos
"""
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class FileType(str, Enum):
    """Tipos de arquivo permitidos"""
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    OTHER = "other"


class FileStorage(Document):
    """Modelo para armazenamento de arquivos"""
    
    # Identificação do arquivo
    filename: str = Field(..., description="Nome único do arquivo no sistema")
    original_name: str = Field(..., description="Nome original do arquivo enviado")
    
    # Tipo e classificação
    file_type: FileType = Field(default=FileType.OTHER, description="Tipo/categoria do arquivo")
    mime_type: str = Field(..., description="MIME type (ex: image/jpeg, application/pdf)")
    
    # Localização
    path: str = Field(..., description="Caminho relativo do arquivo no sistema")
    full_path: str = Field(..., description="Caminho absoluto completo")
    
    # Informações técnicas
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    checksum: Optional[str] = Field(None, description="Hash MD5 do arquivo para validação")
    
    # Datas
    upload_date: datetime = Field(default_factory=datetime.utcnow, description="Data de upload")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração (None = nunca expira)")
    last_accessed: Optional[datetime] = Field(None, description="Último acesso ao arquivo")
    
    # Relacionamentos
    uploaded_by: Optional[str] = Field(None, description="ID do usuário que fez upload")
    related_to: Optional[str] = Field(None, description="ID de recurso relacionado (offer, post, etc)")
    related_type: Optional[str] = Field(None, description="Tipo do recurso relacionado")
    
    # Metadados adicionais
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados extras (dimensões, duração, etc)")
    tags: list[str] = Field(default_factory=list, description="Tags para organização")
    description: Optional[str] = Field(None, description="Descrição do arquivo")
    
    # Controle
    is_public: bool = Field(default=False, description="Se o arquivo é acessível publicamente")
    download_count: int = Field(default=0, description="Contador de downloads")
    
    class Settings:
        name = "file_storage"
        indexes = [
            "filename",
            "uploaded_by",
            "file_type",
            "upload_date",
            "expires_at",
            [("related_to", 1), ("related_type", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "2024-11-04_abc123.jpg",
                "original_name": "produto-foto.jpg",
                "file_type": "image",
                "mime_type": "image/jpeg",
                "path": "uploads/2024/11/04/abc123.jpg",
                "size": 1048576,
                "uploaded_by": "507f1f77bcf86cd799439011",
                "metadata": {
                    "width": 1920,
                    "height": 1080
                },
                "is_public": False
            }
        }
    
    def is_expired(self) -> bool:
        """Verifica se o arquivo está expirado"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def get_url(self, base_url: str = "") -> str:
        """Retorna URL para download do arquivo"""
        return f"{base_url}/files/{self.id}/download"
    
    def increment_download(self):
        """Incrementa contador de downloads"""
        self.download_count += 1
        self.last_accessed = datetime.utcnow()
    
    @staticmethod
    def get_file_type_from_mime(mime_type: str) -> FileType:
        """Determina FileType baseado no MIME type"""
        if mime_type.startswith("image/"):
            return FileType.IMAGE
        elif mime_type.startswith("video/"):
            return FileType.VIDEO
        elif mime_type.startswith("audio/"):
            return FileType.AUDIO
        elif mime_type in ["application/pdf", "application/msword", 
                          "application/vnd.openxmlformats-officedocument",
                          "text/plain", "application/vnd.ms-excel"]:
            return FileType.DOCUMENT
        return FileType.OTHER
