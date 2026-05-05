import os, time, pyotp, logging
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
from SmartApi import SmartConnect
import requests

# --- क्रेडेंशियल्स ---
API_KEY = "x9Zs2hWZ"
CLIENT_ID = "J109737"
PASSWORD = "4966"
TOTP_SECRET = "HDVHUMXPPC2FTJOSHKSK6CO5AA"
BOT_TOKEN = "8665264906:AAFJD6a08qPbw0RvLQWNL7YF6624PcSgN-w"
CHAT_ID = "8748890897"

app = Flask(__name__)
CORS(app)

class SheraRailway:
    def __init__(self):
        self.smart = None
        self.running = False

    def tg_send(self, msg):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

    def login(self):
        try:
            totp = pyotp.TOTP(TOTP_SECRET).now()
            self.smart = SmartConnect(api_key=API_KEY)
            data = self.smart.generateSession(CLIENT_ID, PASSWORD, totp)
            if data['status']:
                self.tg_send("🚀 **नमस्ते जितेन्द्र भाई!**\nलखनऊ का शेरा v3 (MACD) अब Railway पर लाइव है! 🦁\n\n_आज का मार्केट शिकार के लिए तैयार है!_")
                return True
            return False
        except Exception as e:
            print(f"Login Error: {e}")
            return False

shera = SheraRailway()

@app.route('/')
def home():
    return "<h1>Shera V3 is Online! 🦁</h1>"

@app.route('/start')
def start():
    if not shera.running:
        if shera.login():
            shera.running = True
            return "✅ Bot Started! Welcome message sent to Telegram."
        return "❌ Login Failed! Check logs."
    return "ℹ️ Bot is already running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
