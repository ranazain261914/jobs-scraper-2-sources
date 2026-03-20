#!/usr/bin/env python3
"""Quick test script for Ashby scraping"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Setup driver
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

try:
    print("[1] Loading Ashby careers page...")
    driver.get("https://www.ashbyhq.com/careers")
    
    print("[2] Waiting for content to load...")
    time.sleep(5)
    
    print("[3] Checking page source...")
    page_source = driver.page_source
    
    print(f"    Page source length: {len(page_source)} characters")
    
    # Look for job-related content
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Search for links
    all_links = soup.find_all('a', href=True)
    print(f"    Total links found: {len(all_links)}")
    
    # Look for job-related links
    job_links = []
    for link in all_links:
        href = link.get('href', '').strip()
        text = link.get_text(strip=True).lower()
        
        if 'job' in href.lower() or 'position' in text or 'opening' in text:
            job_links.append({
                'href': href,
                'text': link.get_text(strip=True)[:100]
            })
    
    print(f"    Job-related links found: {len(job_links)}")
    
    # Look for job containers
    job_containers = soup.find_all('div', class_=lambda x: x and ('job' in x.lower() or 'position' in x.lower()))
    print(f"    Job containers found: {len(job_containers)}")
    
    # Look for specific API or data
    scripts = soup.find_all('script')
    print(f"    Script tags: {len(scripts)}")
    
    for i, script in enumerate(scripts[:3]):  # Check first 3 scripts
        if script.string and len(script.string) > 50:
            print(f"    Script {i}: {len(script.string)} characters - {script.string[:100]}")
    
    # Print sample links
    print("\n[SAMPLE JOB LINKS]")
    for link in job_links[:5]:
        print(f"  {link}")

finally:
    print("\n[4] Closing browser...")
    driver.quit()
