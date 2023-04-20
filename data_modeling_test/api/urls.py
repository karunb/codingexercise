from django.urls import re_path, path
from rest_framework import routers


from api import views

router = routers.DefaultRouter()


router.register(r"weather", views.WeatherDataAPIViewSet, basename="weather-data")

urlpatterns = [
    re_path(
        r"^weather/stats/", views.WeatherStatsAPIView.as_view(), name="weather-stats"
    ),
]

urlpatterns += router.urls
