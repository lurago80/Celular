@echo off
chcp 65001 >nul
title Criar Atalho - Sistema Loja de Celulares

echo.
echo  Criando atalho na Area de Trabalho...
echo.

:: Gera um VBScript temporario para criar o atalho
set "SCRIPT_TEMP=%TEMP%\criar_atalho_tmp.vbs"
set "PASTA=%~dp0"
:: Remove barra final se houver
if "%PASTA:~-1%"=="\" set "PASTA=%PASTA:~0,-1%"

(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo Desktop = WshShell.SpecialFolders^("Desktop"^)
echo Set SC = WshShell.CreateShortcut^(Desktop ^& "\Sistema Loja de Celulares.lnk"^)
echo SC.TargetPath = "%PASTA%\INICIAR_SERVIDOR_OCULTO.vbs"
echo SC.WorkingDirectory = "%PASTA%"
echo SC.Description = "Iniciar Sistema Loja de Celulares"
echo SC.IconLocation = "C:\Windows\System32\shell32.dll,14"
echo SC.Save^(^)
echo WScript.Echo "Atalho criado com sucesso!"
) > "%SCRIPT_TEMP%"

cscript //nologo "%SCRIPT_TEMP%"
del "%SCRIPT_TEMP%" >nul 2>&1

echo.
echo  Atalho "Sistema Loja de Celulares" criado na Area de Trabalho!
echo  Basta dar duplo clique nele para iniciar o sistema.
echo.
pause
