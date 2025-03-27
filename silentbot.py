import requests
import time
import random
import threading
from telegram import Bot
from selenium_helper import run_selenium
from selenium_script import contribute, automation_interact, run_profiles  # Import từ file chứa selenium
import http.client
import json
import asyncio  # Add this import

def worker_function(token, name):
    while True:
        position_result = get_position(token)
        ping_result = ping_server(token)

        message = f"{name} is pinging {'successfully' if ping_result else 'failed'} | "
        if ping_result:
            message += f"Behind {position_result['behind']} users | Estimated wait time: {position_result['timeRemaining']}"

            if 50 < position_result['behind'] < 60:
                asyncio.run(send_telegram_message(f"{name}: Behind {position_result['behind']} users. Estimated wait time: {position_result['timeRemaining']}"))  # Use asyncio.run to call the async function

            if position_result['behind'] == 0:
                if not getattr(worker_function, f"{token}_automation_started", False):
                    print(f"{name} is starting run_automation in a new thread")
                    threading.Thread(target=run_automation, args=(token, name)).start()
                    setattr(worker_function, f"{token}_automation_started", True)

        else:
            message += "Error fetching data"

        print(message)
        time.sleep(10)  # Add a 10-second delay before the next iteration

def start_worker_threads(tokens):
    threads = []
    for index, token in enumerate(tokens):
        name = f"profile{index + 1}"
        thread = threading.Thread(target=worker_function, args=(token, name))
        thread.start()
        threads.append(thread)
    return threads

POSITION_URL = "https://ceremony-backend.silentprotocol.org/ceremony/position"
PING_URL = "https://ceremony-backend.silentprotocol.org/ceremony/ping"

TELEGRAM_BOT_TOKEN = '7967235265:AAHdTKlwR0fYBt2CEEzNaUrmD3KxLavGOLM'
TELEGRAM_CHAT_ID = '-1001787620122'
MESSAGE_THREAD_ID = 152233

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, message_thread_id=MESSAGE_THREAD_ID)
        print("Message sent to Telegram successfully.")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

import httpx

def send_request(url, token):
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {token}",
        "if-none-match": 'W/"14-Y53wuE/mmbSikKcT/WualL1N65U"',
        "origin": "https://ceremony.silentprotocol.org",
        "referer": "https://ceremony.silentprotocol.org/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }

    timeout = httpx.Timeout(60.0)

    try:
        with httpx.Client(http2=True, timeout=timeout) as client:
            response = client.get(url, headers=headers)
            print(f"✅ Status: {response.status_code} - {url}")

            if response.status_code == 304:
                return {"behind": -1, "timeRemaining": "N/A"} 

            return response.json()

    except httpx.RequestError as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    return None


def get_position(token):
    return send_request(POSITION_URL, token)

def ping_server(token):
    return send_request(PING_URL, token)

def load_tokens():
    try:
        with open('token.txt', 'r') as file:
            tokens = [line.strip() for line in file if line.strip()]
        print(f"Loaded {len(tokens)} token(s).")
        return tokens
    except Exception as e:
        print(f"Error: Cannot read file token.txt! {e}")
        return []


def run_automation(token, name):
    profiles = [name]
    
    silent_jwt = token

    run_profiles(profiles, silent_jwt)
if __name__ == "__main__":
    tokens = load_tokens()
    if not tokens:
        print("No tokens found. Exiting program.")
    else:
        asyncio.run(send_telegram_message(f"Bot updated 9/3: {len(tokens)} token(s) loaded, running..."))  # Use asyncio.run to call the async function
        start_worker_threads(tokens)
