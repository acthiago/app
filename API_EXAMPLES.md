# 🧪 Exemplos de Requisições - Ecosystem API v2.2.1

> Coleção de exemplos prontos para usar com cURL, Postman, Insomnia ou fetch()

---

## 📋 Índice

1. [Autenticação](#-autenticação)
2. [Ofertas](#-ofertas)
3. [Usuários](#-usuários)
4. [Cupons](#-cupons)
5. [Arquivos](#-arquivos)
6. [Configurações do Site](#-configurações-do-site)
7. [Histórico de Preços](#-histórico-de-preços)

---

## 🔐 Autenticação

### 1. Login

```bash
# cURL
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "senha123"
  }'

# JavaScript fetch
fetch('http://localhost:8000/users/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@example.com',
    password: 'senha123'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

**Resposta:**
```json
{
  "status": "success",
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "673a...",
    "name": "Admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### 2. Obter Perfil do Usuário Autenticado

```bash
# cURL (substitua SEU_TOKEN)
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer SEU_TOKEN"

# JavaScript fetch
fetch('http://localhost:8000/users/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 🏷️ Ofertas

### 1. Listar Ofertas (Público)

```bash
# cURL - Primeiras 20 ofertas
curl -X GET "http://localhost:8000/offers/?limit=20&skip=0"

# Com filtros
curl -X GET "http://localhost:8000/offers/?category=Eletrônicos&min_price=50&max_price=500&limit=10"

# JavaScript fetch
fetch('http://localhost:8000/offers/?limit=20&skip=0')
  .then(res => res.json())
  .then(data => {
    console.log('Total:', data.total);
    console.log('Ofertas:', data.data);
  });
```

**Resposta:**
```json
{
  "total": 125,
  "limit": 20,
  "skip": 0,
  "data": [
    {
      "id": "673a...",
      "title": "iPhone 15 Pro Max",
      "price_discounted": 6999.99,
      "discount": "15%",
      "image": "https://...",
      "images": ["https://...", "https://..."],
      "category": "Eletrônicos",
      "tags": ["smartphone", "apple", "5g"],
      "affiliate_slug": "mercadolivre"
    }
  ]
}
```

### 2. Buscar Oferta por ID (Público)

```bash
# cURL
curl -X GET http://localhost:8000/offers/673a6e2f5e8c9d4a2b1c3d5f

# JavaScript
fetch('http://localhost:8000/offers/673a6e2f5e8c9d4a2b1c3d5f')
  .then(res => res.json())
  .then(data => console.log(data));
```

### 3. Extrair Oferta de URL 🔒 (Requer Auth)

```bash
# cURL
curl -X POST http://localhost:8000/offers/extract \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.mercadolivre.com.br/produto/MLB123456"
  }'

# JavaScript
fetch('http://localhost:8000/offers/extract', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://www.mercadolivre.com.br/produto/MLB123456'
  })
})
.then(res => res.json())
.then(data => {
  if (data.status === 'duplicate') {
    console.log('Oferta já existe:', data.existing_offer);
  } else {
    console.log('Nova oferta criada:', data.data);
  }
});
```

### 4. Atualizar Oferta 🔒 (Requer Moderador)

```bash
# cURL
curl -X PUT http://localhost:8000/offers/673a6e2f5e8c9d4a2b1c3d5f \
  -H "Authorization: Bearer SEU_TOKEN_MODERADOR" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Novo Título",
    "price_discounted": 5999.99,
    "status": "active"
  }'
```

### 5. Deletar Oferta 🔒 (Requer Admin)

```bash
# cURL
curl -X DELETE http://localhost:8000/offers/673a6e2f5e8c9d4a2b1c3d5f \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN"
```

---

## 👥 Usuários

### 1. Criar Usuário 🔒 (Requer Admin)

```bash
# cURL
curl -X POST http://localhost:8000/users/ \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@example.com",
    "password": "Senha@123",
    "role": "user"
  }'

# JavaScript
fetch('http://localhost:8000/users/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'João Silva',
    email: 'joao@example.com',
    password: 'Senha@123',
    role: 'user'
  })
})
.then(res => res.json())
.then(data => console.log('Usuário criado:', data));
```

**Roles disponíveis:**
- `user` - Usuário comum
- `moderator` - Moderador (pode criar/editar recursos)
- `admin` - Administrador (acesso total)

### 2. Listar Usuários 🔒 (Requer Auth)

```bash
# cURL
curl -X GET "http://localhost:8000/users/?limit=50&skip=0" \
  -H "Authorization: Bearer SEU_TOKEN"

# Com filtros
curl -X GET "http://localhost:8000/users/?role=moderator&is_active=true" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### 3. Atualizar Próprio Perfil 🔒 (Requer Auth)

```bash
# cURL
curl -X PUT http://localhost:8000/users/SEU_USER_ID \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva Atualizado",
    "bio": "Desenvolvedor Full Stack",
    "avatar": "https://..."
  }'
```

---

## 🎫 Cupons

