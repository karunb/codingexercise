from django.db import models
from django.utils.translation import gettext_lazy as _


class WeatherHistory(models.Model):
    location = models.CharField(max_length=50)
    record_date = models.DateField()
    max_temp = models.SmallIntegerField()
    min_temp = models.SmallIntegerField()
    precipitation_amount = models.SmallIntegerField()
    created_at = models.DateTimeField(
        verbose_name=_("Created"),
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        unique_together = ("location", "record_date")


class WeatherAggregatedData(models.Model):
    location = models.CharField(max_length=50)
    year = models.SmallIntegerField()
    avg_max_temp = models.FloatField()
    avg_min_temp = models.FloatField()
    sum_precipitation_amount = models.FloatField()
    created_at = models.DateTimeField(
        verbose_name=_("Created"),
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        unique_together = ("location", "year")
