from rest_framework import generics, filters, status
from rest_framework.response import Response
from .models import WeatherData
from .serializers import WeatherDataSerializer
from django_filters import rest_framework as df_filters
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .services import fetch_weather

class WeatherDataFilter(df_filters.FilterSet):
    min_temperature = df_filters.NumberFilter(field_name="temperature", lookup_expr="gte")
    max_temperature = df_filters.NumberFilter(field_name="temperature", lookup_expr="lte")

    min_feels_like = df_filters.NumberFilter(field_name="feels_like", lookup_expr="gte")
    max_feels_like = df_filters.NumberFilter(field_name="feels_like", lookup_expr="lte")

    min_pressure = df_filters.NumberFilter(field_name="pressure", lookup_expr="gte")
    max_pressure = df_filters.NumberFilter(field_name="pressure", lookup_expr="lte")
    
    min_hum = df_filters.NumberFilter(field_name="humidity", lookup_expr="gte")
    max_hum = df_filters.NumberFilter(field_name="humidity", lookup_expr="lte")
    
    min_wind = df_filters.NumberFilter(field_name="wind_speed", lookup_expr="gte")
    max_wind = df_filters.NumberFilter(field_name="wind_speed", lookup_expr="lte")

    min_cloudiness = df_filters.NumberFilter(field_name="cloudiness", lookup_expr="gte")
    max_cloudiness = df_filters.NumberFilter(field_name="cloudiness", lookup_expr="lte")
    
    min_measured_at = df_filters.DateTimeFilter(field_name="measured_at", lookup_expr="gte")
    max_measured_at = df_filters.DateTimeFilter(field_name="measured_at", lookup_expr="lte")

    city = df_filters.CharFilter(field_name="city", lookup_expr="icontains")

    class Meta:
        model = WeatherData
        fields = []

class WeatherDataListCreate(generics.ListCreateAPIView):
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer
    filter_backends = [df_filters.DjangoFilterBackend]
    filterset_class = WeatherDataFilter

    # # Search partial string across multiple fields
    # # filter_backends = [df_filters.DjangoFilterBackend, filters.SearchFilter]
    # filter_backends.append(filters.SearchFilter)
    # search_fields = ['location', 'conditions']

class WeatherDataRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer
