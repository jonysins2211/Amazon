from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.get_items_request import GetItemsRequest
from paapi5_python_sdk.get_items_resource import GetItemsResource
from paapi5_python_sdk.partner_type import PartnerType
from paapi5_python_sdk.rest import ApiException
from constants import *
import re

class AmazonAPI:

    def __init__(self):
        self.api = DefaultApi(
        access_key=AMAZON_ACCESS_KEY, secret_key=AMAZON_SECRET_KEY, host=AMAZON_HOST, region=AMAZON_REGION
    )
    
    def get_product_from_url(self, url):
        # ✅ 1. Extract ASIN from URL
        asin_match = re.search(r"(?:dp|product)/([A-Z0-9]{10})", url)
        if not asin_match:
            print("❌ ASIN not found in URL")
            return None

        asin = asin_match.group(1)

        # ✅ 2. Define resources to fetch
        resources = [
            GetItemsResource.ITEMINFO_TITLE,
            GetItemsResource.OFFERS_LISTINGS_PRICE,
            GetItemsResource.IMAGES_PRIMARY_LARGE,
            GetItemsResource.IMAGES_VARIANTS_MEDIUM,
        ]

        # ✅ 3. Build the request
        request = GetItemsRequest(
            partner_tag=PARTNER_TAG,
            partner_type=PartnerType.ASSOCIATES,
            marketplace="www.amazon.in",
            item_ids=[asin],
            resources=resources
        )

        # ✅ 4. Make the request safely
        try:
            response = self.api.get_items(request)

            # Ensure the response is valid before accessing .items
            if (
                not response
                or not response.items_result
                or not response.items_result.items
                or len(response.items_result.items) == 0
            ):
                print("⚠️ No product data in response.")
                return None

            product = response.items_result.items[0]
            return product

        except ApiException as e:
            print(f"❌ Amazon API error: {e}")
            return None
