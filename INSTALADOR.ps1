# ==============================================================================
#  INSTALADOR.ps1 - Sistema Loja de Celulares
#  Execute com:  INSTALADOR.bat  (duplo clique)
#  Versao: 1.1  |  11/03/2026  (compativel Windows 7 / PS 3.0+)
# ==============================================================================

# Verificacao de versao do PowerShell em runtime (compativel com todas as versoes)
if ($PSVersionTable.PSVersion.Major -lt 3) {
    Write-Host ""
    Write-Host "  [ERRO] PowerShell 3.0 ou superior e necessario." -ForegroundColor Red
    Write-Host "  Sua versao atual: $($PSVersionTable.PSVersion)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Para atualizar no Windows 7:" -ForegroundColor White
    Write-Host "    Baixe o Windows Management Framework 5.1 em:" -ForegroundColor Cyan
    Write-Host "    https://www.microsoft.com/download/details.aspx?id=54616" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

$ErrorActionPreference = "Continue"
$ProgressPreference    = "SilentlyContinue"

# --- CONFIGURACAO -------------------------------------------------------------
$NOME_SISTEMA   = "Sistema Loja de Celulares"
$VERSAO         = "1.0"
$DESTINO_PADRAO = "C:\SistemaLoja"
$PORTA          = 8000
$OSV            = [Environment]::OSVersion.Version
$IS_WINDOWS_7   = ($OSV.Major -eq 6 -and $OSV.Minor -eq 1)
$PYTHON_REQUISITO = if ($IS_WINDOWS_7) { "3.8.x" } else { "3.8+" }
# Compativel com PowerShell 2.0/3.0 ($PSScriptRoot so existe a partir do PS 3.0)
if ($PSScriptRoot) { $FONTE = $PSScriptRoot } else { $FONTE = Split-Path -Parent $MyInvocation.MyCommand.Definition }

# Pastas e arquivos excluidos ao copiar para o destino
$EXCLUIR_PASTAS = @(
    '.venv', '__pycache__', '.git', 'node_modules',
    'backups', 'logs', 'staticfiles', '.vscode'
)
$EXCLUIR_ARQUIVOS = @(
    '*.pyc', '*.pyo', '*.log', 'db.sqlite3',
    '_dout.log', '_derr.log', '_waout.log', '_waerr.log',
    'INSTALADOR.ps1', 'INSTALADOR.bat'
)

# --- HELPERS UI ---------------------------------------------------------------
function Linha {
    param([string]$c = "-", [int]$n = 64)
    Write-Host ("  " + ($c * $n)) -ForegroundColor DarkGray
}
function OK    { param([string]$m) Write-Host "      OK  $m" -ForegroundColor Green }
function INFO  { param([string]$m) Write-Host "      >>  $m" -ForegroundColor Cyan }
function AVISO { param([string]$m) Write-Host "       !  $m" -ForegroundColor Yellow }
function FALHA { param([string]$m) Write-Host "       X  $m" -ForegroundColor Red }

function Cabecalho {
    Clear-Host
    Write-Host ""
    Linha "=" 64
    Write-Host "    $NOME_SISTEMA  -  Instalador v$VERSAO" -ForegroundColor Cyan
    Write-Host "    $(Get-Date -Format 'dd/MM/yyyy HH:mm')  |  Windows" -ForegroundColor DarkGray
    Linha "=" 64
    Write-Host ""
}

function Passo {
    param([int]$i, [int]$t, [string]$m)
    Write-Host ""
    Write-Host "  [$i/$t]  $m" -ForegroundColor Yellow
    Linha
}

function Pausar {
    param([string]$m = "Pressione Enter para continuar...")
    Write-Host ""
    Write-Host "  $m" -ForegroundColor DarkGray
    $null = Read-Host
}

function Confirmar {
    param([string]$pergunta, [string]$padrao = "S")
    if ($padrao -eq "S") { $suf = "[S/n]" } else { $suf = "[s/N]" }
    Write-Host "      ?  $pergunta $suf : " -ForegroundColor White -NoNewline
    $r = Read-Host
    if ([string]::IsNullOrWhiteSpace($r)) { $r = $padrao }
    return ($r.Trim().ToUpper() -in @("S","SIM","Y","YES"))
}

function LerTexto {
    param([string]$prompt, [string]$padrao = "")
    if ($padrao) {
        Write-Host "      ?  $prompt [$padrao] : " -ForegroundColor White -NoNewline
    } else {
        Write-Host "      ?  $prompt : " -ForegroundColor White -NoNewline
    }
    $r = Read-Host
    if ([string]::IsNullOrWhiteSpace($r)) { return $padrao }
    return $r.Trim()
}

function LerSenha {
    param([string]$prompt)
    Write-Host "      ?  $prompt : " -ForegroundColor White -NoNewline
    $ss  = Read-Host -AsSecureString
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ss)
    $txt = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    return $txt
}

