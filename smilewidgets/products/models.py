from django.db import models
from django.db.models import Q


class Product(models.Model):
    name = models.CharField(max_length=25, help_text='Customer facing name of product')
    code = models.CharField(max_length=10, help_text='Internal facing reference to product', unique=True)
    price = models.PositiveIntegerField(help_text='Price of product in cents')

    def __str__(self):
        return '{} - {}'.format(self.name, self.code)

    def get_price_on_date(self, date):
        intervals = ProductPriceSchedule.find_applicable(date)
        if not intervals:
            return self.price
        interval = intervals[0]
        return ProductPrice.objects.get(schedule=interval, product=self).price


class Interval(models.Model):
    # both date_start and date_end are inclusive
    date_start = models.DateField()
    date_end = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def find_applicable(model, date):
        return model.objects.filter(
            Q(date_start__lte=date)
            & (Q(date_end__isnull=True) | Q(date_end__gte=date))
        )

    def is_applicable(self, date):
        return (self.date_start <= date
                and (self.date_end is None or date <= self.date_end))


class GiftCard(Interval):
    code = models.CharField(max_length=30, unique=True)
    amount = models.PositiveIntegerField(help_text='Value of gift card in cents')

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
