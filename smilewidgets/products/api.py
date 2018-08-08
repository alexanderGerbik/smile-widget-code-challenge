from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .serializers import GetPriceSerializer
from .models import Product, GiftCard
from .utils import get_product_price


class GetPrice(APIView):
    def post(self, request, format=None):
        serializer = GetPriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_code = serializer.validated_data['product_code']
        gift_card_code = serializer.validated_data.get('gift_card_code', None)

        date = serializer.validated_data['date']

        try:
            product = Product.objects.get(code=product_code)
        except Product.DoesNotExist:
            raise ValidationError('Product with such code doesn\'t exist.')

        if gift_card_code is None:
            gift_card = None
        else:
            try:
                gift_card = GiftCard.objects.get(code=gift_card_code)
            except GiftCard.DoesNotExist:
                raise ValidationError('Gift card with such code doesn\'t exist.')
            if not gift_card.is_applicable(date):
                raise ValidationError('Gift card is not applicable for this date: {}'.format(date))

        price = get_product_price(product, date, gift_card)
        price = '${0:.2f}'.format(price / 100)
        return Response({'product_price': price})
