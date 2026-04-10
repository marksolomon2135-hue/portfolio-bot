import os
import requests
from datetime import datetime

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

TICKERS = ["GOOGL", "NFLX", "BRK-B", "AXON", "OXY", "PAYC", "NU"]
DISPLAY_NAMES = {"BRK-B": "BRKB"}

def fetch_quote(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1y"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    meta = data["chart"]["result"][0]["meta"]
    return {
        "price": meta.get("regularMarketPrice") or meta.get("previousClose"),
        "prev_close": meta["previousClose"],
        "high_52w": meta["fiftyTwoWeekHigh"],
        "low_52w": meta["fiftyTwoWeekLow"],
    }

def build_message():
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    rows = []
    for ticker in TICKERS:
        label = DISPLAY_NAMES.get(ticker, ticker)
        try:
            q = fetch_quote(ticker)
            price = q["price"]
            change = price - q["prev_close"]
            pct = (change / q["prev_close"]) * 100
            sign = "+" if change >= 0 else ""
            rows.append(
                f"{label:<6} | ${price:<9.2f} | {sign}${change:<9.2f} | {sign}{pct:.2f}%"
                f"  | ${q['high_52w']:<9.2f} | ${q['low_52w']:.2f}"
            )
        except Exception as e:
            rows.append(f"{label:<6} | ERROR: {e}")

    table = "\n".join(rows)
    return (
        f"<b>=== MORNING PORTFOLIO SUMMARY — {date_str} (Market Open) ===</b>\n\n"
        f"<pre>"
        f"Ticker | Price      | Change      | % Change  | 52W High   | 52W Low\n"
        f"-------|------------|-------------|-----------|------------|--------\n"
        f"{table}"
        f"</pre>\n\n"
        f"Market opens today. Good luck!"
    )

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    })
    resp.raise_for_status()
    print("Message sent successfully.")

if __name__ == "__main__":
    msg = build_message()
    send_telegram(msg)
