from rest_framework import serializers


class GetPriceSerializer(serializers.Serializer):
    product_code = serializers.CharField(max_length=10)
    date = serializers.DateField()
    gift_card_code = serializers.CharField(max_length=30, required=False)
