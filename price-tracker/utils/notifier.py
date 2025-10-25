"""
Notification system for price alerts - Email, Telegram, SMS
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
import logging
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Import config
try:
    import config
except ImportError:
    # Fallback config
    class config:
        EMAIL_ENABLED = True
        SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
        SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
        RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL', '')
        SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
        TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
        TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_settings():
    """Load settings from JSON file"""
    try:
        with open('data/settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


class EmailNotifier:
    """Sends email notifications for price changes"""

    def __init__(self):
        self.sender_email = config.SENDER_EMAIL
        self.sender_password = config.SENDER_PASSWORD
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT

    def get_receiver_email(self):
        """Get receiver email from settings.json (dynamic)"""
        settings = load_settings()
        receiver = settings.get('email_address', None)
        
        # Fallback to config or sender email if no receiver is set
        if not receiver or receiver == 'user@example.com':
            receiver = config.RECEIVER_EMAIL or self.sender_email
            
        return receiver

    def send_price_alert(self, product_info: Dict) -> bool:
        """
        Send price alert email

        Args:
            product_info: Dictionary with product details
        """
        if not config.EMAIL_ENABLED:
            logger.info("Email notifications are disabled")
            return False

        try:
            receiver_email = self.get_receiver_email()
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🔔 Price Alert: {product_info['name']}"
            message["From"] = self.sender_email
            message["To"] = receiver_email

            # Create email body
            text_body = self._create_text_body(product_info)
            html_body = self._create_html_body(product_info)

            # Attach both plain text and HTML versions
            text_part = MIMEText(text_body, "plain")
            html_part = MIMEText(html_body, "html")
            message.attach(text_part)
            message.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, receiver_email, message.as_string())

            logger.info(f"Price alert email sent for {product_info['name']} to {receiver_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def _create_text_body(self, product_info: Dict) -> str:
        """Create plain text email body"""
        old_price = product_info.get('old_price', 0)
        new_price = product_info.get('new_price', 0)
        alert_price = product_info.get('alert_price', 0)
        
        # Calculate savings from alert price (target savings)
        alert_savings = alert_price - new_price if alert_price > 0 else 0
        alert_savings_pct = (alert_savings / alert_price) * 100 if alert_price > 0 else 0
        
        # Calculate price change from previous price
        price_change_savings = old_price - new_price if old_price else 0

        body = f"""
🔔 Price Alert for {product_info['name']}!

💰 CURRENT PRICE: ₹{new_price:.2f}
🎯 YOUR ALERT PRICE: ₹{alert_price:.2f}
💵 YOU SAVE: ₹{alert_savings:.2f} ({alert_savings_pct:.1f}% OFF!)
"""

        if old_price and old_price != new_price:
            price_change = ((new_price - old_price) / old_price) * 100
            direction = "dropped" if price_change < 0 else "increased"
            body += f"📊 Previous Price: ₹{old_price:.2f} ({direction} by {abs(price_change):.1f}%)\n"

        body += f"""
🛒 Site: {product_info.get('site', 'Unknown')}
🔗 Product URL: {product_info.get('url', 'N/A')}

