# 📚 Documentação da API - Ecosystem Backend v2.2.1

> **Backend completo com JWT, Cache Redis, IA, Histórico de Preços, Gerenciamento de Arquivos e Sistema de Segurança Robusto!**

## 🌐 Base URL
```
http://localhost:8000
```

## 📖 Documentação Interativa
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔒 Autenticação JWT

A partir da v2.2.1, **todos os endpoints sensíveis estão protegidos com JWT**. Ver `SECURITY_FIXES_SUMMARY.md` para detalhes completos.

### Como Autenticar

1. **Login:**
```bash
POST /users/login
{
  "email": "admin@example.com",
  "password": "senha"
}
```

2. **Usar Token:**
```bash
Authorization: Bearer {access_token}
```

### Níveis de Acesso

- **Admin**: Acesso total (DELETE, configurações, operações em lote)
- **Moderator**: Criar/editar recursos (POST, PUT, PATCH)
- **User**: Operações básicas (extrair ofertas, usar cupons)
- **Público**: Leitura de dados não-sensíveis (GET ofertas, cupons, etc)

---

## 🆕 Novidades v2.2.1

### � Sistema de Segurança Completo ✨ NOVO
- 31 endpoints protegidos com autenticação JWT
- Hierarquia de permissões (Admin > Moderator > User > Público)
- Proteção de endpoints críticos (/users, /site-config, etc)

### 📜 Endpoints de Políticas e Termos ✨ NOVO
- `GET /site-config/privacy-policy` - Política de privacidade (público)
- `PUT /site-config/privacy-policy` - Atualizar política (admin)
- `GET /site-config/terms-of-service` - Termos de serviço (público)
- `PUT /site-config/terms-of-service` - Atualizar termos (admin)

---

## 🆕 Novidades v2.2.0

### 📁 Sistema de Gerenciamento de Arquivos
Upload, download, listagem e exclusão de arquivos com organização automática
- `POST /files/upload` - Upload com validação (max 10MB) **🔒 Auth**
- `GET /files/` - Listar com filtros (tipo, tags, público) **🔒 Auth**
- `GET /files/{id}` - Metadados do arquivo **🔒 Auth**
- `GET /files/{id}/download` - Download com rastreamento **🔒 Auth**
- `DELETE /files/{id}` - Exclusão (próprios ou admin) **🔒 Auth**
- Estrutura organizada: `uploads/{tipo}s/YYYY/MM/DD/`
- Extensões permitidas: jpg, jpeg, png, gif, webp, pdf, doc, docx, xls, xlsx, txt, mp4, mp3
- Limpeza automática de expirados (diária às 3h)

### 🖼️ Extração de Múltiplas Imagens
Agora extrai até 10 imagens por produto (Mercado Livre, Shopee, AliExpress)
- Novo campo `images: List[str]` no modelo Offer
- Campo `image` mantido (primeira imagem, compatibilidade)
- Conversão automática para alta resolução
- Suporte completo a `.webp`

## 🆕 Novidades v2.1.0

### 🔐 Autenticação JWT
Endpoints sensíveis requerem autenticação. Faça login para obter token:
```bash
POST /users/login
Authorization: Bearer {token}
```

### 📊 Histórico de Preços
- `GET /price-history/offer/{id}` - Histórico completo (últimos 30 dias)
- `GET /price-history/offer/{id}/variation` - Variação percentual
- `GET /price-history/offer/{id}/lowest` - Menor preço registrado
- `POST /price-history/offer/{id}/record` - Registrar manualmente (moderador)

### 🤖 IA - Categorização Automática
Ofertas são categorizadas automaticamente com OpenAI GPT-3.5 em 16 categorias

### �️ IA - Geração Automática de Tags
Tags inteligentes geradas via OpenAI GPT-3.5 (máximo 5 por oferta)
- `POST /offers/{id}/generate-tags` - Gera tags para oferta específica
- `POST /offers/batch/generate-tags` - Gera tags em lote para todas ofertas sem tags

### �🏥 Health Check
- `GET /health/` - Status básico
- `GET /health/detailed` - MongoDB, Redis, Python version, features

### ⚡ Performance & Segurança
- ✅ Cache Redis (TTL 1h nas extrações)
- ✅ Retry automático (3x com backoff exponencial)
- ✅ Rate limiting por IP
- ✅ Logs estruturados JSON
- ✅ Validadores Pydantic customizados

---

## � Observação Importante: Campos `url` vs `extract_url`

- **`url`**: URL completa/longa após redirecionamento (usada para scraping e garantir acesso ao produto)
- **`extract_url`**: URL curta/original enviada na requisição (ideal para compartilhar no Telegram/WhatsApp)

**Exemplo:**
```json
{
  "extract_url": "https://mercadolivre.com/sec/2sLbH4a",  // ← URL curta (compartilhar)
  "url": "https://www.mercadolivre.com.br/produto-completo..."  // ← URL longa (scraping)
}
```

**💡 Recomendação:** Use `/offers/extract-and-save` que configura ambos automaticamente.

---

## �🚀 Recursos Principais
- ✅ Extração automática de ofertas (Mercado Livre, AliExpress, Shopee)
- ✅ **Extração de múltiplas imagens por produto (até 10)**
- ✅ Sistema anti-duplicatas inteligente
- ✅ CRUD completo de ofertas
- ✅ **Gerenciamento completo de arquivos (upload, download, organização automática)**
- ✅ Gerenciamento de posts multi-canal (Telegram, WhatsApp, Site, Instagram)
- ✅ **Sistema de usuários com autenticação**
- ✅ **Controle de permissões (user, admin, moderator)**
- ✅ **Senha criptografada com bcrypt**
- ✅ **Gerenciamento de sites afiliados**
- ✅ **Gerenciamento de canais de publicação**
- ✅ **Configurações globais do site**
- ✅ **Sistema de cupons de desconto com validação**

## 📊 Resumo de Endpoints

