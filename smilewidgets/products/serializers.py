from rest_framework import serializers
from rest_framework.serializers import ValidationError

from .models import Product, GiftCard


class GetPriceSerializer(serializers.Serializer):
    product_code = serializers.CharField(max_length=10)
    date = serializers.DateField()
    gift_card_code = serializers.CharField(max_length=30, required=False)

    def validate_product_code(self, value):
        try:
            return Product.objects.get(code=value)
        except Product.DoesNotExist:
            raise ValidationError('Product with such code doesn\'t exist.')

    def validate_gift_card_code(self, value):
        try:
            return GiftCard.objects.get(code=value)
        except GiftCard.DoesNotExist:
            raise ValidationError('Gift card with such code doesn\'t exist.')

    def validate(self, attrs):
        date = attrs['date']
        gift_card = attrs.get('gift_card_code', None)
        if gift_card is not None:
            if not gift_card.is_applicable(date):
                raise ValidationError("Gift card '{}' is not applicable for this date: {}".format(gift_card, date))
        return attrs
