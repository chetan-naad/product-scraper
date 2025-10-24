"""
User Agent Management for Web Scraping
"""
from fake_useragent import UserAgent
import random

class UserAgentManager:
    """Manages user agent rotation for requests"""

    def __init__(self):
        try:
            self.ua = UserAgent()
        except Exception:
            # Fallback if fake_useragent fails
            self.ua = None

        # Fallback user agents
        self.fallback_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def get_random_ua(self):
        """Get a random user agent string"""
        try:
            if self.ua:
                return self.ua.random
        except Exception:
            pass

        # Use fallback
        return random.choice(self.fallback_agents)

    def get_chrome_ua(self):
        """Get a Chrome user agent"""
        try:
            if self.ua:
                return self.ua.chrome
        except Exception:
            pass

        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def get_firefox_ua(self):
        """Get a Firefox user agent"""
        try:
            if self.ua:
                return self.ua.firefox
        except Exception:
            pass

        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0"

    def get_mobile_ua(self):
        """Get a mobile user agent"""
        mobile_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 12; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ]
        return random.choice(mobile_agents)

# Create a global instance
user_agent_manager = UserAgentManager()
