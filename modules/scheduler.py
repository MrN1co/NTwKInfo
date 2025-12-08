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
    send_favorite_cities_rain_alert,
    DEFAULT_LAT,
    DEFAULT_LON,
)

logger = logging.getLogger(__name__)

def send_daily_rain_alerts():
    """
    Daily task: for each user with favorites, check if it will rain today
    and send email alert with list of rainy cities.
    Called once per day at configured time (default: 08:00 AM).
    """
    print("\n🔔 [SCHEDULER] Starting daily rain alert check...")
    
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
                
                # Check weather for each favorite city
                for fav in favs:
                    try:
                        lat = fav.lat if fav.lat else DEFAULT_LAT
                        lon = fav.lon if fav.lon else DEFAULT_LON
                        
                        raw = fetch_daily_forecast(lat, lon, cnt=7, units="metric")
                        data = normalize_forecast(raw)
                        
                        # Check if rain today (first day in forecast)
                        if data["days"] and data["days"][0].get("precip_mm", 0) > 0:
                            rainy_cities.append(fav.city)
                    except Exception as e:
                        logger.error(f"Error checking forecast for {fav.city}: {e}")
                        continue
                
                # Send email if there are rainy cities
                if rainy_cities:
                    try:
                        send_favorite_cities_rain_alert(user.email, rainy_cities)
                        alerts_sent += 1
                        logger.info(f"✓ Alert sent to {user.email} for {len(rainy_cities)} cities")
                    except Exception as e:
                        logger.error(f"Error sending alert to {user.email}: {e}")
                        
            except Exception as e:
                logger.error(f"Error processing user {user.id}: {e}")
                continue
        
        print(f"✓ Daily alert check completed. Alerts sent: {alerts_sent}\n")
        
    except Exception as e:
        logger.error(f"Fatal error in send_daily_rain_alerts: {e}")
        print(f"✗ Fatal error in scheduler: {e}\n")


def init_scheduler(app):
    """
    Initialize the background scheduler for recurring tasks.
    Called once when app starts.
    """
    scheduler = BackgroundScheduler()
    
    # Configure to use Flask app context
    def job_with_context():
        with app.app_context():
            send_daily_rain_alerts()
    
    # Schedule daily task at 06:00 AM
    scheduler.add_job(
        func=job_with_context,
        trigger="cron",
        hour=6,
        minute=0,
        second=0,
        id="daily_rain_alerts",
        name="Daily rain alerts for favorite cities",
        replace_existing=True,
        timezone="Europe/Warsaw",  # Poland timezone; adjust if needed
    )
    
    try:
        scheduler.start()
        logger.info("✓ Scheduler started successfully")
        print("✓ Background scheduler initialized (daily alerts at 08:00 AM)")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        print(f"✗ Failed to start scheduler: {e}")
    
    return scheduler
