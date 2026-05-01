import os
import time
import pyotp
import pandas as pd
import requests
from SmartApi import SmartConnect
from datetime import datetime, timedelta

# Railway के Variables से क्रेडेंशियल्स लेना (सुरक्षा के लिए)
API_KEY       = os.environ.get("API_KEY")
CLIENT_ID     = os.environ.get("CLIENT_ID")
PASSWORD      = os.environ.get("PASSWORD")
TOTP_SECRET   = os.environ.get("TOTP_SECRET")
BOT_TOKEN     = os.environ.get("BOT_TOKEN")
CHAT_ID       = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except:
        pass

def login_angel_one():
    try:
        smartApi = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        data = smartApi.generateSession(CLIENT_ID, PASSWORD, totp)
        return smartApi if data['status'] else None
    except:
        return None

if __name__ == "__main__":
    api_obj = login_angel_one()
    if api_obj:
        send_telegram_message("🚀 *Lucknow Shera V4.1* Railway पर सफलतापूर्वक शुरू हो गया है!")
        
    # सर्वर को चालू रखने के लिए
    while True:
        time.sleep(3600)
      
