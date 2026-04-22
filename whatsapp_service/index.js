/**
 * WhatsApp Service via Baileys
 * ────────────────────────────
 * Microserviço Express que mantém uma sessão WhatsApp ativa
 * e expõe endpoints REST para o sistema Django.
 *
 * Endpoints:
 *   GET  /status         → { connected: bool, phone?: string }
 *   POST /send           → { phone: "5511999...", message: "..." }
 *   POST /connect        → Reinicia a conexão / gera novo QR
 *   GET  /qr             → Retorna imagem base64 do QR atual
 *   DELETE /disconnect   → Desconecta a sessão
 */

import express from 'express'
import {
  makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  jidDecode,
} from '@whiskeysockets/baileys'
import pino from 'pino'
import qrcode from 'qrcode-terminal'
import { Boom } from '@hapi/boom'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const AUTH_DIR = path.join(__dirname, 'auth_state')
const PORT = process.env.PORT || 3000

const logger = pino({ level: 'silent' })
const app = express()
app.use(express.json())

// ── Estado global da conexão ──────────────────────────────────
let sock = null
let isConnected = false
let connectedPhone = null
let currentQR = null
let reconnectAttempts = 0
const MAX_RECONNECT = 5

// ── Inicializa / reconecta ─────────────────────────────────────
async function startConnection() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR)
  const { version } = await fetchLatestBaileysVersion()

  sock = makeWASocket({
    version,
    logger,
    auth: state,
    printQRInTerminal: false,         // gerenciamos o QR manualmente
    browser: ['Sistema Loja', 'Chrome', '1.0.0'],
    syncFullHistory: false,
  })

  // ── Eventos ──────────────────────────────────────────────────
  sock.ev.on('creds.update', saveCreds)

  sock.ev.on('connection.update', (update) => {
    const { connection, lastDisconnect, qr } = update

    if (qr) {
      currentQR = qr
      console.log('\n📱 Escaneie o QR Code abaixo com o WhatsApp:')
      qrcode.generate(qr, { small: true })
      console.log(`\nOu acesse http://localhost:${PORT}/qr para obter o QR em base64\n`)
    }

    if (connection === 'open') {
      isConnected = true
      currentQR = null
      reconnectAttempts = 0
      connectedPhone = sock.user?.id?.split(':')[0] ?? null
      console.log(`✅ WhatsApp conectado! Telefone: ${connectedPhone}`)
    }

    if (connection === 'close') {
      isConnected = false
      connectedPhone = null
      const statusCode = new Boom(lastDisconnect?.error)?.output?.statusCode
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut

      console.log(`❌ Conexão encerrada (código ${statusCode}). Reconectar: ${shouldReconnect}`)

      if (shouldReconnect && reconnectAttempts < MAX_RECONNECT) {
        reconnectAttempts++
        const delay = reconnectAttempts * 3000
        console.log(`🔄 Tentativa ${reconnectAttempts}/${MAX_RECONNECT} em ${delay / 1000}s...`)
        setTimeout(startConnection, delay)
      } else if (statusCode === DisconnectReason.loggedOut) {
        console.log('🚪 Sessão encerrada. Removendo dados de autenticação...')
        fs.rmSync(AUTH_DIR, { recursive: true, force: true })
      }
    }
  })

  // Log de mensagens recebidas (opcional)
  sock.ev.on('messages.upsert', ({ messages }) => {
    for (const msg of messages) {
      if (!msg.key.fromMe) {
        const from = jidDecode(msg.key.remoteJid)?.user ?? msg.key.remoteJid
        const text = msg.message?.conversation
          || msg.message?.extendedTextMessage?.text
          || '[mídia]'
        console.log(`📨 [${from}]: ${text}`)
      }
    }
  })
}

// ── Helpers ───────────────────────────────────────────────────
function normalizePhone(phone) {
  // Remove tudo que não é dígito
  let num = phone.replace(/\D/g, '')
  // Adiciona DDI Brasil se ausente
  if (!num.startsWith('55')) num = '55' + num
  return num + '@s.whatsapp.net'
}

// ── Endpoints REST ────────────────────────────────────────────

// GET /status
app.get('/status', (req, res) => {
  res.json({
    connected: isConnected,
    phone: connectedPhone,
    qr_available: !!currentQR,
  })
})

// GET /qr  — retorna QR atual como texto (para scanear via curl ou browser)
app.get('/qr', (req, res) => {
  if (!currentQR) {
    return res.status(404).json({ error: 'Nenhum QR disponível. Já conectado ou aguarde.' })
  }
  // Retorna o QR como string; o cliente pode gerar imagem com a lib qrcode
  res.json({ qr: currentQR })
})

// POST /connect  — (re)inicia conexão
app.post('/connect', async (req, res) => {
  if (isConnected) {
    return res.json({ success: true, message: 'Já conectado.', phone: connectedPhone })
  }
  try {
    await startConnection()
    res.json({ success: true, message: 'Iniciando conexão. Verifique /qr ou o terminal.' })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// POST /send  — envia mensagem
app.post('/send', async (req, res) => {
  const { phone, message } = req.body

  if (!phone || !message) {
    return res.status(400).json({ success: false, error: 'Campos "phone" e "message" são obrigatórios.' })
  }

  if (!isConnected || !sock) {
    return res.status(503).json({ success: false, error: 'WhatsApp não conectado. Escaneie o QR Code primeiro.' })
  }

  try {
    const jid = normalizePhone(phone)
    await sock.sendMessage(jid, { text: message })
    console.log(`✉️  Mensagem enviada para ${phone}`)
    res.json({ success: true, phone, message })
  } catch (err) {
    console.error('Erro ao enviar mensagem:', err)
    res.status(500).json({ success: false, error: err.message })
  }
})

// DELETE /disconnect  — encerra sessão
app.delete('/disconnect', async (req, res) => {
  if (sock) {
    await sock.logout().catch(() => {})
    sock = null
  }
  isConnected = false
  connectedPhone = null
  res.json({ success: true, message: 'Desconectado.' })
})

// ── Inicialização ─────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`\n🚀 WhatsApp Service rodando em http://localhost:${PORT}`)
  console.log('   Aguardando conexão...\n')
})

// Tenta conectar ao iniciar
startConnection().catch(err => {
  console.error('Erro ao iniciar conexão:', err)
})
