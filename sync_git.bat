# Script de sincronização automática

# Este script faz commit e push automático de todas as alterações no projeto.
# Salve como sync_git.bat na raiz do projeto.

@echo off
cd /d %~dp0
git add .
git commit -m "Atualização automática"
git push
