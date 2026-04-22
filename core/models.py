from django.db import models
from django.core.validators import RegexValidator


class Emitente(models.Model):
    """Informações da empresa emitente"""
    nome = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True, help_text="Nome fantasia (opcional). Se preenchido, será exibido nos relatórios.")
    cnpj = models.CharField(max_length=18, unique=True)
    endereco = models.TextField()
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    prazo_garantia_celular = models.IntegerField(default=90, help_text="Prazo em dias")
    prazo_garantia_acessorio = models.IntegerField(default=30, help_text="Prazo em dias")
    texto_garantia = models.TextField(
        default="Garantia contra defeitos de fabricação.",
        help_text="Texto padrão da garantia"
    )
    ativo = models.BooleanField(default=False, help_text="Emitente padrão para documentos")
    
    class Meta:
        verbose_name = "Emitente"
        verbose_name_plural = "Emitentes"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

    @classmethod
    def get_ativo(cls):
        """Retorna o emitente ativo, ou o primeiro cadastrado"""
        return cls.objects.filter(ativo=True).first() or cls.objects.first()

    def set_ativo(self):
        """Define este emitente como ativo, desativa os demais"""
        Emitente.objects.update(ativo=False)
        self.ativo = True
        self.save(update_fields=['ativo'])


class Cliente(models.Model):
    """Clientes da loja"""
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    endereco = models.TextField()
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.cpf}"


class Fornecedor(models.Model):
    """Fornecedores de produtos"""
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    telefone2 = models.CharField(max_length=20, blank=True, verbose_name='Telefone 2')
    email = models.EmailField(blank=True)
    site = models.URLField(blank=True, verbose_name='Site / WhatsApp')
    contato = models.CharField(max_length=100, blank=True, verbose_name='Nome do Contato')
    endereco = models.TextField(blank=True)
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    TIPO_CHOICES = [
        ('celular', 'Celular'),
        ('acessorio', 'Acessório'),
    ]
    
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    descricao = models.TextField(blank=True)
    foto = models.ImageField(upload_to='produtos/', blank=True, null=True, help_text="Foto do produto")
    codigo_barras = models.CharField(max_length=20, blank=True, help_text="EAN-13 ou outro código de barras")
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Preço de compra")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField(default=0)
    estoque_minimo = models.IntegerField(default=5, help_text="Alerta quando estoque atingir este valor")
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    ativo = models.BooleanField(default=True)
    imei = models.CharField(
        max_length=15, blank=True,
        validators=[RegexValidator(regex=r'^\d{0,15}$', message='IMEI deve ter até 15 dígitos')],
        help_text='IMEI 1 (somente para celulares)'
    )
    imei2 = models.CharField(
        max_length=15, blank=True,
        validators=[RegexValidator(regex=r'^\d{0,15}$', message='IMEI 2 deve ter até 15 dígitos')],
        help_text='IMEI 2 (somente para celulares dual SIM)'
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"
    
    def tem_estoque(self, quantidade=1):
        return self.estoque >= quantidade
    
    def lucro(self):
        """Calcula o lucro do produto"""
        return self.preco_venda - self.preco_custo
    
    def margem_lucro(self):
        """Calcula a margem de lucro em percentual"""
        if self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_custo) * 100
        return 0


class Venda(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    data_venda = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    vendedor = models.CharField(max_length=200, default="Sistema")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Desconto em reais")
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Desconto em porcentagem")
    forma_pagamento = models.CharField(max_length=50, choices=[
        ('dinheiro', 'Dinheiro'),
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
        ('pix', 'PIX'),
        ('parcelado', 'Parcelado'),
    ], default='dinheiro')
    parcelas = models.IntegerField(default=1, help_text="Número de parcelas (para crédito/parcelado)")
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-data_venda']
    
    def __str__(self):
        return f"Venda #{self.id} - {self.cliente.nome} - {self.data_venda.strftime('%d/%m/%Y')}"
    
    def calcular_total(self):
        total = sum(item.subtotal for item in self.items.all())
        # Subtrair valor de trade-ins
        trade_in_total = sum(ti.valor_desconto for ti in self.tradeins.all())
        # Aplicar desconto
        total_com_trade = total - trade_in_total
        if self.desconto_percentual > 0:
            self.desconto = total_com_trade * self.desconto_percentual / 100
        self.total = total_com_trade - self.desconto
        self.save()


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='items')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    serial_produto = models.ForeignKey(
        'SerialProduto', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='itens_venda', verbose_name="Serial/IMEI da unidade"
    )
    
    class Meta:
        verbose_name = "Item de Venda"
        verbose_name_plural = "Itens de Venda"
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
    
    def save(self, *args, **kwargs):
        from decimal import Decimal
        # Garantir que ambos sejam Decimal para evitar erro de tipo
        preco = Decimal(str(self.preco_unitario))
        qtd = Decimal(str(self.quantidade))
        self.subtotal = preco * qtd
        super().save(*args, **kwargs)


