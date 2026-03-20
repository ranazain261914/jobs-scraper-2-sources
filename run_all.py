#!/usr/bin/env python3
"""
MASTER JOB SCRAPER & ANALYZER
Complete pipeline for extracting, parsing, consolidating, and analyzing job data

Execution Flow:
1. Run individual job scrapers (Punjab, Greenhouse, Ashby)
2. Consolidate all job data from multiple sources
3. Analyze job market trends and generate insights report
4. Output results to CSV and Markdown report

Usage:
    python run_all.py [--skip-scraping] [--skip-analysis]
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime


class JobPipelineManager:
    """Manages complete job scraping and analysis pipeline"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.base_dir = Path(__file__).parent
        self.results = {
            'scraping': {},
            'consolidation': {},
            'analysis': {}
        }
    
    def run_command(self, cmd, description, show_output=False):
        """Run a Python module as subprocess"""
        print(f"\n{'='*80}")
        print(f"🔄 {description}")
        print(f"{'='*80}")
        
        try:
            if show_output:
                result = subprocess.run(cmd, shell=True, cwd=self.base_dir)
            else:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    cwd=self.base_dir,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                print(f"✅ {description} - SUCCESS")
                return True
            else:
                print(f"❌ {description} - FAILED")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}")
                return False
        
        except Exception as e:
            print(f"❌ {description} - ERROR: {e}")
            return False
    
    def run_scraping(self):
        """Run all job scrapers"""
        print("\n" + "="*80)
        print("📥 PHASE 1: JOB SCRAPING")
        print("="*80)
        
        scrapers = [
            ('scrapers.scraper_punjab', 'Punjab Jobs Portal'),
            ('scrapers.scraper_greenhouse', 'Greenhouse/Remote.com'),
            ('scrapers.scraper_ashby', 'Ashby Careers Platform'),
        ]
        
        for module, description in scrapers:
            cmd = f"python -m {module}"
            success = self.run_command(cmd, f"Scraping {description}")
            self.results['scraping'][description] = success
            if success:
                time.sleep(2)  # Brief pause between scrapers
        
        # Summary
        scraped_count = sum(1 for v in self.results['scraping'].values() if v)
        total_count = len(self.results['scraping'])
        print(f"\n✓ Scraping complete: {scraped_count}/{total_count} scrapers successful")
    
    def run_consolidation(self):
        """Run data consolidation"""
        print("\n" + "="*80)
        print("🔗 PHASE 2: DATA CONSOLIDATION")
        print("="*80)
        
        cmd = "python -m utilities.consolidator"
        success = self.run_command(cmd, "Consolidating job data from all sources")
        self.results['consolidation']['consolidator'] = success
        
        if success:
            print("\n✓ Consolidation complete")
    
    def run_analysis(self):
        """Run job market analysis"""
        print("\n" + "="*80)
        print("📊 PHASE 3: JOB MARKET ANALYSIS")
        print("="*80)
        
        # Run analysis directly to avoid subprocess encoding issues
        try:
            from analyze_jobs import JobAnalyzer
            from pathlib import Path
            
            jobs_file = self.base_dir / 'data' / 'final' / 'all_jobs.csv'
            if jobs_file.exists():
                analyzer = JobAnalyzer(jobs_file)
                output = analyzer.generate_report()
                print(f"✅ Analyzing job market trends and generating insights - SUCCESS")
                print(f"✓ Analysis complete - Report generated at {output}")
                self.results['analysis']['analyzer'] = True
                return
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
        
        self.results['analysis']['analyzer'] = False
    
    def print_summary(self):
        """Print final execution summary"""
        elapsed = datetime.now() - self.start_time
        
        print("\n" + "="*80)
        print("📋 EXECUTION SUMMARY")
        print("="*80)
        
        # Job Counts
        data_dir = self.base_dir / 'data' / 'final'
        final_jobs_file = data_dir / 'all_jobs.csv'
        
        if final_jobs_file.exists():
            with open(final_jobs_file, 'r', encoding='utf-8') as f:
                job_count = sum(1 for _ in f) - 1  # Subtract header
            print(f"\n✅ Total Jobs Consolidated: {job_count}")
        
        # Report location
        insights_file = data_dir / 'HIRING_INSIGHTS_REPORT.md'
        if insights_file.exists():
            print(f"✅ Insights Report: {insights_file}")
        
        # Execution time
        print(f"\n⏱️  Total Execution Time: {elapsed.total_seconds():.1f} seconds")
        
        # Results breakdown
        print("\n📊 Results Breakdown:")
        print(f"  Scraping:     {sum(1 for v in self.results['scraping'].values() if v)}/{len(self.results['scraping'])} successful")
        print(f"  Consolidation: {'✅' if self.results['consolidation'].get('consolidator') else '❌'}")
        print(f"  Analysis:      {'✅' if self.results['analysis'].get('analyzer') else '❌'}")
        
        # Output files
        print("\n📁 Output Files:")
        output_files = [
            'all_jobs.csv',
            'all_job_links.csv',
            'HIRING_INSIGHTS_REPORT.md',
            'jobs_greenhouse.csv',
            'jobs_punjab.csv',
            'jobs_ashby.csv',
        ]
        
        for filename in output_files:
            filepath = data_dir / filename
            if filepath.exists():
                size = filepath.stat().st_size
                print(f"  ✅ {filename} ({size:,} bytes)")
            else:
                print(f"  ⚠️  {filename} (not found)")
        
        print("\n" + "="*80)
        print("🎉 JOB SCRAPING & ANALYSIS PIPELINE COMPLETE!")
        print("="*80 + "\n")
    
    def run_all(self, skip_scraping=False, skip_analysis=False):
        """Run complete pipeline"""
        print("\n" + "🚀 "*30)
        print("JOB SCRAPER & ANALYZER - MASTER EXECUTION SCRIPT")
        print("🚀 "*30 + "\n")
        
        try:
            if not skip_scraping:
                self.run_scraping()
            else:
                print("\n⏭️  Skipping scraping phase")
            
            self.run_consolidation()
            
            if not skip_analysis:
                self.run_analysis()
            else:
                print("\n⏭️  Skipping analysis phase")
            
            self.print_summary()
            return 0
        
        except KeyboardInterrupt:
            print("\n\n❌ Pipeline interrupted by user")
            return 1
        except Exception as e:
            print(f"\n\n❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Complete job scraping and analysis pipeline'
    )
    parser.add_argument(
        '--skip-scraping',
        action='store_true',
        help='Skip scraping phase (use existing data)'
    )
    parser.add_argument(
        '--skip-analysis',
        action='store_true',
        help='Skip analysis phase'
    )
    
    args = parser.parse_args()
    
    pipeline = JobPipelineManager()
    exit_code = pipeline.run_all(
        skip_scraping=args.skip_scraping,
        skip_analysis=args.skip_analysis
    )
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
