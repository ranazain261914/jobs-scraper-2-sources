"""
Master Link Extraction Script

Orchestrates extraction of job links from all three websites:
1. Greenhouse
2. Ashby
3. Punjab Jobs

Saves all extracted links to CSV with deduplication and validation.
"""

import logging
import csv
import os
from typing import List, Dict
from datetime import datetime

# Import individual extractors
from greenhouse_scraper import GreenhouseExtractor
from ashby_scraper import AshbyExtractor
from punjab_scraper import PunjabJobsExtractor
from utils import remove_duplicates, add_delay

logger = logging.getLogger(__name__)

# Output configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'job_links.csv')


class LinkExtractor:
    """Master orchestrator for link extraction from all websites."""
    
    def __init__(self):
        """Initialize the link extractor."""
        self.all_links = {
            'greenhouse': [],
            'ashby': [],
            'punjab': []
        }
        self.total_links = 0
    
    def extract_all(self) -> Dict[str, List[str]]:
        """
        Extract links from all three websites.
        
        Returns:
            Dict: Links organized by source
        """
        logger.info("=" * 70)
        logger.info("Starting Link Extraction from All Websites")
        logger.info("=" * 70)
        
        # 1. Extract from Greenhouse
        logger.info("\n[1/3] Extracting from Greenhouse...")
        logger.info("-" * 70)
        self._extract_greenhouse()
        
        # 2. Extract from Ashby
        logger.info("\n[2/3] Extracting from Ashby...")
        logger.info("-" * 70)
        add_delay(5, 10)  # Delay between different websites
        self._extract_ashby()
        
        # 3. Extract from Punjab Jobs
        logger.info("\n[3/3] Extracting from Punjab Jobs...")
        logger.info("-" * 70)
        add_delay(5, 10)  # Delay between different websites
        self._extract_punjab()
        
        logger.info("\n" + "=" * 70)
        logger.info("Link Extraction Complete")
        logger.info("=" * 70)
        
        return self.all_links
    
    def _extract_greenhouse(self):
        """Extract links from Greenhouse."""
        try:
            with GreenhouseExtractor(headless=True) as extractor:
                links = extractor.extract_links()
                self.all_links['greenhouse'] = links
                self.total_links += len(links)
                logger.info(f"✓ Greenhouse: {len(links)} links extracted")
        except Exception as e:
            logger.error(f"✗ Greenhouse extraction failed: {e}")
            self.all_links['greenhouse'] = []
    
    def _extract_ashby(self):
        """Extract links from Ashby."""
        try:
            with AshbyExtractor(headless=True) as extractor:
                links = extractor.extract_links()
                self.all_links['ashby'] = links
                self.total_links += len(links)
                logger.info(f"✓ Ashby: {len(links)} links extracted")
        except Exception as e:
            logger.error(f"✗ Ashby extraction failed: {e}")
            self.all_links['ashby'] = []
    
    def _extract_punjab(self):
        """Extract links from Punjab Jobs."""
        try:
            with PunjabJobsExtractor(headless=True) as extractor:
                links = extractor.extract_links()
                self.all_links['punjab'] = links
                self.total_links += len(links)
                logger.info(f"✓ Punjab Jobs: {len(links)} links extracted")
        except Exception as e:
            logger.error(f"✗ Punjab Jobs extraction failed: {e}")
            self.all_links['punjab'] = []
    
    def save_to_csv(self) -> str:
        """
        Save all extracted links to CSV file.
        
        Returns:
            str: Path to CSV file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Prepare data for CSV
            rows = []
            
            for source, links in self.all_links.items():
                for url in links:
                    rows.append({
                        'url': url,
                        'source': source,
                        'extracted_at': datetime.now().isoformat()
                    })
            
            # Remove duplicates based on URL
            unique_rows = {}
            for row in rows:
                url = row['url']
                if url not in unique_rows:
                    unique_rows[url] = row
            
            # Write to CSV
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['url', 'source', 'extracted_at'])
                writer.writeheader()
                writer.writerows(unique_rows.values())
            
            logger.info(f"✓ Saved {len(unique_rows)} unique links to {OUTPUT_FILE}")
            return OUTPUT_FILE
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise
    
    def print_summary(self):
        """Print extraction summary."""
        print("\n" + "=" * 70)
        print("LINK EXTRACTION SUMMARY")
        print("=" * 70)
        
        for source, links in self.all_links.items():
            print(f"{source.upper():12} {len(links):>4} links")
        
        print("-" * 70)
        print(f"{'TOTAL':12} {self.total_links:>4} links")
        print("=" * 70)
        
        print(f"\n✓ CSV saved to: {OUTPUT_FILE}")
        print("\nTo view links:")
        print(f"  head -20 {OUTPUT_FILE}")


def main():
    """Main function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('extraction.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        extractor = LinkExtractor()
        
        # Extract from all websites
        extractor.extract_all()
        
        # Save to CSV
        extractor.save_to_csv()
        
        # Print summary
        extractor.print_summary()
        
        logger.info("\n✓ Link extraction completed successfully!")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