# --------------------------- TELA INICIAL -------------------------------------
Cabecalho
Write-Host "  Este instalador vai configurar o $NOME_SISTEMA" -ForegroundColor White
Write-Host "  no seu computador de forma automatica." -ForegroundColor Gray
Write-Host ""
Write-Host "  O que sera feito:" -ForegroundColor White
Write-Host "    1.  Verificar Python instalado (compativel com o Windows)" -ForegroundColor Gray
    Write-Host "    2.  Verificar Node.js instalado (servico WhatsApp)" -ForegroundColor Gray
    Write-Host "    3.  Escolher pasta de instalacao" -ForegroundColor Gray
    Write-Host "    4.  Copiar arquivos do sistema" -ForegroundColor Gray
    Write-Host "    5.  Criar ambiente Python virtual" -ForegroundColor Gray
    Write-Host "    6.  Instalar dependencias Python" -ForegroundColor Gray
    Write-Host "    7.  Instalar dependencias Node.js (WhatsApp)" -ForegroundColor Gray
    Write-Host "    8.  Configurar banco de dados" -ForegroundColor Gray
    Write-Host "    9.  Criar usuario administrador" -ForegroundColor Gray
    Write-Host "   10.  Criar atalhos" -ForegroundColor Gray
Write-Host ""
if (-not (Confirmar "Deseja iniciar a instalacao agora?" "S")) {
    Write-Host ""
    AVISO "Instalacao cancelada."
    Pausar "Pressione Enter para sair."
    exit 0
}

# --------------------------- 1. PYTHON ----------------------------------------
Cabecalho
Passo 1 10 "Verificando Python..."

$pythonCmd = $null
$pythonVer  = $null

