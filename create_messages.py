from deep_translator import GoogleTranslator

def format_deal_message(product):
    try:
        # Title translation (Marathi to English or auto detect)
        title = product.item_info.title.display_value
        translated_title = GoogleTranslator(source='auto', target='en').translate(title)
        
        # Prices
        price = None
        savings = None
        regular_price = None

        if product.offers and product.offers.listings:
            price = product.offers.listings[0].price.amount
            savings_data = product.offers.listings[0].price.savings
            if savings_data:
                savings = savings_data.amount
                regular_price = price + savings

        if not price:
            print("⚠️ Price not available, skipping product.")
            return None

        # Calculate discount percentage
        discount_percent = f"{(savings / regular_price * 100):.2f}%" if savings and regular_price else "N/A"

        # Format message
        message = (
            f"🤯 {translated_title}\n\n"
            f"😱 Discount: ₹{savings:.2f} ({discount_percent}) 🔥\n\n"
            f"❌ Regular Price: ₹{regular_price:.2f}/-\n\n"
            f"✅ Deal Price: ₹{price:.0f}/-\n\n"
            f"🛒 𝗕𝗨𝗬 𝗡𝗢𝗪 👇 \n {product.detail_page_url}"
        )

        return message

    except Exception as e:
        print(f"❌ Error formatting message: {e}")
        return None
