from django.urls import path
from .views import WeatherDataListCreate, WeatherDataRetrieveUpdateDestroy
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/api/weather/')),
    path('api/weather/', WeatherDataListCreate.as_view(), name='weather-list-create'),
    path('api/weather/<int:pk>/', WeatherDataRetrieveUpdateDestroy.as_view(), name='weather-detail')
]
