from django.db import models
from django.db.models import Q

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
