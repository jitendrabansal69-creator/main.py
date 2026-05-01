import os
import time
import pyotp
import requests
from SmartApi import SmartConnect

# Railway Variables
API_KEY       = os.environ.get("API_KEY")
CLIENT_ID     = os.environ.get("CLIENT_ID")
PASSWORD      = os.environ.get("PASSWORD")
TOTP_SECRET   = os.environ.get("TOTP_SECRET")
BOT_TOKEN     = os.environ.get("BOT_TOKEN")
CHAT_ID       = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    """Telegram पर मैसेज भेजने का सिस्टम"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        print("Telegram API Response:", response.status_code)
    except Exception as e:
        print("Telegram Error:", e)

def login_angel_one():
    """Angel One में लॉगिन करने का सिस्टम"""
    print(f"लॉगिन का प्रयास किया जा रहा है... Client ID: {CLIENT_ID}")
    try:
        smartApi = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        data = smartApi.generateSession(CLIENT_ID, PASSWORD, totp)
        
        if data['status']:
            print("✅ Angel One लॉगिन सफल!")
            send_telegram_message("✅ *Angel One लॉगिन सफलतापूर्वक हो गया! Lucknow Shera V4.1 तैयार है।*")
            return smartApi
        else:
            print("❌ लॉगिन फेल:", data)
            send_telegram_message(f"❌ *Angel One लॉगिन फेल हो गया!*\nकारण: `{data}`")
            return None
    except Exception as e:
        print("⚠️ एरर:", e)
        send_telegram_message(f"⚠️ *कोड में कोई एरर आ गया है:*\n`{e}`")
        return None

if __name__ == "__main__":
    print("Lucknow Shera Bot is Starting...")
    # सबसे पहले चेक करते हैं कि क्या Telegram काम कर रहा है
    send_telegram_message("🚀 *बॉट सर्वर पर स्टार्ट हो रहा है... चेक कर रहा हूँ कि सब सही है या नहीं।*")
    
    # फिर Angel One में लॉगिन करते हैं
    api_obj = login_angel_one()
    
    # कोड को 24/7 चालू रखने के लिए
    while True:
        time.sleep(3600)
