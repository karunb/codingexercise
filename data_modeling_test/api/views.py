import datetime
import logging
import time
from django.db.models.functions import ExtractYear
from django.db.models import Count, Avg, Sum
from django.db.models import Q

from rest_framework import mixins, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import (
    WeatherHistorySerializer,
    WeatherAggregatedDataSerializer,
    StatsSerializer,
)
from api.models import WeatherHistory, WeatherAggregatedData


logger = logging.getLogger(__name__)


class WeatherDataAPIViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WeatherHistorySerializer
    model = WeatherHistory
    queryset = WeatherHistory.objects.all()

    def get_queryset(self):
        params = self.request.GET
        filter_q = Q()
        if params.get("start_date"):
            filter_q &= Q(record_date__gte=params["start_date"])
        if params.get("end_date"):
            filter_q &= Q(record_date__lte=params["end_date"])

        if params.get("location"):
            filter_q &= Q(location=params["location"])

        return self.model.objects.filter(filter_q)

    @swagger_auto_schema(
        operation_summary="Retrieve Raw Data",
        query_serializer=StatsSerializer,
    )
    def list(self, request, *args, **kwargs):
        """
        Get list of uploaded records from database.
        This can be filtered by start date / end date and location
        """
        serializer = StatsSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Upload File Data",
        request_body=openapi.Schema(
            type="object",
            properties={"file": openapi.Schema(type="string", format="binary")},
        ),
    )
    def create(self, request):
        """
        Ask user to upload file. This will create a logs/records in database
        """
        file_obj = request.FILES["file"]
        location, _ = file_obj.name.split(".")

        start_time = time.time()

        for line in file_obj:
            _record = line.decode("utf-8").split("\t")
            _record = [s.strip() for s in _record]
            record = {
                "location": location,
                "record_date": datetime.datetime.strptime(
                    _record[0], "%Y%m%d"
                ).strftime("%Y-%m-%d"),
                "max_temp": _record[1],
                "min_temp": _record[2],
                "precipitation_amount": _record[3],
            }
            # data.append(record)
            serializer = self.serializer_class(data=record)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        end_time = time.time()

        logger.info(
            "Time to execute files: %s minutes"
            % (round((end_time - start_time) / 60, 2))
        )

        return Response(
            {"success": True, "message": "Records are created."},
            status=status.HTTP_201_CREATED,
        )


class WeatherStatsAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve Stats Data",
        query_serializer=StatsSerializer,
    )
    def get(self, request, *args, **kwargs):
        """
        This will aggregate data by location and year and will store in different table
        """
        serializer = StatsSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        filter_q = Q()
        if params.get("start_date"):
            filter_q &= Q(record_date__gte=params["start_date"])
        if params.get("end_date"):
            filter_q &= Q(record_date__lte=params["end_date"])

        if params.get("location"):
            filter_q &= Q(location=params["location"])

        queryset = (
            WeatherHistory.objects.filter(filter_q)
            .exclude(Q(max_temp=-9999) | Q(min_temp=-9999))
            .annotate(year=ExtractYear("record_date"))
            .values("location", "year")
            .annotate(
                avg_max_temp=Avg("max_temp"),
                avg_min_temp=Avg("min_temp"),
                sum_precipitation_amount=Sum("precipitation_amount"),
            )
        )

        for result in queryset:
            serializer = WeatherAggregatedDataSerializer(data=result)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({"results": queryset}, status=status.HTTP_200_OK)
