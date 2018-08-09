from rest_framework.views import APIView
from rest_framework.response import Response
from djangorestframework_camel_case.util import underscoreize

from .serializers import GetPriceSerializer


class GetPrice(APIView):
    def get(self, request, format=None):
        data = underscoreize(request.query_params)
        serializer = GetPriceSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product_code']
        date = serializer.validated_data['date']
        gift_card = serializer.validated_data.get('gift_card_code', None)

        price = product.get_price_on_date(date)
        if gift_card is not None:
            price = gift_card.apply(price)
        price = '${0:.2f}'.format(price / 100)
        return Response({'product_price': price})