| Recurso | Método | Endpoint | Descrição |
|---------|--------|----------|-----------|
| **Ofertas** | POST | `/offers/extract` | Extrair dados de URL |
| | POST | `/offers/extract-and-save` | Extrair e salvar automaticamente |
| | POST | `/offers/` | Criar nova oferta |
| | GET | `/offers/` | Listar ofertas (com filtros) |
| | GET | `/offers/{offer_id}` | Buscar oferta específica |
| | PUT | `/offers/{offer_id}` | Atualizar oferta (moderador) |
| | DELETE | `/offers/{offer_id}` | Excluir oferta (admin) |
| | POST | `/offers/{offer_id}/generate-tags` | Gerar tags com IA (moderador) ✨ |
| | POST | `/offers/batch/generate-tags` | Gerar tags em lote (admin) ✨ |
| | GET | `/offers/health/check` | Health check |
| **Arquivos** | POST | `/files/upload` | Upload de arquivo (autenticado) ✨ |
| | GET | `/files/` | Listar arquivos com filtros ✨ |
| | GET | `/files/{id}` | Obter metadados do arquivo ✨ |
| | GET | `/files/{id}/download` | Download do arquivo ✨ |
| | DELETE | `/files/{id}` | Excluir arquivo (próprio/admin) ✨ |
| | POST | `/files/cleanup/expired` | Limpeza manual de expirados (admin) ✨ |
| | POST | `/files/cleanup/orphans` | Limpeza manual de órfãos (admin) ✨ |
| | GET | `/files/stats/storage` | Estatísticas de armazenamento (admin) ✨ |
| | GET | `/files/health/check` | Health check do serviço ✨ |
| **Usuários** | POST | `/users/` | Criar usuário |
| | GET | `/users/` | Listar usuários |
| | GET | `/users/{user_id}` | Buscar usuário |
| | PUT | `/users/{user_id}` | Atualizar usuário |
| | DELETE | `/users/{user_id}` | Excluir usuário |
| | POST | `/users/login` | Autenticar usuário |
| | PATCH | `/users/{user_id}/toggle-active` | Ativar/desativar usuário |
| **Posts** | GET | `/posts/` | Listar posts (com filtros) |
| | PATCH | `/posts/{post_id}` | Atualizar status do post |
| | DELETE | `/posts/{post_id}` | Excluir post por ID |
| | DELETE | `/posts/offer/{offer_id}` | Excluir todos posts associados a uma oferta |
| **Afiliados** | POST | `/affiliates/` | Criar site afiliado |
| | GET | `/affiliates/` | Listar afiliados |
| | GET | `/affiliates/{affiliate_id}` | Buscar afiliado por ID |
| | GET | `/affiliates/slug/{slug}` | Buscar afiliado por slug |
| | PUT | `/affiliates/{affiliate_id}` | Atualizar afiliado |
| | DELETE | `/affiliates/{affiliate_id}` | Excluir afiliado |
| | PATCH | `/affiliates/{affiliate_id}/toggle-active` | Ativar/desativar afiliado |
| **Canais** | POST | `/channels/` | Criar canal |
| | GET | `/channels/` | Listar canais |
| | GET | `/channels/active` | Listar canais ativos |
| | GET | `/channels/{channel_id}` | Buscar canal por ID |
| | GET | `/channels/slug/{slug}` | Buscar canal por slug |
| | PUT | `/channels/{channel_id}` | Atualizar canal |
| | DELETE | `/channels/{channel_id}` | Excluir canal |
| | PATCH | `/channels/{channel_id}/toggle-active` | Ativar/desativar canal |
| | PATCH | `/channels/{channel_id}/stats` | Atualizar estatísticas |
| **Config** | GET | `/site-config/` | Obter configuração do site |
| | PUT | `/site-config/` | Atualizar configuração **🔒 Admin** |
| | PATCH | `/site-config/social-media` | Atualizar redes sociais **🔒 Admin** |
| | PATCH | `/site-config/group-links` | Atualizar links de grupos **🔒 Admin** |
| | PATCH | `/site-config/about-us` | Atualizar "Sobre Nós" **🔒 Admin** |
| | PATCH | `/site-config/maintenance-mode` | Toggle modo manutenção **🔒 Admin** |
| | POST | `/site-config/reset` | Resetar configuração **🔒 Admin** |
| | GET | `/site-config/privacy-policy` | Obter política de privacidade |
| | PUT | `/site-config/privacy-policy` | Atualizar política **🔒 Admin** |
| | GET | `/site-config/terms-of-service` | Obter termos de serviço |
| | PUT | `/site-config/terms-of-service` | Atualizar termos **🔒 Admin** |
| **Cupons** | POST | `/coupons/` | Criar cupom **🔒 Moderator** |
| | GET | `/coupons/` | Listar cupons |
| | GET | `/coupons/{coupon_id}` | Buscar cupom por ID |
| | GET | `/coupons/code/{code}` | Buscar cupom por código |
| | POST | `/coupons/validate` | Validar cupom |
| | POST | `/coupons/{coupon_id}/use` | Usar/incrementar cupom |
| | PUT | `/coupons/{coupon_id}` | Atualizar cupom |
| | DELETE | `/coupons/{coupon_id}` | Excluir cupom |
| | PATCH | `/coupons/{coupon_id}/toggle-active` | Ativar/desativar cupom |

---

## 🎯 Endpoints Principais

### 1. OFERTAS (`/offers`) - 8 endpoints

**POST** `/offers/extract`

Extrai informações de produto de uma URL (Mercado Livre, AliExpress, Shopee).

**Request Body:**
```json
{
  "url": "https://mercadolivre.com/sec/2sLbH4a"
}
```

**Response 200:**
```json
{
  "status": "success",
  "data": }
---

#### 3.3 Excluir Post por ID
**DELETE** `/posts/{post_id}`

Remove um post específico do sistema.

**Response 200:**
```json
{
  "status": "deleted",
  "id": "673f2b1c5e8c9d4a2b1c3d5f"
}
```

**Response 404:**
```json
{
  "detail": "Post não encontrado"
}
```

---

#### 3.4 Excluir Posts por Offer ID
**DELETE** `/posts/offer/{offer_id}`

Remove todos os posts relacionados a uma oferta (útil ao remover uma oferta manualmente).

**Response 200 (quando houver posts):**
```json
{
  "status": "deleted",
  "offer_id": "673f2a1b5e8c9d4a2b1c3d4e",
  "deleted_count": 4,
  "deleted_ids": [
    "673f2b1c5e8c9d4a2b1c3d5f",
    "673f2b1c5e8c9d4a2b1c3d60",
    "673f2b1c5e8c9d4a2b1c3d61",
    "673f2b1c5e8c9d4a2b1c3d62"
  ]
}
```

**Response 200 (quando não houver posts):**
```json
{
  "status": "no_content",
  "message": "Nenhum post encontrado para essa oferta",
  "offer_id": "673f2a1b5e8c9d4a2b1c3d4e"
}
```

---

## 🔄 Fluxo Recomendado
    "source": "Mercado Livre",
    "title": "Samsung Galaxy A06 Dual Sim 128 Gb",
    "price": "608",
    "original_price": "900.90",
    "discount": "32% OFF",
    "installments": "12x R$50.67 sem juros",
    "currency": "BRL",
    "image": "https://http2.mlstatic.com/...",
    "description": "Descrição do produto",
    "note": null
  }
}
```

