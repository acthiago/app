# Stage 1: Build
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar dependências do sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copiar dependências instaladas do stage builder
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Configurar PATH para incluir pacotes do usuário
ENV PATH=/home/appuser/.local/bin:$PATH

# Variáveis de ambiente (podem ser sobrescritas no docker-compose ou runtime)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/')"

# Comando de inicialização (SEM --reload em produção)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
