from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('venda/nova/', views.nova_venda, name='nova_venda'),
    path('venda/<int:venda_id>/finalizar/', views.finalizar_venda, name='finalizar_venda'),
    path('garantia/<int:garantia_id>/pdf/', views.garantia_pdf, name='garantia_pdf'),
    path('venda/<int:venda_id>/', views.venda_visualizar, name='venda_visualizar'),
    path('venda/<int:venda_id>/comprovante/', views.comprovante_venda, name='comprovante_venda'),
    path('garantia/<int:garantia_id>/termo/', views.termo_garantia, name='termo_garantia'),
    
    # Cadastros
    path('cliente/cadastrar/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('cliente/listar/', views.listar_clientes, name='listar_clientes'),
    path('cliente/<int:cliente_id>/', views.detalhe_cliente, name='detalhe_cliente'),
    path('cliente/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('produto/cadastrar/', views.cadastrar_produto, name='cadastrar_produto'),
    path('produto/listar/', views.listar_produtos, name='listar_produtos'),
    path('produto/<int:produto_id>/editar/', views.editar_produto, name='editar_produto'),
    path('usuario/cadastrar/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('usuario/listar/', views.listar_usuarios, name='listar_usuarios'),
    path('usuario/<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('compra/nova/', views.nova_compra, name='nova_compra'),
    path('compra/listar/', views.listar_compras, name='listar_compras'),
    path('compra/<int:compra_id>/recibo/', views.recibo_compra, name='recibo_compra'),
    path('compra/<int:compra_id>/termo/', views.termo_compra, name='termo_compra'),
    path('venda/<int:venda_id>/termo-venda/', views.termo_venda, name='termo_venda'),
    path('emitente/configurar/', views.configurar_emitente, name='configurar_emitente'),
    # Busca por IMEI
    path('busca/imei/', views.busca_imei, name='busca_imei'),
    # Cancelar venda
    path('venda/<int:venda_id>/cancelar/', views.cancelar_venda, name='cancelar_venda'),
    
    # PDV
    path('pdv/', views.pdv, name='pdv'),
    path('pdv/limpar/', views.pdv_limpar, name='pdv_limpar'),
    path('pdv/finalizar/', views.pdv_finalizar, name='pdv_finalizar'),
    
    # Caixa
    path('caixa/abrir/', views.caixa_abrir, name='caixa_abrir'),
    path('caixa/conferir/<int:caixa_id>/', views.caixa_conferir, name='caixa_conferir'),
    path('caixa/fechar/<int:caixa_id>/', views.caixa_fechar, name='caixa_fechar'),
    path('caixa/historico/', views.caixa_historico, name='caixa_historico'),
    
    # Relatórios
    path('relatorio/produtos-comprados/', views.relatorio_produtos_comprados, name='relatorio_produtos_comprados'),
    path('relatorio/produtos-vendidos/', views.relatorio_produtos_vendidos, name='relatorio_produtos_vendidos'),
    path('relatorio/clientes/', views.relatorio_clientes, name='relatorio_clientes'),
    path('relatorio/vendas-periodo/', views.relatorio_vendas_periodo, name='relatorio_vendas_periodo'),
    path('relatorio/curva-abc/', views.relatorio_curva_abc, name='relatorio_curva_abc'),
    path('relatorio/inventario/', views.relatorio_inventario, name='relatorio_inventario'),
    
    # Backup e Restore
    path('backup/', views.backup_restore, name='backup_restore'),
    path('backup/criar/', views.backup_criar, name='backup_criar'),
    path('backup/restaurar/', views.backup_restaurar, name='backup_restaurar'),
    path('backup/download/<str:backup_name>/', views.backup_download, name='backup_download'),
    path('backup/deletar/<str:backup_name>/', views.backup_deletar, name='backup_deletar'),
    
    # Licença
    path('licenca/verificar/', views.verificar_licenca, name='verificar_licenca'),
    path('licenca/gerar-chave/', views.gerar_chave_licenca, name='gerar_chave_licenca'),

    # Ordens de Serviço
    path('os/', views.lista_os, name='lista_os'),
    path('os/nova/', views.nova_os, name='nova_os'),
    path('os/<int:os_id>/', views.detalhe_os, name='detalhe_os'),
    path('os/<int:os_id>/imprimir/', views.imprimir_os, name='imprimir_os'),
    path('os/<int:os_id>/termo-garantia-conserto/', views.termo_garantia_conserto, name='termo_garantia_conserto'),

    # Código de barras
    path('produto/<int:produto_id>/barcode/', views.barcode_produto, name='barcode_produto'),

    # Seriais / IMEI por produto
    path('produto/<int:produto_id>/seriais/', views.serial_listar, name='serial_listar'),
    path('serial/<int:serial_id>/deletar/', views.serial_deletar, name='serial_deletar'),

    # Relatório de lucro
    path('relatorio/lucro/', views.relatorio_lucro, name='relatorio_lucro'),

    # Exportação Excel
    path('export/excel/<str:tipo>/', views.exportar_excel, name='exportar_excel'),

    # WhatsApp
    path('whatsapp/enviar/', views.whatsapp_enviar, name='whatsapp_enviar'),
    path('whatsapp/status/', views.whatsapp_status, name='whatsapp_status'),
    path('whatsapp/painel/', views.whatsapp_painel, name='whatsapp_painel'),
    path('whatsapp/qr/', views.whatsapp_qr, name='whatsapp_qr'),
    path('whatsapp/conectar/', views.whatsapp_conectar, name='whatsapp_conectar'),
    path('whatsapp/desconectar/', views.whatsapp_desconectar, name='whatsapp_desconectar'),

    # Emitentes / Filiais
    path('emitente/<int:emitente_id>/ativar/', views.emitente_set_ativo, name='emitente_set_ativo'),
    path('emitente/<int:emitente_id>/deletar/', views.emitente_deletar, name='emitente_deletar'),

    # Fornecedores
    path('fornecedor/', views.listar_fornecedores, name='listar_fornecedores'),
    path('fornecedor/novo/', views.cadastrar_fornecedor, name='cadastrar_fornecedor'),
    path('fornecedor/<int:fornecedor_id>/', views.detalhe_fornecedor, name='detalhe_fornecedor'),
    path('fornecedor/<int:fornecedor_id>/editar/', views.editar_fornecedor, name='editar_fornecedor'),
    path('fornecedor/<int:fornecedor_id>/deletar/', views.deletar_fornecedor, name='deletar_fornecedor'),

    # Relatório de OS
    path('relatorio/os/', views.relatorio_os, name='relatorio_os'),

    # OS → Venda
    path('os/<int:os_id>/gerar-venda/', views.os_gerar_venda, name='os_gerar_venda'),

    # Devoluções
    path('devolucoes/', views.lista_devolucoes, name='lista_devolucoes'),
    path('venda/<int:venda_id>/devolucao/', views.nova_devolucao, name='nova_devolucao'),

    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('sair/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]

