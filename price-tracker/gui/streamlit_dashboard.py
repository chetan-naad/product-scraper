import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sys
import os
import json
import hashlib

# --- Page Configuration ---
st.set_page_config(
    page_title="Price Tracker",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced Professional Styling ---
st.markdown("""
<style>
    /* Dark Navy Background - Clean like FlowTrack */
    body, .main, .stApp {
        background: #0a1929;
        background-attachment: fixed;
    }
    
    /* Subtle Grid Pattern - Dark */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(30, 58, 95, 0.12) 1px, transparent 1px),
            linear-gradient(90deg, rgba(30, 58, 95, 0.12) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 20% 50%, rgba(25, 118, 210, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(33, 150, 243, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    h1, h2, h3, h4, h5 {
        color: #ffffff;
        font-family: 'Nunito', 'Segoe UI', Arial;
        text-shadow: 0 2px 12px rgba(25, 118, 210, 0.3);
        font-weight: 700;
    }
    
    .big-metric {
        font-size: 2.5rem;
        font-weight: 900;
        color: #ffffff;
        text-shadow: 0 2px 8px rgba(33, 150, 243, 0.5);
    }
    
    /* Glass morphism cards with visible borders like FlowTrack */
    .metric-card {
        background: rgba(15, 31, 51, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        margin: 6px 0px 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        padding: 20px;
        border: 2px solid rgba(30, 58, 95, 0.6);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 16px;
        border: 1px solid rgba(33, 150, 243, 0.2);
        pointer-events: none;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(25, 118, 210, 0.5);
        background: rgba(19, 47, 76, 0.7);
        border-color: rgba(33, 150, 243, 0.8);
    }
    
    .section-card {
        background: rgba(15, 31, 51, 0.4);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-top: 16px;
        padding: 24px;
        border: 2px solid rgba(30, 58, 95, 0.5);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #142743 0%, #19446e 100%);
        color: #fff;
        border-radius: 22px;
        font-size: 1rem;
        padding: 10px 32px;
        font-weight: 700;
        border: 2px solid #233f5e;
        box-shadow: 0 4px 16px rgba(10, 25, 41, 0.25);
        margin-bottom: 6px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #19446e 0%, #2196f3 100%);
        color: #fff;
        border-color: #2196f3;
        box-shadow: 0 6px 22px rgba(33, 150, 243, 0.38);
        transform: translateY(-2px) scale(1.04);
    }
    
    .stButton > button:active {
        background: #142743;
        border-color: #132f4c;
        color: #b0bec5;
        box-shadow: 0 3px 10px rgba(33, 150, 243, 0.22);
        transform: scale(0.98);
    }
    
    /* For prominent or "primary" actions */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #19446e 0%, #2196f3 100%);
        border-color: #2196f3;
    }
    
    /* Dark Input fields with borders */
    .stTextInput input, .stNumberInput input {
        border-radius: 12px !important; 
        border: 2px solid rgba(30, 58, 95, 0.7) !important;
        font-weight: 600; 
        background: rgba(15, 31, 51, 0.6) !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        color: #ffffff !important;
        padding: 12px 16px !important;
    }
    
    /* Light Gray Placeholder */
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {
        color: #78909c !important;
        opacity: 1 !important;
        font-weight: 500 !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        background: rgba(19, 47, 76, 0.8) !important;
        border-color: #2196f3 !important;
        box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.25);
        color: #ffffff !important;
    }
    
    /* Select boxes with borders */
    .stSelectbox > div > div {
        background: rgba(15, 31, 51, 0.6) !important;
        border-radius: 12px;
        border: 2px solid rgba(30, 58, 95, 0.7) !important;
        color: #ffffff !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #2196f3 !important;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background: rgba(15, 31, 51, 0.6) !important;
        border: 2px solid rgba(30, 58, 95, 0.7) !important;
        border-radius: 12px;
    }
    
    /* Data tables */
    .stDataFrame, .dataframe {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 13px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 8px;
        border: 1px solid rgba(30, 58, 95, 0.3);
    }
    
    /* Dark Navy Sidebar with Grid Pattern */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1929 0%, #0f1f33 50%, #132f4c 100%);
        background-attachment: fixed;
        border-right: 2px solid rgba(30, 58, 95, 0.7);
        box-shadow: 2px 0 20px rgba(0, 0, 0, 0.4);
        padding: 2.2rem 1.2rem 1.2rem 1.2rem;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stSidebar"] .stMetric {
        background: rgba(25, 118, 210, 0.12);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 2px solid rgba(30, 58, 95, 0.6);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(90deg, #1976d2 0%, #2196f3 100%);
        font-weight: 700;
        color: #ffffff;
        border: none;
        border-radius: 25px;
        box-shadow: 0 3px 12px rgba(25, 118, 210, 0.4);
        margin-top: 0.7rem;
        padding: 10px 24px;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(90deg, #42a5f5 0%, #2196f3 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 18px rgba(33, 150, 243, 0.6);
    }
    
    [data-testid="stSidebar"] .stCaption {
        color: #b0bec5 !important;
    }
    
    /* Labels */
    .stSelectbox label, .stRadio label, .stCheckbox label, .stMultiSelect label {
        color: #b0bec5 !important;
        font-weight: 700;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    /* Notification boxes with borders */
    .stSuccess {
        background: rgba(16, 185, 129, 0.15) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid #10b981 !important;
        border: 2px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px;
        font-weight: 600;
        color: white !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.15) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid #f44336 !important;
        border: 2px solid rgba(244, 67, 54, 0.3) !important;
        border-radius: 12px;
        font-weight: 600;
        color: white !important;
        box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
    }
    
    .stInfo {
        background: rgba(33, 150, 243, 0.15) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid #2196f3 !important;
        border: 2px solid rgba(33, 150, 243, 0.3) !important;
        border-radius: 12px;
        font-weight: 500;
        color: white !important;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
    }
    
    .stWarning {
        background: rgba(255, 152, 0, 0.15) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid #ff9800 !important;
        border: 2px solid rgba(255, 152, 0, 0.3) !important;
        border-radius: 12px;
        font-weight: 600;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
    }
    
    /* Expander with border */
    .streamlit-expanderHeader {
        background: rgba(15, 31, 51, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 2px solid rgba(30, 58, 95, 0.6);
        color: white !important;
        font-weight: 600;
    }
    
    /* Tabs with borders */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(15, 31, 51, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        color: #78909c;
        font-weight: 600;
        padding: 12px 24px;
        border: 2px solid rgba(30, 58, 95, 0.5);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1976d2 0%, #2196f3 100%);
        border: 2px solid rgba(33, 150, 243, 0.6);
        color: white;
    }
    
    /* Slider */
    .stSlider label {
        color: #b0bec5 !important;
        font-weight: 600;
    }
    
    /* Radio buttons with borders */
    .stRadio > div {
        background: rgba(15, 31, 51, 0.4);
        padding: 0.7rem;
        border-radius: 12px;
        border: 2px solid rgba(30, 58, 95, 0.4);
    }
    
    /* User avatar */
    .user-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1976d2, #2196f3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        box-shadow: 0 4px 16px rgba(25, 118, 210, 0.6);
        margin: 0 auto;
        border: 3px solid rgba(33, 150, 243, 0.4);
    }
    
    /* Badge - Rounded Pills */
    .badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0 4px;
        border: 2px solid;
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border-color: #10b981;
    }
    
    .badge-danger {
        background: rgba(244, 67, 54, 0.15);
        color: #f44336;
        border-color: #f44336;
    }
    
    .badge-warning {
        background: rgba(255, 152, 0, 0.15);
        color: #ff9800;
        border-color: #ff9800;
    }
    
    .badge-info {
        background: rgba(0, 188, 212, 0.15);
        color: #00bcd4;
        border-color: #00bcd4;
    }
</style>
""", unsafe_allow_html=True)

# --- Utility Functions ---
def format_price(amount, currency='INR'):
    """Format price with currency symbol - always requires currency parameter"""
    symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}
    symbol = symbols.get(currency, '₹')
    try:
        amt = float(amount) if amount else 0
    except:
        amt = 0
    return f"{symbol}{amt:.2f}"


