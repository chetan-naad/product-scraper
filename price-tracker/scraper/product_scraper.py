"""
Product scraper for extracting price and image information from websites
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Optional, Dict
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
    logger.info("✅ Selenium is available for Meesho/Myntra scraping")
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("⚠️ Selenium not available - Meesho/Myntra won't work")

class ProductScraper:
    """Scrapes product information from e-commerce websites"""

    def __init__(self):
        self.session = requests.Session()
        self.timeout = 15
        self.retry_attempts = 3
        self.delay_between_requests = 2

    def scrape_product(self, url: str) -> Optional[Dict]:
        """Scrape product information from URL"""
        site = self._identify_site(url)
        logger.info(f"🔍 Starting to scrape {site} product: {url}")
        
        # Use Selenium for JavaScript sites
        if site in ['meesho', 'myntra'] and SELENIUM_AVAILABLE:
            logger.info(f"🌐 Using Selenium for {site}")
            return self._scrape_with_selenium(url, site)
        
        # Use regular scraper for other sites
        for attempt in range(self.retry_attempts):
            try:
                headers = self._get_headers()
                logger.info(f"Attempt {attempt + 1}: Scraping {site} - {url}")
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                if site == 'amazon':
                    product_info = self._scrape_amazon(soup, url)
                elif site == 'flipkart':
                    product_info = self._scrape_flipkart(soup, url)
                elif site == 'ebay':
                    product_info = self._scrape_ebay(soup, url)
                else:
                    product_info = self._scrape_generic(soup, url)

                if product_info and product_info.get('name') and product_info.get('price'):
                    product_info['site'] = site
                    logger.info(f"✅ Successfully scraped: {product_info['name']} - ₹{product_info['price']}")
                    return product_info
                else:
                    logger.warning(f"⚠️ Attempt {attempt + 1}: Incomplete data - name: {bool(product_info.get('name'))}, price: {bool(product_info.get('price'))}")

            except requests.RequestException as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.delay_between_requests)
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")

        logger.warning(f"⚠️ All scraping attempts failed for {url}")
        return None

    def _scrape_with_selenium(self, url: str, site: str) -> Optional[Dict]:
        """Use Selenium for JavaScript-heavy sites"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            
            time.sleep(2)  # Extra wait for dynamic content
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
            
            # Extract data based on site
            if site == 'meesho':
                return self._extract_meesho(soup, url)
            elif site == 'myntra':
                return self._extract_myntra(soup, url)
                
        except Exception as e:
            logger.error(f"❌ Selenium scraping failed: {e}")
            return None

    def _extract_meesho(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Extract Meesho data from rendered HTML"""
        name = None
        price = None
        image = None

        # Product name - find longest text element
        for elem in soup.find_all(['h1', 'h2', 'span', 'p']):
            text = elem.get_text(strip=True)
            if len(text) > 10 and len(text) < 200:
                name = text
                break

        # Price - search for ₹ symbol
        for elem in soup.find_all(string=re.compile(r'₹\d+')):
            price_text = elem.strip()
            parsed = self._parse_price(price_text)
            if parsed and parsed > 10:
                price = parsed
                break

        # Image
        img_elem = soup.find('img')
        if img_elem:
            image = img_elem.get('src') or img_elem.get('data-src')

        if name and price:
            logger.info(f"✅ Meesho: {name[:50]}... - ₹{price}")
            return {'name': name, 'price': price, 'url': url, 'image_url': image, 'availability': 'In Stock'}
    
        logger.warning(f"⚠️ Meesho extraction failed: name={bool(name)}, price={bool(price)}")
        return None


    def _extract_myntra(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        name = None
        price = None
        image = None

        # Name extraction (already works for you)
        name_elem = soup.select_one('h1.pdp-title') or soup.select_one('h1.pdp-name') or soup.select_one('h1')
        if name_elem:
            name = name_elem.get_text(strip=True)
    
        # Price extraction (already works for you)
        price_elem = soup.select_one('span.pdp-price strong') or soup.select_one('strong.pdp-price') or soup.select_one('span.pdp-price')
        if price_elem:
            price = self._parse_price(price_elem.get_text(strip=True))
    
        # Image extraction - get first large product image
        img_elem = None
    
        # Myntra main product image often has these classes:
        img_elem = soup.select_one('img.img-responsive.img-center') or \
            soup.select_one('div.image-grid-image img') or \
            soup.select_one('img.pdp-img') or \
            soup.select_one('img[alt][src]')
    
        if img_elem:
            image = img_elem.get('src')
    
        # As ultimate fallback, try og:image meta tag
        if not image:
            meta_img = soup.find('meta', {'property': 'og:image'})
            if meta_img:
                image = meta_img.get('content')
    
        if name and price:
            logger.info(f"✅ Myntra: {name[:50]}... - ₹{price} | Img: {bool(image)}")
            return {'name': name, 'price': price, 'url': url, 'image_url': image, 'availability': 'In Stock'}
        return None


    def _identify_site(self, url: str) -> str:
        """Identify which e-commerce site"""
        domain = urlparse(url).netloc.lower()
        if 'amazon' in domain:
            return 'amazon'
        elif 'flipkart' in domain:
            return 'flipkart'
        elif 'ebay' in domain:
            return 'ebay'
        elif 'meesho' in domain:
            return 'meesho'
        elif 'myntra' in domain:
            return 'myntra'
        else:
            return 'generic'

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def _scrape_flipkart(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Flipkart scraper"""
        name = None
        price = None
        image = None

        name_selectors = ['span.VU-ZEz', 'span.B_NuCI', 'h1.yhB1nd']
        for selector in name_selectors:
            elem = soup.select_one(selector)
            if elem:
                name = elem.get_text(strip=True)
                break

        price_selectors = ['div.Nx9bqj.CxhGGd', 'div._30jeq3._16Jk6d', 'div._30jeq3']
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                price = self._parse_price(elem.get_text(strip=True))
                if price:
                    break

        img_selectors = ['img._53J4C-', 'img._396cs4']
        for selector in img_selectors:
            elem = soup.select_one(selector)
            if elem:
                image = elem.get('src')
                break

        if name and price:
            return {'name': name, 'price': price, 'url': url, 'image_url': image, 'availability': 'In Stock'}
        return None

    def _scrape_amazon(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Amazon scraper"""
        name = None
        price = None
        image = None

        name_elem = soup.select_one('span#productTitle')
        if name_elem:
            name = name_elem.get_text(strip=True)

        price_elem = soup.select_one('span.a-price-whole') or soup.select_one('span#priceblock_ourprice')
        if price_elem:
            price = self._parse_price(price_elem.get_text())

        img_elem = soup.select_one('img#landingImage') or soup.select_one('img.a-dynamic-image')
        if img_elem:
            image = img_elem.get('data-old-hires') or img_elem.get('src')

        if name and price:
            return {'name': name, 'price': price, 'url': url, 'image_url': image, 'availability': 'In Stock'}
        return None

    def _scrape_ebay(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """eBay scraper"""
        name = None
        price = None
        image = None

        name_selectors = ['h1.x-item-title__mainTitle span', 'h1#itemTitle']
        for selector in name_selectors:
            elem = soup.select_one(selector)
            if elem:
                name = elem.get_text(strip=True).replace('Details about', '').strip()
                break

        price_selectors = ['div.x-price-primary span.ux-textspans', 'span.x-price-approx__price']
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                price = self._parse_price(elem.get_text(strip=True))
                if price:
                    break

        img_selectors = ['div.ux-image-carousel-item img', 'img#icImg']
        for selector in img_selectors:
            elem = soup.select_one(selector)
            if elem:
                image = elem.get('src')
                break

        if name and price:
            return {'name': name, 'price': price, 'url': url, 'image_url': image, 'availability': 'In Stock'}
        return None

    def _scrape_generic(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Generic fallback"""
        name = None
        price = None
        image = None

        title_tag = soup.find('meta', {'property': 'og:title'}) or soup.find('h1')
        if title_tag:
            name = title_tag.get('content') or title_tag.get_text(strip=True)

        price_tag = soup.find('meta', {'property': 'product:price:amount'})
        if price_tag:
            price = self._parse_price(price_tag.get('content'))

        img_tag = soup.find('meta', {'property': 'og:image'})
        if img_tag:
            image = img_tag.get('content')

        if name and price:
            return {'name': name, 'price': price, 'url': url, 'image_url': image, 'availability': 'Unknown'}
        return None

    def _parse_price(self, text: str) -> Optional[float]:
        """Convert text to numeric price"""
        if not text:
            return None
        try:
            cleaned = re.sub(r"[₹$,€£¥\s]", "", text)
            numbers = re.findall(r"\d+\.?\d*", cleaned)
            if numbers:
                price = float(numbers[0])
                return price if price > 0 else None
        except Exception as e:
            logger.error(f"Price parse error: {text}")
        return None

    def close(self):
        """Close the session"""
        self.session.close()