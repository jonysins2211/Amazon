
from deep_translator import GoogleTranslator

def create_product_post(product):
    caption = ""
    image_url = ""

    if not product:
        return None, None

    try:
        title = product.item_info.title.display_value
        translated_title = GoogleTranslator(source='auto', target='en').translate(title)
        image_url = product.images.primary.large.url

        price = None
        old_price = None
        savings = None

        # ✅ Use lowest offer instead of only the first one
        if product.offers and product.offers.listings:
            best_offer = None

            for listing in product.offers.listings:
                try:
                    offer_price = listing.price.amount
                    if not best_offer or offer_price < best_offer.price.amount:
                        best_offer = listing
                except:
                    continue

            if best_offer:
                price = best_offer.price.amount
                savings_data = best_offer.price.savings
                if savings_data and savings_data.amount:
                    savings = savings_data.amount
                    old_price = price + savings
                else:
                    # Fallback: try list_price if available
                    try:
                        price_data = best_offer.price.to_dict()
                        list_price = price_data.get("list_price", {}).get("amount")
                        if list_price and list_price > price:
                            old_price = list_price
                            savings = old_price - price
                    except:
                        pass

        # 🚫 Skip if no price
        if not price:
            print("⚠️ Price not available, skipping product.")
            return None, None

        # 🔢 Calculate discount %
        discount_percent = f"{(savings / old_price * 100):.2f}%" if savings and old_price else "N/A"

        # 📝 Build caption
        caption += f"🤯 {translated_title}\n\n"
        if savings:
            caption += f"😱 Discount: ₹{savings:.0f} ({discount_percent}) 🔥\n\n"
        if old_price:
            caption += f"❌ Regular Price: ₹{old_price:.0f}/-\n\n"
        caption += f"✅ Deal Price: ₹{price:.0f}/-\n\n"
        caption += f"🛒 𝗕𝗨𝗬 𝗡𝗢𝗪 👇 \n {product.detail_page_url}"

        return image_url, caption

    except Exception as e:
        print(f"❌ Error creating product post: {e}")
        return None, None
