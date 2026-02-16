const express = require("express");
const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");

const app = express();
app.use(express.json());

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "/data/session" }),
  puppeteer: {
    headless: true,
    protocolTimeout: 120000, // 120s timeout for low-RAM VM
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--disable-extensions",
      "--disable-background-timer-throttling",
      "--disable-renderer-backgrounding",
    ],
  },
});

// QR Code no terminal
client.on("qr", (qr) => {
  console.log("📱 Escaneie este QR code para autenticar:");
  qrcode.generate(qr, { small: true });
});

client.on("ready", () => {
  console.log("✅ Cliente WhatsApp pronto!");
});

client.on("authenticated", () => {
  console.log("🔑 Autenticado com sucesso!");
});

client.on("auth_failure", (msg) => {
  console.error("❌ Falha na autenticação:", msg);
});

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

// Enviar mensagem
app.post("/send", async (req, res) => {
  const { number, message } = req.body;

  if (!number || !message) {
    return res.status(400).json({ error: "number e message são obrigatórios" });
  }

  const cleanNumber = number.replace(/@[a-z.]+$/, "");

  try {
    // Use getNumberId to resolve the correct WhatsApp ID (workaround for LID issue)
    const numberId = await client.getNumberId(cleanNumber);
    
    if (!numberId) {
      console.error(`❌ Número ${cleanNumber} não encontrado no WhatsApp`);
      return res.status(404).json({ error: "Número não encontrado no WhatsApp" });
    }

    const chatId = numberId._serialized;
    console.log(`📤 Enviando para ${chatId}...`);
    await client.sendMessage(chatId, message);
    console.log(`✅ Mensagem enviada para ${chatId}`);
    res.json({ status: "Mensagem enviada com sucesso" });
  } catch (err) {
    console.error(`❌ Erro ao enviar para ${cleanNumber}:`, err.message || err);
    res.status(500).json({ error: "Erro ao enviar mensagem", details: err.message });
  }
});

const PORT = process.env.PORT || 4000;

app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 API rodando em http://localhost:${PORT}`);
});

client.initialize();
