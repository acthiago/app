# 🚀 Ecosystem Backend v2.3.1

Backend completo com JWT, Cache Redis, IA para categorização e tags, Histórico de Preços, **Gerenciamento de Arquivos**, **Sistema de Analytics** e **Sistema de Segurança Robusto**!

## 🛒 Plataformas Suportadas

Extração automática de ofertas de:
- 🟡 **Mercado Livre** (mercadolivre.com.br)
- 🟠 **Shopee** (shopee.com.br)
- 🔴 **AliExpress** (pt.aliexpress.com)
- 🟢 **Amazon** (amazon.com.br + links amzn.to)
- 🔵 **Kabum** (kabum.com.br + links tidd.ly) ✨ NOVO

## ✨ Novidades v2.3.1

- 🔵 **Extrator Kabum**
  - Suporte completo para Kabum.com.br (5ª plataforma)
  - Resolução de links encurtados (tidd.ly)
  - Extração via JSON-LD (Schema.org) para máxima confiabilidade
  - **Até 11 imagens de alta qualidade** por produto
  - **Marca e SKU** extraídos automaticamente
  - **Avaliações completas** (nota + quantidade)
  - Descrição detalhada (500 chars), disponibilidade e categoria

## ✨ Novidades v2.3.0

- 📊 **Sistema Completo de Analytics**
  - Rastreamento de cliques em ofertas com origem
  - Rastreamento de visualizações de páginas
  - Métricas detalhadas por oferta (total, por fonte, por dia)
  - Dashboard de analytics com top 10 ofertas e páginas mais vistas
  - 4 novos endpoints públicos
  - 2 novos modelos: OfferClick e PageView
  - Campo `total_clicks` nas ofertas

## ✨ Novidades v2.2.2

- 🟢 **Extrator Amazon**
  - Suporte completo a produtos da Amazon Brasil
  - Resolução automática de links encurtados (amzn.to)
  - Extração de avaliações, reviews e disponibilidade
  - Até 10 imagens por produto em alta qualidade

- 📊 **Melhorias Backend (Fase 1)**
  - Auto-aprovação de ofertas por canal
  - Contador de posts e estatísticas de canais
  - Título da oferta nos endpoints de posts

## ✨ Novidades v2.2.1

- 🔒 **Sistema de segurança completo com JWT**
  - 31 endpoints protegidos com autenticação
  - Hierarquia de permissões (Admin > Moderator > User > Público)
  - Proteção de endpoints críticos (/users, /site-config, etc)
  - Ver `SECURITY_FIXES_SUMMARY.md` para detalhes

- 📜 **Políticas e Termos**
  - Endpoint para política de privacidade (GET/PUT)
  - Endpoint para termos de serviço (GET/PUT)
  - Suporte a Markdown/HTML

## ✨ Novidades v2.2.0

- 📁 **Sistema completo de gerenciamento de arquivos**
  - Upload com validação (10MB, múltiplas extensões)
  - Organização automática por tipo e data
  - Limpeza automática de expirados (scheduler)
  - Controle de permissões e rastreamento
  - 9 endpoints REST completos
- 🖼️ **Extração de múltiplas imagens**
  - Até 10 imagens por produto
  - Suporte completo a .webp
  - Conversão para alta resolução

## ⚙️ Requisitos

- Python 3.12+
- MongoDB Atlas (ou local)
- Redis (opcional, mas recomendado para cache)
- OpenAI API Key (opcional, para categorização e tags com IA)

## 📦 Instalação

```bash
# 1. Criar virtual environment
python -m venv .venv

# 2. Ativar virtual environment
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt
```

## 🔧 Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
# MongoDB
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGO_DB=ecosystem_db

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (opcional)
REDIS_URL=redis://localhost:6379

# OpenAI (opcional)
OPENAI_API_KEY=sk-...

