import os, time, threading, datetime, pyotp, logging
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS
from SmartApi import SmartConnect
import requests

# क्रेडेंशियल्स
API_KEY = "x9Zs2hWZ"
CLIENT_ID = "J109737"
PASSWORD = "4966"
TOTP_SECRET = "HDVHUMXPPC2FTJOSHKSK6CO5AA"
BOT_TOKEN = "8665264906:AAFJD6a08qPbw0RvLQWNL7YF6624PcSgN-w"
CHAT_ID = "8748890897"

app = Flask(__name__)
CORS(app)

class SheraBot:
    def __init__(self):
        self.smart = None
        self.is_running = False

    def login(self):
        try:
            totp = pyotp.TOTP(TOTP_SECRET).now()
            self.smart = SmartConnect(api_key=API_KEY)
            data = self.smart.generateSession(CLIENT_ID, PASSWORD, totp)
            if data['status']:
                self.send_tg("🚀 **नमस्ते जितेन्द्र भाई!**\nलखनऊ का शेरा v3 (MACD) अब Railway पर लाइव है! 🦁")
                return True
            return False
        except Exception as e:
            print(f"Login Error: {e}")
            return False

    def send_tg(self, msg):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

    def compute_macd(self, df):
        # EMA 9/21
        df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
        # MACD (12, 26, 9)
        df['macd'] = df['close'].ewm(span=12, adjust=False).mean() - df['close'].ewm(span=26, adjust=False).mean()
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Signal Logic
        df['buy'] = (df['ema9'] > df['ema21'] + 5) & (df['macd'] > df['signal'])
        df['sell'] = (df['ema9'] < df['ema21'] - 5) & (df['macd'] < df['signal'])
        return df

shera = SheraBot()

@app.route('/')
def home():
    return "<h1>Shera V3 is Roaring! 🦁</h1>"

@app.route('/start')
def start():
    if not shera.is_running:
        if shera.login():
            shera.is_running = True
            return "Bot Started! Check Telegram."
    return "Already Running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
