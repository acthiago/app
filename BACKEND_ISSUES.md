# 🐛 Issues Identificadas no Backend - XDesconto API

**Projeto Backend**: `/home/thiago/bff-ecossistema/app`  
**Data**: 08/11/2025  
**Versão Frontend**: 1.1.3

---

## Issues Prioritárias para Próxima Versão

### 1. 📊 Contador de Posts nos Canais

**Problema**: Posts com status "success" não estão sendo contabilizados no campo `total_posts` dos canais.

**Impacto**: 
- Estatísticas incorretas na tela administrativa de Canais
- Taxa de sucesso (`success_rate`) não é calculada corretamente
- Impossível rastrear performance real dos canais

**Localização sugerida**: 
- Endpoint: `POST /posts/` (criação de posts)
- Endpoint: `PUT /posts/{id}` (atualização de status)
- Collection: `channels`

**Solução proposta**:
```python
# Ao criar post com sucesso ou atualizar status para "success"
async def increment_channel_posts(channel_id: str, status: str):
    if status == "success":
        # Incrementar total_posts
        await db.channels.update_one(
            {"_id": ObjectId(channel_id)},
            {"$inc": {"total_posts": 1}}
        )
        
        # Recalcular success_rate
        channel = await db.channels.find_one({"_id": ObjectId(channel_id)})
        total = channel.get("total_posts", 0)
        
        # Contar posts com sucesso
        success_count = await db.posts.count_documents({
            "channel": channel["name"],
            "status": "success"
        })
        
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        await db.channels.update_one(
            {"_id": ObjectId(channel_id)},
            {"$set": {"success_rate": success_rate}}
        )
```

---

### 2. ✅ Auto-aprovação de Ofertas Postadas no Site

**Problema**: Ofertas postadas no canal "Site" ficam com status "pending" em vez de "approved".

**Impacto**:
- Ofertas não aparecem na página principal automaticamente
- Requer aprovação manual mesmo já estando publicadas
- Experiência do usuário inconsistente

**Localização sugerida**:
- Endpoint: `POST /posts/` (criação de posts)
- Collection: `offers`
- Collection: `channels`

**Solução proposta - Opção 1** (Mais simples):
```python
# Na criação do post
async def create_post(post_data: dict):
    # ... código existente ...
    
    # Verificar se o canal é do tipo "site"
    channel = await db.channels.find_one({"name": post_data["channel"]})
    
    if channel and channel.get("type") == "site":
        # Auto-aprovar a oferta
        await db.offers.update_one(
            {"_id": ObjectId(post_data["offer_id"])},
            {"$set": {"status": "approved"}}
        )
```

**Solução proposta - Opção 2** (Mais flexível):
```python
# Adicionar campo "auto_approve" no modelo Channel
class Channel(BaseModel):
    name: str
    type: str
    auto_approve: bool = False  # Novo campo
    # ... outros campos ...

# Na criação do post
async def create_post(post_data: dict):
    # ... código existente ...
    
    channel = await db.channels.find_one({"name": post_data["channel"]})
    
    if channel and channel.get("auto_approve", False):
        await db.offers.update_one(
            {"_id": ObjectId(post_data["offer_id"])},
            {"$set": {"status": "approved"}}
        )
```

---

### 3. 🏷️ Título do Produto nos Posts

**Problema**: API `GET /posts/` não retorna o título da oferta relacionada, apenas o `offer_id`.

**Impacto**:
- Dificulta identificação visual dos posts na tela administrativa
- Administradores precisam abrir cada oferta para ver o que foi postado
- Má experiência de usuário

**Localização sugerida**:
- Endpoint: `GET /posts/`
- Collections: `posts` + `offers` (join)

**Solução proposta** (MongoDB Aggregation):
```python
async def get_posts():
    """Retorna posts com título da oferta incluído"""
    
    posts = await db.posts.aggregate([
        # Fazer lookup com a collection de ofertas
        {
            "$lookup": {
                "from": "offers",
                "localField": "offer_id",
                "foreignField": "_id",
                "as": "offer_data"
            }
        },
        # Extrair apenas o título da oferta
        {
            "$addFields": {
                "offer_title": {
                    "$arrayElemAt": ["$offer_data.title", 0]
                }
            }
        },
        # Remover o array completo de offer_data (otimização)
        {
            "$project": {
                "offer_data": 0
            }
        },
        # Ordenar por data de criação (mais recente primeiro)
        {
            "$sort": {"created_at": -1}
        }
    ]).to_list(length=None)
    
    return posts
```

**Response esperada**:
```json
[
  {
    "_id": "673a5e8f...",
    "offer_id": "6c3a5e8f...",
    "offer_title": "Refil Para Bolha de Sabão Líquido Concentrado",
    "channel": "Telegram",
    "status": "success",
    "enviado": true,
    "created_at": "2025-11-03T12:00:00",
    "updated_at": "2025-11-03T12:00:05"
  }
]
```

