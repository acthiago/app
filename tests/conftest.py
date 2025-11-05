"""
Configuração do pytest
"""
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o módulo app
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app.core.database import init_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client():
    """Create async HTTP client for testing"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def initialize_db():
    """Initialize database before tests"""
    await init_db()
