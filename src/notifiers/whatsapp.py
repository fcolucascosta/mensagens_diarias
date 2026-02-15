import requests
import os
import json

class WhatsAppNotifier:
    def __init__(self):
        # WPPConnect Server Configuration
        # Default URL for local docker container: http://localhost:21465
        self.base_url = os.getenv('WPPCONNECT_SERVER_URL', 'http://localhost:21465')
        self.session_key = os.getenv('WPPCONNECT_SESSION_KEY', 'zapdiario_session')
        self.token = os.getenv('WPPCONNECT_SECRET_KEY', 'THISISMYSECURETOKEN')
        self.recipient_phone = os.getenv('WHATSAPP_RECIPIENT_PHONE')

    def send_message(self, message):
        if not self.recipient_phone:
            print("Error: WHATSAPP_RECIPIENT_PHONE not set.")
            return False

        # WPPConnect API Endpoint: /api/:session/send-message
        url = f"{self.base_url}/api/{self.session_key}/send-message"
        
        # Ensure phone number formatting (WPPConnect is flexible but prefers DDI+DDD+Number)
        # Assuming input is like 558599...
        
        payload = {
            "phone": self.recipient_phone,
            "message": message,
            "isGroup": False
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

        try:
            print(f"Sending to {url}...")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 201 or response.status_code == 200:
                print("Message sent successfully! (WPPConnect)")
                return True
            else:
                print(f"Failed to send message. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
