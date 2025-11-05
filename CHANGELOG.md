# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.2.1] - 2025-11-05

### 🔒 Segurança

- **Correção Crítica de Segurança - Autenticação JWT**
  - Protegidos **31 endpoints** que estavam sem autenticação
  - Sistema de hierarquia de permissões implementado (Admin > Moderator > User > Público)
  - Detalhes completos em `SECURITY_FIXES_SUMMARY.md`

#### Endpoints Protegidos:

**`/users` (CRÍTICO)**
- `POST /users/` → Requer `require_admin`
- `GET /users/` → Requer `get_current_user`
- `GET /users/{id}` → Requer `get_current_user` (dono ou admin)
- `PUT /users/{id}` → Requer `get_current_user` (dono ou admin)
- `DELETE /users/{id}` → Requer `require_admin`

**`/site-config` (CRÍTICO)**
- Todas operações de modificação → Requer `require_admin`

**`/posts`, `/channels`, `/affiliates`**
- POST, PUT → Requer `require_moderator`
- DELETE, toggle-active → Requer `require_admin`

**`/coupons`**
- POST, PUT → Requer `require_moderator`
- POST /{id}/use → Requer `get_current_user`
- DELETE, toggle-active → Requer `require_admin`

**`/offers`**
- POST /extract → Requer `get_current_user` (OpenAI custoso)
- POST / → Requer `require_moderator`

### ✨ Novidades

- **Endpoints para Políticas e Termos**
  - `GET /site-config/privacy-policy` - Obter política de privacidade (público)
  - `PUT /site-config/privacy-policy` - Atualizar política (admin)
  - `GET /site-config/terms-of-service` - Obter termos de serviço (público)
  - `PUT /site-config/terms-of-service` - Atualizar termos (admin)
  - Suporte a Markdown/HTML nos campos

### 🔧 Melhorias

- Adicionados campos `privacy_policy` e `terms_of_service` no modelo `SiteConfig`
- Documentação de segurança completa (`SECURITY_ANALYSIS.md`)

---

## [2.2.0] - 2025-11-04

### 🚀 Novidades Principais

- **Sistema de Gerenciamento de Arquivos**
  - Novo modelo `FileStorage` com campos completos (filename, mime_type, size, checksum, tags, etc)
  - Estrutura organizada: `uploads/{tipo}s/YYYY/MM/DD/`
  - 9 endpoints REST completos:
    - `POST /files/upload` - Upload com validação
    - `GET /files/` - Listagem com filtros (tipo, usuário, público, tags)
    - `GET /files/{id}` - Metadados do arquivo
    - `GET /files/{id}/download` - Download com contador
    - `DELETE /files/{id}` - Exclusão (próprios ou admin)
    - `POST /files/cleanup/expired` - Limpeza manual de expirados (admin)
    - `POST /files/cleanup/orphans` - Limpeza de órfãos (admin)
    - `GET /files/stats/storage` - Estatísticas (admin)
    - `GET /files/health/check` - Health check
  - Validações configuráveis:
    - Tamanho máximo: 10MB (padrão)
    - Extensões permitidas: jpg, jpeg, png, gif, webp, pdf, doc, docx, xls, xlsx, txt, mp4, mp3
    - Checksum MD5 para integridade
  - Scheduler automático (APScheduler):
    - Limpeza diária de expirados (3h da manhã)
    - Limpeza semanal de órfãos (opcional)
  - Sistema de permissões:
    - Usuários acessam próprios arquivos
    - Arquivos públicos visíveis para todos
    - Admins têm acesso total
  - Rastreamento completo:
    - Contador de downloads
    - Data de último acesso
    - Relacionamento com recursos (offer_id, post_id, etc)
    - Tags customizáveis

