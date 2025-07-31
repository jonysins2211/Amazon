
from deep_translator import GoogleTranslator

def create_product_post(product):
    caption = ""
    image_url = ""

    if not product:
        return None, None

    try:
        # Translate product title to English
        title = product.item_info.title.display_value
        translated_title = GoogleTranslator(source='auto', target='en').translate(title)

        # Get product image
        image_url = product.images.primary.large.url

        # Get price and savings from the first listing only (base repo logic)
        price = None
        old_price = None
        savings = None

        if product.offers and product.offers.listings:
            price = product.offers.listings[0].price.amount
            savings_data = product.offers.listings[0].price.savings
            if savings_data and savings_data.amount:
                savings = savings_data.amount
                old_price = price + savings

        # Skip if no price available
        if not price:
            print("⚠️ Price not available, skipping product.")
            return None, None

        # Calculate discount percentage if applicable
        discount_percent = f"{(savings / old_price * 100):.2f}%" if savings and old_price else "N/A"

        # Build the caption
        caption += f"🤯 {translated_title}\n\n"
        
        if savings:
            quote_block = ""
            quote_block += f"😱 Discount: ₹{savings:.0f} ({discount_percent}) 🔥\n\n"
        if old_price:
            quote_block += f"❌ Regular Price: ₹{old_price:.0f}/-\n\n"
        quote_block += f"✅ Deal Price: ₹{price:.0f}/-\n\n"
        caption += f"```\n{quote_block}```\n\n"
        
        caption += f"🛒 𝗕𝗨𝗬 𝗡𝗢𝗪 👇 \n {product.detail_page_url}"

        return image_url, caption
          
        bot.send_message(chat_id, caption, parse_mode='Markdown')

    except Exception as e:
        print(f"❌ Error creating product post: {e}")
        return None, None
