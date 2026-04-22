# Sistema de Licença - Loja de Celulares

## 📋 Visão Geral

Sistema de controle de uso por licença com expiração a cada 3 meses. Requer ativação via chave válida para uso contínuo.

## 🔐 Como Funciona

### 1. Expiração Automática
- Licença válida por 90 dias (3 meses)
- Após expirar, sistema bloqueia automaticamente
- Usuário é redirecionado para tela de ativação

### 2. Ativação de Licença
- Tela de "Licença Expirada" exibida automaticamente
- Campo para inserir chave de ativação
- Validação automática da chave
- Ativação por 90 dias após validação bem-sucedida

### 3. Geração de Chaves
- Aplicação externa: `gerar_chave_licenca.py`
- Gera chaves seguras com checksum
- Formato: XXXX-XXXX-XXXX-XXXX-XXXX

## 🚀 Como Usar

### Gerar Nova Chave

Execute o script gerador:

```bash
python gerar_chave_licenca.py
```

Isso irá:
1. Gerar uma chave única
2. Salvar em arquivo `.txt`
3. Exibir a chave no console
4. Tentar copiar para área de transferência

### Ativar Licença no Sistema

1. Quando o sistema expirar, a tela de ativação aparece automaticamente
2. Digite a chave no campo fornecido
3. Clique em "Ativar Licença"
4. Sistema revalidado por mais 3 meses

## 🛠️ Estrutura Técnica

### Modelo `Licenca`

```python
class Licenca(models.Model):
    chave = models.CharField(max_length=100, unique=True)
    data_ativacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    ativa = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True)
```

### Métodos Principais

- `Licenca.licenca_valida()`: Verifica se existe licença válida
- `Licenca.ativar_licenca(chave)`: Ativa nova licença
- `Licenca.validar_chave(chave)`: Valida formato e checksum da chave

### Decorator de Verificação

```python
@verificar_licenca_view
def minha_view(request):
    # View protegida por licença
    pass
```

## 🔒 Segurança

### Validação de Chave

1. **Formato**: 5 blocos de 4 caracteres (A-Z, 0-9)
   - Exemplo: `A3B2-C9D1-E4F5-G6H7-IJKL`

2. **Checksum**: Último bloco é hash dos primeiros 4 blocos
   - Impede chaves aleatórias
   - Garante autenticidade

3. **Hash MD5**: Primeiros 4 caracteres do hash MD5
   - Valida integridade da chave
   - Dificulta falsificação

### Formato da Chave

```
XXXX-XXXX-XXXX-XXXX-XXXX
│        │
└────────┴── Blocos principais
         └── Checksum (últimos 4 caracteres)
```

## 📁 Arquivos do Sistema

```
.
├── gerar_chave_licenca.py    # Gerador standalone de chaves
├── core/models.py             # Modelo Licenca
├── core/views.py              # Views de ativação
├── core/urls.py               # Rotas de licença
├── core/admin.py              # Admin para gerenciar licenças
└── templates/core/
    ├── licenca_expirada.html # Tela de ativação
    └── gerar_chave_licenca.html # Interface web de geração
```

## 🎯 URLs Disponíveis

- `/licenca/verificar/` - Tela de ativação (exibida automaticamente)
- `/licenca/gerar-chave/` - Gerar chave via web (requer admin)

## 📊 Admin Django

Acesse o Django Admin para:
- Ver histórico de licenças
- Verificar datas de expiração
- Ativar/desativar licenças manualmente

## ⚠️ Importante

1. **Backup**: Faça backup antes de renovar licenças
2. **Superusuário**: Apenas admins podem gerar chaves
3. **Validade**: 90 dias a partir da ativação
4. **Única**: Apenas uma licença ativa por vez

## 🔄 Fluxo de Renovação

```
Licença expira → Sistema bloqueia → Tela de ativação
                                              ↓
                    Gerador cria chave → Envia para cliente
                                              ↓
                    Cliente insere chave → Licença revalidada
                                              ↓
                    Sistema liberado por mais 90 dias
```

## 📞 Suporte

Para gerar chaves adicionais:
- Execute: `python gerar_chave_licenca.py`
- Ou acesse: `/admin/core/licenca/` (como admin)
- Ou acesse: `/licenca/gerar-chave/` (como superusuário)

## 📝 Exemplo de Uso

### 1. Gerar Chave

```bash
$ python gerar_chave_licenca.py

========================================================
GERADOR DE CHAVES DE LICENÇA
Sistema de Gestão - Loja de Celulares
========================================================

✓ Chave gerada com sucesso!

CHAVE DE LICENÇA:
========================================================
         A3B2-C9D1-E4F5-G6H7-IJKL
========================================================

Data de geração: 27/10/2025 15:30:45
Validade: 90 dias (3 meses)
```

### 2. Ativar no Sistema

1. Sistema expirado exibe tela de ativação
2. Insira chave: `A3B2-C9D1-E4F5-G6H7-IJKL`
3. Clique em "Ativar Licença"
4. Sistema revalidado por 90 dias

---

**Desenvolvido para garantir controle de uso e segurança do sistema.** 🔒

