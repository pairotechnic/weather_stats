from celery import shared_task
from .services import fetch_and_store_all_cities
from datetime import datetime, timezone
import traceback
from celery.exceptions import MaxRetriesExceededError

@shared_task(bind=True, max_retries=3)
def fetch_weather_data(self):
    try :
        fetch_and_store_all_cities()
        return f"Weather data fetched and processed for all cities - {datetime.now(timezone.utc)}"
    except Exception as exc:
        print(f"Error fetching or saving weather data : {str(exc)}")
        print(traceback.format_exc())