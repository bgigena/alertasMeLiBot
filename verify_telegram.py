import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"Token: {TOKEN}")
print(f"Chat ID: {CHAT_ID}")

# 1. Check Bot Identity
try:
    resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe")
    print(f"getMe response: {resp.text}")
    if resp.status_code == 200:
        bot_id = str(resp.json()["result"]["id"])
        print(f"Bot ID: {bot_id}")
        if bot_id == CHAT_ID:
            print("CRITICAL: TELEGRAM_CHAT_ID is identical to the Bot ID. A bot cannot send messages to itself this way.")
except Exception as e:
    print(f"Error checking bot identity: {e}")

# 2. Check Chat Availability
try:
    resp = requests.post(f"https://api.telegram.org/bot{TOKEN}/getChat", json={"chat_id": CHAT_ID})
    print(f"getChat response: {resp.text}")
except Exception as e:
    print(f"Error checking chat availability: {e}")
