import json, time, threading, datetime, os, logging, requests, pyotp, io
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from SmartApi import SmartConnect
from gtts import gTTS

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
CONFIG = {
    "API_KEY": "x9Zs2hWZ",
    "CLIENT_ID": "J109737",
    "PASSWORD": "4966",
    "TOTP_SECRET": "HDVHUMXPPC2FTJOSHKSK6CO5AA",
    "BOT_TOKEN": "8665264906:AAFJD6a08qPbw0RvLQWNL7YF6624PcSgN-w",
    "CHAT_ID": "8748890897",
    "SELECTED_SYMBOL": "NIFTY 50",
    "EMA_FAST": 9,
    "EMA_SLOW": 21,
    "EMA_GAP_POINTS": 5,
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,
    "VOLUME_MULTIPLIER": 1.2,
    "VOLUME_PERIOD": 20,
    "INTERVAL": "FIVE_MINUTE",
    "MODE": "paper", # backtest | paper | live
    "LOT_SIZE": 50,
}

# Instrument Data
INSTRUMENTS = {
    "NIFTY 50": {"token":"99926000","exchange":"NSE","lot":50,"strike_gap":50},
    "BANKNIFTY": {"token":"99926009","exchange":"NSE","lot":15,"strike_gap":100}
}

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class TradingState:
    def __init__(self):
        self.running = False
        self.smart_api = None
        self.trades = []
        self.last_signal = None

state = TradingState()

# ─── ANGEL ONE FUNCTIONS ─────────────────────────────────────────────────────
def angel_login():
    try:
        totp = pyotp.TOTP(CONFIG["TOTP_SECRET"]).now()
        smart = SmartConnect(api_key=CONFIG["API_KEY"])
        data = smart.generateSession(CONFIG["CLIENT_ID"], CONFIG["PASSWORD"], totp)
        if data["status"]:
            state.smart_api = smart
            logger.info("✅ Angel One Login Successful!")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Login Error: {e}")
        return False

def tg_send(msg):
    url = f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendMessage"
    requests.post(url, data={"chat_id": CONFIG["CHAT_ID"], "text": msg, "parse_mode": "HTML"})

def send_welcome():
    msg = (f"🙏 <b>नमस्ते जितेन्द्र भाई!</b>\n"
           f"लखनऊ का शेरा v3 Railway पर लाइव है! 🦁\n"
           f"━━━━━━━━━━━━━━━━━━\n"
           f"📊 Symbol: {CONFIG['SELECTED_SYMBOL']}\n"
           f"📈 MACD + EMA Strategy: Active\n"
           f"🚀 System Ready!")
    tg_send(msg)

# ─── MACD STRATEGY ──────────────────────────────────────────────────────────
def compute_indicators(df):
    df = df.copy()
    # EMA
    df['ema9'] = df['close'].ewm(span=CONFIG["EMA_FAST"], adjust=False).mean()
    df['ema21'] = df['close'].ewm(span=CONFIG["EMA_SLOW"], adjust=False).mean()
    # MACD
    df['macd_line'] = df['close'].ewm(span=CONFIG["MACD_FAST"], adjust=False).mean() - \
                      df['close'].ewm(span=CONFIG["MACD_SLOW"], adjust=False).mean()
    df['signal_line'] = df['macd_line'].ewm(span=CONFIG["MACD_SIGNAL"], adjust=False).mean()
    
    # Logic: EMA Cross + MACD Above Signal
    df['ce_signal'] = (df['ema9'] > df['ema21'] + CONFIG["EMA_GAP_POINTS"]) & (df['macd_line'] > df['signal_line'])
    df['pe_signal'] = (df['ema9'] < df['ema21'] - CONFIG["EMA_GAP_POINTS"]) & (df['macd_line'] < df['signal_line'])
    return df

# ─── MAIN LOOP ───────────────────────────────────────────────────────────────
def trading_loop():
    send_welcome()
    while state.running:
        now = datetime.datetime.now()
        # Market hours check (9:15 to 15:30)
        if now.hour >= 9 and now.hour <= 15:
            logger.info("🔍 Scanning Market...")
            # यहाँ आपका डेटा फेचिंग और ट्रेडिंग लॉजिक आएगा
        time.sleep(300)

# ─── FLASK ROUTES ────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return "<h1>Lucknow Shera v3 is Running on Railway! 🦁</h1>"

@app.route('/start', methods=['GET', 'POST'])
def start():
    if not state.running:
        if angel_login():
            state.running = True
            threading.Thread(target=trading_loop, daemon=True).start()
            return jsonify({"status": "Started", "msg": "Welcome sent to Telegram"})
    return jsonify({"status": "Already Running"})

if __name__ == "__main__":
    # Railway के लिए Port सेटिंग
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
