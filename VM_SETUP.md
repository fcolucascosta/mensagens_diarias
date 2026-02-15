# Guia de Instalação: ZapDiario na Oracle Cloud (VM) ☁️

Este guia vai te ajudar a configurar sua Máquina Virtual (VM) da Oracle para rodar o bot 24 horas por dia, de graça.

## Pré-requisitos
1.  **Conta Oracle Cloud**: "Always Free" (Grátis para sempre).
2.  **VM Escolhida**:
    *   **Recomendado (Top):** VM.Standard.A1.Flex (Processador Ampere/ARM). De graça dão 4 CPUs e 24GB de RAM. É muito potente.
    *   **Alternativa (Básico):** VM.Standard.E2.1.Micro (AMD). Tem só 1GB de RAM. **Se escolher essa, faça o Passo Extra de Swap abaixo.**
3.  **Sistema Operacional**: Ubuntu 22.04 ou 24.04 (Recomendado).

---

## Passo 0: (IMPORTANTE) Configurar Memória Swap
Se sua VM tiver pouca memória (1GB), o servidor do WhatsApp vai travar ela. Execute isso para criar uma "memória extra" no disco:

```bash
# Criar 2GB de swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Passo 1: Preparar a Máquina e Instalar Docker
O Docker é o sistema que vai rodar o "WhatsApp Server" isolado.

```bash
# Atualizar o sistema
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg git

# Instalar Docker (Script automático oficial)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Dar permissão para seu usuário usar o Docker sem "sudo"
sudo usermod -aG docker $ubuntu
# (Se seu usuário for opc, troque ubuntu por opc)
newgrp docker
```

---

## Passo 2: Baixar o Código do ZapDiario
Clone seu repositório para dentro da VM.

```bash
cd ~
git clone https://github.com/fcolucascosta/mensagens_diarias.git
cd mensagens_diarias
```

---

## Passo 3: Subir o Servidor do WhatsApp
Rode o comando abaixo. Ele vai baixar e ligar o `wppconnect-server` na porta 21465.

```bash
docker compose up -d
```

Verifique se subiu:
```bash
docker ps
```
*(Deve aparecer um container "wppconnect-server" rodando).*

---

## Passo 4: Conectar seu WhatsApp (Ler QR Code)
Agora precisamos ler o QR Code. Como a VM não tem tela, vamos pegar o código no terminal.

1.  Acompanhe os logs em tempo real:
    ```bash
    docker logs -f wppconnect-server
    ```
2.  Você verá mensagens de "Starting...". Quando aparecer o **QR Code** (ele desenha no terminal com caracteres), abra seu WhatsApp no celular > Aparelhos Conectados > Conectar e aponte a câmera.
3.  Se der certo, vai aparecer "Success" ou "Connected".
4.  Aperte `Ctrl + C` para sair dos logs (o servidor continua rodando).

*Nota: Se o QR Code ficar desconfigurado no terminal, copie a string "base64" (código gigante) que aparece e cole num site como [base64-image.de](https://www.base64-image.de/) para ver a imagem.*

---

## Passo 5: Configurar o Bot Python
Vamos instalar o Python para rodar nosso script `main.py`.

```bash
# Instalar Python e gerenciador de pacotes
sudo apt-get install -y python3-pip python3-venv

# Criar ambiente virtual (para não bagunçar o sistema)
python3 -m venv venv
source venv/bin/activate

# Instalar as bibliotecas do projeto
pip install -r requirements.txt
```

### Criar o arquivo de senhas (.env)
```bash
nano .env
```
Cole o conteúdo abaixo (Use o botão direito do mouse para colar no terminal):

```env
# Configuração Local (VM)
WPPCONNECT_SERVER_URL=http://localhost:21465
WPPCONNECT_SESSION_KEY=zapdiario_session
WPPCONNECT_SECRET_KEY=THISISMYSECURETOKEN

# Seus Dados
WHATSAPP_RECIPIENT_PHONE=5585991617709
# Canais YouTube
YOUTUBE_CHANNEL_WEEKDAY=UCP6L9TPS3pHccVRiDB_cvqQ
YOUTUBE_CHANNEL_SATURDAY=UCuQH2IQ95hg72ZmC0P5V-bg
```
*   Para Salvar: `Ctrl + O`, `Enter`.
*   Para Sair: `Ctrl + X`.

---

## Passo 6: Testar
Tente rodar uma vez para ver se envia a mensagem:

```bash
python src/main.py
```
*(Se tudo der certo, você receberá a mensagem no WhatsApp!)*

---

## Passo 7: Agendar (Automático todo dia) ⏰
Vamos usar o `cron` do Linux para rodar todo dia às 06:00 da manhã.

1.  Abra o editor do cron:
    ```bash
    crontab -e
    ```
    *(Escolha 1 se perguntar qual editor - nano).*

2.  Vá até o final do arquivo e adicione essa linha (cuidado com os caminhos!):

    ```cron
    0 6 * * * cd /home/ubuntu/mensagens_diarias && /home/ubuntu/mensagens_diarias/venv/bin/python src/main.py >> /home/ubuntu/mensagens_diarias/bot.log 2>&1
    ```
    *Explicação: Todo dia às 06:00, entra na pasta, usa o python do venv para rodar o script e salva o resultado no bot.log.*

3.  Salve e saia (`Ctrl+O`, `Enter`, `Ctrl+X`).

**PARABÉNS! 🚀**
Seu bot agora vive na nuvem, de graça, sem depender de API paga.
