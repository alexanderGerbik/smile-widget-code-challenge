def get_product_price(product, date, gift_card):
    price = product.get_price_on_date(date)
    if gift_card is not None:
        price = max(0, price - gift_card.amount)
    return price
