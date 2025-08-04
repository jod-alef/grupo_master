# Grupo Master - Sistema de Qualificação de Soldadores

Sistema web para gerenciamento de qualificação de soldadores, desenvolvido em Django.

## 🚀 Deploy na Nuvem (Coolify)

### Pré-requisitos

- Coolify instalado e configurado
- Banco PostgreSQL configurado
- Domínio configurado (opcional)

### Configuração no Coolify

1. **Criar novo projeto no Coolify**
2. **Configurar repositório Git**
3. **Configurar variáveis de ambiente**:

```bash
# Django Settings
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Database Configuration
DB_NAME=grupo_master
DB_USER=postgres
DB_PASSWORD=sua-senha-postgres
DB_HOST=seu-host-postgres
DB_PORT=5432

# Email Configuration (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-email
DEFAULT_FROM_EMAIL=noreply@grupo-master.com
```

4. **Configurar build**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT grupoMaster.wsgi:application`
   - **Port**: `8000`

5. **Configurar volumes** (se necessário):
   - `/app/media` → para uploads de arquivos
   - `/app/logs` → para logs da aplicação

### Deploy Local com Docker

```bash
# 1. Copiar arquivo de exemplo
cp env.example .env

# 2. Configurar variáveis no .env
nano .env

# 3. Executar com Docker Compose
docker-compose up -d

# 4. Executar migrações
docker-compose exec web python manage.py migrate --settings=grupoMaster.settings_production

# 5. Criar superusuário
docker-compose exec web python manage.py createsuperuser --settings=grupoMaster.settings_production

# 6. Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput --settings=grupoMaster.settings_production
```

### Deploy Local sem Docker

```bash
# 1. Ativar ambiente virtual
source bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar .env
cp env.example .env
nano .env

# 4. Executar script de deploy
./deploy.sh
```

## 🛠️ Desenvolvimento

### Instalação

```bash
# 1. Clonar repositório
git clone <url-do-repositorio>
cd grupo_master

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar banco SQLite (desenvolvimento)
python manage.py migrate

# 5. Criar superusuário
python manage.py createsuperuser

# 6. Executar servidor
python manage.py runserver
```

### Estrutura do Projeto

```
grupo_master/
├── grupoMaster/          # Configurações do projeto
│   ├── settings.py       # Configurações de desenvolvimento
│   ├── settings_production.py  # Configurações de produção
│   └── wsgi.py          # Configuração WSGI
├── raqs/                # Aplicação principal
│   ├── models.py        # Modelos de dados
│   ├── views.py         # Views da aplicação
│   ├── forms.py         # Formulários
│   └── templates/       # Templates HTML
├── static/              # Arquivos estáticos
├── media/               # Uploads de arquivos
├── requirements.txt     # Dependências Python
├── Dockerfile          # Configuração Docker
├── docker-compose.yml  # Orquestração Docker
└── deploy.sh           # Script de deploy
```

## 🔧 Configurações

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SECRET_KEY` | Chave secreta do Django | - |
| `DEBUG` | Modo debug | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `DB_NAME` | Nome do banco | `grupo_master` |
| `DB_USER` | Usuário do banco | `postgres` |
| `DB_PASSWORD` | Senha do banco | - |
| `DB_HOST` | Host do banco | `localhost` |
| `DB_PORT` | Porta do banco | `5432` |

### Banco de Dados

O sistema suporta:
- **SQLite** (desenvolvimento)
- **PostgreSQL** (produção recomendado)

### Segurança

- HTTPS habilitado em produção
- Headers de segurança configurados
- Validação de senhas forte
- Sessões seguras

## 📝 Logs

Os logs são salvos em:
- `logs/django.log` - Logs da aplicação
- Console - Logs em tempo real

## 🔄 Migrações

```bash
# Criar migração
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Verificar status
python manage.py showmigrations
```

## 📊 Backup

### Backup do Banco

```bash
# PostgreSQL
pg_dump -h localhost -U postgres grupo_master > backup.sql

# Restaurar
psql -h localhost -U postgres grupo_master < backup.sql
```

### Backup de Arquivos

```bash
# Backup da pasta media
tar -czf media_backup.tar.gz media/

# Backup completo
tar -czf backup_completo.tar.gz . --exclude='.git' --exclude='venv'
```

## 🆘 Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco**
   - Verificar credenciais no `.env`
   - Verificar se o PostgreSQL está rodando

2. **Erro de permissão**
   - Verificar permissões da pasta `media/`
   - Verificar permissões da pasta `logs/`

3. **Arquivos estáticos não carregam**
   - Executar `python manage.py collectstatic`
   - Verificar configuração do `STATIC_ROOT`

4. **Erro de migração**
   - Verificar se todas as migrações foram aplicadas
   - Executar `python manage.py migrate --fake-initial`

## 📞 Suporte

Para suporte técnico, entre em contato com a equipe de desenvolvimento.

---

**Versão**: 1.0.0  
**Última atualização**: $(date +%Y-%m-%d) 