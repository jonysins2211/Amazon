# constants.py
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env

# TELEGRAM
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("-1001948532295")

# AMAZON
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
PARTNER_TAG = os.getenv("ironman1122-21")
AMAZON_HOST = os.getenv("webservices.amazon.in")
AMAZON_REGION = os.getenv("eu-west-1")
