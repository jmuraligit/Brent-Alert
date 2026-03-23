import requests
import time
import os

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

THRESHOLD = 85

def get_brent_price():
    url = "https://api.oilpriceapi.com/v1/prices/latest?by_code=BRENT_CRUDE_USD"
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data']['price']

def send_alert(price):
    message = f"🚨 Brent Alert: ${price}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

last_alert = None

while True:
    try:
        price = get_brent_price()
        print("Brent:", price)

        if price > THRESHOLD and (last_alert is None or last_alert <= THRESHOLD):
            send_alert(price)
            last_alert = price

        time.sleep(300)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
