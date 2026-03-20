"""
Diagnostic script to inspect the Punjab jobs portal
and understand the dropdown/pagination mechanism
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

try:
    url = "https://jobs.punjab.gov.pk/new_recruit/jobs"
    print(f"Loading: {url}")
    driver.get(url)
    
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
    
    time.sleep(2)
    
    print("\n" + "="*80)
    print("DROPDOWN INVESTIGATION")
    print("="*80)
    
    # Find all select elements
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"\nFound {len(selects)} <select> elements")
    
    for idx, select in enumerate(selects):
        print(f"\n  [SELECT #{idx+1}]")
        print(f"  ID: {select.get_attribute('id')}")
        print(f"  Name: {select.get_attribute('name')}")
        print(f"  Class: {select.get_attribute('class')}")
        
        options_list = select.find_elements(By.TAG_NAME, "option")
        print(f"  Options ({len(options_list)}):")
        for opt in options_list:
            print(f"    - {opt.text} (value={opt.get_attribute('value')})")
    
    # Check for DataTables initialization (common pagination library)
    print("\n" + "="*80)
    print("DATATABLE INVESTIGATION")
    print("="*80)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Look for DataTables wrapper
    datatable_wrappers = soup.find_all(class_='dataTables_wrapper')
    print(f"\nDataTables wrappers found: {len(datatable_wrappers)}")
    
    # Look for pagination elements
    pagination_elements = soup.find_all(class_=['pagination', 'dataTables_paginate'])
    print(f"Pagination elements found: {len(pagination_elements)}")
    if pagination_elements:
        print("\nPagination structure:")
        for elem in pagination_elements:
            print(elem.prettify()[:500])
    
    # Look for any table info
    table_info = soup.find(class_='dataTables_info')
    if table_info:
        print(f"\nTable info: {table_info.get_text(strip=True)}")
    
    # Check the actual table
    print("\n" + "="*80)
    print("TABLE STRUCTURE")
    print("="*80)
    
    tables = soup.find_all('table')
    print(f"\nTables found: {len(tables)}")
    
    for idx, table in enumerate(tables):
        table_id = table.get_attribute('id') if table.get('id') else 'no-id'
        table_class = table.get('class', [])
        rows = table.find_all('tr')
        print(f"\n  [TABLE #{idx+1}]")
        print(f"  ID: {table_id}")
        print(f"  Class: {table_class}")
        print(f"  Rows: {len(rows)}")
        
        # Check if it's DataTables
        if 'dataTable' in str(table_class):
            print(f"  ✓ This appears to be a DataTable")
    
    # Look for jQuery/DataTables scripts
    print("\n" + "="*80)
    print("SCRIPT/LIBRARY DETECTION")
    print("="*80)
    
    scripts = soup.find_all('script')
    datatable_scripts = [s for s in scripts if s.string and ('dataTable' in str(s.string) or 'DataTable' in str(s.string))]
    print(f"\nDataTables-related scripts: {len(datatable_scripts)}")
    
    # Look for pagination links
    print("\n" + "="*80)
    print("PAGINATION LINKS")
    print("="*80)
    
    all_links = soup.find_all('a')
    prev_next = [a for a in all_links if 'previous' in a.get_text().lower() or 'next' in a.get_text().lower()]
    print(f"\nFound {len(prev_next)} 'Previous/Next' links")
    
    page_links = [a for a in all_links if a.get('href', '').endswith('?page') or '?page=' in a.get('href', '')]
    print(f"Found {len(page_links)} page parameter links")
    
    # Print current page URL
    print("\n" + "="*80)
    print("CURRENT URL & PAGE SOURCE ANALYSIS")
    print("="*80)
    print(f"Current URL: {driver.current_url}")
    
    # Check if there's a URL parameter for page/offset
    if '?' in driver.current_url:
        print(f"URL already has parameters: {driver.current_url.split('?')[1]}")
    
    # Try to manually navigate with different parameters
    print("\n" + "="*80)
    print("TESTING URL PARAMETERS")
    print("="*80)
    
    test_params = [
        ('?page=2', 'Page 2'),
        ('?offset=10', 'Offset 10'),
        ('?start=10', 'Start 10'),
        ('?per_page=100', 'Per page 100'),
        ('?limit=100', 'Limit 100'),
    ]
    
    for param, desc in test_params:
        test_url = url + param
        print(f"\nTrying {desc}: {param}")
        driver.get(test_url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table')
        if table:
            rows = len(table.find_all('tr')) - 1  # Exclude header
            print(f"  Result: {rows} rows displayed")
    
finally:
    driver.quit()
    print("\n✓ Driver closed")
