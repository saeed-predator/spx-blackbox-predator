import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5927427570")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, data=payload, timeout=10)
    print("Telegram status:", r.status_code, r.text)

@app.route("/")
def home():
    return "Predator Bot Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    print("Webhook received:", data)

    msg = f"""🔥 TradingView Alert

📌 Symbol: {data.get('ticker', 'Unknown')}
💰 Price: {data.get('price', 'Unknown')}
⏰ Time: {data.get('time', 'Unknown')}
🎯 Signal: {data.get('signal', 'Unknown')}
"""

    send_telegram(msg)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
