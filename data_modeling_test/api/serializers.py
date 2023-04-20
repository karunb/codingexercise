from rest_framework import serializers

from api.models import WeatherHistory, WeatherAggregatedData


class WeatherHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherHistory
        fields = "__all__"
        unique_together = ("location", "record_date")

    def is_valid(self, *, raise_exception=False):
        # Disable unique validation
        self.validators = [
            v
            for v in self.validators
            if not isinstance(v, serializers.UniqueTogetherValidator)
        ]
        return super().is_valid(raise_exception=raise_exception)

    def save(self, **kwargs):
        WeatherHistory.objects.get_or_create(
            location=self.validated_data["location"],
            record_date=self.validated_data["record_date"],
            defaults={
                "max_temp": self.validated_data["max_temp"],
                "min_temp": self.validated_data["min_temp"],
                "precipitation_amount": self.validated_data["precipitation_amount"],
            },
        )


class WeatherAggregatedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherAggregatedData
        fields = "__all__"
        unique_together = ("location", "year")

    def is_valid(self, *, raise_exception=False):
        # Disable unique validation
        self.validators = [
            v
            for v in self.validators
            if not isinstance(v, serializers.UniqueTogetherValidator)
        ]
        return super().is_valid(raise_exception=raise_exception)

    def save(self, **kwargs):
        WeatherAggregatedData.objects.get_or_create(
            location=self.validated_data["location"],
            year=self.validated_data["year"],
            defaults={
                "avg_max_temp": self.validated_data["avg_max_temp"],
                "avg_min_temp": self.validated_data["avg_min_temp"],
                "sum_precipitation_amount": self.validated_data[
                    "sum_precipitation_amount"
                ],
            },
        )


class StatsSerializer(serializers.Serializer):
    start_date = serializers.DateField(
        format="%Y-%m-%d",
        help_text="Start Date",
        required=False,
    )
    end_date = serializers.DateField(
        format="%Y-%m-%d",
        help_text="End Date",
        required=False,
    )
    location = serializers.CharField(
        help_text="Location",
        required=False,
    )
