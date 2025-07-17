import os
from dotenv import load_dotenv

load_dotenv()

# TELEGRAM
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# AMAZON API
AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY", "")
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY", "")
PARTNER_TAG = os.getenv("AFFILIATE_TAG", "ironman1122-21")
AMAZON_HOST = os.getenv("AMAZON_HOST", "webservices.amazon.in")
AMAZON_REGION = os.getenv("AMAZON_REGION", "eu-west-1")
