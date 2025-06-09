from deep_translator import GoogleTranslator

def create_product_post(product):
    caption = ""
    image_url = ""

    if not product:
        return None, None

    try:
        title = product.item_info.title.display_value
        translated_title = GoogleTranslator(source='auto', target='mr').translate(title)
        image_url = product.images.primary.large.url

        price = None
        old_price = None
        if product.offers and product.offers.listings:
            price = product.offers.listings[0].price.amount
            savings = product.offers.listings[0].price.savings
            if savings and savings.amount:
                old_price = price + savings.amount

        # 🚫 Skip products with no price
        if not price:
            print("⚠️ Price not available, skipping product.")
            return None, None

        # ✅ Build caption
        caption += f"🎯 <b>{translated_title}</b>\n\n"
        caption += f"💥 किंमत: <b>{price}₹</b>\n"

        if old_price:
            caption += f"❌ जुनी किंमत: <s>{old_price}₹</s>\n"
            caption += f"🎁 बचत: <b>{old_price - price}₹</b>\n\n"
        else:
            caption += "\n"

        caption += (
            f"🚀 <b>फायदे:</b>\n"
            f"• दर्जेदार उत्पादन 🔝\n"
            f"• Deals Marathi ची खात्रीशीर डिल 🔐\n"
            f"• सवलतीत खरेदीची संधी 🛍️\n\n"
        )

        caption += f"👇🏻 खरेदीसाठी क्लिक करा:\n👉🏻 {product.detail_page_url} ✅"

        return image_url, caption

    except Exception as e:
        print(f"❌ Error creating product post: {e}")
        return None, None
