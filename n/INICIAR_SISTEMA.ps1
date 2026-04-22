# =============================================================================
#  INICIAR_SISTEMA.ps1 - Loja de Celulares
#  Log unificado de todos os servicos em uma unica janela
# =============================================================================
$ErrorActionPreference = "Continue"

$PROJ_ROOT    = "C:\VS_Code\Celular"
$VENV_PYTHON  = "$PROJ_ROOT\.venv\Scripts\python.exe"
$MANAGE       = "$PROJ_ROOT\manage.py"
$WA_DIR       = "$PROJ_ROOT\whatsapp_service"
$PORTA_DJANGO = 8000
$PORTA_WA     = 3000

$LOG_DJANGO_O = "$PROJ_ROOT\_dout.log"
$LOG_DJANGO_E = "$PROJ_ROOT\_derr.log"
$LOG_WA_O     = "$PROJ_ROOT\_waout.log"
$LOG_WA_E     = "$PROJ_ROOT\_waerr.log"

$host.UI.RawUI.WindowTitle = "Loja de Celulares - Sistema"

function Linha  { Write-Host ("  " + ("-" * 52)) -ForegroundColor DarkGray }
function Passo  { param($m) Write-Host "`n  >>> $m" -ForegroundColor Cyan }
function OK     { param($m) Write-Host "  [OK]   $m" -ForegroundColor Green }
function Aviso  { param($m) Write-Host "  [!]    $m" -ForegroundColor Yellow }
function Erro   { param($m) Write-Host "  [X]    $m" -ForegroundColor Red }
function Info   { param($m) Write-Host "  [i]    $m" -ForegroundColor Gray }

Clear-Host
Write-Host ""
Linha
Write-Host "    LOJA DE CELULARES - INICIALIZANDO SISTEMA" -ForegroundColor Blue
Write-Host "    $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor DarkGray
Linha

# ─── 1. Ambiente Python ───────────────────────────────────────────────────────
Passo "Verificando ambiente Python (.venv)..."
if (-not (Test-Path $VENV_PYTHON)) {
    Erro "Ambiente virtual nao encontrado: $PROJ_ROOT\.venv"
    Aviso "Execute: python -m venv .venv"
    Aviso "Depois:  .venv\Scripts\pip install -r requirements.txt"
    Read-Host "`n  Pressione Enter para sair"; exit 1
}
OK "Python venv pronto."

# ─── 2. Fechar processos nas portas ───────────────────────────────────────────
function Fechar-Porta {
    param([int]$porta, [string]$nome)
    $conns = netstat -ano 2>$null | Select-String ":$porta "
    $pidsList = @()
    foreach ($linha in $conns) {
        $str = $linha.ToString().Trim()
        if ($str -match 'LISTENING|LISTEN') {
            $partes = $str -split '\s+'
            $ultimoPid = $partes[-1]
            if ($ultimoPid -match '^\d+$' -and [int]$ultimoPid -gt 0) {
                $pidsList += [int]$ultimoPid
            }
        }
    }
    foreach ($pidVal in ($pidsList | Sort-Object -Unique)) {
        $proc = Get-Process -Id $pidVal -ErrorAction SilentlyContinue
        if ($null -ne $proc) {
            Aviso "Encerrando '$($proc.Name)' PID=$pidVal (porta $porta/$nome)"
            Stop-Process -Id $pidVal -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 500
            OK "Encerrado."
        }
    }
}

Passo "Verificando portas $PORTA_DJANGO e $PORTA_WA..."
Fechar-Porta -porta $PORTA_DJANGO -nome "Django"
Fechar-Porta -porta $PORTA_WA     -nome "WhatsApp"
Start-Sleep -Milliseconds 600
OK "Portas liberadas."

# ─── 3. Check Django ──────────────────────────────────────────────────────────
Passo "Verificando configuracao Django..."
$checkOut = & $VENV_PYTHON $MANAGE check 2>&1
if ($LASTEXITCODE -ne 0) {
    Erro "Falha na configuracao:"
    $checkOut | ForEach-Object { Erro $_ }
    Read-Host "`n  Pressione Enter para sair"; exit 1
}
OK "Configuracao Django: OK"

# ─── 4. Migracoes ─────────────────────────────────────────────────────────────
Passo "Verificando migracoes..."
& $VENV_PYTHON $MANAGE migrate --check 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Aviso "Migracoes pendentes. Aplicando..."
    $migOut = & $VENV_PYTHON $MANAGE migrate 2>&1
    if ($LASTEXITCODE -ne 0) {
        $migOut | ForEach-Object { Erro $_ }
        Read-Host "`n  Pressione Enter para sair"; exit 1
    }
    $migOut | ForEach-Object { Info $_ }
    OK "Migracoes aplicadas."
} else {
    OK "Banco de dados OK - nenhuma migracao pendente."
}

