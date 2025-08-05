# 🚀 Deploy Grupo Master no Coolify

## Configuração do Projeto

### 1. Configurações Básicas
- **Nome do Projeto**: Grupo Master
- **Tipo**: Aplicação Web
- **Framework**: Django
- **Runtime**: Python 3.12

### 2. Configuração do Repositório
- **Branch**: main
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT grupoMaster.wsgi:application`
- **Port**: 8005

### 3. Variáveis de Ambiente (Environment Variables)

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=grupoMaster.settings_production
SECRET_KEY=(niyq6ke+m8akaexh1m#+-q=7xc1uacq&@!a_^e6cl%h$sl3mu
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Database Configuration (PostgreSQL)
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

### 4. Volumes (se necessário)
- `/app/media` → para uploads de arquivos
- `/app/logs` → para logs da aplicação

### 5. Health Check
- **Path**: `/`
- **Port**: 8005
- **Interval**: 30s
- **Timeout**: 10s

## Passos para Deploy

### 1. Criar Projeto no Coolify
1. Acesse o painel do Coolify
2. Clique em "New Project"
3. Selecione "Application"
4. Escolha "Git Repository"

### 2. Configurar Repositório
1. Conecte seu repositório Git
2. Selecione a branch `main`
3. Configure o build path se necessário

### 3. Configurar Build
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT grupoMaster.wsgi:application`
- **Port**: 8005

### 4. Configurar Variáveis de Ambiente
Copie as variáveis acima e configure no painel do Coolify.

### 5. Configurar Banco de Dados
1. Crie um banco PostgreSQL no Coolify
2. Configure as variáveis DB_* com os dados do banco
3. Ou use um banco externo PostgreSQL

### 6. Deploy
1. Clique em "Deploy"
2. Aguarde o build e deploy
3. Verifique os logs se houver problemas

## Pós-Deploy

### 1. Executar Migrações
```bash
# Via terminal do Coolify ou SSH
python manage.py migrate --settings=grupoMaster.settings_production
```

### 2. Criar Superusuário
```bash
python manage.py createsuperuser --settings=grupoMaster.settings_production
```

### 3. Coletar Arquivos Estáticos
```bash
python manage.py collectstatic --noinput --settings=grupoMaster.settings_production
```

## Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco**
   - Verificar credenciais do PostgreSQL
   - Verificar se o banco está acessível

2. **Erro de permissão**
   - Verificar permissões das pastas media/ e logs/
   - Configurar volumes corretamente

3. **Erro de build**
   - Verificar se requirements.txt está correto
   - Verificar se todas as dependências estão listadas

4. **Erro de template**
   - Verificar se os templates estão corretos
   - Verificar se os filtros customizados estão funcionando

## Status do Projeto

✅ **Pronto para Deploy**
- [x] Configurações de produção
- [x] Dependências atualizadas
- [x] Dockerfile configurado
- [x] Filtros de template corrigidos
- [x] Segurança configurada
- [x] PostgreSQL configurado
- [x] Logs configurados
- [x] Arquivos estáticos configurados

🎯 **Próximo passo**: Fazer deploy no Coolify! 