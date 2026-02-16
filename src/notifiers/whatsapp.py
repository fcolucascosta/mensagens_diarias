import requests
import os


class WhatsAppNotifier:
    """Sends messages via a self-hosted WPPConnect Server."""

    def __init__(self):
        self.base_url = os.getenv('WPPCONNECT_SERVER_URL', 'http://localhost:21465')
        self.session = os.getenv('WPPCONNECT_SESSION_KEY', 'zapdiario_session')
        self.token = os.getenv('WPPCONNECT_TOKEN', '')
        self.recipient_phone = os.getenv('WHATSAPP_RECIPIENT_PHONE')

    def send_message(self, message):
        if not self.recipient_phone:
            print("Error: WHATSAPP_RECIPIENT_PHONE not set.")
            return False

        if not self.token:
            print("Error: WPPCONNECT_TOKEN not set. Run generate-token first.")
            return False

        url = f"{self.base_url}/api/{self.session}/send-message"

        payload = {
            "phone": self.recipient_phone,
            "message": message,
            "isGroup": False
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

        try:
            print(f"Sending to {url}...")
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in (200, 201):
                print("Message sent successfully! (WPPConnect)")
                return True
            else:
                print(f"Failed. Status: {response.status_code}, Body: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
