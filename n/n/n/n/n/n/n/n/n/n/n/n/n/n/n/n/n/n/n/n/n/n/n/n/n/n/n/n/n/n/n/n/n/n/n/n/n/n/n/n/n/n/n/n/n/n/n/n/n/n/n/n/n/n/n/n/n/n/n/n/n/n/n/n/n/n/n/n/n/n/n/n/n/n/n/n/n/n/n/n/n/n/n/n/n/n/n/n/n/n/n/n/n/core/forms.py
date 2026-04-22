from django import forms
from django.core.validators import RegexValidator
from .models import Venda, ItemVenda, TradeIn, Produto, Cliente, Garantia, Fornecedor, Emitente, SerialProduto, Devolucao


BS = {'class': 'form-control'}  # atalho Bootstrap


def _bs(extra=None):
    attrs = {'class': 'form-control'}
    if extra:
        attrs.update(extra)
    return attrs


class ClienteForm(forms.ModelForm):
    """Form com validação de CPF e unicidade"""
    cpf = forms.CharField(
        max_length=14,
        required=False,
        validators=[RegexValidator(
            regex=r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$',
            message='Informe um CPF válido (ex: 000.000.000-00)'
        )],
        widget=forms.TextInput(attrs=_bs({'placeholder': '000.000.000-00'}))
    )

    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'telefone', 'email', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs=_bs({'placeholder': 'Nome completo'})),
            'telefone': forms.TextInput(attrs=_bs({'placeholder': '(11) 99999-9999'})),
            'email': forms.EmailInput(attrs=_bs({'placeholder': 'email@exemplo.com'})),
            'endereco': forms.Textarea(attrs=_bs({'rows': 3, 'placeholder': 'Rua, número, bairro, cidade – UF'})),
        }
        labels = {
            'nome': 'Nome Completo *',
            'cpf': 'CPF',
            'telefone': 'Telefone *',
            'email': 'E-mail',
            'endereco': 'Endereço Completo *',
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '').strip()
        if not cpf:
            return None
        # Normalizar para apenas dígitos para comparação
        cpf_digits = ''.join(filter(str.isdigit, cpf))
        if len(cpf_digits) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        qs = Cliente.objects.filter(cpf__in=[cpf, cpf_digits])
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('CPF já cadastrado no sistema.')
        return cpf


class ProdutoForm(forms.ModelForm):
    """Form com validação de preços e estoque"""

    class Meta:
        model = Produto
        fields = [
            'nome', 'tipo', 'marca', 'modelo', 'descricao', 'foto', 'codigo_barras',
            'preco_custo', 'preco_venda', 'estoque', 'estoque_minimo',
            'fornecedor', 'ativo',
        ]
        widgets = {
            'nome': forms.TextInput(attrs=_bs()),
            'tipo': forms.Select(attrs=_bs()),
            'marca': forms.TextInput(attrs=_bs()),
            'modelo': forms.TextInput(attrs=_bs()),
            'descricao': forms.Textarea(attrs=_bs({'rows': 3})),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'codigo_barras': forms.TextInput(attrs=_bs({'placeholder': 'EAN-13 (13 dígitos)', 'maxlength': '20'})),
            'preco_custo': forms.NumberInput(attrs=_bs({'step': '0.01', 'min': '0'})),
            'preco_venda': forms.NumberInput(attrs=_bs({'step': '0.01', 'min': '0'})),
            'estoque': forms.NumberInput(attrs=_bs({'min': '0'})),
            'estoque_minimo': forms.NumberInput(attrs=_bs({'min': '0'})),
            'fornecedor': forms.Select(attrs=_bs()),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome': 'Nome do Produto *',
            'tipo': 'Tipo *',
            'foto': 'Foto do Produto',
            'codigo_barras': 'Código de Barras (EAN-13)',
            'preco_custo': 'Preço de Custo (R$) *',
            'preco_venda': 'Preço de Venda (R$) *',
            'estoque': 'Estoque Inicial',
            'estoque_minimo': 'Estoque Mínimo (alerta)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fornecedor'].queryset = Fornecedor.objects.order_by('nome')
        self.fields['fornecedor'].empty_label = 'Nenhum'
        self.fields['fornecedor'].required = False

    def clean(self):
        cleaned = super().clean()
        custo = cleaned.get('preco_custo')
        venda = cleaned.get('preco_venda')
        if custo and venda and venda < custo:
            self.add_error('preco_venda', 'Preço de venda não pode ser menor que o custo.')
        return cleaned


class VendaForm(forms.ModelForm):
    """Formulário para criar/editar vendas"""
    
    class Meta:
        model = Venda
        fields = ['cliente', 'vendedor']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'vendedor': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }


class ItemVendaForm(forms.ModelForm):
    """Formulário para itens de venda"""
    
    class Meta:
        model = ItemVenda
        fields = ['produto', 'quantidade', 'preco_unitario']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control produto-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 1}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas produtos ativos e com estoque
        self.fields['produto'].queryset = Produto.objects.filter(ativo=True).order_by('nome')


class TradeInForm(forms.ModelForm):
    """Formulário para trade-ins"""
    
    class Meta:
        model = TradeIn
        fields = ['descricao', 'condicao', 'valor_desconto']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: iPhone 8 64GB'}),
            'condicao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usado, novo, etc.'}),
            'valor_desconto': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'placeholder': '0.00'}
            ),
        }


