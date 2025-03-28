import asyncio
from telegram import Bot
from telegram.constants import ParseMode  # Correct import for ParseMode
import logging
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_CHAT_ID = '-1001787620122'  # Centralized chat ID
RUNNER_NAME = os.getenv("RUNNER_NAME", "Unknown Runner")  # Get runner's name from .env

TELEGRAM_BOTS = {
    "primary": {
        "token": '7967235265:AAHdTKlwR0fYBt2CEEzNaUrmD3KxLavGOLM',
        "thread_id": 152233
    },
    "secondary": {
        "token": '7832816964:AAELcVRtQoxVA6bOfqWevhbk9QxcHz9TRbQ',
        "thread_id": 177301
    }
}

def get_bot(bot_key):
    """Retrieve a Bot instance for the given bot key."""
    bot_config = TELEGRAM_BOTS[bot_key]
    return Bot(token=bot_config["token"])

def full_message_template(message):
    """Format the full message with the runner's name."""
    # Replace <br /> with a valid HTML tag or remove it
    return f"<b>==={RUNNER_NAME}===</b>\n{message}"  # Use \n for markdown line breaks

def send_telegram_message(bot_key: str, message: str):
    bot_config = TELEGRAM_BOTS.get(bot_key)
    if not bot_config:
        logging.error(f"Unknown bot key: {bot_key}")
        return

    token = bot_config["token"]
    thread_id = bot_config["thread_id"]

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": full_message_template(message),
        "message_thread_id": thread_id,
        "parse_mode": "HTML"
    }

    try:
        resp = requests.post(url, data=payload)
        if resp.ok:
            logging.info(f"✅ Message sent with bot '{bot_key}'")
        else:
            logging.error(f"Failed to send Telegram message: {resp.text}")
    except Exception as e:
        logging.error(f"Error sending Telegram message using bot '{bot_key}': {e}")

if __name__ == "__main__":
    async def main():
        # Test sending a message with HTML markdown formatting
        # await send_telegram_message(
        #     bot_key="primary",
        #     message="Test message from the primary bot."
        # )
        await send_telegram_message(
            bot_key="secondary",
            message="Token expired. Login required.\n\nPlease login to your account and check the status."
        )

    try:
        asyncio.run(main())
    except RuntimeError as e:
        logging.error(f"Runtime error during execution: {e}")