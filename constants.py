# constants.py
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env

# TELEGRAM
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# AMAZON
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
PARTNER_TAG = os.getenv("PARTNER_TAG")
AMAZON_HOST = os.getenv("AMAZON_HOST")
AMAZON_REGION = os.getenv("AMAZON_REGION")
