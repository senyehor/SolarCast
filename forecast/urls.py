from django.urls import path

from forecast.views import forecast_request_view, train_model_view
from locations.views import upload_generation_data

urlpatterns = [
    path('', forecast_request_view, name='forecast_main'),
    path('train-lstm/', train_model_view, name='train_lstm'),
]