---

#### 1.2 Extrair e Salvar Automaticamente
**POST** `/offers/extract-and-save`

Extrai dados da URL, verifica duplicatas e salva automaticamente no banco.

**Request Body:**
```json
{
  "url": "https://mercadolivre.com/sec/2sLbH4a"
}
```

**Response 200 (Sucesso):**
```json
{
  "status": "success",
  "message": "Oferta extraída e salva com sucesso",
  "id": "673f2a1b5e8c9d4a2b1c3d4e",
  "extracted_data": { /* dados extraídos */ },
  "offer": {
    "_id": "673f2a1b5e8c9d4a2b1c3d4e",
    "source": "Mercado Livre",
    "url": "https://www.mercadolivre.com.br/...",
    "extract_url": "https://mercadolivre.com/sec/2sLbH4a",
    "title": "Samsung Galaxy A06",
    "price_original": 900.90,
    "price_discounted": 608.0,
    "discount": "32% OFF",
    "installments": "12x R$50.67 sem juros",
    "currency": "BRL",
    "image": "https://...",
    "description": "...",
    "note": null,
    "category": null,
    "tags": [],
    "optimized_message": null,
    "status": "pending",
    "created_at": "2025-10-28T10:30:00",
    "updated_at": "2025-10-28T10:30:00"
  }
}
```

**Response 200 (Duplicata):**
```json
{
  "status": "duplicate",
  "message": "Oferta duplicada: já existe uma oferta com mesmo título e preço criada hoje ou mesma URL",
  "existing_offer_id": "673f2a1b5e8c9d4a2b1c3d4e",
  "extracted_data": { /* dados extraídos */ },
  "existing_offer": { /* oferta existente */ }
}
```

---

#### 1.3 Criar Oferta Manualmente
**POST** `/offers/`

Cria uma nova oferta no banco de dados.

**Request Body:**
```json
{
  "source": "Mercado Livre",
  "url": "https://www.mercadolivre.com.br/...",
  "extract_url": "https://mercadolivre.com/sec/2sLbH4a",
  "title": "Samsung Galaxy A06",
  "price_original": 900.90,
  "price_discounted": 608.0,
  "discount": "32% OFF",
  "installments": "12x R$50.67 sem juros",
  "currency": "BRL",
  "image": "https://...",
  "description": "Descrição",
  "category": "Eletrônicos",
  "tags": ["smartphone", "samsung"],
  "optimized_message": "🔥 OFERTA IMPERDÍVEL!",
  "note": null,
  "status": "pending"
}
```

**Response 200:**
```json
{
  "status": "success",
  "id": "673f2a1b5e8c9d4a2b1c3d4e",
  "data": { /* oferta criada */ }
}
```

---

#### 1.4 Listar Ofertas
**GET** `/offers/`

Lista todas as ofertas com filtros opcionais.

**Query Parameters:**
- `status` (opcional): pending | approved | rejected
- `source` (opcional): Mercado Livre | AliExpress | Shopee
- `limit` (opcional, padrão: 50): Número máximo de resultados
- `skip` (opcional, padrão: 0): Paginação

**Exemplo:**
```
GET /offers/?status=pending&source=Mercado Livre&limit=20&skip=0
```

**Response 200:**
```json
{
  "total": 150,
  "limit": 20,
  "skip": 0,
  "data": [
    {
      "_id": "673f2a1b5e8c9d4a2b1c3d4e",
      "source": "Mercado Livre",
      "url": "https://...",
      "extract_url": "https://mercadolivre.com/sec/2sLbH4a",
      "title": "Samsung Galaxy A06",
      "price_original": 900.90,
      "price_discounted": 608.0,
      "discount": "32% OFF",
      "installments": "12x R$50.67 sem juros",
      "currency": "BRL",
      "image": "https://...",
      "status": "pending",
      "created_at": "2025-10-28T10:30:00"
    }
  ]
}
```

---

#### 1.5 Buscar Oferta por ID
**GET** `/offers/{offer_id}`

Retorna uma oferta específica.

**Response 200:**
```json
{
  "_id": "673f2a1b5e8c9d4a2b1c3d4e",
  "source": "Mercado Livre",
  "title": "Samsung Galaxy A06",
  /* ... todos os campos ... */
}
```

**Response 404:**
```json
{
  "detail": "Oferta não encontrada"
}
```

---

#### 1.6 Atualizar Oferta
**PUT** `/offers/{offer_id}`

Atualiza uma oferta existente.

**Request Body (campos opcionais):**
```json
{
  "title": "Novo título",
  "price_discounted": 550.0,
  "discount": "40% OFF",
  "optimized_message": "🔥 SUPER OFERTA!",
  "status": "approved",
  "tags": ["promoção", "destaque"]
}
```

**Response 200:**
```json
{
  "status": "updated",
  "data": { /* oferta atualizada */ }
}
```

---

#### 1.7 Excluir Oferta
**DELETE** `/offers/{offer_id}`

Remove uma oferta do banco de dados.

**Response 200:**
```json
{
  "status": "deleted",
  "id": "673f2a1b5e8c9d4a2b1c3d4e"
}
```

---

#### 1.8 Health Check
**GET** `/offers/health/check`

Verifica se o serviço está funcionando.

**Response 200:**
```json
{
  "status": "ok"
}
```

---

### 2. USUÁRIOS (`/users`)

Gerencia usuários do sistema para administração.

#### 2.1 Criar Usuário
**POST** `/users/`

Cria um novo usuário no sistema.

