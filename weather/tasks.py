from celery import shared_task
from .services import fetch_and_store_all_cities, send_weather_report_email
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

@shared_task(bind=True, max_retries=3)
def send_daily_report(self):
    try :
        dail_report_sent = send_weather_report_email(timeframe="Daily")
        if not dail_report_sent :
            return f"\nFailed to send daily report email"
        return f"Successfully sent daily report email"
    except Exception as exc:
        print(f"Error sending daily report mail : {str(exc)}")
        print(traceback.format_exc())