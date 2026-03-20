#!/usr/bin/env python3
"""
Job Market Analysis & Insights Report Generator

Analyzes consolidated job data to extract hiring insights:
- Top skills from job descriptions
- Geographic distribution of openings
- Company hiring activity
- Entry-level/internship positions
- Most common job titles
"""

import csv
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


class JobAnalyzer:
    """Analyze job market trends and insights"""
    
    def __init__(self, jobs_csv_path):
        """Initialize analyzer with jobs CSV file"""
        self.jobs_csv_path = Path(jobs_csv_path)
        self.jobs = []
        self.load_jobs()
    
    def load_jobs(self):
        """Load jobs from CSV file"""
        if not self.jobs_csv_path.exists():
            raise FileNotFoundError(f"Jobs file not found: {self.jobs_csv_path}")
        
        with open(self.jobs_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.jobs = list(reader)
        
        print(f"✓ Loaded {len(self.jobs)} jobs")
    
    def extract_top_skills(self, top_n=15):
        """Extract most common skills from job descriptions"""
        # Common tech skills and keywords to search for
        skills_keywords = {
            # Programming Languages
            'Python': r'\bpython\b',
            'JavaScript': r'\bjavascript|js\b',
            'Java': r'\bjava\b',
            'C++': r'\bc\+\+|cpp\b',
            'C#': r'\bc#\b',
            'Go': r'\bgo\b|\bgolang\b',
            'Rust': r'\brust\b',
            'PHP': r'\bphp\b',
            'SQL': r'\bsql\b',
            
            # Frameworks & Libraries
            'React': r'\breact\b',
            'Vue': r'\bvue\b',
            'Angular': r'\bangular\b',
            'Django': r'\bdjango\b',
            'Flask': r'\bflask\b',
            'Node.js': r'\bnode\.js|nodejs\b',
            'Spring': r'\bspring\b',
            'FastAPI': r'\bfastapi\b',
            
            # Cloud & DevOps
            'AWS': r'\baws\b|amazon\s*web\s*services',
            'Azure': r'\bazure\b',
            'GCP': r'\bgcp\b|google\s*cloud',
            'Docker': r'\bdocker\b',
            'Kubernetes': r'\bkubernetes|k8s\b',
            'CI/CD': r'\bci/cd|cicd\b',
            'Git': r'\bgit\b',
            
            # Data & Analytics
            'SQL': r'\bsql\b',
            'Machine Learning': r'\bmachine\s*learning|ml\b',
            'Data Science': r'\bdata\s*science',
            'Pandas': r'\bpandas\b',
            'NumPy': r'\bnumpy\b',
            'TensorFlow': r'\btensorflow\b',
            'Big Data': r'\bbig\s*data|hadoop|spark\b',
            
            # Soft Skills
            'Communication': r'\bcommunication\b',
            'Leadership': r'\bleadership\b',
            'Problem-solving': r'\bproblem[\s-]*solv',
            'Teamwork': r'\bteamwork|team\s*player\b',
            'Project Management': r'\bproject\s*management|pmp\b',
            'Agile': r'\bagile|scrum\b',
            
            # Other
            'REST API': r'\brest\s*api|restful\b',
            'GraphQL': r'\bgraphql\b',
            'Security': r'\bsecurity|secure|encryption\b',
            'Testing': r'\btesting|unit\s*test|automation\b',
        }
        
        skill_counts = Counter()
        
        for job in self.jobs:
            description = (job.get('job_description', '') or '').lower()
            title = (job.get('job_title', '') or '').lower()
            
            combined_text = description + ' ' + title
            
            for skill, pattern in skills_keywords.items():
                if re.search(pattern, combined_text, re.IGNORECASE):
                    skill_counts[skill] += 1
        
        return skill_counts.most_common(top_n)
    
    def get_geographic_distribution(self):
        """Analyze job distribution by location"""
        locations = Counter()
        
        for job in self.jobs:
            location = (job.get('location', '') or '').strip()
            if location and location.lower() != 'none':
                # Extract country or region (last part usually)
                parts = [p.strip() for p in location.split(',')]
                if parts and parts[-1]:
                    region = parts[-1]  # Last part is usually country/region
                    locations[region] += 1
            else:
                # Count remote/unspecified
                locations['Remote/Not Specified'] += 1
        
        return locations.most_common(15) if locations else [('Unknown', len(self.jobs))]
    
    def get_top_companies(self, top_n=10):
        """Get companies with most job openings"""
        companies = Counter()
        
        for job in self.jobs:
            company = (job.get('company_name', '') or '').strip()
            if company:
                companies[company] += 1
        
        return companies.most_common(top_n)
    
    def count_entry_level_positions(self):
        """Count internship, junior, and entry-level positions"""
        entry_level_patterns = {
            'Internship': r'\bintern',
            'Junior': r'\bjunior\b',
            'Entry-level': r'\bentry[\s-]*level\b',
            'Graduate': r'\bgraduate\b',
            'Associate': r'\bassociate\b',
            'Trainee': r'\btrainee\b',
        }
        
        entry_level_counts = Counter()
        matched_jobs = []
        
        for job in self.jobs:
            title = (job.get('job_title', '') or '').lower()
            description = (job.get('job_description', '') or '').lower()
            
            combined = title + ' ' + description
            
            for level, pattern in entry_level_patterns.items():
                if re.search(pattern, combined, re.IGNORECASE):
                    entry_level_counts[level] += 1
                    if title not in [j['job_title'] for j in matched_jobs]:
                        matched_jobs.append(job)
                    break
        
        return entry_level_counts, len(matched_jobs)
    
    def get_top_job_titles(self, top_n=15):
        """Get most common job titles"""
        # Normalize titles
        titles = Counter()
        
        for job in self.jobs:
            title = (job.get('job_title', '') or '').strip()
            if title:
                # Clean up title
                title = re.sub(r'\s+', ' ', title).title()
                titles[title] += 1
        
        return titles.most_common(top_n)
    
    def get_job_title_families(self):
        """Extract job families based on title keywords"""
        title_families = {
            'Engineering/Developer': r'\bengineer|developer|programmer|architect|devops\b',
            'Sales': r'\bsales|account\s*executive|business\s*development\b',
            'Customer Success': r'\bcustomer\s*success|customer\s*support|support\b',
            'Product Management': r'\bproduct\s*manager|pm\b',
            'Design': r'\bdesigner|ux|ui|design\b',
            'Marketing': r'\bmarketing|marketing\s*manager\b',
            'Data/Analytics': r'\bdata|analytics|analyst\b',
            'Operations': r'\boperations|ops\b',
            'Management': r'\bmanager|director|head\b',
            'Finance': r'\bfinance|accountant|accounting\b',
            'HR/People': r'\bhr|human\s*resources|recruiter\b',
            'Legal': r'\blegal|counsel|attorney\b',
        }
        
        family_counts = Counter()
        
        for job in self.jobs:
            title = (job.get('job_title', '') or '').lower()
            
            matched = False
            for family, pattern in title_families.items():
                if re.search(pattern, title, re.IGNORECASE):
                    family_counts[family] += 1
                    matched = True
                    break
            
            if not matched:
                family_counts['Other'] += 1
        
        return family_counts
    
    def generate_report(self, output_path=None):
        """Generate comprehensive hiring insights report"""
        if output_path is None:
            output_path = self.jobs_csv_path.parent / 'HIRING_INSIGHTS_REPORT.md'
        
        # Generate insights
        top_skills = self.extract_top_skills()
        locations = self.get_geographic_distribution()
        companies = self.get_top_companies()
        entry_level_counts, entry_level_total = self.count_entry_level_positions()
        top_titles = self.get_top_job_titles()
        title_families = self.get_job_title_families()
        
        # Create report
        report = f"""# Job Market Analysis & Hiring Insights Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Jobs Analyzed:** {len(self.jobs)}

---

## 📊 Executive Summary

This report analyzes {len(self.jobs)} job postings across multiple platforms to identify hiring trends, in-demand skills, geographic hotspots, and market composition.

---

## 🎯 Top In-Demand Skills

### Technical & Professional Skills (Top 15)

| Rank | Skill | Frequency | % of Jobs |
|------|-------|-----------|-----------|
"""
        
        for idx, (skill, count) in enumerate(top_skills, 1):
            percentage = (count / len(self.jobs)) * 100
            report += f"| {idx} | **{skill}** | {count} | {percentage:.1f}% |\n"
        
        report += f"""

### Key Insights
- **Most Demanded:** {top_skills[0][0]} appears in {top_skills[0][1]} jobs
- **Skill Diversity:** {len([s for s, c in top_skills if c >= 2])} skills appear in 2+ job postings
- **Average Skills per Job:** {sum(c for s, c in top_skills) / len(self.jobs):.1f}

---

## 🌍 Geographic Distribution

### Job Openings by Region (Top 15)

| Rank | Location | Count | % of Jobs |
|------|----------|-------|-----------|
"""
        
        for idx, (location, count) in enumerate(locations, 1):
            percentage = (count / len(self.jobs)) * 100
            report += f"| {idx} | {location} | {count} | {percentage:.1f}% |\n"
        
        report += f"""

### Geographic Insights
- **Hottest Market:** {locations[0][0] if locations else 'N/A'} with {locations[0][1] if locations else 0} job openings
- **Geographic Spread:** {len(locations)} different regions represented
- **Top 3 Regions:** {locations[0][0] if locations else 'N/A'} ({locations[0][1] if locations else 0}), {locations[1][0] if len(locations) > 1 else 'N/A'} ({locations[1][1] if len(locations) > 1 else 0}), {locations[2][0] if len(locations) > 2 else 'N/A'} ({locations[2][1] if len(locations) > 2 else 0})

---

## 🏢 Top Hiring Companies

### Companies with Most Job Openings (Top 10)

| Rank | Company | Openings | % of Jobs |
|------|---------|----------|-----------|
"""
        
        for idx, (company, count) in enumerate(companies, 1):
            percentage = (count / len(self.jobs)) * 100
            report += f"| {idx} | {company} | {count} | {percentage:.1f}% |\n"
        
        report += f"""

### Hiring Insights
- **Most Active Employer:** {companies[0][0] if companies else 'N/A'} with {companies[0][1] if companies else 0} open positions
- **Employer Diversity:** {len(companies)} companies hiring
- **Top Employer's Share:** {(companies[0][1] / len(self.jobs) * 100):.1f}% of all jobs

---

## 👨‍💼 Job Level & Career Stage

### Entry-Level Position Count

| Level | Count | % of Jobs |
|-------|-------|-----------|
"""
        
        for level, count in sorted(entry_level_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.jobs)) * 100
            report += f"| {level} | {count} | {percentage:.1f}% |\n"
        
        report += f"""

**Total Entry-Level/Junior Positions:** {entry_level_total} ({(entry_level_total/len(self.jobs)*100):.1f}%)

### Career Level Insights
- **Entry-Level Availability:** {entry_level_total} positions suitable for career starters
- **Opportunity Type:** Mix of internships, junior roles, and entry-level positions
- **Career Progression:** {len(self.jobs) - entry_level_total} mid-level to senior positions

---

## 💼 Job Titles & Roles

### Most Common Job Titles (Top 15)

| Rank | Job Title | Count |
|------|-----------|-------|
"""
        
        for idx, (title, count) in enumerate(top_titles, 1):
            report += f"| {idx} | {title} | {count} |\n"
        
        report += f"""

### Job Title Families (Role Categories)

| Role Family | Count | % of Jobs |
|-------------|-------|-----------|
"""
        
        for family, count in sorted(title_families.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.jobs)) * 100
            report += f"| {family} | {count} | {percentage:.1f}% |\n"
        
        report += f"""

### Role Distribution Insights
- **Most Common Family:** {max(title_families.items(), key=lambda x: x[1])[0]} with {max(title_families.items(), key=lambda x: x[1])[1]} positions
- **Role Diversity:** {len(title_families)} different job families
- **Engineering Focus:** {title_families.get('Engineering/Developer', 0)} engineering/developer roles ({title_families.get('Engineering/Developer', 0)/len(self.jobs)*100:.1f}%)

---

## 📈 Market Composition

### Job Source Distribution

"""
        
        source_counts = Counter()
        for job in self.jobs:
            source = job.get('source', 'unknown')
            source_counts[source] += 1
        
        for source, count in source_counts.most_common():
            percentage = (count / len(self.jobs)) * 100
            report += f"- **{source.title()}:** {count} jobs ({percentage:.1f}%)\n"
        
        report += f"""

### Employment Type

"""
        
        employment_counts = Counter()
        for job in self.jobs:
            emp_type = job.get('employment_type', 'Not specified')
            if emp_type:
                employment_counts[emp_type] += 1
        
        if employment_counts:
            for emp_type, count in employment_counts.most_common():
                percentage = (count / len(self.jobs)) * 100
                report += f"- **{emp_type}:** {count} jobs ({percentage:.1f}%)\n"
        
        report += f"""

---

## 🔍 Key Findings & Recommendations

### For Job Seekers

1. **High-Demand Skills to Develop:**
   - Focus on: {', '.join([s[0] for s in top_skills[:3]])}
   - These skills appear in {sum(c for s, c in top_skills[:3])} job postings

2. **Geographic Opportunities:**
   - Most positions available in: {locations[0][0] if locations else 'N/A'}
   - Consider remote opportunities with {companies[0][0] if companies else 'N/A'}

3. **Entry-Level Opportunities:**
   - {entry_level_total} positions available for career starters
   - Primary entry routes: {', '.join([k for k, v in sorted(entry_level_counts.items(), key=lambda x: x[1], reverse=True)[:2]])}

4. **Growing Fields:**
   - {max(title_families.items(), key=lambda x: x[1])[0]}: {max(title_families.items(), key=lambda x: x[1])[1]} openings
   - Career growth opportunity in this sector

### For Employers

1. **Competitive Landscape:**
   - {len(companies)} active companies in this market
   - Average openings per company: {sum(c for _, c in companies) / len(companies):.1f}

2. **Skill Market:**
   - Top candidates should have: {', '.join([s[0] for s in top_skills[:3]])}
   - {len([s for s, c in top_skills if c >= 5])} highly demanded specialized skills

3. **Hiring Trends:**
   - {(entry_level_total/len(self.jobs)*100):.1f}% of market is entry-level focused
   - Opportunity to invest in talent development programs

---

## 📋 Data Quality Notes

- **Data Sources:** {len(source_counts)} different job platforms
- **Total Records Analyzed:** {len(self.jobs)}
- **Geographic Coverage:** {len(locations)} regions
- **Unique Companies:** {len(companies)}
- **Unique Job Titles:** {len(title_families)} role categories

---

## 📅 Report Metadata

- **Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}
- **Data Extraction Date:** See source job files
- **Next Update:** Recommended quarterly for trend analysis

---

*Report generated by Job Market Analysis System*  
*For data inquiries, refer to the consolidated job CSV files*
"""
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✓ Report generated: {output_path}")
        return str(output_path)


def main():
    """Main entry point"""
    import sys
    
    # Find the all_jobs.csv file
    current_dir = Path(__file__).parent
    jobs_file = current_dir / 'data' / 'final' / 'all_jobs.csv'
    
    if not jobs_file.exists():
        print("❌ Error: all_jobs.csv not found")
        print(f"   Expected at: {jobs_file}")
        sys.exit(1)
    
    try:
        analyzer = JobAnalyzer(jobs_file)
        output_file = analyzer.generate_report()
        print(f"\n✓ Analysis complete!")
        print(f"✓ Report saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
