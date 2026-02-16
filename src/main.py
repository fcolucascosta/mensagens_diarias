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

    # 3. Choose primary YouTube Channel
    if today == 5:  # Sábado
        print("\n📺 Sábado — canal primário: Padre Mario Sartori")
        primary_channel = CHANNEL_ID_SATURDAY
        fallback_channel = CHANNEL_ID_WEEKDAY
        primary_name = "Padre Mario Sartori"
        fallback_name = "Padre Paulo Ricardo"
    else:
        print("\n📺 Dia útil/Domingo — canal primário: Padre Paulo Ricardo")
        primary_channel = CHANNEL_ID_WEEKDAY
        fallback_channel = CHANNEL_ID_SATURDAY
        primary_name = "Padre Paulo Ricardo"
        fallback_name = "Padre Mario Sartori"

    # 4. Initialize Modules
    yt_scraper = YouTubeScraper()
    web_scraper = WebScraper()
    notifier = WhatsAppNotifier()

    # 5. Fetch YouTube Video (with fallback)
    print(f"\n🔍 Buscando homilia no canal de {primary_name}...")
    video = yt_scraper.get_latest_video(primary_channel, title_pattern="homilia", check_today=True)
    video_source = primary_name

    if not video:
        print(f"\n🔄 Tentando fallback: {fallback_name}...")
        video = yt_scraper.get_latest_video(fallback_channel, title_pattern="homilia", check_today=True)
        video_source = fallback_name

    # 6. Fetch Evangelho de AMANHÃ (via calendário do site)
    print(f"\n📖 Buscando Evangelho de amanhã ({tomorrow.strftime('%d/%m')})...")
    liturgy_url = web_scraper.get_liturgy_url_for_date(
        day=tomorrow.day, month=tomorrow.month, year=tomorrow.year
    )

    web_text = None
    if liturgy_url:
        web_text = web_scraper.extract_text(liturgy_url)
    else:
        print("⚠️ URL da liturgia de amanhã não encontrada.")

    # 7. Send Notifications
    date_str = tomorrow.strftime('%d/%m/%Y')

    # Send Evangelho
    if web_text:
        print(f"\n📤 Enviando Evangelho...")
        notifier.send_message(web_text)
    else:
        print("⚠️ Evangelho não encontrado, pulando.")

    # Send Video
    if video:
        print(f"📤 Enviando vídeo de {video_source}...")
        notifier.send_message(
            f"{video['title']}\n"
            f"{video['link']}"
        )
    else:
        print("⚠️ Nenhuma homilia encontrada em nenhum canal.")
        notifier.send_message(
            f"⚠️ *Homilia de Amanhã ({date_str})*\n\n"
            f"Nenhum vídeo de homilia encontrado hoje nos canais "
            f"de {primary_name} ou {fallback_name}."
        )

    print("\n✅ Concluído!")


if __name__ == "__main__":
    main()
