from datetime import date

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Product, ProductPrice, ProductPriceSchedule, GiftCard


class IntervalTestCase(TestCase):
    fixtures = ['0001_fixtures.json']

    def test_product_price_schedule_positive_cases(self):
        cases = (
            (date(2018, 5, 5), []),
            (date(2018, 11, 22), []),
            (date(2018, 11, 23), ['<ProductPriceSchedule: Black Friday Prices - 2018-11-23-2018-11-25>']),
            (date(2018, 11, 25), ['<ProductPriceSchedule: Black Friday Prices - 2018-11-23-2018-11-25>']),
            (date(2018, 11, 26), []),
            (date(2018, 12, 31), []),
            (date(2019, 1, 1), ['<ProductPriceSchedule: 2019 Prices - 2019-01-01-∞>']),
        )
        for dt, expected in cases:
            with self.subTest(date=dt, expected=expected):
                actual = ProductPriceSchedule.find_applicable(dt)
                self.assertQuerysetEqual(actual, expected, ordered=False)

    def test_ambiguous_price__choose_lowest(self):
        prod = Product.objects.get(code='big_widget')
        expen = ProductPriceSchedule.objects.create(
            name='expensive',
            date_start=date(2018, 5, 3),
            date_end=date(2018, 5, 7)
        )
        cheap = ProductPriceSchedule.objects.create(
            name='cheap',
            date_start=date(2018, 5, 1),
            date_end=date(2018, 5, 5)
        )
        ProductPrice.objects.create(price=70000, schedule=expen, product=prod)
        ProductPrice.objects.create(price=50000, schedule=cheap, product=prod)

        price = prod.get_price_on_date(date(2018, 5, 4))

        self.assertEqual(price, 50000)

    def test_no_price_for_product__return_default(self):
        day = date(2018, 5, 5)
        ProductPriceSchedule.objects.create(name='promo', date_start=day, date_end=day)
        product = Product.objects.get(code='big_widget')

        price = product.get_price_on_date(day)

        self.assertEqual(price, product.price)

    def test_gift_card_positive_cases(self):
        cases = (
            (date(2018, 6, 30), []),
            (date(2018, 7, 1), [
                '<GiftCard: 10OFF - $10.00>',
                '<GiftCard: 50OFF - $50.00>',
            ]),
            (date(2018, 11, 23), [
                '<GiftCard: 10OFF - $10.00>',
                '<GiftCard: 50OFF - $50.00>',
            ]),
            (date(2018, 11, 30), [
                '<GiftCard: 10OFF - $10.00>',
                '<GiftCard: 50OFF - $50.00>',
            ]),
            (date(2018, 12, 31), [
                '<GiftCard: 10OFF - $10.00>',
                '<GiftCard: 50OFF - $50.00>',
                '<GiftCard: 250OFF - $250.00>',
            ]),
            (date(2019, 1, 2), [
                '<GiftCard: 10OFF - $10.00>',
                '<GiftCard: 50OFF - $50.00>',
            ]),
        )
        for dt, expected in cases:
            with self.subTest(date=dt, expected=expected):
                actual = GiftCard.find_applicable(dt)
                self.assertQuerysetEqual(actual, expected, ordered=False)


class GetPriceAPITestCase(APITestCase):
    fixtures = ['0001_fixtures.json']

    def test_positive_cases(self):
        cases = (
            ({'productCode': 'big_widget', 'date': '2018-11-20'}, '$1000.00'),
            ({'productCode': 'big_widget', 'date': '2018-11-24'}, '$800.00'),
            ({'productCode': 'big_widget', 'date': '2019-01-22'}, '$1200.00'),
            ({'productCode': 'sm_widget', 'date': '2018-11-20'}, '$99.00'),
            ({'productCode': 'sm_widget', 'date': '2018-11-24'}, '$0.00'),
            ({'productCode': 'sm_widget', 'date': '2019-01-22'}, '$125.00'),
            ({   # apply gift card
                 'productCode': 'big_widget',
                 'date': '2019-01-01',
                 'giftCardCode': '250OFF',
             }, '$950.00'),
            ({   # apply gift card on cheap product so price becomes negative
                 'productCode': 'sm_widget',
                 'date': '2019-01-01',
                 'giftCardCode': '250OFF',
             }, '$0.00'),
        )
        for payload, expected in cases:
            with self.subTest(payload=payload, expected=expected):
                response = self.client.get('/api/get-price', payload)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.json()['productPrice'], expected)

    def test_negative_cases(self):
        cases = (
            ({
                 'productCode': 'qwe',
                 'date': '2019-01-01',
                 'giftCardCode': '250OFF',
             }, {'productCode': ['Product with such code doesn\'t exist.']}),
            ({
                 'productCode': 'sm_widget',
                 'date': '2019-01-01',
                 'giftCardCode': '250Oqw',
             },
             {'giftCardCode': ['Gift card with such code doesn\'t exist.']}),
            ({
                 'productCode': 'big_widget',
                 'date': '2019-01-22',
                 'giftCardCode': '250OFF',
             }, {
                 'nonFieldErrors': [
                     "Gift card '250OFF - $250.00'"
                     " is not applicable for this date: 2019-01-22"
                 ],
             }),
            ({
                 'date': '2019-01-01',
             }, {'productCode': ['This field is required.']}),
            ({
                 'productCode': 'sm_widget',
             }, {'date': ['This field is required.']}),
        )
        for payload, expected in cases:
            with self.subTest(payload=payload, expected=expected):
                response = self.client.get('/api/get-price', payload)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(response.json(), expected)
