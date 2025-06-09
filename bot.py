import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from constants import *
from create_messages import *
from amazon_api import AmazonAPI
from create_messages import create_product_post
from utils import expand_url  # Assume you move the function to a utils file


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot = Bot(token=TELEGRAM_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Welcome {update.effective_user.first_name}, send me the amazon link of a product for '
                                    'create the post on your channel!')

from amazon_api import AmazonAPI
from create_messages import create_product_post
from utils import expand_url  # Assume you move the function to a utils file

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    logging.info(f"Received message: {message_text}")

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

        try:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image_url,
                caption=caption,
                parse_mode='HTML'
            )
        except Exception as e:
            logging.error(f"Error sending photo: {e}")
            await update.message.reply_text("An error occurred while sending the image to the channel.")
    else:
        await update.message.reply_text("Please send a valid Amazon link.")



app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

if __name__ == '__main__':
    print("Starting bot polling...")
    app.run_polling()