foreach ($cmd in @("python", "python3", "py")) {
    try {
        $v = & $cmd --version 2>&1
        if ($v -match "Python (\d+\.\d+)") {
            $verStr = $Matches[1]
            $partes = $verStr.Split('.')
            $major  = [int]$partes[0]
            $minor  = [int]$partes[1]
            $versaoOk = $false
            if ($IS_WINDOWS_7) {
                # No Windows 7 o Python suportado oficialmente e a linha 3.8.
                $versaoOk = ($major -eq 3 -and $minor -eq 8)
            } else {
                $versaoOk = ($major -eq 3 -and $minor -ge 8)
            }
            if ($versaoOk) {
                $pythonCmd = $cmd
                $pythonVer = ($v -replace "Python ","").Trim()
                break
            }
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host ""
    if ($IS_WINDOWS_7) {
        FALHA "Python 3.8.x nao encontrado no sistema!"
    } else {
        FALHA "Python 3.8+ nao encontrado no sistema!"
    }
    Write-Host ""
    Write-Host "  Para instalar o Python:" -ForegroundColor White
    if ($IS_WINDOWS_7) {
        Write-Host "    1. Baixe Python 3.8.10 em:" -ForegroundColor Cyan
        Write-Host "       https://www.python.org/downloads/release/python-3810/" -ForegroundColor Cyan
    } else {
        Write-Host "    1. Baixe em: https://www.python.org/downloads/" -ForegroundColor Cyan
    }
    Write-Host "    2. Execute o instalador" -ForegroundColor Cyan
    Write-Host "    3. IMPORTANTE: marque 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host "    4. Apos instalar, execute este instalador novamente" -ForegroundColor Cyan
    Write-Host ""
    if (Confirmar "Abrir pagina de download do Python no navegador?" "S") {
        if ($IS_WINDOWS_7) {
            Start-Process "https://www.python.org/downloads/release/python-3810/"
        } else {
            Start-Process "https://www.python.org/downloads/"
        }
    }
    Pausar "Pressione Enter para sair."
    exit 1
}

Write-Host ""
OK "Python $pythonVer encontrado! (comando: $pythonCmd)"
INFO "Regra de compatibilidade aplicada: Python $PYTHON_REQUISITO"

# --------------------------- 2. NODE.JS ---------------------------------------
Cabecalho
Passo 2 10 "Verificando Node.js..."

$nodeCmd = $null
$nodeVer  = $null

foreach ($cmd in @("node", "node.exe")) {
    try {
        $v = & $cmd --version 2>&1
        if ($v -match "v(\d+)\.(\d+)") {
            $nodeMajor = [int]$Matches[1]
            if ($nodeMajor -ge 18) {
                $nodeCmd = $cmd
                $nodeVer = $v.Trim()
                break
            }
        }
    } catch {}
}

if (-not $nodeCmd) {
    Write-Host ""
    FALHA "Node.js 18+ nao encontrado no sistema!"
    Write-Host ""
    Write-Host "  O servico de WhatsApp requer Node.js 18 ou superior." -ForegroundColor White
    Write-Host "  Para instalar:" -ForegroundColor White
    Write-Host "    1. Baixe em: https://nodejs.org/en/download" -ForegroundColor Cyan
    Write-Host "    2. Execute o instalador (LTS recomendado)" -ForegroundColor Cyan
    Write-Host "    3. IMPORTANTE: mantenha 'Add to PATH' marcado" -ForegroundColor Yellow
    Write-Host "    4. Apos instalar, execute este instalador novamente" -ForegroundColor Cyan
    Write-Host ""
    if (Confirmar "Abrir pagina de download do Node.js no navegador?" "S") {
        Start-Process "https://nodejs.org/en/download"
    }
    Write-Host ""
    if (Confirmar "Continuar a instalacao SEM o servico de WhatsApp?" "N") {
        AVISO "Continuando sem Node.js. O servico de WhatsApp nao estara disponivel."
        $nodeCmd = $null
    } else {
        Pausar "Instale o Node.js e execute este instalador novamente. Pressione Enter para sair."
        exit 1
    }
} else {
    Write-Host ""
    OK "Node.js $nodeVer encontrado! (comando: $nodeCmd)"
    # Verificar npm
    try {
        $npmVer = & npm --version 2>&1
        OK "npm $npmVer encontrado."
    } catch {
        AVISO "npm nao encontrado. As dependencias do WhatsApp nao serao instaladas."
        $nodeCmd = $null
    }
}

# --------------------------- 3. PASTA DE INSTALAcaO ---------------------------
Cabecalho
Passo 3 10 "Escolhendo pasta de instalacao."
Write-Host ""
Write-Host "  Onde instalar o sistema?" -ForegroundColor White
Write-Host "  Padrao recomendado: $DESTINO_PADRAO" -ForegroundColor Gray
Write-Host ""

$DESTINO = LerTexto "Pasta de instalacao" $DESTINO_PADRAO
$MANTER_BD = $false

# Verificar instalacao anterior
if (Test-Path "$DESTINO\manage.py") {
    Write-Host ""
    AVISO "Ja existe uma instalacao em: $DESTINO"
    Write-Host ""
    if (Confirmar "Deseja ATUALIZAR (preservar banco de dados existente)?" "S") {
        $MANTER_BD = $true
        INFO "Atualizacao selecionada. Banco de dados sera preservado."
    } else {
        FALHA "Operacao cancelada. Escolha outra pasta ou confirme S para atualizar."
        Pausar
        exit 1
    }
}

Write-Host ""
INFO "Destino: $DESTINO"

# --------------------------- 4. COPIAR ARQUIVOS -------------------------------
Cabecalho
Passo 4 10 "Copiando arquivos do sistema..."

if (-not (Test-Path "$FONTE\manage.py")) {
    Write-Host ""
    FALHA "Arquivos do projeto nao encontrados em: $FONTE"
    FALHA "Certifique-se de que o instalador esta dentro da pasta do projeto."
    Pausar
    exit 1
}

if (-not (Test-Path $DESTINO)) {
    New-Item -ItemType Directory -Path $DESTINO -Force | Out-Null
    OK "Pasta criada: $DESTINO"
}

$contadorCopiados = 0
$contadorIgnorados = 0

function Copiar-Projeto {
    param([string]$origem, [string]$destino)
    $itens = Get-ChildItem -Path $origem -Force -ErrorAction SilentlyContinue
    foreach ($item in $itens) {
        if ($item.PSIsContainer) {
            if ($EXCLUIR_PASTAS -contains $item.Name) {
                $script:contadorIgnorados++
                continue
            }
            $subDest = Join-Path $destino $item.Name
            if (-not (Test-Path $subDest)) {
                New-Item -ItemType Directory -Path $subDest -Force | Out-Null
            }
            Copiar-Projeto -origem $item.FullName -destino $subDest
        } else {
            $excluir = $false
            foreach ($padrao in $EXCLUIR_ARQUIVOS) {
                if ($item.Name -like $padrao) { $excluir = $true; break }
            }
            if ($MANTER_BD -and $item.Name -eq "db.sqlite3") {
                INFO "Preservando banco de dados existente."
                continue
            }
            if ($excluir) { $script:contadorIgnorados++; continue }
            Copy-Item -Path $item.FullName -Destination (Join-Path $destino $item.Name) -Force
            $script:contadorCopiados++
        }
    }
}

Write-Host ""
INFO "Origem : $FONTE"
INFO "Destino: $DESTINO"
Write-Host ""

Copiar-Projeto -origem $FONTE -destino $DESTINO

Write-Host ""
OK "$contadorCopiados arquivo(s) copiado(s).  ($contadorIgnorados ignorado(s))"

# --------------------------- 5. AMBIENTE VIRTUAL ------------------------------
Cabecalho
Passo 5 10 "Configurando ambiente Python (.venv)..."

$VENV    = "$DESTINO\.venv"
$VENV_PY = "$VENV\Scripts\python.exe"

Write-Host ""
if (Test-Path $VENV_PY) {
    OK "Ambiente virtual ja existe. Reutilizando."
} else {
    INFO "Criando ambiente virtual em $VENV ..."
    & $pythonCmd -m venv $VENV 2>&1
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VENV_PY)) {
        Write-Host ""
        FALHA "Falha ao criar ambiente virtual!"
        FALHA "Verifique se o Python tem permissao de escrita em: $VENV"
        Pausar
        exit 1
    }
    OK "Ambiente virtual criado com sucesso."
}

