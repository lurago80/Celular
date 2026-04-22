@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Instalacao - Sistema Loja de Celulares

echo ============================================================
echo    INSTALACAO - SISTEMA LOJA DE CELULARES
echo ============================================================
echo.

:: Encontrar pasta do projeto automaticamente
set "PROJETO_ENCONTRADO=0"
for %%P in (
    "%~dp0"
    "C:\INOVE\CELULAR"
    "C:\Inove\Celular"
    "C:\PROJETOS\CELULAR"
    "C:\Projetos\Celular"
) do (
    if exist "%%~P\manage.py" (
        cd /d %%~P
        set "PROJETO_ENCONTRADO=1"
        goto :projeto_encontrado
    )
)

:projeto_encontrado
if "%PROJETO_ENCONTRADO%"=="0" (
    echo ERRO: Projeto nao encontrado!
    echo Procurei em:
    echo - Pasta do script: %~dp0
    echo - C:\INOVE\CELULAR (Cliente)
    echo - C:\PROJETOS\CELULAR (Desenvolvimento)
    echo.
    pause
    exit /b 1
)

echo Pasta do projeto: %CD%
echo.

:: PASSO 1: Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.8 ou superior de: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo    Python encontrado: !PYTHON_VERSION!
echo.

:: PASSO 2: Criar ambiente virtual
echo [2/6] Criando ambiente virtual (.venv)...
if exist ".venv\Scripts\python.exe" (
    echo    Ambiente virtual ja existe. Pulando...
) else (
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
    echo    Ambiente virtual criado com sucesso!
)
echo.

:: PASSO 3: Ativar ambiente virtual e atualizar pip
echo [3/6] Atualizando pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --no-warn-script-location >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo AVISO: Nao foi possivel atualizar pip. Continuando...
)
echo    Pip atualizado!
echo.

:: PASSO 4: Instalar dependencias
echo [4/6] Instalando dependencias...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt --no-warn-script-location
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Falha ao instalar dependencias!
        pause
        exit /b 1
    )
    echo    Dependencias instaladas com sucesso!
) else (
    echo AVISO: Arquivo requirements.txt nao encontrado!
    echo    Instalando Django diretamente...
    python -m pip install "django>=4.2,<6.0" --no-warn-script-location
)
echo.

:: PASSO 5: Aplicar migracoes
echo [5/6] Aplicando migracoes do banco de dados...
python manage.py migrate --noinput
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao aplicar migracoes!
    pause
    exit /b 1
)
echo    Migracoes aplicadas com sucesso!
echo.

:: PASSO 6: Criar superusuario
echo [6/6] Criando usuario administrador...
echo.
set /p CRIAR_ADMIN="Deseja criar usuario administrador automaticamente? (S/N): "
if /i "!CRIAR_ADMIN!"=="S" (
    python criar_admin.py
    if %ERRORLEVEL% NEQ 0 (
        echo AVISO: Nao foi possivel criar usuario automaticamente.
        echo    Você pode criar manualmente com: python manage.py createsuperuser
    )
) else (
    echo    Pulando criacao de usuario.
    echo    Para criar manualmente, execute: python manage.py createsuperuser
)
echo.

:: Finalizacao
echo ============================================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo ============================================================
echo.
echo Para iniciar o servidor:
echo    1. Execute: INICIAR_SERVIDOR_OCULTO.vbs (oculto - recomendado)
echo    2. Ou manualmente: python manage.py runserver
echo.
echo O sistema estara disponivel em: http://localhost:8000
echo.
pause

