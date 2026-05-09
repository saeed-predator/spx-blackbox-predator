import os
import requests
from flask import Flask

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = "5927427570"

@app.route("/")
def home():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": "🔥 Predator Bot شغال بنجاح"
    }

    requests.post(url, data=data)

    return "Bot Working"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
