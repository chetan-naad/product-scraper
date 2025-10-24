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
    page_title="Price Tracker Pro",
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
def format_price(amount, currency=None):
    if currency is None:
        settings = load_settings()
        currency = settings.get('currency', 'USD')
    symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}
    symbol = symbols.get(currency, '$')
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
            'currency': 'USD',
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
                '💰 Current': format_price(deal['current_price']),
                '💸 Original': format_price(deal.get('original_price', deal['current_price'])),
                '📊 Discount': f"{deal['discount_percent']:.0f}%",
                '🛒 Site': deal.get('site', 'N/A')
            } for deal in best_deals])
            st.dataframe(deals_df, use_container_width=True, hide_index=True)
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
            settings = load_settings()
            currency_symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}
            currency_symbol = currency_symbols.get(settings.get('currency', 'USD'), '$')
            with col1:
                product_name = st.text_input("Product Name", placeholder="e.g., iPhone 15 Pro")
                product_url = st.text_input("Product URL", placeholder="https://...")
                alert_price = st.number_input(f"Alert Price ({currency_symbol})", min_value=0.0, value=100.0)
            with col2:
                sites = st.multiselect(
                    "Sites to Track",
                    ["Amazon", "Flipkart", "eBay", "Walmart"],
                    default=["Amazon"]
                )
                category = st.selectbox(
                    "Category",
                    ["Electronics", "Fashion", "Home", "Books", "Sports", "Gaming", "Beauty", "Other"]
                )
                enable_alerts = st.checkbox("Enable Price Alerts", value=True)
            st.markdown("---")
            if st.button("✨ Add Product", type="primary", use_container_width=True):
                if product_name and product_url:
                    success = st.session_state.db.add_product(
                        product_name, product_url, alert_price, category, sites[0] if sites else "Unknown"
                    )
                    if success:
                        st.success(f"✅ Successfully added {product_name}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to add product. It may already exist.")
                else:
                    st.warning("⚠️ Please enter both product name and URL")
        
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
            
            # Display products
            for product in filtered_products:
                status = '🔴 ALERT!' if (product['current_price'] and product['alert_price'] and 
                                        product['current_price'] <= product['alert_price']) else '🟢 Active'
                
                st.markdown(f"""
                    <div class='metric-card'>
                        <h3 style='margin: 0 0 8px 0;'>{product['name'][:60]}</h3>
                        <p style='margin: 4px 0; opacity: 0.8;'>
                            <strong>Current:</strong> {format_price(product['current_price']) if product['current_price'] else 'N/A'} | 
                            <strong>Alert:</strong> {format_price(product['alert_price']) if product['alert_price'] else 'N/A'}
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
                    if st.button("🔍 View Details", key=f"view_{product['id']}", use_container_width=True):
                        st.info(f"Product URL: {product['url']}")
                with col2:
                    if st.button("📈 Price History", key=f"history_{product['id']}", use_container_width=True):
                        st.info("Price history feature coming soon!")
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{product['id']}", use_container_width=True):
                        if st.session_state.db.delete_product(product['id']):
                            st.success("✅ Product deleted!")
                            time.sleep(0.5)
                            st.rerun()
        else:
            st.info("📭 No products tracked yet. Add your first product above!")

elif page == "📈 Analytics":
    st.markdown("<h1>📈 Price Analytics & Insights</h1>", unsafe_allow_html=True)
    time_range = st.select_slider(
        "Select Time Range",
        options=["7 Days", "30 Days", "90 Days", "1 Year"],
        value="30 Days"
    )
    st.info("📊 Analytics features coming soon! Connect to real price history data.")

elif page == "🤖 AI Predictions":
    st.markdown("<h1>🤖 AI-Powered Predictions</h1>", unsafe_allow_html=True)
    st.info("🔮 ML prediction features coming soon! Train models with historical data.")
    if backend_available:
        products = st.session_state.db.get_all_products()
        if products:
            selected = st.selectbox(
                "Select Product",
                options=[p['name'] for p in products]
            )
            st.write(f"Selected: {selected}")
            st.write("Prediction model will analyze price history and forecast trends.")

elif page == "⚙️ Settings":
    st.markdown("<h1>⚙️ Settings & Configuration</h1>", unsafe_allow_html=True)
    current_settings = load_settings()
    tab1, tab2, tab3 = st.tabs(["🔔 Notifications", "🎨 Appearance", "👤 Profile"])
    
    with tab1:
        st.subheader("Notification Preferences")
        col1, col2 = st.columns(2)
        with col1:
            email_enabled = st.checkbox("📧 Email Notifications", value=True)
            email_addr = st.text_input("Email Address", value=current_settings.get('email_address', 'user@example.com'))
            telegram_enabled = st.checkbox("📱 Telegram Alerts", value=current_settings.get('telegram_enabled', False))
            telegram_token = st.text_input("Telegram Bot Token", type="password", value=current_settings.get('telegram_token', ''))
        with col2:
            alert_freq = st.slider("Alert Frequency (hours)", 1, 24, current_settings.get('alert_freq', 6))
            price_threshold = st.slider("Price Drop Threshold (%)", 1, 50, current_settings.get('price_threshold', 10))
        if st.button("💾 Save Notification Settings", key="save_notif", use_container_width=True):
            current_settings['email_address'] = email_addr
            current_settings['telegram_token'] = telegram_token
            current_settings['telegram_enabled'] = telegram_enabled
            current_settings['alert_freq'] = alert_freq
            current_settings['price_threshold'] = price_threshold
            save_settings(current_settings)
            st.success("✅ Settings saved successfully!")
            time.sleep(1)
            st.rerun()
    
    with tab2:
        st.subheader("Appearance")
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "INR"], index=["USD", "EUR", "GBP", "INR"].index(current_settings.get('currency', 'USD')))
        timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "IST"], index=["UTC", "EST", "PST", "IST"].index(current_settings.get('timezone', 'IST')))
        
        if st.button("💾 Save Appearance Settings", use_container_width=True):
            current_settings['currency'] = currency
            current_settings['timezone'] = timezone
            save_settings(current_settings)
            st.success("✅ Settings saved!")
            time.sleep(0.5)
            st.rerun()
    
    with tab3:
        st.subheader("User Profile")
        username = st.text_input("Username", value=current_settings.get('username', 'pricetracker_user'))
        
        if st.button("💾 Save Profile", key="save_profile", use_container_width=True):
            current_settings['username'] = username
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