### 1. Listar Cupons Ativos (Público)

```bash
# cURL
curl -X GET "http://localhost:8000/coupons/?is_active=true&is_public=true"

# JavaScript
fetch('http://localhost:8000/coupons/?is_active=true&is_public=true')
  .then(res => res.json())
  .then(data => console.log('Cupons:', data));
```

### 2. Buscar Cupom por Código (Público)

```bash
# cURL
curl -X GET http://localhost:8000/coupons/code/PROMO10

# JavaScript
fetch('http://localhost:8000/coupons/code/PROMO10')
  .then(res => res.json())
  .then(data => console.log('Cupom:', data));
```

### 3. Validar Cupom (Público)

```bash
# cURL
curl -X POST http://localhost:8000/coupons/validate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "PROMO10",
    "purchase_value": 150.00
  }'

# JavaScript
fetch('http://localhost:8000/coupons/validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: 'PROMO10',
    purchase_value: 150.00
  })
})
.then(res => res.json())
.then(data => {
  if (data.valid) {
    console.log('Cupom válido!');
    console.log('Desconto:', data.discount_amount);
    console.log('Valor final:', data.final_value);
  } else {
    console.log('Cupom inválido:', data.message);
  }
});
```

**Resposta (válido):**
```json
{
  "valid": true,
  "coupon": {
    "code": "PROMO10",
    "description": "10% de desconto",
    "discount_type": "percentage"
  },
  "discount_amount": 15.00,
  "final_value": 135.00
}
```

### 4. Criar Cupom 🔒 (Requer Moderador)

```bash
# cURL
curl -X POST http://localhost:8000/coupons/ \
  -H "Authorization: Bearer SEU_TOKEN_MODERADOR" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "PROMO10",
    "description": "10% de desconto",
    "discount_type": "percentage",
    "discount_value": 10,
    "min_purchase_value": 50.00,
    "max_discount_value": 20.00,
    "expiry_date": "2025-12-31T23:59:59",
    "usage_limit": 100,
    "is_public": true,
    "affiliate_slug": "shopee"
  }'
```

---

## 📁 Arquivos

### 1. Upload de Arquivo 🔒 (Requer Auth)

```bash
# cURL
curl -X POST http://localhost:8000/files/upload \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "file=@/caminho/para/imagem.jpg" \
  -F "file_type=image" \
  -F "is_public=true" \
  -F "tags=produto,destaque"

# JavaScript (com FormData)
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('file_type', 'image');
formData.append('is_public', 'true');
formData.append('tags', 'produto,destaque');

fetch('http://localhost:8000/files/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
    // NÃO adicionar Content-Type - o browser define automaticamente
  },
  body: formData
})
.then(res => res.json())
.then(data => console.log('Upload concluído:', data));
```

**Resposta:**
```json
{
  "id": "673f...",
  "filename": "imagem_20251105_143025.jpg",
  "original_filename": "imagem.jpg",
  "url": "/uploads/images/2025/11/05/imagem_20251105_143025.jpg",
  "size": 2458640,
  "mime_type": "image/jpeg",
  "file_type": "image",
  "is_public": true,
  "tags": ["produto", "destaque"]
}
```

### 2. Listar Arquivos 🔒 (Requer Auth)

```bash
# cURL
curl -X GET "http://localhost:8000/files/?file_type=image&limit=20" \
  -H "Authorization: Bearer SEU_TOKEN"

# Com filtros
curl -X GET "http://localhost:8000/files/?is_public=true&tags=produto" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### 3. Download de Arquivo 🔒 (Requer Auth)

```bash
# cURL (salvar arquivo)
curl -X GET http://localhost:8000/files/673f.../download \
  -H "Authorization: Bearer SEU_TOKEN" \
  -o arquivo_baixado.jpg

# JavaScript (abrir em nova aba)
const fileId = '673f...';
const token = localStorage.getItem('access_token');

window.open(
  `http://localhost:8000/files/${fileId}/download?token=${token}`,
  '_blank'
);
```

### 4. Deletar Arquivo 🔒 (Requer Auth - Dono ou Admin)

```bash
# cURL
curl -X DELETE http://localhost:8000/files/673f... \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## ⚙️ Configurações do Site

### 1. Obter Configuração (Público)

```bash
# cURL
curl -X GET http://localhost:8000/site-config/

# JavaScript
fetch('http://localhost:8000/site-config/')
  .then(res => res.json())
  .then(config => {
    console.log('Nome do site:', config.site_name);
    console.log('Redes sociais:', config.social_media);
  });
```

### 2. Política de Privacidade (Público)

```bash
# cURL
curl -X GET http://localhost:8000/site-config/privacy-policy

# JavaScript
fetch('http://localhost:8000/site-config/privacy-policy')
  .then(res => res.json())
  .then(data => {
    console.log('Política:', data.privacy_policy);
    // Renderizar Markdown se necessário
  });
```

### 3. Termos de Serviço (Público)

