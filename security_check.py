#!/usr/bin/env python3
"""
Script de verificação de segurança para o projeto Grupo Master
"""

import os
import sys
from pathlib import Path

def check_security_settings():
    """Verifica configurações de segurança"""
    print("🔒 Verificando configurações de segurança...")
    
    issues = []
    
    # Verificar SECRET_KEY
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        issues.append("❌ SECRET_KEY não está definida nas variáveis de ambiente")
    elif secret_key == 'django-insecure-*j@6*q-0*8@2a*!!jf!v&!7f4zr!w-o=&j-@q72_^n)l@puw@2':
        issues.append("❌ SECRET_KEY está usando o valor padrão inseguro")
    else:
        print("✅ SECRET_KEY configurada corretamente")
    
    # Verificar DEBUG
    debug = os.environ.get('DEBUG', 'True')
    if debug.lower() == 'true':
        issues.append("❌ DEBUG está habilitado (deve ser False em produção)")
    else:
        print("✅ DEBUG desabilitado")
    
    # Verificar ALLOWED_HOSTS
    allowed_hosts = os.environ.get('ALLOWED_HOSTS')
    if not allowed_hosts:
        issues.append("❌ ALLOWED_HOSTS não está configurado")
    else:
        print("✅ ALLOWED_HOSTS configurado")
    
    # Verificar banco de dados
    db_engine = os.environ.get('DB_ENGINE', 'sqlite')
    if db_engine == 'sqlite':
        issues.append("⚠️ Usando SQLite (recomendado PostgreSQL para produção)")
    else:
        print("✅ Configuração de banco de dados adequada")
    
    return issues

def check_file_permissions():
    """Verifica permissões de arquivos"""
    print("\n📁 Verificando permissões de arquivos...")
    
    issues = []
    
    # Verificar se .env existe
    if not Path('.env').exists():
        issues.append("❌ Arquivo .env não encontrado")
    else:
        print("✅ Arquivo .env encontrado")
    
    # Verificar pasta media
    media_path = Path('media')
    if not media_path.exists():
        print("⚠️ Pasta media não existe (será criada automaticamente)")
    else:
        print("✅ Pasta media existe")
    
    # Verificar pasta logs
    logs_path = Path('logs')
    if not logs_path.exists():
        print("⚠️ Pasta logs não existe (será criada automaticamente)")
    else:
        print("✅ Pasta logs existe")
    
    return issues

def check_dependencies():
    """Verifica dependências de segurança"""
    print("\n📦 Verificando dependências...")
    
    issues = []
    
    # Verificar se requirements.txt existe
    if not Path('requirements.txt').exists():
        issues.append("❌ requirements.txt não encontrado")
    else:
        print("✅ requirements.txt encontrado")
    
    # Verificar se psycopg2 está incluído
    with open('requirements.txt', 'r') as f:
        content = f.read()
        if 'psycopg2' not in content:
            issues.append("⚠️ psycopg2 não encontrado em requirements.txt")
        else:
            print("✅ psycopg2 incluído")
    
    return issues

def main():
    """Função principal"""
    print("🚀 Verificação de Segurança - Grupo Master")
    print("=" * 50)
    
    all_issues = []
    
    # Executar verificações
    all_issues.extend(check_security_settings())
    all_issues.extend(check_file_permissions())
    all_issues.extend(check_dependencies())
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📋 RELATÓRIO FINAL")
    print("=" * 50)
    
    if all_issues:
        print(f"❌ Encontrados {len(all_issues)} problema(s):")
        for issue in all_issues:
            print(f"   {issue}")
        print("\n🔧 Ações recomendadas:")
        print("   1. Configure as variáveis de ambiente no arquivo .env")
        print("   2. Gere uma nova SECRET_KEY segura")
        print("   3. Configure DEBUG=False para produção")
        print("   4. Configure ALLOWED_HOSTS com seu domínio")
        print("   5. Configure PostgreSQL para produção")
        return False
    else:
        print("✅ Todas as verificações passaram!")
        print("🎉 Seu projeto está pronto para deploy!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 