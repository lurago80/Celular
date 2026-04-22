@echo off
chcp 65001 >nul 2>nul
setlocal enabledelayedexpansion
title Instalacao - Sistema Loja de Celulares

echo ============================================================
echo    INSTALACAO - SISTEMA LOJA DE CELULARES
echo ============================================================
echo.

:: Ir para a pasta onde o .bat esta (a propria pasta do projeto)
cd /d "%~dp0"
echo Pasta do projeto: %CD%
echo.

:: Confirmar que e a pasta correta
if not exist "manage.py" goto :pasta_errada
goto :pasta_ok

:pasta_errada
echo ERRO: manage.py nao encontrado em %CD%
echo Certifique-se de executar o instalador de dentro da pasta do projeto.
echo.
pause
exit /b 1

:pasta_ok

:: ============================================================
:: PASSO 1 - Verificar Python
:: ============================================================
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 goto :sem_python
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo    Python encontrado: %PYVER%
echo.
goto :passo2

:sem_python
echo ERRO: Python nao encontrado!
echo.
echo  Instale Python 3.8.x para Windows 7 (ex: 3.8.6 ou 3.8.10):
echo  https://www.python.org/downloads/release/python-3810/
echo.
echo  IMPORTANTE: marque "Add Python to PATH" durante a instalacao.
pause
exit /b 1

:: ============================================================
:: PASSO 2 - Criar ambiente virtual
:: ============================================================
:passo2
echo [2/6] Criando ambiente virtual...
if not exist ".venv\Scripts\python.exe" goto :criar_venv

:: Testar se o venv existente funciona
.venv\Scripts\python.exe --version >nul 2>&1
if errorlevel 1 goto :venv_quebrado
echo    Ambiente virtual existente ok.
goto :passo3

:venv_quebrado
echo    Ambiente virtual quebrado (Python removido). Recriando...
rmdir /s /q .venv

:criar_venv
python -m venv .venv
if errorlevel 1 goto :erro_venv
echo    Ambiente virtual criado.
goto :passo3

:erro_venv
echo ERRO: Falha ao criar ambiente virtual!
pause
exit /b 1

:: ============================================================
:: PASSO 3 - Atualizar pip
:: ============================================================
:passo3
echo.
echo [3/6] Atualizando pip...
.venv\Scripts\python.exe -m pip install --upgrade "pip<25" --quiet --no-warn-script-location
echo    Pip atualizado.
echo.

:: ============================================================
:: PASSO 4 - Instalar dependencias
:: ============================================================
echo [4/6] Instalando dependencias...
.venv\Scripts\python.exe -m pip install "django>=4.2,<4.3" "pillow>=9.5,<10.0" --no-warn-script-location
if errorlevel 1 goto :erro_deps
echo    Dependencias instaladas.
echo.
goto :passo5

:erro_deps
echo ERRO: Falha ao instalar dependencias!
echo.
echo  Verifique sua conexao com a internet.
echo  Python necessario: 3.8.x
pause
exit /b 1

:: ============================================================
:: PASSO 5 - Banco de dados
:: ============================================================
:passo5
echo [5/6] Configurando banco de dados...
.venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 goto :erro_migrate
echo    Banco de dados configurado.
echo.
goto :passo6

:erro_migrate
echo ERRO: Falha ao configurar banco de dados!
pause
exit /b 1

:: ============================================================
:: PASSO 6 - Criar administrador
:: ============================================================
:passo6
echo [6/6] Criando usuario administrador...
echo.
set /p CRIAR_ADMIN=Deseja criar o usuario admin agora? (S/N): 
if /i "%CRIAR_ADMIN%"=="S" goto :criar_admin
if /i "%CRIAR_ADMIN%"=="SIM" goto :criar_admin
goto :pular_admin

:criar_admin
.venv\Scripts\python.exe criar_admin.py
echo.
goto :concluido

:pular_admin
echo    Pulado. Crie depois com: python manage.py createsuperuser
echo.

:: ============================================================
:: CONCLUSAO
:: ============================================================
:concluido
echo ============================================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo ============================================================
echo.
echo  Para iniciar o sistema:
echo    Execute: INICIAR_SERVIDOR_OCULTO.vbs
echo.
echo  Depois acesse: http://localhost:8000
echo.
pause

