import time
import pyotp
import requests
from SmartApi import SmartConnect

# --- आपके सारे क्रेडेंशियल्स सीधे यहीं पर हैं ---
API_KEY       = "x9Zs2hWZ"
CLIENT_ID     = "J109737"
PASSWORD      = "4966"
TOTP_SECRET   = "HDVHUMXPPC2FTJOSHKSK6CO5AA"
BOT_TOKEN     = "8665264906:AAFJd6a08qPbw0RvLQWNL7YF6624PcSgN-w"
CHAT_ID       = "8748890897"

def p(msg):
    """मैसेज को तुरंत स्क्रीन पर दिखाने के लिए"""
    print(msg, flush=True)

def send_telegram_message(message):
    p("👉 Telegram पर मैसेज भेजा जा रहा है...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        p(f"✅ Telegram का जवाब: {response.status_code}")
    except Exception as e:
        p(f"❌ Telegram एरर: {e}")

def login_angel_one():
    p(f"👉 Angel One लॉगिन शुरू... Client ID: {CLIENT_ID}")
    try:
        smartApi = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        p("👉 OTP बन गया है, रिक्वेस्ट भेजी जा रही है...")
        
        data = smartApi.generateSession(CLIENT_ID, PASSWORD, totp)
        
        if data and data.get('status'):
            p("🎉 Angel One लॉगिन एकदम सफल!")
            send_telegram_message("✅ *Angel One लॉगिन सफलतापूर्वक हो गया! Lucknow Shera V4.1 तैयार है।*")
            return smartApi
        else:
            p(f"❌ लॉगिन फेल हो गया। डेटा: {data}")
            send_telegram_message(f"❌ *Angel One लॉगिन फेल!*\nकारण: `{data}`")
            return None
    except Exception as e:
        p(f"⚠️ Angel One सिस्टम एरर: {e}")
        send_telegram_message(f"⚠️ *कोड में सिस्टम एरर:*\n`{e}`")
        return None

if __name__ == "__main__":
    p("🚀 Lucknow Shera Bot is Starting... [STEP 1]")
    
    # सबसे पहले Telegram चेक
    send_telegram_message("🚀 *बॉट सर्वर पर स्टार्ट हो रहा है... नेटवर्क चेक कर रहा हूँ।*")
    
    p("🚀 Telegram टेस्ट पूरा हुआ। अब Angel One की बारी... [STEP 2]")
    # फिर Angel One में लॉगिन
    api_obj = login_angel_one()
    
    p("⏳ सेटअप पूरा हुआ। अब बॉट 24/7 एक्टिव रहेगा... [STEP 3]")
    # कोड को 24/7 चालू रखने के लिए
    while True:
        time.sleep(3600)
        
