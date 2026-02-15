import requests
import os
import json

class WhatsAppNotifier:
    def __init__(self):
        # Green API Credentials
        self.instance_id = os.getenv('GREEN_API_INSTANCE_ID')
        self.api_token = os.getenv('GREEN_API_TOKEN')
        self.recipient_phone = os.getenv('WHATSAPP_RECIPIENT_PHONE')
        
        # Base URL for Green API
        # Format: https://api.green-api.com/waInstance{{idInstance}}/{{method}}/{{apiTokenInstance}}
        if self.instance_id and self.api_token:
            self.base_url = f"https://api.green-api.com/waInstance{self.instance_id}"

    def send_message(self, message):
        if not self.instance_id or not self.api_token or not self.recipient_phone:
            print("Error: GREEN_API_INSTANCE_ID, GREEN_API_TOKEN, or WHATSAPP_RECIPIENT_PHONE not set.")
            return False

        url = f"{self.base_url}/sendMessage/{self.api_token}"
        
        # Green API expects chatId in format: "11001234567@c.us"
        chat_id = f"{self.recipient_phone}@c.us"

        payload = {
            "chatId": chat_id,
            "message": message
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                print("Message sent successfully!")
                return True
            else:
                print(f"Failed to send message. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