- **Extração de Múltiplas Imagens**
  - Novo campo `images: List[str]` no modelo `Offer`
  - Campo `image` mantido para compatibilidade (primeira imagem)
  - Extractors atualizados (Mercado Livre, Shopee, AliExpress):
    - Busca em galeria de produtos
    - Busca em carrossel de thumbnails
    - Conversão automática para imagens em alta resolução
    - Suporte a `.webp` e `.jpg`
    - Filtragem de imagens de produto (NQ_NP)
    - Limite de 10 imagens por produto
  - Log de quantidade de imagens extraídas
  - Remoção automática de duplicatas

### 🔧 Melhorias
- Suporte completo a arquivos `.webp`
- Correção de autenticação em endpoints de arquivos
- Sistema de cleanup automático configurável via `.env`
- Logs estruturados para operações de arquivo

### 📦 Dependências
- Adicionado: `apscheduler==3.10.4`

### ⚙️ Variáveis de Ambiente
```env
# Configuração de Armazenamento de Arquivos
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx,txt,mp4,mp3,webp
FILE_EXPIRY_DAYS=30
FILE_CLEANUP_ENABLED=true
FILE_CLEANUP_HOUR=3
FILE_CLEANUP_ORPHANS_ENABLED=false
```

---

## [2.1.0] - 2025-11-03

### 🚀 Novidades Principais
- **Autenticação JWT completa**
  - Sistema de tokens JWT para autenticação segura
  - Decoradores `@require_auth`, `@require_admin`, `@require_moderator`
  - Endpoint `/users/me` para obter usuário autenticado
  - Login retorna `access_token` e `token_type: bearer`
  - Endpoints sensíveis protegidos (DELETE ofertas requer admin, UPDATE requer moderator)

- **Cache Redis**
  - Cache de extrações com TTL de 1 hora
  - Chave baseada em hash MD5 da URL
  - Fallback gracioso quando Redis não disponível
  - Endpoint `/health/detailed` mostra status do Redis

- **Retry com backoff exponencial**
  - Biblioteca `tenacity` integrada
  - 3 tentativas com espera exponencial (2s, 4s, 8s)
  - Aplicado em todas as extrações de ofertas

- **Rate Limiting**
  - Biblioteca `slowapi` integrada
  - Proteção contra abuso de API
  - Limitação por IP do cliente

- **Logs estruturados**
  - Biblioteca `structlog` configurada
  - Logs em formato JSON para análise
  - Eventos rastreados: extraction_started, offer_created, price_history_recorded, tags_generated, etc
  - Níveis: info, warning, error com contexto completo

- **Health Check detalhado**
  - Endpoint `/health/` para check básico
  - Endpoint `/health/detailed` com status de MongoDB, Redis e features
  - Versão da aplicação e Python incluídos

- **Histórico de preços**
  - Novo modelo `PriceHistory` para rastrear variações
  - Registro automático ao criar/atualizar ofertas
  - 4 novos endpoints:
    - `GET /price-history/offer/{id}` - Histórico completo
    - `GET /price-history/offer/{id}/variation` - Variação percentual
    - `GET /price-history/offer/{id}/lowest` - Menor preço registrado
    - `POST /price-history/offer/{id}/record` - Registrar manualmente

- **Categorização automática com IA**
  - Integração com OpenAI GPT-3.5-turbo
  - 16 categorias pré-definidas
  - Fallback para categorização por keywords quando IA não disponível
  - Aplicado automaticamente em `/extract-and-save`

- **Geração automática de tags com IA** ✨ NOVO
  - Tags inteligentes geradas via OpenAI GPT-3.5-turbo
  - Máximo de 5 tags relevantes por oferta
  - Análise de título, descrição e categoria
  - Fallback para extração por keywords
  - 3 novos endpoints:
    - `POST /offers/{id}/generate-tags` - Gera tags para oferta específica (moderator)
    - `POST /offers/batch/generate-tags` - Gera tags em lote para todas ofertas sem tags (admin)
  - Tags automáticas ao criar novas ofertas em `/extract-and-save`
  - Exemplos de tags: `["ar-condicionado", "split", "samsung", "inverter", "12.000 btus"]`