**Request Body:**
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "password": "senha123",
  "role": "user",
  "avatar": "https://example.com/avatar.jpg",
  "bio": "Administrador do sistema"
}
```

**Campos:**
- `name` (obrigatório): Nome completo (mín. 3 caracteres)
- `email` (obrigatório): Email válido e único
- `password` (obrigatório): Senha (mín. 6 caracteres)
- `role` (opcional): "user" | "admin" | "moderator" (padrão: "user")
- `avatar` (opcional): URL da foto
- `bio` (opcional): Biografia

**Response 201:**
```json
{
  "status": "success",
  "message": "Usuário criado com sucesso",
  "id": "673f3a1b5e8c9d4a2b1c3d7e",
  "data": {
    "id": "673f3a1b5e8c9d4a2b1c3d7e",
    "name": "João Silva",
    "email": "joao@example.com",
    "role": "user",
    "is_active": true,
    "avatar": "https://example.com/avatar.jpg",
    "bio": "Administrador do sistema",
    "created_at": "2025-10-28T10:30:00",
    "updated_at": "2025-10-28T10:30:00"
  }
}
```

**Response 400:**
```json
{
  "detail": "Email já cadastrado"
}
```

---

#### 2.2 Listar Usuários
**GET** `/users/`

Lista todos os usuários com filtros opcionais.

**Query Parameters:**
- `role` (opcional): user | admin | moderator
- `is_active` (opcional): true | false
- `limit` (opcional): Número de resultados (padrão: 50)
- `skip` (opcional): Paginação offset (padrão: 0)

**Exemplo:**
```
GET /users/?role=admin&is_active=true&limit=10
```

**Response 200:**
```json
{
  "total": 25,
  "limit": 10,
  "skip": 0,
  "data": [
    {
      "id": "673f3a1b5e8c9d4a2b1c3d7e",
      "name": "João Silva",
      "email": "joao@example.com",
      "role": "admin",
      "is_active": true,
      "avatar": "https://example.com/avatar.jpg",
      "bio": "Administrador do sistema",
      "created_at": "2025-10-28T10:30:00",
      "updated_at": "2025-10-28T10:30:00",
      "last_login": "2025-10-28T12:00:00"
    }
  ]
}
```

---

#### 2.3 Buscar Usuário por ID
**GET** `/users/{user_id}`

Retorna dados de um usuário específico.

**Response 200:**
```json
{
  "id": "673f3a1b5e8c9d4a2b1c3d7e",
  "name": "João Silva",
  "email": "joao@example.com",
  "role": "admin",
  "is_active": true,
  "avatar": "https://example.com/avatar.jpg",
  "bio": "Administrador do sistema",
  "created_at": "2025-10-28T10:30:00",
  "updated_at": "2025-10-28T10:30:00",
  "last_login": "2025-10-28T12:00:00"
}
```

**Response 404:**
```json
{
  "detail": "Usuário não encontrado"
}
```

---

#### 2.4 Atualizar Usuário
**PUT** `/users/{user_id}`

Atualiza dados de um usuário existente.

**Request Body (todos campos opcionais):**
```json
{
  "name": "João Silva Santos",
  "email": "novo@example.com",
  "password": "novaSenha123",
  "role": "admin",
  "is_active": true,
  "avatar": "https://example.com/new-avatar.jpg",
  "bio": "Nova biografia"
}
```

**Response 200:**
```json
{
  "status": "success",
  "message": "Usuário atualizado com sucesso",
  "data": {
    "id": "673f3a1b5e8c9d4a2b1c3d7e",
    "name": "João Silva Santos",
    "email": "novo@example.com",
    "role": "admin",
    "is_active": true,
    "avatar": "https://example.com/new-avatar.jpg",
    "bio": "Nova biografia",
    "updated_at": "2025-10-28T14:00:00"
  }
}
```

**Response 400:**
```json
{
  "detail": "Email já está em uso"
}
```

---

#### 2.5 Excluir Usuário
**DELETE** `/users/{user_id}`

Remove um usuário do sistema.

**Response 200:**
```json
{
  "status": "success",
  "message": "Usuário excluído com sucesso",
  "id": "673f3a1b5e8c9d4a2b1c3d7e"
}
```

---

#### 2.6 Login
**POST** `/users/login`

Autentica um usuário no sistema.

**Request Body:**
```json
{
  "email": "joao@example.com",
  "password": "senha123"
}
```

**Response 200:**
```json
{
  "status": "success",
  "message": "Login realizado com sucesso",
  "user": {
    "id": "673f3a1b5e8c9d4a2b1c3d7e",
    "name": "João Silva",
    "email": "joao@example.com",
    "role": "admin",
    "avatar": "https://example.com/avatar.jpg",
    "bio": "Administrador do sistema"
  }
}
```

**Response 401:**
```json
{
  "detail": "Email ou senha incorretos"
}
```

**Response 403:**
```json
{
  "detail": "Usuário inativo"
}
```

---

#### 2.7 Ativar/Desativar Usuário
**PATCH** `/users/{user_id}/toggle-active`

Alterna o status ativo/inativo de um usuário.

**Response 200:**
```json
{
  "status": "success",
  "message": "Usuário ativado com sucesso",
  "is_active": true
}
```

---

### 3. POSTS (`/posts`)

Gerencia o status de publicação das ofertas nos canais.

#### 3.1 Listar Posts
**GET** `/posts/`

Lista posts com filtros opcionais.

**Query Parameters:**
- `enviado` (opcional): true | false
- `status` (opcional): pending | success | failed
- `offer_id` (opcional): ID da oferta
- `channel` (opcional): telegram | whatsapp | site | instagram

**Exemplo:**
```
GET /posts/?enviado=false&status=pending&channel=telegram
```

**Response 200:**
```json
[
  {
    "_id": "673f2b1c5e8c9d4a2b1c3d5f",
    "offer_id": "673f2a1b5e8c9d4a2b1c3d4e",
    "channel": "telegram",
    "enviado": false,
    "status": "pending",
    "responses": {},
    "error": null,
    "created_at": "2025-10-28T10:30:00",
    "updated_at": "2025-10-28T10:30:00"
  }
]
```

---

#### 3.2 Atualizar Status do Post
**PATCH** `/posts/{post_id}`

Atualiza o status de um post (usado pelo n8n após enviar).

**Request Body:**
```json
{
  "enviado": true,
  "status": "success",
  "responses": {
    "message_id": "12345",
    "timestamp": "2025-10-28T10:35:00"
  }
}
```

**Response 200:**
```json
{
  "status": "updated",
  "id": "673f2b1c5e8c9d4a2b1c3d5f"
}
```

---

### 4. AFILIADOS (`/affiliates`)

Gerencia sites afiliados (Shopee, Mercado Livre, AliExpress, Amazon, etc).

#### 4.1 Criar Afiliado
**POST** `/affiliates/`

Cria um novo site afiliado.

**Request Body:**
```json
{
  "name": "Shopee",
  "slug": "shopee",
  "url": "https://shopee.com.br",
  "logo": "https://example.com/shopee-logo.png",
  "api_key": "sk_test_123",
  "api_secret": "secret_123",
  "commission_rate": 5.5,
  "affiliate_id": "AFF123",
  "description": "Programa de afiliados Shopee",
  "terms_url": "https://shopee.com.br/terms",
  "priority": 10
}
```

**Response 201:**
```json
{
  "status": "success",
  "message": "Afiliado criado com sucesso",
  "id": "673f4a1b5e8c9d4a2b1c3d8e",
  "data": { /* dados do afiliado */ }
}
```

#### 4.2 Listar Afiliados
**GET** `/affiliates/?is_active=true&limit=50`

Lista afiliados ordenados por prioridade.

**Response 200:**
```json
{
  "total": 5,
  "limit": 50,
  "skip": 0,
  "data": [
    {
      "_id": "673f4a1b5e8c9d4a2b1c3d8e",
      "name": "Shopee",
      "slug": "shopee",
      "url": "https://shopee.com.br",
      "logo": "https://example.com/shopee-logo.png",
      "commission_rate": 5.5,
      "is_active": true,
      "priority": 10,
      "created_at": "2025-10-31T10:00:00"
    }
  ]
}
```

#### 4.3 Buscar Afiliado por Slug
**GET** `/affiliates/slug/{slug}`

Busca afiliado por identificador único.

**Exemplo:** `GET /affiliates/slug/shopee`

---

### 5. CANAIS (`/channels`)

Gerencia canais de publicação (Telegram, WhatsApp, Instagram, Site, Email, Discord).

#### 5.1 Criar Canal
**POST** `/channels/`

Cria um novo canal de publicação.

**Request Body:**
```json
{
  "name": "Canal Telegram Oficial",
  "slug": "telegram-oficial",
  "type": "telegram",
  "description": "Canal principal do Telegram",
  "api_token": "123456:ABC-DEF",
  "channel_id": "-1001234567890",
  "config": {
    "parse_mode": "HTML",
    "disable_notification": false
  },
  "priority": 10
}
```

**Response 201:**
```json
{
  "status": "success",
  "message": "Canal criado com sucesso",
  "id": "673f5a1b5e8c9d4a2b1c3d9e",
  "data": { /* dados do canal */ }
}
```

#### 5.2 Listar Canais Ativos
**GET** `/channels/active`

Retorna apenas canais ativos ordenados por prioridade.

**Response 200:**
```json
{
  "total": 4,
  "data": [
    {
      "_id": "673f5a1b5e8c9d4a2b1c3d9e",
      "name": "Canal Telegram Oficial",
      "slug": "telegram-oficial",
      "type": "telegram",
      "is_active": true,
      "priority": 10,
      "total_posts": 150,
      "success_rate": 98.5,
      "last_post_at": "2025-10-31T10:30:00"
    }
  ]
}
```

#### 5.3 Atualizar Estatísticas do Canal
**PATCH** `/channels/{channel_id}/stats`

Atualiza estatísticas de posts do canal.

**Request Body:**
```json
{
  "total_posts": 151,
  "success_rate": 98.6
}
```

---

### 6. CONFIGURAÇÕES DO SITE (`/site-config`)

Gerencia configurações globais do site (singleton - apenas uma configuração).

#### 6.1 Obter Configuração
**GET** `/site-config/`

Retorna a configuração atual do site.

**Response 200:**
```json
{
  "_id": "673f6a1b5e8c9d4a2b1c3dae",
  "site_name": "Ecosystem",
  "site_description": "Plataforma de ofertas",
  "site_url": "https://ecosystem.com",
  "logo": "https://ecosystem.com/logo.png",
  "social_media": {
    "facebook": "https://facebook.com/ecosystem",
    "instagram": "https://instagram.com/ecosystem",
    "twitter": "https://twitter.com/ecosystem"
  },
  "group_links": {
    "telegram": "https://t.me/ecosystem",
    "whatsapp": "https://chat.whatsapp.com/xyz"
  },
  "about_us": "Somos uma plataforma...",
  "contact_email": "contato@ecosystem.com",
  "maintenance_mode": false,
  "created_at": "2025-10-31T10:00:00",
  "updated_at": "2025-10-31T10:00:00"
}
```

#### 6.2 Atualizar Configuração
**PUT** `/site-config/`

Atualiza a configuração do site.

**Request Body (todos campos opcionais):**
```json
{
  "site_name": "Novo Nome",
  "about_us": "Nova descrição sobre nós...",
  "contact_email": "novo@email.com"
}
```

#### 6.3 Atualizar Redes Sociais
**PATCH** `/site-config/social-media`

Atualiza apenas as redes sociais.

**Request Body:**
```json
{
  "facebook": "https://facebook.com/newpage",
  "instagram": "https://instagram.com/newpage",
  "tiktok": "https://tiktok.com/@newpage"
}
```

#### 6.4 Modo de Manutenção
**PATCH** `/site-config/maintenance-mode` **🔒 Admin**

Ativa ou desativa o modo de manutenção.

**Request Body:**
```json
{
  "maintenance_mode": true,
  "maintenance_message": "Site em manutenção. Voltamos em breve!"
}
```

#### 6.5 Política de Privacidade
**GET** `/site-config/privacy-policy`

Retorna a política de privacidade do site (público).

**Response 200:**
```json
{
  "privacy_policy": "# Política de Privacidade\n\n1. Coleta de dados...",
  "updated_at": "2025-11-05T20:30:00"
}
```

**PUT** `/site-config/privacy-policy` **🔒 Admin**

Atualiza a política de privacidade (suporta Markdown/HTML).

**Query Parameter:**
- `privacy_policy` (string) - Texto da política (Markdown ou HTML)

**Response 200:**
```json
{
  "status": "success",
  "message": "Política de privacidade atualizada com sucesso",
  "privacy_policy": "# Política de Privacidade...",
  "updated_at": "2025-11-05T20:30:00"
}
```

#### 6.6 Termos de Serviço
**GET** `/site-config/terms-of-service`

Retorna os termos de serviço do site (público).

**Response 200:**
```json
{
  "terms_of_service": "# Termos de Serviço\n\n1. Aceitação...",
  "updated_at": "2025-11-05T20:30:00"
}
```

**PUT** `/site-config/terms-of-service` **🔒 Admin**

Atualiza os termos de serviço (suporta Markdown/HTML).

**Query Parameter:**
- `terms_of_service` (string) - Texto dos termos (Markdown ou HTML)

**Response 200:**
```json
{
  "status": "success",
  "message": "Termos de serviço atualizados com sucesso",
  "terms_of_service": "# Termos de Serviço...",
  "updated_at": "2025-11-05T20:30:00"
}
```

---

### 7. CUPONS (`/coupons`)

Gerencia cupons de desconto com validação inteligente.

#### 7.1 Criar Cupom
**POST** `/coupons/`

Cria um novo cupom de desconto.

**Request Body:**
```json
{
  "code": "PROMO10",
  "description": "10% de desconto",
  "discount_type": "percentage",
  "discount_value": 10,
  "min_purchase_value": 50.00,
  "max_discount_value": 20.00,
  "start_date": "2025-11-01T00:00:00",
  "expiry_date": "2025-11-30T23:59:59",
  "usage_limit": 100,
  "usage_limit_per_user": 1,
  "affiliate_slug": "shopee",
  "is_public": true
}
```

**Tipos de desconto:**
- `percentage` - Desconto percentual
- `fixed` - Valor fixo de desconto
- `free_shipping` - Frete grátis

**Response 201:**
```json
{
  "status": "success",
  "message": "Cupom criado com sucesso",
  "id": "673f7a1b5e8c9d4a2b1c3dbe",
  "data": { /* dados do cupom */ }
}
```

#### 7.2 Validar Cupom
**POST** `/coupons/validate`

Valida se um cupom pode ser usado.

**Request Body:**
```json
{
  "code": "PROMO10",
  "purchase_value": 100.00,
  "user_id": "user_123"
}
```

**Response 200 (Cupom Válido):**
```json
{
  "valid": true,
  "message": "Cupom válido",
  "coupon": {
    "code": "PROMO10",
    "description": "10% de desconto",
    "discount_type": "percentage",
    "discount_value": 10,
    "discount_amount": 10.00,
    "expiry_date": "2025-11-30T23:59:59",
    "usage_remaining": 85
  }
}
```

**Response 200 (Cupom Inválido):**
```json
{
  "valid": false,
  "message": "Cupom expirado",
  "coupon": null
}
```

#### 7.3 Usar Cupom
**POST** `/coupons/{coupon_id}/use`

Incrementa o contador de uso do cupom (registrar uso).

**Response 200:**
```json
{
  "status": "success",
  "message": "Cupom usado com sucesso",
  "current_usage": 16,
  "remaining": 84
}
```

#### 7.4 Buscar Cupom por Código
**GET** `/coupons/code/{code}`

Busca um cupom por código.

**Exemplo:** `GET /coupons/code/PROMO10`

---

## 🔄 Fluxo Recomendado

### Cenário 1: Adicionar Nova Oferta (Automático)
```
1. POST /offers/extract-and-save
   → Extrai, verifica duplicata e salva automaticamente
   → Cria posts para cada canal (telegram, whatsapp, site, instagram)