# ─── 5. Integridade das tabelas ───────────────────────────────────────────────
Passo "Verificando integridade das tabelas..."
$scriptInt = @'
import sys, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","loja.settings")
import django; django.setup()
from django.db import connection
from django.apps import apps
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tdb = {r[0] for r in cursor.fetchall()}
erros = []
total = 0
for m in apps.get_models():
    total += 1
    t = m._meta.db_table
    if t not in tdb:
        erros.append("TABELA AUSENTE: {} ({})".format(t, m.__name__)); continue
    cursor.execute("PRAGMA table_info({});".format(t))
    cols = {r[1] for r in cursor.fetchall()}
    for f in m._meta.local_fields:
        c = getattr(f,"column",None)
        if c and c not in cols:
            erros.append("COLUNA AUSENTE: {}.{} ({}.{})".format(t,c,m.__name__,f.name))
if erros: [print("ERRO: "+e) for e in erros]; sys.exit(1)
else: print("OK: {} modelos verificados.".format(total)); sys.exit(0)
'@
$tmpInt = "$PROJ_ROOT\_chk.py"
$scriptInt | Set-Content -Path $tmpInt -Encoding UTF8
$intOut  = & $VENV_PYTHON $tmpInt 2>&1
$intCode = $LASTEXITCODE
Remove-Item $tmpInt -Force -ErrorAction SilentlyContinue
if ($intCode -ne 0) {
    $intOut | ForEach-Object { Aviso $_ }
    Aviso "Executando syncdb para corrigir..."
    & $VENV_PYTHON $MANAGE migrate --run-syncdb 2>&1 | ForEach-Object { Info $_ }
} else {
    OK ($intOut | Select-Object -Last 1)
}

# ─── 6. Superusuario ──────────────────────────────────────────────────────────
Passo "Verificando superusuario..."
$scriptAdm = @'
import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE","loja.settings")
import django; django.setup()
from django.contrib.auth import get_user_model
U = get_user_model()
if U.objects.filter(is_superuser=True).count() == 0:
    if not U.objects.filter(username="admin").exists():
        U.objects.create_superuser("admin","admin@loja.local","admin123")
        print("NOVO: usuario=admin  senha=admin123")
    else:
        print("OK:existe")
else:
    print("OK:{}".format(U.objects.filter(is_superuser=True).count()))
'@
$tmpAdm = "$PROJ_ROOT\_adm.py"
$scriptAdm | Set-Content -Path $tmpAdm -Encoding UTF8
$admOut = (& $VENV_PYTHON $tmpAdm 2>&1 | Select-Object -Last 1).Trim()
Remove-Item $tmpAdm -Force -ErrorAction SilentlyContinue
if ($admOut -like "NOVO*") { OK $admOut; Aviso "Altere a senha 'admin123' no primeiro acesso!" }
else { OK "Superusuario: $admOut" }

# ─── 7. Verificar Node.js ─────────────────────────────────────────────────────
$nodeOk = $false
Passo "Verificando Node.js para WhatsApp..."
$nodeVer = node --version 2>&1
if ($LASTEXITCODE -eq 0 -and $nodeVer -match 'v(\d+)' -and [int]$Matches[1] -ge 18) {
    $nodeOk = $true
    OK "Node.js $nodeVer encontrado."
    if (-not (Test-Path "$WA_DIR\node_modules")) {
        Aviso "Instalando dependencias npm..."
        Push-Location $WA_DIR; npm install 2>&1 | ForEach-Object { Info $_ }; Pop-Location
        OK "Dependencias instaladas."
    }
} else {
    Aviso "Node.js nao encontrado ou < v18. WhatsApp ignorado."
}

# =============================================================================
# FUNCAO: le novas linhas de um arquivo com FileShare.ReadWrite (tail seguro)
# =============================================================================
function Ler-Log {
    param([string]$arquivo, [ref]$posicao, [string]$prefixo, [string]$corPadrao)
    if (-not (Test-Path $arquivo)) { return }
    try {
        $fs = [System.IO.FileStream]::new(
            $arquivo,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            [System.IO.FileShare]::ReadWrite)
        $sr = [System.IO.StreamReader]::new($fs, [System.Text.Encoding]::UTF8)
        $fs.Seek($posicao.Value, [System.IO.SeekOrigin]::Begin) | Out-Null
        $linha = $sr.ReadLine()
        while ($null -ne $linha) {
            if ($linha.Trim() -ne "") {
                $ts  = Get-Date -Format "HH:mm:ss"
                $cor = $corPadrao
                if ($linha -match 'Error|Exception|Traceback|CRITICAL') { $cor = "Red" }
                elseif ($linha -match 'WARNING|WARN') { $cor = "DarkYellow" }
                Write-Host "  [$ts][$prefixo]  $linha" -ForegroundColor $cor
            }
            $linha = $sr.ReadLine()
        }
        $posicao.Value = $fs.Position
        $sr.Dispose(); $fs.Dispose()
    } catch {}
}

