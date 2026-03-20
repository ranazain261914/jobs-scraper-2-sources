"""
Job Consolidation Module

Consolidates job data from all sources into unified CSV files
"""

import logging
import csv
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import OUTPUT_FILES, RAW_DATA_DIR, FINAL_DATA_DIR
except ImportError:
    # Fallback for when imported from parent directory
    from selenium.config import OUTPUT_FILES, RAW_DATA_DIR, FINAL_DATA_DIR


class JobConsolidator:
    """Consolidates job data from multiple sources"""
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('consolidator')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def consolidate_links(self) -> dict:
        """
        Consolidate job links from all sources
        
        Returns:
            Dictionary with source -> count mapping
        """
        self.logger.info("\n" + "="*80)
        self.logger.info("CONSOLIDATING JOB LINKS")
        self.logger.info("="*80)
        
        all_links = []
        source_counts = {}
        seen_urls = set()
        
        # Define sources to consolidate
        sources = ['greenhouse', 'ashby', 'punjab']
        
        for source in sources:
            links_file = OUTPUT_FILES[source]['links']
            
            if not links_file.exists():
                self.logger.warning(f"⚠ No links file found for {source}: {links_file}")
                source_counts[source] = 0
                continue
            
            try:
                with open(links_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    count = 0
                    
                    for row in reader:
                        url = row.get('url', '').strip()
                        
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            all_links.append(row)
                            count += 1
                
                source_counts[source] = count
                self.logger.info(f"✓ {source.upper()}: {count} unique links")
            
            except Exception as e:
                self.logger.error(f"✗ Error reading {source} links: {e}")
                source_counts[source] = 0
        
        # Save consolidated links
        output_file = OUTPUT_FILES['consolidated']['links']
        self._save_csv(all_links, output_file, ['url', 'source', 'extracted_at'])
        
        self.logger.info(f"\n✓ Consolidated {len(all_links)} unique job links")
        self.logger.info(f"  Saved to: {output_file}")
        
        return source_counts
    
    def consolidate_jobs(self) -> dict:
        """
        Consolidate job details from all sources
        
        Returns:
            Dictionary with source -> count mapping
        """
        self.logger.info("\n" + "="*80)
        self.logger.info("CONSOLIDATING JOB DATA")
        self.logger.info("="*80)
        
        all_jobs = []
        source_counts = {}
        seen_urls = set()
        
        # Define sources to consolidate
        sources = ['greenhouse', 'ashby', 'punjab']
        
        for source in sources:
            jobs_file = OUTPUT_FILES[source]['jobs']
            
            if not jobs_file.exists():
                self.logger.warning(f"⚠ No jobs file found for {source}: {jobs_file}")
                source_counts[source] = 0
                continue
            
            try:
                with open(jobs_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    count = 0
                    
                    for row in reader:
                        job_url = row.get('job_url', '').strip()
                        
                        if job_url and job_url not in seen_urls:
                            seen_urls.add(job_url)
                            all_jobs.append(row)
                            count += 1
                
                source_counts[source] = count
                self.logger.info(f"✓ {source.upper()}: {count} unique jobs")
            
            except Exception as e:
                self.logger.error(f"✗ Error reading {source} jobs: {e}")
                source_counts[source] = 0
        
        # Save consolidated jobs
        output_file = OUTPUT_FILES['consolidated']['jobs']
        fieldnames = [
            'job_title', 'company_name', 'location', 'employment_type',
            'posted_date', 'job_description', 'job_url', 'source',
            'department', 'skills', 'extracted_at'
        ]
        self._save_csv(all_jobs, output_file, fieldnames)
        
        self.logger.info(f"\n✓ Consolidated {len(all_jobs)} unique jobs")
        self.logger.info(f"  Saved to: {output_file}")
        
        return source_counts
    
    def _save_csv(self, data: list, output_file: Path, fieldnames: list) -> bool:
        """Save data to CSV file"""
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, restval='')
                writer.writeheader()
                writer.writerows(data)
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """Get consolidation statistics"""
        stats = {
            'consolidated_links': 0,
            'consolidated_jobs': 0,
            'sources': {}
        }
        
        # Count links
        links_file = OUTPUT_FILES['consolidated']['links']
        if links_file.exists():
            with open(links_file, 'r', encoding='utf-8') as f:
                stats['consolidated_links'] = sum(1 for _ in csv.DictReader(f))
        
        # Count jobs
        jobs_file = OUTPUT_FILES['consolidated']['jobs']
        if jobs_file.exists():
            with open(jobs_file, 'r', encoding='utf-8') as f:
                stats['consolidated_jobs'] = sum(1 for _ in csv.DictReader(f))
        
        return stats


def main():
    """Main entry point"""
    consolidator = JobConsolidator()
    
    # Consolidate links
    link_counts = consolidator.consolidate_links()
    
    # Consolidate jobs
    job_counts = consolidator.consolidate_jobs()
    
    # Print summary
    consolidator.logger.info("\n" + "="*80)
    consolidator.logger.info("CONSOLIDATION SUMMARY")
    consolidator.logger.info("="*80)
    
    consolidator.logger.info("\nLinks by source:")
    total_links = 0
    for source, count in link_counts.items():
        consolidator.logger.info(f"  {source.upper()}: {count}")
        total_links += count
    consolidator.logger.info(f"  TOTAL: {total_links}")
    
    consolidator.logger.info("\nJobs by source:")
    total_jobs = 0
    for source, count in job_counts.items():
        consolidator.logger.info(f"  {source.upper()}: {count}")
        total_jobs += count
    consolidator.logger.info(f"  TOTAL: {total_jobs}")
    
    consolidator.logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
