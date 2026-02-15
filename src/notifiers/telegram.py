import requests
import os

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

    def send_message(self, message):
        if not self.token or not self.chat_id:
            print("Error: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set.")
            return False

        # Telegram API URL
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown", # Allows bold/italic (e.g. *bold*)
            "disable_web_page_preview": False
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("Message sent successfully (Telegram)!")
                return True
            else:
                print(f"Failed to send to Telegram. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending to Telegram: {e}")
            return False
