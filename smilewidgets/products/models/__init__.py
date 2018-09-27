from django.db import models

from .interval import Interval


class Product(models.Model):
    name = models.CharField(max_length=25, help_text='Customer facing name of product')
    code = models.CharField(max_length=10, help_text='Internal facing reference to product', unique=True)
    price = models.PositiveIntegerField(help_text='Price of product in cents')

    def __str__(self):
        return '{} - {}'.format(self.name, self.code)

    def get_price_on_date(self, date):
        schedules = ProductPriceSchedule.find_applicable(date)
        product_price = (
            ProductPrice.objects
            .filter(schedule__in=schedules, product=self)
            .order_by('price')
            .first()
        )
        return product_price.price if product_price else self.price


class GiftCard(Interval):
    code = models.CharField(max_length=30, unique=True)
    amount = models.PositiveIntegerField(help_text='Value of gift card in cents')

    def apply(self, price):
        return max(0, price - self.amount)

    def __str__(self):
        return '{} - {}'.format(self.code, self.formatted_amount)

    @property
    def formatted_amount(self):
        return '${0:.2f}'.format(self.amount / 100)


class ProductPriceSchedule(Interval):
    name = models.CharField(max_length=25, help_text='Price schedule description')

    def __str__(self):
        return '{} - {}-{}'.format(self.name, self.date_start, self.date_end or '∞')


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    schedule = models.ForeignKey(ProductPriceSchedule, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(help_text='Price of product in cents during specific period')

    def __str__(self):
        return '{}({}) - {}'.format(self.product, self.price, self.schedule)
