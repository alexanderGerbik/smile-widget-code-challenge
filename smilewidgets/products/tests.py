from datetime import date

from django.test import TestCase

from .models import ProductPriceSchedule, GiftCard


class ContainingIntervalTestCase(TestCase):
    fixtures = ['0001_fixtures.json']

    def test_product_price_schedule(self):
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

    def test_gift_card(self):
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
