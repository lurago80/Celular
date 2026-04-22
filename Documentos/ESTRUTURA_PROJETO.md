# 📁 Estrutura do Projeto - Arquivos Essenciais

## ✅ Arquivos e Pastas Mantidos

### 🔧 Core do Django (ESSENCIAL)
- `manage.py` - Script de gerenciamento Django
- `requirements.txt` - Dependências Python
- `db.sqlite3` - Banco de dados SQLite

### 📂 Pastas Principais
- `core/` - Aplicação principal Django
  - `models.py` - Modelos de dados
  - `views.py` - Views e lógica de negócio
  - `urls.py` - Rotas da aplicação
  - `admin.py` - Configuração do Django Admin
  - `forms.py` - Formulários
  - `migrations/` - Migrações do banco de dados
- `loja/` - Configurações do projeto Django
  - `settings.py` - Configurações
  - `urls.py` - URLs principais
  - `wsgi.py` / `asgi.py` - Servidores WSGI/ASGI
- `templates/` - Templates HTML do sistema
- `static/` - Arquivos estáticos (CSS, JS, imagens)
- `media/` - Arquivos de mídia enviados pelos usuários
- `backups/` - Backups do banco de dados
- `Termos/` - PDFs de termos de garantia e compra
- `Projeto/` - Documentação do projeto

### 🐍 Scripts Python
- `gerar_chave_licenca.py` - Gera chaves de licença do sistema
- `iniciar_servidor_oculto.py` - Inicia o servidor Django de forma oculta (sem janelas)
- `criar_admin.py` - Script auxiliar para criar usuário administrador

### 🚀 Scripts de Inicialização
- `INICIAR_SERVIDOR_OCULTO.vbs` - **Script principal**: Inicia servidor oculto (sem janelas CMD/PowerShell)
- `INICIAR_FINAL.vbs` - Alternativa simplificada de inicialização
- `VERIFICAR_SERVIDOR.bat` - Diagnóstico do status do servidor

### 📚 Documentação
- `README.md` - Documentação principal do projeto
- `SISTEMA_LICENCA.md` - Documentação do sistema de licenças
- `TERMO_COMPRA_README.md` - Documentação sobre termos de compra
- `TERMO_GARANTIA_ATUALIZADO.md` - Documentação sobre termos de garantia
- `ARQUIVOS_REMOVIDOS.md` - Lista de arquivos removidos na limpeza

---

## 🔄 Como Iniciar o Sistema

### Opção 1: Inicialização Oculto (Recomendado)
1. Execute `INICIAR_SERVIDOR_OCULTO.vbs` (duplo clique)
2. O servidor inicia automaticamente sem mostrar janelas
3. O navegador abre automaticamente em `http://localhost:8000`

### Opção 2: Inicialização Manual
1. Abra um terminal na pasta do projeto
2. Ative o ambiente virtual: `.venv\Scripts\activate`
3. Execute: `python manage.py runserver`
4. Acesse: `http://127.0.0.1:8000`

### Verificar Status do Servidor
Execute `VERIFICAR_SERVIDOR.bat` para verificar:
- Se o servidor está rodando
- Processos Python ativos
- Arquivos de log
- Detalhes de diagnóstico

---

## 📝 Notas Importantes

### Scripts de Instalação
**ATENÇÃO**: Os scripts de instalação foram removidos durante a limpeza. Se precisar reinstalar:
1. Use `pip install -r requirements.txt`
2. Execute `python manage.py migrate`
3. Crie usuário admin com `python manage.py createsuperuser` ou use `criar_admin.py`

### Ambiente Virtual
O ambiente virtual (`.venv/`) não está visível na listagem acima, mas deve estar presente no projeto.

### Banckups
Os backups são gerados automaticamente em `backups/`. Não exclua essa pasta.

---

**Última atualização:** Limpeza realizada removendo ~35 arquivos desnecessários

