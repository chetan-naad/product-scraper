
# 2. integrations/telegram_notification.py - Telegram Bot Integration
telegram_code = '''"""
Telegram Bot Integration for Product Price Tracker
Send price alerts and interact with users via Telegram
"""
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    """
    Telegram Bot for price tracking notifications and commands
    """
    
    def __init__(self, bot_token: str, chat_id: str = None):
        """
        Initialize Telegram Bot
        
        Args:
            bot_token: Telegram Bot API token from @BotFather
            chat_id: Default chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
        self.application = None
        logger.info("Telegram Bot initialized")
    
    async def send_message(self, text: str, chat_id: str = None, 
                          parse_mode: str = 'Markdown') -> bool:
        """
        Send a text message via Telegram
        
        Args:
            text: Message text
            chat_id: Recipient chat ID (uses default if not provided)
            parse_mode: Text formatting ('Markdown' or 'HTML')
            
        Returns:
            Success status
        """
        try:
            target_chat = chat_id or self.chat_id
            
            if not target_chat:
                logger.error("No chat ID provided")
                return False
            
            await self.bot.send_message(
                chat_id=target_chat,
                text=text,
                parse_mode=parse_mode
            )
            
            logger.info(f"Message sent to {target_chat}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def send_message_sync(self, text: str, chat_id: str = None) -> bool:
        """Synchronous wrapper for send_message"""
        return asyncio.run(self.send_message(text, chat_id))
    
    async def send_price_alert(self, product_info: Dict, chat_id: str = None) -> bool:
        """
        Send formatted price alert
        
        Args:
            product_info: Product information dictionary
            chat_id: Recipient chat ID
            
        Returns:
            Success status
        """
        try:
            old_price = product_info.get('old_price', 0)
            new_price = product_info.get('new_price', 0)
            savings = old_price - new_price if old_price else 0
            
            # Determine emoji based on price change
            if new_price < old_price:
                emoji = "📉"
                trend = "dropped"
            elif new_price > old_price:
                emoji = "📈"
                trend = "increased"
            else:
                emoji = "➡️"
                trend = "unchanged"
            
            message = f"""
🔔 *PRICE ALERT!*

📦 *Product:* {product_info.get('name', 'Unknown')}

{emoji} *Price {trend}:*
💰 New Price: `${new_price:.2f}`
"""
            
            if old_price:
                message += f"📊 Old Price: `${old_price:.2f}`\n"
            
            if savings > 0:
                savings_pct = (savings / old_price) * 100 if old_price else 0
                message += f"💵 *You Save:* `${savings:.2f}` ({savings_pct:.1f}%)\n"
            
            if product_info.get('price_change'):
                change = product_info['price_change']
                message += f"📈 *Change:* `{change:+.2f}%`\n"
            
            message += f"""
🛒 *Site:* {product_info.get('site', 'Unknown')}
⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 [View Product]({product_info.get('url', '#')})

_Happy Shopping!_ 🛍️
"""
            
            return await self.send_message(message, chat_id)
            
        except Exception as e:
            logger.error(f"Error sending price alert: {e}")
            return False
    
    def send_price_alert_sync(self, product_info: Dict, chat_id: str = None) -> bool:
        """Synchronous wrapper for send_price_alert"""
        return asyncio.run(self.send_price_alert(product_info, chat_id))
    
    async def send_daily_summary(self, summary_data: Dict, chat_id: str = None) -> bool:
        """
        Send daily summary report
        
        Args:
            summary_data: Summary statistics dictionary
            chat_id: Recipient chat ID
            
        Returns:
            Success status
        """
        try:
            message = f"""
📊 *DAILY PRICE TRACKING SUMMARY*
_{datetime.now().strftime('%B %d, %Y')}_

📦 *Products Tracked:* {summary_data.get('total_products', 0)}
🔔 *Active Alerts:* {summary_data.get('active_alerts', 0)}
📉 *Price Drops Today:* {summary_data.get('price_drops', 0)}
💰 *Total Savings:* ${summary_data.get('total_savings', 0):.2f}

"""
            
            # Add best deals if available
            if summary_data.get('best_deals'):
                message += "*🔥 Top Deals Today:*\n"
                for i, deal in enumerate(summary_data['best_deals'][:5], 1):
                    message += f"\n{i}. {deal['name']}\n"
                    message += f"   💰 ${deal['current_price']:.2f} "
                    message += f"({deal['discount_percent']:.0f}% OFF)\n"
            
            message += "\n_Keep tracking for more savings!_ 🎯"
            
            return await self.send_message(message, chat_id)
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    def send_daily_summary_sync(self, summary_data: Dict, chat_id: str = None) -> bool:
        """Synchronous wrapper for send_daily_summary"""
        return asyncio.run(self.send_daily_summary(summary_data, chat_id))
    
    async def send_photo(self, photo_path: str, caption: str = None, 
                        chat_id: str = None) -> bool:
        """
        Send photo (e.g., price chart image)
        
        Args:
            photo_path: Path to image file or URL
            caption: Image caption
            chat_id: Recipient chat ID
            
        Returns:
            Success status
        """
        try:
            target_chat = chat_id or self.chat_id
            
            await self.bot.send_photo(
                chat_id=target_chat,
                photo=photo_path,
                caption=caption,
                parse_mode='Markdown'
            )
            
            logger.info(f"Photo sent to {target_chat}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return False
    
    # Bot Commands (for interactive bot)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🛒 *Welcome to Price Tracker Bot!*

I can help you track product prices and get alerts!

*Available Commands:*
/start - Show this message
/track - Track a new product
/list - List all tracked products
/status - Show tracking status
/help - Get help

Let's start saving money! 💰
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📖 *Help - How to Use Price Tracker Bot*

*Commands:*
• `/track <url>` - Start tracking a product
• `/list` - See all your tracked products
• `/remove <product_id>` - Stop tracking a product
• `/status` - Check bot status
• `/settings` - Configure alerts

*Features:*
✅ Real-time price monitoring
✅ Multi-site comparison
✅ Instant price drop alerts
✅ Daily summary reports

Need more help? Contact support!
"""
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_message = """
📊 *Bot Status*

✅ Bot is active and running
🔄 Last check: 2 minutes ago
📦 Tracking: 15 products
🔔 Active alerts: 3

All systems operational! 🚀
"""
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command - show tracked products"""
        # This would fetch from database in real implementation
        products_message = """
📦 *Your Tracked Products*

1. iPhone 15 Pro - $999 📉
   Alert at: $950
   
2. Sony Headphones - $299 ✅
   Alert at: $250
   
3. Samsung TV - $699 🔔
   Alert at: $650 (TRIGGERED!)

Use /remove <id> to stop tracking
"""
        await update.message.reply_text(products_message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        text = update.message.text
        
        # Check if it's a URL
        if text.startswith('http'):
            response = f"""
✅ *Product URL received!*

I'll start tracking: {text}

Set your alert price:
Send: `alert <price>`

Example: `alert 99.99`
"""
        else:
            response = """
I didn't understand that. Try:
• Send a product URL to track
• Use /help for commands
"""
        
        await update.message.reply_text(response, parse_mode='Markdown')
    
    def run_bot(self):
        """
        Run the bot (for interactive mode)
        This creates a long-running bot that responds to commands
        """
        try:
            # Create application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Register command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("list", self.list_command))
            
            # Register message handler
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
            )
            
            # Start bot
            logger.info("Starting Telegram Bot...")
            self.application.run_polling()
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")
    
    async def get_chat_id(self) -> str:
        """
        Get your chat ID (useful for setup)
        
        Returns:
            Instructions on how to get chat ID
        """
        try:
            updates = await self.bot.get_updates()
            
            if updates:
                latest_update = updates[-1]
                chat_id = latest_update.message.chat.id
                logger.info(f"Your Chat ID: {chat_id}")
                return str(chat_id)
            else:
                logger.info("No updates found. Send /start to your bot first!")
                return None
                
        except Exception as e:
            logger.error(f"Error getting chat ID: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test bot connection"""
        try:
            bot_info = asyncio.run(self.bot.get_me())
            logger.info(f"Bot connected: @{bot_info.username}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Quick usage example
if __name__ == "__main__":
    # Replace with your bot token from @BotFather
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    CHAT_ID = "YOUR_CHAT_ID_HERE"
    
    # Create bot instance
    bot = TelegramBot(BOT_TOKEN, CHAT_ID)
    
    # Test connection
    if bot.test_connection():
        print("✅ Bot connected successfully!")
        
        # Send test message
        bot.send_message_sync("🤖 Bot is online!")
        
        # Send test price alert
        test_product = {
            'name': 'iPhone 15 Pro',
            'new_price': 999.99,
            'old_price': 1099.99,
            'price_change': -9.09,
            'site': 'Amazon',
            'url': 'https://amazon.com/product'
        }
        bot.send_price_alert_sync(test_product)
    else:
        print("❌ Failed to connect to Telegram")
        print("Make sure your bot token is correct")
'''

print("✅ integrations/telegram_notification.py code created!")
