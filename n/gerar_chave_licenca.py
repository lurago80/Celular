#!/usr/bin/env python
"""
Gerador de Chaves de Licença - Aplicação Externa
Sistema de Gestão - Loja de Celulares

Este script gera chaves de licença válidas para ativar o sistema por 3 meses.
"""

import hashlib
import secrets
import string
from datetime import datetime
import sys


def gerar_chave_licenca():
    """Gera uma nova chave de licença válida"""
    
    # Gerar 4 blocos de 4 caracteres (letras maiúsculas e números)
    def gerar_bloco():
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(4))
    
    blocos = [gerar_bloco() for _ in range(4)]
    chave_base = '-'.join(blocos)
    
    # Calcular checksum (últimos 4 caracteres são hash dos primeiros)
    hash_value = hashlib.md5(chave_base.encode()).hexdigest()[:4].upper()
    chave_completa = f"{chave_base}-{hash_value}"
    
    return chave_completa


def main():
    """Função principal do gerador"""
    
    print("=" * 70)
    print("GERADOR DE CHAVES DE LICENÇA")
    print("Sistema de Gestão - Loja de Celulares")
    print("=" * 70)
    print()
    
    # Gerar chave
    chave = gerar_chave_licenca()
    data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    print(f"✓ Chave gerada com sucesso!")
    print()
    print("CHAVE DE LICENÇA:")
    print("=" * 70)
    print(chave.center(70))
    print("=" * 70)
    print()
    print(f"Data de geração: {data_geracao}")
    print(f"Validade: 90 dias (3 meses)")
    print()
    print("=" * 70)
    print()
    
    # Salvar em arquivo
    nome_arquivo = f"chave_licenca_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("CHAVE DE LICENÇA - SISTEMA DE GESTÃO\n")
            f.write("Loja de Celulares\n")
            f.write("=" * 50 + "\n")
            f.write(f"\nChave: {chave}\n")
            f.write(f"Data de geração: {data_geracao}\n")
            f.write(f"Validade: 90 dias (3 meses)\n")
            f.write("\n" + "=" * 50 + "\n")
            f.write("\nInstruções:\n")
            f.write("1. Envie esta chave para o cliente\n")
            f.write("2. O cliente deve acessar o sistema\n")
            f.write("3. Quando aparecer a tela de 'Licença Expirada'\n")
            f.write("4. Cole a chave no campo de ativação\n")
            f.write("5. Clique em 'Ativar Licença'\n")
            
        print(f"✓ Chave salva em: {nome_arquivo}")
    except Exception as e:
        print(f"⚠ Erro ao salvar arquivo: {e}")
    
    print()
    
    # Copiar para clipboard (opcional - requer pyperclip)
    try:
        import pyperclip
        pyperclip.copy(chave)
        print("✓ Chave copiada para a área de transferência")
    except ImportError:
        print("💡 Dica: Instale 'pyperclip' para copiar automaticamente:")
        print("   pip install pyperclip")
    except Exception as e:
        pass
    
    print()
    print("Pressione ENTER para gerar outra chave ou Ctrl+C para sair...")
    try:
        input()
        main()  # Gerar outra chave
    except KeyboardInterrupt:
        print("\n\nSaindo...")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcesso interrompido pelo usuário.")
        sys.exit(0)

