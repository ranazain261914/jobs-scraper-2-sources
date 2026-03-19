"""
Job Data Extraction Script

Reads job links from CSV and extracts detailed information from each job page.
Saves results to final CSV file.
"""

import logging
import csv
import os
from typing import List, Dict
import time
from selenium_utils import SeleniumDriver
from job_parser import create_parser
from utils import add_delay
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


logger = logging.getLogger(__name__)

# File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'raw', 'job_links.csv')
OUTPUT_FILE = os.path.join(DATA_DIR, 'final', 'jobs.csv')


class JobDataExtractor:
    """Extracts detailed job information from job links."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.driver = SeleniumDriver(browser='chrome', headless=True)
        self.jobs_data = []
        self.failed_links = []
    
    def load_links(self) -> List[Dict[str, str]]:
        """
        Load job links from CSV file.
        
        Returns:
            List: List of dicts with 'url' and 'source' keys
        """
        links = []
        
        if not os.path.exists(INPUT_FILE):
            logger.error(f"Input file not found: {INPUT_FILE}")
            return links
        
        try:
            with open(INPUT_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    links.append({
                        'url': row['url'],
                        'source': row['source']
                    })
            
            logger.info(f"Loaded {len(links)} links from {INPUT_FILE}")
            return links
        
        except Exception as e:
            logger.error(f"Error loading links: {e}")
            return links
    
    def extract_job_data(self, limit: int = None) -> List[Dict]:
        """
        Extract data from all job links.
        
        Args:
            limit: Maximum number of jobs to extract (None for all)
            
        Returns:
            List: Extracted job data
        """
        logger.info("=" * 70)
        logger.info("Starting Job Data Extraction")
        logger.info("=" * 70)
        
        links = self.load_links()
        
        if not links:
            logger.error("No links found. Run extract_links.py first.")
            return []
        
        if limit:
            links = links[:limit]
        
        total_links = len(links)
        logger.info(f"Processing {total_links} job links...\n")
        
        for index, link_info in enumerate(links, 1):
            url = link_info['url']
            source = link_info['source']
            
            logger.info(f"[{index}/{total_links}] Extracting: {url[:60]}...")
            
            try:
                # Visit the job page
                self.driver.visit(url)
                add_delay(2, 4)
                
                # Get page HTML
                html_content = self.driver.get_page_source()
                
                # Parse job details
                parser = create_parser(html_content, url, source)
                job_data = parser.extract()
                
                # Validate data
                if self._is_valid_job(job_data):
                    self.jobs_data.append(job_data)
                    logger.info(f"  ✓ Extracted: {job_data.get('job_title', 'N/A')}")
                else:
                    logger.warning(f"  ⚠ Invalid job data - skipping")
                    self.failed_links.append(url)
            
            except Exception as e:
                logger.error(f"  ✗ Error extracting {url}: {e}")
                self.failed_links.append(url)
            
            # Avoid overloading servers
            if index % 10 == 0:
                logger.info(f"Processed {index}/{total_links} jobs. Taking a longer break...")
                add_delay(5, 10)
        
        logger.info(f"\n✓ Extracted {len(self.jobs_data)} valid jobs")
        logger.info(f"✗ Failed to extract {len(self.failed_links)} links")
        
        return self.jobs_data
    
    def _is_valid_job(self, job_data: Dict) -> bool:
        """
        Validate extracted job data.
        
        Args:
            job_data: Job data dict
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Must have at least title and URL
        if not job_data.get('job_title') or not job_data.get('job_url'):
            return False
        
        # Title should be reasonable length
        title = job_data.get('job_title', '')
        if len(title) < 3 or len(title) > 200:
            return False
        
        return True
    
    def save_to_csv(self):
        """Save extracted job data to CSV file."""
        try:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            
            fieldnames = [
                'job_title',
                'company_name',
                'location',
                'department',
                'employment_type',
                'posted_date',
                'job_url',
                'job_description',
                'required_skills',
                'experience_level',
                'source',
                'extracted_at'
            ]
            
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.jobs_data)
            
            logger.info(f"✓ Saved {len(self.jobs_data)} jobs to {OUTPUT_FILE}")
        
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise
    
    def close(self):
        """Close the Selenium driver."""
        self.driver.close()
    
    def print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 70)
        print("JOB DATA EXTRACTION SUMMARY")
        print("=" * 70)
        print(f"Total jobs extracted:        {len(self.jobs_data)}")
        print(f"Failed extractions:          {len(self.failed_links)}")
        print(f"Success rate:                {len(self.jobs_data)/(len(self.jobs_data)+len(self.failed_links))*100:.1f}%")
        print("-" * 70)
        print(f"Output file:                 {OUTPUT_FILE}")
        print("=" * 70)
        
        if self.jobs_data:
            print("\nSample extracted job:")
            job = self.jobs_data[0]
            print(f"  Title:       {job.get('job_title')}")
            print(f"  Company:     {job.get('company_name')}")
            print(f"  Location:    {job.get('location')}")
            print(f"  Source:      {job.get('source')}")


def main():
    """Main function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('job_extraction.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        extractor = JobDataExtractor()
        
        # Extract job data (limit to 100 for testing)
        extractor.extract_job_data(limit=None)
        
        # Save to CSV
        if extractor.jobs_data:
            extractor.save_to_csv()
        
        # Print summary
        extractor.print_summary()
        
        logger.info("✓ Job extraction completed!")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)
    
    finally:
        if 'extractor' in locals():
            extractor.close()


if __name__ == "__main__":
    main()
