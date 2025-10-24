"""
Configuration settings for Advanced Product Price Tracker
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_PATH = "data/products.db"
DATABASE_URL = "sqlite:///data/products.db"

# Email Configuration
EMAIL_ENABLED = True
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "receiver@gmail.com")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your-bot-token-here")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your-chat-id-here")

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "credentials.json")

# Scraping Configuration
REQUEST_TIMEOUT = 10
RETRY_ATTEMPTS = 3
SLEEP_BETWEEN_REQUESTS = 2
MAX_CONCURRENT_REQUESTS = 10

# Scheduling Configuration
CHECK_INTERVAL_HOURS = 6  # Check prices every 6 hours

# Price Alert Configuration
ALERT_PERCENTAGE_DROP = 5  # Alert if price drops by 5% or more
DEFAULT_ALERT_PRICE = 0.0

# ML Configuration
ENABLE_PREDICTIONS = True
PREDICTION_HORIZON = 7  # days
MODEL_RETRAIN_DAYS = 7

# Dashboard Configuration
DASHBOARD_REFRESH_INTERVAL = 300  # seconds
CHART_THEME = "plotly_white"

# Multi-currency
BASE_CURRENCY = "USD"
SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY"]

# Proxy Configuration (optional)
USE_PROXIES = False
PROXY_LIST = []

# User Agent Configuration
ROTATE_USER_AGENTS = True