- **Validadores Pydantic customizados**
  - `validate_url()` - Valida URLs HTTP/HTTPS
  - `validate_password_strength()` - Senha forte (min 8 chars, maiúsc, minúsc, número)
  - `validate_text_length()` - Limite de caracteres configurável
  - `validate_slug()` - Formato de slug válido

- **Testes automatizados**
  - Configurado `pytest` + `pytest-asyncio` + `pytest-cov`
  - Cobertura mínima exigida: 70%
  - 8 testes iniciais cobrindo endpoints principais
  - Arquivo `pytest.ini` com configurações
  - Relatório HTML de cobertura

### 🔧 Modificações
- Versão atualizada para `2.1.0`
- `main.py`: Integrado Redis, structlog, slowapi e IA
- `database.py`: Adicionado `PriceHistory` aos modelos
- `users.py`: Login retorna JWT token
- `offers.py`: Protegido UPDATE (moderator) e DELETE (admin), adicionada geração de tags
- `cache.py`: Adicionado `load_dotenv()` para carregar variáveis de ambiente
- `ai_categorization.py`: Adicionado `load_dotenv()` e funções `generate_tags()` e `generate_tags_by_keywords()`
- `offers.py`: Cache e retry em extrações
- `offers.py`: Registro automático no histórico de preços
- `offers.py`: Categorização automática com IA

### 📦 Dependências Adicionadas
- `python-jose[cryptography]==3.3.0` - JWT
- `python-multipart==0.0.9` - Upload de arquivos
- `redis==5.0.1` - Cache
- `slowapi==0.1.9` - Rate limiting
- `tenacity==8.2.3` - Retry com backoff
- `structlog==23.3.0` - Logs estruturados
- `pytest==7.4.3` - Testes
- `pytest-asyncio==0.21.1` - Testes assíncronos
- `pytest-cov==4.1.0` - Cobertura de código
- `httpx==0.25.2` - Cliente HTTP para testes
- `openai==1.54.0` - Categorização com IA

### 🔐 Segurança
- Endpoints administrativos protegidos com JWT
- Validação de senhas fortes
- Rate limiting contra abuso
- Logs estruturados para auditoria

### 📝 Variáveis de Ambiente
Adicionadas ao `.env`:
```
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=... (opcional)
```

---

## [2.0.1] - 2025-11-03

### 🐛 Corrigido
- **Campo `extract_url` preservando URL original**
  - Adicionado `extract_url` ao schema `OfferUpdate` para preservar durante atualizações
  - Endpoint POST `/offers/` agora usa fallback `extract_url = data.extract_url or data.url`
  - Campo `extract_url` sempre guarda a URL curta/original enviada na request (melhor para compartilhar)
  - Campo `url` guarda a URL longa após redirecionamento (melhor para scraping)
  - Script de correção aplicado em 11 ofertas antigas que estavam com `extract_url` null

- **Conversão de preços brasileiros**
  - Criada função `convert_price_to_float()` para tratar formatos de preço brasileiros
  - Corrige conversão de valores como "5.950" que eram interpretados como 5.95 em vez de 5950.0
  - Suporta múltiplos formatos: "5.950" → 5950.0, "3.254,99" → 3254.99, "10,50" → 10.5
  - Detecta automaticamente se o ponto é separador de milhar ou decimal

### 📝 Nota para Frontend
- **Recomendação**: Usar endpoint `/offers/extract-and-save` que já extrai e salva corretamente
- **Alternativa**: Ao usar `/extract` + POST `/offers/`, enviar `extract_url` com a URL original no payload

---

## [2.0.0] - 2025-10-31

### 🎉 Adicionado
- **CRUD completo de Afiliados** (`/affiliates`)
  - Modelo `Affiliate` com campos: name, slug, url, logo, api_key, commission_rate, etc
  - 7 endpoints: criar, listar, buscar por ID, buscar por slug, atualizar, deletar, toggle-active
  - Validação de slug único e priorização por ordem