---
🤖 Price Tracker Notification
Sent at: {product_info.get('timestamp', 'Unknown')}
"""

        return body

    def _create_html_body(self, product_info: Dict) -> str:
        """Create HTML email body"""
        old_price = product_info.get('old_price', 0)
        new_price = product_info.get('new_price', 0)
        alert_price = product_info.get('alert_price', 0)
        
        # Calculate savings from alert price (target savings)
        alert_savings = alert_price - new_price if alert_price > 0 else 0
        alert_savings_pct = (alert_savings / alert_price) * 100 if alert_price > 0 else 0
        
        # Calculate price change from previous price
        price_change_savings = old_price - new_price if old_price else 0
        change_color = "#28a745" if alert_savings > 0 else "#dc3545"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .price-box {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .price-current {{ font-size: 32px; font-weight: bold; color: #28a745; }}
        .price-alert {{ font-size: 20px; color: #6c757d; }}
        .savings {{ font-size: 24px; color: #28a745; font-weight: bold; }}
        .price-old {{ font-size: 16px; color: #6c757d; text-decoration: line-through; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; color: #6c757d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 Price Alert!</h1>
            <p>Your tracked product is below your target price!</p>
        </div>

        <div class="content">
            <h2 style="color: #333; margin-bottom: 20px;">{product_info['name']}</h2>

            <div class="price-box">
                <div style="text-align: center;">
                    <div style="margin-bottom: 15px;">
                        <span class="price-current">₹{new_price:.2f}</span>
                        <div style="font-size: 14px; color: #6c757d; margin-top: 5px;">CURRENT PRICE</div>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <span class="price-alert">₹{alert_price:.2f}</span>
                        <div style="font-size: 14px; color: #6c757d; margin-top: 5px;">YOUR ALERT PRICE</div>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 15px; background-color: #d4edda; border-radius: 8px;">
                        <span class="savings">💰 YOU SAVE ₹{alert_savings:.2f}!</span>
                        <div style="font-size: 16px; color: #28a745; margin-top: 5px;">({alert_savings_pct:.1f}% OFF)</div>
                    </div>
                </div>
            </div>
"""

        if old_price and old_price != new_price:
            price_change = ((new_price - old_price) / old_price) * 100
            direction = "📉 Dropped" if price_change < 0 else "📈 Increased"
            html += f"""
            <div style="background-color: #e9ecef; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="font-size: 16px; margin: 0;">
                    <strong>Price Change:</strong> 
                    <span style="color: {change_color};">{direction} by {abs(price_change):.1f}%</span>
                </p>
                <p style="font-size: 14px; color: #6c757d; margin: 5px 0 0 0;">
                    Previous Price: <span class="price-old">₹{old_price:.2f}</span>
                </p>
            </div>
"""

        html += f"""
            <p><strong>🛒 Site:</strong> {product_info.get('site', 'Unknown')}</p>

            <a href="{product_info.get('url', '#')}" class="button">
                View Product 🛍️
            </a>
        </div>

        <div class="footer">
            <p>This is an automated notification from your Price Tracker</p>
            <p>🤖 Sent at: {product_info.get('timestamp', 'Unknown')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def send_daily_report(self, products: list) -> bool:
        """Send daily summary report"""
        try:
            receiver_email = self.get_receiver_email()
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "📊 Daily Price Tracking Report"
            message["From"] = self.sender_email
            message["To"] = receiver_email

            # Create report content
            report = self._create_daily_report(products)
            html_part = MIMEText(report, "html")
            message.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, receiver_email, message.as_string())

            logger.info(f"Daily report sent successfully to {receiver_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending daily report: {e}")
            return False

    def _create_daily_report(self, products: list) -> str:
        """Create HTML daily report"""
        total_products = len(products)
        alerts = sum(1 for p in products if p.get('should_alert', False))

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
        .container {{ max-width: 700px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .stats {{ display: flex; justify-content: space-around; padding: 25px; background-color: #f8f9fa; }}
        .stat {{ text-align: center; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .product-list {{ padding: 25px; }}
        .product {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
        .product:last-child {{ border-bottom: none; }}
        .product-card {{ border: 1px solid #e9ecef; border-radius: 8px; padding: 25px; margin-bottom: 20px; background-color: #f8f9fa; }}
        .product-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }}
        .product-info {{ flex: 1; }}
        .product-metrics {{ display: flex; gap: 25px; margin-bottom: 15px; flex-wrap: wrap; }}
        .metric {{ text-align: center; min-width: 120px; }}
        .metric-label {{ font-size: 12px; color: #6c757d; display: block; margin-bottom: 5px; }}
        .metric-value {{ font-weight: bold; }}
        .view-button {{ text-align: center; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Daily Price Report</h1>
            <p>Your price tracking summary</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-number">{total_products}</div>
                <div>Products Tracked</div>
            </div>
            <div class="stat">
                <div class="stat-number">{alerts}</div>
                <div>Price Alerts</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len([p for p in products if p.get('price_change', 0) < 0])}</div>
                <div>Price Drops</div>
            </div>
        </div>

        <div class="product-list">
            <h3>Product Updates:</h3>
"""

        for product in products[:10]:
            change_color = "#28a745" if product.get('price_change', 0) < 0 else "#dc3545"
            current_price = product.get('current_price', 0)
            alert_price = product.get('alert_price', 0)
            
            # Calculate savings from alert price
            alert_savings = alert_price - current_price if alert_price > 0 else 0
            alert_savings_pct = (alert_savings / alert_price) * 100 if alert_price > 0 else 0
            
            # Calculate price change from previous price
            old_price = product.get('old_price', 0)
            price_change = product.get('price_change', 0)
            
            # Handle savings display - remove minus symbol and show appropriate message
            if alert_savings > 0:
                savings_display = f"₹{alert_savings:.2f} ({alert_savings_pct:.1f}% OFF)"
                savings_color = "#28a745"
                savings_label = "You Save:"
            else:
                savings_display = f"₹{abs(alert_savings):.2f} ({abs(alert_savings_pct):.1f}% MORE)"
                savings_color = "#dc3545"
                savings_label = "Price Above Target:"
            
            html += f"""
            <div class="product" style="border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; margin-bottom: 20px; background-color: #f8f9fa;">
                <h4 style="margin: 0 0 15px 0; color: #333; font-size: 16px; line-height: 1.3;">{product.get('name', 'Unknown Product')}</h4>
                
                <div style="display: flex; gap: 25px; margin-bottom: 15px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 120px;">
                        <span style="font-size: 12px; color: #6c757d; display: block; margin-bottom: 5px;">Current Price:</span>
                        <span style="color: {change_color}; font-weight: bold; font-size: 18px;">₹{(current_price or 0):.2f}</span>
                    </div>
                    <div style="flex: 1; min-width: 120px;">
                        <span style="font-size: 12px; color: #6c757d; display: block; margin-bottom: 5px;">Alert Price:</span>
                        <span style="color: #6c757d; font-weight: bold; font-size: 16px;">₹{(alert_price or 0):.2f}</span>
                    </div>
                    <div style="flex: 1; min-width: 120px;">
                        <span style="font-size: 12px; color: #6c757d; display: block; margin-bottom: 5px;">{savings_label}</span>
                        <span style="color: {savings_color}; font-weight: bold; font-size: 16px;">{savings_display}</span>
                    </div>
                </div>
                
                <div style="font-size: 12px; color: #6c757d; margin-bottom: 15px;">
                    🛒 Site: {product.get('site', 'Unknown')}
                    {f' | 📊 Price Change: {price_change:+.1f}%' if price_change != 0 else ''}
                </div>
                
                <div style="text-align: center;">
                    <a href="{product.get('url', '#')}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 14px; font-weight: bold;">
                        View Product 🛍️
                    </a>
                </div>
            </div>
"""

        html += """
        </div>
    </div>
</body>
</html>
"""
        return html

    def test_connection(self) -> bool:
        """Test SMTP connection and credentials"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            logger.info("Email connection test successful!")
            return True
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False


class TelegramNotifier:
    """Send notifications via Telegram Bot"""

    def __init__(self):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID

    def send_price_alert(self, product_info: Dict) -> bool:
        """Send price alert via Telegram"""
        try:
            import requests

            old_price = product_info.get('old_price', 0)
            new_price = product_info.get('new_price', 0)
            alert_price = product_info.get('alert_price', 0)
            
            # Calculate savings from alert price (target savings)
            alert_savings = alert_price - new_price if alert_price > 0 else 0
            alert_savings_pct = (alert_savings / alert_price) * 100 if alert_price > 0 else 0
            
            # Handle savings display - remove minus symbol
            if alert_savings > 0:
                savings_display = f"₹{alert_savings:.2f} ({alert_savings_pct:.1f}% OFF!)"
                savings_label = "YOU SAVE:"
            else:
                savings_display = f"₹{abs(alert_savings):.2f} ({abs(alert_savings_pct):.1f}% MORE)"
                savings_label = "PRICE ABOVE TARGET:"

            message = f"""
