"""
Greenhouse Careers Link Extractor

Extracts job listing links from Greenhouse careers page.
Website: https://www.greenhouse.com/careers/opportunities

Strategy:
1. Load the careers page
2. Wait for job listings to load
3. Extract job detail links from the job cards
4. Validate and deduplicate links
"""

import logging
import time
from typing import List
from selenium.webdriver.common.by import By
from selenium_utils import SeleniumDriver
from utils import (
    is_valid_url, 
    normalize_url, 
    clean_text, 
    remove_duplicates,
    add_delay
)

logger = logging.getLogger(__name__)

GREENHOUSE_URL = "https://www.greenhouse.com/careers/opportunities"
BASE_URL = "https://www.greenhouse.com"


class GreenhouseExtractor:
    """Extracts job links from Greenhouse careers page."""
    
    def __init__(self, headless: bool = True):
        """Initialize the extractor with Selenium driver."""
        self.driver = SeleniumDriver(browser='chrome', headless=headless)
        self.base_url = BASE_URL
        self.jobs_url = GREENHOUSE_URL
        self.extracted_links = []
    
    def extract_links(self) -> List[str]:
        """
        Extract all job links from Greenhouse careers page.
        
        Returns:
            List: List of job URLs
        """
        try:
            logger.info(f"Starting Greenhouse link extraction from {self.jobs_url}")
            
            # Visit the careers page
            self.driver.visit(self.jobs_url)
            add_delay(3, 5)  # Wait for dynamic content
            
            # Strategy 1: Look for job posting links in the main content
            job_links = self._extract_from_job_cards()
            
            if not job_links:
                # Strategy 2: Fallback - look for all links with job-related patterns
                logger.warning("No links found with primary strategy, trying fallback...")
                job_links = self._extract_with_fallback()
            
            # Remove duplicates
            job_links = remove_duplicates(job_links)
            
            # Validate links
            valid_links = [link for link in job_links if is_valid_url(link)]
            
            logger.info(f"Extracted {len(valid_links)} valid Greenhouse job links")
            self.extracted_links = valid_links
            
            return valid_links
            
        except Exception as e:
            logger.error(f"Error extracting Greenhouse links: {e}")
            return []
    
    def _extract_from_job_cards(self) -> List[str]:
        """
        Extract links from job listing cards.
        
        Greenhouse typically uses a grid or list layout with clickable job cards.
        Each card contains a link to the job details page.
        
        Returns:
            List: Extracted job URLs
        """
        links = []
        
        try:
            # Try multiple selectors as Greenhouse may have different HTML structures
            selectors = [
                # Common Greenhouse structure - job container with link
                "a[href*='/jobs/']",
                "a[data-test-id='job-posting-link']",
                "div.job-posting a",
                ".opening a",
                "a.job-title",
            ]
            
            for selector in selectors:
                try:
                    logger.info(f"Trying selector: {selector}")
                    elements = self.driver.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements:
                            href = element.get_attribute('href')
                            if href:
                                # Convert relative URLs to absolute
                                absolute_url = normalize_url(self.base_url, href)
                                
                                # Only add if it's a valid job link (contains /jobs/)
                                if '/jobs/' in absolute_url.lower():
                                    links.append(absolute_url)
                                    logger.debug(f"Extracted: {absolute_url}")
                        
                        # If we found links with this selector, don't try others
                        if links:
                            break
                
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in _extract_from_job_cards: {e}")
        
        return links
    
    def _extract_with_fallback(self) -> List[str]:
        """
        Fallback method: Extract all links from the page and filter job-related ones.
        
        Returns:
            List: Extracted job URLs
        """
        links = []
        
        try:
            logger.info("Using fallback extraction method...")
            
            # Get all links on the page
            all_links = self.driver.driver.find_elements(By.TAG_NAME, "a")
            logger.info(f"Found {len(all_links)} total links on page")
            
            for link in all_links:
                href = link.get_attribute('href')
                
                if href:
                    # Convert relative to absolute
                    absolute_url = normalize_url(self.base_url, href)
                    
                    # Filter for job-related links
                    if any(pattern in absolute_url.lower() for pattern in 
                           ['/jobs/', '/careers/', '/opportunity', '/position']):
                        
                        # Avoid navigation/footer links
                        if not any(nav in absolute_url.lower() for nav in
                                 ['#', '/page', '/company', '/blog', '/support']):
                            
                            links.append(absolute_url)
                            logger.debug(f"Extracted (fallback): {absolute_url}")
            
        except Exception as e:
            logger.error(f"Fallback extraction error: {e}")
        
        return links
    
    def get_links(self) -> List[str]:
        """Get the extracted links."""
        return self.extracted_links
    
    def close(self):
        """Close the Selenium driver."""
        self.driver.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Main function to test Greenhouse extraction."""
    logger.info("=" * 60)
    logger.info("Greenhouse Job Links Extraction")
    logger.info("=" * 60)
    
    with GreenhouseExtractor(headless=False) as extractor:
        links = extractor.extract_links()
        
        if links:
            print(f"\n✓ Successfully extracted {len(links)} job links from Greenhouse\n")
            print("Sample links (first 5):")
            for i, link in enumerate(links[:5], 1):
                print(f"  {i}. {link}")
            
            if len(links) > 5:
                print(f"  ... and {len(links) - 5} more links")
        else:
            print("\n✗ No links extracted. Check if:")
            print("  1. Website structure has changed")
            print("  2. Page requires JavaScript rendering")
            print("  3. Network connectivity issues")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
