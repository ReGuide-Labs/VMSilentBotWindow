import requests
import time
import random
import threading
from selenium_script import run_profiles  # Import từ file chứa selenium
import asyncio  # Add this import
import logging  # Add logging module
from telegram_helper import send_telegram_message  # Import the helper function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def worker_function(token, name):
    while True:
        position_result = get_position(token)
        ping_result = ping_server(token)
        # if not getattr(worker_function, f"{token}_automation_started", False):
        #     logging.info(f"{name} is starting run_automation in a new thread")
        #     threading.Thread(target=run_automation, args=(token, name)).start()
        #     setattr(worker_function, f"{token}_automation_started", True)
        message = f"{name} is pinging {'successfully' if ping_result else 'failed'} | "
        if ping_result:
            message += f"Behind {position_result['behind']} users | Estimated wait time: {position_result['timeRemaining']}"

            if 50 < position_result['behind'] < 52:
                asyncio.run(send_telegram_message(
                    bot_key="primary",
                    message=f"{name}: Behind {position_result['behind']} users. Estimated wait time: {position_result['timeRemaining']}"
                ))

            if position_result['behind'] == 0:
                if not getattr(worker_function, f"{token}_automation_started", False):
                    logging.info(f"{name} is starting run_automation in a new thread")
                    threading.Thread(target=run_automation, args=(token, name)).start()
                    setattr(worker_function, f"{token}_automation_started", True)

        else:
            message += "Error fetching data"

        logging.info(message)  # Replace print with logging
        time.sleep(10)  # Add a 10-second delay before the next iteration

def start_worker_threads(tokens):
    threads = []
    for index, token in enumerate(tokens):
        name = f"profile{index + 1}"
        thread = threading.Thread(target=worker_function, args=(token, name))
        thread.start()
        threads.append(thread)
        if index < len(tokens) - 1:  # Add delay only if there are more tokens to process
            time.sleep(1 * 30)  # Delay seconds
    return threads

POSITION_URL = "https://ceremony-backend.silentprotocol.org/ceremony/position"
PING_URL = "https://ceremony-backend.silentprotocol.org/ceremony/ping"

import httpx
# Biến toàn cục lưu các token đã thông báo
from queue import Queue

notified_tokens = set()
lock = threading.Lock()
notification_queue = Queue()

def telegram_worker():
    while True:
        token = notification_queue.get()
        if token is None:
            break  # Exit signal

        try:
            asyncio.run(notify_unauthorized(token))
        except Exception as e:
            logging.error(f"Error sending message to Telegram: {e}")
        finally:
            notification_queue.task_done()

# Thread chạy worker xử lý queue
notification_thread = threading.Thread(target=telegram_worker, daemon=True)
notification_thread.start()

async def notify_unauthorized(token):
    await send_telegram_message(
        bot_key="secondary",
        message=f"Unauthorized: Token {token[-15:]} is invalid.\nPlease check the token and update it if necessary."
    )

def handle_unauthorized(token):
    logging.error(f"Unauthorized: Token {token[-15:]} is invalid.")
    with lock:
        if token not in notified_tokens:
            notified_tokens.add(token)
            notification_queue.put(token)
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
            logging.info(f"✅ Status: {response.status_code} - {url}")

            if response.status_code == 304:
                return {"behind": -1, "timeRemaining": "N/A"}             
            elif response.status_code == 401:
                handle_unauthorized(token)
                return None
            elif response.status_code == 502:
                logging.error("Bad Gateway: Server error.")
                return None
            return response.json()

    except httpx.RequestError as e:
        logging.error(f"Request error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    return None

def get_position(token):
    return send_request(POSITION_URL, token)

def ping_server(token):
    return send_request(PING_URL, token)

def load_tokens():
    try:
        with open('token.txt', 'r') as file:
            tokens = [line.strip() for line in file if line.strip()]
        logging.info(f"Loaded {len(tokens)} token(s).")  # Replace print with logging
        return tokens
    except Exception as e:
        logging.error(f"Error: Cannot read file token.txt! {e}")  # Replace print with logging
        return []

def reset_automation_state(token):
    """Reset the automation state for the given token."""
    setattr(worker_function, f"{token}_automation_started", False)
    logging.info(f"Automation state reset for token: {token}")  # Use logging for consistency
    
def run_automation(token, name):
    def on_reset():
        reset_automation_state(token)

    profiles = [name]
    silent_jwt = token
    logger = logging.getLogger(name)
    try:
        run_profiles(profiles, silent_jwt, logger, on_reset)
    finally:
        setattr(worker_function, f"{token}_automation_started", False)

async def notify_startup(tokens_count):
    """Send a startup notification to Telegram using the primary bot."""
    await send_telegram_message(
        bot_key="primary",
        message=f"Silent Node Running 27/03: {tokens_count} token(s) loaded, running..."
    )

if __name__ == "__main__":
    tokens = load_tokens()
    if not tokens:
        logging.info("No tokens found. Exiting program.")
    else:
        start_worker_threads(tokens)
        logging.info("Worker threads started.")