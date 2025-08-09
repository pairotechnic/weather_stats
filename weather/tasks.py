from celery import shared_task
from .services import fetch_and_store_all_cities
from datetime import datetime, timezone
import traceback
from celery.exceptions import MaxRetriesExceededError
import json

@shared_task(bind=True, max_retries=3)
def fetch_weather_data(self):
    try :
        updated_cities = fetch_and_store_all_cities()
        if not updated_cities :
            return f"\nNo fresh data available for any city"
        return f"\nWeather data updated for the following cities - \n{json.dumps(updated_cities, indent=4)}"
    except Exception as exc:
        print(f"Error fetching or saving weather data : {str(exc)}")
        print(traceback.format_exc())