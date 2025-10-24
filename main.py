import logging
import requests
import os  # Import the OS library to read Environment Variables
import asyncio
from telethon import TelegramClient, events

# --- Configuration ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your API Key and the API's URL
API_KEY = "KNOXRAHUL"
API_URL = "https://numtoinfobyekam.ct.ws/api/num.php"

# --- Read Bot Token from Environment Variables ---
# This is the SAFE way to get your token on Render.
# os.environ.get('BOT_TOKEN') reads the 'BOT_TOKEN' variable you will set
# in the Render dashboard.
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    logger.critical("!!! ERROR: BOT_TOKEN environment variable is not set. !!!")
    logger.critical("Please add it in the 'Environment' tab on Render.")
    exit()

# Create the bot
bot = TelegramClient('bot_session', api_id=0, api_hash='').build_bot_client(token=BOT_TOKEN)
# We set dummy api_id and api_hash because they are not needed for bots.

# --- Bot Functions ---

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Sends a welcome message when the /start command is issued."""
    user = await event.get_sender()
    user_name = user.first_name
    
    # The message now includes your developer credit
    start_message = (
        f"Hi {user_name}!\n\n"
        f"Welcome to the Phone Number Bot. Just send me any "
        f"phone number and I'll try to find information about it.\n\n"
        f"— This bot was created by Rahul Sharma"
    )
    
    await event.reply(start_message)
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern='^(?!/)'))
async def message_handler(event):
    """Handles any regular text message (that doesn't start with '/')"""
    phone_number = event.message.text
    chat_id = event.chat_id
    
    logger.info(f"Received number: {phone_number} from chat_id: {chat_id}")
    
    async with bot.action(chat_id, 'typing'):
        try:
            # --- Calling the API ---
            params = {
                "key": API_KEY,
                "number": phone_number
            }
            
            response = requests.get(API_URL, params=params)
            response.raise_for_status()  # Check for HTTP errors
            
            data = response.json()
            logger.info(f"API Response: {data}")

            # --- Formatting the Reply ---
            if data.get("error"):
                await event.reply(f"Error: {data['error']}")
                return

            reply_message = f"<b>Info for {phone_number}:</b>\n"
            info_found = False

            for key, value in data.items():
                if value and str(value).strip() not in ["", "NA", "N/A"]:
                    formatted_key = key.replace("_", " ").title()
                    reply_message += f"\n<b>{formatted_key}:</b> {value}"
                    info_found = True
            
            if not info_found:
                await event.reply(f"No details found for {phone_number}.")
            else:
                await event.reply(reply_message, parse_mode='html')

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            await event.reply("The API service seems to be down. Please try again later.")
            
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error occurred: {req_err}")
            await event.reply("I'm having trouble connecting to the API.")
            
        except Exception as e:
            logger.error(f"An unknown error occurred: {e}")
            await event.reply("An unexpected error happened. I've logged it.")


async def main():
    """Start the bot."""
    logger.info("Bot started (Telethon)...")
    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
