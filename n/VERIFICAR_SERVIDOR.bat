@echo off
chcp 65001 >nul
title Verificar Status do Servidor

echo ============================================================
echo    VERIFICAR STATUS DO SERVIDOR DJANGO
echo ============================================================
echo.

:: Detectar automaticamente a pasta do projeto
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

echo Pasta: %CD%
echo.

echo [1] Verificando servidor na porta 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Servidor esta RODANDO na porta 8000
) else (
    echo ✗ Servidor NAO esta rodando na porta 8000
)
echo.

echo [2] Verificando processos Python...
tasklist /FI "IMAGENAME eq python.exe" | findstr python.exe
tasklist /FI "IMAGENAME eq pythonw.exe" | findstr pythonw.exe
echo.

echo [3] Verificando arquivos de log...
echo.
if exist "django_server.log" (
    echo Arquivo django_server.log encontrado:
    echo Ultimas 10 linhas:
    echo ============================================================
    powershell -Command "Get-Content 'django_server.log' -Tail 10"
    echo ============================================================
) else (
    echo ✗ django_server.log NAO encontrado
)
echo.

if exist "erro_servidor.log" (
    echo Arquivo erro_servidor.log encontrado:
    echo Conteudo:
    echo ============================================================
    type erro_servidor.log
    echo ============================================================
) else (
    echo ✓ erro_servidor.log nao existe (sem erros conhecidos)
)
echo.

echo [4] Verificando arquivo iniciar_servidor_oculto.py...
if exist "iniciar_servidor_oculto.py" (
    echo ✓ Arquivo encontrado
    echo Tamanho: 
    dir iniciar_servidor_oculto.py | findstr iniciar
) else (
    echo ✗ Arquivo NAO encontrado
)
echo.

pause