class TradeIn(models.Model):
    """Trade-in usado em vendas"""
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='tradeins')
    descricao = models.CharField(max_length=200, help_text="Ex: iPhone 8 64GB")
    condicao = models.CharField(max_length=50, default="Usado")
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Trade-in"
        verbose_name_plural = "Trade-ins"
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor_desconto}"


class Compra(models.Model):
    """Compras de fornecedores"""
    data_compra = models.DateTimeField(auto_now_add=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True)
    forma_pagamento = models.CharField(max_length=50, choices=[
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência'),
        ('cheque', 'Cheque'),
        ('boleto', 'Boleto'),
    ], default='dinheiro', blank=True)
    
    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-data_compra']
    
    def __str__(self):
        return f"Compra #{self.id} - {self.fornecedor.nome}"


class ItemCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='items')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Item de Compra"
        verbose_name_plural = "Itens de Compra"
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
    
    def save(self, *args, **kwargs):
        from decimal import Decimal
        # Garantir que ambos sejam Decimal para evitar erro de tipo
        preco = Decimal(str(self.preco_unitario))
        qtd = Decimal(str(self.quantidade))
        self.subtotal = preco * qtd
        super().save(*args, **kwargs)
        # Atualiza estoque
        self.produto.estoque += self.quantidade
        self.produto.save()
        
        # Atualiza total da compra
        self.compra.total = sum(item.subtotal for item in self.compra.items.all())
        self.compra.save()


class Garantia(models.Model):
    """Garantias emitidas para vendas"""
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='garantias')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    item = models.ForeignKey(ItemVenda, on_delete=models.PROTECT)
    imei = models.CharField(
        max_length=15, 
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\d{15}$', message='IMEI deve ter 15 dígitos')]
    )
    imei2 = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\d{15}$', message='IMEI 2 deve ter 15 dígitos')]
    )
    data_inicio = models.DateField()
    data_fim = models.DateField()
    prazo_dias = models.IntegerField()
    texto = models.TextField()
    
    class Meta:
        verbose_name = "Garantia"
        verbose_name_plural = "Garantias"
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"Garantia #{self.id} - {self.produto.nome} ({self.data_fim})"


class Caixa(models.Model):
    """Registro de abertura e fechamento de caixa"""
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    valor_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Valor em caixa no início")
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Valor em caixa no fechamento")
    operador = models.CharField(max_length=200)
    observacoes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('aberto', 'Aberto'),
        ('fechado', 'Fechado'),
    ], default='aberto')
    
    # Contagem física
    notas_100 = models.IntegerField(default=0)
    notas_50 = models.IntegerField(default=0)
    notas_20 = models.IntegerField(default=0)
    notas_10 = models.IntegerField(default=0)
    notas_5 = models.IntegerField(default=0)
    notas_2 = models.IntegerField(default=0)
    moedas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Caixa"
        verbose_name_plural = "Caixas"
        ordering = ['-data_abertura']
    
    def __str__(self):
        return f"Caixa #{self.id} - {self.data_abertura.strftime('%d/%m/%Y %H:%M')}"
    
    def calcular_contagem_fisica(self):
        """Calcula o total da contagem física de cédulas e moedas"""
        total = (self.notas_100 * 100) + (self.notas_50 * 50) + (self.notas_20 * 20) + \
                (self.notas_10 * 10) + (self.notas_5 * 5) + (self.notas_2 * 2) + self.moedas
        return total
    
    def vendas_periodo(self):
        """Retorna vendas do período de caixa aberto"""
        from datetime import datetime
        if self.status == 'aberto':
            return Venda.objects.filter(
                data_venda__gte=self.data_abertura,
                status='finalizada'
            )
        elif self.data_fechamento:
            return Venda.objects.filter(
                data_venda__gte=self.data_abertura,
                data_venda__lte=self.data_fechamento,
                status='finalizada'
            )
        return Venda.objects.none()


