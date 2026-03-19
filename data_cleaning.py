"""
Data Cleaning Module

Cleans and normalizes extracted job data:
- Remove duplicates
- Normalize locations
- Clean descriptions
- Extract skills
- Validate data
"""

import logging
import pandas as pd
import os
import re
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

# File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'final', 'jobs.csv')
OUTPUT_FILE = os.path.join(DATA_DIR, 'final', 'jobs_cleaned.csv')


class DataCleaner:
    """Cleans and normalizes job data."""
    
    def __init__(self, input_file: str = INPUT_FILE):
        """
        Initialize the data cleaner.
        
        Args:
            input_file: Path to input CSV file
        """
        self.input_file = input_file
        self.df = None
        self.original_count = 0
        self.cleaned_count = 0
    
    def load_data(self) -> bool:
        """
        Load data from CSV file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.input_file):
                logger.error(f"File not found: {self.input_file}")
                return False
            
            self.df = pd.read_csv(self.input_file)
            self.original_count = len(self.df)
            
            logger.info(f"✓ Loaded {self.original_count} records from {self.input_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def clean(self) -> pd.DataFrame:
        """
        Perform all cleaning operations.
        
        Returns:
            pd.DataFrame: Cleaned data
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        logger.info("\nStarting data cleaning...")
        logger.info("-" * 70)
        
        # 1. Remove duplicates
        logger.info("1. Removing duplicates...")
        self.df = self._remove_duplicates()
        
        # 2. Clean text fields
        logger.info("2. Cleaning text fields...")
        self.df = self._clean_text_fields()
        
        # 3. Normalize locations
        logger.info("3. Normalizing locations...")
        self.df = self._normalize_locations()
        
        # 4. Standardize employment types
        logger.info("4. Standardizing employment types...")
        self.df = self._standardize_employment_type()
        
        # 5. Remove records with missing critical fields
        logger.info("5. Removing incomplete records...")
        self.df = self._remove_incomplete_records()
        
        # 6. Extract and normalize skills
        logger.info("6. Extracting and normalizing skills...")
        self.df = self._extract_and_normalize_skills()
        
        self.cleaned_count = len(self.df)
        
        logger.info("-" * 70)
        logger.info(f"✓ Cleaning complete: {self.original_count} → {self.cleaned_count} records")
        
        return self.df
    
    def _remove_duplicates(self) -> pd.DataFrame:
        """
        Remove duplicate records based on job URL.
        
        Returns:
            pd.DataFrame: Deduplicated data
        """
        before = len(self.df)
        # Handle both 'job_url' and 'job_link' column names
        dup_col = 'job_url' if 'job_url' in self.df.columns else 'job_link'
        df = self.df.drop_duplicates(subset=[dup_col], keep='first')
        after = len(df)
        
        logger.info(f"   Removed {before - after} duplicate URLs")
        return df
    
    def _clean_text_fields(self) -> pd.DataFrame:
        """
        Clean text fields (strip, normalize whitespace).
        
        Returns:
            pd.DataFrame: Cleaned data
        """
        text_fields = [
            'job_title',
            'company_name',
            'location',
            'department',
            'employment_type',
            'posted_date',
            'experience_level'
        ]
        
        for field in text_fields:
            if field in self.df.columns:
                # Strip whitespace and normalize
                self.df[field] = self.df[field].fillna('').apply(
                    lambda x: re.sub(r'\s+', ' ', str(x).strip()) if x else None
                )
        
        # Clean job description (limit length)
        if 'job_description' in self.df.columns:
            self.df['job_description'] = self.df['job_description'].apply(
                lambda x: x[:2000] if pd.notna(x) else None
            )
        
        logger.info("   Cleaned text fields")
        return self.df
    
    def _normalize_locations(self) -> pd.DataFrame:
        """
        Normalize location names.
        
        Returns:
            pd.DataFrame: Data with normalized locations
        """
        if 'location' not in self.df.columns:
            return self.df
        
        # Mapping of common location variations
        location_map = {
            'New York': ['NY', 'NYC', 'New York City'],
            'San Francisco': ['SF', 'San Fran'],
            'Los Angeles': ['LA', 'Los Angeles'],
            'Chicago': ['CHI'],
            'Remote': ['Remote', 'Work from home', 'WFH', 'Virtual'],
            'Hybrid': ['Hybrid', 'Mixed'],
        }
        
        def normalize_location(loc):
            if pd.isna(loc) or not loc:
                return None
            
            loc_str = str(loc).strip()
            
            # Check mappings
            for canonical, variations in location_map.items():
                for variation in variations:
                    if variation.lower() in loc_str.lower():
                        return canonical
            
            # If no mapping found, return original (cleaned)
            return loc_str
        
        self.df['location'] = self.df['location'].apply(normalize_location)
        logger.info("   Normalized location names")
        return self.df
    
    def _standardize_employment_type(self) -> pd.DataFrame:
        """
        Standardize employment type values.
        
        Returns:
            pd.DataFrame: Data with standardized employment types
        """
        if 'employment_type' not in self.df.columns:
            return self.df
        
        def standardize_type(emp_type):
            if pd.isna(emp_type) or not emp_type:
                return None
            
            emp_type_lower = str(emp_type).lower()
            
            if 'full' in emp_type_lower or 'permanent' in emp_type_lower:
                return 'Full-time'
            elif 'part' in emp_type_lower:
                return 'Part-time'
            elif 'contract' in emp_type_lower:
                return 'Contract'
            elif 'intern' in emp_type_lower:
                return 'Internship'
            elif 'temporary' in emp_type_lower or 'temp' in emp_type_lower:
                return 'Temporary'
            else:
                return emp_type
        
        self.df['employment_type'] = self.df['employment_type'].apply(standardize_type)
        logger.info("   Standardized employment types")
        return self.df
    
    def _remove_incomplete_records(self) -> pd.DataFrame:
        """
        Remove records missing critical fields.
        
        Returns:
            pd.DataFrame: Data with complete records only
        """
        before = len(self.df)
        
        # Must have job title and URL (handle both 'job_url' and 'job_link')
        url_col = 'job_url' if 'job_url' in self.df.columns else 'job_link'
        self.df = self.df.dropna(subset=['job_title', url_col])
        
        # Job title must be reasonable length
        self.df = self.df[self.df['job_title'].str.len() > 3]
        
        after = len(self.df)
        removed = before - after
        
        if removed > 0:
            logger.info(f"   Removed {removed} incomplete records")
        
        return self.df
    
    def _extract_and_normalize_skills(self) -> pd.DataFrame:
        """
        Extract and normalize skills list.
        
        Returns:
            pd.DataFrame: Data with extracted skills
        """
        if 'required_skills' not in self.df.columns:
            return self.df
        
        def normalize_skills(skills_str):
            if pd.isna(skills_str) or not skills_str:
                return None
            
            skills_list = str(skills_str).split(',')
            skills_list = [s.strip() for s in skills_list]
            skills_list = [s.title() for s in skills_list if s.strip()]
            
            # Remove duplicates
            skills_list = list(set(skills_list))
            
            return ', '.join(sorted(skills_list)) if skills_list else None
        
        self.df['required_skills'] = self.df['required_skills'].apply(normalize_skills)
        logger.info("   Extracted and normalized skills")
        return self.df
    
    def save(self, output_file: str = OUTPUT_FILE):
        """
        Save cleaned data to CSV.
        
        Args:
            output_file: Path to output CSV file
        """
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            self.df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"✓ Saved cleaned data to {output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the cleaned data.
        
        Returns:
            Dict: Data statistics
        """
        stats = {
            'total_records': len(self.df),
            'total_companies': self.df['company_name'].nunique() if 'company_name' in self.df.columns else 0,
            'total_locations': self.df['location'].nunique() if 'location' in self.df.columns else 0,
            'total_sources': self.df['source'].nunique() if 'source' in self.df.columns else 0,
        }
        
        return stats
    
    def print_summary(self):
        """Print cleaning summary."""
        print("\n" + "=" * 70)
        print("DATA CLEANING SUMMARY")
        print("=" * 70)
        print(f"Original records:            {self.original_count}")
        print(f"Cleaned records:             {self.cleaned_count}")
        print(f"Records removed:             {self.original_count - self.cleaned_count}")
        print(f"Retention rate:              {self.cleaned_count/self.original_count*100:.1f}%")
        print("-" * 70)
        
        if self.df is not None:
            stats = self.get_statistics()
            print(f"Unique companies:            {stats['total_companies']}")
            print(f"Unique locations:            {stats['total_locations']}")
            print(f"Data sources:                {stats['total_sources']}")
        
        print("=" * 70)


def main():
    """Main function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    cleaner = DataCleaner()
    
    if not cleaner.load_data():
        exit(1)
    
    cleaner.clean()
    cleaner.save()
    cleaner.print_summary()
    
    logger.info("✓ Data cleaning completed!")


if __name__ == "__main__":
    main()
