@echo off
chcp 65001 >nul 2>nul
title Instalador - Sistema Loja de Celulares
setlocal

echo.
echo ============================================================
echo    INSTALACAO - SISTEMA LOJA DE CELULARES
echo ============================================================
echo.

:: ----------------------------------------------------------
:: Tentar PowerShell - Tentativa 1: ExecutionPolicy Bypass
:: ----------------------------------------------------------
where powershell.exe >nul 2>nul
if errorlevel 1 goto :sem_powershell

echo Iniciando instalador principal via PowerShell...
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALADOR.ps1"
if not errorlevel 1 goto :ok

:: ----------------------------------------------------------
:: Tentativa 2: ExecutionPolicy Unrestricted (PS 2.0 Win7)
:: ----------------------------------------------------------
echo.
echo [!] Falha na tentativa 1. Tentando modo compativel...
echo.
powershell.exe -NoProfile -ExecutionPolicy Unrestricted -File "%~dp0INSTALADOR.ps1"
if not errorlevel 1 goto :ok

:: ----------------------------------------------------------
:: Fallback: instalador em modo puro CMD (sem PowerShell)
:: ----------------------------------------------------------
:sem_powershell
echo.
echo [!] PowerShell indisponivel ou bloqueado.
echo     Usando instalador alternativo...
echo.
if exist "%~dp0INSTALAR.bat" (
    call "%~dp0INSTALAR.bat"
    goto :fim
)
echo [ERRO] Instalador alternativo nao encontrado.
pause
exit /b 1

:ok
:fim
endlocal
