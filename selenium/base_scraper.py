"""
Base Scraper Class - Common functionality for all scrapers
"""

import logging
import csv
import time
import sys
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from config import SELENIUM_OPTIONS, TIMEOUTS


class BaseScraper(ABC):
    """Base class for all job scrapers"""
    
    def __init__(self, source_name: str, target_url: str):
        """Initialize scraper"""
        self.source_name = source_name
        self.target_url = target_url
        self.logger = self._setup_logger()
        self.driver = None
        self.wait = None
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for this scraper"""
        logger = logging.getLogger(self.source_name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with common options"""
        options = Options()
        
        if SELENIUM_OPTIONS['headless']:
            options.add_argument('--headless')
        if SELENIUM_OPTIONS['no_sandbox']:
            options.add_argument('--no-sandbox')
        if SELENIUM_OPTIONS['disable_dev_shm']:
            options.add_argument('--disable-dev-shm-usage')
        if SELENIUM_OPTIONS['disable_blink']:
            options.add_argument('--disable-blink-features=AutomationControlled')
        
        options.add_argument(f'user-agent={SELENIUM_OPTIONS["user_agent"]}')
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(TIMEOUTS['page_load'])
            self.wait = WebDriverWait(driver, TIMEOUTS['element_wait'])
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def load_page(self) -> bool:
        """Load the target page"""
        try:
            self.logger.info(f"Loading: {self.target_url}")
            self.driver.get(self.target_url)
            return True
        except Exception as e:
            self.logger.warning(f"Page load timeout (expected for heavy JS): {e}")
            time.sleep(3)
            return True  # Continue anyway
    
    def get_page_source(self) -> str:
        """Get rendered page source"""
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Failed to get page source: {e}")
            return ""
    
    def wait_for_element(self, by: By, value: str, timeout: int = None) -> bool:
        """Wait for an element to appear"""
        try:
            wait_time = timeout or TIMEOUTS['element_wait']
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except Exception as e:
            self.logger.warning(f"Timeout waiting for {value}: {e}")
            return False
    
    def save_links_to_csv(self, links: list, output_path: Path) -> bool:
        """Save extracted links to CSV"""
        if not links:
            self.logger.warning("No links to save")
            return False
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['url', 'source', 'extracted_at'])
                writer.writeheader()
                for link in links:
                    writer.writerow({
                        'url': link['url'],
                        'source': link['source'],
                        'extracted_at': link['extracted_at']
                    })
            
            self.logger.info(f"✓ Saved {len(links)} links to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save links: {e}")
            return False
    
    def save_jobs_to_csv(self, jobs: list, output_path: Path) -> bool:
        """Save extracted jobs to CSV"""
        if not jobs:
            self.logger.warning("No jobs to save")
            return False
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Get all unique keys from jobs
            fieldnames = [
                'job_title', 'company_name', 'location', 'employment_type',
                'posted_date', 'job_description', 'job_url', 'source',
                'department', 'skills', 'extracted_at'
            ]
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, restval='')
                writer.writeheader()
                for job in jobs:
                    writer.writerow(job)
            
            self.logger.info(f"✓ Saved {len(jobs)} jobs to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save jobs: {e}")
            return False
    
    def sleep(self, seconds: float = None):
        """Respectful delay between requests"""
        delay = seconds or TIMEOUTS['between_requests']
        time.sleep(delay)
    
    def cleanup(self):
        """Close browser and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed")
            except Exception as e:
                self.logger.warning(f"Error closing browser: {e}")
    
    @abstractmethod
    def extract_job_links(self) -> list:
        """Extract job links from the page - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def parse_job_details(self, job_url: str) -> dict:
        """Parse job details from individual job page - to be implemented by subclasses"""
        pass
