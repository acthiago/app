# 🔒 Segurança e Arquivos Ignorados

## Arquivos Protegidos pelo `.gitignore`

### ⚠️ NUNCA Commitar

#### Dados Confidenciais
- ✅ `.env` - Contém senhas, tokens, chaves secretas
- ✅ `*.pem`, `*.key`, `*.crt` - Certificados e chaves SSL
- ✅ `secrets.json`, `credentials.json` - Credenciais
- ✅ `config.local.json` - Configurações locais

#### Uploads e Dados de Usuários
- ✅ `uploads/` - Arquivos enviados pelos usuários
- ✅ `media/` - Mídias temporárias
- ✅ `tmp/`, `temp/` - Arquivos temporários
- ✅ `*.log` - Logs podem conter dados sensíveis

#### Ambientes Python
- ✅ `.venv/`, `venv/`, `env/` - Ambiente virtual Python
- ✅ `__pycache__/`, `*.pyc` - Bytecode Python
- ✅ `.pytest_cache/` - Cache de testes
- ✅ `.mypy_cache/` - Cache do MyPy

#### IDEs e Editores
- ✅ `.vscode/` - Configurações do VS Code (podem conter caminhos locais)
- ✅ `.idea/` - Configurações do PyCharm
- ✅ `*.swp`, `*.swo` - Arquivos temporários do Vim

#### Sistema Operacional
- ✅ `.DS_Store` - macOS
- ✅ `Thumbs.db` - Windows
- ✅ `.directory` - Linux

#### Bancos de Dados Locais
- ✅ `*.db`, `*.sqlite` - Bancos SQLite locais
- ✅ `dump/`, `*.bson` - Dumps de MongoDB

## ✅ Arquivos Commitados (Seguros)

### Documentação
- ✅ `README.md` - Documentação principal
- ✅ `CHANGELOG.md` - Histórico de versões
- ✅ `API_DOCUMENTATION.md` - Documentação da API
- ✅ `API_EXAMPLES.md` - Exemplos de uso
- ✅ `FRONTEND_GUIDE.md` - Guia para frontend
- ✅ `.env.example` - Template de configuração (SEM dados reais)

### Código Fonte
- ✅ `app/` - Todo o código da aplicação
- ✅ `tests/` - Testes automatizados
- ✅ `requirements.txt` - Dependências Python

### Configuração
- ✅ `Dockerfile`, `Dockerfile.dev` - Containers Docker
- ✅ `docker-compose.yml`, `docker-compose.dev.yml` - Orquestração
- ✅ `.dockerignore` - Arquivos ignorados no build Docker
- ✅ `.gitignore` - Arquivos ignorados no git
- ✅ `pytest.ini` - Configuração de testes

### Scripts de Teste (OPCIONAL - considere remover se não forem úteis)
- ⚠️ `test_ali.py`, `test_ml_quick.py`, etc. - Scripts de teste manual
- ⚠️ `fix_extract_url.py` - Script de correção

## 🚨 Verificação Antes do Commit

Execute antes de cada commit:

```bash
# 1. Verificar se .env não está sendo commitado
git status | grep ".env"

# 2. Verificar se uploads/ não está sendo commitado
git status | grep "uploads/"

# 3. Verificar arquivos tracked
git ls-files | grep -E "\.env$|\.log$|\.key$|\.pem$"

# Se algum comando retornar algo, PARE e investigue!
```

## 📋 Checklist de Segurança

Antes de fazer push:

- [ ] Arquivo `.env` não está no git
- [ ] Pasta `uploads/` não está no git
- [ ] Nenhum `.log` foi commitado
- [ ] Nenhuma chave/certificado foi commitado
- [ ] `.env.example` não contém dados reais
- [ ] `__pycache__/` não está no git
- [ ] `.venv/` não está no git

## 🔄 Se Acidentalmente Commitou Dados Sensíveis

```bash
# 1. Remover do último commit (SE AINDA NÃO DEU PUSH)
git rm --cached .env
git commit --amend

# 2. Se já deu push, limpar histórico (CUIDADO!)
# Considere usar: git-filter-repo ou BFG Repo-Cleaner
# Documente no SECURITY.md

# 3. Trocar TODAS as senhas/tokens comprometidos
# 4. Notificar equipe se necessário
```

## 📝 Notas

- O arquivo `.env.example` serve como **template** e **deve** ser commitado
- Desenvolvedores devem copiar `.env.example` para `.env` e preencher com dados reais
- Scripts de teste manuais (`test_*.py`) podem ser removidos do repo se não forem úteis para outros desenvolvedores

---

**Última atualização**: 2025-11-05  
**Versão**: 2.2.1
