# WhatsApp Service (Baileys)

Microserviço Node.js que conecta ao WhatsApp via Baileys e expõe uma API REST
consumida pelo sistema Django.

## Requisitos

- Node.js >= 18
- npm ou yarn

## Instalação

```bash
cd whatsapp_service
npm install
```

## Uso

```bash
npm start
```

Na primeira execução, um **QR Code** aparecerá no terminal.  
Abra o WhatsApp no celular → **Dispositivos Vinculados → Vincular Dispositivo** e escaneie.

A sessão é salva em `auth_state/`. Nas próximas execuções a reconexão é automática.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/status` | Status da conexão (`connected`, `phone`) |
| GET | `/qr` | QR Code atual (string base64) |
| POST | `/connect` | Inicia/reinicia conexão |
| POST | `/send` | Envia mensagem `{ phone, message }` |
| DELETE | `/disconnect` | Encerra sessão |

## Configuração no Django

No `settings.py`:
```python
WHATSAPP_SERVICE_URL = 'http://localhost:3000'
```

## Notas de Segurança

- Adicione autenticação (API Key) antes de expor em produção
- Nunca exponha este serviço publicamente sem firewall
- O `auth_state/` contém credenciais — não faça commit dele