def load_settings():
    try:
        with open('data/settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'email_address': 'user@example.com',
            'telegram_token': '',
            'telegram_enabled': False,
            'alert_freq': 6,
            'price_threshold': 10,
            'username': 'pricetracker_user',
            'currency': 'INR',
            'timezone': 'IST'
        }

def save_settings(settings):
    os.makedirs('data', exist_ok=True)
    with open('data/settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

def get_user_initials(name):
    """Get user initials for avatar"""
    if not name:
        return "U"
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return name[0].upper()

    # --- INSTANT ALERT FUNCTIONS ---
import smtplib
from email.mime.text import MIMEText
import requests

def send_email_notification(to_email, subject, body):
    """Send email alert using the proper notifier"""
    try:
        if backend_available and 'notifier' in st.session_state:
            # Use the proper notifier from the backend
            product_info = {
                'name': subject.replace('🚨 Price Alert: ', ''),
                'new_price': 0,  # Will be filled by the calling function
                'old_price': 0,
                'url': '',
                'site': 'Unknown'
            }
            
            # Create a custom email message
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = st.session_state.notifier.sender_email
            msg["To"] = to_email
            
            # Create both text and HTML versions
            text_part = MIMEText(body, "plain")
            html_part = MIMEText(st.session_state.notifier._create_html_body(product_info), "html")
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send using the notifier's SMTP settings
            with smtplib.SMTP(st.session_state.notifier.smtp_server, st.session_state.notifier.smtp_port) as server:
                server.starttls()
                server.login(st.session_state.notifier.sender_email, st.session_state.notifier.sender_password)
                server.sendmail(st.session_state.notifier.sender_email, to_email, msg.as_string())
            
            print("✅ Email sent via notifier")
        else:
            # Fallback to simple email
            from_email = "naadchetan@gmail.com"
            password = "your_gmail_app_password"  # Replace with your actual app password
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()
            print("✅ Email sent via fallback")
    except Exception as e:
        print(f"❌ Email error: {e}")

def send_telegram_notification(bot_token, chat_id, message):
    """Send Telegram alert"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Telegram sent")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def send_price_alert(product_name, current_price, alert_price, product_url, currency='INR'):
    """Send instant alert when price below threshold"""
    settings = load_settings()
    currency_symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}
    symbol = currency_symbols.get(currency, '₹')
    
    # Calculate savings
    savings = alert_price - current_price
    savings_pct = (savings / alert_price) * 100 if alert_price > 0 else 0
    
    # Email
    email_address = settings.get('email_address', 'user@example.com')
    subject = f"🚨 INSTANT ALERT: {product_name} - Price Below Target!"
    
    # Create proper product_info for the notifier
    product_info = {
        'name': product_name,
        'new_price': current_price,
        'old_price': alert_price,  # Using alert_price as "old_price" for comparison
        'url': product_url,
        'site': 'Price Tracker',
        'price_change': -savings_pct,  # Negative because it's a drop
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        # Use the proper notifier for HTML email
        if backend_available and 'notifier' in st.session_state:
            # Create custom HTML email for instant alert
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .price-box {{ background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #ffc107; }}
        .price-current {{ font-size: 32px; font-weight: bold; color: #28a745; }}
        .price-alert {{ font-size: 20px; color: #6c757d; }}
        .savings {{ font-size: 24px; color: #dc3545; font-weight: bold; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: bold; }}
        .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; color: #6c757d; font-size: 12px; }}
        .alert-badge {{ background: #dc3545; color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 INSTANT PRICE ALERT! 🚨</h1>
            <p>This product is already below your target price!</p>
            <span class="alert-badge">DON'T MISS THIS DEAL!</span>
        </div>

        <div class="content">
            <h2 style="color: #333; margin-bottom: 20px;">{product_name}</h2>

            <div class="price-box">
                <div style="text-align: center;">
                    <div class="price-current">{symbol}{current_price:.2f}</div>
                    <div style="font-size: 16px; color: #6c757d; margin-top: 5px;">Current Price</div>
                </div>

                <div style="text-align: center; margin-top: 15px;">
                    <div class="price-alert">{symbol}{alert_price:.2f}</div>
                    <div style="font-size: 14px; color: #6c757d;">Your Alert Price</div>
                </div>

                <div style="text-align: center; margin-top: 20px;">
                    <div class="savings">💰 You Save: {symbol}{savings:.2f} ({savings_pct:.1f}% OFF!)</div>
                </div>
            </div>

            <p style="font-size: 18px; text-align: center; color: #dc3545; font-weight: bold;">
                ⚡ This product is already below your target price!<br>
                🏃‍♂️ Don't miss this deal - act fast!
            </p>

            <div style="text-align: center;">
                <a href="{product_url}" class="button">
                    🛍️ View Product Now
                </a>
            </div>
        </div>

        <div class="footer">
            <p>This is an automated instant alert from your Price Tracker Pro</p>
            <p>🤖 Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Create message
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = st.session_state.notifier.sender_email
            msg["To"] = email_address
            
            # Create both text and HTML versions
            text_message = f"""🚨 INSTANT PRICE ALERT! 🚨

Product: {product_name}
Current Price: {symbol}{current_price:.2f}
Your Alert Price: {symbol}{alert_price:.2f}
You Save: {symbol}{savings:.2f} ({savings_pct:.1f}% OFF!)

This product is already below your target price!
Don't miss this deal - act fast!

View Product: {product_url}

---
🤖 Price Tracker Pro - Instant Alert System
Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            text_part = MIMEText(text_message, "plain")
            html_part = MIMEText(html_body, "html")
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send using the notifier's SMTP settings
            with smtplib.SMTP(st.session_state.notifier.smtp_server, st.session_state.notifier.smtp_port) as server:
                server.starttls()
                server.login(st.session_state.notifier.sender_email, st.session_state.notifier.sender_password)
                server.sendmail(st.session_state.notifier.sender_email, email_address, msg.as_string())
            
            print(f"✅ Instant email alert sent for {product_name}")
        else:
            # Fallback to simple email
            send_email_notification(email_address, subject, text_message)
            print(f"✅ Instant email alert sent for {product_name}")
    except Exception as e:
        print(f"❌ Email alert failed: {e}")
    
    # Telegram
    bot_token = settings.get('telegram_token', '')
    chat_id = settings.get('telegram_chat_id', '1934728827')  # Use from settings
    
    if bot_token and chat_id:
        telegram_msg = f"""🚨 *INSTANT PRICE ALERT!* 🚨

*{product_name}*
💰 Current: {symbol}{current_price:.2f}
🎯 Target: {symbol}{alert_price:.2f}
💵 You Save: {symbol}{savings:.2f} ({savings_pct:.1f}% OFF!)

This product is already below your target price!
Don't miss this deal - act fast!

[View Product]({product_url})

---
🤖 *Price Tracker Pro - Instant Alert*
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        try:
            send_telegram_notification(bot_token, chat_id, telegram_msg)
            print(f"✅ Instant Telegram alert sent for {product_name}")
        except Exception as e:
            print(f"❌ Telegram alert failed: {e}")
    else:
        print("⚠️ Telegram not configured - skipping Telegram alert")


# --- Backend Initialization ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from utils.database import DatabaseManager
    from utils.notifier import EmailNotifier
    from scraper.product_scraper import ProductScraper
    backend_available = True
except ImportError as e:
    st.error(f"Backend import error: {e}")
    backend_available = False

if backend_available:
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager("data/products.db")
    if 'notifier' not in st.session_state:
        st.session_state.notifier = EmailNotifier()
    if 'scraper' not in st.session_state:
        st.session_state.scraper = ProductScraper()

# --- Sidebar ---
with st.sidebar:
    # User Profile
    settings = load_settings()
    username = settings.get('username', 'User')
    
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 24px;'>
            <div class='user-avatar'>{get_user_initials(username)}</div>
            <h3 style='margin-top: 12px;'>@{username}</h3>
            <p style='font-size: 0.85rem; opacity: 0.8;'>{settings.get('email_address', '')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("<h2 style='text-align:center;'>🛒 Price Tracker Pro</h2>", unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📦 Products", "📈 Analytics", "🤖 AI Predictions", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.subheader("Quick Stats")
    if backend_available:
        analytics = st.session_state.db.get_analytics_data()
        st.metric("Tracked Products", analytics.get('total_products', 0))
        st.metric("Active Alerts", analytics.get('active_alerts', 0))
        st.metric("Avg Price", format_price(analytics.get('avg_price', 0)))
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Refresh Data"):
        st.rerun()

# --- Main Page ---
if page == "📊 Dashboard":
    st.markdown("<h1>📊 Price Tracking Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-card'><h3>Welcome back, {username}! 👋</h3><p>Here's your price tracking overview</p></div>", unsafe_allow_html=True)
    
    if not backend_available:
        st.error("⚠️ Backend modules not available. Check imports.")
    else:
        analytics = st.session_state.db.get_analytics_data()
        best_deals = st.session_state.db.get_best_deals(limit=5)
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='metric-card'><h4>🛍️ Products</h4><div class='big-metric'>{analytics.get('total_products', 0)}</div><span class='badge badge-info'>Active</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><h4>💰 Avg Price</h4><div class='big-metric'>{format_price(analytics.get('avg_price', 0))}</div><span class='badge badge-success'>Updated</span></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'><h4>📉 Alerts</h4><div class='big-metric'>{analytics.get('active_alerts', 0)}</div><span class='badge badge-warning'>Watching</span></div>", unsafe_allow_html=True)
        with col4:
            if best_deals:
                st.markdown(f"<div class='metric-card'><h4>🎯 Best Deal</h4><div class='big-metric'>{best_deals[0]['discount_percent']:.0f}%</div><span class='badge badge-success'>OFF</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='metric-card'><h4>🎯 Best Deal</h4><div class='big-metric'>N/A</div></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Trends & Categories
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📈 Price Trends")
            dates = pd.date_range(start='2025-09-20', periods=30, freq='D')
            np.random.seed(42)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=np.random.uniform(50, 100, 30),
                mode='lines+markers',
                name='Average Price',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8, color='#3b82f6')
            ))
            fig.update_layout(height=340, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("💹 Categories")
            if analytics.get('top_categories'):
                cat_data = pd.DataFrame(
                    list(analytics['top_categories'].items()),
                    columns=['Category', 'Count']
                )
                fig_pie = px.pie(cat_data, values='Count', names='Category', hole=0.5, color_discrete_sequence=px.colors.sequential.Teal)
                fig_pie.update_layout(height=340, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No categories yet")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🔥 Hot Deals Right Now")
        if best_deals:
            deals_df = pd.DataFrame([{
                '🏷️ Product': deal['name'],
                '💰 Current': format_price(deal['current_price'], deal.get('currency', 'INR')),
                '💸 Alert Price': format_price(deal['alert_price'], deal.get('currency', 'INR')),
                '📊 Savings': f"{format_price(deal['alert_price'] - deal['current_price'], deal.get('currency', 'INR'))} ({deal['discount_percent']:.0f}% OFF)",
                '🛒 Site': deal.get('site', 'N/A')
            } for deal in best_deals])
            st.dataframe(deals_df, width='stretch', hide_index=True)
        else:
            st.info("No deals available yet. Add products to track!")
        
        st.subheader("⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📧 Send Daily Report"):
                try:
                    products = st.session_state.db.get_all_products()
                    st.session_state.notifier.send_daily_report(products)
                    st.success("Daily report sent!")
                except Exception as e:
                    st.error(f"Error: {e}")
        with col2:
            if st.button("📊 Export to CSV"):
                try:
                    st.session_state.db.export_to_csv("data/price_export.csv")
                    st.success("Data exported to data/price_export.csv")
                except Exception as e:
                    st.error(f"Error: {e}")
        with col3:
            if st.button("🔄 Check Prices Now"):
                with st.spinner("Checking prices..."):
                    products = st.session_state.db.get_all_products()
                    checked = 0
                    progress = st.progress(0)
                    for i, product in enumerate(products[:3]):
                        result = st.session_state.scraper.scrape_product(product['url'])
                        if result:
                            st.session_state.db.update_price(product['url'], result['price'])
                            checked += 1
                        progress.progress((i + 1) / min(3, len(products)))
                    st.success(f"Checked {checked} products!")

elif page == "📦 Products":
    st.markdown("<h1>📦 Product Management</h1>", unsafe_allow_html=True)
    if not backend_available:
        st.error("⚠️ Backend not available")
    else:
        with st.expander("➕ Add New Product", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("Product Name", placeholder="e.g., iPhone 15 Pro")
                product_url = st.text_input("Product URL", placeholder="https://...")
                # Per-product currency selection
                product_currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"], index=0)
                currency_symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}
                currency_symbol = currency_symbols.get(product_currency, '₹')
                alert_price = st.number_input(f"Alert Price ({currency_symbol})", min_value=0.0, value=1000.0)
            
            with col2:
                
                sites = st.multiselect(
                    "Sites to Track",
                    ["Amazon", "Flipkart", "eBay", "Meesho", "Myntra"],
                    default=["Flipkart"]
                )

                category = st.selectbox(
                    "Category",
                    ["Electronics", "Fashion", "Home", "Books", "Sports", "Gaming", "Beauty", "Other"]
                )
                enable_alerts = st.checkbox("Enable Price Alerts", value=True)
            
            st.markdown("---")
            
            # Small centered Add Product button
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                add_button = st.button("✨ Add", type="primary", width='stretch')
            
            if add_button:
                if product_name and product_url:
                    with st.spinner("🔍 Fetching product details and saving..."):
                        try:
                            # Step 1: Scrape product from URL with better error handling
                            st.info("🔍 Attempting to fetch product details...")
                            result = st.session_state.scraper.scrape_product(product_url)
                
                            # Initialize fields
                            current_price, image_url = None, None
                            scraping_success = False
                
                            if result and result.get('price'):
                                current_price = result.get('price')
                                image_url = result.get('image_url')
                                scraping_success = True
                                st.success(f"✅ Successfully fetched price: {currency_symbol}{current_price}")
                            else:
                                # Try alternative scraping methods
                                st.warning("⚠️ Initial scraping failed. Trying alternative methods...")
                                
                                # Method 1: Try with different user agent
                                try:
                                    import requests
                                    from bs4 import BeautifulSoup
                                    
                                    headers = {
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                        'Accept-Language': 'en-US,en;q=0.5',
                                        'Accept-Encoding': 'gzip, deflate',
                                        'Connection': 'keep-alive',
                                    }
                                    
                                    response = requests.get(product_url, headers=headers, timeout=10)
                                    if response.status_code == 200:
                                        soup = BeautifulSoup(response.content, 'html.parser')
                                        
                                        # Try to extract price using generic methods
                                        price_text = None
                                        for elem in soup.find_all(string=lambda text: text and ('₹' in text or '$' in text or '€' in text or '£' in text)):
                                            if any(char.isdigit() for char in elem):
                                                price_text = elem.strip()
                                                break
                                        
                                        if price_text:
                                            # Simple price extraction
                                            import re
                                            numbers = re.findall(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                                            if numbers:
                                                current_price = float(numbers[0])
                                                scraping_success = True
                                                st.success(f"✅ Alternative method found price: {currency_symbol}{current_price}")
                                
                                except Exception as e:
                                    st.warning(f"⚠️ Alternative scraping also failed: {str(e)}")
                                
                                # If all scraping methods fail, show error message
                                if not scraping_success:
                                    st.error("❌ Could not fetch product price automatically. Please try again later or check if the URL is correct.")
                            
                            # Step 2: Add to database (only if scraping was successful)
                            if scraping_success and current_price:
                                success = st.session_state.db.add_product(
                                    name=product_name,
                                    url=product_url,
                                    alert_price=alert_price,
                                    category=category,
                                    site=sites[0] if sites else "Unknown",
                                    currency=product_currency,
                                    current_price=current_price,
                                    image_url=image_url
                                )
                                
                                if success:
                                    st.success(f"✅ Added '{product_name}' with current price {currency_symbol}{current_price}!")
                            
                                    # 🚨 CHECK AND SEND INSTANT ALERT
                                    if current_price <= alert_price and alert_price > 0:
                                        # Calculate savings for display
                                        savings = alert_price - current_price
                                        savings_pct = (savings / alert_price) * 100 if alert_price > 0 else 0
                                        
                                        # Send instant alert
                                        with st.spinner("🚨 Sending instant alert..."):
                                            send_price_alert(product_name, current_price, alert_price, product_url, product_currency)
                                        
                                        # Show prominent alert message
                                        st.markdown(f"""
                                        <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); padding: 20px; border-radius: 12px; margin: 10px 0; text-align: center; color: white;">
                                            <h3 style="margin: 0; color: white;">🚨 INSTANT ALERT SENT! 🚨</h3>
                                            <p style="margin: 10px 0; font-size: 18px;">
                                                <strong>{product_name}</strong><br>
                                                Current: {currency_symbol}{current_price:.2f} | Target: {currency_symbol}{alert_price:.2f}<br>
                                                <span style="font-size: 20px; font-weight: bold;">You Save: {currency_symbol}{savings:.2f} ({savings_pct:.1f}% OFF!)</span>
                                            </p>
                                            <p style="margin: 0; font-size: 14px; opacity: 0.9;">
                                                Email and Telegram notifications sent immediately!
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.info(f"ℹ️ Price {currency_symbol}{current_price} is above alert price {currency_symbol}{alert_price}. No alert sent.")
                                else:
                                    st.error("❌ Product already exists in database!")
                            else:
                                st.error("❌ Cannot add product without current price. Please ensure the URL is correct and try again.")

                    
                                # Progress animation like Check Prices Now
                                progress = st.progress(0)
                                for i in range(100):
                                    time.sleep(0.005)
                                    progress.progress(i + 1)
                    
                                time.sleep(0.5)
                                st.rerun()
                    
                        except Exception as e:
                            st.error(f"⚠️ Error occurred: {str(e)}")
                else:
                    st.warning("⚠️ Please enter Product Name and URL")

        
        st.subheader("📋 Your Tracked Products")
        products = st.session_state.db.get_all_products()
        
        if products:
            # Search and Filter
            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 Search products", placeholder="Search by name...")
            with col2:
                filter_cat = st.selectbox("Filter by Category", ["All"] + list(set(p.get('category', 'Other') for p in products)))
            with col3:
                sort_by = st.selectbox("Sort by", ["Latest", "Price (Low to High)", "Price (High to Low)", "Name"])
            
            # Apply filters
            filtered_products = products
            if search:
                filtered_products = [p for p in filtered_products if search.lower() in p['name'].lower()]
            if filter_cat != "All":
                filtered_products = [p for p in filtered_products if p.get('category') == filter_cat]
            
            # Display products with images
            for product in filtered_products:
                product_currency = product.get('currency', 'INR')
                status = '🔴 ALERT!' if (product.get('current_price') and product.get('alert_price') and 
                                        product['current_price'] <= product['alert_price']) else '🟢 Active'
                
                col_img, col_content = st.columns([1, 4])
                
                with col_img:
                    if product.get('image_url'):
                        st.image(product['image_url'], width=100)
                    else:
                        st.markdown("<div style='width:100px;height:100px;background:#1a2742;border-radius:8px;display:flex;align-items:center;justify-content:center;'>📦</div>", unsafe_allow_html=True)
                
                with col_content:
                    st.markdown(f"""
                        <div class='metric-card'>
                            <h3 style='margin: 0 0 8px 0;'>{product['name'][:60]}</h3>
                            <p style='margin: 4px 0; opacity: 0.8;'>
                                <strong>Current:</strong> {format_price(product.get('current_price'), product_currency) if product.get('current_price') else 'N/A'} | 
                                <strong>Alert:</strong> {format_price(product.get('alert_price'), product_currency)}
                            </p>
                            <p style='margin: 4px 0; font-size: 0.85rem;'>
                                <span class='badge badge-info'>{product.get('category', 'Other')}</span>
                                <span class='badge badge-info'>{product.get('site', 'N/A')}</span>
                                <span class='badge {"badge-danger" if "ALERT" in status else "badge-success"}'>{status}</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🔍 View", key=f"view_{product['id']}", width='stretch'):
                        st.info(f"URL: {product['url']}")
                with col2:
                    if st.button("🔄 Update Price", key=f"update_{product['id']}", width='stretch'):
                        with st.spinner("Updating..."):
                            result = st.session_state.scraper.scrape_product(product['url'])
                            if result and result.get('price'):
                                st.session_state.db.update_price(product['url'], result['price'])
                                st.success(f"✅ Updated to {format_price(result['price'], product_currency)}")
                                time.sleep(1)
                                st.rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{product['id']}", width='stretch'):
                        if st.session_state.db.delete_product(product['id']):
                            st.success("✅ Deleted!")
                            time.sleep(0.5)
                            st.rerun()
        else:
            st.info("📭 No products yet. Add one above!")


elif page == "📈 Analytics":
    st.markdown("<h1>📈 Price Analytics & Insights</h1>", unsafe_allow_html=True)
    
    if not backend_available:
        st.error("⚠️ Backend modules not available. Check imports.")
    else:
        # Time range selector
        time_range = st.select_slider(
            "Select Time Range",
            options=["7 Days", "30 Days", "90 Days", "1 Year"],
            value="30 Days"
        )
        
        # Convert time range to days
        days_map = {"7 Days": 7, "30 Days": 30, "90 Days": 90, "1 Year": 365}
        days = days_map[time_range]
        
        # Get analytics data
        analytics = st.session_state.db.get_analytics_data()
        products = st.session_state.db.get_all_products()
        
        if not products:
            st.info("📭 No products to analyze yet. Add some products first!")
        else:
            # Overview metrics
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class='metric-card'>
                        <h4>📊 Total Products</h4>
                        <div class='big-metric'>{analytics.get('total_products', 0)}</div>
                        <span class='badge badge-info'>Tracked</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_price = analytics.get('avg_price', 0)
                st.markdown(f"""
                    <div class='metric-card'>
                        <h4>💰 Avg Price</h4>
                        <div class='big-metric'>{format_price(avg_price)}</div>
                        <span class='badge badge-success'>Current</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                active_alerts = analytics.get('active_alerts', 0)
                st.markdown(f"""
                    <div class='metric-card'>
                        <h4>🔔 Active Alerts</h4>
                        <div class='big-metric'>{active_alerts}</div>
                        <span class='badge badge-warning'>Watching</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                best_deals = st.session_state.db.get_best_deals(limit=1)
                if best_deals:
                    discount = best_deals[0]['discount_percent']
                    st.markdown(f"""
                        <div class='metric-card'>
                            <h4>🎯 Best Deal</h4>
                            <div class='big-metric'>{discount:.0f}%</div>
                            <span class='badge badge-success'>OFF</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class='metric-card'>
                            <h4>🎯 Best Deal</h4>
                            <div class='big-metric'>N/A</div>
                            <span class='badge badge-info'>None</span>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Price trends chart
            st.subheader("📈 Price Trends Over Time")
            
            # Get price history for all products
            all_price_data = []
            for product in products:
                history_df = st.session_state.db.get_price_history(product['id'], days=days)
                if not history_df.empty:
                    for _, record in history_df.iterrows():
                        all_price_data.append({
                            'timestamp': record['timestamp'],
                            'price': record['price'],
                            'product_name': product['name'],
                            'site': product['site']
                        })
            
            if all_price_data:
                df_prices = pd.DataFrame(all_price_data)
                
                # Create interactive price trends chart
                fig = go.Figure()
                
                # Add traces for each product
                for product_name in df_prices['product_name'].unique():
                    product_data = df_prices[df_prices['product_name'] == product_name]
                    fig.add_trace(go.Scatter(
                        x=product_data['timestamp'],
                        y=product_data['price'],
                        mode='lines+markers',
                        name=product_name,
                        line=dict(width=2),
                        marker=dict(size=6)
                    ))
                
                fig.update_layout(
                    title="Price Trends",
                    xaxis_title="Date",
                    yaxis_title="Price (₹)",
                    height=500,
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Price statistics
                st.subheader("📊 Price Statistics")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Price distribution
                    fig_hist = px.histogram(
                        df_prices, 
                        x='price', 
                        nbins=20,
                        title="Price Distribution",
                        color_discrete_sequence=['#3b82f6']
                    )
                    fig_hist.update_layout(
                        template='plotly_dark',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        height=400
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    # Site comparison
                    site_stats = df_prices.groupby('site')['price'].agg(['mean', 'count']).reset_index()
                    site_stats.columns = ['Site', 'Avg Price', 'Data Points']
                    
                    fig_bar = px.bar(
                        site_stats, 
                        x='Site', 
                        y='Avg Price',
                        title="Average Price by Site",
                        color='Avg Price',
                        color_continuous_scale='viridis'
                    )
                    fig_bar.update_layout(
                        template='plotly_dark',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        height=400
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Detailed analytics table
                st.subheader("📋 Detailed Analytics")
                
                # Calculate price changes for each product
                analytics_data = []
                for product in products:
                    history_df = st.session_state.db.get_price_history(product['id'], days=days)
                    if not history_df.empty and len(history_df) >= 2:
                        current_price = history_df.iloc[-1]['price']
                        previous_price = history_df.iloc[0]['price']
                        price_change = current_price - previous_price
                        price_change_pct = (price_change / previous_price) * 100 if previous_price > 0 else 0
                        
                        analytics_data.append({
                            'Product': product['name'],
                            'Current Price': format_price(current_price),
                            'Price Change': format_price(price_change),
                            'Change %': f"{price_change_pct:+.1f}%",
                            'Data Points': len(history_df),
                            'Site': product['site'],
                            'Status': '📈 Up' if price_change > 0 else '📉 Down' if price_change < 0 else '➡️ Stable'
                        })
                
                if analytics_data:
                    analytics_df = pd.DataFrame(analytics_data)
                    st.dataframe(analytics_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Not enough price history data for detailed analytics")
            
            else:
                st.info("📊 No price history data available for the selected time range")
                
                # Show products without price history
                st.subheader("📦 Products Without Price History")
                products_without_history = []
                for product in products:
                    history_df = st.session_state.db.get_price_history(product['id'], days=days)
                    if history_df.empty:
                        products_without_history.append(product)
                
                if products_without_history:
                    for product in products_without_history:
                        st.markdown(f"""
                            <div class='product-card'>
                                <h4>{product['name']}</h4>
                                <p>Current Price: {format_price(product['current_price'])}</p>
                                <p>Site: {product['site']}</p>
                                <p><em>No price history data available</em></p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ All products have price history data!")

elif page == "🤖 AI Predictions":
    st.markdown("<h1>🤖 AI-Powered Predictions</h1>", unsafe_allow_html=True)
    
    if not backend_available:
        st.error("⚠️ Backend modules not available. Check imports.")
    else:
        # Import ML modules
        try:
            from ml.price_predictor import PricePredictor, TrendAnalyzer
            ml_available = True
        except ImportError as e:
            st.error(f"ML modules not available: {e}")
            ml_available = False
        
        if ml_available:
            products = st.session_state.db.get_all_products()
            
            if not products:
                st.info("📭 No products to analyze yet. Add some products first!")
            else:
                # Product selection
                selected_product_name = st.selectbox(
                    "Select Product for Prediction",
                    options=[p['name'] for p in products],
                    help="Choose a product to generate AI-powered price predictions"
                )
                
                selected_product = next(p for p in products if p['name'] == selected_product_name)
                st.markdown(f"**Selected:** {selected_product_name}")
                
                # Get price history for selected product
                price_history_df = st.session_state.db.get_price_history(selected_product['id'], days=90)
                
                if len(price_history_df) < 10:
                    st.warning(f"⚠️ Insufficient price history data ({len(price_history_df)} points). Need at least 10 data points for reliable predictions.")
                    st.info("💡 Add more price history by updating prices regularly or wait for more data points.")
                else:
                    st.success(f"✅ Sufficient data available ({len(price_history_df)} price points)")
                    
                    # Convert to DataFrame for ML (already a DataFrame)
                    df_history = price_history_df.copy()
                    df_history = df_history.sort_values('timestamp')
                    
                    # Prediction parameters
                    col1, col2 = st.columns(2)
                    with col1:
                        prediction_days = st.slider("Prediction Horizon (days)", 1, 30, 7, help="Number of days to predict ahead")
                    with col2:
                        model_type = st.selectbox("ML Model", ["random_forest", "linear_regression"], help="Choose the machine learning model")
                    
                    # Train model and make predictions
                    if st.button("🔮 Generate Predictions", type="primary"):
                        with st.spinner("Training ML model and generating predictions..."):
                            try:
                                # Initialize predictor
                                predictor = PricePredictor(model_type=model_type)
                                
                                # Train model
                                training_metrics = predictor.train(df_history, selected_product['id'])
                                
                                if 'error' in training_metrics:
                                    st.error(f"Training failed: {training_metrics['error']}")
                                else:
                                    # Display training metrics
                                    st.subheader("📊 Model Performance")
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        st.metric("Training R²", f"{training_metrics['train_r2']:.3f}")
                                    with col2:
                                        st.metric("Test R²", f"{training_metrics['test_r2']:.3f}")
                                    with col3:
                                        st.metric("Training MAE", f"₹{training_metrics['train_mae']:.2f}")
                                    with col4:
                                        st.metric("Test MAE", f"₹{training_metrics['test_mae']:.2f}")
                                    
                                    # Generate predictions
                                    recent_data = df_history.tail(30)  # Use last 30 days for prediction
                                    predictions = predictor.predict_next_days(recent_data, days=prediction_days)
                                    
                                    if 'predictions' in predictions:
                                        # Display predictions
                                        st.subheader("🔮 Price Predictions")
                                        
                                        # Create prediction chart
                                        fig = go.Figure()
                                        
                                        # Historical data
                                        fig.add_trace(go.Scatter(
                                            x=df_history['timestamp'],
                                            y=df_history['price'],
                                            mode='lines+markers',
                                            name='Historical Prices',
                                            line=dict(color='#3b82f6', width=2),
                                            marker=dict(size=6)
                                        ))
                                        
                                        # Predictions
                                        future_dates = pd.date_range(
                                            start=df_history['timestamp'].iloc[-1] + timedelta(days=1),
                                            periods=prediction_days,
                                            freq='D'
                                        )
                                        
                                        fig.add_trace(go.Scatter(
                                            x=future_dates,
                                            y=predictions['predictions'],
                                            mode='lines+markers',
                                            name='AI Predictions',
                                            line=dict(color='#10b981', width=3, dash='dash'),
                                            marker=dict(size=8)
                                        ))
                                        
                                        # Confidence intervals
                                        if 'confidence_intervals' in predictions:
                                            upper_bound = [p + predictions['confidence_intervals'][i] for i, p in enumerate(predictions['predictions'])]
                                            lower_bound = [p - predictions['confidence_intervals'][i] for i, p in enumerate(predictions['predictions'])]
                                            
                                            fig.add_trace(go.Scatter(
                                                x=future_dates,
                                                y=upper_bound,
                                                mode='lines',
                                                name='Upper Bound',
                                                line=dict(color='rgba(16, 185, 129, 0.3)', width=0),
                                                showlegend=False
                                            ))
                                            
                                            fig.add_trace(go.Scatter(
                                                x=future_dates,
                                                y=lower_bound,
                                                mode='lines',
                                                name='Confidence Interval',
                                                line=dict(color='rgba(16, 185, 129, 0.3)', width=0),
                                                fill='tonexty',
                                                fillcolor='rgba(16, 185, 129, 0.1)',
                                                showlegend=True
                                            ))
                                        
                                        fig.update_layout(
                                            title=f"Price Predictions for {selected_product_name}",
                                            xaxis_title="Date",
                                            yaxis_title="Price (₹)",
                                            height=500,
                                            template='plotly_dark',
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            plot_bgcolor='rgba(0,0,0,0)',
                                            font=dict(color='white')
                                        )
                                        
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                        # Prediction details
                                        st.subheader("📋 Prediction Details")
                                        prediction_df = pd.DataFrame({
                                            'Date': future_dates,
                                            'Predicted Price': [f"₹{p:.2f}" for p in predictions['predictions']],
                                            'Change from Current': [f"{((p - df_history['price'].iloc[-1]) / df_history['price'].iloc[-1] * 100):+.1f}%" for p in predictions['predictions']]
                                        })
                                        st.dataframe(prediction_df, use_container_width=True, hide_index=True)
                                        
                                        # Buy recommendation
                                        if 'predictions' in predictions:
                                            recommendation = predictor.get_buy_recommendation(predictions['predictions'], df_history['price'].iloc[-1])
                                            
                                            st.subheader("💡 AI Recommendation")
                                            
                                            # Recommendation card
                                            if recommendation['recommendation'] == 'BUY_NOW':
                                                st.markdown(f"""
                                                    <div class='metric-card' style='border-color: #10b981;'>
                                                        <h4>🛒 BUY NOW</h4>
                                                        <p><strong>Reason:</strong> {recommendation['reason']}</p>
                                                        <p><strong>Confidence:</strong> {recommendation['confidence']:.1%}</p>
                                                    </div>
                                                """, unsafe_allow_html=True)
                                            else:
                                                wait_days = recommendation['recommendation'].split('_')[1]
                                                st.markdown(f"""
                                                    <div class='metric-card' style='border-color: #f59e0b;'>
                                                        <h4>⏳ WAIT {wait_days} DAYS</h4>
                                                        <p><strong>Reason:</strong> {recommendation['reason']}</p>
                                                        <p><strong>Potential Savings:</strong> ₹{recommendation['potential_savings']:.2f} ({recommendation['potential_savings_pct']:.1f}%)</p>
                                                        <p><strong>Confidence:</strong> {recommendation['confidence']:.1%}</p>
                                                    </div>
                                                """, unsafe_allow_html=True)
                                        
                                        # Feature importance
                                        if hasattr(predictor, 'get_feature_importance'):
                                            importance = predictor.get_feature_importance()
                                            if importance:
                                                st.subheader("🔍 Feature Importance")
                                                importance_df = pd.DataFrame(list(importance.items()), columns=['Feature', 'Importance'])
                                                importance_df = importance_df.sort_values('Importance', ascending=True)
                                                
                                                fig_importance = px.bar(
                                                    importance_df,
                                                    x='Importance',
                                                    y='Feature',
                                                    orientation='h',
                                                    title="Model Feature Importance",
                                                    color='Importance',
                                                    color_continuous_scale='viridis'
                                                )
                                                fig_importance.update_layout(
                                                    template='plotly_dark',
                                                    paper_bgcolor='rgba(0,0,0,0)',
                                                    plot_bgcolor='rgba(0,0,0,0)',
                                                    font=dict(color='white'),
                                                    height=400
                                                )
                                                st.plotly_chart(fig_importance, use_container_width=True)
                                    
                                    else:
                                        st.error("Failed to generate predictions")
                            
                            except Exception as e:
                                st.error(f"Error generating predictions: {str(e)}")
                                st.exception(e)
                    
                    # Trend analysis
                    st.subheader("📈 Trend Analysis")
                    
                    if len(price_history_df) >= 5:
                        # Analyze trends
                        prices = price_history_df['price'].tolist()
                        trend_direction = TrendAnalyzer.detect_trend(prices)
                        volatility = TrendAnalyzer.calculate_volatility(prices)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Trend Direction", trend_direction)
                        with col2:
                            # Calculate trend strength as percentage change over time
                            if len(prices) >= 7:
                                recent_change = ((prices[-1] - prices[-7]) / prices[-7]) * 100
                                st.metric("7-Day Change", f"{recent_change:+.1f}%")
                            else:
                                st.metric("Trend Strength", "N/A")
                        with col3:
                            st.metric("Volatility", f"{volatility:.2f}%")
                        
                        # Support and resistance levels
                        support_resistance = TrendAnalyzer.find_support_resistance(prices)
                        
                        st.subheader("🎯 Support & Resistance Levels")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Support Level", f"₹{support_resistance['support']:.2f}")
                        with col2:
                            st.metric("Resistance Level", f"₹{support_resistance['resistance']:.2f}")
                    
                    else:
                        st.info("Need at least 5 price points for trend analysis")
                
                # Model information
                st.subheader("🤖 About AI Predictions")
                st.markdown("""
                <div class='section-card'>
                    <h4>How it works:</h4>
                    <ul>
                        <li><strong>Random Forest:</strong> Uses multiple decision trees for robust predictions</li>
                        <li><strong>Linear Regression:</strong> Finds linear patterns in price data</li>
                        <li><strong>Feature Engineering:</strong> Creates time-based features like moving averages, trends, and seasonality</li>
                        <li><strong>Confidence Intervals:</strong> Provides uncertainty estimates for predictions</li>
                    </ul>
                    <p><em>Note: Predictions are based on historical patterns and may not account for external factors like market events or promotions.</em></p>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.error("ML prediction modules are not available. Please check the installation.")

elif page == "⚙️ Settings":
    st.markdown("<h1>⚙️ Settings & Configuration</h1>", unsafe_allow_html=True)
    current_settings = load_settings()
    tab1, tab3 = st.tabs(["🔔 Notifications", "👤 Profile"])

    with tab1:
        st.subheader("Notification Preferences")
        col1, col2 = st.columns(2)
        with col1:
            email_enabled = st.checkbox("📧 Email Notifications", value=True)
            email_addr = st.text_input("Email Address", value=current_settings.get('email_address', 'user@example.com'))
            telegram_enabled = st.checkbox("📱 Telegram Alerts", value=current_settings.get('telegram_enabled', False))
            telegram_token = st.text_input("Telegram Bot Token", type="password", value=current_settings.get('telegram_token', ''))
            telegram_chat_id = st.text_input("Telegram Chat ID", value=current_settings.get('telegram_chat_id', ''), help="Your Telegram chat ID for receiving alerts")
        with col2:
            st.info("📧 Email and Telegram notifications are automatically sent when products are added with prices below your alert price.")
        # Save button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("💾 Save", key="save_notif"):
                current_settings['email_address'] = email_addr
                current_settings['telegram_token'] = telegram_token
                current_settings['telegram_chat_id'] = telegram_chat_id
                current_settings['telegram_enabled'] = telegram_enabled
                save_settings(current_settings)
                st.success("✅ Saved!")
                time.sleep(1)
                st.rerun()

    with tab3:
        st.subheader("User Profile")
        username = st.text_input("Username", value=current_settings.get('username', 'pricetracker_user'), key="profile_username")
        email = st.text_input("Email", value=current_settings.get('email_address', 'user@example.com'), key="profile_email")
        st.markdown("---")
        st.subheader("Appearance")
        timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "IST"], 
                            index=["UTC", "EST", "PST", "IST"].index(current_settings.get('timezone', 'IST')),
                            key="profile_timezone")
        theme = st.selectbox("Preferred Theme", ["System Default", "Dark Mode", "Light Mode"], index=0, key="profile_theme")
        st.markdown("---")
        st.subheader("Personal Details")
        full_name = st.text_input("Full Name", value=current_settings.get('full_name', ''), key="profile_fullname")
        phone = st.text_input("Phone Number (optional)", value=current_settings.get('phone', ''), key="profile_phone")
        occupation = st.selectbox("Occupation", ["Student", "Developer", "Professional", "Other"], index=0, key="profile_occupation")
    
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("💾 Save", key="save_profile"):
                current_settings['username'] = username
                current_settings['email_address'] = email
                current_settings['timezone'] = timezone
                current_settings['theme'] = theme
                current_settings['full_name'] = full_name
                current_settings['phone'] = phone
                current_settings['occupation'] = occupation
                save_settings(current_settings)
                st.success("✅ Profile updated!")
                time.sleep(0.8)
                st.rerun()



# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #cbd5e1; padding: 24px; font-weight: 600;'>
        <p>🛒 <strong>Advanced Price Tracker Pro</strong> | Built with ❤️ using Streamlit</p>
        <p style='font-size: 0.9em;'>© 2025 | Track Smarter, Save More!</p>
    </div>
    """,
    unsafe_allow_html=True
)
