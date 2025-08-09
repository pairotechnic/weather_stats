import os
import requests
import traceback
from datetime import datetime, timezone
from django.conf import settings
from .models import WeatherData
from .redis_utils import get_redis_client
import json

def fetch_weather(city):
    '''
    Retrieves current weather from OpenWeatherMap API for WeatherData Model
    '''
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try :
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        measured_at = datetime.fromtimestamp(data["dt"], tz=timezone.utc)

        weather_obj = {
            "temperature" : data["main"]["temp"],
            "feels_like" : data["main"]["feels_like"],
            "pressure" : data["main"]["pressure"],
            "humidity" : data["main"]["humidity"],
            "wind_speed" : data["wind"]["speed"],
            "cloudiness" : data["clouds"]["all"],
            "measured_at" : measured_at,
            "city" : data["name"],
            "success" : True
        }

        print(f"Retrieved weather successfully for {city}")
        print(json.dumps(weather_obj, indent=4, default=str))

        return weather_obj
    
    except Exception as e:
        print(f"Error fetching weather for {city} : {str(e)}")
        print(traceback.format_exc())
        return {
            "success" : False,
            "error" : str(e)
        }
    
def fetch_and_store_all_cities():
    cities = [
        "Bangkok", "Istanbul", "London", "Hong Kong", 
        "Paris", "Dubai", "Singapore", "Tokyo",
        "New York", "Barcelona"
    ]

    updated_cities = []

    redis_client = get_redis_client()

    for city in cities:
        weather_data = fetch_weather(city)

        if not weather_data["success"]:
            print("Failed to fetch weather for {city}. Continuing...")
            continue

        redis_key = f"{city}_weather_last_updated_at"
        last_timestamp = redis_client.get(redis_key)

        if last_timestamp :
            last_measured_at = datetime.fromisoformat(last_timestamp)
            if weather_data["measured_at"] <= last_measured_at:
                print(f"Data hasn't been refreshed for {city}. Continuing...")
                continue
        else :
            # Fallback to database query if Redis is empty ( happens for the very first query, and will happen again if that redis key is deleted )
            last_record = WeatherData.objects.filter(city=city).order_by('-measured_at').first()
            if last_record and weather_data["measured_at"] <= last_record.measured_at:
                print(f"Redis key missing, and data hasn't been refreshed for {city}. Continuing...")
                continue
        
        # Create record and update redis
        print(f"New data detected for {city}! Saving to DB...") 
        WeatherData.objects.create(
            city=weather_data["city"],
            temperature=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            pressure=weather_data["pressure"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            cloudiness=weather_data["cloudiness"],
            measured_at=weather_data["measured_at"]
        )
        redis_client.set(redis_key, weather_data["measured_at"].isoformat())
        updated_cities.append(city)

    return updated_cities