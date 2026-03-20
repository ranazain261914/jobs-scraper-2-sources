"""
Ashby Jobs Scraper

Scrapes job listings from https://www.ashbyhq.com/careers
Uses API approach to fetch job data (preferred) with Selenium fallback
"""

import logging
import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

try:
    from base_scraper import BaseScraper
    from config import WEBSITES, OUTPUT_FILES, TIMEOUTS
except ImportError:
    from selenium.base_scraper import BaseScraper
    from selenium.config import WEBSITES, OUTPUT_FILES, TIMEOUTS


class AshbyScraper(BaseScraper):
    """Scraper for Ashby Careers Page"""
    
    # Known Ashby API endpoint (can be found via DevTools)
    ASHBY_API_URLS = [
        'https://api.ashbyhq.com/job-postings',
        'https://www.ashbyhq.com/api/job-postings',
        # Additional potential endpoints
    ]
    
    def __init__(self):
        super().__init__(
            source_name='ashby',
            target_url=WEBSITES['ashby']['url']
        )
    
    def extract_job_links(self) -> list:
        """
        Extract job links from Ashby
        
        Returns:
            List of job link dictionaries
        """
        self.logger.info("\n" + "="*80)
        self.logger.info("ASHBY CAREERS - LINK EXTRACTION")
        self.logger.info("="*80)
        
        job_links = []
        
        try:
            self.driver = self._setup_driver()
            self.logger.info(f"Loading: {self.target_url}")
            self.driver.get(self.target_url)
            
            # Wait for job elements to appear (may be loaded via API)
            self.logger.info("Waiting for job listings to load...")
            time.sleep(4)
            
            # Wait for job boards/listings element
            try:
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.support.ui import WebDriverWait
                
                # Try to wait for job listing divs
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job-board")))
                self.logger.info("  Job board element loaded")
            except:
                self.logger.warning("  Could not find job-board class, continuing anyway...")
            
            # Scroll to load more
            self.logger.info("Scrolling to load all jobs...")
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            # Parse the page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Try to find job postings
            # Ashby often uses data attributes or specific structures
            self.logger.info("Searching for job listings...")
            
            # Look for job posting links - try multiple selectors
            all_links = soup.find_all('a', href=True)
            self.logger.info(f"  Found {len(all_links)} total links")
            
            seen_urls = set()
            
            # Filter for job-related links
            for link in all_links:
                href = link.get('href', '').strip()
                text = link.get_text(strip=True)
                
                # Skip if empty or fragment
                if not href or href.startswith('#'):
                    continue
                
                # Normalize URL
                if href.startswith('/'):
                    normalized = 'https://www.ashbyhq.com' + href
                elif href.startswith('http'):
                    normalized = href
                else:
                    continue
                
                # Check if this looks like a job URL
                # Ashby might use URLs like /careers or /jobs or job IDs
                url_lower = normalized.lower()
                
                # Common patterns for job board URLs
                is_job = False
                
                # Direct job/position/opening paths
                if any(p in url_lower for p in ['/jobs/', '/positions/', '/openings/', '/job-postings/']):
                    is_job = True
                
                # If it has ashbyhq.com and a UUID or ID-like pattern
                if 'ashbyhq.com' in url_lower and (
                    any(c.isdigit() for c in href) or  # Has numbers
                    len(href) > 40  # Long URL suggests parameters
                ):
                    # Additional check: has job-related text
                    if any(kw in text for kw in ['Apply', 'Job', 'Position', 'View', 'Engineer', 'Designer', 'Manager', 'Developer']):
                        is_job = True
                
                if is_job and normalized not in seen_urls and 'careers' not in normalized:
                    seen_urls.add(normalized)
                    job_links.append({
                        'url': normalized,
                        'source': 'ashby',
                        'extracted_at': datetime.now().isoformat()
                    })
                    self.logger.debug(f"  Found: {text[:40]}... -> {normalized[:60]}...")
            
            self.logger.info(f"✓ Extracted {len(job_links)} job links")
            
        except Exception as e:
            self.logger.error(f"Error extracting Ashby jobs: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
        
        finally:
            self.cleanup()
        
        return job_links
    
    def _extract_via_api(self) -> list:
        """
        Attempt to extract jobs via Ashby API
        
        Returns:
            List of job links or empty list
        """
        self.logger.info("[STEP 1] Attempting API-based extraction...")
        
        try:
            # First, load the careers page to intercept API call
            self.driver = self._setup_driver()
            self.load_page()
            
            # Wait for content
            time.sleep(4)
            
            # Try to find API endpoint from network or page source
            self.logger.info("  Analyzing page for API endpoints...")
            
            # Get page source and look for API calls
            page_source = self.get_page_source()
            if not page_source:
                return []
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Try common Ashby API endpoints
            api_endpoints = [
                'https://api.ashbyhq.com/jobs',
                'https://api.ashbyhq.com/api/jobs',
                'https://www.ashbyhq.com/api/jobs',
                'https://api.ashbyhq.com/job-postings',
            ]
            
            for api_url in api_endpoints:
                try:
                    self.logger.info(f"  Trying API: {api_url}...")
                    response = requests.get(
                        api_url,
                        timeout=10,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.logger.info(f"  ✓ Found API endpoint: {api_url}")
                        
                        # Parse based on response structure
                        if isinstance(data, list):
                            return self._parse_api_jobs(data)
                        elif isinstance(data, dict):
                            # Try common key patterns
                            for key in ['jobs', 'data', 'results', 'postings']:
                                if key in data:
                                    return self._parse_api_jobs(data[key])
                
                except (requests.RequestException, ValueError):
                    continue
        
        except Exception as e:
            self.logger.debug(f"API extraction failed: {e}")
        
        finally:
            if self.driver:
                self.cleanup()
        
        return []
    
    def _parse_api_jobs(self, jobs_data) -> list:
        """Parse job data from API response"""
        job_links = []
        seen_urls = set()
        
        try:
            for job in jobs_data:
                # Handle different API formats
                if isinstance(job, dict):
                    job_id = job.get('id')
                    job_link = job.get('link') or job.get('url') or job.get('jobUrl')
                    job_title = job.get('title') or job.get('jobTitle')
                elif isinstance(job, str):
                    job_link = job
                    job_title = None
                else:
                    continue
                
                # Construct URL if not present
                if not job_link and job_id:
                    job_link = f"https://www.ashbyhq.com/careers/{job_id}"
                
                # Normalize URL
                if job_link:
                    job_link = self._normalize_url(job_link)
                    
                    if job_link and job_link not in seen_urls:
                        seen_urls.add(job_link)
                        job_links.append({
                            'url': job_link,
                            'source': 'ashby',
                            'extracted_at': datetime.now().isoformat()
                        })
        
        except Exception as e:
            self.logger.error(f"Error parsing API jobs: {e}")
        
        return job_links
    
    def _extract_via_selenium(self) -> list:
        """
        Fallback: Extract jobs using Selenium with full JS rendering
        
        Returns:
            List of job link dictionaries
        """
        self.logger.info("[STEP 2] Selenium-based extraction...")
        
        job_links = []
        seen_urls = set()
        
        try:
            self.driver = self._setup_driver()
            self.load_page()
            
            # Wait for page and scroll
            self.logger.info("  Scrolling to load all content...")
            time.sleep(3)
            
            # Scroll to bottom multiple times
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 5
            
            while scroll_attempts < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    self.logger.info("  ✓ Reached bottom of page")
                    break
                
                last_height = new_height
                scroll_attempts += 1
            
            # Parse page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for job links
            # Ashby usually uses specific class patterns
            job_containers = soup.find_all('a', class_=re.compile('job|position|career', re.I))
            
            self.logger.info(f"  Found {len(job_containers)} potential job links")
            
            for link in job_containers:
                href = link.get('href', '').strip()
                text = link.get_text(strip=True)
                
                if not href or len(text) < 3:
                    continue
                
                href = self._normalize_url(href)
                
                if href and href not in seen_urls:
                    seen_urls.add(href)
                    job_links.append({
                        'url': href,
                        'source': 'ashby',
                        'extracted_at': datetime.now().isoformat()
                    })
            
            return job_links
        
        except Exception as e:
            self.logger.error(f"Error in Selenium extraction: {e}")
            return []
        
        finally:
            if self.driver:
                self.cleanup()
    
    def _normalize_url(self, url: str) -> str:
        """Normalize job URL"""
        url = url.strip()
        
        if url.startswith('/'):
            return 'https://www.ashbyhq.com' + url
        elif url.startswith('http'):
            return url
        else:
            return None
    
    def parse_job_details(self, job_url: str) -> dict:
        """
        Parse job details from individual job page
        
        Args:
            job_url: URL of job posting
            
        Returns:
            Dictionary of job data
        """
        try:
            self.driver.get(job_url)
            time.sleep(1)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            job_data = {
                'job_title': None,
                'company_name': 'Ashby',
                'location': None,
                'job_description': None,
                'employment_type': None,
                'posted_date': None,
                'source': 'ashby',
                'job_url': job_url,
                'department': None,
                'skills': None,
                'extracted_at': datetime.now().isoformat()
            }
            
            # Extract title
            title_elem = soup.find(['h1', 'h2'])
            if title_elem:
                job_data['job_title'] = title_elem.get_text(strip=True)
            
            # Extract job details from sections
            sections = soup.find_all(['div', 'section'], class_=re.compile('detail|info|meta', re.I))
            
            for section in sections:
                text = section.get_text(strip=True)
                
                # Location
                if 'location' in text.lower() and not job_data['location']:
                    parts = text.split(':')
                    if len(parts) > 1:
                        job_data['location'] = parts[1].strip()[:100]
                
                # Employment type
                if 'employment' in text.lower() or 'type' in text.lower():
                    if not job_data['employment_type']:
                        parts = text.split(':')
                        if len(parts) > 1:
                            job_data['employment_type'] = parts[1].strip()[:100]
            
            # Extract description
            main_content = soup.find('main') or soup.find('article') or soup.find(class_=re.compile('content|description', re.I))
            if main_content:
                # Remove scripts and styles
                for tag in main_content.find_all(['script', 'style']):
                    tag.decompose()
                
                job_data['job_description'] = main_content.get_text(separator=' ', strip=True)[:3000]
            
            return job_data if job_data['job_title'] else None
        
        except Exception as e:
            self.logger.error(f"Error parsing {job_url}: {e}")
            return None


def main():
    """Main entry point for Ashby scraper"""
    scraper = AshbyScraper()
    
    # Phase 1: Extract links
    job_links = scraper.extract_job_links()
    if not job_links:
        scraper.logger.error("Failed to extract job links from Ashby")
        return
    
    # Save links
    links_output = OUTPUT_FILES['ashby']['links']
    scraper.save_links_to_csv(job_links, links_output)
    
    # Phase 2: Parse job details
    scraper.logger.info("\n[PHASE 2/2] PARSING JOB DETAILS")
    scraper.logger.info(f"Will parse {len(job_links)} jobs...")
    
    jobs_data = []
    try:
        scraper.driver = scraper._setup_driver()
        
        for idx, link_data in enumerate(job_links, 1):
            if idx % 5 == 0 or idx == 1:
                scraper.logger.info(f"  Parsing: [{idx}/{len(job_links)}] jobs...")
            
            job_data = scraper.parse_job_details(link_data['url'])
            if job_data:
                jobs_data.append(job_data)
            
            scraper.sleep(TIMEOUTS['between_jobs'])
    finally:
        scraper.cleanup()
    
    # Save jobs
    scraper.logger.info(f"\n✓ Successfully parsed {len(jobs_data)} jobs")
    jobs_output = OUTPUT_FILES['ashby']['jobs']
    scraper.save_jobs_to_csv(jobs_data, jobs_output)
    
    # Summary
    scraper.logger.info("\n" + "="*80)
    scraper.logger.info(f"ASHBY SCRAPER COMPLETE")
    scraper.logger.info("="*80)
    scraper.logger.info(f"  Links extracted: {len(job_links)}")
    scraper.logger.info(f"  Jobs parsed: {len(jobs_data)}")
    if job_links:
        scraper.logger.info(f"  Success rate: {100*len(jobs_data)/len(job_links):.1f}%")
    scraper.logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