---

## 📝 Checklist de Implementação

### Issue #1 - Contador de Posts
- [ ] Criar função `increment_channel_posts(channel_id, status)`
- [ ] Chamar função ao criar post com sucesso
- [ ] Chamar função ao atualizar status para "success"
- [ ] Adicionar recálculo de `success_rate`
- [ ] Testar com posts existentes e novos
- [ ] Verificar estatísticas no frontend

### Issue #2 - Auto-aprovação
- [ ] Decidir entre Opção 1 (tipo "site") ou Opção 2 (flag "auto_approve")
- [ ] Implementar lógica no endpoint POST /posts/
- [ ] Atualizar modelo Channel se necessário
- [ ] Testar criação de post no canal Site
- [ ] Verificar que oferta aparece na página principal
- [ ] Documentar comportamento

### Issue #3 - Título nos Posts
- [ ] Substituir query simples por aggregation pipeline
- [ ] Adicionar lookup com collection offers
- [ ] Adicionar campo `offer_title` na response
- [ ] Testar performance com muitos posts
- [ ] Verificar que frontend exibe títulos corretamente
- [ ] Adicionar índice em `offer_id` se necessário

---

## 🔄 Sugestões de Melhoria Futuras

### Indexação
```python
# Melhorar performance das queries
await db.posts.create_index([("channel", 1), ("status", 1)])
await db.posts.create_index([("offer_id", 1)])
await db.channels.create_index([("name", 1), ("type", 1)])
```

### Cache
- Considerar cache Redis para estatísticas de canais
- Cache de posts recentes para reduzir queries no MongoDB

### Webhooks
- Implementar webhooks para notificar frontend em tempo real quando posts são criados/atualizados

---

---

## 📊 Nova Feature: Sistema de Métricas e Analytics

**Data**: 08/11/2025  
**Prioridade**: Média  
**Versão Frontend preparada**: 1.1.4

### Objetivo
Implementar sistema de rastreamento de cliques em ofertas e visualizações de páginas para análise de performance.

### Endpoints Necessários

#### 1. POST /analytics/click
**Função**: Registrar clique em uma oferta

**Request Body**:
```json
{
  "offer_id": "673a5e8f...",
  "source": "home" // ou "ofertas", "dashboard", etc
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Click registrado"
}
```

**Implementação sugerida**:
```python
# Modelo
class OfferClick(BaseModel):
    offer_id: str
    source: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    clicked_at: datetime

# Collection: offer_clicks
# Índices: offer_id, source, clicked_at

@router.post("/analytics/click")
async def track_offer_click(
    data: dict,
    request: Request
):
    click_data = {
        "offer_id": ObjectId(data["offer_id"]),
        "source": data.get("source", "web"),
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "clicked_at": datetime.utcnow()
    }
    
    await db.offer_clicks.insert_one(click_data)
    
    # Incrementar contador na oferta
    await db.offers.update_one(
        {"_id": ObjectId(data["offer_id"])},
        {"$inc": {"total_clicks": 1}}
    )
    
    return {"status": "success", "message": "Click registrado"}
```

#### 2. POST /analytics/pageview
**Função**: Registrar visualização de página

**Request Body**:
```json
{
  "page": "home" // ou "ofertas", "cupons", etc
}
```

**Response**:
```json
{
  "status": "success"
}
```

**Implementação sugerida**:
```python
# Modelo
class PageView(BaseModel):
    page: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    viewed_at: datetime

# Collection: page_views
# Índices: page, viewed_at

@router.post("/analytics/pageview")
async def track_page_view(
    data: dict,
    request: Request
):
    view_data = {
        "page": data["page"],
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "viewed_at": datetime.utcnow()
    }
    
    await db.page_views.insert_one(view_data)
    return {"status": "success"}
```

#### 3. GET /analytics/offer/{offer_id}
**Função**: Obter métricas de uma oferta específica

**Response**:
```json
{
  "offer_id": "673a5e8f...",
  "offer_title": "Produto XYZ",
  "total_clicks": 245,
  "clicks_by_source": {
    "home": 120,
    "ofertas": 100,
    "dashboard": 25
  },
  "clicks_by_day": [
    {"date": "2025-11-01", "clicks": 45},
    {"date": "2025-11-02", "clicks": 52}
  ],
  "last_30_days": 245
}
```

