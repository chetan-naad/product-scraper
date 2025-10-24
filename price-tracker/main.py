"""
Main application entry point for Advanced Product Price Tracker
Supports multiple run modes: CLI, service, and dashboard
"""
import sys
import argparse
import schedule
import time
from datetime import datetime
import logging

# Import our modules
try:
    from utils.database import DatabaseManager
    from scraper.product_scraper import ProductScraper
    from utils.notifier import MultiNotifier
    from ml.price_predictor import PricePredictor
    import config
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are in the correct directories")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PriceTrackerService:
    """Main service for automated price tracking"""

    def __init__(self):
        self.db = DatabaseManager(config.DATABASE_PATH)
        self.scraper = ProductScraper()
        self.notifier = MultiNotifier()
        self.predictor = PricePredictor()
        logger.info("Price Tracker Service initialized")

    def check_all_prices(self):
        """Check prices for all tracked products"""
        logger.info("="*60)
        logger.info(f"Starting price check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60)

        products = self.db.get_all_products()

        if not products:
            logger.info("No products to track. Add products first.")
            return

        logger.info(f"Checking {len(products)} products...")

        alerts_sent = 0
        successful_checks = 0

        for i, product in enumerate(products, 1):
            logger.info(f"[{i}/{len(products)}] Checking: {product['name']}")

            try:
                # Scrape current price
                result = self.scraper.scrape_product(product['url'])

                if result:
                    # Update database
                    update_info = self.db.update_price(
                        product['url'], 
                        result['price'], 
                        result.get('site', ''),
                        result.get('availability', 'In Stock')
                    )

                    if update_info:
                        old_price = update_info['old_price']
                        new_price = update_info['new_price']
                        successful_checks += 1

                        if old_price:
                            change = update_info['price_change']
                            symbol = "📉" if change < 0 else "📈"
                            logger.info(f"  {symbol} Price: ${old_price:.2f} → ${new_price:.2f} ({change:+.2f}%)")
                        else:
                            logger.info(f"  ✓ Initial price: ${new_price:.2f}")

                        # Check if alert should be sent
                        if update_info['should_alert']:
                            logger.info(f"  ⚠️  ALERT! Price dropped below ${update_info['alert_price']:.2f}")

                            # Prepare notification data
                            notification_data = {
                                **update_info,
                                'url': product['url'],
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }

                            # Send notifications
                            channels = ['email']
                            if config.TELEGRAM_BOT_TOKEN:
                                channels.append('telegram')

                            results = self.notifier.send_price_alert(notification_data, channels)

                            if any(results.values()):
                                logger.info(f"  ✉️  Alerts sent: {[k for k, v in results.items() if v]}")
                                alerts_sent += 1
                            else:
                                logger.warning(f"  ❌ Failed to send alerts")

                        # Add delay between requests
                        time.sleep(config.SLEEP_BETWEEN_REQUESTS)
                else:
                    logger.warning(f"  ✗ Failed to scrape price for {product['name']}")

            except Exception as e:
                logger.error(f"  ✗ Error checking {product['name']}: {e}")

        logger.info("="*60)
        logger.info(f"Price check completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Results: {successful_checks}/{len(products)} successful, {alerts_sent} alerts sent")
        logger.info("="*60)

    def train_ml_models(self):
        """Train ML models for all products with sufficient history"""
        logger.info("Training ML models...")

        products = self.db.get_all_products()
        trained_models = 0

        for product in products:
            try:
                # Get price history
                history = self.db.get_price_history(product['id'], days=90)

                if len(history) >= 30:  # Need at least 30 data points
                    metrics = self.predictor.train(history, product['id'])

                    if 'error' not in metrics:
                        logger.info(f"Model trained for {product['name']} - R²: {metrics.get('test_r2', 0):.3f}")
                        trained_models += 1
                    else:
                        logger.warning(f"Failed to train model for {product['name']}: {metrics['error']}")
                else:
                    logger.info(f"Insufficient data for {product['name']} ({len(history)} points)")

            except Exception as e:
                logger.error(f"Error training model for {product['name']}: {e}")

        logger.info(f"ML training completed. {trained_models} models trained.")

    def generate_predictions(self):
        """Generate price predictions for all products"""
        logger.info("Generating price predictions...")

        products = self.db.get_all_products()
        predictions_generated = 0

        for product in products:
            try:
                # Load model for this product
                if self.predictor.load_model(f"model_product_{product['id']}"):
                    # Get recent history
                    recent_history = self.db.get_price_history(product['id'], days=30)

                    if len(recent_history) >= 10:
                        predictions = self.predictor.predict_next_days(recent_history, days=7)

                        if 'predictions' in predictions:
                            recommendation = self.predictor.get_buy_recommendation(
                                predictions['predictions'], 
                                product['current_price']
                            )

                            logger.info(f"Prediction for {product['name']}: {recommendation['recommendation']}")
                            predictions_generated += 1

            except Exception as e:
                logger.error(f"Error generating prediction for {product['name']}: {e}")

        logger.info(f"Predictions generated for {predictions_generated} products")

    def send_daily_report(self):
        """Send daily summary report"""
        logger.info("Sending daily report...")

        try:
            # Get analytics data
            analytics = self.db.get_analytics_data()
            best_deals = self.db.get_best_deals(limit=10)

            # Prepare report data
            report_data = {
                'total_products': analytics.get('total_products', 0),
                'active_alerts': analytics.get('active_alerts', 0),
                'best_deals': best_deals,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Send email report
            if config.EMAIL_ENABLED:
                success = self.notifier.email_notifier.send_daily_report(best_deals)
                if success:
                    logger.info("Daily report sent successfully")
                else:
                    logger.error("Failed to send daily report")

        except Exception as e:
            logger.error(f"Error sending daily report: {e}")

    def run_scheduled(self):
        """Run the service with scheduled tasks"""
        logger.info("\n" + "="*60)
        logger.info("🚀 ADVANCED PRODUCT PRICE TRACKER SERVICE")
        logger.info("="*60)
        logger.info(f"Check interval: Every {config.CHECK_INTERVAL_HOURS} hours")
        logger.info(f"Email alerts: {'Enabled' if config.EMAIL_ENABLED else 'Disabled'}")
        logger.info(f"Telegram alerts: {'Enabled' if config.TELEGRAM_BOT_TOKEN else 'Disabled'}")
        logger.info(f"ML predictions: {'Enabled' if config.ENABLE_PREDICTIONS else 'Disabled'}")
        logger.info(f"Database: {config.DATABASE_PATH}")
        logger.info("="*60 + "\n")

        # Schedule tasks
        schedule.every(config.CHECK_INTERVAL_HOURS).hours.do(self.check_all_prices)
        schedule.every().day.at("09:00").do(self.send_daily_report)

        if config.ENABLE_PREDICTIONS:
            schedule.every(config.MODEL_RETRAIN_DAYS).days.do(self.train_ml_models)
            schedule.every(12).hours.do(self.generate_predictions)

        # Run initial tasks
        logger.info("Running initial price check...")
        self.check_all_prices()

        if config.ENABLE_PREDICTIONS:
            logger.info("Training initial ML models...")
            self.train_ml_models()

        logger.info(f"\nService is now running. Press Ctrl+C to stop.")
        logger.info(f"Next price check scheduled in {config.CHECK_INTERVAL_HOURS} hours\n")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\n\nStopping Price Tracker Service...")
            self.scraper.close()
            logger.info("Service stopped. Goodbye!")

    def run_once(self):
        """Run price check once and exit"""
        logger.info("Running one-time price check...")
        self.check_all_prices()

        if config.ENABLE_PREDICTIONS:
            self.generate_predictions()

        self.scraper.close()
        logger.info("One-time check completed.")

    def add_sample_products(self):
        """Add sample products for testing"""
        sample_products = [
            {
                'name': 'iPhone 15 Pro Max',
                'url': 'https://www.amazon.com/dp/B0CHBQT16C',  # Example URL
                'alert_price': 1000.0,
                'category': 'Electronics',
                'site': 'Amazon'
            },
            {
                'name': 'Sony WH-1000XM5 Headphones',
                'url': 'https://www.amazon.com/dp/B09XS7JWHH',  # Example URL
                'alert_price': 300.0,
                'category': 'Electronics',
                'site': 'Amazon'
            }
        ]

        for product in sample_products:
            success = self.db.add_product(
                product['name'],
                product['url'],
                product['alert_price'],
                product['category'],
                product['site']
            )

            if success:
                logger.info(f"Added sample product: {product['name']}")
            else:
                logger.info(f"Sample product already exists: {product['name']}")


def launch_dashboard():
    """Launch Streamlit dashboard"""
    try:
        import subprocess
        import os

        # Check if streamlit_dashboard.py exists
        dashboard_file = "gui/streamlit_dashboard.py"
        if not os.path.exists(dashboard_file):
            dashboard_file = "streamlit_dashboard.py"

        if os.path.exists(dashboard_file):
            logger.info(f"Launching Streamlit dashboard: {dashboard_file}")
            subprocess.run(["streamlit", "run", dashboard_file])
        else:
            logger.error("Dashboard file not found. Please ensure streamlit_dashboard.py exists.")

    except ImportError:
        logger.error("Streamlit not installed. Install with: pip install streamlit")
    except Exception as e:
        logger.error(f"Error launching dashboard: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Advanced Product Price Tracker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode dashboard    # Launch web dashboard (default)
  python main.py --mode service      # Run as background service
  python main.py --mode once         # Single price check
  python main.py --mode add-samples  # Add sample products
        """
    )

    parser.add_argument(
        '--mode',
        choices=['dashboard', 'service', 'once', 'add-samples', 'train-models'],
        default='dashboard',
        help='Run mode (default: dashboard)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize service
    try:
        service = PriceTrackerService()
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        return 1

    # Execute based on mode
    if args.mode == 'dashboard':
        logger.info("Starting dashboard mode...")
        launch_dashboard()

    elif args.mode == 'service':
        logger.info("Starting service mode...")
        service.run_scheduled()

    elif args.mode == 'once':
        logger.info("Starting one-time check...")
        service.run_once()

    elif args.mode == 'add-samples':
        logger.info("Adding sample products...")
        service.add_sample_products()

    elif args.mode == 'train-models':
        logger.info("Training ML models...")
        service.train_ml_models()

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
