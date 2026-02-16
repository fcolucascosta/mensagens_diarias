const express = require("express");
const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");

const app = express();
app.use(express.json());

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "/data/session" }),
  puppeteer: {
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
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

  // Remove any existing suffix, then add @c.us
  const cleanNumber = number.replace(/@[a-z.]+$/, "");
  const chatId = `${cleanNumber}@c.us`;

  try {
    console.log(`📤 Enviando para ${chatId}...`);
    await client.sendMessage(chatId, message);
    console.log(`✅ Mensagem enviada para ${chatId}`);
    res.json({ status: "Mensagem enviada com sucesso" });
  } catch (err) {
    console.error(`❌ Erro ao enviar para ${chatId}:`, err.message || err);
    res.status(500).json({ error: "Erro ao enviar mensagem", details: err.message });
  }
});

const PORT = process.env.PORT || 4000;

app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 API rodando em http://localhost:${PORT}`);
});

client.initialize();
