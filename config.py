"""
Configuration file for job scraping system
"""

import os
from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
FINAL_DATA_DIR = DATA_DIR / "final"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Target websites
WEBSITES = {
    'greenhouse': {
        'url': 'https://job-boards.greenhouse.io/remotecom',
        'name': 'Greenhouse Remote.com',
        'driver_wait_time': 10
    },
    'ashby': {
        'url': 'https://www.ashbyhq.com/careers',
        'name': 'Ashby',
        'driver_wait_time': 10
    },
    'punjab': {
        'url': 'https://jobs.punjab.gov.pk/new_recruit/jobs',
        'name': 'Punjab',
        'driver_wait_time': 10
    }
}

# Output files
OUTPUT_FILES = {
    'greenhouse': {
        'links': RAW_DATA_DIR / 'job_links_greenhouse.csv',
        'jobs': FINAL_DATA_DIR / 'jobs_greenhouse.csv'
    },
    'ashby': {
        'links': RAW_DATA_DIR / 'job_links_ashby.csv',
        'jobs': FINAL_DATA_DIR / 'jobs_ashby.csv'
    },
    'punjab': {
        'links': RAW_DATA_DIR / 'job_links_punjab.csv',
        'jobs': FINAL_DATA_DIR / 'jobs_punjab.csv'
    },
    'consolidated': {
        'links': RAW_DATA_DIR / 'all_job_links.csv',
        'jobs': FINAL_DATA_DIR / 'all_jobs.csv'
    }
}

# Selenium options
SELENIUM_OPTIONS = {
    'headless': False,  # Set to False for debugging
    'no_sandbox': True,
    'disable_dev_shm': True,
    'disable_blink': True,  # Avoid automation detection
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Job data fields
JOB_FIELDS = [
    'job_title',
    'company_name',
    'location',
    'employment_type',
    'posted_date',
    'job_description',
    'job_url',
    'source',
    'department',
    'skills',
    'extracted_at'
]

# Timeouts and delays
TIMEOUTS = {
    'page_load': 15,
    'element_wait': 10,
    'between_requests': 0.5,
    'between_jobs': 1.0
}
