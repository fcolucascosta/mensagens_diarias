# 📖 ZapDiário — Documentação Completa

> **Projeto:** Bot automatizado que envia o Evangelho do dia seguinte e o vídeo da Homilia Diária direto no WhatsApp, todas as noites às 22h.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Estrutura de Pastas](#estrutura-de-pastas)
4. [Fluxo de Execução Completo](#fluxo-de-execução-completo)
5. [Arquivo por Arquivo](#arquivo-por-arquivo)
   - [src/main.py — O Orquestrador](#srcmainpy--o-orquestrador)
   - [src/scrapers/youtube.py — Scraper do YouTube](#srcscrapersyoutubepy--scraper-do-youtube)
   - [src/scrapers/web.py — Scraper do Evangelho](#srcscraperswebpy--scraper-do-evangelho)
   - [src/notifiers/whatsapp.py — Notificador WhatsApp](#srcnotifierswhatsapppy--notificador-whatsapp)
   - [src/notifiers/telegram.py — Notificador Telegram (backup)](#srcnotifierstelegrampy--notificador-telegram-backup)
   - [whatsapp-server/index.js — API WhatsApp (Node.js)](#whatsapp-serverindexjs--api-whatsapp-nodejs)
   - [whatsapp-server/Dockerfile — Container Docker](#whatsapp-serverdockerfile--container-docker)
   - [whatsapp-server/package.json — Dependências Node.js](#whatsapp-serverpackagejson--dependências-nodejs)
   - [docker-compose.yml — Orquestração Docker](#docker-composeyml--orquestração-docker)
   - [.env — Variáveis de Ambiente](#env--variáveis-de-ambiente)
   - [requirements.txt — Dependências Python](#requirementstxt--dependências-python)
6. [Infraestrutura e Deploy](#infraestrutura-e-deploy)
7. [Problemas Conhecidos e Soluções](#problemas-conhecidos-e-soluções)
8. [Glossário Técnico](#glossário-técnico)

---

## Visão Geral

O **ZapDiário** é um sistema automatizado que toda noite às **22h (horário de Brasília)** realiza as seguintes etapas:

1. **Busca o Evangelho de amanhã** no site da Canção Nova (web scraping)
2. **Busca o vídeo da Homilia Diária** no YouTube (via feed RSS)
3. **Envia ambos no WhatsApp** do usuário via API local

O usuário então, na manhã seguinte, encaminha as mensagens para o grupo da família.

### Por que existe?

O dono do projeto costumava **manualmente** acessar o site da Canção Nova, copiar o Evangelho, buscar o vídeo da homilia no YouTube, salvar tudo no WhatsApp à noite, e encaminhar para a família de manhã. Este bot automatiza toda essa parte da coleta e envio.

---

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    Oracle Cloud VM                       │
│                  (Ubuntu 24.04, 1GB RAM)                 │
│                                                          │
│  ┌──────────┐    ┌────────────────────────────────────┐  │
│  │  CRON    │    │        Docker Container            │  │
│  │ (22h BR) │    │  ┌──────────────────────────────┐  │  │
│  └────┬─────┘    │  │   whatsapp-server (Node.js)  │  │  │
│       │          │  │                              │  │  │
│       ▼          │  │  Express API (porta 4000)    │  │  │
│  ┌──────────┐    │  │  whatsapp-web.js + Puppeteer │  │  │
│  │  Python  │    │  │  Chromium (headless)          │  │  │
│  │ main.py  │───▶│  └──────────────────────────────┘  │  │
│  └──────────┘    │       ▲                            │  │
│       │          │       │ POST /send                 │  │
│       │          └───────┼────────────────────────────┘  │
│       │                  │                               │
│       ▼                  ▼                               │
│  ┌──────────┐    ┌──────────────┐                        │
│  │ Scrapers │    │  WhatsApp    │                        │
│  │ YouTube  │    │  (sessão     │                        │
│  │ Web      │    │   autenticada)│                       │
│  └──────────┘    └──────────────┘                        │
└─────────────────────────────────────────────────────────┘
       │                     │
       ▼                     ▼
┌──────────────┐   ┌──────────────────┐
│ Canção Nova  │   │  Seu WhatsApp    │
│ YouTube RSS  │   │  (celular)       │
└──────────────┘   └──────────────────┘
```

### Duas partes independentes:

| Parte | Linguagem | Função |
|-------|-----------|--------|
| **Bot Python** | Python 3 | Faz scraping, monta mensagens, chama a API |
| **API WhatsApp** | Node.js | Mantém sessão do WhatsApp Web, envia mensagens |

O Python **não** tem acesso direto ao WhatsApp. Ele manda um pedido HTTP (POST) para a API Node.js, que por sua vez usa o Chromium para enviar via WhatsApp Web.

---

## Estrutura de Pastas

```
zapdiario/
│
├── src/                          # ← Código Python (o bot)
│   ├── __init__.py               #    Marca como pacote Python
│   ├── main.py                   #    🎯 ORQUESTRADOR — ponto de entrada
│   │
│   ├── scrapers/                 #    Módulos de coleta de dados
│   │   ├── __init__.py
│   │   ├── youtube.py            #    Busca vídeos no YouTube via RSS
│   │   └── web.py                #    Busca Evangelho no Canção Nova
│   │
│   └── notifiers/                #    Módulos de envio de mensagens
│       ├── __init__.py
│       ├── whatsapp.py           #    Envia via API WhatsApp local
│       └── telegram.py           #    Envia via Telegram (backup, não usado)
│
├── whatsapp-server/              # ← Microserviço Node.js (API WhatsApp)
│   ├── index.js                  #    Servidor Express + whatsapp-web.js
│   ├── package.json              #    Dependências Node.js
│   ├── Dockerfile                #    Imagem Docker com Chromium
│   └── .gitignore                #    Ignora node_modules, arquivos de sessão
│
├── docker-compose.yml            # ← Orquestração do container
├── requirements.txt              # ← Dependências Python
├── .env                          # ← Variáveis de ambiente (NUNCA commitar!)
├── .gitignore                    # ← Ignora .env, .venv, etc.
└── VM_SETUP.md                   # ← Guia de setup na VM Oracle
```

### O que NÃO está no repositório (e por quê):
- `.env` — contém o número de telefone e tokens (segurança)
- `.venv/` — ambiente virtual Python (reinstalável)
- `node_modules/` — dependências Node.js (reinstalável)
- `ssh-key-*.key` — chave SSH da VM (segurança)

---

## Fluxo de Execução Completo

Aqui está **exatamente** o que acontece quando o cron dispara às 22h:

### Passo 0: Cron aciona o script

```bash
# Esta linha no crontab (crontab -l) do Ubuntu:
0 1 * * * cd /home/ubuntu/mensagens_diarias && \
  /home/ubuntu/mensagens_diarias/venv/bin/python \
  /home/ubuntu/mensagens_diarias/src/main.py \
  >> /home/ubuntu/mensagens_diarias/cron.log 2>&1
```

**Explicação campo a campo:**
- `0 1 * * *` → Minuto 0, hora 1 (UTC) = **22:00 Brasil (UTC-3)**
- `cd /home/ubuntu/mensagens_diarias` → Entra na pasta do projeto
- `/home/ubuntu/.../venv/bin/python` → Usa o Python do ambiente virtual (não o do sistema)
- `/home/ubuntu/.../src/main.py` → Executa o script principal
- `>> .../cron.log 2>&1` → Redireciona toda a saída (normal + erros) para o arquivo `cron.log`

O `>>` (dois `>`) significa **append**: cada execução adiciona ao final do arquivo, sem apagar as anteriores. Isso permite ver o histórico de execuções.

### Passo 1: main.py carrega configuração

```python
load_dotenv()  # Carrega variáveis do arquivo .env
```

Isso lê o `.env` e disponibiliza as variáveis como `os.getenv('NOME')`. Sem isso, as variáveis de ambiente ficariam vazias.

### Passo 2: Calcula horário do Brasil e data de amanhã

```python
br_now = get_brazil_time()
tomorrow = br_now + datetime.timedelta(days=1)
today = br_now.weekday()
```

- `get_brazil_time()` converte UTC → Brasil (UTC-3)
- `timedelta(days=1)` adiciona 1 dia → amanhã
- `weekday()` retorna 0=Segunda, 1=Terça, ..., 5=Sábado, 6=Domingo

**Por que não usar `datetime.now()` direto?**
Porque a VM está em UTC. Se fosse 23h Brasil (= 02h UTC do dia seguinte), `datetime.now()` retornaria a data errada.

### Passo 3: Escolhe o canal do YouTube

```python
if today == 5:  # Sábado
    primary_channel = CHANNEL_ID_SATURDAY    # Padre Mario Sartori
else:
    primary_channel = CHANNEL_ID_WEEKDAY     # Padre Paulo Ricardo
```

No sábado à noite o canal primário muda porque o Padre Paulo Ricardo publica conteúdo diferente aos sábados.

### Passo 4: Busca o vídeo da Homilia

```python
video = yt_scraper.get_latest_video(primary_channel, title_pattern="homilia", check_today=True)

if not video:
    video = yt_scraper.get_latest_video(fallback_channel, title_pattern="homilia", check_today=True)
```

**Fluxo:**
1. Acessa o feed RSS do canal primário
2. Varre os 10 últimos vídeos procurando "homilia" no título
3. Verifica se foi publicado nas últimas 28 horas
4. Se não achou → tenta o canal de fallback
5. Se nenhum canal tem → mais tarde envia mensagem de aviso

### Passo 5: Busca o Evangelho de amanhã

```python
liturgy_url = web_scraper.get_liturgy_url_for_date(
    day=tomorrow.day, month=tomorrow.month, year=tomorrow.year
)
web_text = web_scraper.extract_text(liturgy_url)
```

**Fluxo (duas requisições HTTP):**
1. **Primeira requisição:** Acessa a página principal da Canção Nova com `?sMes=02&sAno=2026` para carregar o calendário do mês
2. **Busca no calendário:** Procura um link `<a>` que tenha `sDia=17` (dia de amanhã)
3. O link encontrado tem o **slug** correto, ex: `/pb/liturgia/6a-semana-tempo-comum-terca-feira-5/`
4. **Segunda requisição:** Acessa essa URL e extrai o texto do Evangelho
5. **Formata:** Remove espaços extras, cola traços no texto, organiza seções

### Passo 6: Envia as mensagens

```python
notifier.send_message(web_text)          # Evangelho
notifier.send_message(f"{video['title']}\n{video['link']}")  # Vídeo
```

Cada `send_message()` faz um POST HTTP para `http://localhost:4000/send` com o número do destinatário e o texto.

### Passo 7: API Node.js recebe e envia via WhatsApp

```javascript
const numberId = await client.getNumberId(cleanNumber);
const chatId = numberId._serialized;
await client.sendMessage(chatId, message, { linkPreview: true });
```

O Node.js usa o Puppeteer (controlador de navegador) para interagir com o WhatsApp Web e enviar a mensagem como se fosse um humano digitando.

---

## Arquivo por Arquivo

### `src/main.py` — O Orquestrador

> **Responsabilidade:** Coordena todo o fluxo — o "maestro" do sistema.

Este é o **ponto de entrada** do programa. Não faz scraping nem envia mensagens diretamente — ele **delega** para os módulos especializados.

#### Imports e configuração inicial

```python
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

from scrapers.youtube import YouTubeScraper
from scrapers.web import WebScraper
from notifiers.whatsapp import WhatsAppNotifier
```

**Por que `load_dotenv()` vem antes dos imports dos módulos?**
Porque os módulos (`WhatsAppNotifier`, por exemplo) leem variáveis de ambiente no seu `__init__`. Se o `load_dotenv()` viesse depois, as variáveis estariam vazias quando os módulos fossem importados.

#### Função `get_brazil_time()`

```python
def get_brazil_time():
    """Returns current datetime in Brazil timezone (UTC-3)."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    br_tz = datetime.timezone(datetime.timedelta(hours=-3))
    return utc_now.astimezone(br_tz)
```

**Linha a linha:**
1. `datetime.datetime.now(datetime.timezone.utc)` → Pega a hora atual em UTC (fuso universal, não depende do sistema operacional)
2. `datetime.timezone(datetime.timedelta(hours=-3))` → Define o fuso de Brasília como UTC - 3 horas
3. `.astimezone(br_tz)` → Converte o horário UTC para o horário do Brasil

**Por que não usar simplesmente `datetime.now()`?**
Porque `datetime.now()` retorna a hora do **sistema operacional**. Na VM Oracle, o sistema está em UTC. Se fossem 23h no Brasil, `datetime.now()` retornaria 02h do dia seguinte — data errada!

**Por que não usar `datetime.utcnow()`?**
Porque `utcnow()` retorna um datetime **naive** (sem informação de fuso). Desde o Python 3.12, ele é considerado **deprecated** (obsoleto). A forma correta é `datetime.now(datetime.timezone.utc)` que retorna um datetime **aware** (com fuso).

#### Função `main()` — Configuração

```python
CHANNEL_ID_WEEKDAY = os.getenv('YOUTUBE_CHANNEL_WEEKDAY') or 'UCP6L9TPS3pHccVRiDB_cvqQ'
CHANNEL_ID_SATURDAY = os.getenv('YOUTUBE_CHANNEL_SATURDAY') or 'UCuQH2IQ95hg72ZmC0P5V-bg'
```

Lê os IDs dos canais do `.env`. Se não existir, usa os valores padrão:
- `UCP6L9TPS3pHccVRiDB_cvqQ` = **Padre Paulo Ricardo** (dias úteis)
- `UCuQH2IQ95hg72ZmC0P5V-bg` = **Padre Mario Sartori** (sábados/fallback)

**O que é esse código tipo `UC...`?**
É o **Channel ID** do YouTube. Todo canal tem um identificador único. Você pode encontrá-lo na URL do canal ou usando a API do YouTube.

#### Escolha do canal com fallback

```python
if today == 5:  # Sábado
    primary_channel = CHANNEL_ID_SATURDAY
    fallback_channel = CHANNEL_ID_WEEKDAY
    primary_name = "Padre Mario Sartori"
    fallback_name = "Padre Paulo Ricardo"
else:
    primary_channel = CHANNEL_ID_WEEKDAY
    fallback_channel = CHANNEL_ID_SATURDAY
    primary_name = "Padre Paulo Ricardo"
    fallback_name = "Padre Mario Sartori"
```

**O que é "fallback"?**
É um **plano B**. Se o canal primário não tiver vídeo de homilia hoje, o bot tenta o canal secundário antes de desistir.

#### Envio das mensagens

```python
# Evangelho — texto puro, sem título
if web_text:
    notifier.send_message(web_text)

# Vídeo — título + link
if video:
    notifier.send_message(f"{video['title']}\n{video['link']}")
else:
    # Aviso que nenhuma homilia foi encontrada
    notifier.send_message(f"⚠️ *Homilia de Amanhã ({date_str})*\n\n"
        f"Nenhum vídeo de homilia encontrado hoje nos canais "
        f"de {primary_name} ou {fallback_name}.")
```

O Evangelho vai sem título porque será encaminhado para o grupo, o vídeo vai com título e link para que o WhatsApp gere a preview com thumbnail.

---

### `src/scrapers/youtube.py` — Scraper do YouTube

> **Responsabilidade:** Buscar o vídeo mais recente da Homilia Diária nos canais do YouTube.

#### Como funciona por dentro: Feed RSS do YouTube

O YouTube disponibiliza um **feed RSS** para cada canal público. É um arquivo XML com os últimos 15 vídeos do canal, atualizado automaticamente.

**URL do feed:**
```
https://www.youtube.com/feeds/videos.xml?channel_id=UCP6L9TPS3pHccVRiDB_cvqQ
```

**Exemplo de entrada no feed (simplificado):**
```xml
<entry>
  <title>Homilia Diária | "Por que esta gente pede um sinal?"</title>
  <link href="https://www.youtube.com/watch?v=ZBu2VjZ-bMI"/>
  <published>2026-02-16T21:00:00+00:00</published>
</entry>
```

A biblioteca `feedparser` transforma esse XML em objetos Python fáceis de manipular.

#### Classe `YouTubeScraper`

```python
class YouTubeScraper:
    def __init__(self):
        self.base_url = "https://www.youtube.com/feeds/videos.xml?channel_id="
```

O construtor apenas define a URL base. O channel_id será concatenado depois.

#### Método `get_latest_video()`

**Parâmetros:**
| Parâmetro | Tipo | Padrão | Função |
|-----------|------|--------|--------|
| `channel_id` | str | — | ID do canal YouTube |
| `title_pattern` | str | None | Regex para filtrar o título (ex: "homilia") |
| `check_today` | bool | True | Se deve verificar se o vídeo é recente |
| `max_results` | int | 10 | Quantos vídeos verificar |

**Fluxo detalhado:**

```python
url = f"{self.base_url}{channel_id}"
feed = feedparser.parse(url)
```

1. Monta a URL completa concatenando a base com o channel_id
2. `feedparser.parse()` faz uma requisição HTTP GET, baixa o XML e converte num objeto Python

```python
utc_now = datetime.datetime.now(datetime.timezone.utc)
br_tz = datetime.timezone(datetime.timedelta(hours=-3))
today_br = utc_now.astimezone(br_tz).date()
```

3. Calcula a data de hoje no horário do Brasil (mesmo lógica do `get_brazil_time()`)

```python
entries_to_check = feed.entries[:max_results]
```

4. Pega os `max_results` primeiros vídeos (os mais recentes). O `[:10]` é um **slice** que pega do índice 0 ao 9.

```python
for entry in entries_to_check:
    title = entry.title
    link = entry.link
    published = entry.published
```

5. Para cada vídeo, extrai o título, link e data de publicação

```python
    if title_pattern and not re.search(title_pattern, title, re.IGNORECASE):
        continue
```

6. **Filtro de título:** `re.search("homilia", titulo, re.IGNORECASE)` procura "homilia" em qualquer posição do título, ignorando maiúsculas/minúsculas. Se não encontrar → `continue` (pula para o próximo vídeo)

```python
    if check_today:
        pub_datetime_utc = datetime.datetime.strptime(
            entry.published, "%Y-%m-%dT%H:%M:%S+00:00"
        ).replace(tzinfo=datetime.timezone.utc)
        hours_ago = (utc_now - pub_datetime_utc).total_seconds() / 3600
        if hours_ago > 28:
            continue
```

7. **Filtro de data (janela de 28 horas):**
   - `strptime()` converte a string `"2026-02-16T21:00:00+00:00"` num objeto datetime
   - `.replace(tzinfo=...)` torna o datetime "aware" (com fuso horário)
   - Calcula quantas horas se passaram desde a publicação
   - Se mais de 28 horas → pula (é um vídeo antigo)

**Por que 28 horas e não 24?**
Porque o padre pode publicar às 21h de um dia e o bot rodar às 22h — são 1 hora de diferença. Mas para testes matutinos, o vídeo de ontem à noite pode ter até ~12h. A margem de 28h garante que funcione em qualquer cenário sem aceitar vídeos muito antigos (publicados há 2+ dias).

```python
    return {"title": title, "link": link, "published": published}
```

8. Retorna o primeiro vídeo que passou em todos os filtros como um **dicionário** Python

```python
return None  # Nenhum vídeo encontrado
```

9. Se nenhum dos 10 vídeos passou nos filtros, retorna `None`

---

### `src/scrapers/web.py` — Scraper do Evangelho

> **Responsabilidade:** Acessar o site da Canção Nova, encontrar a URL correta para a data desejada e extrair o texto do Evangelho.

Este é o scraper mais complexo porque o site da Canção Nova exige uma URL específica com **slug** para cada dia litúrgico.

#### Classe `WebScraper`

```python
class WebScraper:
    BASE_URL = "https://liturgia.cancaonova.com/pb/"
```

`BASE_URL` é uma **constante de classe** — não muda entre instâncias. É a URL raiz do site da liturgia.

#### Método `get_liturgy_url_for_date()` — Encontra a URL certa

**O problema que este método resolve:**
O site da Canção Nova não funciona com uma URL simples como `?sDia=17&sMes=02&sAno=2026`. Cada dia litúrgico tem um **slug** único que deve fazer parte da URL:

```
✅ Funciona:  /pb/liturgia/6a-semana-tempo-comum-terca-feira-5/?sDia=17&sMes=02&sAno=2026
❌ NÃO funciona: /pb/?sDia=17&sMes=02&sAno=2026
```

**Como o método encontra o slug correto:**

```python
response = requests.get(self.BASE_URL, headers=headers, params={
    'sMes': f'{month:02d}',
    'sAno': str(year)
})
```

1. Faz uma requisição GET para a página principal, passando mês e ano como parâmetros
2. O site retorna a página com o **calendário do mês** (uma tabela com links para cada dia)

```python
soup = BeautifulSoup(response.text, 'html.parser')
```

3. **BeautifulSoup** faz o **parsing** do HTML — transforma uma string HTML gigante numa estrutura de dados navegável (árvore de tags)

```python
target_param = f"sDia={day}"

for link in soup.find_all('a', href=True):
    href = link['href']
    if target_param in href and '/liturgia/' in href:
        if re.search(rf'sDia={day}(&|$)', href):
            return href
```

4. **Busca no calendário:**
   - `soup.find_all('a', href=True)` → encontra todos os links (`<a>`) que têm atributo `href`
   - Filtra por links que contenham `sDia=17` E `/liturgia/` na URL
   - O `re.search(rf'sDia={day}(&|$)', href)` é uma **proteção extra**: garante que `sDia=1` não case com `sDia=17` (o `&` ou fim de string `$` após o número impede isso)

5. Retorna a URL completa com slug, ex: `https://liturgia.cancaonova.com/pb/liturgia/6a-semana-tempo-comum-terca-feira-5/?sDia=17&sMes=02&sAno=2026`

#### Método `extract_text()` — Extrai o Evangelho

```python
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
```

1. Acessa a URL com slug e parseia o HTML

```python
content_div = soup.select_one('#content') or soup.body
```

2. Encontra a `<div id="content">` que contém todo o conteúdo da página. Se não existir, usa o `<body>` inteiro como fallback.

```python
evangelho_header = content_div.find(
    lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4', 'p', 'strong']
    and 'Evangelho' in tag.get_text()
)
```

3. **Encontra o início do Evangelho:** Procura por qualquer tag de título ou texto que contenha a palavra "Evangelho". Usa uma **lambda** (função anônima) como critério de busca — mais flexível que procurar uma tag específica.

```python
extracted_text = [evangelho_header.get_text(separator=' ', strip=True)]

for sibling in evangelho_header.next_siblings:
    if sibling.name in ['h1', 'h2', 'h3', 'h4', 'hr']:
        break
    if sibling.name == 'p':
        text = sibling.get_text(separator=' ', strip=True)
        text = re.sub(r' +', ' ', text).strip()
        if text:
            extracted_text.append(text)
```

4. **Coleta o texto:**
   - Começa com o texto do header ("Evangelho (Mc 8,14-21)")
   - `next_siblings` percorre todos os elementos HTML **após** o header, na mesma hierarquia
   - Se encontra outro título (`h1`, `h2`, etc.) ou linha horizontal (`hr`) → **para** (chegou na próxima seção)
   - Se é um parágrafo (`p`) → extrai o texto e adiciona à lista
   - `get_text(separator=' ')` → mantém espaços entre tags internas (como `<sup>` dos versículos)
   - `re.sub(r' +', ' ', text)` → substitui múltiplos espaços por um só

```python
raw_text = "\n\n".join(extracted_text)
return self._format_evangelho(raw_text)
```

5. Junta todos os parágrafos com **duas quebras de linha** entre eles e aplica formatação

#### Método `_format_evangelho()` — Formata o texto

> O `_` no início do nome indica que é um método **privado** — só usado internamente pela classe.

```python
# Fix "- Text" → "-Text" (dash touching text)
text = re.sub(r'^- ', '-', text, flags=re.MULTILINE)
```

1. Remove o espaço depois do traço no início de cada linha. `^- ` com `re.MULTILINE` casa com `- ` no início de **qualquer** linha (não só a primeira).

```python
# Regras de junção de linhas
if 'Aleluia' in current and next_non_empty.startswith('-'):
    should_join = True

if 'Proclamação' in current and 'Glória' in next_non_empty:
    should_join = True

if 'Palavra da Salvação' in current and 'Glória' in next_non_empty:
    should_join = True
```

2. **Remove linhas em branco** entre pares específicos:
   - Depois do "Aleluia" → antes da Aclamação (que começa com `-`)
   - Depois da "Proclamação" → antes do "Glória a vós"
   - Depois da "Palavra da Salvação" → antes do "Glória a vós"

**O resultado final** é o texto formatado exatamente como o usuário quer: limpo, sem espaços extras, com traços colados no texto.

---

### `src/notifiers/whatsapp.py` — Notificador WhatsApp

> **Responsabilidade:** Enviar mensagens via a API WhatsApp local (Node.js).

```python
class WhatsAppNotifier:
    def __init__(self):
        self.api_url = os.getenv('WHATSAPP_API_URL', 'http://localhost:4000')
        self.recipient_phone = os.getenv('WHATSAPP_RECIPIENT_PHONE')
```

**O construtor:**
- `api_url` → URL da API Node.js (localhost:4000 por padrão)
- `recipient_phone` → Número de telefone do destinatário, lido do `.env`

```python
def send_message(self, message):
    url = f"{self.api_url}/send"
    payload = {
        "number": self.recipient_phone,
        "message": message
    }
    response = requests.post(url, json=payload)
```

**O método `send_message()`:**
1. Monta a URL completa: `http://localhost:4000/send`
2. Cria o **payload** (corpo da requisição) com o número e a mensagem
3. `requests.post(url, json=payload)` → Faz uma requisição **POST** com corpo JSON
4. O `json=payload` automaticamente converte o dicionário Python para JSON e define o header `Content-Type: application/json`

**O que acontece por baixo:**
```
Python (send_message) → HTTP POST → Node.js (index.js) → WhatsApp Web → Celular
```

---

### `src/notifiers/telegram.py` — Notificador Telegram (backup)

> **Status:** Não utilizado atualmente. Foi criado como alternativa ao WhatsApp mas não é chamado no `main.py`.

Funciona de forma similar ao WhatsApp, mas usa a API oficial do Telegram:

```python
url = f"https://api.telegram.org/bot{self.token}/sendMessage"
```

O Telegram tem uma API REST oficial e gratuita — diferente do WhatsApp que precisa do workaround com Puppeteer. Se um dia o WhatsApp parar de funcionar, este módulo pode ser ativado como backup.

---

### `whatsapp-server/index.js` — API WhatsApp (Node.js)

> **Responsabilidade:** Manter uma sessão autenticada do WhatsApp Web e expor uma API HTTP para enviar mensagens.

Este é o arquivo mais complexo em termos de infraestrutura. Ele roda **dentro de um container Docker**.

#### Imports e setup

```javascript
const express = require("express");
const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");

const app = express();
app.use(express.json());
```

- `express` → framework web para criar a API HTTP
- `whatsapp-web.js` → biblioteca que controla o WhatsApp Web via Puppeteer
- `qrcode-terminal` → gera QR codes no terminal
- `express.json()` → middleware que parseia o corpo das requisições JSON

#### Configuração do cliente WhatsApp

```javascript
const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "/data/session" }),
  puppeteer: {
    headless: true,
    protocolTimeout: 120000,
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
```

**`authStrategy: new LocalAuth({ dataPath: "/data/session" })`:**
Salva a sessão do WhatsApp no diretório `/data/session` dentro do container. Esse diretório é mapeado para um **volume Docker** chamado `whatsapp_session`, o que significa que a sessão persiste mesmo se o container for recriado. Sem isso, seria necessário escanear o QR code toda vez.

**`puppeteer: { ... }`:**
Configurações do Chromium (navegador embutido):

| Flag | Função |
|------|--------|
| `headless: true` | Roda sem interface gráfica (obrigatório no servidor) |
| `protocolTimeout: 120000` | 120 segundos de timeout (padrão é 30s, muito pouco para 1GB RAM) |
| `--no-sandbox` | Desativa sandbox do Chromium (necessário no Docker) |
| `--disable-dev-shm-usage` | Não usa `/dev/shm` (compartilhamento de memória — limitado no Docker) |
| `--disable-gpu` | Sem aceleração gráfica (não tem GPU no servidor) |
| `--disable-extensions` | Sem extensões (economia de memória) |
| `--disable-background-timer-throttling` | Não reduzir timers em segundo plano |
| `--disable-renderer-backgrounding` | Não pausar renderização em background |

As duas últimas flags garantem que o Chromium não "durma" quando está em segundo plano, o que causaria falhas ao enviar mensagens.

#### Eventos do cliente

```javascript
client.on("qr", (qr) => {
  qrcode.generate(qr, { small: true });
});
```

Quando o WhatsApp pede autenticação, gera um QR code no terminal. Você vê isso nos logs do Docker (`docker logs -f whatsapp-server`).

```javascript
client.on("ready", () => {
  console.log("✅ Cliente WhatsApp pronto!");
});
```

Emitido quando o WhatsApp está 100% conectado e pronto para enviar.

```javascript
client.on("auth_failure", (msg) => {
  console.error("❌ Falha na autenticação:", msg);
});
```

Se a sessão expirar ou for removida pelo celular.

#### Endpoint `/send` — Envio de mensagens

```javascript
app.post("/send", async (req, res) => {
  const { number, message } = req.body;
```

Recebe um POST com JSON contendo `number` e `message`.

```javascript
  const cleanNumber = number.replace(/@[a-z.]+$/, "");
```

**Sanitiza o número:** Remove sufixos como `@c.us` ou `@s.whatsapp.net` se vieram junto. O regex `/@[a-z.]+$/` casa com `@` seguido de letras minúsculas e pontos no final da string.

```javascript
  const numberId = await client.getNumberId(cleanNumber);
  if (!numberId) {
    return res.status(404).json({ error: "Número não encontrado no WhatsApp" });
  }
  const chatId = numberId._serialized;
```

**Resolução do ID (workaround para bug "No LID for user"):**
O WhatsApp usa internamente dois IDs diferentes:
- **Chat ID**: `5585991617709@c.us` (formato antigo)
- **LID**: identificador interno novo

O `getNumberId()` consulta os servidores do WhatsApp para obter o ID correto, independente de qual formato esteja em uso. Sem isso, o envio falha com erro "No LID for user" em certas contas.

```javascript
  if (message.match(/https?:\/\//)) {
    console.log(`⏳ Link detectado, aguardando 5s para preview...`);
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
```

**Delay de 5 segundos para links:**
Se a mensagem contém uma URL (`http://` ou `https://`), espera 5 segundos antes de enviar. Isso dá tempo para o WhatsApp buscar a **preview** do link (thumbnail, título).

O `new Promise(resolve => setTimeout(resolve, 5000))` é a forma JavaScript de "esperar" — cria uma Promise que resolve sozinha após 5 segundos.

```javascript
  await client.sendMessage(chatId, message, { linkPreview: true });
```

Envia a mensagem. O `{ linkPreview: true }` instrui o WhatsApp a gerar preview de links.

#### Inicialização do servidor

```javascript
const PORT = process.env.PORT || 4000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 API rodando em http://localhost:${PORT}`);
});
client.initialize();
```

- `app.listen()` → inicia o servidor Express na porta 4000
- `"0.0.0.0"` → aceita conexões de qualquer IP (necessário dentro do Docker)
- `client.initialize()` → inicia o Puppeteer, abre o Chromium e carrega o WhatsApp Web

---

### `whatsapp-server/Dockerfile` — Container Docker

> **Responsabilidade:** Criar uma imagem Docker com Node.js + Chromium + todas as dependências.

```dockerfile
FROM node:20-slim
```

Imagem base: Node.js 20 na versão "slim" (pequena, sem extras desnecessários).

```dockerfile
RUN apt-get update && apt-get install -y \
  git wget ca-certificates fonts-liberation \
  libappindicator3-1 libasound2 libatk-bridge2.0-0 \
  libatk1.0-0 libcups2 libdbus-1-3 libgbm1 libgtk-3-0 \
  libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
  libxdamage1 libxrandr2 xdg-utils \
  --no-install-recommends && rm -rf /var/lib/apt/lists/*
```

Instala as **dependências do Chromium**. O Puppeteer baixa o Chromium automaticamente, mas ele precisa dessas bibliotecas de sistema para funcionar:

| Pacote | Função |
|--------|--------|
| `git` | Necessário para instalar `whatsapp-web.js` do GitHub |
| `wget`, `ca-certificates` | Para baixar o Chromium |
| `fonts-liberation` | Fontes para renderizar texto |
| `libgbm1`, `libgtk-3-0`, etc. | Bibliotecas gráficas que o Chromium precisa |
| `xdg-utils` | Utilitários de desktop (exigidos pelo Chromium) |

`--no-install-recommends` → Instala apenas o necessário, sem pacotes "recomendados" (economia de espaço).
`rm -rf /var/lib/apt/lists/*` → Limpa cache do apt (economia de espaço na imagem).

```dockerfile
WORKDIR /whatsapp-server
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 4000
CMD ["npm", "start"]
```

**Ordem otimizada para cache Docker:**
1. Copia apenas `package.json` primeiro
2. Roda `npm install` (instala dependências)
3. Depois copia o código

Por quê esta ordem? Por causa das **camadas do Docker**: se o `package.json` não mudou, o Docker reutiliza o cache do `npm install` e não reinstala tudo. Só recopia o código que mudou. Isso faz o build ser muito mais rápido na maioria das vezes.

---

### `whatsapp-server/package.json` — Dependências Node.js

```json
{
  "dependencies": {
    "express": "^5.1.0",
    "qrcode-terminal": "^0.12.0",
    "whatsapp-web.js": "^1.26.1-alpha.3"
  }
}
```

| Pacote | Versão | Função |
|--------|--------|--------|
| `express` | 5.1.0 | Framework web para a API REST |
| `qrcode-terminal` | 0.12.0 | Gera QR code ASCII no terminal |
| `whatsapp-web.js` | 1.26.1-alpha.3 | Controla o WhatsApp Web via Puppeteer |

**Por que `^1.26.1-alpha.3`?**
O `^` permite atualizar patches (ex: 1.26.2) mas não major (ex: 2.0.0). A versão alpha é necessária porque as versões estáveis do `whatsapp-web.js` não suportam as últimas mudanças do WhatsApp Web.

---

### `docker-compose.yml` — Orquestração Docker

```yaml
services:
  whatsapp:
    build: ./whatsapp-server
    container_name: whatsapp-server
    ports:
      - "4000:4000"
    volumes:
      - whatsapp_session:/data/session
    restart: always

volumes:
  whatsapp_session:
```

**Linha a linha:**

| Propriedade | Valor | Explicação |
|-------------|-------|------------|
| `build: ./whatsapp-server` | — | Build a imagem a partir do Dockerfile nesta pasta |
| `container_name` | `whatsapp-server` | Nome fixo do container (para `docker logs whatsapp-server`) |
| `ports: "4000:4000"` | — | Mapeia porta 4000 do container → porta 4000 do host |
| `volumes: whatsapp_session:/data/session` | — | Persiste a sessão do WhatsApp no volume Docker |
| `restart: always` | — | Se o container crashar, reinicia automaticamente |

**Volume `whatsapp_session`:**
É um armazenamento persistente gerenciado pelo Docker. Mesmo que o container seja destruído e recriado, os dados (sessão do WhatsApp) permanecem. Sem isso, seria necessário escanear o QR code toda vez que o container fosse recriado.

---

### `.env` — Variáveis de Ambiente

```ini
# WhatsApp API (Docker microservice)
WHATSAPP_API_URL=http://localhost:4000
WHATSAPP_RECIPIENT_PHONE=5585991617709

# YouTube Channels
YOUTUBE_CHANNEL_WEEKDAY=UCP6L9TPS3pHccVRiDB_cvqQ
YOUTUBE_CHANNEL_SATURDAY=UCuQH2IQ95hg72ZmC0P5V-bg
```

| Variável | Valor | Usado por |
|----------|-------|-----------|
| `WHATSAPP_API_URL` | `http://localhost:4000` | `whatsapp.py` → URL da API Node.js |
| `WHATSAPP_RECIPIENT_PHONE` | Número do destinatário | `whatsapp.py` → Para quem enviar |
| `YOUTUBE_CHANNEL_WEEKDAY` | ID do canal PPR | `main.py` → Canal de dias úteis |
| `YOUTUBE_CHANNEL_SATURDAY` | ID do canal Mario | `main.py` → Canal de sábados |

**⚠️ Segurança:** O `.env` está no `.gitignore` e NUNCA é commitado no Git. Contém dados sensíveis (número de telefone).

---

### `requirements.txt` — Dependências Python

```
requests
beautifulsoup4
feedparser
python-dotenv
```

| Pacote | Função |
|--------|--------|
| `requests` | Fazer requisições HTTP (GET/POST) |
| `beautifulsoup4` | Parsing de HTML para web scraping |
| `feedparser` | Parsing de feeds RSS/XML do YouTube |
| `python-dotenv` | Carregar variáveis do `.env` para o Python |

**Instalação:** `pip install -r requirements.txt`

---

## Infraestrutura e Deploy

### VM Oracle Cloud (Free Tier)

| Especificação | Valor |
|---------------|-------|
| **OS** | Ubuntu 24.04 LTS |
| **CPU** | 1 vCPU (AMD) |
| **RAM** | 1 GB |
| **Disco** | ~44 GB |
| **IP Público** | Fixo |
| **Custo** | Gratuito (Always Free) |

### Serviços rodando na VM

1. **Docker** → Container `whatsapp-server` (Node.js + Chromium) — roda 24/7
2. **Cron** → Executa `main.py` diariamente à 01:00 UTC (22h Brasil)

### Diagrama temporal

```
21:00 BR │ Padre publica Homilia no YouTube
         │
22:00 BR │ CRON dispara main.py
  (01:00 UTC)
         │ ┌─ YouTubeScraper busca RSS → encontra homilia
         │ ├─ WebScraper busca calendário Canção Nova → encontra URL
         │ ├─ WebScraper extrai Evangelho da URL
         │ ├─ WhatsAppNotifier POST /send (Evangelho)
         │ └─ WhatsAppNotifier POST /send (Vídeo)
         │
22:01 BR │ Mensagens chegam no WhatsApp do usuário
         │
         │ zzz... (dormindo)
         │
08:00 BR │ Usuário acorda, encaminha para o grupo da família
```

---

## Problemas Conhecidos e Soluções

### 1. "Runtime.callFunctionOn timed out"
**Causa:** VM com 1GB RAM não consegue processar a mensagem dentro do timeout padrão (30s).
**Solução:** `protocolTimeout: 120000` na configuração do Puppeteer.

### 2. "No LID for user"
**Causa:** Versões recentes do WhatsApp usam um novo sistema de identificação (LID) internamente.
**Solução:** Usar `client.getNumberId()` para resolver o ID correto antes de enviar.

### 3. Chromium lock de perfil
**Causa:** O container reiniciou sem fechar o Chromium corretamente, deixando um lock file.
**Solução:** `docker compose down && docker volume rm mensagens_diarias_whatsapp_session && docker compose up -d` (precisa escanear QR de novo).

### 4. Evangelho do dia errado
**Causa:** A URL do Canção Nova precisa de um slug, não funciona apenas com parâmetros de data.
**Solução:** `get_liturgy_url_for_date()` busca o calendário e encontra a URL correta.

### 5. Vídeo antigo ao invés do novo
**Causa:** O filtro de data era muito rígido (só "hoje") e um vídeo postado às 21h aparecia com data UTC do dia seguinte.
**Solução:** Janela de 28 horas ao invés de comparação exata de datas.

### 6. Vídeo sem thumbnail
**Causa:** WhatsApp precisa cachear a preview do link no servidor. Na primeira vez que um link novo é enviado, a preview pode não estar pronta.
**Solução parcial:** Delay de 5s antes do envio. Na prática, quando o usuário encaminha de manhã (~10h depois), a thumbnail já está cacheada e aparece normalmente.

---

## Glossário Técnico

| Termo | Significado |
|-------|------------|
| **Scraping/Web Scraping** | Técnica de extrair dados de sites automaticamente, lendo o HTML da página |
| **RSS Feed** | Formato XML usado para publicar atualizações de conteúdo (vídeos, notícias, etc.) |
| **API REST** | Interface HTTP para comunicação entre sistemas (usa verbos GET, POST, etc.) |
| **Docker** | Plataforma que empacota aplicações em "containers" — ambientes isolados e reproduzíveis |
| **Container** | Uma instância de uma imagem Docker rodando como processo isolado |
| **Volume Docker** | Armazenamento persistente que sobrevive à destruição de containers |
| **Puppeteer** | Biblioteca que controla um navegador Chromium por código |
| **Headless** | Navegador sem interface gráfica — roda apenas em memória |
| **Express** | Framework web minimalista para Node.js |
| **BeautifulSoup** | Biblioteca Python para parsing e navegação de HTML/XML |
| **feedparser** | Biblioteca Python para parsing de feeds RSS/Atom |
| **Cron/Crontab** | Agendador de tarefas do Linux, executa comandos em horários definidos |
| **Slug** | Parte descritiva de uma URL, geralmente derivada de um título (ex: `6a-semana-tempo-comum`) |
| **UTC** | Coordinated Universal Time — fuso horário de referência mundial (Brasil = UTC-3) |
| **Regex** | Regular Expression — linguagem de padrões para busca em texto |
| **Lambda** | Função anônima (sem nome) definida inline, usada em filtros e callbacks |
| **Middleware** | Função intermediária que processa requisições antes do handler principal |
| **Payload** | Dados úteis de uma requisição HTTP (o "corpo" da mensagem) |
| **Fallback** | Alternativa usada quando o método principal falha (plano B) |
| **Aware datetime** | Objeto datetime que inclui informação de fuso horário |
| **Naive datetime** | Objeto datetime SEM informação de fuso horário (pode causar bugs) |
| **QR Code** | Código visual escaneável, usado para autenticar dispositivos no WhatsApp |
| **Webhook** | URL que recebe notificações automáticas quando um evento acontece |
| **`.env`** | Arquivo de configuração com variáveis de ambiente (nunca commitado no Git) |
| **`__init__.py`** | Arquivo que marca um diretório Python como "pacote" importável |
