import requests, time, os, yaml, pandas as pd, pandas_ta as ta, matplotlib.pyplot as plt, io
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text, photo=None):
    if photo:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {'photo': ('chart.png', photo)}
        data = {"chat_id": CHAT_ID, "caption": text}
        requests.post(url, data=data, files=files)
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    data = requests.get(url).json()
    return float(data["lastPrice"]), float(data["volume"])

def analyze(symbol):
    price, vol = get_price(symbol)
    data = pd.DataFrame({"price":[price]*50})
    data["EMA20"] = ta.ema(data["price"], length=20)
    data["RSI"] = ta.rsi(data["price"], length=14)
    ema = data["EMA20"].iloc[-1]
    rsi = data["RSI"].iloc[-1]
    signal = "انتظار"
    if price > ema and rsi < 70: signal = "شراء"
    elif price < ema and rsi > 60: signal = "بيع"
    msg = f"📊 {symbol}\nالسعر: {price}\nالإشارة: {signal}\nRSI: {rsi:.2f}\nEMA20: {ema:.2f}"
    return msg, data

def main():
    with open("watchlist.yaml") as f:
        wl = yaml.safe_load(f)["watchlist"]
    for w in wl:
        if w["type"] == "crypto":
            msg, df = analyze(w["symbol"])
            plt.figure(figsize=(6,3))
            plt.plot(df["price"], label="Price")
            plt.plot(df["EMA20"], label="EMA20")
            plt.legend()
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            send_message(msg, photo=buf)
            time.sleep(2)

if __name__ == "__main__":
    main()