class Licenca(models.Model):
    """Sistema de licença - controle de expiração"""
    chave = models.CharField(max_length=100, unique=True)
    data_ativacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    ativa = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Licença"
        verbose_name_plural = "Licenças"
        ordering = ['-data_ativacao']
    
    def __str__(self):
        return f"Licença válida até {self.data_expiracao.strftime('%d/%m/%Y')}"
    
    @classmethod
    def licenca_valida(cls):
        """Verifica se existe licença válida"""
        from django.utils import timezone
        try:
            licenca = cls.objects.filter(ativa=True).latest('data_ativacao')
            if licenca.data_expiracao >= timezone.now():
                return licenca
            return None
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def ativar_licenca(cls, chave):
        """Ativa nova licença por 3 meses"""
        from django.utils import timezone
        from datetime import timedelta
        import hashlib
        
        # Validar chave
        if not cls.validar_chave(chave):
            return False, "Chave inválida!"
        
        # Desativar licenças antigas
        cls.objects.filter(ativa=True).update(ativa=False)
        
        # Criar nova licença
        licenca = cls.objects.create(
            chave=chave,
            data_expiracao=timezone.now() + timedelta(days=90),
            ativa=True,
            observacoes=f"Licença ativada via chave: {chave}"
        )
        
        return True, licenca
    
    @classmethod
    def validar_chave(cls, chave):
        """Valida o formato da chave usando hash"""
        import hashlib
        import re
        
        # Formato esperado: XXXX-XXXX-XXXX-XXXX-XXXX
        pattern = re.compile(r'^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$')
        
        if not pattern.match(chave):
            return False
        
        # Validar checksum (últimos 4 caracteres são hash dos primeiros)
        parts = chave.split('-')
        main_key = '-'.join(parts[:4])
        
        # Hash simples para validação
        hash_value = hashlib.md5(main_key.encode()).hexdigest()[:4].upper()
        
        return hash_value == parts[4]


class OrdemServico(models.Model):
    """Ordem de Serviço para consertos e reparos"""

    STATUS_CHOICES = [
        ('aguardando', 'Aguardando'),
        ('em_andamento', 'Em Andamento'),
        ('orcamento_enviado', 'Orçamento Enviado'),
        ('aprovado', 'Aprovado'),
        ('concluido', 'Concluído'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    TIPO_SERVICO_CHOICES = [
        ('troca_tela', 'Troca de Tela'),
        ('troca_bateria', 'Troca de Bateria'),
        ('reparo_placa', 'Reparo de Placa'),
        ('conector_carga', 'Conector de Carga'),
        ('desbloqueio', 'Desbloqueio'),
        ('software', 'Problema de Software'),
        ('troca_camera', 'Troca de Câmera'),
        ('reparo_botoes', 'Reparo de Botões'),
        ('limpeza', 'Limpeza / Higienização'),
        ('outro', 'Outro'),
    ]

    # Dados da OS
    numero = models.CharField(max_length=20, unique=True, editable=False)
    data_entrada = models.DateTimeField(auto_now_add=True)
    data_previsao = models.DateField(null=True, blank=True, help_text="Previsão de entrega")
    data_conclusao = models.DateField(null=True, blank=True)
    data_entrega = models.DateField(null=True, blank=True)

    # Cliente e aparelho
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ordens_servico')
    aparelho = models.CharField(max_length=200, help_text="Ex: Samsung Galaxy A54")
    imei = models.CharField(
        max_length=15, blank=True,
        validators=[RegexValidator(regex=r'^\d{0,15}$', message='IMEI deve ter até 15 dígitos')]
    )
    imei2 = models.CharField(
        max_length=15, blank=True,
        validators=[RegexValidator(regex=r'^\d{0,15}$', message='IMEI 2 deve ter até 15 dígitos')]
    )
    acessorios = models.CharField(max_length=300, blank=True, help_text="Capinha, carregador, etc.")

    # Serviço
    tipo_servico = models.CharField(max_length=30, choices=TIPO_SERVICO_CHOICES, default='outro')
    descricao_problema = models.TextField(help_text="Descrição do defeito relatado pelo cliente")
    observacoes_tecnico = models.TextField(blank=True, help_text="Notas internas do técnico")

    # Financeiro
    valor_orcamento = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Valor do orçamento")
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Valor cobrado no fechamento")
    forma_pagamento = models.CharField(max_length=50, choices=[
        ('dinheiro', 'Dinheiro'),
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
        ('pix', 'PIX'),
        ('parcelado', 'Parcelado'),
    ], blank=True, default='')
    garantia_dias = models.IntegerField(default=90, help_text="Prazo de garantia do serviço em dias")

    # Status e responsável
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='aguardando')
    tecnico = models.CharField(max_length=200, blank=True, help_text="Nome do técnico responsável")

    class Meta:
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"
        ordering = ['-data_entrada']

    def __str__(self):
        return f"OS #{self.numero} — {self.cliente.nome} ({self.aparelho})"

    def save(self, *args, **kwargs):
        if not self.numero:
            from django.utils import timezone
            year = timezone.now().year
            # Número sequencial por ano: OS-2025-0001
            ultimo = OrdemServico.objects.filter(numero__startswith=f'OS-{year}-').order_by('numero').last()
            if ultimo:
                try:
                    seq = int(ultimo.numero.split('-')[-1]) + 1
                except ValueError:
                    seq = 1
            else:
                seq = 1
            self.numero = f'OS-{year}-{seq:04d}'
        super().save(*args, **kwargs)

    def get_status_badge(self):
        cores = {
            'aguardando': 'secondary',
            'em_andamento': 'primary',
            'orcamento_enviado': 'info',
            'aprovado': 'warning',
            'concluido': 'success',
            'entregue': 'dark',
            'cancelado': 'danger',
        }
        return cores.get(self.status, 'secondary')


class HistoricoStatusOS(models.Model):
    """Registra cada mudança de status de uma OS, com data/hora e usuário"""
    os = models.ForeignKey('OrdemServico', on_delete=models.CASCADE, related_name='historico_status')
    status_anterior = models.CharField(max_length=30, blank=True)
    status_novo = models.CharField(max_length=30)
    usuario = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='historico_os'
    )
    data_hora = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ['data_hora']
        verbose_name = "Histórico de Status OS"
        verbose_name_plural = "Histórico de Status OS"

    def get_status_display_anterior(self):
        mapa = dict(OrdemServico.STATUS_CHOICES)
        return mapa.get(self.status_anterior, self.status_anterior)

    def get_status_display_novo(self):
        mapa = dict(OrdemServico.STATUS_CHOICES)
        return mapa.get(self.status_novo, self.status_novo)

    def get_badge_novo(self):
        cores = {
            'aguardando': 'secondary', 'em_andamento': 'primary',
            'orcamento_enviado': 'info', 'aprovado': 'warning',
            'concluido': 'success', 'entregue': 'dark', 'cancelado': 'danger',
        }
        return cores.get(self.status_novo, 'secondary')


