# Guia de Instalação: ZapDiario na Oracle Cloud (VM) ☁️

Este guia configura sua VM Oracle para rodar o bot 24h/dia, de graça.

## Pré-requisitos
1. **Conta Oracle Cloud** "Always Free"
2. **VM**: Ubuntu 24.04, rede criada com VCN Wizard
3. **Git + Docker** instalados

---

## Passo 1: Instalar Docker

```bash
sudo apt-get update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

*Saia e entre no SSH novamente para aplicar permissões.*

---

## Passo 2: Baixar o Código

```bash
cd ~
git clone https://github.com/fcolucascosta/mensagens_diarias.git
cd mensagens_diarias
```

---

## Passo 3: Subir o Servidor WhatsApp

```bash
docker compose up -d --build
```

---

## Passo 4: Escanear QR Code

```bash
docker logs -f whatsapp-server
```

Espere o QR Code aparecer no terminal. Escaneie com:
**WhatsApp → Aparelhos Conectados → Conectar um aparelho**

Quando aparecer `✅ Cliente WhatsApp pronto!`, pressione `Ctrl+C`.

---

## Passo 5: Configurar Python

```bash
sudo apt-get install -y python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Criar `.env`
```bash
cat > .env << 'EOF'
WHATSAPP_API_URL=http://localhost:4000
WHATSAPP_RECIPIENT_PHONE=5585991617709
YOUTUBE_CHANNEL_WEEKDAY=UCP6L9TPS3pHccVRiDB_cvqQ
YOUTUBE_CHANNEL_SATURDAY=UCuQH2IQ95hg72ZmC0P5V-bg
EOF
```

---

## Passo 6: Testar

```bash
python src/main.py
```

---

## Passo 7: Agendar (Todo dia às 06:00) ⏰

```bash
crontab -e
```

Adicione no final:
```cron
0 6 * * * cd /home/ubuntu/mensagens_diarias && /home/ubuntu/mensagens_diarias/venv/bin/python src/main.py >> /home/ubuntu/mensagens_diarias/bot.log 2>&1
```

**🚀 Pronto! Bot rodando na nuvem, de graça.**
