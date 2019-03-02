from django.db import models
from django.db.models import Q

class IntervalQuerySet(models.QuerySet):
    def applicable(self, date):
        '''
            Filter queryset to contain only those intervals
            which are relevant for a given date
        '''
        return self.filter(
            Q(date_start__lte=date)
            & (Q(date_end__isnull=True) | Q(date_end__gte=date))
        )

class Interval(models.Model):
    # both date_start and date_end are inclusive
    date_start = models.DateField()
    date_end = models.DateField(blank=True, null=True)

    objects = IntervalQuerySet.as_manager()

    class Meta:
        abstract = True

    def __str__(self):
        return '{}-{}'.format(self.date_start, self.date_end or '∞')

    def is_applicable(self, date):
        return (self.date_start <= date
                and (self.date_end is None or date <= self.date_end))
