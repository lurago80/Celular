#!/usr/bin/env python
"""
Script para criar usuário administrador automaticamente
Execute: python criar_admin.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loja.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Verificar se já existe
if User.objects.filter(username='admin').exists():
    print('⚠️  Usuário "admin" já existe!')
    resposta = input('Deseja remover e recriar? (s/N): ').strip().lower()
    if resposta in ['s', 'sim', 'y', 'yes']:
        User.objects.filter(username='admin').delete()
        print('✓ Usuário antigo removido')
    else:
        print('Operação cancelada.')
        sys.exit(0)

# Criar superusuário
try:
    User.objects.create_superuser(
        username='admin',
        email='admin@loja.com',
        password='admin123'
    )
    print('=' * 60)
    print('✓ USUÁRIO ADMINISTRADOR CRIADO COM SUCESSO!')
    print('=' * 60)
    print()
    print('CREDENCIAIS DE ACESSO:')
    print('  Username: admin')
    print('  Email:    admin@loja.com')
    print('  Password: admin123')
    print()
    print('⚠️  IMPORTANTE: Altere a senha após o primeiro acesso!')
    print()
except Exception as e:
    print(f'❌ ERRO ao criar usuário: {e}')
    sys.exit(1)

