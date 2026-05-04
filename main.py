import time, pyotp, requests, os, threading, pytz, random
import pandas as pd
from datetime import datetime, timedelta
from SmartApi import SmartConnect
from gtts import gTTS

# --- कॉन्फ़िगरेशन ---
API_KEY     = "x9Zs2hWZ"
CLIENT_ID   = "J109737"
PASSWORD    = "4966"
TOTP_SECRET = "HDVHUMXPPC2FTJOSHKSK6CO5AA"
BOT_TOKEN   = "8665264906:AAFJD6a08qPbw0RvLQWNL7YF6624PcSgN-w"
CHAT_ID     = "8748890897"

def send_tele_voice(text_msg):
    """क्लाउड से टेलीग्राम पर वॉयस मैसेज भेजने का फंक्शन"""
    def worker():
        try:
            rand_id = random.randint(1000, 9999)
            # Railway के लिए बिना /tmp/ के भी ट्राई कर सकते हैं अगर दिक्कत आए
            filename = f"shera_{rand_id}.mp3" 
            tts = gTTS(text=text_msg, lang='hi', slow=False)
            tts.save(filename)
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"
            with open(filename, "rb") as f:
                requests.post(url, data={"chat_id": CHAT_ID}, files={"voice": f}, timeout=15)
            if os.path.exists(filename): os.remove(filename)
        except: pass
    threading.Thread(target=worker).start()

def send_tele_text(m):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": m, "parse_mode": "HTML"}, timeout=10)
    except: pass

def get_data(obj, token):
    """डेटा लाने और टेक्निकल इंडिकेटर्स कैलकुलेट करने का फंक्शन"""
    for attempt in range(3):
        try:
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            params = {
                "exchange": "NFO", "symboltoken": token, "interval": "FIVE_MINUTE", 
                "fromdate": (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M"), 
                "todate": now.strftime("%Y-%m-%d %H:%M")
            }
            data = obj.getCandleData(params)
            
            if data and data.get("errorcode") == "AB1021":
                time.sleep(7) 
                continue
                
            if data and data.get("status") and data.get("data"):
                df = pd.DataFrame(data["data"], columns=["ts","open","high","low","close","volume"])
                df[["open","close","volume"]] = df[["open","close","volume"]].astype(float)
                
                # --- टेक्निकल इंडिकेटर्स ---
                df["EMA9"] = df["close"].ewm(span=9, adjust=False).mean()
                df["EMA21"] = df["close"].ewm(span=21, adjust=False).mean()
                df["VOL_MA"] = df["volume"].rolling(20).mean()
                
                delta = df["close"].diff()
                gain = delta.where(delta > 0, 0).ewm(alpha=1/14, adjust=False).mean()
                loss = -delta.where(delta < 0, 0).ewm(alpha=1/14, adjust=False).mean()
                df["RSI"] = 100 - (100 / (1 + (gain / loss)))
                return df
        except:
            time.sleep(5)
    return None

def start_bot():
    try:
        obj = SmartConnect(api_key=API_KEY)
        obj.generateSession(CLIENT_ID, PASSWORD, pyotp.TOTP(TOTP_SECRET).now())
        ist = pytz.timezone('Asia/Kolkata')
        
        send_tele_text("🌞 <b>LUCKNOW SHERA V4.1 PRO</b>\nStatus: Strict Monitoring Enabled")
        send_tele_voice("नमस्ते जितेन्द्र भाई, लखनऊ का शेरा अब और भी समझदारी के साथ लाइव हो गया है।")
        
        last_signal, last_hour = None, -1
        call_count, put_count = 0, 0

        while True:
            now = datetime.now(ist)
            if now.hour == 15 and now.minute >= 30:
                msg = f"🏁 <b>MARKET CLOSED</b>\nTotal Signals: {call_count + put_count}\nCalls: {call_count} | Puts: {put_count}"
                send_tele_text(msg)
                send_tele_voice(f"जितेन्द्र भाई, बाज़ार बंद हो गया है। आज हमने {call_count + put_count} सिग्नल पकड़े।")
                return 

            df = get_data(obj, "66691") # Nifty Token
            if df is not None:
                curr, prev = df.iloc[-1], df.iloc[-2]
                rsi_val = round(curr['RSI'], 2)
                ltp = round(curr['close'], 2)
                vol_per = round((curr['volume'] / curr['VOL_MA']) * 100, 2) if curr['VOL_MA'] > 0 else 0
                
                # --- फिल्टर कंडीशंस ---
                is_green = curr['close'] > curr['open']
                is_red   = curr['close'] < curr['open']
                vol_ok   = curr['volume'] > (curr['VOL_MA'] * 1.2) # 1.2x वॉल्यूम काफी है
                rsi_up   = curr['RSI'] > prev['RSI']
                
                # EMA Gap Filter: लाइनों के बीच फासला होना ज़रूरी है
                ema_gap = abs(curr["EMA9"] - curr["EMA21"])
                min_gap = 1.2 # कम से कम 1.2 पॉइंट की दूरी

                # 🟢 CALL SIGNAL
                if (prev["EMA9"] <= prev["EMA21"]) and (curr["EMA9"] > curr["EMA21"] + min_gap):
                    if is_green and rsi_up and vol_ok and rsi_val > 55:
                        if last_signal != "CALL":
                            send_tele_text(f"🟢 <b>STRONG CALL BUY</b>\nPrice: {ltp}\nGap: {round(ema_gap, 2)}\nVol: {vol_per}%")
                            send_tele_voice(f"जितेन्द्र भाई, कॉल बाई का सिग्नल है। मार्केट ऊपर जा रहा है।")
                            last_signal, call_count = "CALL", call_count + 1

                # 🔴 PUT SIGNAL
                elif (prev["EMA9"] >= prev["EMA21"]) and (curr["EMA9"] < curr["EMA21"] - min_gap):
                    if is_red and not rsi_up and vol_ok and rsi_val < 45:
                        if last_signal != "PUT":
                            send_tele_text(f"🔴 <b>STRONG PUT BUY</b>\nPrice: {ltp}\nGap: {round(ema_gap, 2)}\nVol: {vol_per}%")
                            send_tele_voice(f"जितेन्द्र भाई, पुट बाई का सिग्नल है। सावधानी बरतें।")
                            last_signal, put_count = "PUT", put_count + 1

                # प्रति घंटा अपडेट
                if now.minute == 0 and now.hour != last_hour:
                    trend = "तेजी" if ltp > curr['EMA9'] else "मंदी"
                    send_tele_text(f"🕒 <b>HOURLY REPORT</b>\nLTP: {ltp}\nRSI: {rsi_val}\nTrend: {trend}")
                    send_tele_voice(f"जितेन्द्र भाई, बाज़ार में अभी {trend} का ट्रेंड दिख रहा है।")
                    last_hour = now.hour
                    
            time.sleep(60) 
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    ist = pytz.timezone('Asia/Kolkata')
    while True:
        now = datetime.now(ist)
        curr_time = now.hour * 100 + now.minute
        if 915 <= curr_time < 1530:
            start_bot()
        else:
            time.sleep(60)
