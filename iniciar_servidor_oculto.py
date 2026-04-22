#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para iniciar servidor Django oculto e abrir navegador automaticamente
Executa sem mostrar janelas CMD/PowerShell
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

# Windows - flags para esconder janela
if sys.platform == 'win32':
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0

def encontrar_projeto():
    """Encontra automaticamente a pasta do projeto Django"""
    # Ordem de prioridade:
    # 1. Pasta onde o script está (funciona em ambos os ambientes)
    # 2. Ambiente de cliente (produção)
    # 3. Ambiente de desenvolvimento
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    possiveis_caminhos = [
        script_dir,  # Onde o script está (prioridade 1)
        r"C:\INOVE\CELULAR",  # Cliente (produção)
        r"C:\Inove\Celular",  # Cliente (produção - case diferente)
        r"C:\PROJETOS\CELULAR",  # Desenvolvimento
        r"C:\Projetos\Celular",  # Desenvolvimento (case diferente)
    ]
    
    # Remover duplicatas mantendo ordem
    caminhos_unicos = []
    for caminho in possiveis_caminhos:
        caminho_abs = os.path.abspath(caminho)
        if caminho_abs not in caminhos_unicos:
            caminhos_unicos.append(caminho_abs)
    
    for caminho in caminhos_unicos:
        if os.path.exists(os.path.join(caminho, "manage.py")):
            return caminho
    
    return None

