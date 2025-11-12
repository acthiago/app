#!/bin/bash
echo "🔄 Reconstruindo imagem Docker com código atualizado..."
cd /home/thiago/bff-ecossistema/app

echo "
📦 1. Parando containers..."
docker-compose down

echo "
🏗️  2. Fazendo build da nova imagem (v2.2.2 com Fase 1)..."
docker build -t acthiago/api-bff-ecossistema:2.2.2 .

echo "
🚀 3. Subindo containers..."
docker-compose up -d

echo "
⏳ 4. Aguardando backend inicializar (15 segundos)..."
sleep 15

echo "
✅ 5. Verificando versão e features..."
curl -s http://localhost:8000/health/detailed | jq '{version, features}'

echo "
✨ Docker atualizado com código da Fase 1!
"