# --------------------------- 6. DEPENDeNCIAS PYTHON ---------------------------
Cabecalho
Passo 6 10 "Instalando dependencias Python..."

Write-Host ""
INFO "Atualizando pip..."
& $VENV_PY -m pip install --upgrade "pip<25" --quiet --no-warn-script-location 2>&1 | Out-Null
OK "pip atualizado."

Write-Host ""
INFO "Instalando pacotes (requirements.txt)..."
INFO "Aguarde  -  pode demorar alguns minutos na primeira instalacao."
Write-Host ""

& $VENV_PY -m pip install -r "$DESTINO\requirements.txt" --no-warn-script-location

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    AVISO "ATENCAO: Alguns pacotes podem ter falhado."
    AVISO "No Windows 7, a configuracao recomendada e Python 3.8.x."
    AVISO "WeasyPrint (geracao de PDF) pode exigir GTK+ separado no Windows."
    AVISO "O sistema funciona normalmente sem o GTK+  -  apenas PDFs nao serao gerados."
    Write-Host ""
    if (-not (Confirmar "Continuar a instalacao mesmo assim?" "S")) {
        Pausar
        exit 1
    }
} else {
    Write-Host ""
    OK "Todas as dependencias instaladas com sucesso!"
}

# --------------------------- 7. DEPENDeNCIAS NODE.JS --------------------------
Cabecalho
Passo 7 10 "Instalando dependencias Node.js (WhatsApp)..."

if ($nodeCmd) {
    $waDir = Join-Path $DESTINO "whatsapp_service"
    $waMods = Join-Path $waDir "node_modules"
    $waPkg  = Join-Path $waDir "package.json"

    if (-not (Test-Path $waPkg)) {
        AVISO "Pasta whatsapp_service nao encontrada em $waDir. Pulando."
    } elseif (Test-Path $waMods) {
        OK "node_modules ja existe. Pulando npm install."
    } else {
        Write-Host ""
        INFO "Executando npm install em $waDir ..."
        INFO "Aguarde  -  pode demorar alguns minutos na primeira instalacao."
        Write-Host ""
        Push-Location $waDir
        & npm install 2>&1
        $npmExit = $LASTEXITCODE
        Pop-Location
        if ($npmExit -ne 0) {
            Write-Host ""
            AVISO "npm install reportou erros. O servico de WhatsApp pode nao funcionar."
            AVISO "Voce pode tentar manualmente: cd $waDir && npm install"
        } else {
            Write-Host ""
            OK "Dependencias Node.js instaladas com sucesso!"
        }
    }
} else {
    AVISO "Node.js nao disponivel. Etapa ignorada."
}

