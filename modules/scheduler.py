"""
Scheduled tasks for weather alerts and notifications.
Runs daily to send emails to users about rainy cities.
"""
import os
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
import logging
from modules.database import User, Favorite, db
from modules.weather_app import (
    fetch_daily_forecast,
    normalize_forecast,
    send_favorite_cities_weather_alert,
    DEFAULT_LAT,
    DEFAULT_LON,
)

logger = logging.getLogger(__name__)

def send_daily_weather_alerts():
    """
    Daily task: for each user with favorites, check weather alerts (rain and freeze)
    and send email alert with list of cities with rain or freeze.
    Called once per day at configured time (default: 06:00 AM).
    """
    print("\n🔔 [SCHEDULER] Starting daily weather alert check...")
    
    try:
        # Get all users
        users = User.query.all()
        alerts_sent = 0
        
        for user in users:
            try:
                # Get user's favorite cities
                favs = Favorite.get_for_user(user.id)
                
                if not favs:
                    continue  # Skip if no favorites
                
                rainy_cities = []
                cold_cities = []
                snowy_cities = []
                
                # Check weather for each favorite city
                for fav in favs:
                    try:
                        lat = fav.lat if fav.lat else DEFAULT_LAT
                        lon = fav.lon if fav.lon else DEFAULT_LON
                        
                        raw = fetch_daily_forecast(lat, lon, cnt=7, units="metric")
                        data = normalize_forecast(raw)
                        
                        # Check if rain today (first day in forecast)
                        if data["days"] and data["days"][0].get("precip_mm", 0) > 0 or data["days"][0].get("snow_mm", 0) > 0:
                            rainy_cities.append(fav.city)
                        
                        # Check if snow today (first day in forecast)
                        if data["days"] and data["days"][0].get("snow_mm", 0) > 0:
                            snowy_cities.append(fav.city)
                    except Exception as e:
                        logger.error(f"Error checking forecast for {fav.city}: {e}")
                        continue
                
                # Send email if there are any alerts
                if rainy_cities or cold_cities or snowy_cities:
                    try:
                        send_favorite_cities_weather_alert(user.email, rainy_cities, cold_cities, snowy_cities)
                        alerts_sent += 1
                        alert_types = []
                        if rainy_cities:
                            alert_types.append(f"rain in {len(rainy_cities)} cities")
                        if snowy_cities:
                            alert_types.append(f"snow in {len(snowy_cities)} cities")
                        if cold_cities:
                            alert_types.append(f"freeze in {len(cold_cities)} cities")
                        logger.info(f"✓ Alert sent to {user.email} for {', '.join(alert_types)}")
                    except Exception as e:
                        logger.error(f"Error sending alert to {user.email}: {e}")
                        
            except Exception as e:
                logger.error(f"Error processing user {user.id}: {e}")
                continue
        
        print(f"✓ Daily alert check completed. Alerts sent: {alerts_sent}\n")
        
    except Exception as e:
        logger.error(f"Fatal error in send_daily_weather_alerts: {e}")
        print(f"✗ Fatal error in scheduler: {e}\n")

scheduler = None

def init_scheduler(app):
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
    
    # Configure to use Flask app context
    def job_with_context():
        with app.app_context():
            send_daily_weather_alerts()
    
    # Schedule daily task at 06:00 AM
    scheduler.add_job(
        func=job_with_context,
        trigger="cron",
        hour=14,
        minute=21,
        second=00,
        id="daily_weather_alerts",
        name="Daily weather alerts for favorite cities (rain and freeze)",
        replace_existing=True,
        timezone="Europe/Warsaw",  # Poland timezone; adjust if needed
    )
    
    try:
        scheduler.start()
        logger.info("✓ Scheduler started successfully")
        print("✓ Background scheduler initialized (daily alerts at 06:00 AM)")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        print(f"✗ Failed to start scheduler: {e}")
    
    return scheduler
