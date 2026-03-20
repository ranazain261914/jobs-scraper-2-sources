"""
Punjab Jobs Portal Scraper - DataTables Aware

Uses DataTables pagination to extract ALL 53 jobs by:
1. Selecting "100" rows per page via the dropdown (myTable_length)
2. Waiting for DataTables to reload all records
3. Parsing all visible job links

DataTables is a popular JavaScript library for HTML tables.
The rows-per-page dropdown triggers an AJAX reload.
"""

import logging
import csv
import os
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LINKS_OUTPUT = os.path.join(DATA_DIR, 'raw', 'job_links.csv')
JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'jobs.csv')


def scrape_all_punjab_jobs_datatables():
    """
    Scrape all Punjab jobs using DataTables pagination.
    Selects "100" from myTable_length dropdown to show all jobs at once.
    """
    
    logger.info("\n" + "="*80)
    logger.info("PUNJAB JOBS PORTAL - DATATABLES-AWARE SCRAPER")
    logger.info("="*80)
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    
    all_job_links = []
    
    try:
        url = "https://jobs.punjab.gov.pk/new_recruit/jobs"
        logger.info(f"Loading: {url}")
        driver.get(url)
        
        # Wait for DataTable to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.ID, "myTable")))
        
        time.sleep(1)
        
        # STEP 1: Change rows per page to 100
        logger.info("\n[STEP 1] Changing DataTable display to 100 rows per page...")
        
        try:
            # Find the length dropdown (DataTables uses this ID pattern)
            length_select = wait.until(
                EC.presence_of_element_located((By.NAME, "myTable_length"))
            )
            
            # Click the select to open dropdown
            length_select.click()
            time.sleep(0.3)
            
            # Find the "100" option
            option_100 = length_select.find_element(By.CSS_SELECTOR, "option[value='100']")
            option_100.click()
            
            logger.info("  ✓ Selected 100 rows per page")
            
            # Wait for DataTable to reload
            # DataTables will show a loading indicator, wait for it to complete
            time.sleep(2)
            
            # Wait for the table rows to be re-rendered
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#myTable tbody tr")))
            
            logger.info("  ✓ DataTable reloaded with all records")
            
        except Exception as e:
            logger.error(f"  ✗ Error changing rows per page: {e}")
            logger.info("  Attempting pagination method instead...")
            return scrape_by_pagination(driver, url)
        
        # STEP 2: Extract all job links from the table
        logger.info("\n[STEP 2] Extracting job links from table...")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_table = soup.find('table', {'id': 'myTable'})
        
        if not job_table:
            logger.error("Could not find job table")
            return []
        
        rows = job_table.find_all('tr')
        logger.info(f"Found {len(rows)} rows in table (including header)")
        
        # Extract from tbody rows
        tbody_rows = job_table.find('tbody').find_all('tr') if job_table.find('tbody') else rows[1:]
        logger.info(f"Found {len(tbody_rows)} job rows in tbody")
        
        for idx, row in enumerate(tbody_rows, 1):
            cols = row.find_all('td')
            if len(cols) >= 1:
                link_elem = cols[0].find('a')
                if link_elem and link_elem.get('href'):
                    href = link_elem.get('href', '')
                    if '/job_detail/' in href:
                        full_url = 'https://jobs.punjab.gov.pk' + href if not href.startswith('http') else href
                        job_title = link_elem.get_text(strip=True)
                        
                        all_job_links.append({
                            'url': full_url,
                            'source': 'punjab',
                            'job_title': job_title,
                            'extracted_at': datetime.now().isoformat()
                        })
        
        logger.info(f"\n✓ TOTAL JOBS EXTRACTED: {len(all_job_links)}")
        
        if len(all_job_links) < 50:
            logger.warning(f"⚠ WARNING: Only {len(all_job_links)} jobs extracted. Expected ~53.")
            logger.warning("  The 100-rows dropdown may not have worked.")
        else:
            logger.info(f"✓ SUCCESS: Extracted all {len(all_job_links)} jobs!")
        
        # STEP 3: Save job links
        logger.info("\n[STEP 3] Saving job links...")
        os.makedirs(os.path.dirname(LINKS_OUTPUT), exist_ok=True)
        
        with open(LINKS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'source', 'extracted_at', 'job_title'])
            writer.writeheader()
            for link in all_job_links:
                writer.writerow({
                    'url': link['url'],
                    'source': link['source'],
                    'extracted_at': link['extracted_at'],
                    'job_title': link.get('job_title', '')
                })
        
        logger.info(f"✓ Saved {len(all_job_links)} job links to {LINKS_OUTPUT}")
        
        return all_job_links
        
    finally:
        driver.quit()


def scrape_by_pagination(driver, url):
    """Fallback method: scrape by navigating through all pages"""
    
    logger.info("\n[FALLBACK] Using pagination to extract jobs from all 6 pages...")
    
    all_job_links = []
    
    for page_num in range(1, 7):  # 6 pages total
        logger.info(f"\n  [PAGE {page_num}] Navigating...")
        
        try:
            # Navigate to specific page using DataTables pagination
            page_link = driver.find_element(
                By.CSS_SELECTOR, 
                f"a.paginate_button[data-dt-idx='{page_num}']"
            )
            page_link.click()
            
            time.sleep(1)
            
            # Extract jobs from this page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_table = soup.find('table', {'id': 'myTable'})
            
            if job_table:
                tbody_rows = job_table.find('tbody').find_all('tr') if job_table.find('tbody') else []
                
                for row in tbody_rows:
                    cols = row.find_all('td')
                    if len(cols) >= 1:
                        link_elem = cols[0].find('a')
                        if link_elem and link_elem.get('href'):
                            href = link_elem.get('href', '')
                            if '/job_detail/' in href:
                                full_url = 'https://jobs.punjab.gov.pk' + href if not href.startswith('http') else href
                                job_title = link_elem.get_text(strip=True)
                                
                                all_job_links.append({
                                    'url': full_url,
                                    'source': 'punjab',
                                    'job_title': job_title,
                                    'extracted_at': datetime.now().isoformat()
                                })
                
                logger.info(f"    Extracted {len(tbody_rows)} jobs from page {page_num}")
        
        except Exception as e:
            logger.warning(f"  Error on page {page_num}: {e}")
            if page_num == 1:  # If first page fails, stop
                break
    
    logger.info(f"\n✓ Total jobs extracted via pagination: {len(all_job_links)}")
    return all_job_links


