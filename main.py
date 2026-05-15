# IP पता करने के लिए छोटा सा कोड
import requests
def tell_me_my_ip():
    try:
        current_ip = requests.get('https://api.ipify.org').text
        print(f"🦁 SHERA SERVER IP: {current_ip}")
        # टेलीग्राम पर भी भेज दें
        url = f"https://api.telegram.org/bot8352232623:AAFI5uYY2Q3Bt3T4p20eT2EWBLkf3pDOvFE/sendMessage"
        requests.post(url, data={"chat_id": "8748890897", "text": f"📍 SHERA SERVER IP: {current_ip}"})
    except:
        print("IP नहीं मिला")

tell_me_my_ip() # कोड शुरू होते ही IP बताएगा
# -*- coding: utf-8 -*-
"""
LUCKNOW SHERA — SERVER VERSION (V8)
=====================================
- GUI Disabled: रेलवे और क्लाउड सर्वर्स के लिए परफेक्ट।
- रिमोट कंट्रोल: टेलीग्राम (/start, /stop, /status) से कंट्रोल होगा।
- नो आईपी झंझट: सर्वर का फिक्स आईपी एक बार एंजेल वन में डालना होगा।
"""

import threading, datetime, time, logging, os
import requests, pyotp
import pandas as pd
import numpy as np
from SmartApi import SmartConnect

# ─── 1. कॉन्फ़िगरेशन (Credentials) ──────────────────────────────────
CFG = {
    "API_KEY":    "x9Zs2hWZ",
    "CLIENT_ID":  "J109737",
    "PASSWORD":   "4966",
    "TOTP":       "HDVHUMXPPC2FTJOSHKSK6CO5AA",
    "BOT_TOKEN":  "8352232623:AAFI5uYY2Q3Bt3T4p20eT2EWBLkf3pDOvFE",
    "CHAT_ID":    "8748890897",
    "SYMBOL":     "NIFTY 50",
    "EMA_FAST":   9,
    "EMA_SLOW":   21,
    "EMA_GAP":    2,
    "SL_PTS":     30,
    "TSL_PTS":    10,
    "TGT_PTS":    40,
    "LOT_SIZE":   50,
}

# ─── 2. ग्लोबल स्टेट ───────────────────────────────────────────────
class ST:
    running = False
    api     = None
    last_op = None  # आखिरी ट्रेड की जानकारी

# ─── 3. टेलीग्राम और लॉगिंग ──────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

def tg(msg):
    try:
        url = f"https://api.telegram.org/bot{CFG['BOT_TOKEN']}/sendMessage"
        requests.post(url, data={"chat_id": CFG["CHAT_ID"], "text": msg, "parse_mode": "HTML"}, timeout=10)
    except: pass

# ─── 4. एंजेल वन लॉगिन और डेटा ──────────────────────────────────────
def angel_login():
    try:
        totp = pyotp.TOTP(CFG["TOTP"]).now()
        s = SmartConnect(api_key=CFG["API_KEY"])
        res = s.generateSession(CFG["CLIENT_ID"], CFG["PASSWORD"], totp)
        if res['status']:
            ST.api = s
            return True
        return False
    except: return False

def fetch_candles(token, exchange):
    to_dt = datetime.datetime.now()
    frm_dt = to_dt - datetime.timedelta(days=3)
    try:
        r = ST.api.getCandleData({
            "exchange": exchange, "symboltoken": token, "interval": "FIVE_MINUTE",
            "fromdate": frm_dt.strftime("%Y-%m-%d %H:%M"), "todate": to_dt.strftime("%Y-%m-%d %H:%M")
        })
        if r["status"] and r["data"]:
            df = pd.DataFrame(r["data"], columns=["dt","open","high","low","close","volume"])
            df["close"] = pd.to_numeric(df["close"])
            return df
    except: return pd.DataFrame()

# ─── 5. इंडिकेटर और लॉजिक ──────────────────────────────────────────
def calc_indicators(df):
    df["ema_f"] = df["close"].ewm(span=CFG["EMA_FAST"], adjust=False).mean()
    df["ema_s"] = df["close"].ewm(span=CFG["EMA_SLOW"], adjust=False).mean()
    df["gap"]   = df["ema_f"] - df["ema_s"]
    
    last_gap = df["gap"].iloc[-1]
    prev_gap = df["gap"].iloc[-2]
    
    ce_sig = (last_gap >= CFG["EMA_GAP"]) and (prev_gap < CFG["EMA_GAP"])
    pe_sig = (last_gap <= -CFG["EMA_GAP"]) and (prev_gap > -CFG["EMA_GAP"])
    return ce_sig, pe_sig, last_gap

# ─── 6. मेन ट्रेडिंग लूप ────────────────────────────────────────────
def main_strategy_loop():
    tg(f"🚀 <b>{CFG['SYMBOL']}</b> शेरा सर्वर पर जाग गया है!")
    
    while ST.running:
        try:
            now = datetime.datetime.now().time()
            # सिर्फ मार्केट ऑवर में चेक करें (9:15 - 3:30)
            if datetime.time(9,15) <= now <= datetime.time(15,30):
                df = fetch_candles("99926000", "NSE") # NIFTY Spot
                if not df.empty:
                    ce, pe, gap = calc_indicators(df)
                    ltp = df["close"].iloc[-1]
                    
                    if ce:
                        msg = f"🟢 <b>BUY CALL (CE)</b>\nPrice: {ltp}\nGap: {gap:.2f}\nStrategy: BB_RSI_LKO"
                        tg(msg)
                        time.sleep(300) # 5 मिनट का पॉज़
                    elif pe:
                        msg = f"🔴 <b>BUY PUT (PE)</b>\nPrice: {ltp}\nGap: {gap:.2f}\nStrategy: BB_RSI_LKO"
                        tg(msg)
                        time.sleep(300)
            
            time.sleep(60) # हर मिनट चेक करें
        except Exception as e:
            logging.error(f"Loop Error: {e}")
            time.sleep(30)

# ─── 7. टेलीग्राम कंट्रोल (रिमोट) ──────────────────────────────────────
def poll_telegram():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{CFG['BOT_TOKEN']}/getUpdates"
            r = requests.get(url, params={"offset": offset, "timeout": 30}).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                txt = msg.get("text", "").lower()
                
                if txt == "/start":
                    if not ST.running:
                        if angel_login():
                            ST.running = True
                            threading.Thread(target=main_strategy_loop, daemon=True).start()
                        else: tg("❌ लॉगिन फेल! क्रेडेंशियल्स चेक करें।")
                    else: tg("शेरा पहले से ही शिकार पर है! 🦁")
                
                elif txt == "/stop":
                    ST.running = False
                    tg("🛑 शेरा को वापस बुला लिया गया है (Stopped)।")
                
                elif txt == "/status":
                    status = "RUNNING 🟢" if ST.running else "STOPPED 🔴"
                    tg(f"<b>Status:</b> {status}\n<b>Symbol:</b> {CFG['SYMBOL']}\n<b>EMA:</b> {CFG['EMA_FAST']}/{CFG['EMA_SLOW']}")

        except: time.sleep(10)

if __name__ == "__main__":
    print("🦁 शेरा सर्वर कंट्रोल शुरू हो रहा है...")
    poll_telegram()