- **CRUD completo de Canais** (`/channels`)
  - Modelo `Channel` para gerenciar canais de publicação (Telegram, WhatsApp, Instagram, Site, Email, Discord)
  - 9 endpoints: criar, listar, buscar por ID, buscar por slug, atualizar, deletar, toggle-active, listar ativos, atualizar estatísticas
  - Suporte a credenciais de API, webhooks e configurações customizadas por canal
  - Estatísticas de posts: total_posts, success_rate, last_post_at

- **CRUD de Configurações do Site** (`/site-config`)
  - Modelo `SiteConfig` singleton para configurações globais do site
  - 7 endpoints: obter config, atualizar completa, atualizar redes sociais, atualizar links de grupos, atualizar "Sobre Nós", toggle modo manutenção, resetar
  - Suporte a redes sociais, links de grupos, sobre nós, contato, SEO e analytics
  - Modo de manutenção configurável

- **CRUD completo de Cupons** (`/coupons`)
  - Modelo `Coupon` com validação inteligente de cupons de desconto
  - 9 endpoints: criar, listar, buscar por ID, buscar por código, validar, usar/incrementar, atualizar, deletar, toggle-active
  - Tipos de desconto: percentual, fixo, frete grátis
  - Validação de datas, limites de uso, valor mínimo de compra
  - Sistema de uso/contador integrado

- **Endpoint DELETE para Posts**
  - DELETE `/posts/{post_id}` - Remove post por ID
  - DELETE `/posts/offer/{offer_id}` - Remove todos posts de uma oferta
  - Deleção automática de posts ao deletar oferta

### 🔧 Modificado
- Versão da API atualizada para `2.0.0`
- `main.py`: Registrados 4 novos routers (affiliates, channels, site_config, coupons)
- `database.py`: Registrados 4 novos modelos no Beanie
- Descrição da aplicação atualizada no FastAPI

### 📚 Documentação
- Criado arquivo `CHANGELOG.md` para rastreamento de versões
- Documentação da API será atualizada com os novos endpoints

---

## [1.0.0] - 2025-10-28

### 🎉 Adicionado
- **CRUD completo de Ofertas** (`/offers`)
  - Extração automática de dados de URLs (Mercado Livre, AliExpress, Shopee)
  - Validação anti-duplicatas (por URL e título+preço+data)
  - 8 endpoints: extract, extract-and-save, criar, listar, buscar, atualizar, deletar, health-check
  - Criação automática de posts para múltiplos canais

- **CRUD de Posts** (`/posts`)
  - Gerenciamento de publicações em canais (Telegram, WhatsApp, Site, Instagram)
  - 2 endpoints: listar com filtros, atualizar status

- **CRUD completo de Usuários** (`/users`)
  - Sistema de autenticação com bcrypt
  - 7 endpoints: criar, listar, buscar, atualizar, deletar, login, toggle-active
  - Roles: user, admin, moderator
  - Validação de email único

- **Sistema de Web Scraping**
  - Factory pattern para extratores por plataforma
  - Extrator completo para Mercado Livre
  - Extrator parcial para AliExpress
  - Detecção de CAPTCHA para Shopee

### 🔧 Configuração
- MongoDB Atlas integrado com Beanie ODM
- CORS configurado para localhost:3000 e localhost:3001
- Variáveis de ambiente (.env) para MongoDB

### 📚 Documentação
- `API_DOCUMENTATION.md` completa com exemplos
- Swagger UI disponível em `/docs`
- ReDoc disponível em `/redoc`

---

## Tipos de Mudanças
- `Adicionado` para novas funcionalidades
- `Modificado` para mudanças em funcionalidades existentes
- `Descontinuado` para funcionalidades que serão removidas
- `Removido` para funcionalidades removidas
- `Corrigido` para correção de bugs
- `Segurança` para vulnerabilidades

---

## Links
- [Repositório](https://github.com/seu-usuario/bff-ecossistema)
- [Documentação da API](./API_DOCUMENTATION.md)
- [Issues](https://github.com/seu-usuario/bff-ecossistema/issues)
