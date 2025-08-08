from rest_framework import serializers
from .models import WeatherData

class WeatherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherData
        fields = [
            'id', 
            'city', 
            'temperature', 
            'feels_like',
            'pressure',
            'humidity', 
            'wind_speed', 
            'cloudiness', 
            'measured_at',
            'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_at']
