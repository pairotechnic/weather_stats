import os
import requests
import traceback
from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone as django_timezone
from django.conf import settings
from .models import WeatherData
from .redis_utils import get_redis_client
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.db.models import Avg, Max, Min, Count
from django.template.loader import render_to_string

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

        measured_at = datetime.fromtimestamp(data["dt"], tz=dt_timezone.utc)

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
            print(f"Redis key missing for {city}")
            # Fallback to database query if Redis is empty ( happens for the very first query, and will happen again if that redis key is deleted )
            last_record = WeatherData.objects.filter(city=city).order_by('-measured_at').first()
            if last_record and weather_data["measured_at"] <= last_record.measured_at:
                print(f"Also, data hasn't been refreshed for {city}. Continuing...")
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

def send_email(subject, body, html_body=None):
    # Email configuration
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')  # sender's gmail app password
    receiver_email = "rohitkalsankpai@gmail.com"

    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    # Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls() # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email : {str(e)}")
        print(traceback.format_exc())

def send_weather_report_email(timeframe="Daily"):
    '''
        Sends out an email to the recipient/s
        Contains weather info and statistics of each city, along with aggregate statistics
        Timeframe will be passed as a parameter -> daily, weekly, monthly
    '''
    subject = f"{timeframe} Weather Report"
    current_time = django_timezone.now()
    print(f"Current time : {str(current_time)}")

    match timeframe:
        case "Daily":
            measure_duration = "24 hours"
            measure_from = current_time - timedelta(hours=24)
        case "Weekly":
            measure_duration = "7 days"
            measure_from = current_time - timedelta(days=7)
        case "Monthly":
            measure_duration = "30 days"
            measure_from = current_time - timedelta(days=30)
        case _:
            measure_duration = "24 hours"
            measure_from = current_time - timedelta(hours=24)

    print(f"Measure Duration : {measure_duration}")
    print(f"Measure From : {measure_from}")

    # Get all cities
    cities = sorted(set(WeatherData.objects.values_list('city', flat=True)))
    print(f"cities : {cities}")
    print(f"list(cities) : {list(cities)}")
    print(f"sorted(set(cities)) : {sorted(set(cities))}")

    body = f"{timeframe} Weather Report - Last {measure_duration}\n\n"
    body += "=" * 60 + "\n\n"

    city_stats = []
    for city in cities:
        city_data = WeatherData.objects.filter(
            city=city,
            measured_at__gte=measure_from
        )

        if not city_data.exists():
            city_stats.append({
                "name" : city,
                "readings_count" : 0
            })
            body += f"{city}: No data available\n"
            body += "-" * 40 + "\n\n"
            print(f"{city}: No data available\n")
            continue

        stats = city_data.aggregate(

            avg_temperature = Avg('temperature'),
            min_temperature = Min('temperature'),
            max_temperature = Max('temperature'),

            avg_humidity = Avg('humidity'),
            min_humidity = Min('humidity'),
            max_humidity = Max('humidity'),

            avg_wind_speed = Avg('wind_speed'),
            min_wind_speed = Min('wind_speed'),
            max_wind_speed = Max('wind_speed'),

            avg_cloudiness = Avg('cloudiness'),
            min_cloudiness = Min('cloudiness'),
            max_cloudiness = Max('cloudiness'),

            avg_feels_like = Avg('feels_like'),
            min_feels_like = Min('feels_like'),
            max_feels_like = Max('feels_like'),

            avg_pressure = Avg('pressure'),
            min_pressure = Min('pressure'),
            max_pressure = Max('pressure'),

            readings_count = Count('id')

        )

        print(f"{city}: Aggregate Data\n")
        print(json.dumps(stats, indent=4, default=str))

        # Add to plain text body
        body += f"🌤️ {city}:\n\n"
        body += f"   Temperature:\tAvg: {stats['avg_temperature']:.1f}°C,\tMax: {stats['max_temperature']:.1f}°C,\tMin: {stats['min_temperature']:.1f}°C\n"
        body += f"   Humidity:\tAvg: {stats['avg_humidity']:.1f}%,\tMax: {stats['max_humidity']:.1f}%,\tMin: {stats['min_humidity']:.1f}%\n"
        body += f"   Wind Speed:\tAvg: {stats['avg_wind_speed']:.1f} m/s\tMax: {stats['max_wind_speed']:.1f}\tMin: {stats['min_wind_speed']:.1f}\n"
        body += f"   Cloudiness:\tAvg: {stats['avg_cloudiness']:.1f}%\tMax: {stats['max_cloudiness']:.1f}%\tMin: {stats['min_cloudiness']:.1f}%\n"
        body += f"   Pressure:\tAvg: {stats['avg_pressure']:.1f} hPa\tMax: {stats['max_pressure']:.1f} hPa\tMin: {stats['min_pressure']:.1f} hPa\n"
        body += f"   Feels Like:\tAvg: {stats['avg_feels_like']:.1f}°C\tMax: {stats['max_feels_like']:.1f}°C\tMin: {stats['min_feels_like']:.1f}°C\n"
        body += f"   Readings:\t{stats['readings_count']}\n"
        body += "-" * 40 + "\n\n"

        each_city_stats = {
            "name" : city
        }
        each_city_stats.update(stats)
        city_stats.append(each_city_stats)

        print(f"{city} : Each city stats")
        print(json.dumps(city_stats, indent=4, default=str))

    # Overall statistics
    all_data = WeatherData.objects.filter(measured_at__gte=measure_from)

    overall_stats = all_data.aggregate(
        avg_temperature = Avg('temperature'),
        min_temperature = Min('temperature'),
        max_temperature = Max('temperature'),

        avg_humidity = Avg('humidity'),
        min_humidity = Min('humidity'),
        max_humidity = Max('humidity'),

        avg_wind_speed = Avg('wind_speed'),
        min_wind_speed = Min('wind_speed'),
        max_wind_speed = Max('wind_speed'),

        avg_cloudiness = Avg('cloudiness'),
        min_cloudiness = Min('cloudiness'),
        max_cloudiness = Max('cloudiness'),

        avg_feels_like = Avg('feels_like'),
        min_feels_like = Min('feels_like'),
        max_feels_like = Max('feels_like'),

        avg_pressure = Avg('pressure'),
        min_pressure = Min('pressure'),
        max_pressure = Max('pressure'),

        readings_count = Count('id')

    ) if all_data.exists() else {"readings_count" : 0}

    # Add summary to plain text body
    if overall_stats['readings_count'] > 0:
        body += f"\n📈 Across all cities:\n\n"

        body += f"   Temperature:\tAvg: {overall_stats['avg_temperature']:.1f}°C,\tMax: {overall_stats['max_temperature']:.1f}°C,\tMin: {overall_stats['min_temperature']:.1f}°C\n"
        body += f"   Humidity:\tAvg: {overall_stats['avg_humidity']:.1f}%,\tMax: {overall_stats['max_humidity']:.1f}%,\tMin: {overall_stats['min_humidity']:.1f}%\n"
        body += f"   Wind Speed:\tAvg: {overall_stats['avg_wind_speed']:.1f} m/s\tMax: {overall_stats['max_wind_speed']:.1f}\tMin: {overall_stats['min_wind_speed']:.1f}\n"
        body += f"   Cloudiness:\tAvg: {overall_stats['avg_cloudiness']:.1f}%\tMax: {overall_stats['max_cloudiness']:.1f}%\tMin: {overall_stats['min_cloudiness']:.1f}%\n"
        body += f"   Pressure:\tAvg: {overall_stats['avg_pressure']:.1f} hPa\tMax: {overall_stats['max_pressure']:.1f} hPa\tMin: {overall_stats['min_pressure']:.1f} hPa\n"
        body += f"   Feels Like:\tAvg: {overall_stats['avg_feels_like']:.1f}°C\tMax: {overall_stats['max_feels_like']:.1f}°C\tMin: {overall_stats['min_feels_like']:.1f}°C\n"
        body += f"   Readings:\t{overall_stats['readings_count']}\n"

    print(f"Overall stats")
    print(json.dumps(overall_stats, indent=4, default=str))

    email_sent = send_email(subject, body)
    return email_sent