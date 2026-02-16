import os
import datetime
from dotenv import load_dotenv

load_dotenv()


from scrapers.youtube import YouTubeScraper
from scrapers.web import WebScraper
from scrapers.youtube import YouTubeScraper
from scrapers.web import WebScraper
from notifiers.whatsapp import WhatsAppNotifier

def main():
    # 1. Configuration (Load from Env Vars)
    # Defaults are based on user request
    CHANNEL_ID_WEEKDAY = os.getenv('YOUTUBE_CHANNEL_WEEKDAY') or 'UCP6L9TPS3pHccVRiDB_cvqQ' # Padre Paulo Ricardo
    CHANNEL_ID_SATURDAY = os.getenv('YOUTUBE_CHANNEL_SATURDAY') or 'UCuQH2IQ95hg72ZmC0P5V-bg' # Padre Mario Sartori
    
    # 2. Determine Day of Week (Brazil Time UTC-3)
    # 0 = Monday, 6 = Sunday
    utc_now = datetime.datetime.utcnow()
    br_time = utc_now - datetime.timedelta(hours=3)
    today = br_time.weekday()
    
    print(f"Current Brazil Time: {br_time}")
    print(f"Running for day index: {today} (0=Mon, 6=Sun)")

    # Logic: 
    # Mon-Fri (0-4) + Sun (6)? User said "Domingo a Sexta" (Sun-Fri) is one channel.
    # Saturday (5) is the other.
    
    target_channel_id = None
    if today == 5: # Saturday
        print("It is Saturday. Using Saturday Channel.")
        target_channel_id = CHANNEL_ID_SATURDAY
    else: # Sunday (6) or Mon-Fri (0-4)
        print("It is a Weekday/Sunday. Using Weekday Channel.")
        target_channel_id = CHANNEL_ID_WEEKDAY

    # 3. Initialize Modules
    yt_scraper = YouTubeScraper()
    web_scraper = WebScraper()
    notifier = WhatsAppNotifier()

    # 4. Fetch YouTube Video
    video = None
    if target_channel_id:
        print(f"Checking channel ID: {target_channel_id}")
        # Pattern to verify if it is the correct video (User requested "homilia" must be in title)
        video = yt_scraper.get_latest_video(target_channel_id, title_pattern="homilia")
        if video:
            print(f"✅ Video found: {video['title']}")
        else:
            print("⚠️ No video found matching pattern 'homilia' or channel is empty.")
    else:
        print("⚠️ No Channel ID configured for today.")

    # 5. Fetch Website Text
    web_text = None
    # Hardcoded URL for this specific user request
    TARGET_URL = "https://liturgia.cancaonova.com/pb/"
    
    web_text = web_scraper.extract_text(TARGET_URL)

    # 6. Send Notifications
    
    # Send Text
    if web_text:
        print(f"Sending Evangelho preview: {web_text[:50]}...")
        notifier.send_message(f"*Evangelho do Dia*\n\n{web_text}")
    else:
        print("Skipping web text notification (not found or disabled).")

    # Send Video
    if video:
        print(f"Sending Video: {video['title']}")
        message = f"*Vídeo de Hoje*\n{video['title']}\n{video['link']}"
        notifier.send_message(message)
    else:
        print("Skipping video notification (not found or disabled).")

if __name__ == "__main__":
    main()
