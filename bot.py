import logging
import os
from flask import Flask
from threading import Thread
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from constants import TELEGRAM_TOKEN, CHANNEL_ID, PARTNER_TAG
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
    return '✅ Bot is alive!'

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Running Flask on port {port}")
    flask_app.run(host="0.0.0.0", port=port)

# --- Telegram Bot Logic ---
bot = Bot(token=TELEGRAM_TOKEN)

def convert_to_affiliate_link(url):
    try:
        if "amzn.to" in url:
            url = expand_url(url)

        parsed = urlparse(url)

        if "amazon." not in parsed.netloc:
            return None

        query = parse_qs(parsed.query)
        query["tag"] = [PARTNER_TAG]

        new_query = urlencode(query, doseq=True)
        new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', new_query, ''))
        return new_url
    except Exception as e:
        logging.error(f"❌ Error converting to affiliate link: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'👋 Hi {update.effective_user.first_name}, send me an Amazon link!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    logging.info(f"📩 Message received: {message_text}")

    if 'amazon.' in message_text or 'amzn.to' in message_text:
        affiliate_link = convert_to_affiliate_link(message_text)

        if not affiliate_link:
            logging.warning("❌ Could not create affiliate link.")
            await update.message.reply_text("❌ Could not process this link.")
            return

        try:
            amazon_api = AmazonAPI()
            product = amazon_api.get_product_from_url(affiliate_link)
        except Exception as e:
            logging.error(f"❌ Error fetching product: {e}")
            await update.message.reply_text("⚠️ Failed to fetch product details.")
            return

        if not product:
            logging.warning(f"⚠️ ASIN not found or product data missing for: {affiliate_link}")
            await update.message.reply_text(f"🔗 Here's your affiliate link:\n{affiliate_link}")
            return

        try:
            image_url, caption = create_product_post(product)
        except Exception as e:
            logging.error(f"❌ Error creating product post: {e}")
            await update.message.reply_text(f"🔗 Here's your affiliate link:\n{affiliate_link}")
            return

        if not image_url or not caption:
            logging.warning("⚠️ Missing image or caption.")
            await update.message.reply_text(f"🔗 Here's your affiliate link:\n{affiliate_link}")
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
            logging.error(f"❌ Error sending to channel: {e}")
            await update.message.reply_text("⚠️ Error sending post.")
    else:
        await update.message.reply_text("❗️Please send a valid Amazon link.")

# --- Main App Start ---
if __name__ == '__main__':
    try:
        Thread(target=run_flask).start()
        logging.info("🚀 Starting Telegram bot polling...")

        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.run_polling()
    except Exception as e:
        logging.critical(f"🔥 Fatal error: {e}")
