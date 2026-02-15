import requests
import urllib.parse
import os

class WhatsAppNotifier:
    def __init__(self):
        self.phone_number = os.getenv('WHATSAPP_PHONE')
        self.api_key = os.getenv('CALLMEBOT_API_KEY')
        self.base_url = "https://api.callmebot.com/whatsapp.php"

    def send_message(self, message):
        if not self.phone_number or not self.api_key:
            print("Error: WHATSAPP_PHONE or CALLMEBOT_API_KEY not set.")
            return False

        encoded_message = urllib.parse.quote(message)
        url = f"{self.base_url}?phone={self.phone_number}&text={encoded_message}&apikey={self.api_key}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Message sent successfully!")
                return True
            else:
                print(f"Failed to send message. Status Code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
