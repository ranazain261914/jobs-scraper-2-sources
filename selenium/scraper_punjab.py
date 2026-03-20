"""
Punjab Jobs Portal Scraper

Scrapes job listings from https://jobs.punjab.gov.pk/new_recruit/jobs
Uses DataTables pagination to extract all jobs
"""

import logging
import re
import time
from datetime import datetime
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

try:
    from base_scraper import BaseScraper
    from config import WEBSITES, OUTPUT_FILES, TIMEOUTS
except ImportError:
    from selenium.base_scraper import BaseScraper
    from selenium.config import WEBSITES, OUTPUT_FILES, TIMEOUTS


class PunjabScraper(BaseScraper):
    """Scraper for Punjab Jobs Portal"""
    
    def __init__(self):
        super().__init__(
            source_name='punjab',
            target_url=WEBSITES['punjab']['url']
        )
    
    def extract_job_links(self) -> list:
        """
        Extract all job links from Punjab portal using DataTables
        
        Returns:
            List of job link dictionaries
        """
        self.logger.info("\n" + "="*80)
        self.logger.info("PUNJAB JOBS PORTAL - LINK EXTRACTION")
        self.logger.info("="*80)
        
        try:
            self.driver = self._setup_driver()
            self.load_page()
            
            # Wait for table to load
            self.logger.info("[STEP 1] Waiting for DataTable to load...")
            self.wait_for_element(By.ID, "myTable")
            time.sleep(1)
            
            # Step 2: Change rows per page to 100 to get all records
            self.logger.info("[STEP 2] Setting DataTable to show 100 rows per page...")
            self._set_datatable_rows(100)
            
            # Step 3: Extract links
            self.logger.info("[STEP 3] Extracting job links...")
            job_links = self._extract_links_from_table()
            
            self.logger.info(f"\n✓ Extracted {len(job_links)} job links from Punjab")
            return job_links
        
        except Exception as e:
            self.logger.error(f"Error in extract_job_links: {e}")
            return []
        finally:
            self.cleanup()
    
    def _set_datatable_rows(self, num_rows: int) -> bool:
        """Set DataTable to display specified number of rows"""
        try:
            # Find the length dropdown
            length_select = self.driver.find_element(By.NAME, "myTable_length")
            
            # Click to open
            length_select.click()
            time.sleep(0.3)
            
            # Select the desired option
            option = length_select.find_element(By.CSS_SELECTOR, f"option[value='{num_rows}']")
            option.click()
            
            self.logger.info(f"  ✓ Selected {num_rows} rows per page")
            
            # Wait for reload
            time.sleep(2)
            
            # Wait for table rows to be present
            self.wait_for_element(By.CSS_SELECTOR, "#myTable tbody tr")
            
            self.logger.info("  ✓ DataTable reloaded with all records")
            return True
        
        except Exception as e:
            self.logger.error(f"Error setting DataTable rows: {e}")
            return False
    
    def _extract_links_from_table(self) -> list:
        """Extract job links from DataTable"""
        job_links = []
        seen_urls = set()
        
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find the table
            table = soup.find('table', {'id': 'myTable'})
            if not table:
                self.logger.warning("  Could not find job table")
                return []
            
            # Find all rows
            rows = table.find_all('tr')
            self.logger.info(f"  Found {len(rows)} rows in table")
            
            # Extract links from rows (skip header)
            for row in rows[1:]:  # Skip header row
                cells = row.find_all('td')
                if not cells:
                    continue
                
                # First cell typically contains the job title link
                first_cell = cells[0]
                link = first_cell.find('a', href=True)
                
                if link:
                    href = link.get('href', '').strip()
                    text = link.get_text(strip=True)
                    
                    # Normalize URL
                    href = self._normalize_url(href)
                    
                    if href and href not in seen_urls:
                        seen_urls.add(href)
                        job_links.append({
                            'url': href,
                            'source': 'punjab',
                            'extracted_at': datetime.now().isoformat()
                        })
            
            return job_links
        
        except Exception as e:
            self.logger.error(f"Error extracting links from table: {e}")
            return []
    
    def _normalize_url(self, url: str) -> str:
        """Normalize job URL"""
        url = url.strip()
        
        if url.startswith('/'):
            return 'https://jobs.punjab.gov.pk' + url
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
                'company_name': 'Government of Punjab',
                'location': None,
                'job_description': None,
                'employment_type': None,
                'posted_date': None,
                'source': 'punjab',
                'job_url': job_url,
                'department': None,
                'skills': None,
                'extracted_at': datetime.now().isoformat()
            }
            
            # Extract title (usually in h1 or h2)
            title_elem = soup.find(['h1', 'h2'])
            if title_elem:
                job_data['job_title'] = title_elem.get_text(strip=True)
            
            # Extract details from structured sections
            sections = soup.find_all(['div', 'section'], class_=re.compile('detail|info|metadata', re.I))
            
            for section in sections:
                text = section.get_text(strip=True)
                
                # Try to extract location
                if 'location' in text.lower() and not job_data['location']:
                    job_data['location'] = self._extract_field_value(text, 'location')
                
                # Try to extract employment type
                if 'type' in text.lower() and not job_data['employment_type']:
                    job_data['employment_type'] = self._extract_field_value(text, 'type')
                
                # Try to extract department
                if 'department' in text.lower() and not job_data['department']:
                    job_data['department'] = self._extract_field_value(text, 'department')
            
            # Extract job description (all text content)
            body = soup.find('body')
            if body:
                # Remove scripts and styles
                for tag in body.find_all(['script', 'style']):
                    tag.decompose()
                
                text = body.get_text(separator=' ', strip=True)
                text = re.sub(r'\s+', ' ', text)
                job_data['job_description'] = text[:3000] if len(text) > 100 else None
            
            return job_data if job_data['job_title'] else None
        
        except Exception as e:
            self.logger.error(f"Error parsing {job_url}: {e}")
            return None
    
    def _extract_field_value(self, text: str, field_name: str) -> str:
        """Extract field value from text"""
        try:
            pattern = f"{field_name}[^a-z]*[:]*\\s*([^|]*)(?:\\||$)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        except:
            pass
        return None


def main():
    """Main entry point for Punjab scraper"""
    scraper = PunjabScraper()
    
    # Phase 1: Extract links
    job_links = scraper.extract_job_links()
    if not job_links:
        scraper.logger.error("Failed to extract job links")
        return
    
    # Save links
    links_output = OUTPUT_FILES['punjab']['links']
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
    jobs_output = OUTPUT_FILES['punjab']['jobs']
    scraper.save_jobs_to_csv(jobs_data, jobs_output)
    
    # Summary
    scraper.logger.info("\n" + "="*80)
    scraper.logger.info(f"PUNJAB SCRAPER COMPLETE")
    scraper.logger.info("="*80)
    scraper.logger.info(f"  Links extracted: {len(job_links)}")
    scraper.logger.info(f"  Jobs parsed: {len(jobs_data)}")
    if job_links:
        scraper.logger.info(f"  Success rate: {100*len(jobs_data)/len(job_links):.1f}%")
    scraper.logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
