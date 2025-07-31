from deep_translator import GoogleTranslator

def shorten_title(title, word_limit=10):
    words = title.split()
    return " ".join(words[:word_limit]) + ("..." if len(words) > word_limit else "")

def create_product_post(product):
    caption = ""
    image_url = ""

    if not product:
        return None, None

    try:
        # Translate product title to English
        title = product.item_info.title.display_value
        translated_title = GoogleTranslator(source='auto', target='en').translate(title)
        translated_title = shorten_title(translated_title)  # Shorten here

        # Get product image
        image_url = product.images.primary.large.url

        # Get price and savings
        price = None
        old_price = None
        savings = None

        if product.offers and product.offers.listings:
            price = product.offers.listings[0].price.amount
            savings_data = product.offers.listings[0].price.savings
            if savings_data and savings_data.amount:
                savings = savings_data.amount
                old_price = price + savings

        # Skip if no price
        if not price:
            print("⚠️ Price not available, skipping product.")
            return None, None

        # Discount percentage
        discount_percent = f"{(savings / old_price * 100):.2f}%" if savings and old_price else "N/A"

        # Build caption
        caption = f"🤯 {translated_title}\n\n"
        caption += "╭━━━━━━━━━━━━━━━━━━━━━╮\n"
        if savings:
            caption += f"**😱 Discount:** ₹{savings:.0f} ({discount_percent}) 🔥\n\n"
        if old_price:
            caption += f"**❌ Regular Price:** ₹{old_price:.0f}/-\n\n"
        caption += f"**✅ Deal Price:** ₹{price:.0f}/-**\n"
        caption += "╰━━━━━━━━━━━━━━━━━━━━━╯\n\n"

        caption += f"🛒 𝗕𝗨𝗬 𝗡𝗢𝗪 👇\n{product.detail_page_url}"
        return image_url, caption

    except Exception as e:
        print(f"❌ Error creating product post: {e}")
        return None, None
