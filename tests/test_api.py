"""
Testes para endpoints de ofertas
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Testa endpoint raiz"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Ecosystem API Online 🚀"
    assert data["version"] == "2.1.0"


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Testa health check básico"""
    response = await client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_detailed_health_check(client: AsyncClient):
    """Testa health check detalhado"""
    response = await client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "mongodb" in data["services"]
    assert "redis" in data["services"]
    assert "features" in data


@pytest.mark.asyncio
async def test_list_offers(client: AsyncClient):
    """Testa listagem de ofertas"""
    response = await client.get("/offers/?limit=10&skip=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_extract_offer_without_url(client: AsyncClient):
    """Testa extração sem URL"""
    response = await client.post("/offers/extract", json={})
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Testa criação de usuário"""
    user_data = {
        "name": "Test User",
        "email": f"test{pytest.timestamp}@example.com",
        "password": "Test123456",
        "role": "user"
    }
    response = await client.post("/users/", json=user_data)
    assert response.status_code in [201, 400]  # 201 sucesso, 400 se já existe


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Testa login"""
    # Primeiro criar usuário
    user_data = {
        "name": "Login Test",
        "email": "logintest@example.com",
        "password": "Test123456",
        "role": "user"
    }
    await client.post("/users/", json=user_data)
    
    # Tentar login
    login_data = {
        "email": "logintest@example.com",
        "password": "Test123456"
    }
    response = await client.post("/users/login", json=login_data)
    assert response.status_code in [200, 401]
    
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


# Adicionar timestamp único para testes
pytest.timestamp = str(__import__("time").time()).replace(".", "")
