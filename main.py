import os, time, requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5927427570")

last_alert = {}

def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=10
    )

@app.route("/")
def home():
    return "Predator AI Engine Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    ticker = data.get("ticker", "UNKNOWN")
    price = float(data.get("price", 0))
    signal = data.get("signal", "WAIT").upper()
    source = data.get("source", "TradingView")
    timeframe = data.get("timeframe", "UNKNOWN")

    if signal not in ["CALL", "PUT", "BUY", "SELL"]:
        return "Ignored", 200

    direction = "CALL" if signal in ["CALL", "BUY"] else "PUT"

    key = f"{ticker}-{direction}"
    now = time.time()

    if key in last_alert and now - last_alert[key] < 900:
        return "Duplicate blocked", 200

    last_alert[key] = now

    if direction == "CALL":
        tp1 = price * 1.006
        tp2 = price * 1.012
        sl = price * 0.996
    else:
        tp1 = price * 0.994
        tp2 = price * 0.988
        sl = price * 1.004

    msg = f"""🔥 PREDATOR AI SIGNAL

📌 Symbol: {ticker}
🎯 Direction: {direction}
💰 Entry: {price}
⏱ Timeframe: {timeframe}
🧠 Source: {source}

🎯 TP1: {tp1:.2f}
🚀 TP2: {tp2:.2f}
🛑 SL: {sl:.2f}

✅ Reason:
Machine Learning Momentum signal + VWAP confirmation required manually before entry.
"""

    send_telegram(msg)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
