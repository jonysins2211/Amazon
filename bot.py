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
import re

def extract_amazon_urls(text):
    if not text:
        return []
    return re.findall(r'(https?://(?:www\.)?(?:amzn\.to|amazon\.[a-z.]+)[^\s)\n]*)', text)

# --- Setup Logging ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Dummy Flask Server (to keep service alive on platforms like Render/Heroku) ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return '✅ Bot is alive!'

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Running Flask on port {port}")
    flask_app.run(host="0.0.0.0", port=port)

# --- Telegram Bot ---
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
    message = update.message

    if not message:
        return

    message_text = message.text or message.caption or ""
    logging.info(f"📩 Message received: {message_text}")

    amazon_links = extract_amazon_urls(message_text)
    if not amazon_links:
        await message.reply_text("❌ No Amazon link found in the message.")
        return

    posted = 0
    for original_url in amazon_links:
        affiliate_link = convert_to_affiliate_link(original_url)
        if not affiliate_link:
            continue

        try:
            amazon_api = AmazonAPI()
            product = amazon_api.get_product_from_url(affiliate_link)
            if not product:
                continue

            image_url, caption = create_product_post(product)
            if not image_url or not caption:
                continue

            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image_url,
                caption=caption,
                parse_mode='HTML'
            )
            posted += 1

        except Exception as e:
            logging.error(f"❌ Error processing link: {e}")
            continue

    if posted:
        await message.reply_text(f"✅ Sent {posted} deal(s) to channel.")
    else:
        await message.reply_text("⚠️ Could not process any of the links.")
# --- Main App Start ---
if __name__ == '__main__':
    try:
        Thread(target=run_flask).start()
        logging.info("🚀 Starting Telegram bot polling...")

        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))

        # ✅ Important fix: TEXT | CAPTION handles all message types (manual + forwarded)
        app.add_handler(MessageHandler((filters.TEXT | filters.CAPTION) & ~filters.COMMAND, handle_message))

        app.run_polling()
    except Exception as e:
        logging.critical(f"🔥 Fatal error: {e}")