2. GET /posts/?enviado=false&status=pending
   → Frontend ou n8n busca posts pendentes

3. n8n envia para os canais

4. PATCH /posts/{post_id}
   → n8n atualiza status após enviar
```

### Cenário 2: Adicionar Nova Oferta (Manual)
```
1. POST /offers/extract
   → Extrai dados da URL

2. Frontend exibe dados extraídos para revisão

3. Usuário ajusta título, descrição, tags, etc

4. POST /offers/
   → Salva oferta com dados otimizados
   → Cria posts automaticamente
```

### Cenário 3: Gerenciar Ofertas
```
1. GET /offers/?status=pending&limit=20
   → Lista ofertas pendentes

2. PUT /offers/{offer_id}
   → Aprova/rejeita ou edita oferta

3. DELETE /offers/{offer_id}
   → Remove oferta se necessário
```

### Cenário 4: Autenticação e Gerenciamento de Usuários
```
1. POST /users/login
   → Usuário faz login com email e senha
   → Recebe dados do usuário (sem password_hash)

2. GET /users/?role=admin
   → Administrador lista usuários por role

3. POST /users/
   → Criar novo usuário (admin/moderator)

4. PUT /users/{user_id}
   → Atualizar dados ou alterar role

5. PATCH /users/{user_id}/toggle-active
   → Ativar/desativar acesso do usuário