```bash
# cURL
curl -X GET http://localhost:8000/site-config/terms-of-service

# JavaScript
fetch('http://localhost:8000/site-config/terms-of-service')
  .then(res => res.json())
  .then(data => console.log('Termos:', data.terms_of_service));
```

### 4. Atualizar Política de Privacidade 🔒 (Requer Admin)

```bash
# cURL
curl -X PUT "http://localhost:8000/site-config/privacy-policy?privacy_policy=Texto%20da%20politica" \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN"

# JavaScript
const policy = `
# Política de Privacidade

1. Coleta de Dados
2. Uso de Dados
3. Compartilhamento
`;

fetch('http://localhost:8000/site-config/privacy-policy', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ privacy_policy: policy })
})
.then(res => res.json())
.then(data => console.log('Atualizado:', data));
```

### 5. Atualizar Configuração Geral 🔒 (Requer Admin)

```bash
# cURL
curl -X PUT http://localhost:8000/site-config/ \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "site_name": "XDesconto",
    "site_description": "As melhores ofertas da internet",
    "social_media": {
      "instagram": "https://instagram.com/xdesconto",
      "facebook": "https://facebook.com/xdesconto"
    },
    "contact_email": "contato@xdesconto.com"
  }'
```

### 6. Modo de Manutenção 🔒 (Requer Admin)

```bash
# Ativar
curl -X PATCH "http://localhost:8000/site-config/maintenance-mode?maintenance_mode=true&maintenance_message=Site%20em%20manutencao" \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN"

# Desativar
curl -X PATCH "http://localhost:8000/site-config/maintenance-mode?maintenance_mode=false" \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN"
```

---

## 📊 Histórico de Preços

### 1. Obter Histórico (Público)

```bash
# cURL - Últimos 30 dias
curl -X GET "http://localhost:8000/price-history/offer/673a...?days=30"

# JavaScript
fetch('http://localhost:8000/price-history/offer/673a...?days=30')
  .then(res => res.json())
  .then(data => {
    console.log('Registros:', data.data);
    // Usar para gráfico
  });
```

**Resposta:**
```json
{
  "offer_id": "673a...",
  "count": 15,
  "data": [
    {
      "price": 6999.99,
      "recorded_at": "2025-11-05T10:00:00"
    },
    {
      "price": 6799.99,
      "recorded_at": "2025-11-04T10:00:00"
    }
  ]
}
```

### 2. Variação de Preço (Público)

```bash
# cURL
curl -X GET http://localhost:8000/price-history/offer/673a.../variation

# JavaScript
fetch('http://localhost:8000/price-history/offer/673a.../variation')
  .then(res => res.json())
  .then(data => {
    console.log('Variação:', data.variation_percentage);
    if (data.variation_percentage < 0) {
      console.log('Preço diminuiu! 📉');
    }
  });
```

**Resposta:**
```json
{
  "offer_id": "673a...",
  "current_price": 6799.99,
  "previous_price": 6999.99,
  "variation": -200.00,
  "variation_percentage": -2.86
}
```

### 3. Menor Preço Registrado (Público)

```bash
# cURL
curl -X GET http://localhost:8000/price-history/offer/673a.../lowest

# JavaScript
fetch('http://localhost:8000/price-history/offer/673a.../lowest')
  .then(res => res.json())
  .then(data => {
    console.log('Menor preço já registrado:', data.lowest_price);
    console.log('Data:', data.recorded_at);
  });
```

---

## 🏥 Health Check

### 1. Health Check Básico (Público)

```bash
# cURL
curl -X GET http://localhost:8000/health/

# JavaScript
fetch('http://localhost:8000/health/')
  .then(res => res.json())
  .then(data => console.log('Versão:', data.version));
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T20:30:00",
  "version": "2.2.1"
}
```

### 2. Health Check Detalhado (Público)

```bash
# cURL
curl -X GET http://localhost:8000/health/detailed

# JavaScript
fetch('http://localhost:8000/health/detailed')
  .then(res => res.json())
  .then(data => {
    console.log('MongoDB:', data.services.mongodb.status);
    console.log('Redis:', data.services.redis.status);
    console.log('Features:', data.features);
  });
```

---

## 🎯 Coleção Postman/Insomnia

Para importar todos esses exemplos no Postman ou Insomnia, acesse:
- **Swagger UI**: http://localhost:8000/docs (possui botão "Download OpenAPI spec")
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 📝 Notas Importantes

### Rate Limiting

Endpoint `/offers/extract` tem limite de **10 requisições por minuto** por IP.

### Tamanho de Arquivos

Upload máximo: **10MB** por arquivo.

### Token JWT

- Expira em **30 minutos** (padrão)
- Armazene no `localStorage` ou cookie seguro
- Inclua em toda requisição autenticada: `Authorization: Bearer {token}`

### CORS

Requisições aceitas de:
- `http://localhost:3000`
- `http://localhost:3001`

---

**Última atualização**: 2025-11-05  
**Versão da API**: 2.2.1