def parse_punjab_job(driver, url):
    """Parse individual Punjab job posting"""
    try:
        driver.get(url)
        
        wait = WebDriverWait(driver, 8)
        try:
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "td")))
        except:
            pass
        
        time.sleep(0.3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        job_data = {
            'job_title': None,
            'company_name': 'Punjab Government',
            'location': 'Punjab, Pakistan',
            'job_description': None,
            'employment_type': 'Full-time',
            'posted_date': None,
            'source': 'punjab',
            'job_url': url,
            'extracted_at': datetime.now().isoformat()
        }
        
        # Parse table structure for job details
        all_tds = soup.find_all('td')
        
        for i in range(0, len(all_tds)-1, 2):
            try:
                label = all_tds[i].get_text(strip=True).lower()
                value = all_tds[i+1].get_text(strip=True)
                
                if 'role' in label or 'position' in label:
                    if not job_data['job_title'] and value not in ['1', '2', '3', '4', '5']:
                        job_data['job_title'] = value
                elif 'district' in label and value:
                    job_data['location'] = f"{value}, Punjab, Pakistan"
                elif 'employment' in label or 'status' in label:
                    job_data['employment_type'] = value
                elif 'posted' in label and 'date' in label:
                    job_data['posted_date'] = value
            except:
                pass
        
        # Extract job description
        full_text = soup.get_text()
        if 'Job Description' in full_text:
            desc_start = full_text.index('Job Description') + len('Job Description')
            description_text = full_text[desc_start:]
            
            # Stop at common markers
            for marker in ['Job Responsibilities', 'Apply for', 'Sitemap', 'Important Note', 'Degree Level', 'Requirement']:
                if marker in description_text:
                    description_text = description_text[:description_text.index(marker)]
            
            description_text = re.sub(r'\s+', ' ', description_text).strip()
            if description_text and len(description_text) > 20:
                job_data['job_description'] = description_text[:2000]
        
        # Get proper title if not extracted from table
        if not job_data['job_title']:
            page_title = soup.find('h1') or soup.find('h2')
            if page_title:
                title_text = page_title.get_text(strip=True)
                title_text = re.sub(r'Punjab.*Authority|PAKISTAN|PLRA', '', title_text, flags=re.IGNORECASE).strip()
                title_text = re.sub(r'^[\d\s\-]+', '', title_text).strip()
                title_text = re.sub(r'\s*-\s*,\s*$', '', title_text).strip()
                if title_text and len(title_text) > 3:
                    job_data['job_title'] = title_text
        
        # Clean up title
        if job_data['job_title']:
            job_data['job_title'] = re.sub(r'\s*-\s*,\s*$', '', job_data['job_title']).strip()
        
        return job_data if job_data['job_title'] else None
        
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return None


def main():
    """Extract and parse all Punjab jobs"""
    
    # PHASE 1: Extract all job links
    logger.info("\n[PHASE 1/2] EXTRACTING ALL JOB LINKS")
    job_links = scrape_all_punjab_jobs_datatables()
    
    if not job_links:
        logger.error("No job links extracted!")
        return
    
    # PHASE 2: Parse job details
    logger.info("\n[PHASE 2/2] PARSING JOB DETAILS FROM LINKS")
    logger.info(f"Will parse {len(job_links)} job postings...")
    
    jobs_data = []
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    
    try:
        for idx, link_data in enumerate(job_links, 1):
            if idx % 10 == 0 or idx == 1:
                logger.info(f"  Parsing: [{idx}/{len(job_links)}] jobs...")
            
            job_data = parse_punjab_job(driver, link_data['url'])
            if job_data:
                jobs_data.append(job_data)
    finally:
        driver.quit()
    
    logger.info(f"\n✓ Successfully parsed {len(jobs_data)} jobs")
    
    # PHASE 3: Save results
    logger.info("\n[SAVING RESULTS]")
    os.makedirs(os.path.dirname(JOBS_OUTPUT), exist_ok=True)
    
    with open(JOBS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'job_title', 'company_name', 'location', 'job_description',
            'employment_type', 'posted_date', 'source', 'job_url', 'extracted_at'
        ])
        writer.writeheader()
        writer.writerows(jobs_data)
    
    logger.info(f"✓ Saved {len(jobs_data)} jobs to {JOBS_OUTPUT}")
    
    # SUMMARY
    logger.info("\n" + "="*80)
    logger.info(f"FINAL RESULTS: {len(jobs_data)} JOBS EXTRACTED FROM PUNJAB")
    logger.info("="*80)
    logger.info(f"  Job links extracted: {len(job_links)}")
    logger.info(f"  Jobs successfully parsed: {len(jobs_data)}")
    logger.info(f"  Success rate: {100*len(jobs_data)/len(job_links):.1f}%")
    logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