# --------------------------- 8. BANCO DE DADOS --------------------------------
Cabecalho
Passo 8 10 "Configurando banco de dados..."

Set-Location $DESTINO

Write-Host ""
INFO "Aplicando migracoes do banco de dados..."
$migrateOut = & $VENV_PY manage.py migrate --noinput 2>&1
$migrateOut | ForEach-Object { Write-Host "      $_" -ForegroundColor DarkGray }

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    FALHA "Falha ao aplicar migracoes!"
    FALHA "Verifique as mensagens acima."
    Pausar
    exit 1
}
Write-Host ""
OK "Banco de dados configurado com sucesso!"

# --------------------------- 9. USUaRIO ADMIN ---------------------------------
Cabecalho
Passo 9 10 "Criando usuario administrador..."

Write-Host ""
Write-Host "  Defina as credenciais do usuario administrador do sistema." -ForegroundColor White
Write-Host "  (Pressione Enter para aceitar os valores padrao)" -ForegroundColor Gray
Write-Host ""

$ADM_USER  = LerTexto "Nome de usuario" "admin"
$ADM_EMAIL = LerTexto "E-mail"          "admin@loja.com"

# Pedir senha com confirmacao
$senhaOk  = $false
$ADM_PASS = ""
while (-not $senhaOk) {
    $s1 = LerSenha "Senha (Enter = usar 'admin123')"
    if ([string]::IsNullOrWhiteSpace($s1)) {
        $ADM_PASS = "admin123"
        AVISO "Senha padrao: admin123   -   ALTERE apos o primeiro acesso!"
        $senhaOk = $true
    } else {
        $s2 = LerSenha "Confirmar senha"
        if ($s1 -eq $s2) {
            if ($s1.Length -lt 6) {
                AVISO "A senha deve ter pelo menos 6 caracteres. Tente novamente."
            } else {
                $ADM_PASS = $s1
                $senhaOk  = $true
            }
        } else {
            FALHA "Senhas nao conferem. Tente novamente."
        }
    }
}

Write-Host ""
INFO "Criando usuario '$ADM_USER'..."

$env:DJANGO_SUPERUSER_USERNAME = $ADM_USER
$env:DJANGO_SUPERUSER_PASSWORD = $ADM_PASS
$env:DJANGO_SUPERUSER_EMAIL    = $ADM_EMAIL

$criarOut = & $VENV_PY manage.py createsuperuser --noinput 2>&1

Remove-Item env:DJANGO_SUPERUSER_USERNAME -ErrorAction SilentlyContinue
Remove-Item env:DJANGO_SUPERUSER_PASSWORD -ErrorAction SilentlyContinue
Remove-Item env:DJANGO_SUPERUSER_EMAIL    -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    OK "Usuario '$ADM_USER' criado com sucesso!"
} else {
    # Na atualizacao o usuario pode ja existir  -  nao e erro
    AVISO "Usuario '$ADM_USER' ja existia ou nao foi criado automaticamente."
    AVISO "Voce pode criar/redefinir via: http://localhost:$PORTA/admin/"
}

# --------------------------- 10. ATALHOS --------------------------------------
Cabecalho
Passo 10 10 "Criando atalhos..."

$WshShell = New-Object -ComObject WScript.Shell

Write-Host ""

# -- Atalho area de Trabalho ---------------------------------------------------
if (Confirmar "Criar atalho 'Sistema Loja' na Area de Trabalho?" "S") {
    $Desktop  = [System.Environment]::GetFolderPath("Desktop")
    $SC = $WshShell.CreateShortcut("$Desktop\Sistema Loja.lnk")
    $SC.TargetPath       = "$DESTINO\INICIAR_SERVIDOR_OCULTO.vbs"
    $SC.WorkingDirectory = $DESTINO
    $SC.Description      = $NOME_SISTEMA
    $SC.IconLocation     = "C:\Windows\System32\shell32.dll,14"
    $SC.Save()
    OK "Atalho criado na Area de Trabalho."
}

