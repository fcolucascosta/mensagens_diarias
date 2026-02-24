import requests
import os
import time


class WhatsAppNotifier:
    """Sends messages via the local WhatsApp microservice (whatsapp-web.js)."""

    def __init__(self):
        self.api_url = os.getenv('WHATSAPP_API_URL', 'http://localhost:4000')
        self.recipient_phone = os.getenv('WHATSAPP_RECIPIENT_PHONE')

    def send_message(self, message, retries=2, delay=30):
        """
        Sends a message via WhatsApp API with automatic retry.

        Args:
            message: Text to send.
            retries: Number of retry attempts if first send fails.
            delay: Seconds to wait between retries.
        """
        if not self.recipient_phone:
            print("Error: WHATSAPP_RECIPIENT_PHONE not set.")
            return False

        url = f"{self.api_url}/send"

        payload = {
            "number": self.recipient_phone,
            "message": message
        }

        for attempt in range(1, retries + 1):
            try:
                print(f"Sending to {url}..." + (f" (tentativa {attempt})" if attempt > 1 else ""))
                response = requests.post(url, json=payload, timeout=120)

                if response.ok:
                    print("Message sent successfully!")
                    return True
                else:
                    print(f"Failed. Status: {response.status_code}, Body: {response.text}")
            except Exception as e:
                print(f"Error sending message: {e}")

            # Retry if not the last attempt
            if attempt < retries:
                print(f"⏳ Aguardando {delay}s antes de tentar novamente...")
                time.sleep(delay)

        print(f"❌ Falha após {retries} tentativas.")
        return False
