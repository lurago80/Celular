@echo off
chcp 65001 >nul 2>nul
setlocal enabledelayedexpansion
title Instalando Sistema Loja de Celulares...

cls
echo.
echo  ============================================================
echo     SISTEMA LOJA DE CELULARES  -  Instalacao Rapida
echo  ============================================================
echo.
echo  Ferramentas necessarias: Python e Node.js ja instalados.
echo.

:: Garantir que estamos na pasta do projeto
cd /d "%~dp0"

if not exist "manage.py" (
    echo  [ERRO] Execute este arquivo dentro da pasta do projeto!
    pause
    exit /b 1
)

:: ============================================================
:: PASSO 1/5  -  Ambiente virtual Python
:: ============================================================
echo  [1/5]  Criando ambiente virtual Python...

if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe --version >nul 2>&1
    if not errorlevel 1 (
        echo         OK  Ambiente virtual ja existente.
        goto :passo2
    )
    echo         !  Ambiente virtual danificado. Recriando...
    rmdir /s /q .venv
)

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERRO] Python nao encontrado!
    echo         Instale Python 3.8+ e marque "Add Python to PATH".
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)

python -m venv .venv
if errorlevel 1 (
    echo  [ERRO] Falha ao criar ambiente virtual!
    pause
    exit /b 1
)
echo         OK  Ambiente virtual criado.

:: ============================================================
:: PASSO 2/5  -  Instalar dependencias Python
:: ============================================================
:passo2
echo.
echo  [2/5]  Instalando dependencias Python...

.venv\Scripts\python.exe -m pip install --upgrade "pip<25" -q --no-warn-script-location
.venv\Scripts\python.exe -m pip install -r requirements.txt -q --no-warn-script-location

if errorlevel 1 (
    echo  [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)
echo         OK  Dependencias instaladas.

:: ============================================================
:: PASSO 3/5  -  Banco de dados (migrations)
:: ============================================================
echo.
echo  [3/5]  Configurando banco de dados...

.venv\Scripts\python.exe manage.py migrate --run-syncdb -v 0

if errorlevel 1 (
    echo  [ERRO] Falha nas migrations!
    pause
    exit /b 1
)
echo         OK  Banco de dados pronto.

:: ============================================================
:: PASSO 4/5  -  Arquivos estaticos
:: ============================================================
echo.
echo  [4/5]  Coletando arquivos estaticos...

if not exist "static" mkdir static
.venv\Scripts\python.exe manage.py collectstatic --noinput -v 0 >nul 2>&1
echo         OK  Arquivos estaticos prontos.

:: ============================================================
:: PASSO 5/5  -  Criar usuario administrador
:: ============================================================
echo.
echo  [5/5]  Criando usuario administrador...

.venv\Scripts\python.exe criar_admin.py

:: ============================================================
:: OPCIONAL  -  Node.js / WhatsApp
:: ============================================================
echo.
where node >nul 2>&1
if errorlevel 1 (
    echo  [AVISO] Node.js nao encontrado. Servico WhatsApp nao sera instalado.
    echo          Instale Node.js 18+ para usar o envio de mensagens.
    goto :concluido
)

echo  [EXTRA] Instalando dependencias do servico WhatsApp...
pushd "%~dp0whatsapp_service"
call npm install --silent
if errorlevel 1 (
    echo         !  Falha ao instalar pacotes Node.js ^(nao critico^).
) else (
    echo         OK  Servico WhatsApp pronto.
)
popd

:: ============================================================
:: CONCLUIDO
:: ============================================================
:concluido
echo.
echo  ============================================================
echo     INSTALACAO CONCLUIDA COM SUCESSO!
echo  ============================================================
echo.
echo   Para iniciar o sistema:
echo     >> Duplo clique em  INICIAR_SISTEMA.bat
echo.
echo   Acesso no navegador:
echo     >> http://localhost:8000
echo.
echo   Login padrao:
echo     >> Usuario:  admin
echo     >> Senha:    admin123
echo.
echo  ============================================================
echo.
pause
endlocal