```

---

## 📊 Modelos de Dados

### Offer
```typescript
interface Offer {
  _id: string;
  source: string; // "Mercado Livre" | "AliExpress" | "Shopee"
  url: string; // URL completa após redirecionamento
  extract_url?: string; // URL curta original do extract
  title: string;
  price_original?: number;
  price_discounted?: number;
  discount?: string; // Ex: "32% OFF"
  installments?: string; // Ex: "12x R$50.67 sem juros"
  currency: string; // "BRL" | "USD"
  image?: string;
  description?: string;
  category?: string;
  tags: string[];
  optimized_message?: string;
  note?: string; // Avisos sobre limitações
  status: "pending" | "approved" | "rejected";
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}
```

### Post
```typescript
interface Post {
  _id: string;
  offer_id: string;
  channel: "telegram" | "whatsapp" | "site" | "instagram";
  enviado: boolean;
  status: "pending" | "success" | "failed";
  responses?: Record<string, any>;
  error?: string;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}
```

### User
```typescript
interface User {
  _id: string;
  name: string;
  email: string; // Único
  password_hash: string; // Hash bcrypt (nunca retornado)
  role: "user" | "admin" | "moderator";
  is_active: boolean;
  avatar?: string;
  bio?: string;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  last_login?: string; // ISO 8601
}
```

**⚠️ Segurança:**
- Senhas são armazenadas com **bcrypt hash**
- `password_hash` nunca é retornado nas respostas da API
- Validação de email único no banco de dados
- Login atualiza automaticamente `last_login`

### Affiliate
```typescript
interface Affiliate {
  _id: string;
  name: string;
  slug: string; // Único, identificador (ex: shopee, mercadolivre)
  url: string; // URL do site afiliado
  logo?: string;
  api_key?: string;
  api_secret?: string;
  commission_rate?: number; // Taxa de comissão (%)
  affiliate_id?: string; // ID de afiliado no site
  description?: string;
  terms_url?: string;
  is_active: boolean;
  priority: number; // Prioridade de exibição
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}
```

### Channel
```typescript
interface Channel {
  _id: string;
  name: string;
  slug: string; // Único, identificador
  type: "telegram" | "whatsapp" | "instagram" | "site" | "email" | "discord";
  description?: string;
  api_token?: string; // Token de API
  api_key?: string;
  api_secret?: string;
  webhook_url?: string;
  channel_id?: string; // ID do canal/grupo
  phone_number?: string; // Para WhatsApp
  config?: Record<string, any>; // Configurações customizadas
  total_posts: number;
  success_rate: number; // Taxa de sucesso (%)
  is_active: boolean;
  priority: number;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  last_post_at?: string; // ISO 8601
}
```

### SiteConfig
```typescript
interface SiteConfig {
  _id: string;
  site_name: string;
  site_description?: string;
  site_url?: string;
  logo?: string;
  favicon?: string;
  social_media: Record<string, string>; // {facebook: url, instagram: url, ...}
  group_links: Record<string, string>; // {telegram: url, whatsapp: url, ...}
  about_us?: string;
  mission?: string;
  vision?: string;
  values?: string[];
  contact_email?: string;
  contact_phone?: string;
  contact_address?: string;
  meta_keywords?: string[];
  google_analytics_id?: string;
  facebook_pixel_id?: string;
  maintenance_mode: boolean;
  maintenance_message?: string;
  custom_config?: Record<string, any>;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}
