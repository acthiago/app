from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from app.models.site_config import SiteConfig
from app.core.security import require_admin

router = APIRouter(prefix="/site-config", tags=["Site Config"])

class SiteConfigUpdate(BaseModel):
    site_name: Optional[str] = None
    site_description: Optional[str] = None
    site_url: Optional[HttpUrl] = None
    logo: Optional[str] = None
    favicon: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None
    group_links: Optional[Dict[str, str]] = None
    about_us: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: Optional[List[str]] = None
    privacy_policy: Optional[str] = None
    terms_of_service: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    meta_keywords: Optional[List[str]] = None
    google_analytics_id: Optional[str] = None
    facebook_pixel_id: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None

# 1️⃣ Obter configuração do site
@router.get("/")
async def get_site_config():
    """Retorna a configuração atual do site (singleton)"""
    try:
        config = await SiteConfig.get_config()
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar configuração: {str(e)}"
        )

# 2️⃣ Atualizar configuração do site (requer admin)
@router.put("/")
async def update_site_config(data: SiteConfigUpdate, admin = Depends(require_admin)):
    """Atualiza a configuração do site (requer permissão de admin)"""
    try:
        config = await SiteConfig.get_config()
        
        update_data = data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(config, key, value)
        
        await config.save()
        
        return {
            "status": "success",
            "message": "Configuração atualizada com sucesso",
            "data": config
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar configuração: {str(e)}"
        )

# 3️⃣ Atualizar apenas redes sociais (requer admin)
@router.patch("/social-media")
async def update_social_media(social_media: Dict[str, str], admin = Depends(require_admin)):
    """Atualiza apenas as redes sociais (requer permissão de admin)"""
    try:
        config = await SiteConfig.get_config()
        config.social_media = social_media
        config.updated_at = datetime.utcnow()
        await config.save()
        
        return {
            "status": "success",
            "message": "Redes sociais atualizadas com sucesso",
            "social_media": config.social_media
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar redes sociais: {str(e)}"
        )

# 4️⃣ Atualizar apenas links de grupos (requer admin)
@router.patch("/group-links")
async def update_group_links(group_links: Dict[str, str], admin = Depends(require_admin)):
    """Atualiza apenas os links de grupos (requer permissão de admin)"""
    try:
        config = await SiteConfig.get_config()
        config.group_links = group_links
        config.updated_at = datetime.utcnow()
        await config.save()
        
        return {
            "status": "success",
            "message": "Links de grupos atualizados com sucesso",
            "group_links": config.group_links
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar links de grupos: {str(e)}"
        )

# 5️⃣ Atualizar 'Sobre Nós' (requer admin)
@router.patch("/about-us")
async def update_about_us(about_us: str, mission: Optional[str] = None, vision: Optional[str] = None, values: Optional[List[str]] = None, admin = Depends(require_admin)):
    """Atualiza as informações 'Sobre Nós' (requer permissão de admin)"""
    try:
        config = await SiteConfig.get_config()
        config.about_us = about_us
        if mission:
            config.mission = mission
        if vision:
            config.vision = vision
        if values:
            config.values = values
        config.updated_at = datetime.utcnow()
        await config.save()
        
        return {
            "status": "success",
            "message": "Informações 'Sobre Nós' atualizadas com sucesso",
            "about_us": config.about_us,
            "mission": config.mission,
            "vision": config.vision,
            "values": config.values
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar 'Sobre Nós': {str(e)}"
        )

# 6️⃣ Ativar/Desativar modo de manutenção (requer admin)
@router.patch("/maintenance-mode")
async def toggle_maintenance_mode(maintenance_mode: bool, maintenance_message: Optional[str] = None, admin = Depends(require_admin)):
    """Ativa ou desativa o modo de manutenção (requer permissão de admin)"""
    try:
        config = await SiteConfig.get_config()
        config.maintenance_mode = maintenance_mode
        if maintenance_message:
            config.maintenance_message = maintenance_message
        config.updated_at = datetime.utcnow()
        await config.save()
        
        return {
            "status": "success",
            "message": f"Modo de manutenção {'ativado' if maintenance_mode else 'desativado'} com sucesso",
            "maintenance_mode": config.maintenance_mode,
            "maintenance_message": config.maintenance_message
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar modo de manutenção: {str(e)}"
        )

# 7️⃣ Resetar configuração para padrão (requer admin)
@router.post("/reset")
async def reset_site_config(admin = Depends(require_admin)):
    """Reseta a configuração do site para os valores padrão (requer permissão de admin)"""
    try:
        config = await SiteConfig.get_config()
        
        # Resetar para valores padrão
        config.site_name = "Ecosystem"
        config.site_description = None
        config.site_url = None
        config.logo = None
        config.favicon = None
        config.social_media = {}
        config.group_links = {}
        config.about_us = None
        config.mission = None
        config.vision = None
        config.values = []
        config.contact_email = None
        config.contact_phone = None
        config.contact_address = None
        config.meta_keywords = []
        config.google_analytics_id = None
        config.facebook_pixel_id = None
        config.maintenance_mode = False
        config.maintenance_message = None
        config.privacy_policy = None
        config.terms_of_service = None
        config.custom_config = {}
        config.updated_at = datetime.utcnow()
        
        await config.save()
        
        return {
            "status": "success",
            "message": "Configuração resetada com sucesso",
            "data": config
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao resetar configuração: {str(e)}"
        )

# 8️⃣ Obter Política de Privacidade
@router.get("/privacy-policy")
async def get_privacy_policy():
    """Retorna a Política de Privacidade do site (público)"""
    try:
        config = await SiteConfig.get_config()
        return {
            "privacy_policy": config.privacy_policy,
            "updated_at": config.updated_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar política de privacidade: {str(e)}"
        )

# 9️⃣ Atualizar Política de Privacidade (requer admin)
@router.put("/privacy-policy")
async def update_privacy_policy(privacy_policy: str, admin = Depends(require_admin)):
    """Atualiza a Política de Privacidade (requer permissão de admin)"""
    try:
        config = await SiteConfig.get_config()
        config.privacy_policy = privacy_policy
        config.updated_at = datetime.utcnow()
        await config.save()
        
        return {
            "status": "success",
            "message": "Política de privacidade atualizada com sucesso",
            "privacy_policy": config.privacy_policy,
            "updated_at": config.updated_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar política de privacidade: {str(e)}"
        )

# 🔟 Obter Termos de Serviço
@router.get("/terms-of-service")
async def get_terms_of_service():
    """Retorna os Termos de Serviço do site (público)"""
    try:
        config = await SiteConfig.get_config()
        return {
            "terms_of_service": config.terms_of_service,
            "updated_at": config.updated_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar termos de serviço: {str(e)}"
        )

# 1️⃣1️⃣ Atualizar Termos de Serviço (requer admin)
@router.put("/terms-of-service")
async def update_terms_of_service(terms_of_service: str, admin = Depends(require_admin)):
    """Atualiza os Termos de Serviço (requer permissão de admin)"""
    try:
        config = await SiteConfig.get_config()
        config.terms_of_service = terms_of_service
        config.updated_at = datetime.utcnow()
        await config.save()
        
        return {
            "status": "success",
            "message": "Termos de serviço atualizados com sucesso",
            "terms_of_service": config.terms_of_service,
            "updated_at": config.updated_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar termos de serviço: {str(e)}"
        )

