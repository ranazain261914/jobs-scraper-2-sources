"""
Selenium-based web scraping module for job listing extraction.

This module provides tools for extracting job links from multiple websites:
- Greenhouse careers portal
- Ashby job listing platform
- Punjab government jobs portal
"""

from .selenium_utils import SeleniumDriver
from .utils import (
    add_delay,
    is_valid_url,
    check_url_accessible,
    normalize_url,
    clean_text,
    remove_duplicates
)

__all__ = [
    'SeleniumDriver',
    'add_delay',
    'is_valid_url',
    'check_url_accessible',
    'normalize_url',
    'clean_text',
    'remove_duplicates'
]

__version__ = '1.0.0'
