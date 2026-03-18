"""
Data Analysis Module

Analyzes cleaned job data to extract insights:
- Top skills
- Top locations
- Top companies
- Job type distribution
- Entry-level opportunities
"""

import logging
import pandas as pd
import os
from typing import Dict, List, Tuple
import json

logger = logging.getLogger(__name__)

# File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'final', 'jobs_cleaned.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'analysis')
RESULTS_FILE = os.path.join(OUTPUT_DIR, 'analysis_results.json')


class JobAnalyzer:
    """Analyzes job market data."""
    
    def __init__(self, input_file: str = INPUT_FILE):
        """
        Initialize the analyzer.
        
        Args:
            input_file: Path to cleaned CSV file
        """
        self.input_file = input_file
        self.df = None
        self.results = {}
    
    def load_data(self) -> bool:
        """
        Load cleaned data from CSV.
        
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(self.input_file):
                logger.error(f"File not found: {self.input_file}")
                return False
            
            self.df = pd.read_csv(self.input_file)
            logger.info(f"✓ Loaded {len(self.df)} records")
            return True
        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def analyze(self) -> Dict:
        """
        Perform all analyses.
        
        Returns:
            Dict: Analysis results
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        logger.info("\nStarting data analysis...")
        logger.info("-" * 70)
        
        self.results = {
            'summary': self._get_summary(),
            'top_skills': self._get_top_skills(),
            'top_locations': self._get_top_locations(),
            'top_companies': self._get_top_companies(),
            'top_job_titles': self._get_top_job_titles(),
            'employment_type_distribution': self._get_employment_distribution(),
            'entry_level_count': self._count_entry_level(),
            'experience_level_distribution': self._get_experience_distribution(),
            'source_distribution': self._get_source_distribution(),
        }
        
        logger.info("-" * 70)
        logger.info("✓ Analysis complete")
        
        return self.results
    
    def _get_summary(self) -> Dict:
        """Get summary statistics."""
        return {
            'total_jobs': len(self.df),
            'total_companies': self.df['company_name'].nunique(),
            'total_locations': self.df['location'].nunique(),
            'date_range': f"{self.df['extracted_at'].min()} to {self.df['extracted_at'].max()}"
        }
    
    def _get_top_skills(self, top_n: int = 15) -> List[Dict]:
        """
        Get top required skills.
        
        Args:
            top_n: Number of top skills to return
            
        Returns:
            List: Top skills with counts
        """
        skills_data = []
        
        # Expand skills (they're comma-separated)
        for skills_str in self.df['required_skills'].dropna():
            skills = [s.strip() for s in str(skills_str).split(',')]
            skills_data.extend(skills)
        
        # Count skills
        skill_counts = pd.Series(skills_data).value_counts().head(top_n)
        
        result = [
            {'skill': skill, 'count': int(count)}
            for skill, count in skill_counts.items()
        ]
        
        logger.info(f"   Top {top_n} skills identified")
        return result
    
    def _get_top_locations(self, top_n: int = 15) -> List[Dict]:
        """
        Get top job locations.
        
        Args:
            top_n: Number of locations to return
            
        Returns:
            List: Top locations with job counts
        """
        location_counts = self.df['location'].value_counts().head(top_n)
        
        result = [
            {'location': location, 'count': int(count)}
            for location, count in location_counts.items()
        ]
        
        logger.info(f"   Top {top_n} locations identified")
        return result
    
    def _get_top_companies(self, top_n: int = 15) -> List[Dict]:
        """
        Get companies with most job openings.
        
        Args:
            top_n: Number of companies to return
            
        Returns:
            List: Top companies with job counts
        """
        company_counts = self.df['company_name'].value_counts().head(top_n)
        
        result = [
            {'company': company, 'count': int(count)}
            for company, count in company_counts.items()
        ]
        
        logger.info(f"   Top {top_n} companies identified")
        return result
    
    def _get_top_job_titles(self, top_n: int = 15) -> List[Dict]:
        """
        Get most common job titles.
        
        Args:
            top_n: Number of titles to return
            
        Returns:
            List: Top job titles with counts
        """
        title_counts = self.df['job_title'].value_counts().head(top_n)
        
        result = [
            {'title': title, 'count': int(count)}
            for title, count in title_counts.items()
        ]
        
        logger.info(f"   Top {top_n} job titles identified")
        return result
    
    def _get_employment_distribution(self) -> List[Dict]:
        """
        Get distribution of employment types.
        
        Returns:
            List: Employment type distribution
        """
        emp_dist = self.df['employment_type'].value_counts()
        
        result = [
            {'type': emp_type, 'count': int(count)}
            for emp_type, count in emp_dist.items()
        ]
        
        logger.info("   Employment type distribution calculated")
        return result
    
    def _count_entry_level(self) -> Dict:
        """
        Count entry-level and internship opportunities.
        
        Returns:
            Dict: Entry-level statistics
        """
        entry_keywords = ['intern', 'junior', 'graduate', 'entry']
        
        entry_level = 0
        for _, row in self.df.iterrows():
            title = str(row['job_title']).lower()
            exp_level = str(row['experience_level']).lower() if pd.notna(row['experience_level']) else ''
            
            if any(keyword in title or keyword in exp_level for keyword in entry_keywords):
                entry_level += 1
        
        result = {
            'entry_level_count': entry_level,
            'percentage': round(entry_level / len(self.df) * 100, 2)
        }
        
        logger.info(f"   Found {entry_level} entry-level opportunities")
        return result
    
    def _get_experience_distribution(self) -> List[Dict]:
        """
        Get distribution of experience levels.
        
        Returns:
            List: Experience level distribution
        """
        exp_dist = self.df['experience_level'].dropna().value_counts()
        
        result = [
            {'level': level, 'count': int(count)}
            for level, count in exp_dist.items()
        ]
        
        logger.info("   Experience level distribution calculated")
        return result
    
    def _get_source_distribution(self) -> List[Dict]:
        """
        Get distribution of jobs by source.
        
        Returns:
            List: Source distribution
        """
        source_dist = self.df['source'].value_counts()
        
        result = [
            {'source': source, 'count': int(count)}
            for source, count in source_dist.items()
        ]
        
        logger.info("   Source distribution calculated")
        return result
    
    def save_results(self, output_file: str = RESULTS_FILE):
        """
        Save analysis results to JSON file.
        
        Args:
            output_file: Path to output JSON file
        """
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved analysis results to {output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise
    
    def print_report(self):
        """Print analysis report to console."""
        print("\n" + "=" * 70)
        print("JOB MARKET ANALYSIS REPORT")
        print("=" * 70)
        
        # Summary
        print("\n📊 SUMMARY")
        print("-" * 70)
        summary = self.results['summary']
        print(f"Total Jobs:                  {summary['total_jobs']}")
        print(f"Unique Companies:            {summary['total_companies']}")
        print(f"Unique Locations:            {summary['total_locations']}")
        
        # Top Skills
        print("\n🎯 TOP 10 REQUIRED SKILLS")
        print("-" * 70)
        for i, skill_item in enumerate(self.results['top_skills'][:10], 1):
            print(f"{i:2}. {skill_item['skill']:30} {skill_item['count']:>3} jobs")
        
        # Top Locations
        print("\n📍 TOP 10 JOB LOCATIONS")
        print("-" * 70)
        for i, loc_item in enumerate(self.results['top_locations'][:10], 1):
            print(f"{i:2}. {loc_item['location']:30} {loc_item['count']:>3} jobs")
        
        # Top Companies
        print("\n🏢 TOP 10 HIRING COMPANIES")
        print("-" * 70)
        for i, comp_item in enumerate(self.results['top_companies'][:10], 1):
            print(f"{i:2}. {comp_item['company']:30} {comp_item['count']:>3} jobs")
        
        # Top Job Titles
        print("\n💼 TOP 10 JOB TITLES")
        print("-" * 70)
        for i, title_item in enumerate(self.results['top_job_titles'][:10], 1):
            print(f"{i:2}. {title_item['title']:30} {title_item['count']:>3} jobs")
        
        # Employment Types
        print("\n📋 EMPLOYMENT TYPE DISTRIBUTION")
        print("-" * 70)
        for item in self.results['employment_type_distribution']:
            print(f"{item['type']:30} {item['count']:>3} jobs")
        
        # Entry-Level
        print("\n👤 ENTRY-LEVEL OPPORTUNITIES")
        print("-" * 70)
        entry = self.results['entry_level_count']
        print(f"Entry-level jobs:            {entry['entry_level_count']} ({entry['percentage']}%)")
        
        # Source Distribution
        print("\n🌐 JOBS BY SOURCE")
        print("-" * 70)
        for item in self.results['source_distribution']:
            print(f"{item['source']:30} {item['count']:>3} jobs")
        
        print("\n" + "=" * 70)


def main():
    """Main function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    analyzer = JobAnalyzer()
    
    if not analyzer.load_data():
        exit(1)
    
    analyzer.analyze()
    analyzer.save_results()
    analyzer.print_report()
    
    logger.info("✓ Data analysis completed!")


if __name__ == "__main__":
    main()
