from django.urls import path
from .views import WeatherDataListCreate, WeatherDataRetrieveUpdateDestroy

urlpatterns = [
    path('api/weather/', WeatherDataListCreate.as_view(), name='weather-list-create'),
    path('api/weather/<int:pk>/', WeatherDataRetrieveUpdateDestroy.as_view(), name='weather-detail')
]
