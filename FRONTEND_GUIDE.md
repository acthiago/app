# 🎨 Guia de Integração Frontend - Ecosystem API v2.2.1

> Guia completo para desenvolvedores frontend integrarem com a API do Ecosystem

---

## 📋 Índice

1. [Início Rápido](#-início-rápido)
2. [Autenticação e Segurança](#-autenticação-e-segurança)
3. [Gerenciamento de Estado](#-gerenciamento-de-estado)
4. [Fluxos Principais](#-fluxos-principais)
5. [Exemplos de Código](#-exemplos-de-código)
6. [Tratamento de Erros](#-tratamento-de-erros)
7. [CORS e Configurações](#-cors-e-configurações)
8. [Performance e Cache](#-performance-e-cache)

---

## 🚀 Início Rápido

### Base URL

```javascript
const API_BASE_URL = 'http://localhost:8000';
// Produção: 'https://api.xdesconto.com'
```

### Teste de Conectividade

```javascript
// Verificar se a API está online
fetch(`${API_BASE_URL}/health/`)
  .then(res => res.json())
  .then(data => console.log('API Online:', data.version));
```

---

## 🔒 Autenticação e Segurança

### 1. Fluxo de Login

```javascript
// Login do usuário
async function login(email, password) {
  const response = await fetch(`${API_BASE_URL}/users/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error('Credenciais inválidas');
  }

  const data = await response.json();
  
  // Armazenar token e dados do usuário
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data;
}
```

**Resposta de Sucesso:**
```json
{
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "673a...",
    "name": "João Silva",
    "email": "joao@example.com",
    "role": "user",
    "avatar": null,
    "bio": null
  }
}
```

### 2. Requisições Autenticadas

```javascript
// Helper para fazer requisições autenticadas
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  // Se token expirou (401), redirecionar para login
  if (response.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    throw new Error('Token expirado');
  }
  
  return response;
}
```

### 3. Verificar Permissões

```javascript
// Helper para verificar role do usuário
function hasPermission(requiredRole) {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const roles = ['user', 'moderator', 'admin'];
  
  const userRoleIndex = roles.indexOf(user.role);
  const requiredRoleIndex = roles.indexOf(requiredRole);
  
  return userRoleIndex >= requiredRoleIndex;
}

// Exemplo de uso
if (hasPermission('admin')) {
  // Mostrar botão de configurações
}
```

---

## 🗂️ Gerenciamento de Estado

### Context API (React)

```javascript
// AuthContext.jsx
import { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Carregar dados do localStorage
    const savedToken = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

### Hook Personalizado para API

```javascript
// useApi.js
import { useAuth } from './AuthContext';

export function useApi() {
  const { token } = useAuth();

  const api = async (endpoint, options = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro na requisição');
    }

    return response.json();
  };

  return { api };
}
```

---

## 📱 Fluxos Principais

### 1. Listar Ofertas (Página Inicial)

```javascript
// Exemplo com React + useEffect
import { useState, useEffect } from 'react';

function OffersPage() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 20,
    skip: 0,
  });

  useEffect(() => {
    fetchOffers();
  }, [pagination.skip]);

  async function fetchOffers() {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/offers/?limit=${pagination.limit}&skip=${pagination.skip}`
      );
      const data = await response.json();
      
      setOffers(data.data);
      setPagination(prev => ({ ...prev, total: data.total }));
    } catch (error) {
      console.error('Erro ao buscar ofertas:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <>
          <div className="offers-grid">
            {offers.map(offer => (
              <OfferCard key={offer.id} offer={offer} />
            ))}
          </div>
          <Pagination 
            total={pagination.total} 
            limit={pagination.limit}
            skip={pagination.skip}
            onPageChange={(newSkip) => setPagination(prev => ({ ...prev, skip: newSkip }))}
          />
        </>
      )}
    </div>
  );
}
```

### 2. Extrair Oferta (Com Autenticação)

```javascript
async function extractOffer(url) {
  const { api } = useApi();
  
  try {
    // Mostrar loading
    setLoading(true);
    
    const data = await api('/offers/extract', {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
    
    if (data.status === 'duplicate') {
      // Oferta já existe
      alert('Esta oferta já está cadastrada!');
      return data.existing_offer;
    }
    
    // Sucesso - oferta extraída e criada
    return data.data;
    
  } catch (error) {
    // Rate limit (429) ou erro de autenticação (401)
    if (error.message.includes('Rate limit')) {
      alert('Você atingiu o limite de extrações. Aguarde alguns minutos.');
    }
    throw error;
  } finally {
    setLoading(false);
  }
}
```

### 3. Validar Cupom (Público)

```javascript
async function validateCoupon(code, purchaseValue) {
  try {
    const response = await fetch(`${API_BASE_URL}/coupons/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code: code.toUpperCase(),
        purchase_value: purchaseValue,
      }),
    });
    
    const data = await response.json();
    
    if (data.valid) {
      return {
        valid: true,
        discount: data.discount_amount,
        finalValue: data.final_value,
        message: `Cupom aplicado! Desconto de R$ ${data.discount_amount.toFixed(2)}`,
      };
    } else {
      return {
        valid: false,
        message: data.message,
      };
    }
  } catch (error) {
    return {
      valid: false,
      message: 'Erro ao validar cupom',
    };
  }
}
```

### 4. Upload de Arquivo (Com Autenticação)

```javascript
async function uploadFile(file, fileType = 'image', isPublic = true) {
  const { token } = useAuth();
  
  const formData = new FormData();
  formData.append('file', file);
  formData.append('file_type', fileType);
  formData.append('is_public', isPublic);
  
  try {
    const response = await fetch(`${API_BASE_URL}/files/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // NÃO definir Content-Type - o browser define automaticamente para multipart/form-data
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    const data = await response.json();
    return data; // { id, filename, url, size, mime_type, ... }
    
  } catch (error) {
    console.error('Erro no upload:', error);
    throw error;
  }
}

// Componente de exemplo
function FileUploader() {
  const [uploading, setUploading] = useState(false);
  
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validar tamanho (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('Arquivo muito grande! Máximo: 10MB');
      return;
    }
    
    setUploading(true);
    try {
      const result = await uploadFile(file, 'image', true);
      console.log('Upload concluído:', result.url);
      // Usar result.url na sua aplicação
    } catch (error) {
      alert('Erro no upload: ' + error.message);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <input 
      type="file" 
      onChange={handleFileChange} 
      disabled={uploading}
      accept=".jpg,.jpeg,.png,.gif,.webp"
    />
  );
}
```

### 5. Histórico de Preços (Gráfico)

```javascript
// Buscar dados para gráfico
async function getPriceHistory(offerId, days = 30) {
  const response = await fetch(
    `${API_BASE_URL}/price-history/offer/${offerId}?days=${days}`
  );
  const data = await response.json();
  
  // Formatar para biblioteca de gráficos (ex: Chart.js)
  const chartData = {
    labels: data.data.map(item => new Date(item.recorded_at).toLocaleDateString()),
    datasets: [{
      label: 'Preço',
      data: data.data.map(item => item.price),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  };
  
  return chartData;
}
```

---

## 🎨 Exemplos de Componentes React

### Card de Oferta

```jsx
function OfferCard({ offer }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  return (
    <div className="offer-card">
      {/* Imagem Principal ou Galeria */}
      <div className="offer-images">
        {offer.images && offer.images.length > 0 ? (
          <ImageGallery images={offer.images} />
        ) : (
          <img src={offer.image} alt={offer.title} />
        )}
      </div>
      
      {/* Título */}
      <h3>{offer.title}</h3>
      
      {/* Preços */}
      <div className="prices">
        {offer.price_original && (
          <span className="original-price">
            R$ {offer.price_original.toFixed(2)}
          </span>
        )}
        <span className="discounted-price">
          R$ {offer.price_discounted.toFixed(2)}
        </span>
        {offer.discount && (
          <span className="discount-badge">{offer.discount}</span>
        )}
      </div>
      
      {/* Tags */}
      {offer.tags && offer.tags.length > 0 && (
        <div className="tags">
          {offer.tags.map((tag, i) => (
            <span key={i} className="tag">{tag}</span>
          ))}
        </div>
      )}
      
      {/* Ações */}
      <div className="actions">
        <a href={offer.url} target="_blank" rel="noopener noreferrer">
          Ver Oferta
        </a>
        
        {/* Só moderadores podem editar */}
        {user && (user.role === 'moderator' || user.role === 'admin') && (
          <button onClick={() => navigate(`/offers/${offer.id}/edit`)}>
            Editar
          </button>
        )}
      </div>
    </div>
  );
}
```

### Filtros de Ofertas

```jsx
function OfferFilters({ onFilterChange }) {
  const [filters, setFilters] = useState({
    category: '',
    min_price: '',
    max_price: '',
    affiliate: '',
    tags: '',
  });
  
  const handleChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };
  
  return (
    <div className="filters">
      <select 
        value={filters.category} 
        onChange={(e) => handleChange('category', e.target.value)}
      >
        <option value="">Todas Categorias</option>
        <option value="Eletrônicos">Eletrônicos</option>
        <option value="Moda">Moda</option>
        <option value="Casa">Casa</option>
        {/* ... mais categorias */}
      </select>
      
      <input 
        type="number" 
        placeholder="Preço mín"
        value={filters.min_price}
        onChange={(e) => handleChange('min_price', e.target.value)}
      />
      
      <input 
        type="number" 
        placeholder="Preço máx"
        value={filters.max_price}
        onChange={(e) => handleChange('max_price', e.target.value)}
      />
      
      <select 
        value={filters.affiliate} 
        onChange={(e) => handleChange('affiliate', e.target.value)}
      >
        <option value="">Todas Lojas</option>
        <option value="mercadolivre">Mercado Livre</option>
        <option value="shopee">Shopee</option>
        <option value="aliexpress">AliExpress</option>
      </select>
    </div>
  );
}
```

---

## ⚠️ Tratamento de Erros

### Estrutura de Erros da API

```javascript
// Todos os erros retornam este formato:
{
  "detail": "Mensagem de erro descritiva"
}

// Códigos HTTP comuns:
// 400 - Bad Request (dados inválidos)
// 401 - Unauthorized (não autenticado)
// 403 - Forbidden (sem permissão)
// 404 - Not Found (recurso não encontrado)
// 429 - Too Many Requests (rate limit)
// 500 - Internal Server Error
```

### Handler Global de Erros

```javascript
function handleApiError(error, response) {
  // Rate limit
  if (response?.status === 429) {
    return 'Você está fazendo muitas requisições. Aguarde alguns minutos.';
  }
  
  // Não autenticado
  if (response?.status === 401) {
    // Redirecionar para login
    window.location.href = '/login';
    return 'Sua sessão expirou. Faça login novamente.';
  }
  
  // Sem permissão
  if (response?.status === 403) {
    return 'Você não tem permissão para realizar esta ação.';
  }
  
  // Não encontrado
  if (response?.status === 404) {
    return 'Recurso não encontrado.';
  }
  
  // Erro genérico
  return error.detail || 'Ocorreu um erro. Tente novamente.';
}
```

---

## 🌐 CORS e Configurações

### CORS Configurado

O backend já está configurado para aceitar requisições de:
- `http://localhost:3000` (React dev)
- `http://localhost:3001` (Next.js dev)

**Para adicionar novo domínio em produção:**
Contate o admin para adicionar no `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://seu-dominio.com",  # Adicionar aqui
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ⚡ Performance e Cache

### 1. Cache de Ofertas

A API usa cache Redis para extração de ofertas (1 hora). O frontend pode implementar cache adicional:

```javascript
// Cache em memória simples
const cache = new Map();

async function fetchOffersWithCache(limit, skip) {
  const cacheKey = `offers_${limit}_${skip}`;
  
  // Verificar cache (5 minutos)
  const cached = cache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < 5 * 60 * 1000) {
    return cached.data;
  }
  
  // Buscar da API
  const response = await fetch(`${API_BASE_URL}/offers/?limit=${limit}&skip=${skip}`);
  const data = await response.json();
  
  // Salvar no cache
  cache.set(cacheKey, {
    data,
    timestamp: Date.now(),
  });
  
  return data;
}
```

### 2. Lazy Loading de Imagens

```jsx
function LazyImage({ src, alt }) {
  return (
    <img 
      src={src} 
      alt={alt}
      loading="lazy"
      decoding="async"
    />
  );
}
```

### 3. Infinite Scroll (Paginação Infinita)

```javascript
import { useState, useEffect } from 'react';

function InfiniteOffers() {
  const [offers, setOffers] = useState([]);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const loadMore = async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/offers/?limit=20&skip=${skip}`
      );
      const data = await response.json();
      
      if (data.data.length === 0) {
        setHasMore(false);
      } else {
        setOffers(prev => [...prev, ...data.data]);
        setSkip(prev => prev + 20);
      }
    } finally {
      setLoading(false);
    }
  };

  // Carregar ao chegar no final da página
  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
        loadMore();
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [skip, hasMore, loading]);

  return (
    <div>
      {offers.map(offer => (
        <OfferCard key={offer.id} offer={offer} />
      ))}
      {loading && <p>Carregando mais...</p>}
      {!hasMore && <p>Sem mais ofertas</p>}
    </div>
  );
}
```

---

## 📚 Recursos Adicionais

### TypeScript Types

```typescript
// types/api.ts
export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'moderator' | 'user';
  avatar?: string;
  bio?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface Offer {
  id: string;
  title: string;
  url: string;
  price_original?: number;
  price_discounted: number;
  discount?: string;
  installments?: string;
  currency: string;
  image?: string;
  images: string[];
  description?: string;
  category: string;
  tags: string[];
  affiliate_slug: string;
  status: 'pending' | 'active' | 'expired' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface Coupon {
  id: string;
  code: string;
  description: string;
  discount_type: 'percentage' | 'fixed' | 'free_shipping';
  discount_value: number;
  min_purchase_value?: number;
  max_discount_value?: number;
  start_date: string;
  expiry_date?: string;
  usage_count: number;
  usage_limit?: number;
  is_active: boolean;
  is_public: boolean;
  affiliate_slug?: string;
}

export interface ApiResponse<T> {
  status: string;
  data?: T;
  message?: string;
  total?: number;
  limit?: number;
  skip?: number;
}

export interface LoginResponse {
  status: string;
  access_token: string;
  token_type: string;
  user: User;
}
```

### Axios Configuration (Alternativa ao Fetch)

```javascript
// api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token automaticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para tratar erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Uso:
// import api from './api/axios';
// const { data } = await api.get('/offers/');
```

---

## 🔥 Checklist de Implementação

### Essencial (MVP)

- [ ] Configurar base URL da API
- [ ] Implementar sistema de autenticação (login/logout)
- [ ] Criar hook/service para requisições autenticadas
- [ ] Listar ofertas com paginação
- [ ] Exibir detalhes de oferta
- [ ] Validar cupons
- [ ] Tratamento de erros básico
- [ ] Loading states

### Importante

- [ ] Filtros de ofertas (categoria, preço, loja)
- [ ] Busca de ofertas
- [ ] Galeria de imagens (múltiplas fotos)
- [ ] Histórico de preços (gráfico)
- [ ] Upload de arquivos
- [ ] Cache de requisições
- [ ] Lazy loading de imagens
- [ ] Infinite scroll

### Avançado

- [ ] Dashboard admin/moderador
- [ ] Gerenciamento de usuários (admin)
- [ ] Configurações do site (admin)
- [ ] Estatísticas e relatórios
- [ ] Notificações em tempo real
- [ ] PWA (Progressive Web App)
- [ ] Testes unitários e E2E
- [ ] Otimização de performance (memoization, code splitting)

---

## 📞 Suporte

- **Documentação Completa**: `API_DOCUMENTATION.md`
- **Swagger UI**: http://localhost:8000/docs
- **Segurança**: `SECURITY_FIXES_SUMMARY.md`
- **Changelog**: `CHANGELOG.md`

---

**Última atualização**: 2025-11-05  
**Versão da API**: 2.2.1
