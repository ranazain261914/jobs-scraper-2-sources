"""
Punjab Jobs Link Extractor

Extracts job listing links from Punjab government jobs portal.
Website: https://jobs.punjab.gov.pk/new_recruit/jobs

Strategy:
1. Load the jobs page
2. Extract links from job listings (usually table/list format)
3. Handle pagination if present
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

PUNJAB_URL = "https://jobs.punjab.gov.pk/new_recruit/jobs"
BASE_URL = "https://jobs.punjab.gov.pk"


class PunjabJobsExtractor:
    """Extracts job links from Punjab jobs portal."""
    
    def __init__(self, headless: bool = True):
        """Initialize the extractor with Selenium driver."""
        self.driver = SeleniumDriver(browser='chrome', headless=headless)
        self.base_url = BASE_URL
        self.jobs_url = PUNJAB_URL
        self.extracted_links = []
    
    def extract_links(self) -> List[str]:
        """
        Extract all job links from Punjab jobs portal.
        
        Returns:
            List: List of job URLs
        """
        try:
            logger.info(f"Starting Punjab Jobs link extraction from {self.jobs_url}")
            
            # Visit the jobs page
            self.driver.visit(self.jobs_url)
            add_delay(2, 4)
            
            # Extract links from current page
            job_links = self._extract_from_listings()
            
            # Handle pagination if present
            job_links.extend(self._extract_from_pagination())
            
            if not job_links:
                logger.warning("No links found, trying fallback...")
                job_links = self._extract_with_fallback()
            
            # Remove duplicates
            job_links = remove_duplicates(job_links)
            
            # Validate links
            valid_links = [link for link in job_links if is_valid_url(link)]
            
            logger.info(f"Extracted {len(valid_links)} valid Punjab job links")
            self.extracted_links = valid_links
            
            return valid_links
            
        except Exception as e:
            logger.error(f"Error extracting Punjab Jobs links: {e}")
            return []
    
    def _extract_from_listings(self) -> List[str]:
        """
        Extract links from job listing elements.
        
        Punjab portal typically uses:
        - Table rows with job information
        - Links in table cells
        - Job detail links
        
        Returns:
            List: Extracted job URLs
        """
        links = []
        
        try:
            # Try multiple selectors
            selectors = [
                # Table-based listings
                "table a[href*='job']",
                "tr a",
                "td a",
                # List-based
                "li a",
                ".job-item a",
                "div.job-listing a",
                # Generic job links
                "a[href*='/job/']",
                "a[href*='/recruit/']",
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
                                
                                # Filter for job-related links
                                if any(pattern in absolute_url.lower() 
                                      for pattern in ['/job', '/recruit', '/vacancy', '/position']):
                                    
                                    links.append(absolute_url)
                                    logger.debug(f"Extracted: {absolute_url}")
                        
                        if links:
                            break
                
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in _extract_from_listings: {e}")
        
        return links
    
    def _extract_from_pagination(self) -> List[str]:
        """
        Extract links from paginated results.
        
        Returns:
            List: Extracted job URLs from other pages
        """
        links = []
        
        try:
            logger.info("Checking for pagination...")
            
            # Look for pagination links
            pagination_selectors = [
                "a.next",
                "a.pagination",
                "nav a",
                ".pager a",
            ]
            
            next_page_found = True
            pages_processed = 0
            max_pages = 3  # Limit to avoid too many requests
            
            while next_page_found and pages_processed < max_pages:
                next_page_found = False
                
                for selector in pagination_selectors:
                    try:
                        elements = self.driver.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        # Find next page link
                        for element in elements:
                            text = element.text.lower()
                            href = element.get_attribute('href')
                            
                            if href and any(keyword in text for keyword in ['next', '>']):
                                # Click next page
                                logger.info(f"Following pagination link...")
                                self.driver.driver.execute_script(
                                    "arguments[0].scrollIntoView(true);", element
                                )
                                add_delay(1, 2)
                                element.click()
                                
                                add_delay(2, 4)  # Wait for page load
                                
                                # Extract links from new page
                                page_links = self._extract_from_listings()
                                links.extend(page_links)
                                
                                next_page_found = True
                                pages_processed += 1
                                break
                    
                    except Exception as e:
                        logger.debug(f"Pagination error: {e}")
                        continue
                    
                    if next_page_found:
                        break
            
        except Exception as e:
            logger.warning(f"Error in pagination: {e}")
        
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
                          for pattern in ['/job', '/recruit', '/vacancy', '/position', 'jobs']):
                        
                        # Avoid nav/footer
                        if not any(nav in absolute_url.lower() 
                                 for nav in ['#', '/page', '/admin', '/contact', '/about']):
                            
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
    """Main function to test Punjab Jobs extraction."""
    logger.info("=" * 60)
    logger.info("Punjab Jobs Link Extraction")
    logger.info("=" * 60)
    
    with PunjabJobsExtractor(headless=False) as extractor:
        links = extractor.extract_links()
        
        if links:
            print(f"\n✓ Successfully extracted {len(links)} job links from Punjab Jobs\n")
            print("Sample links (first 5):")
            for i, link in enumerate(links[:5], 1):
                print(f"  {i}. {link}")
            
            if len(links) > 5:
                print(f"  ... and {len(links) - 5} more links")
        else:
            print("\n✗ No links extracted. Check if:")
            print("  1. Website structure has changed")
            print("  2. Network connectivity issues")
            print("  3. Website blocks automated access")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
