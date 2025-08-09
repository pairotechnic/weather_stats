from django.db import models

class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    temperature = models.FloatField()
    feels_like = models.FloatField()
    pressure = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    cloudiness = models.FloatField()
    measured_at = models.DateTimeField() # When data was last updated by weather stations in city
    recorded_at = models.DateTimeField(auto_now_add=True)  # When entry was saved in db

    def __str__(self):
        return f"{self.city} - {self.temperature}°C at {self.measured_at}"
    
    class Meta:
        ordering = ["-measured_at"]