Write-Host ""

# -- Atalho Menu Iniciar -------------------------------------------------------
if (Confirmar "Criar atalho no Menu Iniciar?" "S") {
    $StartMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Sistema Loja"
    New-Item -ItemType Directory -Path $StartMenu -Force | Out-Null

    $SC1 = $WshShell.CreateShortcut("$StartMenu\Iniciar Sistema.lnk")
    $SC1.TargetPath       = "$DESTINO\INICIAR_SERVIDOR_OCULTO.vbs"
    $SC1.WorkingDirectory = $DESTINO
    $SC1.Description      = $NOME_SISTEMA
    $SC1.IconLocation     = "C:\Windows\System32\shell32.dll,14"
    $SC1.Save()

    $SC2 = $WshShell.CreateShortcut("$StartMenu\Abrir no Navegador.lnk")
    $SC2.TargetPath       = "http://localhost:$PORTA/"
    $SC2.WorkingDirectory = $DESTINO
    $SC2.Description      = "Abrir $NOME_SISTEMA no navegador"
    $SC2.IconLocation     = "C:\Windows\System32\shell32.dll,13"
    $SC2.Save()

    OK "Atalhos criados no Menu Iniciar."
}

Write-Host ""

# -- Inicializacao automatica com Windows --------------------------------------
if (Confirmar "Iniciar o sistema automaticamente com o Windows?" "N") {
    $StartupDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
    $SCauto = $WshShell.CreateShortcut("$StartupDir\SistemaLoja.lnk")
    $SCauto.TargetPath       = "$DESTINO\INICIAR_SERVIDOR_OCULTO.vbs"
    $SCauto.WorkingDirectory = $DESTINO
    $SCauto.Description      = "$NOME_SISTEMA - Autostart"
    $SCauto.Save()
    OK "Sistema configurado para iniciar automaticamente com o Windows."
} else {
    INFO "Autostart nao configurado. Inicie manualmente pelo atalho."
}

# --------------------------- CONCLUSaO ----------------------------------------
Cabecalho
Linha "=" 64
Write-Host "    INSTALACAO CONCLUIDA COM SUCESSO!" -ForegroundColor Green
Linha "=" 64
Write-Host ""
Write-Host "  Instalado em : $DESTINO" -ForegroundColor Cyan
Write-Host "  Porta        : $PORTA" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Credenciais de acesso:" -ForegroundColor White
Write-Host "    Usuario : $ADM_USER" -ForegroundColor Cyan
Write-Host "    Senha   : $ADM_PASS" -ForegroundColor Yellow
if ($ADM_PASS -eq "admin123") {
    Write-Host ""
    Write-Host "  !! ATENCAO: ALTERE A SENHA PADRAO apos o primeiro acesso !!" -ForegroundColor Red
}
Write-Host ""
Write-Host "  Como iniciar:" -ForegroundColor White
Write-Host "    -> Atalho 'Sistema Loja' na Area de Trabalho" -ForegroundColor Gray
Write-Host "    -> Ou abra: $DESTINO\INICIAR_SERVIDOR_OCULTO.vbs" -ForegroundColor Gray
Write-Host ""
Write-Host "  Apos iniciar, acesse no navegador:" -ForegroundColor White
Write-Host "    http://localhost:$PORTA" -ForegroundColor Cyan
Write-Host ""

# -- Backup info ---------------------------------------------------------------
Linha
Write-Host ""
Write-Host "  BACKUP: O banco de dados fica em:" -ForegroundColor Yellow
Write-Host "    $DESTINO\db.sqlite3" -ForegroundColor Gray
Write-Host "  Faca backup periodico deste arquivo!" -ForegroundColor Yellow
Write-Host ""
Linha "=" 64
Write-Host ""

if (Confirmar "Deseja iniciar o sistema agora?" "S") {
    INFO "Iniciando servidor em segundo plano..."
    Start-Process "$DESTINO\INICIAR_SERVIDOR_OCULTO.vbs"
    Write-Host ""
    INFO "Aguardando servidor iniciar..."
    Start-Sleep -Seconds 4
    INFO "Abrindo navegador..."
    Start-Process "http://localhost:$PORTA"
}

Write-Host ""
Pausar "Pressione Enter para fechar o instalador."
