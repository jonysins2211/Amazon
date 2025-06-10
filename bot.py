import logging
import os
from flask import Flask
from threading import Thread
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from constants import *
from create_messages import create_product_post
from amazon_api import AmazonAPI
from utils import expand_url

# --- Setup Logging ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Dummy Flask Server (keeps Render Web Service alive) ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return 'Bot is alive!'

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Running Flask on port {port}")
    flask_app.run(host="0.0.0.0", port=port)

# --- Telegram Bot Logic ---
bot = Bot(token=TELEGRAM_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hi {update.effective_user.first_name}, send me an Amazon link!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    logging.info(f"Message received: {message_text}")

    if 'amazon.' in message_text or 'amzn.to' in message_text:
        if 'amzn.to' in message_text:
            expanded_url = expand_url(message_text)
            if not expanded_url:
                await update.message.reply_text("Could not expand the shortened Amazon link.")
                return
            message_text = expanded_url

        amazon_api = AmazonAPI()
        product = amazon_api.get_product_from_url(message_text)

        if product is None:
            await update.message.reply_text("I couldn't find the product. Please check the link.")
            return

        image_url, caption = create_product_post(product)

        if not image_url or not caption:
            await update.message.reply_text("Product data incomplete.")
            return

        try:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image_url,
                caption=caption,
                parse_mode='HTML'
            )
            await update.message.reply_text("✅ Post sent to channel.")
        except Exception as e:
            logging.error(f"Error sending to channel: {e}")
            await update.message.reply_text("Error sending post.")
    else:
        await update.message.reply_text("Please send a valid Amazon link.")

# --- Main ---
if __name__ == '__main__':
    # Run Flask in background
    Thread(target=run_flask).start()

    # Run Telegram bot in main thread (asyncio required)
    logging.info("Starting Telegram bot polling...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()
