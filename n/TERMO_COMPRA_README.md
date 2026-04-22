# Termo de Compra de Produtos Usados

## 📋 Visão Geral

Sistema de geração automática de termo de compra e venda para aquisição de produtos usados de clientes/fornecedores.

## 🎯 Funcionalidades

### 1. Geração Automática
- Termo completo e formal de compra e venda
- Dados completos do fornecedor e empresa
- Lista detalhada de produtos comprados
- Informações de pagamento
- Cláusulas legais completas

### 2. Acesso ao Termo
- **Recibo de Compra**: Botão "Gerar Termo" após finalizar compra
- **Listagem de Compras**: Botão do termo para cada compra registrada

### 3. Conteúdo do Termo

#### Cláusulas Incluídas:
1. **Das Partes**: Dados completos do vendedor (fornecedor) e comprador (empresa)
2. **Do Objeto**: Tabela completa de produtos comprados com valores
3. **Valor e Forma de Pagamento**: Total e método de pagamento
4. **Transmissão de Propriedade**: Transferência de propriedade dos produtos
5. **Observações Especiais** (se houver)
6. **Disposições Gerais**: 
   - Venda "como está"
   - Responsabilidade por origem dos produtos
   - Sem direito de devolução
   - Foro de jurisdição

## 📄 Estrutura do Termo

### Cabeçalho
- Nome da empresa
- Endereço
- CNPJ
- Telefone

### Título
- "TERMO DE COMPRA E VENDA DE PRODUTOS USADOS"
- Número do documento

### Parte I - Dados das Partes
**VENDEDOR (Fornecedor):**
- Nome completo
- Telefone
- Endereço
- CPF/CNPJ

**COMPRADOR (Empresa):**
- Razão social
- CNPJ
- Endereço

### Parte II - Produtos
Tabela completa com:
- Nome do produto
- Quantidade
- Valor unitário
- Valor total por item
- **TOTAL GERAL**

### Parte III - Pagamento
- Valor total da compra
- Forma de pagamento (Dinheiro, PIX, Transferência, Cheque, Boleto)
- Momento do pagamento

### Parte IV - Transmissão
- Momento da transferência de propriedade
- Responsabilidade do vendedor

### Parte V/VI - Disposições Gerais
- Produtos vendidos "como estão"
- Responsabilidade criminal e civil
- Sem direito de arrependimento
- Foro de disputas
- Vias do documento

### Assinaturas
- Espaço para assinatura do vendedor (fornecedor)
- Espaço para assinatura do comprador (empresa)
- Carimbo e data

## 🖨️ Como Usar

### 1. Registrar Compra
1. Acesse "Cadastros" > "Nova Compra"
2. Selecione o fornecedor
3. Adicione os produtos comprados
4. Preencha forma de pagamento
5. Adicione observações (opcional)
6. Clique em "Registrar Compra"

### 2. Gerar Termo
**Opção A - Após Registrar:**
- Automaticamente redireciona para o recibo
- Clique no botão **"Gerar Termo"**

**Opção B - Na Listagem:**
- Acesse "Cadastros" > "Ver Compras"
- Clique no botão do termo (📄) na linha da compra desejada

### 3. Imprimir
1. O termo abre em nova aba
2. Clique em "Imprimir" ou pressione Ctrl+P
3. Imprima em 2 vias
4. Ambas as partes assinam

## 🔒 Proteções Legais

### Para a Empresa (Compradora):
- ✅ Documento comprobatório da origem dos produtos
- ✅ Proteção contra disputas de propriedade
- ✅ Registro completo da transação
- ✅ Comprovação de pagamento

### Cláusulas Importantes:
- **Venda "Como Está"**: Sem garantia de funcionamento
- **Sem Devolução**: Nenhuma das partes pode se arrepender
- **Responsabilidade**: Vendedor é responsável pela origem
- **Foro**: Disputas no foro da empresa
- **Vias**: Documento em 2 cópias (1 para cada parte)

## 📊 Integração com o Sistema

### Dados Populados Automaticamente:
- ✅ Dados da empresa (Emitente)
- ✅ Dados do fornecedor
- ✅ Lista de produtos comprados
- ✅ Quantidades e valores
- ✅ Total da compra
- ✅ Forma de pagamento
- ✅ Data e hora da compra
- ✅ Observações (se houver)

### Banco de Dados:
- Termo é gerado dinamicamente a partir da compra
- Não é salvo como arquivo (gerado sob demanda)
- Pode ser impresso quantas vezes necessário
- Histórico fica na compra registrada

## 📁 Arquivos do Sistema

```
templates/core/
├── termo_compra.html      # Template do termo
├── recibo_compra.html     # Recibo (com botão para termo)
└── lista_compras.html     # Listagem (com botão para termo)

core/
├── views.py               # View termo_compra()
└── urls.py                # Rota termo_compra
```

## 🎨 Layout

- **Formato**: A4 (210 x 297 mm)
- **Font**: Times New Roman
- **Margens**: 1.5cm
- **Espaçamento**: Adequado para assinatura
- **Impressão**: Otimizada para impressão em papel

## ⚙️ Configuração Necessária

### Dados do Emitente (Empresa)
Acesse: "Cadastros" > "Emitente" e preencha:
- Nome da empresa
- CNPJ
- Endereço completo
- Telefone

### Dados do Fornecedor
Ao cadastrar fornecedor, inclua:
- Nome completo
- CPF/CNPJ
- Telefone
- Endereço (opcional)

## 📝 Exemplo de Uso

### Cenário: Compra de Celular Usado

1. **Cliente chega com iPhone 11 usado**
2. **Registrar Compra:**
   - Fornecedor: João Silva
   - Produto: iPhone 11 64GB
   - Quantidade: 1
   - Preço: R$ 1.200,00
   - Forma de pagamento: Dinheiro
   - Observação: "Tela com pequeno risco, bateria original"

3. **Finalizar Compra**
   - Sistema salva e atualiza estoque
   - Redireciona para recibo

4. **Gerar Termo:**
   - Clicar em "Gerar Termo"
   - Termo completo é gerado
   - Imprimir em 2 vias

5. **Assinaturas:**
   - João Silva (vendedor) assina
   - Representante da empresa assina
   - Cada parte fica com 1 via
   - Arquivo na compra registrada

## ✅ Vantagens

- 📄 Documento legal completo
- 🔒 Proteção para empresa e cliente
- 📊 Integrado com sistema
- 🖨️ Impressão profissional
- 📋 Registro histórico
- ⚡ Geração automática instantânea

---

**Sistema desenvolvido para garantir segurança jurídica nas compras de produtos usados.** 📚

