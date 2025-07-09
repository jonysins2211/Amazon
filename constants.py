# constants.py
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env

# TELEGRAM
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("-1001948532295")

# AMAZON
AMAZON_ACCESS_KEY = os.getenv("AKPA645Y391752095807")
AMAZON_SECRET_KEY = os.getenv("FDeCqkr0YyaX/X+Cdgwfpw6RfTjIq/30UB0LcV3h")
PARTNER_TAG = os.getenv("ironman1122-21")
AMAZON_HOST = os.getenv("webservices.amazon.in")
AMAZON_REGION = os.getenv("eu-west-1")
