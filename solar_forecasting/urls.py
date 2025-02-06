from django.urls import include, path

urlpatterns = [
    path('users/', include('users.urls')),
    path('', include('forecast.urls')),
    path('', include('locations.urls'))
]