# Gerenciamento de Arquivos
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx,txt,mp4,mp3,webp
FILE_EXPIRY_DAYS=30
FILE_CLEANUP_ENABLED=true
FILE_CLEANUP_HOUR=3
FILE_CLEANUP_ORPHANS_ENABLED=false
```

## 🏃 Executar

```bash
# Desenvolvimento (com reload)
uvicorn app.main:app --reload

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testes

```bash
# Rodar todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Ver relatório HTML
open htmlcov/index.html  # ou abra manualmente no navegador

# Testar extrator Kabum
python test_kabum.py

# Testar Fase 1 (Backend Issues)
python test_phase1.py

# Testar Fase 2 (Analytics)
python test_phase2.py
```

## 📚 Documentação

Acesse após iniciar o servidor:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health/detailed

## 🔐 Autenticação e Segurança

### ⚠️ Sistema Totalmente Protegido (v2.2.0)

A partir da versão 2.2.0, **todos os endpoints sensíveis estão protegidos com JWT**. 

### Primeiro Acesso

**Apenas na primeira vez**, crie um usuário admin (endpoint aberto apenas se não houver usuários):

```bash
POST /users/
{
  "name": "Admin Principal",
  "email": "admin@xdesconto.com",
  "password": "AdminSecure123!",
  "role": "admin"
}
```

### Login

```bash
POST /users/login
{
  "email": "admin@xdesconto.com",
  "password": "AdminSecure123!"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { "id": "...", "role": "admin" }
}
```

### Usar Token

```bash
Authorization: Bearer {access_token}
```

### Níveis de Acesso

- **Admin**: Acesso total (deletar, configurações, operações em lote)
- **Moderator**: Criar/editar ofertas, posts, canais, cupons
- **User**: Extrair ofertas, usar cupons, gerenciar próprio perfil
- **Público**: Ver ofertas, cupons, canais (leitura apenas)

Ver documentação completa em `SECURITY_FIXES_SUMMARY.md`

## 📊 Sistema de Analytics (v2.3.0)

### Endpoints Disponíveis

**POST /analytics/click** - Registrar clique em oferta
```json
{
  "offer_id": "673a5e8f...",
  "source": "home"  // home, ofertas, dashboard, etc
}
```

**POST /analytics/pageview** - Registrar visualização de página
```json
{
  "page": "home"  // home, ofertas, cupons, etc
}
```

**GET /analytics/offer/{offer_id}** - Métricas de oferta
```json
{
  "offer_id": "...",
  "offer_title": "Produto XYZ",
  "total_clicks": 245,
  "clicks_by_source": {"home": 120, "ofertas": 100},
  "clicks_by_day": [{"date": "2025-11-01", "clicks": 45}],
  "last_30_days": 245
}
```

**GET /analytics/summary** - Resumo geral
```json
{
  "total_offer_clicks": 1234,
  "total_page_views": 5678,
  "most_clicked_offers": [...],
  "most_viewed_pages": {"home": 2500},
  "clicks_last_7_days": 456,
  "views_last_7_days": 1234
}
```

### Como Usar

```bash
# Registrar clique
curl -X POST http://localhost:8000/analytics/click \
  -H "Content-Type: application/json" \
  -d '{"offer_id": "123", "source": "home"}'

# Ver métricas de oferta
curl http://localhost:8000/analytics/offer/123

# Ver resumo geral
curl http://localhost:8000/analytics/summary
```

## 🆕 Novidades v2.1.0

### ✨ Features
- 🔐 Autenticação JWT completa
- 📁 **Sistema completo de gerenciamento de arquivos** (upload, download, organização, limpeza)
- 🖼️ **Extração de múltiplas imagens por produto** (até 10 imagens)
- 📊 Histórico de preços com 4 endpoints
- 🤖 Categorização automática com IA (16 categorias)
- 🏷️ **Geração automática de tags com IA** (máximo 5 tags inteligentes por oferta)
- ⚡ Cache Redis (TTL 1h)
- 🔄 Retry com backoff exponencial (3 tentativas)
- 🛡️ Rate limiting por IP
- 📝 Logs estruturados (JSON)
- ⏰ **Scheduler para limpeza automática** (APScheduler) ✨ NOVO
- 🏥 Health check detalhado (MongoDB + Redis + features)
- ✅ Testes automatizados (pytest + cobertura)

