from django.urls import path

from locations.views import fetch_weather_view, upload_generation_data

urlpatterns = [
    path('upload/', upload_generation_data, name='upload_generation_data'),
    path('fetch-weather/', fetch_weather_view, name='fetch_weather'),
]

