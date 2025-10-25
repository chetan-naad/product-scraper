# 🛍️ Price Tracker Pro

A comprehensive price tracking application that monitors product prices across multiple e-commerce platforms and sends intelligent alerts when prices drop below your target.

## ✨ Features

### 🎯 **Core Functionality**
- **Multi-Platform Tracking**: Monitor products from Amazon, Flipkart, eBay, and other major e-commerce sites
- **Smart Price Alerts**: Get notified when prices drop below your target
- **Real-Time Monitoring**: Continuous price tracking with configurable intervals
- **Historical Analysis**: Track price trends and patterns over time

### 📊 **Analytics & Insights**
- **Price Trends**: Interactive charts showing price history
- **Best Deals Detection**: Automatically identify products with significant discounts
- **Price Distribution**: Visualize price patterns across different sites
- **Site Comparison**: Compare average prices across platforms

### 🤖 **AI-Powered Predictions**
- **Price Forecasting**: ML models predict future price movements
- **Trend Analysis**: Detect price trends, volatility, and support/resistance levels
- **Buy Recommendations**: AI-powered suggestions for optimal purchase timing
- **Multiple Models**: Random Forest and Linear Regression for different prediction scenarios

### 📧 **Smart Notifications**
- **Email Alerts**: Rich HTML emails with detailed product information
- **Telegram Integration**: Instant notifications via Telegram bot
- **Daily Reports**: Comprehensive summaries of tracked products
- **Customizable Alerts**: Set different alert prices for different products

### 🎨 **Modern Interface**
- **Streamlit Dashboard**: Beautiful, responsive web interface
- **Interactive Charts**: Plotly-powered visualizations
- **Mobile-Friendly**: Responsive design works on all devices
- **Dark/Light Themes**: Customizable interface themes

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd price-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings**
   ```bash
   cp config.py.example config.py
   # Edit config.py with your email and API credentials
   ```

4. **Initialize the database**
   ```bash
   python -c "from utils.database import DatabaseManager; db = DatabaseManager(); print('Database initialized!')"
   ```

5. **Run the application**
   ```bash
   streamlit run gui/streamlit_dashboard.py
   ```

## 📁 Project Structure

```
price-tracker/
├── gui/
│   └── streamlit_dashboard.py    # Main web interface
├── utils/
│   ├── database.py              # Database operations
│   ├── notifier.py              # Email & Telegram notifications
│   └── scraper.py               # Web scraping utilities
├── ml/
│   └── price_predictor.py       # AI prediction models
├── integrations/
│   └── telegram_notification.py # Telegram bot integration
├── data/
│   └── products.db              # SQLite database
├── config.py                    # Configuration settings
├── main.py                      # Main application entry point
└── requirements.txt             # Python dependencies
```

## 🔧 Configuration

### Email Notifications
```python
# In config.py
EMAIL_ENABLED = True
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
```

### Telegram Bot
```python
# In config.py
TELEGRAM_BOT_TOKEN = "your-bot-token"
TELEGRAM_CHAT_ID = "your-chat-id"
```

### Database
The application uses SQLite for data storage. The database is automatically created in the `data/` directory.

## 📊 Usage

### Adding Products
1. Open the Streamlit dashboard
2. Navigate to "Add Product"
3. Enter product URL, alert price, and category
4. The system will automatically scrape current price and start tracking

### Viewing Analytics
1. Go to "Analytics" page
2. View price trends, distributions, and site comparisons
3. Use interactive charts to analyze data

### AI Predictions
1. Navigate to "AI Predictions" page
2. Select a product and prediction model
3. Set prediction horizon (days)
4. View price forecasts and buy recommendations

### Managing Alerts
- Set custom alert prices for each product
- Receive instant notifications when prices drop
- View daily reports with all tracked products

## 🎯 Key Features in Detail

### Smart Deal Detection
The system automatically identifies the best deals using two methods:
- **Historical Discounts**: Products currently priced below their historical maximum
- **Alert Price Triggers**: Products below your set alert price

### Advanced Analytics
- **Price Trends**: Track price movements over time
- **Volatility Analysis**: Understand price stability
- **Support/Resistance**: Identify key price levels
- **Site Comparison**: Compare prices across different platforms

### AI-Powered Insights
- **Price Forecasting**: Predict future price movements
- **Trend Detection**: Identify upward/downward trends
- **Volatility Calculation**: Measure price stability
- **Buy Recommendations**: Optimal purchase timing suggestions

### Professional Notifications
- **Rich HTML Emails**: Beautiful, responsive email templates
- **Detailed Information**: Current price, alert price, savings amount
- **Action Buttons**: Direct links to product pages
- **Smart Messaging**: Clear, actionable notifications

## 🔒 Security & Privacy

- **Local Database**: All data stored locally on your machine
- **Secure Credentials**: API keys and passwords stored securely
- **No Data Sharing**: Your tracking data remains private
- **Encrypted Communications**: Secure email and API communications

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📈 Performance

- **Efficient Scraping**: Optimized web scraping with rate limiting
- **Smart Caching**: Reduces redundant API calls
- **Database Optimization**: Indexed queries for fast data retrieval
- **Memory Management**: Efficient handling of large datasets

## 🐛 Troubleshooting

### Common Issues

**Email notifications not working**
- Check SMTP credentials in config.py
- Ensure app passwords are used for Gmail
- Verify firewall settings

**Scraping failures**
- Check internet connection
- Verify product URLs are accessible
- Review rate limiting settings

**Database errors**
- Ensure data directory exists
- Check file permissions
- Verify SQLite installation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the wiki for detailed guides
- **Community**: Join our Discord server for discussions

## 🎉 Acknowledgments

- **Streamlit**: For the amazing web framework
- **Plotly**: For interactive visualizations
- **Scikit-learn**: For machine learning capabilities
- **SQLite**: For reliable data storage

---

**Made with ❤️ for smart shoppers everywhere!**

*Track prices, save money, shop smarter!* 🛍️💰