### 🔒 Endpoints Protegidos
- `PUT /offers/{id}` - Requer moderador
- `DELETE /offers/{id}` - Requer admin
- `POST /offers/{id}/generate-tags` - Requer moderador
- `POST /offers/batch/generate-tags` - Requer admin
- `POST /price-history/offer/{id}/record` - Requer moderador
- `PATCH /users/{id}/toggle-active` - Requer admin
- `POST /files/upload` - Requer autenticação ✨ NOVO
- `DELETE /files/{id}` - Requer dono ou admin ✨ NOVO
- `POST /files/cleanup/*` - Requer admin ✨ NOVO
- `GET /files/stats/storage` - Requer admin ✨ NOVO

## 📊 Estrutura do Projeto

```
app/
├── main.py                 # Aplicação FastAPI
├── core/
│   ├── database.py        # Configuração MongoDB
│   ├── security.py        # JWT e autenticação
│   ├── cache.py           # Redis
│   ├── logging.py         # Logs estruturados
│   └── validators.py      # Validadores customizados
├── models/                # Modelos Beanie
│   ├── offer.py
│   ├── post.py
│   ├── user.py
│   ├── affiliate.py
│   ├── channel.py
│   ├── site_config.py
│   ├── coupon.py
│   ├── price_history.py
│   ├── file_storage.py
│   ├── offer_click.py     # ✨ NOVO v2.3.0
│   └── page_view.py       # ✨ NOVO v2.3.0
├── routes/                # Endpoints
│   ├── offers.py
│   ├── posts.py
│   ├── users.py
│   ├── affiliates.py
│   ├── channels.py
│   ├── site_config.py
│   ├── coupons.py
│   ├── health.py
│   ├── price_history.py
│   ├── files.py
│   └── analytics.py       # ✨ NOVO v2.3.0
├── services/
│   ├── offer_extractor/   # Web scraping
│   │   ├── base.py
│   │   ├── factory.py
│   │   ├── mercadolivre.py
│   │   ├── shopee.py
│   │   ├── aliexpress.py
│   │   ├── amazon.py
│   │   └── kabum.py       # ✨ NOVO v2.3.1
│   ├── ai_categorization.py  # OpenAI IA categorização + tags
│   └── file_storage.py
└── tests/
    ├── conftest.py
    ├── test_api.py
    ├── test_phase1.py
    ├── test_phase2.py
    └── test_kabum.py      # ✨ NOVO v2.3.1
```

## 🏷️ Exemplos de Tags Geradas pela IA

```json
// Ar-condicionado Samsung
["ar-condicionado", "split", "samsung", "inverter", "12.000 btus"]

// PlayStation 5
["playstation 5", "slim", "825gb", "digital", "console"]

// Tênis Puma
["tênis", "masculino", "feminino", "puma", "club 5v5"]

// Placa-mãe Asus
["placa-mãe", "asus", "b550m-plus", "am4", "tuf gaming"]
```

**Como usar:**
- Tags são geradas automaticamente ao criar ofertas via `/extract-and-save`
- Endpoint `POST /offers/{id}/generate-tags` para ofertas individuais
- Endpoint `POST /offers/batch/generate-tags` para processar em lote

## 🐛 Troubleshooting

### Redis não conecta
O sistema funciona sem Redis, mas com funcionalidade degradada (sem cache).

### Categorização não funciona
Configure `OPENAI_API_KEY`. Fallback usa categorização por keywords.

### Testes falhando
```bash
# Verificar se MongoDB está acessível
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

## 📝 Licença

MIT

## 👥 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
3. Abra um Pull Request

---

**Versão**: 2.3.0  
**Última atualização**: 2025-11-10
