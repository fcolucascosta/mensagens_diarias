# Guia de Instalação: ZapDiario na Oracle Cloud (VM) ☁️

Este guia vai te ajudar a configurar sua Máquina Virtual (VM) da Oracle para rodar o bot 24 horas por dia, de graça.

## Pré-requisitos
1.  **Conta Oracle Cloud**: "Always Free" (Grátis para sempre).
2.  **VM Shape**: VM.Standard.A1.Flex (4 OCPU, 12GB RAM) - dentro do limite gratuito.
3.  **Rede**: Criada com "Start VCN Wizard" > "Create VCN with Internet Connectivity".
4.  **Sistema Operacional**: Ubuntu 24.04.

---

## Passo 0: Configurar Memória Swap
Cria "memória extra" no disco para evitar travamentos:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Passo 1: Instalar Docker

```bash
sudo apt-get update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

*Saia e entre novamente no SSH para as permissões do Docker funcionarem.*

---

## Passo 2: Baixar o Código

```bash
cd ~
git clone https://github.com/fcolucascosta/mensagens_diarias.git
cd mensagens_diarias
```

---

## Passo 3: Subir o Servidor do WhatsApp

```bash
docker compose up -d
docker ps  # Deve mostrar "wppconnect-server" rodando
```

---

## Passo 4: Gerar Token de Acesso

A SECRET_KEY (`THISISMYSECURETOKEN`) é usada **apenas** para gerar o token real.

```bash
curl -X POST "http://localhost:21465/api/zapdiario_session/THISISMYSECURETOKEN/generate-token"
```

**Resposta esperada:**
```json
{
  "status": "success",
  "session": "zapdiario_session",
  "token": "$2b$10$abc...",
  "full": "zapdiario_session:$2b$10$abc..."
}
```

> **IMPORTANTE:** Copie o valor de `"full"`. Esse é o seu Bearer Token para todas as chamadas.

---

## Passo 5: Conectar seu WhatsApp (QR Code)

Inicie a sessão (escape os `$` com `\$`):

```bash
curl -X POST "http://localhost:21465/api/zapdiario_session/start-session" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer zapdiario_session:\$2b\$10\$SEU_TOKEN_AQUI"
```

**1ª chamada:** Retorna `status: INITIALIZING` (browser iniciando).
**2ª chamada (depois de 10s):** Retorna `status: QRCODE` com o QR Code em base64.

Copie o valor de `"qrcode"` (começa com `data:image/png;base64,...`) e cole em:
👉 https://base64.guru/converter/decode/image

Escaneie o QR Code com: **WhatsApp > Aparelhos Conectados > Conectar um aparelho**.

---

## Passo 6: Configurar o Bot Python

```bash
sudo apt-get install -y python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Criar o arquivo `.env`
```bash
nano .env
```

Cole:
```env
WPPCONNECT_SERVER_URL=http://localhost:21465
WPPCONNECT_SESSION_KEY=zapdiario_session
WPPCONNECT_TOKEN=zapdiario_session:$2b$10$SEU_TOKEN_COMPLETO_AQUI

WHATSAPP_RECIPIENT_PHONE=5585991617709
YOUTUBE_CHANNEL_WEEKDAY=UCP6L9TPS3pHccVRiDB_cvqQ
YOUTUBE_CHANNEL_SATURDAY=UCuQH2IQ95hg72ZmC0P5V-bg
```

Salvar: `Ctrl+O`, `Enter`. Sair: `Ctrl+X`.

---

## Passo 7: Testar

```bash
python src/main.py
```

---

## Passo 8: Agendar (Automático todo dia às 06:00) ⏰

```bash
crontab -e
```

Adicione no final:
```cron
0 6 * * * cd /home/ubuntu/mensagens_diarias && /home/ubuntu/mensagens_diarias/venv/bin/python src/main.py >> /home/ubuntu/mensagens_diarias/bot.log 2>&1
```

**🚀 Seu bot agora vive na nuvem, de graça, sem depender de API paga.**
