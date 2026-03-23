import requests
import time
import os

# =========================
# CONFIG (from Railway env)
# =========================
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

THRESHOLD_HIGH = 85
THRESHOLD_LOW = 80

# =========================
# GET BRENT PRICE
# =========================
def get_brent_price():
    url = "https://api.oilpriceapi.com/v1/prices/latest?by_code=BRENT_CRUDE_USD"
    headers = {"Authorization": f"Token {API_KEY}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        print("API RESPONSE:", data)

        # Case 1: Standard format
        if 'data' in data and isinstance(data['data'], dict):
            if 'price' in data['data']:
                return float(data['data']['price'])

        # Case 2: Direct price
        if 'price' in data:
            return float(data['price'])

        # Case 3: List format
        if 'data' in data and isinstance(data['data'], list):
            return float(data['data'][0]['price'])

        raise Exception(f"Unexpected API format: {data}")

    except Exception as e:
        print("Error fetching price:", e)
        return None


# =========================
# SEND TELEGRAM ALERT
# =========================
def send_alert(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
        print("Alert sent:", message)
    except Exception as e:
        print("Error sending alert:", e)


# =========================
# MAIN LOOP
# =========================
last_state = None  # track previous state

while True:
    try:
        price = get_brent_price()

        if price is None:
            time.sleep(60)
            continue

        print(f"Current Brent Price: {price}")

        # Determine state
        if price > THRESHOLD_HIGH:
            current_state = "HIGH"
        elif price < THRESHOLD_LOW:
            current_state = "LOW"
        else:
            current_state = "NORMAL"

        # Send alert only on state change (avoids spam)
        if current_state != last_state:

            if current_state == "HIGH":
                send_alert(f"🚨 Brent BREAKOUT ↑\nPrice: ${price}")

            elif current_state == "LOW":
                send_alert(f"⚠️ Brent BREAKDOWN ↓\nPrice: ${price}")

            else:
                send_alert(f"ℹ️ Brent back to normal\nPrice: ${price}")

            last_state = current_state

        # Optional: log to file
        with open("price_log.txt", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},{price}\n")

        # Wait 5 minutes
        time.sleep(300)

    except Exception as e:
        print("Main loop error:", e)
        time.sleep(60)