**Implementação sugerida**:
```python
@router.get("/analytics/offer/{offer_id}")
async def get_offer_metrics(offer_id: str):
    offer = await db.offers.find_one({"_id": ObjectId(offer_id)})
    
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta não encontrada")
    
    # Total de cliques
    total_clicks = await db.offer_clicks.count_documents({
        "offer_id": ObjectId(offer_id)
    })
    
    # Cliques por fonte
    clicks_by_source = await db.offer_clicks.aggregate([
        {"$match": {"offer_id": ObjectId(offer_id)}},
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(length=None)
    
    # Cliques por dia (últimos 30 dias)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    clicks_by_day = await db.offer_clicks.aggregate([
        {
            "$match": {
                "offer_id": ObjectId(offer_id),
                "clicked_at": {"$gte": thirty_days_ago}
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$clicked_at"}},
                "clicks": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]).to_list(length=None)
    
    return {
        "offer_id": str(offer["_id"]),
        "offer_title": offer.get("title"),
        "total_clicks": total_clicks,
        "clicks_by_source": {item["_id"]: item["count"] for item in clicks_by_source},
        "clicks_by_day": [{"date": item["_id"], "clicks": item["clicks"]} for item in clicks_by_day],
        "last_30_days": total_clicks
    }
```

#### 4. GET /analytics/summary
**Função**: Obter resumo geral de métricas

**Response**:
```json
{
  "total_offer_clicks": 1234,
  "total_page_views": 5678,
  "most_clicked_offers": [
    {
      "offer_id": "673a5e8f...",
      "title": "Produto XYZ",
      "clicks": 245
    }
  ],
  "most_viewed_pages": {
    "home": 2500,
    "ofertas": 1800,
    "cupons": 1378
  },
  "clicks_last_7_days": 456,
  "views_last_7_days": 1234
}
```

**Implementação sugerida**:
```python
@router.get("/analytics/summary")
async def get_analytics_summary():
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Total de cliques
    total_clicks = await db.offer_clicks.count_documents({})
    
    # Total de visualizações
    total_views = await db.page_views.count_documents({})
    
    # Ofertas mais clicadas
    most_clicked = await db.offer_clicks.aggregate([
        {"$group": {"_id": "$offer_id", "clicks": {"$sum": 1}}},
        {"$sort": {"clicks": -1}},
        {"$limit": 10},
        {
            "$lookup": {
                "from": "offers",
                "localField": "_id",
                "foreignField": "_id",
                "as": "offer"
            }
        },
        {
            "$project": {
                "offer_id": "$_id",
                "title": {"$arrayElemAt": ["$offer.title", 0]},
                "clicks": 1
            }
        }
    ]).to_list(length=None)
    
    # Páginas mais visualizadas
    most_viewed_pages = await db.page_views.aggregate([
        {"$group": {"_id": "$page", "views": {"$sum": 1}}},
        {"$sort": {"views": -1}}
    ]).to_list(length=None)
    
    # Cliques últimos 7 dias
    clicks_last_7_days = await db.offer_clicks.count_documents({
        "clicked_at": {"$gte": seven_days_ago}
    })
    
    # Views últimos 7 dias
    views_last_7_days = await db.page_views.count_documents({
        "viewed_at": {"$gte": seven_days_ago}
    })
    
    return {
        "total_offer_clicks": total_clicks,
        "total_page_views": total_views,
        "most_clicked_offers": most_clicked,
        "most_viewed_pages": {item["_id"]: item["views"] for item in most_viewed_pages},
        "clicks_last_7_days": clicks_last_7_days,
        "views_last_7_days": views_last_7_days
    }
```

### Alterações no Modelo Offers
Adicionar campo para contador de cliques:
```python
class Offer(BaseModel):
    # ... campos existentes ...
    total_clicks: int = 0  # Novo campo
```

### Índices MongoDB Recomendados
```python
# Collection: offer_clicks
await db.offer_clicks.create_index([("offer_id", 1), ("clicked_at", -1)])
await db.offer_clicks.create_index([("source", 1)])
await db.offer_clicks.create_index([("clicked_at", -1)])

# Collection: page_views
await db.page_views.create_index([("page", 1), ("viewed_at", -1)])
await db.page_views.create_index([("viewed_at", -1)])

# Collection: offers
await db.offers.create_index([("total_clicks", -1)])  # Para ordenar por mais clicados
```

### Frontend já preparado
- ✅ Hook `usePageView` - rastreia visualizações automáticas
- ✅ Função `trackOfferClick` - registra cliques em ofertas
- ✅ Implementado em: Home.tsx e PublicOffers.tsx
- ✅ API client atualizado com métodos de analytics

### Próximos passos (Frontend)
Após implementação no backend:
- [ ] Adicionar página de analytics no dashboard
- [ ] Mostrar métricas na listagem de ofertas (admin)
- [ ] Gráficos de performance de ofertas
- [ ] Ranking de ofertas mais clicadas

---

**Preparado por**: Frontend v1.1.4  
**Para ser implementado em**: Backend API - `/home/thiago/bff-ecossistema/app`