```

**⚠️ Singleton:**
- Apenas uma configuração existe no sistema
- Criada automaticamente se não existir

### Coupon
```typescript
interface Coupon {
  _id: string;
  code: string; // Único, maiúsculas
  description?: string;
  discount_type: "percentage" | "fixed" | "free_shipping";
  discount_value: number; // % ou valor fixo
  min_purchase_value?: number; // Valor mínimo de compra
  max_discount_value?: number; // Cap do desconto
  start_date?: string; // ISO 8601
  expiry_date?: string; // ISO 8601
  usage_limit?: number; // Limite total de usos
  usage_limit_per_user?: number;
  current_usage: number; // Contador atual
  applicable_to?: string[]; // Categorias/produtos aplicáveis
  excluded_items?: string[];
  affiliate_slug?: string;
  is_active: boolean;
  is_public: boolean;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  created_by?: string; // ID do usuário
}
```

---

## 🛡️ Sistema Anti-Duplicatas

A API verifica automaticamente duplicatas em **2 níveis**:

1. **Por URL**: Se a URL já existe → DUPLICATA
2. **Por Título + Preço + Data**: Mesmo título + preço no mesmo dia → DUPLICATA

**Permitido:**
- ✅ Mesmo título + preço diferente
- ✅ Mesmo produto em dias diferentes

---

## 🌍 Plataformas Suportadas

| Plataforma | Extração | Campos Completos |
|------------|----------|------------------|
| **Mercado Livre** | ✅ Completa | title, price, original_price, discount, installments, image, description |
| **AliExpress** | ⚠️ Parcial | title, image, description (preço manual) |
| **Shopee** | ⚠️ Limitada | URL, note com aviso de CAPTCHA |

---

## 🚀 Exemplo de Integração Frontend

```javascript
// 1. Extrair e salvar oferta
async function addOffer(url) {
  const response = await fetch('http://localhost:8000/offers/extract-and-save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  
  const result = await response.json();
  
  if (result.status === 'duplicate') {
    alert('Oferta já cadastrada!');
    return result.existing_offer;
  }
  
  return result.offer;
}

// 2. Listar ofertas pendentes
async function getPendingOffers() {
  const response = await fetch('http://localhost:8000/offers/?status=pending&limit=20');
  const data = await response.json();
  return data.data; // Array de ofertas
}

// 3. Atualizar oferta
async function approveOffer(offerId, optimizedMessage) {
  const response = await fetch(`http://localhost:8000/offers/${offerId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      status: 'approved',
      optimized_message: optimizedMessage
    })
  });
  
  return await response.json();
}

// 4. Buscar posts pendentes
async function getPendingPosts() {
  const response = await fetch('http://localhost:8000/posts/?enviado=false&status=pending');
  return await response.json();
}

// 5. Login de usuário
async function login(email, password) {
  const response = await fetch('http://localhost:8000/users/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const result = await response.json();
  
  if (response.status === 200) {
    // Salvar dados do usuário (localStorage, context, etc)
    localStorage.setItem('user', JSON.stringify(result.user));
    return result.user;
  } else {
    throw new Error(result.detail);
  }
}

// 6. Criar novo usuário (admin apenas)
async function createUser(userData) {
  const response = await fetch('http://localhost:8000/users/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: userData.name,
      email: userData.email,
      password: userData.password,
      role: userData.role || 'user',
      avatar: userData.avatar,
      bio: userData.bio
    })
  });
  
  return await response.json();
}

// 7. Listar usuários (com filtros)
async function getUsers(filters = {}) {
  const params = new URLSearchParams();
  if (filters.role) params.append('role', filters.role);
  if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
  if (filters.limit) params.append('limit', filters.limit);
  
  const response = await fetch(`http://localhost:8000/users/?${params}`);
  return await response.json();
}

// 8. Gerar tags para uma oferta específica ✨
async function generateOfferTags(offerId, token) {
  const response = await fetch(`http://localhost:8000/offers/${offerId}/generate-tags`, {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${token}`
    }
  });
  
  const result = await response.json();
  // Retorna: { status: "success", offer_id: "...", tags: ["tag1", "tag2"], method: "ai" }
  return result;
}

// 9. Gerar tags em lote para todas ofertas sem tags ✨
async function batchGenerateTags(adminToken) {
  const response = await fetch('http://localhost:8000/offers/batch/generate-tags', {
    method: 'POST',
    headers: { 
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  const result = await response.json();
  // Retorna: { status: "completed", total_offers: 10, updated: 10, errors: 0 }
  return result;
}
```

---

## 🏷️ Exemplos de Tags Geradas pela IA

```json
// Ar-condicionado Samsung
{
  "tags": ["ar-condicionado", "split", "samsung", "inverter", "12.000 btus"]
}

// PlayStation 5
{
  "tags": ["playstation 5", "slim", "825gb", "digital", "console"]
}

// Tênis Puma
{
  "tags": ["tênis", "masculino", "feminino", "puma", "club 5v5"]
}

// Placa-mãe Asus
{
  "tags": ["placa-mãe", "asus", "b550m-plus", "am4", "tuf gaming"]
}

// Máquina de lavar Brastemp
{
  "tags": ["máquina de lavar", "13kg", "brastemp", "branca", "automática"]
}
```

**Características das Tags:**
- ✅ Máximo de 5 tags por oferta
- ✅ Geradas automaticamente via OpenAI GPT-3.5-turbo
- ✅ Análise inteligente de título, descrição e categoria
- ✅ Fallback para extração por keywords se IA não disponível
- ✅ Tags em lowercase para consistência
- ✅ Aplicadas automaticamente em ofertas novas

---

## 📁 FILES - Gerenciamento de Arquivos

### **POST** `/files/upload`
Upload de arquivo com validação e organização automática.

**Autenticação:** Obrigatória (Bearer token)

**Parâmetros de Query:**
- `expires_in_days` (int, opcional): Dias até expiração (padrão: 30)
- `is_public` (bool, padrão: false): Se arquivo é público
- `related_to` (str, opcional): ID do recurso relacionado (offer_id, post_id)
- `related_type` (str, opcional): Tipo do recurso (offer, post, user)
- `tags` (str, opcional): Tags separadas por vírgula
- `description` (str, opcional): Descrição do arquivo

**Body:** multipart/form-data
- `file`: Arquivo a ser enviado

**Limites:**
- Tamanho máximo: 10MB
- Extensões: jpg, jpeg, png, gif, webp, pdf, doc, docx, xls, xlsx, txt, mp4, mp3

**Resposta:**
```json
{
  "id": "690a0ab1825aeaafc97f13a0",
  "filename": "20251104_141617_186cf665664e.webp",
  "original_name": "produto.webp",
  "file_type": "image",
  "size": 17730,
  "url": "/api/files/690a0ab1825aeaafc97f13a0/download",
  "expires_at": "2025-12-04T14:16:17.443216Z"
}
```

**Exemplo cURL:**
```bash
curl -X POST "http://localhost:8000/files/upload?is_public=false&tags=produto,destaque" \
  -H "Authorization: Bearer {token}" \
  -F "file=@imagem.webp"
```

---

### **GET** `/files/`
Lista arquivos com filtros avançados.

**Autenticação:** Obrigatória

**Parâmetros de Query:**
- `file_type` (str): image, document, video, audio, other
- `uploaded_by` (str): ID do usuário
- `related_to` (str): ID do recurso relacionado
- `is_public` (bool): Filtrar públicos/privados
- `tags` (str): Tags separadas por vírgula
- `limit` (int, padrão: 50): Máximo de resultados
- `skip` (int, padrão: 0): Pular resultados (paginação)

**Regras de Permissão:**
- Usuários comuns veem: próprios arquivos + arquivos públicos
- Admins veem: todos os arquivos

**Resposta:**
```json
{
  "total": 25,
  "limit": 50,
  "skip": 0,
  "data": [
    {
      "_id": "690a0ab1825aeaafc97f13a0",
      "filename": "20251104_141617_186cf665664e.webp",
      "original_name": "produto.webp",
      "file_type": "image",
      "mime_type": "image/webp",
      "size": 17730,
      "checksum": "a1b2c3d4e5f6...",
      "upload_date": "2025-11-04T14:16:17.443216Z",
      "expires_at": "2025-12-04T14:16:17.443216Z",
      "uploaded_by": "6901df707f37ebde29326609",
      "related_to": "690a0f2e825aeaafc97f13a7",
      "related_type": "offer",
      "tags": ["produto", "destaque"],
      "is_public": false,
      "download_count": 5,
      "last_accessed": "2025-11-04T14:30:00.000000Z"
    }
  ]
}
```

---

### **GET** `/files/{id}`
Obtém metadados de um arquivo específico.

**Autenticação:** Obrigatória

**Resposta:** Objeto FileStorage completo

---

### **GET** `/files/{id}/download`
Faz download do arquivo.

**Autenticação:** Obrigatória

**Comportamento:**
- Incrementa contador de downloads
- Atualiza `last_accessed`
- Verifica permissões (próprio arquivo, público ou admin)
- Verifica se arquivo não expirou

**Resposta:** Arquivo binário com headers apropriados

---

### **DELETE** `/files/{id}`
Exclui arquivo (físico + registro no banco).

**Autenticação:** Obrigatória

**Permissões:**
- Donos podem excluir próprios arquivos
- Admins podem excluir qualquer arquivo

**Resposta:**
```json
{
  "status": "success",
  "message": "Arquivo deletado com sucesso",
  "file_id": "690a0ab1825aeaafc97f13a0"
}
```

---

### **POST** `/files/cleanup/expired` 🔒 Admin
Executa limpeza manual de arquivos expirados.

**Autenticação:** Admin

**Resposta:**
```json
{
  "deleted": 15,
  "failed": 0,
  "freed_mb": 45.2
}
```

---

### **POST** `/files/cleanup/orphans` 🔒 Admin
Executa limpeza manual de arquivos órfãos (sem registro no banco).

**Autenticação:** Admin

---

### **GET** `/files/stats/storage` 🔒 Admin
Retorna estatísticas de armazenamento.

**Autenticação:** Admin

**Resposta:**
```json
{
  "total_files": 150,
  "total_size_bytes": 157286400,
  "total_size_mb": 150.0,
  "by_type": {
    "image": {
      "count": 100,
      "size_bytes": 104857600,
      "size_mb": 100.0
    },
    "document": {
      "count": 30,
      "size_bytes": 31457280,
      "size_mb": 30.0
    }
  }
}
```

---

### **GET** `/files/health/check`
Health check do serviço de arquivos.

**Resposta:**
```json
{
  "status": "healthy",
  "upload_dir_exists": true,
  "upload_dir_writable": true,
  "timestamp": "2025-11-04T14:30:00.000000Z"
}
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)
```env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=ecosystem_db

# Gerenciamento de Arquivos
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx,txt,mp4,mp3,webp
FILE_EXPIRY_DAYS=30
FILE_CLEANUP_ENABLED=true
FILE_CLEANUP_HOUR=3
FILE_CLEANUP_ORPHANS_ENABLED=false
```

### Canais Padrão
Ao criar uma oferta, posts são criados automaticamente para:
- telegram
- whatsapp
- site
- instagram

---

## 📝 Notas Importantes

1. **IDs MongoDB**: Use o formato `PydanticObjectId` (24 caracteres hexadecimais)
2. **Datas**: Formato ISO 8601 (ex: `2025-10-28T10:30:00`)
3. **Preços**: Valores numéricos (float), não strings
4. **Status**: Sempre use os valores exatos (pending, approved, rejected, success, failed)
5. **Paginação**: Use `limit` e `skip` para performance
6. **Autenticação**: 
   - Senhas são criptografadas com **bcrypt**
   - O campo `password_hash` nunca é retornado pela API
   - Implemente JWT ou sessões no frontend para manter usuário logado
   - Valide permissões por `role` (user, admin, moderator)
7. **Segurança de Email**: 
   - Emails são validados e únicos
   - Use validação no frontend também
8. **Roles**: 
   - `user`: Acesso básico
   - `moderator`: Pode gerenciar conteúdo
   - `admin`: Acesso total (incluindo gerenciar usuários)

---

## 🔗 Links Úteis

- **Documentação Swagger**: http://localhost:8000/docs
- **Repositório**: [GitHub](seu-repositorio)
- **MongoDB Atlas**: [Console](https://cloud.mongodb.com)

---

## 💡 Dicas para o Frontend

1. **Cache**: Implemente cache para lista de ofertas
2. **Paginação**: Use scroll infinito ou paginação tradicional
3. **Filtros**: Combine múltiplos filtros para melhor UX
4. **Preview**: Mostre preview da oferta antes de salvar
5. **Feedback**: Indique claramente quando uma oferta é duplicada
6. **Status Visual**: Use cores diferentes para cada status (pending=amarelo, approved=verde, rejected=vermelho)
7. **Imagens**: Implemente lazy loading para as imagens dos produtos
8. **Busca**: Adicione busca por título no frontend (filtrar array local)

---

Desenvolvido com ❤️ para o Ecosystem Backend
