from rest_framework import serializers

from .models import Product, GiftCard


class GetPriceSerializer(serializers.Serializer):
    product_code = serializers.SlugRelatedField(
        'code', queryset=Product.objects, source='product'
    )
    date = serializers.DateField()
    gift_card_code = serializers.SlugRelatedField(
        'code', queryset=GiftCard.objects, source='gift_card', required=False
    )

    def validate(self, attrs):
        date = attrs['date']
        gift_card = attrs.get('gift_card')
        if gift_card:
            if not gift_card.is_applicable(date):
                raise serializers.ValidationError(f"Gift card '{gift_card}' is not applicable for this date: {date}")
        return attrs