# =============================================================================
# INICIAR OS PROCESSOS
# =============================================================================
Write-Host ""
Linha
Write-Host "    INICIANDO SERVICOS - LOG UNIFICADO" -ForegroundColor Blue
Linha
Write-Host ""

# Limpa logs antigos
foreach ($f in @($LOG_DJANGO_O,$LOG_DJANGO_E,$LOG_WA_O,$LOG_WA_E)) {
    Remove-Item $f -Force -ErrorAction SilentlyContinue
}

# Django
$procDjango = Start-Process `
    -FilePath       $VENV_PYTHON `
    -ArgumentList   "$MANAGE runserver $PORTA_DJANGO" `
    -WorkingDirectory $PROJ_ROOT `
    -RedirectStandardOutput $LOG_DJANGO_O `
    -RedirectStandardError  $LOG_DJANGO_E `
    -WindowStyle    Hidden `
    -PassThru

OK "Django iniciado (PID $($procDjango.Id)) -> http://127.0.0.1:$PORTA_DJANGO"

# WhatsApp
$procWA = $null
if ($nodeOk -and (Test-Path "$WA_DIR\package.json")) {
    $nodePath = (Get-Command node).Source
    $procWA = Start-Process `
        -FilePath       $nodePath `
        -ArgumentList   "index.js" `
        -WorkingDirectory $WA_DIR `
        -RedirectStandardOutput $LOG_WA_O `
        -RedirectStandardError  $LOG_WA_E `
        -WindowStyle    Hidden `
        -PassThru
    OK "WhatsApp Service iniciado (PID $($procWA.Id)) -> http://localhost:$PORTA_WA"
}

Write-Host ""
Linha
Write-Host "  Sistema:   http://127.0.0.1:$PORTA_DJANGO" -ForegroundColor Cyan
Write-Host "  Admin:     http://127.0.0.1:$PORTA_DJANGO/admin/" -ForegroundColor Cyan
if ($procWA) { Write-Host "  WhatsApp:  http://localhost:$PORTA_WA/status" -ForegroundColor Cyan }
Write-Host ""
Write-Host "  Legenda:  [DJANGO] verde   [WA] amarelo   erros vermelho" -ForegroundColor DarkGray
Write-Host "  Pressione CTRL+C para encerrar todos os servicos." -ForegroundColor DarkGray
Linha
Write-Host ""

[long]$posDjangoO = 0; [long]$posDjangoE = 0
[long]$posWAO     = 0; [long]$posWAE     = 0

# =============================================================================
# LOOP PRINCIPAL
# =============================================================================
try {
    while ($true) {
        Ler-Log -arquivo $LOG_DJANGO_O -posicao ([ref]$posDjangoO) -prefixo "DJANGO" -corPadrao "Green"
        Ler-Log -arquivo $LOG_DJANGO_E -posicao ([ref]$posDjangoE) -prefixo "DJANGO" -corPadrao "Green"

        if ($procWA) {
            Ler-Log -arquivo $LOG_WA_O -posicao ([ref]$posWAO) -prefixo "WA    " -corPadrao "Yellow"
            Ler-Log -arquivo $LOG_WA_E -posicao ([ref]$posWAE) -prefixo "WA    " -corPadrao "Yellow"
        }

        # Detecta crash do Django
        if ($procDjango.HasExited) {
            Write-Host ""
            Erro "Django encerrou inesperadamente! (codigo: $($procDjango.ExitCode))"
            # Drena o restante dos logs
            Ler-Log -arquivo $LOG_DJANGO_O -posicao ([ref]$posDjangoO) -prefixo "DJANGO" -corPadrao "Red"
            Ler-Log -arquivo $LOG_DJANGO_E -posicao ([ref]$posDjangoE) -prefixo "DJANGO" -corPadrao "Red"
            break
        }

        Start-Sleep -Milliseconds 250
    }
}
finally {
    Write-Host ""
    Linha
    Aviso "Encerrando servicos..."

    if ($null -ne $procDjango -and -not $procDjango.HasExited) {
        $procDjango.Kill(); $procDjango.Dispose()
        OK "Django encerrado."
    }
    if ($null -ne $procWA -and -not $procWA.HasExited) {
        $procWA.Kill(); $procWA.Dispose()
        OK "WhatsApp Service encerrado."
    }

    # Remove arquivos de log temporarios
    foreach ($f in @($LOG_DJANGO_O,$LOG_DJANGO_E,$LOG_WA_O,$LOG_WA_E)) {
        Remove-Item $f -Force -ErrorAction SilentlyContinue
    }

    Linha
    Write-Host "  Sistema finalizado em $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor DarkGray
    Write-Host ""
    Read-Host "  Pressione Enter para fechar"
}
