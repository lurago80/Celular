from django.contrib import admin
from .models import (
    Emitente, Cliente, Fornecedor, Produto,
    Venda, ItemVenda, TradeIn, Compra, ItemCompra, Garantia, Caixa, Licenca,
    OrdemServico,
)


@admin.register(Emitente)
class EmitenteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'telefone']
    search_fields = ['nome', 'cnpj']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'telefone', 'email']
    search_fields = ['nome', 'cpf', 'email']
    list_filter = ['cpf']


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'telefone']
    search_fields = ['nome', 'cnpj']


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1
    fields = ['produto', 'quantidade', 'preco_unitario', 'subtotal']
    readonly_fields = ['subtotal']


class TradeInInline(admin.TabularInline):
    model = TradeIn
    extra = 0
    fields = ['descricao', 'condicao', 'valor_desconto']


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'data_venda', 'status', 'total']
    list_filter = ['status', 'data_venda']
    search_fields = ['cliente__nome', 'cliente__cpf']
    readonly_fields = ['data_venda', 'total']
    inlines = [ItemVendaInline, TradeInInline]
    date_hierarchy = 'data_venda'


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'marca', 'preco_custo', 'preco_venda', 'estoque', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'marca', 'modelo']
    list_editable = ['preco_custo', 'preco_venda', 'estoque', 'ativo']


class ItemCompraInline(admin.TabularInline):
    model = ItemCompra
    extra = 1
    fields = ['produto', 'quantidade', 'preco_unitario', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'fornecedor', 'data_compra', 'total', 'forma_pagamento', 'get_observacoes_short']
    list_filter = ['data_compra', 'forma_pagamento']
    search_fields = ['fornecedor__nome', 'observacoes']
    readonly_fields = ['data_compra', 'total']
    inlines = [ItemCompraInline]
    
    def get_observacoes_short(self, obj):
        if obj.observacoes:
            return obj.observacoes[:50] + '...' if len(obj.observacoes) > 50 else obj.observacoes
        return '-'
    get_observacoes_short.short_description = 'Observações'


@admin.register(Garantia)
class GarantiaAdmin(admin.ModelAdmin):
    list_display = ['id', 'produto', 'cliente', 'imei', 'data_inicio', 'data_fim']
    list_filter = ['data_inicio', 'data_fim']
    search_fields = ['imei', 'produto__nome', 'venda__cliente__nome']
    readonly_fields = ['venda', 'produto', 'item', 'data_inicio', 'data_fim', 'prazo_dias', 'texto']
    
    def cliente(self, obj):
        return obj.venda.cliente.nome
    cliente.short_description = 'Cliente'


@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ['id', 'operador', 'data_abertura', 'data_fechamento', 'status', 'valor_inicial', 'valor_final']
    list_filter = ['status', 'data_abertura']
    search_fields = ['operador']
    readonly_fields = ['data_abertura', 'data_fechamento', 'status']
    date_hierarchy = 'data_abertura'


@admin.register(Licenca)
class LicencaAdmin(admin.ModelAdmin):
    list_display = ['id', 'chave', 'data_ativacao', 'data_expiracao', 'ativa']
    list_filter = ['ativa', 'data_ativacao', 'data_expiracao']
    search_fields = ['chave']
    readonly_fields = ['data_ativacao']
    date_hierarchy = 'data_ativacao'


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'aparelho', 'tipo_servico', 'status', 'valor_orcamento', 'data_entrada']
    list_filter = ['status', 'tipo_servico', 'data_entrada']
    search_fields = ['numero', 'cliente__nome', 'aparelho', 'imei']
    readonly_fields = ['numero', 'data_entrada']
    date_hierarchy = 'data_entrada'
