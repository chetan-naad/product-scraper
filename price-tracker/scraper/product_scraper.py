"""
Product scraper for extracting price information from websites
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
import logging

# Import our user agent manager
try:
    from utils.user_agents import user_agent_manager
except ImportError:
    # Fallback if running standalone
    class UserAgentManager:
        def get_random_ua(self):
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    user_agent_manager = UserAgentManager()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductScraper:
    """Scrapes product information from e-commerce websites"""

    def __init__(self):
        self.session = requests.Session()
        self.timeout = 10
        self.retry_attempts = 3
        self.delay_between_requests = 2

    def scrape_product(self, url: str) -> Optional[Dict]:
        """
        Scrape product information from URL

        Args:
            url: Product page URL

        Returns:
            Dictionary with product_name, price, site, availability
        """
        for attempt in range(self.retry_attempts):
            try:
                # Determine site type
                site = self._identify_site(url)

                # Get page content
                headers = self._get_headers()
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()

                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract product information based on site
                if site == 'amazon':
                    product_info = self._scrape_amazon(soup, url)
                elif site == 'flipkart':
                    product_info = self._scrape_flipkart(soup, url)
                elif site == 'ebay':
                    product_info = self._scrape_ebay(soup, url)
                else:
                    product_info = self._scrape_generic(soup, url)

                if product_info:
                    product_info['site'] = site
                    logger.info(f"Successfully scraped: {product_info['name']}")
                    return product_info
                else:
                    logger.warning(f"Could not extract product info from {url}")
                    return None

            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.delay_between_requests)
                else:
                    logger.error(f"All attempts failed for {url}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error scraping {url}: {e}")
                return None

        return None

    def _identify_site(self, url: str) -> str:
        """Identify which e-commerce site this URL belongs to"""
        domain = urlparse(url).netloc.lower()

        if 'amazon' in domain:
            return 'amazon'
        elif 'flipkart' in domain:
            return 'flipkart'
        elif 'ebay' in domain:
            return 'ebay'
        elif 'walmart' in domain:
            return 'walmart'
        elif 'myntra' in domain:
            return 'myntra'
        else:
            return 'generic'

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with rotating user agent"""
        return {
            'User-Agent': user_agent_manager.get_random_ua(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def _scrape_amazon(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Amazon-specific extraction logic"""
        product_name = None
        price = None
        availability = "In Stock"

        # Product name
        name_selectors = [
            'span#productTitle',
            'h1.a-size-large',
            'h1 span'
        ]

        for selector in name_selectors:
            element = soup.select_one(selector)
            if element:
                product_name = element.get_text(strip=True)
                break

        # Price extraction - Amazon has multiple formats
        price_selectors = [
            'span.a-price-whole',
            'span.a-price.a-text-price.a-size-medium.apexPriceToPay',
            'span.a-price-range',
            'span#priceblock_dealprice',
            'span#priceblock_ourprice',
            'span.a-offscreen'
        ]

        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self._parse_price(price_text)
                if price:
                    break

        # Availability
        availability_element = soup.select_one('div#availability span')
        if availability_element:
            avail_text = availability_element.get_text(strip=True).lower()
            if 'out of stock' in avail_text or 'unavailable' in avail_text:
                availability = "Out of Stock"

        if product_name and price:
            return {
                'name': product_name,
                'price': price,
                'url': url,
                'availability': availability
            }

        return None

    def _scrape_flipkart(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Flipkart-specific extraction logic"""
        product_name = None
        price = None

        # Product name
        name_selectors = [
            'span.B_NuCI',
            'h1.x-product-title-label',
            'span.G6XhBx'
        ]

        for selector in name_selectors:
            element = soup.select_one(selector)
            if element:
                product_name = element.get_text(strip=True)
                break

        # Price
        price_selectors = [
            'div._30jeq3._16Jk6d',
            'div._30jeq3',
            'div._1_WHN1'
        ]

        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self._parse_price(price_text)
                if price:
                    break

        if product_name and price:
            return {
                'name': product_name,
                'price': price,
                'url': url,
                'availability': 'In Stock'
            }

        return None

    def _scrape_ebay(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """eBay-specific extraction logic"""
        product_name = None
        price = None

        # Product name
        name_element = soup.select_one('h1#x-title-label-lbl')
        if name_element:
            product_name = name_element.get_text(strip=True)

        # Price
        price_selectors = [
            'span.u-flL.condText',
            'span.u-flL.secondary',
            'span#mm-saleDscPrc'
        ]

        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self._parse_price(price_text)
                if price:
                    break

        if product_name and price:
            return {
                'name': product_name,
                'price': price,
                'url': url,
                'availability': 'In Stock'
            }

        return None

    def _scrape_generic(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """
        Generic extraction for unknown sites
        Uses common patterns and meta tags
        """
        product_name = None
        price = None

        # Try meta tags for product name
        meta_name_tags = [
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'twitter:title'}),
            ('meta', {'property': 'product:name'}),
            ('title', {}),
            ('h1', {}),
        ]

        for tag, attrs in meta_name_tags:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    product_name = element.get('content')
                else:
                    product_name = element.get_text(strip=True)

                if product_name and len(product_name) > 10:
                    break

        # Try common price patterns
        price_patterns = [
            ('meta', {'property': 'product:price:amount'}),
            ('meta', {'property': 'og:price:amount'}),
            ('span', {'class': 'price'}),
            ('div', {'class': 'price'}),
            ('span', {'itemprop': 'price'}),
            ('div', {'itemprop': 'price'}),
            ('span', {'class': 'product-price'}),
            ('div', {'class': 'product-price'}),
        ]

        for tag, attrs in price_patterns:
            element = soup.find(tag, attrs)
            if element:
                if tag == 'meta':
                    price_text = element.get('content')
                else:
                    price_text = element.get_text(strip=True)

                if price_text:
                    price = self._parse_price(price_text)
                    if price:
                        break

        if product_name and price:
            return {
                'name': product_name[:200],  # Limit length
                'price': price,
                'url': url,
                'availability': 'Unknown'
            }

        return None

    def _parse_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None

        try:
            # Remove common currency symbols and whitespace
            clean_text = re.sub(r'[₹$€£¥,\s]', '', price_text)

            # Extract first numeric value (including decimals)
            match = re.search(r'(\d+\.?\d*)', clean_text)
            if match:
                price = float(match.group(1))
                # Reasonable price validation
                if 0.01 <= price <= 1000000:  # Between 1 cent and 1M
                    return price

            return None

        except (ValueError, AttributeError) as e:
            logger.error(f"Error parsing price '{price_text}': {e}")
            return None

    def search_products(self, search_term: str, sites: List[str] = None) -> List[Dict]:
        """
        Search for products across multiple sites

        Args:
            search_term: What to search for
            sites: List of sites to search (optional)

        Returns:
            List of product dictionaries
        """
        if sites is None:
            sites = ['amazon', 'flipkart']

        results = []

        for site in sites:
            try:
                if site == 'amazon':
                    search_url = f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}"
                elif site == 'flipkart':
                    search_url = f"https://www.flipkart.com/search?q={search_term.replace(' ', '+')}"
                else:
                    continue  # Skip unknown sites

                # This is a simplified version - full implementation would
                # scrape search results and extract individual product URLs
                logger.info(f"Would search {site} for '{search_term}'")
                # results.extend(self._scrape_search_results(search_url, site))

            except Exception as e:
                logger.error(f"Error searching {site}: {e}")

        return results

    def close(self):
        """Close the session"""
        self.session.close()


# Example usage and testing
if __name__ == "__main__":
    scraper = ProductScraper()

    # Test URLs (replace with actual product URLs)
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",  # Example Amazon URL
        "https://www.flipkart.com/sample-product"  # Example Flipkart URL
    ]

    for url in test_urls:
        result = scraper.scrape_product(url)
        if result:
            print(f"Scraped: {result}")
        else:
            print(f"Failed to scrape: {url}")

    scraper.close()