🔔 *Price Alert!*

📦 *Product:* {product_info['name']}
💰 *Current Price:* ₹{new_price:.2f}
🎯 *Your Alert Price:* ₹{alert_price:.2f}
💵 *{savings_label}* {savings_display}
"""

            if old_price and old_price != new_price:
                price_change = ((new_price - old_price) / old_price) * 100
                emoji = "📉" if price_change < 0 else "📈"
                message += f"{emoji} *Price Change:* {price_change:+.1f}% (Previous: ₹{old_price:.2f})\n"

            message += f"""
🛒 *Site:* {product_info.get('site', 'Unknown')}
🔗 [View Product]({product_info.get('url', '')})
"""

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, data=data)
            response.raise_for_status()

            logger.info(f"Telegram alert sent for {product_info['name']}")
            return True

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            import requests

            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url)
            response.raise_for_status()

            logger.info("Telegram connection test successful!")
            return True

        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False


class SMSNotifier:
    """Send SMS notifications via Twilio"""

    def __init__(self):
        self.account_sid = getattr(config, 'TWILIO_ACCOUNT_SID', '')
        self.auth_token = getattr(config, 'TWILIO_AUTH_TOKEN', '')
        self.phone_number = getattr(config, 'TWILIO_PHONE_NUMBER', '')

    def send_price_alert(self, product_info: Dict, to_number: str) -> bool:
        """Send SMS price alert"""
        try:
            from twilio.rest import Client

            client = Client(self.account_sid, self.auth_token)

            new_price = product_info.get('new_price', 0)
            message_body = f"""
🔔 Price Alert!
{product_info['name']}
New Price: ₹{new_price:.2f}
Site: {product_info.get('site', 'Unknown')}
"""

            message = client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=to_number
            )

            logger.info(f"SMS sent: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False


# Multi-channel notifier
class MultiNotifier:
    """Send notifications across multiple channels"""

    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.telegram_notifier = TelegramNotifier()
        self.sms_notifier = SMSNotifier()

    def send_price_alert(self, product_info: Dict, channels: list = None) -> Dict[str, bool]:
        """Send alert across specified channels"""
        if channels is None:
            channels = ['email', 'telegram']

        results = {}

        if 'email' in channels:
            results['email'] = self.email_notifier.send_price_alert(product_info)

        if 'telegram' in channels:
            results['telegram'] = self.telegram_notifier.send_price_alert(product_info)

        if 'sms' in channels:
            # You would need to specify the phone number
            results['sms'] = False  # self.sms_notifier.send_price_alert(product_info, phone_number)

        return results

    def test_all_connections(self) -> Dict[str, bool]:
        """Test all notification channels"""
        return {
            'email': self.email_notifier.test_connection(),
            'telegram': self.telegram_notifier.test_connection()
        }