class SerialProduto(models.Model):
    """Controle individual de serial/IMEI por unidade em estoque"""

    STATUS_CHOICES = [
        ('em_estoque', 'Em Estoque'),
        ('vendido', 'Vendido'),
        ('em_reparo', 'Em Reparo / OS'),
        ('devolvido', 'Devolvido'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='seriais')
    serial = models.CharField(max_length=100, unique=True, help_text="Número de série")
    imei = models.CharField(
        max_length=15, blank=True,
        validators=[RegexValidator(regex=r'^\d{0,15}$', message='IMEI deve ter até 15 dígitos')],
        help_text="IMEI 1 (somente para celulares)"
    )
    imei2 = models.CharField(
        max_length=15, blank=True,
        validators=[RegexValidator(regex=r'^\d{0,15}$', message='IMEI 2 deve ter até 15 dígitos')],
        help_text="IMEI 2 (somente para celulares dual SIM)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='em_estoque')
    data_entrada = models.DateTimeField(auto_now_add=True)
    data_saida = models.DateTimeField(null=True, blank=True)
    observacoes = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Serial / IMEI"
        verbose_name_plural = "Seriais / IMEIs"
        ordering = ['-data_entrada']

    def __str__(self):
        return f"{self.produto.nome} | S/N: {self.serial}"


class Devolucao(models.Model):
    """Registro de devoluções / trocas de produtos vendidos"""

    MOTIVO_CHOICES = [
        ('defeito', 'Defeito / Falha'),
        ('arrependimento', 'Arrependimento'),
        ('produto_errado', 'Produto Errado'),
        ('danificado_entrega', 'Danificado na Entrega'),
        ('outro', 'Outro'),
    ]

    TIPO_CHOICES = [
        ('devolucao', 'Devolução (reembolso)'),
        ('troca', 'Troca por outro produto'),
        ('credito', 'Crédito em loja'),
    ]

    venda = models.ForeignKey(
        Venda, on_delete=models.PROTECT, related_name='devolucoes',
        help_text="Venda de origem"
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, related_name='devolucoes'
    )
    quantidade = models.IntegerField(default=1)
    motivo = models.CharField(max_length=30, choices=MOTIVO_CHOICES, default='defeito')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='devolucao')
    descricao = models.TextField(blank=True, help_text="Descrição detalhada do problema")
    valor_reembolso = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Valor devolvido ao cliente"
    )
    data_devolucao = models.DateTimeField(auto_now_add=True)
    registrado_por = models.CharField(max_length=200, default='Sistema')
    repor_estoque = models.BooleanField(
        default=True, help_text="Devolver o produto ao estoque?"
    )

    class Meta:
        verbose_name = "Devolução"
        verbose_name_plural = "Devoluções"
        ordering = ['-data_devolucao']

    def __str__(self):
        return f"Devolução #{self.id} — {self.produto.nome} (Venda #{self.venda_id})"

    def save(self, *args, **kwargs):
        repondo = self.repor_estoque and self._state.adding
        super().save(*args, **kwargs)
        if repondo:
            self.produto.estoque += self.quantidade
            self.produto.save(update_fields=['estoque'])
