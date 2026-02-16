import os
import datetime
from dotenv import load_dotenv

load_dotenv()

from scrapers.youtube import YouTubeScraper
from scrapers.web import WebScraper
from notifiers.whatsapp import WhatsAppNotifier


def get_brazil_time():
    """Returns current datetime in Brazil timezone (UTC-3)."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    br_tz = datetime.timezone(datetime.timedelta(hours=-3))
    return utc_now.astimezone(br_tz)


def main():
    # 1. Configuration
    CHANNEL_ID_WEEKDAY = os.getenv('YOUTUBE_CHANNEL_WEEKDAY') or 'UCP6L9TPS3pHccVRiDB_cvqQ'
    CHANNEL_ID_SATURDAY = os.getenv('YOUTUBE_CHANNEL_SATURDAY') or 'UCuQH2IQ95hg72ZmC0P5V-bg'

    # 2. Determine Day of Week (Brazil Time UTC-3)
    br_now = get_brazil_time()
    tomorrow = br_now + datetime.timedelta(days=1)
    today = br_now.weekday()  # 0=Mon, 6=Sun

    print(f"Horário Brasil: {br_now.strftime('%d/%m/%Y %H:%M')}")
    print(f"Evangelho de amanhã: {tomorrow.strftime('%d/%m/%Y')}")
    print(f"Dia da semana (hoje): {today} (0=Seg, 6=Dom)")

    # 3. Choose YouTube Channel
    # Sábado (5) = Padre Mario Sartori, outros dias = Padre Paulo Ricardo
    if today == 5:
        print("Sábado — usando canal do Padre Mario Sartori.")
        target_channel_id = CHANNEL_ID_SATURDAY
    else:
        print("Dia útil/Domingo — usando canal do Padre Paulo Ricardo.")
        target_channel_id = CHANNEL_ID_WEEKDAY

    # 4. Initialize Modules
    yt_scraper = YouTubeScraper()
    web_scraper = WebScraper()
    notifier = WhatsAppNotifier()

    # 5. Fetch YouTube Video
    video = None
    if target_channel_id:
        print(f"Buscando vídeo no canal: {target_channel_id}")
        video = yt_scraper.get_latest_video(target_channel_id, title_pattern="homilia")
        if video:
            print(f"✅ Vídeo encontrado: {video['title']}")
        else:
            print("⚠️ Nenhum vídeo com 'homilia' no título encontrado.")

    # 6. Fetch Evangelho de AMANHÃ
    liturgy_url = (
        f"https://liturgia.cancaonova.com/pb/"
        f"?sDia={tomorrow.day}&sMes={tomorrow.month:02d}&sAno={tomorrow.year}"
    )
    print(f"Buscando liturgia de amanhã: {liturgy_url}")
    web_text = web_scraper.extract_text(liturgy_url)

    # 7. Send Notifications
    if web_text:
        date_str = tomorrow.strftime('%d/%m/%Y')
        print(f"Enviando Evangelho: {web_text[:50]}...")
        notifier.send_message(f"📖 *Evangelho de Amanhã ({date_str})*\n\n{web_text}")
    else:
        print("⚠️ Evangelho não encontrado, pulando.")

    if video:
        print(f"Enviando vídeo: {video['title']}")
        notifier.send_message(f"🎬 *Homilia do Dia*\n{video['title']}\n{video['link']}")
    else:
        print("⚠️ Vídeo não encontrado, pulando.")


if __name__ == "__main__":
    main()
