"""
Job Data Extraction Module

Extracts structured job information from job detail pages.
Handles multiple website formats.
"""

import logging
import re
from typing import Dict, Optional, List
from datetime import datetime
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class JobParser:
    """Base class for parsing job details from HTML."""
    
    def __init__(self, html_content: str, url: str, source: str):
        """
        Initialize the parser.
        
        Args:
            html_content: HTML content of the job page
            url: Job URL
            source: Source website (greenhouse, ashby, punjab)
        """
        self.html = html_content
        self.url = url
        self.source = source
        self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def extract(self) -> Dict[str, Optional[str]]:
        """
        Extract all job details.
        
        Returns:
            Dict: Extracted job information
        """
        return {
            'job_title': self.extract_title(),
            'company_name': self.extract_company(),
            'location': self.extract_location(),
            'department': self.extract_department(),
            'employment_type': self.extract_employment_type(),
            'posted_date': self.extract_posted_date(),
            'job_url': self.url,
            'job_description': self.extract_description(),
            'required_skills': self.extract_skills(),
            'experience_level': self.extract_experience_level(),
            'source': self.source,
            'extracted_at': datetime.now().isoformat()
        }
    
    def extract_title(self) -> Optional[str]:
        """Extract job title. Override in subclasses."""
        # Common patterns
        selectors = [
            'h1',
            '.job-title',
            '[data-testid="job-title"]',
            '.position-title',
        ]
        
        for selector in selectors:
            element = self.soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 5:
                    return title
        
        return None
    
    def extract_company(self) -> Optional[str]:
        """Extract company name. Override in subclasses."""
        selectors = [
            '.company-name',
            '[data-testid="company-name"]',
            '.company',
            '.employer',
        ]
        
        for selector in selectors:
            element = self.soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return None
    
    def extract_location(self) -> Optional[str]:
        """Extract job location. Override in subclasses."""
        selectors = [
            '.job-location',
            '[data-testid="job-location"]',
            '.location',
            '.job-meta .location',
        ]
        
        for selector in selectors:
            element = self.soup.select_one(selector)
            if element:
                location = element.get_text(strip=True)
                # Clean location (remove "Location:", etc.)
                location = re.sub(r'^Location:\s*', '', location, flags=re.IGNORECASE)
                return location
        
        return None
    
    def extract_department(self) -> Optional[str]:
        """Extract department/team. Override in subclasses."""
        selectors = [
            '.department',
            '[data-testid="department"]',
            '.team',
            '.job-department',
        ]
        
        for selector in selectors:
            element = self.soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Try to extract from text
        text = self.soup.get_text()
        match = re.search(r'Department:\s*([^\n]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def extract_employment_type(self) -> Optional[str]:
        """Extract employment type (Full-time, Part-time, etc.)."""
        text = self.soup.get_text().lower()
        
        employment_types = [
            'full-time', 'full time',
            'part-time', 'part time',
            'contract',
            'temporary',
            'internship',
            'apprenticeship',
            'permanent'
        ]
        
        for emp_type in employment_types:
            if emp_type in text:
                return emp_type.title()
        
        return None
    
    def extract_posted_date(self) -> Optional[str]:
        """Extract job posting date."""
        selectors = [
            '.posted-date',
            '[data-testid="posted-date"]',
            '.date-posted',
            'time',
        ]
        
        for selector in selectors:
            element = self.soup.select_one(selector)
            if element:
                date_text = element.get_text(strip=True)
                if date_text:
                    return date_text
        
        # Try to find date pattern in text
        text = self.soup.get_text()
        match = re.search(r'Posted:\s*([^\n]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def extract_description(self) -> Optional[str]:
        """Extract job description."""
        selectors = [
            '.job-description',
            '[data-testid="job-description"]',
            '.description',
            '.job-details',
            'article',
        ]
        
        for selector in selectors:
            element = self.soup.select_one(selector)
            if element:
                description = element.get_text(separator='\n', strip=True)
                if description and len(description) > 20:
                    return description
        
        # Fallback: get all body text
        body = self.soup.find('body')
        if body:
            description = body.get_text(separator='\n', strip=True)
            if description and len(description) > 100:
                # Limit to 5000 chars
                return description[:5000]
        
        return None
    
    def extract_skills(self) -> List[str]:
        """Extract required skills."""
        skills = []
        
        # Common skill keywords
        skill_keywords = [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust',
            'sql', 'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'linux', 'windows',
            'git', 'rest api', 'graphql', 'mongodb', 'postgresql', 'mysql',
            'communication', 'leadership', 'team', 'management', 'analysis',
            'problem-solving', 'critical thinking', 'sales', 'marketing',
            'excel', 'power bi', 'tableau', 'machine learning', 'ai', 'data science'
        ]
        
        text = self.soup.get_text().lower()
        
        for skill in skill_keywords:
            if skill in text:
                skills.append(skill.title())
        
        # Remove duplicates
        return list(set(skills))
    
    def extract_experience_level(self) -> Optional[str]:
        """Extract experience level (Junior, Mid, Senior, etc.)."""
        text = self.soup.get_text().lower()
        
        levels = {
            'intern': 'Internship',
            'entry': 'Entry-level',
            'junior': 'Junior',
            'mid': 'Mid-level',
            'senior': 'Senior',
            'lead': 'Lead',
            'principal': 'Principal',
        }
        
        for key, level in levels.items():
            if key in text:
                return level
        
        return None


def create_parser(html_content: str, url: str, source: str) -> JobParser:
    """
    Factory function to create appropriate parser for source.
    
    Args:
        html_content: HTML content of job page
        url: Job URL
        source: Source website
        
    Returns:
        JobParser: Appropriate parser instance
    """
    return JobParser(html_content, url, source)


logger.info("Job parser module loaded")
