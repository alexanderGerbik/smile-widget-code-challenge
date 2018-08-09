from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import GetPriceSerializer
from .utils import get_product_price


class GetPrice(APIView):
    def post(self, request, format=None):
        serializer = GetPriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product_code']
        date = serializer.validated_data['date']
        gift_card = serializer.validated_data.get('gift_card_code', None)

        price = get_product_price(product, date, gift_card)
        price = '${0:.2f}'.format(price / 100)
        return Response({'product_price': price})
