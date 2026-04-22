# Sistema de Loja de Celulares --- MVP Simples (para Cursor)

## 0) Visão geral do projeto

-   **Nome do projeto:** loja
-   **App:** core
-   **Banco:** SQLite (simples, pode evoluir para PostgreSQL)
-   **PDF:** WeasyPrint
-   **UI:** Django Admin + tela de Vendas customizada
-   **Funcionalidades:** Emitente, Clientes, Fornecedores, Produtos,
    Vendas (com Trade-in), Compras, Garantias.

------------------------------------------------------------------------

## 1) Comandos iniciais

``` bash
python -m venv .venv && . .venv/bin/activate
pip install django==5.0 weasyprint==61.0 pillow==10.4
django-admin startproject loja .
python manage.py startapp core
mkdir -p templates/core static
python manage.py migrate
python manage.py createsuperuser --username admin --email admin@local
```

Arquivo `requirements.txt`:

``` txt
django==5.0
weasyprint==61.0
pillow==10.4
```

------------------------------------------------------------------------

## 2) Configuração --- loja/settings.py

*(Conteúdo completo incluído acima na conversa)*

------------------------------------------------------------------------

## 3) URLs --- loja/urls.py

*(Conteúdo completo incluído acima na conversa)*

------------------------------------------------------------------------

## 4) Modelos --- core/models.py

*(Todos os modelos: Emitente, Cliente, Fornecedor, Produto, Venda,
ItemVenda, TradeIn, Compra, ItemCompra, Garantia)*

------------------------------------------------------------------------

## 5) Admin --- core/admin.py

*(CRUD pronto via Django Admin)*

------------------------------------------------------------------------

## 6) Formulários --- core/forms.py

*(Formulários para Venda, ItemVenda e TradeIn)*

------------------------------------------------------------------------

## 7) Views --- core/views.py

*(Dashboard, Nova Venda, Finalizar Venda, Garantia PDF)*

------------------------------------------------------------------------

## 8) Templates principais

-   base.html
-   dashboard.html
-   venda_nova.html
-   venda_finalizar.html
-   garantia_template.html

------------------------------------------------------------------------

## 9) Dados iniciais

Cadastrar: 1. Emitente com prazos de garantia e texto padrão. 2.
Produtos (celular e acessórios).

------------------------------------------------------------------------

## 10) Fluxo de uso

1.  Login → Admin.
2.  Cadastros: Emitente, Clientes, Produtos.
3.  Nova venda → adicionar itens → Trade-in → Concluir.
4.  PDF disponível em `/garantia/<id>/pdf/`.

------------------------------------------------------------------------

## 11) Compras

Feitas pelo Admin --- aumentam o estoque.

------------------------------------------------------------------------

## 12) Testes manuais

-   IMEI obrigatório em celulares.
-   Estoque insuficiente bloqueia venda.
-   Venda concluída baixa estoque e gera garantias.

------------------------------------------------------------------------

## 13) Deploy rápido

-   Railway ou Render com Gunicorn.
-   Em produção, configurar MEDIA_ROOT para PDFs.
