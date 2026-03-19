"""
Selenium utilities for web driver management and common operations.
"""

import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
#-----------------
#from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options import Options
#options = Options()
#options.headless = True  # keep headless if you don’t want Chrome window
#options.add_argument("--no-sandbox")
#options.add_argument("--disable-dev-shm-usage")
#service = Service(ChromeDriverManager().install())
# Force 64-bit ChromeDriver and correct version
#service = Service(
#    ChromeDriverManager(version="146.0.7680.80").install()
#)


#driver = webdriver.Chrome(service=service, options=options)
#-----------------

logger = logging.getLogger(__name__)


class SeleniumDriver:
    """Manages Selenium WebDriver lifecycle."""
    
    def __init__(self, browser: str = 'chrome', headless: bool = True):
        """
        Initialize Selenium WebDriver.
        
        Args:
            browser: 'chrome' or 'firefox'
            headless: Run in headless mode (no UI)
        """
        self.browser = browser.lower()
        self.headless = headless
        self.driver = None
        self._initialize_driver()
    
    def _initialize_driver(self):
        """Initialize and configure the WebDriver."""
        try:
            if self.browser == 'chrome':
                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
            elif self.browser == 'firefox':
                options = webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")
            
            logger.info(f"WebDriver initialized: {self.browser}")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """
        Wait for element to be present in DOM.
        
        Args:
            by: Selenium By selector (By.XPATH, By.CSS_SELECTOR, etc.)
            value: Selector value
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement: Found element
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            logger.info(f"Element found with selector: {value}")
            return element
        except Exception as e:
            logger.warning(f"Element not found: {value} - {e}")
            return None
    
    def wait_for_elements(self, by: By, value: str, timeout: int = 10):
        """
        Wait for multiple elements to be present in DOM.
        
        Args:
            by: Selenium By selector
            value: Selector value
            timeout: Maximum wait time in seconds
            
        Returns:
            List: Found elements
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            logger.info(f"Found {len(elements)} elements with selector: {value}")
            return elements
        except Exception as e:
            logger.warning(f"Elements not found: {value} - {e}")
            return []
    
    def get_page_source(self):
        """Get current page HTML source."""
        return self.driver.page_source
    
    def get_current_url(self):
        """Get current page URL."""
        return self.driver.current_url
    
    def visit(self, url: str):
        """Visit a URL and wait for page to load."""
        try:
            logger.info(f"Visiting: {url}")
            self.driver.get(url)
            # Wait for page to fully load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except Exception as e:
            logger.error(f"Error visiting {url}: {e}")
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


logger.info("Selenium utilities module loaded")
