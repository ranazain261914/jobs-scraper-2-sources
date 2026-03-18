"""
Utility module for web scraping operations.
Handles common tasks like delays, validation, logging.
"""

import time
import logging
from typing import List
from urllib.parse import urljoin, urlparse
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def add_delay(min_seconds: float = 2, max_seconds: float = 5) -> None:
    """
    Add random delay between requests to avoid overloading servers.
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    import random
    delay = random.uniform(min_seconds, max_seconds)
    logger.info(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)


def is_valid_url(url: str) -> bool:
    """
    Validate if URL is properly formatted and accessible.
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception as e:
        logger.warning(f"URL validation error for {url}: {e}")
        return False


def check_url_accessible(url: str, timeout: int = 10) -> bool:
    """
    Check if a URL is accessible without getting blocked.
    
    Args:
        url: URL to check
        timeout: Timeout in seconds
        
    Returns:
        bool: True if accessible, False otherwise
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        return response.status_code < 400
    except Exception as e:
        logger.warning(f"URL check failed for {url}: {e}")
        return False


def normalize_url(base_url: str, relative_url: str) -> str:
    """
    Convert relative URLs to absolute URLs.
    
    Args:
        base_url: Base URL of the page
        relative_url: Relative URL from the page
        
    Returns:
        str: Absolute URL
    """
    return urljoin(base_url, relative_url)


def clean_text(text: str) -> str:
    """
    Clean whitespace and normalize text.
    
    Args:
        text: Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()


def remove_duplicates(items: List[str]) -> List[str]:
    """
    Remove duplicate items while preserving order.
    
    Args:
        items: List of items
        
    Returns:
        List: Deduplicated list
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


logger.info("Utils module loaded successfully")