ItemVendaFormSet = forms.inlineformset_factory(
    Venda, 
    ItemVenda, 
    form=ItemVendaForm,
    extra=0,
    can_delete=True,
    min_num=0,
    validate_min=False
)

TradeInFormSet = forms.inlineformset_factory(
    Venda, 
    TradeIn, 
    form=TradeInForm,
    extra=0,
    can_delete=True,
    min_num=0
)


class EmitenteForm(forms.ModelForm):
    """Form para cadastro/edição de emitentes/filiais"""

    class Meta:
        model = Emitente
        fields = [
            'nome', 'cnpj', 'endereco', 'telefone', 'email',
            'prazo_garantia_celular', 'prazo_garantia_acessorio', 'texto_garantia',
        ]
        widgets = {
            'nome': forms.TextInput(attrs=_bs()),
            'cnpj': forms.TextInput(attrs=_bs({'placeholder': '00.000.000/0001-00'})),
            'endereco': forms.Textarea(attrs=_bs({'rows': 3})),
            'telefone': forms.TextInput(attrs=_bs({'placeholder': '(11) 3000-0000'})),
            'email': forms.EmailInput(attrs=_bs()),
            'prazo_garantia_celular': forms.NumberInput(attrs=_bs({'min': 0})),
            'prazo_garantia_acessorio': forms.NumberInput(attrs=_bs({'min': 0})),
            'texto_garantia': forms.Textarea(attrs=_bs({'rows': 4})),
        }
        labels = {
            'nome': 'Razão Social / Nome *',
            'cnpj': 'CNPJ *',
            'prazo_garantia_celular': 'Prazo Garantia Celular (dias)',
            'prazo_garantia_acessorio': 'Prazo Garantia Acessório (dias)',
            'texto_garantia': 'Texto Padrão de Garantia',
        }


class SerialForm(forms.ModelForm):
    """Cadastro de serial/IMEI de produto em estoque"""

    class Meta:
        model = SerialProduto
        fields = ['serial', 'imei', 'status', 'observacoes']
        widgets = {
            'serial': forms.TextInput(attrs=_bs({'placeholder': 'Número de série'})),
            'imei': forms.TextInput(attrs=_bs({'placeholder': '15 dígitos (somente celulares)', 'maxlength': '15'})),
            'status': forms.Select(attrs=_bs()),
            'observacoes': forms.TextInput(attrs=_bs({'placeholder': 'Observações opcionais'})),
        }
        labels = {
            'serial': 'Número de Série *',
            'imei': 'IMEI (opcional)',
            'status': 'Status',
        }


class FornecedorForm(forms.ModelForm):
    """Form para cadastro e edição de fornecedores"""

    class Meta:
        model = Fornecedor
        fields = ['nome', 'cnpj', 'contato', 'telefone', 'telefone2', 'email', 'site', 'endereco', 'observacoes', 'ativo']
        widgets = {
            'nome':       forms.TextInput(attrs=_bs({'placeholder': 'Razão social ou nome fantasia'})),
            'cnpj':       forms.TextInput(attrs=_bs({'placeholder': '00.000.000/0001-00'})),
            'contato':    forms.TextInput(attrs=_bs({'placeholder': 'Nome do responsável / vendedor'})),
            'telefone':   forms.TextInput(attrs=_bs({'placeholder': '(11) 99999-9999'})),
            'telefone2':  forms.TextInput(attrs=_bs({'placeholder': '(11) 99999-9999 (opcional)'})),
            'email':      forms.EmailInput(attrs=_bs({'placeholder': 'email@fornecedor.com'})),
            'site':       forms.TextInput(attrs=_bs({'placeholder': 'https://site.com ou WhatsApp'})),
            'endereco':   forms.Textarea(attrs=_bs({'rows': 3, 'placeholder': 'Rua, número, bairro, cidade – UF'})),
            'observacoes':forms.Textarea(attrs=_bs({'rows': 3, 'placeholder': 'Condições comerciais, prazo de entrega, etc.'})),
            'ativo':      forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome':       'Nome / Razão Social *',
            'cnpj':       'CNPJ',
            'contato':    'Contato (responsável)',
            'telefone':   'Telefone principal',
            'telefone2':  'Telefone 2',
            'email':      'E-mail',
            'site':       'Site / Link WhatsApp',
            'endereco':   'Endereço',
            'observacoes':'Observações',
            'ativo':      'Fornecedor ativo',
        }


class DevolucaoForm(forms.ModelForm):
    """Form para registrar devolução / troca de produto"""

    class Meta:
        model = Devolucao
        fields = ['produto', 'quantidade', 'motivo', 'tipo', 'descricao', 'valor_reembolso', 'repor_estoque']
        widgets = {
            'produto': forms.Select(attrs=_bs()),
            'quantidade': forms.NumberInput(attrs=_bs({'min': 1})),
            'motivo': forms.Select(attrs=_bs()),
            'tipo': forms.Select(attrs=_bs()),
            'descricao': forms.Textarea(attrs=_bs({'rows': 3, 'placeholder': 'Descreva o problema ou motivo'})),
            'valor_reembolso': forms.NumberInput(attrs=_bs({'step': '0.01', 'min': '0'})),
            'repor_estoque': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'produto': 'Produto *',
            'quantidade': 'Quantidade *',
            'motivo': 'Motivo *',
            'tipo': 'Tipo *',
            'descricao': 'Descrição',
            'valor_reembolso': 'Valor Reembolso (R$)',
            'repor_estoque': 'Repor produto ao estoque',
        }
