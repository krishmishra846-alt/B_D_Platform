import os
import requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_thank_you_message(donor_name: str, chat_id: str, language: str = "en"):
    """Fires an instant, localized Thank You message via Telegram Bot API."""
    print(f"Routing localized Thank You message to {donor_name} in '{language}'...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Multilingual Templates
    templates = {
        "en": (
            f"Hello {donor_name}! 🩸\n\n"
            "Your blood donation is deeply appreciated. Thank you for being a lifesaver today. "
            "Your attendance has been securely verified and logged on the zero-trust ledger."
        ),
        "mr": (
            f"नमस्कार {donor_name}! 🩸\n\n"
            "तुमचे रक्तदान बहुमोल आहे. आज प्राणरक्षक बनल्याबद्दल धन्यवाद. "
            "तुमची उपस्थिती झिरो-ट्रस्ट लेजरवर सुरक्षितपणे नोंदवली गेली आहे."
        ),
        "hi": (
            f"नमस्ते {donor_name}! 🩸\n\n"
            "आपके रक्तदान की हम गहराई से सराहना करते हैं। आज जीवन रक्षक बनने के लिए धन्यवाद। "
            "आपकी उपस्थिति सुरक्षित रूप से ज़ीरो-ट्रस्ट लेजर पर दर्ज कर ली गई है।"
        )
    }
    
    # Fallback to English if an unknown language code is passed
    message_text = templates.get(language, templates["en"])
    
    payload = {
        "chat_id": chat_id,
        "text": message_text
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Success! Message delivered.")
        else:
            print(f"Delivery failed: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")