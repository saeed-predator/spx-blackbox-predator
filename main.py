import os, time, requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5927427570")

market = {}
last_sent = {}

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=10
    )

def score_engine():
    spx = market.get("SPX")
    qqq = market.get("QQQ")
    vix = market.get("VIX")
    es = market.get("ES")

    if not spx:
        return None

    call = 0
    put = 0
    reasons = []

    if spx.get("bias") == "BULL":
        call += 3
        reasons.append("SPX bullish structure")
    elif spx.get("bias") == "BEAR":
        put += 3
        reasons.append("SPX bearish structure")

    if spx.get("vwap") == "ABOVE":
        call += 2
        reasons.append("SPX above VWAP")
    elif spx.get("vwap") == "BELOW":
        put += 2
        reasons.append("SPX below VWAP")

    if spx.get("sweep") == "LOW":
        call += 3
        reasons.append("Liquidity sweep low")
    elif spx.get("sweep") == "HIGH":
        put += 3
        reasons.append("Liquidity sweep high")

    if spx.get("volume") == "HIGH":
        call += 1
        put += 1
        reasons.append("Volume expansion")

    if qqq:
        if qqq.get("bias") == "BULL":
            call += 2
            reasons.append("QQQ confirms bullish")
        elif qqq.get("bias") == "BEAR":
            put += 2
            reasons.append("QQQ confirms bearish")

    if es:
        if es.get("bias") == "BULL":
            call += 2
            reasons.append("ES leading bullish")
        elif es.get("bias") == "BEAR":
            put += 2
            reasons.append("ES leading bearish")

    if vix:
        if vix.get("bias") == "BEAR":
            call += 2
            reasons.append("VIX falling supports CALL")
        elif vix.get("bias") == "BULL":
            put += 2
            reasons.append("VIX rising supports PUT")

    direction = "WAIT"
    score = max(call, put)

    if call >= 9 and call > put:
        direction = "CALL"
    elif put >= 9 and put > call:
        direction = "PUT"

    return direction, score, reasons, spx

@app.route("/")
def home():
    return "Predator AI Engine Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    symbol = data.get("symbol", data.get("ticker", "UNKNOWN")).upper()

    market[symbol] = {
        "bias": data.get("bias", "MIXED").upper(),
        "vwap": data.get("vwap", "UNKNOWN").upper(),
        "sweep": data.get("sweep", "NONE").upper(),
        "volume": data.get("volume", "NORMAL").upper(),
        "price": data.get("price", "0"),
        "time": time.time()
    }

    result = score_engine()
    if not result:
        return "SPX not ready", 200

    direction, score, reasons, spx = result

    if direction == "WAIT":
        return f"WAIT score {score}", 200

    key = f"{direction}-{spx.get('price')}"
    now = time.time()

    if key in last_sent and now - last_sent[key] < 900:
        return "Duplicate ignored", 200

    last_sent[key] = now

    price = float(spx.get("price", 0))
    if price <= 0:
        return "Bad price", 200

    if direction == "CALL":
        sl = price * 0.996
        tp1 = price * 1.006
        tp2 = price * 1.012
    else:
        sl = price * 1.004
        tp1 = price * 0.994
        tp2 = price * 0.988

    msg = f"""🔥 PREDATOR AI SIGNAL

Direction: {direction}
Symbol: SPX
Entry: {price}
Score: {score}/14

TP1: {tp1:.2f}
TP2: {tp2:.2f}
SL: {sl:.2f}

Reasons:
- """ + "\n- ".join(reasons)

    send(msg)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
