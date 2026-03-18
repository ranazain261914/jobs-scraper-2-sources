"""
Ashby Careers Link Extractor

Extracts job listing links from Ashby careers page.
Website: https://www.ashbyhq.com/careers

Strategy:
1. Load the careers page
2. Wait for job listings to load (Ashby is heavily JavaScript-based)
3. Extract job detail links from the job listings
4. Validate and deduplicate links
"""

import logging
from typing import List
from selenium.webdriver.common.by import By
from selenium_utils import SeleniumDriver
from utils import (
    is_valid_url, 
    normalize_url, 
    remove_duplicates,
    add_delay
)

logger = logging.getLogger(__name__)

ASHBY_URL = "https://www.ashbyhq.com/careers"
BASE_URL = "https://www.ashbyhq.com"


class AshbyExtractor:
    """Extracts job links from Ashby careers page."""
    
    def __init__(self, headless: bool = True):
        """Initialize the extractor with Selenium driver."""
        self.driver = SeleniumDriver(browser='chrome', headless=headless)
        self.base_url = BASE_URL
        self.jobs_url = ASHBY_URL
        self.extracted_links = []
    
    def extract_links(self) -> List[str]:
        """
        Extract all job links from Ashby careers page.
        
        Returns:
            List: List of job URLs
        """
        try:
            logger.info(f"Starting Ashby link extraction from {self.jobs_url}")
            
            # Visit the careers page
            self.driver.visit(self.jobs_url)
            add_delay(3, 5)  # Wait for dynamic content
            
            # Ashby uses dynamic content, need to scroll to load all jobs
            self._scroll_to_load_jobs()
            
            # Extract job links
            job_links = self._extract_from_job_listings()
            
            if not job_links:
                logger.warning("No links found, trying fallback method...")
                job_links = self._extract_with_fallback()
            
            # Remove duplicates
            job_links = remove_duplicates(job_links)
            
            # Validate links
            valid_links = [link for link in job_links if is_valid_url(link)]
            
            logger.info(f"Extracted {len(valid_links)} valid Ashby job links")
            self.extracted_links = valid_links
            
            return valid_links
            
        except Exception as e:
            logger.error(f"Error extracting Ashby links: {e}")
            return []
    
    def _scroll_to_load_jobs(self):
        """
        Scroll through the page to trigger lazy loading of job listings.
        Ashby uses infinite scroll, so we need to scroll multiple times.
        """
        try:
            logger.info("Scrolling to load job listings...")
            
            for _ in range(5):  # Scroll 5 times
                self.driver.driver.execute_script(
                    "window.scrollBy(0, window.innerHeight);"
                )
                add_delay(1, 2)
            
            # Scroll back to top
            self.driver.driver.execute_script("window.scrollTo(0, 0);")
            
        except Exception as e:
            logger.warning(f"Error scrolling page: {e}")
    
    def _extract_from_job_listings(self) -> List[str]:
        """
        Extract links from Ashby job listing elements.
        
        Ashby structure typically uses:
        - Job containers with specific data attributes
        - Links that lead to job detail pages
        
        Returns:
            List: Extracted job URLs
        """
        links = []
        
        try:
            # Try multiple selectors for Ashby
            selectors = [
                "a[href*='/jobs/']",  # Generic job link pattern
                "a[data-job-id]",  # Ashby-specific data attribute
                ".job-posting a",
                "div[data-test='job-card'] a",
                "a.job-listing-link",
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
                                absolute_url = normalize_url(self.base_url, href)
                                
                                # Ashby job links typically contain /jobs/ or similar
                                if any(pattern in absolute_url.lower() 
                                      for pattern in ['/job', '/position', '/opportunity']):
                                    links.append(absolute_url)
                                    logger.debug(f"Extracted: {absolute_url}")
                        
                        if links:
                            break
                
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in _extract_from_job_listings: {e}")
        
        return links
    
    def _extract_with_fallback(self) -> List[str]:
        """
        Fallback method: Extract all links and filter for job-related ones.
        
        Returns:
            List: Extracted job URLs
        """
        links = []
        
        try:
            logger.info("Using fallback extraction method...")
            
            all_links = self.driver.driver.find_elements(By.TAG_NAME, "a")
            logger.info(f"Found {len(all_links)} total links on page")
            
            for link in all_links:
                href = link.get_attribute('href')
                
                if href:
                    absolute_url = normalize_url(self.base_url, href)
                    
                    # Filter for job-related patterns
                    if any(pattern in absolute_url.lower() 
                          for pattern in ['/job', '/careers', '/position', '/opportunity']):
                        
                        # Avoid nav/footer
                        if not any(nav in absolute_url.lower() 
                                 for nav in ['#', '/blog', '/company', '/about']):
                            
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
    """Main function to test Ashby extraction."""
    logger.info("=" * 60)
    logger.info("Ashby Job Links Extraction")
    logger.info("=" * 60)
    
    with AshbyExtractor(headless=False) as extractor:
        links = extractor.extract_links()
        
        if links:
            print(f"\n✓ Successfully extracted {len(links)} job links from Ashby\n")
            print("Sample links (first 5):")
            for i, link in enumerate(links[:5], 1):
                print(f"  {i}. {link}")
            
            if len(links) > 5:
                print(f"  ... and {len(links) - 5} more links")
        else:
            print("\n✗ No links extracted. Check if:")
            print("  1. Website structure has changed")
            print("  2. JavaScript loading issues")
            print("  3. Network connectivity issues")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
