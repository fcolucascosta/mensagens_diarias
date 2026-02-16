import requests
import os


class WhatsAppNotifier:
    """Sends messages via the local WhatsApp microservice (whatsapp-web.js)."""

    def __init__(self):
        self.api_url = os.getenv('WHATSAPP_API_URL', 'http://localhost:4000')
        self.recipient_phone = os.getenv('WHATSAPP_RECIPIENT_PHONE')

    def send_message(self, message):
        if not self.recipient_phone:
            print("Error: WHATSAPP_RECIPIENT_PHONE not set.")
            return False

        url = f"{self.api_url}/send"

        payload = {
            "number": self.recipient_phone,
            "message": message
        }

        try:
            print(f"Sending to {url}...")
            response = requests.post(url, json=payload)

            if response.ok:
                print("Message sent successfully!")
                return True
            else:
                print(f"Failed. Status: {response.status_code}, Body: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
