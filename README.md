# Sistema de Loja de Celulares - MVP

Sistema completo para gestao de loja de celulares desenvolvido em Django 4.2 LTS.

## Funcionalidades

- ✅ **Cadastro de Clientes**: Gestão completa de clientes
- ✅ **Produtos**: Cadastro de celulares e acessórios com controle de estoque
- ✅ **Vendas**: Sistema completo de vendas com itens e trade-in
- ✅ **Compras**: Gestão de compras para reposição de estoque
- ✅ **Garantias**: Geração automática de certificados de garantia em PDF
- ✅ **Dashboard**: Visão geral de vendas, estoque e estatísticas
- ✅ **Django Admin**: Interface administrativa completa

## Estrutura do Projeto

```
Celular/
├── loja/              # Configurações do projeto
├── core/              # Aplicação principal
│   ├── models.py      # Modelos de dados
│   ├── views.py       # Views do sistema
│   ├── admin.py       # Configuração do Django Admin
│   ├── forms.py       # Formulários
│   └── urls.py        # URLs da aplicação
├── templates/         # Templates HTML
│   ├── base.html
│   └── core/
├── media/             # Arquivos de mídia (PDFs)
├── static/            # Arquivos estáticos
└── manage.py          # Script de gerenciamento Django
```

## Instalação e Configuração

### Pre-requisitos

- Windows 7: Python 3.8.x
- Windows 10/11: Python 3.8+
- pip (o instalador atualiza automaticamente para uma versao compativel)

### Compatibilidade Windows 7

- O instalador principal (INSTALADOR.ps1) valida e aplica a regra de Python 3.8.x.
- O nucleo do sistema (Django + SQLite + Pillow) funciona no Windows 7.
- WeasyPrint (PDF) e opcional no Windows 7 e pode exigir GTK Runtime.
- Servico WhatsApp (Node.js/Baileys) exige Node 18 e deve ser tratado como opcional no Windows 7.

### Passos para Instalação

1. **Ativar o ambiente virtual**:
```bash
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

2. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

3. **Aplicar migrações**:
```bash
python manage.py migrate
```

4. **Criar superusuário** (opcional):
```bash
python manage.py createsuperuser --username admin --email admin@local
```

5. **Executar o servidor**:
```bash
python manage.py runserver
```

## Acesso ao Sistema

### Interface Web
- URL: http://127.0.0.1:8000/
- Login: admin / admin123 (ou use suas credenciais do superusuário)

### Django Admin
- URL: http://127.0.0.1:8000/admin/

## Modelos de Dados

### Emitente
Informações da empresa (nome, CNPJ, endereço, prazos de garantia).

### Cliente
Clientes da loja (nome, CPF, telefone, endereço).

### Fornecedor
Fornecedores de produtos.

### Produto
Produtos cadastrados (celulares e acessórios):
- Tipo (celular/acessório)
- Marca e modelo
- Preço e estoque
- Status ativo/inativo

### Venda
Vendas realizadas:
- Cliente
- Vendedor
- Status (aberta/finalizada/cancelada)
- Total

### ItemVenda
Itens vendidos com quantidade e preço.

### TradeIn
Aparelhos usados aceitos como parte do pagamento.

### Compra
Compras de fornecedores para repor estoque.

### Garantia
Certificados de garantia gerados automaticamente:
- IMEI (para celulares)
- Período de validade
- PDF exportável

## Fluxo de Uso

1. **Configuração Inicial**:
   - Acesse o Django Admin
   - Cadastre o Emitente (dados da empresa)
   - Cadastre Fornecedores
   - Cadastre Produtos
   - Cadastre Clientes

2. **Realizar Venda**:
   - Acesse "Nova Venda"
   - Selecione cliente e vendedor
   - Adicione produtos
   - (Opcional) Adicione trade-ins
   - Clique em "Continuar"

3. **Finalizar Venda**:
   - Informe IMEI dos celulares (obrigatório)
   - Revise os dados
   - Clique em "Finalizar Venda"
   - O sistema irá:
     - Baixar o estoque
     - Gerar garantias automaticamente
     - Calcular totais

4. **Gerenciar Estoque**:
   - Via Django Admin: Criar Compra
   - Adicionar Itens de Compra
   - O estoque é atualizado automaticamente

## Recursos de Segurança

- ✅ Login obrigatório para acessar o sistema
- ✅ CSRF protection habilitado
- ✅ Validação de IMEI (15 dígitos)
- ✅ Controle de estoque (vendas bloqueadas se sem estoque)
- ✅ Validação de dados em formulários

## Arquivos Estáticos

- Bootstrap 5.3.0 (CDN)
- Bootstrap Icons (CDN)
- Responsivo e moderno

## Próximas Melhorias

- [ ] Relatórios de vendas
- [ ] Notificações de estoque baixo
- [ ] Dashboard com gráficos
- [ ] Exportação de dados (Excel/CSV)
- [ ] API REST
- [ ] Sistema de backup automático

## Suporte

Para problemas com WeasyPrint no Windows, consulte:
https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation

## Licença

Projeto desenvolvido para fins de aprendizado e uso comercial.

---

**Desenvolvido com Django 4.2 LTS**

