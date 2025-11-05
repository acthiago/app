from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from app.models.user import User
from app.core.security import create_access_token, get_current_user, require_admin, require_moderator
from app.core.logging import get_logger

router = APIRouter(prefix="/users", tags=["Users"])
logger = get_logger(__name__)

class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default="user", pattern="^(user|admin|moderator)$")
    avatar: Optional[str] = None
    bio: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    role: Optional[str] = Field(None, pattern="^(user|admin|moderator)$")
    is_active: Optional[bool] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    avatar: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 1️⃣ Criar novo usuário (requer admin)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, admin: User = Depends(require_admin)):
    """
    Cria um novo usuário no sistema (requer permissão de admin)
    """
    try:
        # Verificar se email já existe
        existing_user = await User.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Criar usuário
        user = User(
            name=data.name,
            email=data.email,
            password_hash=User.hash_password(data.password),
            role=data.role,
            avatar=data.avatar,
            bio=data.bio,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await user.insert()
        
        logger.info("user_created", user_id=str(user.id), email=user.email, role=user.role)
        
        return {
            "status": "success",
            "message": "Usuário criado com sucesso",
            "id": str(user.id),
            "data": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "avatar": user.avatar,
                "bio": user.bio,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("user_creation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )


# 2️⃣ Listar usuários (requer autenticação)
@router.get("/")
async def list_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os usuários com filtros opcionais (requer autenticação)
    """
    try:
        query = {}
        if role:
            query["role"] = role
        if is_active is not None:
            query["is_active"] = is_active
        
        users = await User.find(query).skip(skip).limit(limit).to_list()
        total = await User.find(query).count()
        
        # Remover password_hash da resposta
        users_response = []
        for user in users:
            users_response.append({
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "avatar": user.avatar,
                "bio": user.bio,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login
            })
        
        return {
            "total": total,
            "limit": limit,
            "skip": skip,
            "data": users_response
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar usuários: {str(e)}"
        )


# 3️⃣ Buscar usuário por ID (requer autenticação)
@router.get("/{user_id}")
async def get_user(user_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    """
    Busca um usuário específico por ID (usuário pode ver próprio perfil, admin vê todos)
    """
    try:
        # Verificar permissão: usuário pode ver próprio perfil, admin vê todos
        if str(current_user.id) != str(user_id) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para visualizar este usuário"
            )
        
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "avatar": user.avatar,
            "bio": user.bio,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar usuário: {str(e)}"
        )


# 4️⃣ Atualizar usuário (requer autenticação)
@router.put("/{user_id}")
async def update_user(user_id: PydanticObjectId, data: UserUpdate, current_user: User = Depends(get_current_user)):
    """
    Atualiza um usuário existente (usuário pode editar próprio perfil, admin edita todos)
    """
    try:
        # Verificar permissão: usuário pode editar próprio perfil, admin edita todos
        if str(current_user.id) != str(user_id) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para editar este usuário"
            )
        
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        update_data = data.dict(exclude_unset=True)
        
        # Não permitir que usuários comuns alterem o role (apenas admins)
        if "role" in update_data and update_data["role"] != user.role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem alterar roles de usuários"
            )
        
        # Se está atualizando email, verificar se já existe
        if "email" in update_data and update_data["email"] != user.email:
            existing = await User.get_by_email(update_data["email"])
            if existing and str(existing.id) != str(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já está em uso"
                )
        
        # Se está atualizando senha, fazer hash
        if "password" in update_data:
            update_data["password_hash"] = User.hash_password(update_data.pop("password"))
        
        update_data["updated_at"] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(user, key, value)
        
        await user.save()
        
        return {
            "status": "success",
            "message": "Usuário atualizado com sucesso",
            "data": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "avatar": user.avatar,
                "bio": user.bio,
                "updated_at": user.updated_at
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar usuário: {str(e)}"
        )


# 5️⃣ Excluir usuário (requer admin)
@router.delete("/{user_id}")
async def delete_user(user_id: PydanticObjectId, admin: User = Depends(require_admin)):
    """
    Remove um usuário do sistema (requer permissão de admin)
    """
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        await user.delete()
        
        logger.info("user_deleted", user_id=str(user_id))
        
        return {
            "status": "success",
            "message": "Usuário excluído com sucesso",
            "id": str(user_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir usuário: {str(e)}"
        )


# 6️⃣ Login (autenticação básica)
@router.post("/login")
async def login(data: LoginRequest):
    """
    Autentica um usuário
    """
    try:
        user = await User.get_by_email(data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        
        if not user.verify_password(data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Atualizar last_login
        user.last_login = datetime.utcnow()
        await user.save()
        
        logger.info("user_login", user_id=str(user.id), email=user.email, role=user.role)
        
        # Criar token JWT
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        return {
            "status": "success",
            "message": "Login realizado com sucesso",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "avatar": user.avatar,
                "bio": user.bio
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer login: {str(e)}"
        )


# 7️⃣ Endpoint para obter usuário atual (autenticado)
@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado
    """
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "avatar": current_user.avatar,
        "bio": current_user.bio,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }


# 8️⃣ Desativar/Ativar usuário (requer admin)
@router.patch("/{user_id}/toggle-active")
async def toggle_user_active(user_id: PydanticObjectId, admin: User = Depends(require_admin)):
    """
    Ativa ou desativa um usuário
    """
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        await user.save()
        
        return {
            "status": "success",
            "message": f"Usuário {'ativado' if user.is_active else 'desativado'} com sucesso",
            "is_active": user.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar status do usuário: {str(e)}"
        )
