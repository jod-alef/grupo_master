#!/bin/bash

# Script de deploy para Grupo Master
set -e

echo "🚀 Iniciando deploy do Grupo Master..."

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "📝 Copie o arquivo env.example para .env e configure as variáveis:"
    echo "   cp env.example .env"
    echo "   nano .env"
    exit 1
fi

# Carregar variáveis de ambiente
source .env

echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo "🗄️ Executando migrações..."
python manage.py migrate --settings=grupoMaster.settings_production

echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=grupoMaster.settings_production

echo "👤 Criando superusuário (se necessário)..."
python manage.py shell --settings=grupoMaster.settings_production << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@grupo-master.com', 'admin123')
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
EOF

echo "✅ Deploy concluído com sucesso!"
echo "🌐 Acesse: http://localhost:8000"
echo "👤 Login: admin / admin123" 