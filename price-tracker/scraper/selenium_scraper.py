"""
Selenium-based scraper for JavaScript-heavy sites (Meesho, Myntra)
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging
import re
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumScraper:
    """Uses Selenium for JavaScript-rendered sites"""
    
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')  # Run without opening browser
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    def scrape_meesho(self, url: str) -> Optional[Dict]:
        """Scrape Meesho product"""
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
            driver.get(url)

            # Longer wait for Meesho
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'₹')]"))

            )
        
            time.sleep(1)  # Extra wait for dynamic content
        
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
        
            # Product name - try multiple patterns
            ame = None
            for elem in soup.find_all(['h1', 'h2', 'span', 'p']):
                text = elem.get_text(strip=True)
                if len(text) > 10 and len(text) < 200:  # Likely a product name
                    name = text
                    break
        
            # Price - search for any text with ₹ symbol
            price = None
            for elem in soup.find_all(string=re.compile(r'₹\d+')):
                price_text = elem.strip()
                parsed = self._parse_price(price_text)
                if parsed and parsed > 10:  # Must be > ₹10
                    price = parsed
                    break
        
            # Image - first image tag
            image = None
            img_elem = soup.find('img')
            if img_elem:
                image = img_elem.get('src') or img_elem.get('data-src')
        
            if name and price:
                logger.info(f"✅ Meesho scraped: {name[:50]}... - ₹{price}")
                return {'name': name, 'price': price, 'url': url, 'image_url': image, 'availability': 'In Stock'}
        
            logger.warning(f"⚠️ Meesho: Found name={bool(name)}, price={bool(price)}")
            return None
        
        except Exception as e:
            logger.error(f"❌ Meesho scraping failed: {e}")
            return None

    
    def scrape_myntra(self, url: str) -> Optional[Dict]:
        """Scrape Myntra product"""
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pdp-title"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Product name
            name = None
            name_elem = soup.select_one('h1.pdp-title') or soup.select_one('h1.pdp-name')
            if name_elem:
                name = name_elem.get_text(strip=True)
            
            # Price
            price = None
            price_elem = soup.select_one('span.pdp-price strong') or soup.select_one('strong')
            if price_elem:
                price = self._parse_price(price_elem.get_text(strip=True))
            
            # Image
            image = None
            img_elem = soup.select_one('div.image-grid-image img')
            if img_elem:
                image = img_elem.get('src')
            
            driver.quit()
            
            if name and price:
                logger.info(f"✅ Myntra scraped: {name} - ₹{price}")
                return {'name': name, 'price': price, 'url': url, 'image_url': image, 'availability': 'In Stock'}
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Myntra scraping failed: {e}")
            return None
    
    def _parse_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        if not text:
            return None
        try:
            cleaned = re.sub(r"[₹$,€£¥\s]", "", text)
            numbers = re.findall(r"\d+\.?\d*", cleaned)
            if numbers:
                return float(numbers[0])
        except:
            pass
        return None