def iniciar_servidor():
    """Inicia o servidor Django e retorna o processo"""
    # Encontrar pasta do projeto
    projeto_path = encontrar_projeto()
    if not projeto_path:
        with open("erro_servidor.log", "w") as f:
            f.write("ERRO: Projeto Django não encontrado!\n")
            f.write("Procurei em:\n")
            f.write(f"- Pasta do script: {os.path.dirname(os.path.abspath(__file__))}\n")
            f.write("- C:\\INOVE\\CELULAR (Cliente/Produção)\n")
            f.write("- C:\\PROJETOS\\CELULAR (Desenvolvimento)\n")
        sys.exit(1)
    
    # Mudar para diretório do projeto
    os.chdir(projeto_path)
    projeto_path_abs = os.path.abspath(projeto_path)
    
    # Tentar usar pythonw.exe primeiro (sem janela), depois python.exe
    venv_python = Path(projeto_path_abs) / ".venv" / "Scripts" / "pythonw.exe"
    if not venv_python.exists():
        venv_python = Path(projeto_path_abs) / ".venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            # Mostrar erro em arquivo de log
            erro_log = os.path.join(projeto_path_abs, "erro_servidor.log")
            with open(erro_log, "w") as f:
                f.write(f"ERRO: Ambiente virtual não encontrado!\n")
                f.write(f"Procure em: {projeto_path_abs}\\.venv\\Scripts\\python.exe")
            sys.exit(1)
    
    # Iniciar servidor Django usando subprocess SEM mostrar janela
    # Configurar STARTUPINFO para Windows
    startupinfo = None
    creationflags = 0
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        # CREATE_NO_WINDOW flag
        try:
            creationflags = subprocess.CREATE_NO_WINDOW
        except AttributeError:
            # Python < 3.7 - usar constante manual
            creationflags = CREATE_NO_WINDOW
    
    # Abrir arquivo de log (modo append para não perder logs anteriores)
    log_path = os.path.join(projeto_path_abs, "django_server.log")
    erro_path = os.path.join(projeto_path_abs, "erro_servidor.log")
    
    # Abrir arquivo de log (manter aberto enquanto processo roda)
    log_file = open(log_path, "a", encoding='utf-8', buffering=1)
    log_file.write("\n" + "="*50 + "\n")
    log_file.write(f"Iniciando servidor Django - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_file.write("="*50 + "\n")
    log_file.flush()
    
    try:
        # Usar Popen para manter processo rodando em background
        process = subprocess.Popen([
            str(venv_python),
            "manage.py",
            "runserver",
            "127.0.0.1:8000",
            "--noreload"
        ], 
        stdout=log_file,
        stderr=subprocess.STDOUT,
        startupinfo=startupinfo,
        creationflags=creationflags,
        shell=False,
        cwd=projeto_path_abs
        )
        
        # Pequeno delay para verificar se processo iniciou
        time.sleep(0.5)
        
        # Verificar se processo ainda está rodando
        if process.poll() is not None:
            # Processo já terminou (erro)
            log_file.write(f"ERRO: Processo terminou com código {process.returncode}\n")
            log_file.flush()
            log_file.close()
            with open(erro_path, "w") as f:
                f.write("ERRO: Servidor Django terminou imediatamente após iniciar.\n")
                f.write("Verifique django_server.log para detalhes.\n")
            return None
        
        # Armazenar referência ao log_file no processo para não fechar
        process._log_file = log_file
        
        return process
            
    except Exception as e:
        log_file.write(f"ERRO ao iniciar servidor: {e}\n")
        import traceback
        log_file.write(traceback.format_exc())
        log_file.flush()
        log_file.close()
        with open(erro_path, "w") as f:
            f.write(f"ERRO ao iniciar servidor: {e}\n")
            f.write(traceback.format_exc())
        return None

def verificar_servidor_pronto(max_tentativas=30, intervalo=1):
    """Verifica se o servidor está pronto para receber conexões"""
    import socket
    for i in range(max_tentativas):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            if result == 0:
                return True  # Servidor está pronto
        except:
            pass
        time.sleep(intervalo)
    return False  # Servidor não iniciou a tempo

def main():
    """Função principal"""
    # Encontrar pasta do projeto automaticamente
    projeto_path = encontrar_projeto()
    if not projeto_path:
        with open("erro_servidor.log", "w") as f:
            f.write("ERRO: Projeto Django não encontrado!\n")
            f.write("Procurei em:\n")
            f.write(f"- Pasta do script: {os.path.dirname(os.path.abspath(__file__))}\n")
            f.write("- C:\\INOVE\\CELULAR (Cliente/Produção)\n")
            f.write("- C:\\PROJETOS\\CELULAR (Desenvolvimento)\n")
        sys.exit(1)
    
    # Mudar para diretório do projeto
    try:
        os.chdir(projeto_path)
    except Exception as e:
        with open("erro_servidor.log", "w") as f:
            f.write(f"ERRO: Não foi possível acessar {projeto_path}: {e}")
        sys.exit(1)
    
    # Verificar se manage.py existe
    if not os.path.exists("manage.py"):
        with open("erro_servidor.log", "w") as f:
            f.write("ERRO: Projeto não encontrado!")
        sys.exit(1)
    
    # Verificar ambiente virtual
    venv_python = Path(".venv\\Scripts\\python.exe")
    if not venv_python.exists():
        venv_python = Path(".venv\\Scripts\\pythonw.exe")
        if not venv_python.exists():
            with open("erro_servidor.log", "w") as f:
                f.write("ERRO: Ambiente virtual não encontrado!")
            sys.exit(1)
    
    # Iniciar servidor diretamente (não em thread)
    server_process = iniciar_servidor()
    
    if server_process is None:
        # Erro ao iniciar servidor
        projeto_path = encontrar_projeto() or "."
        erro_path = os.path.join(projeto_path, "erro_servidor.log")
        mensagem = "Não foi possível iniciar o servidor Django.\n\n"
        if os.path.exists(erro_path):
            with open(erro_path, "r") as f:
                mensagem += f.read()
        mensagem += "\n\nVerifique os logs em C:\\INOVE\\CELULAR\\"
        
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, mensagem, "Erro ao iniciar servidor", 0x10)
        except:
            pass
        sys.exit(1)
    
    # Aguardar servidor iniciar e verificar se está pronto
    time.sleep(2)  # Dar tempo inicial para o processo iniciar
    
    # Verificar se servidor está pronto (aguarda até 30 segundos)
    if verificar_servidor_pronto(max_tentativas=30, intervalo=0.5):
        # Servidor está pronto, abrir navegador
        time.sleep(0.5)  # Pequeno delay adicional
        webbrowser.open("http://localhost:8000")
    else:
        # Servidor não iniciou a tempo, verificar log de erros
        projeto_path = encontrar_projeto()
        if projeto_path:
            log_path = os.path.join(projeto_path, "django_server.log")
            erro_path = os.path.join(projeto_path, "erro_servidor.log")
        else:
            log_path = "django_server.log"
            erro_path = "erro_servidor.log"
        
        mensagem = "Servidor Django não iniciou após 30 segundos.\n\n"
        if os.path.exists(erro_path):
            with open(erro_path, "r") as f:
                mensagem += f"Erro: {f.read()}\n\n"
        if os.path.exists(log_path):
            mensagem += f"Verifique o log: {log_path}"
        
        # Mostrar mensagem de erro (mesmo sendo oculto, é importante)
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, mensagem, "Erro ao iniciar servidor", 0x10)
        except:
            pass
    
    # Aguardar processo terminar (mantém processo vivo)
    if server_process:
        try:
            server_process.wait()
        except KeyboardInterrupt:
            # Tentar finalizar processo
            if server_process:
                server_process.terminate()
                server_process.wait()
            # Fechar arquivo de log
            if hasattr(server_process, '_log_file'):
                try:
                    server_process._log_file.close()
                except:
                    pass

if __name__ == "__main__":
    main()

