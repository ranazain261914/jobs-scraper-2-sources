# 🚀 Quick Start Guide - Job Scraping System# 🚀 QUICKSTART GUIDE



## Installation## Installation



```bash```powershell

pip install -r requirements.txt# Install required packages

```pip install -r requirements.txt

```

## 5-Minute Quickstart

## Running the Scrapers

### Run Single Scraper

### Option 1: Get the Master Consolidated Data (Fastest)

```bash```powershell

python -m scrapers.scraper_greenhousepython consolidate_jobs.py

``````

**Time:** <1 second  

Output:**Output:** 

- `data/raw/job_links_greenhouse.csv` - Extracted links- `data/raw/all_job_links.csv` (104 job links)

- `data/final/jobs_greenhouse.csv` - Job details- `data/final/all_jobs.csv` (103 complete jobs)



## Full Pipeline (All Sources)### Option 2: Scrape Individual Sources

```powershell

```bash# Punjab Government Jobs (53 jobs, ~3 min)

# 1. Greenhouse (3-4 min)python scraper_punjab.py

python -m scrapers.scraper_greenhouse

# Remote.com / Greenhouse Jobs (50 jobs, ~4 min)

# 2. Punjab (1-2 min)  python scraper_greenhouse.py

python -m scrapers.scraper_punjab

# Consolidate the results

# 3. Ashby (2-3 min)python consolidate_jobs.py

python -m scrapers.scraper_ashby```



# 4. Consolidate (<1 sec)### Option 3: Full Automated Pipeline

python -m utilities.consolidator```powershell

# Scrape all sources and consolidate (7-8 minutes total)

# 5. Verify (3-5 min)python master_scraper.py

python -m utilities.verifier```

```

## Understanding the Output

**Total: 10-15 minutes**

### Master Files (Use These!)

## Output Files- **`data/final/all_jobs.csv`** - 103 complete job records with all details

- **`data/raw/all_job_links.csv`** - 104 job posting URLs

### Raw Links

- `data/raw/job_links_greenhouse.csv`### Data Fields in all_jobs.csv

- `data/raw/job_links_punjab.csv````

- `data/raw/job_links_ashby.csv`job_title          - Position name

- `data/raw/all_job_links.csv` (consolidated)company_name       - Company hiring

location          - Job location

### Job Details  job_description   - Full job description

- `data/final/jobs_greenhouse.csv`employment_type   - Full-time, Part-time, etc.

- `data/final/jobs_punjab.csv`posted_date       - Date posted

- `data/final/jobs_ashby.csv`source            - Data source (punjab/greenhouse)

- `data/final/all_jobs.csv` (consolidated)job_url           - Direct link to job

extracted_at      - Extraction timestamp

## CSV Fields```



- `job_title` - Position name## Project Structure

- `company_name` - Company/Organization

- `location` - Job location```

- `employment_type` - Full-time, Part-time, etc.├── scraper_punjab.py          ✅ Working (53 jobs)

- `posted_date` - When posted├── scraper_greenhouse.py      ✅ Working (50 jobs)

- `job_description` - Full description├── scraper_ashby.py           ⚠️  Framework (needs API work)

- `job_url` - Direct link├── consolidate_jobs.py        ✅ Main consolidation tool

- `source` - greenhouse, punjab, or ashby├── master_scraper.py          ✅ Full pipeline orchestrator

- `department` - Department (if available)│

- `skills` - Required skills (if available)├── data/

- `extracted_at` - Extraction timestamp│   ├── raw/                   Raw job links (CSV files)

│   └── final/                 Processed job data (CSV files)

## Troubleshooting│

├── QUICKSTART.md              This file

**No jobs extracted?**├── PROJECT_DESCRIPTION.md     Complete technical documentation

- Check internet connection└── requirements.txt           Python dependencies

- Verify Chrome is installed```

- Try single scraper: `python -m scrapers.scraper_greenhouse`

## Quick Examples

**Chrome driver issues?**

```bash### View extracted data

pip install --upgrade webdriver-manager```powershell

```# Open in Excel or Python

Import-Csv 'data/final/all_jobs.csv' | Format-Table -AutoSize

**Timeout errors?**```

Increase timeout in `config.py`:

```python### Count records

TIMEOUTS = {```powershell

    'page_load': 20,@(Import-Csv 'data/final/all_jobs.csv').Count

    'element_wait': 15,# Output: 103 jobs

}```

```

### Get jobs by location

## File Structure```powershell

Import-Csv 'data/final/all_jobs.csv' | Where-Object {$_.location -like "*Lahore*"}

``````

scrap-pnjb-green/

├── config.py                      # Configuration## Troubleshooting

├── requirements.txt               # Dependencies

├── scrapers/**Q: No jobs extracted?**

│   ├── base_scraper.py           # Base class- Check internet connection

│   ├── scraper_greenhouse.py     # Greenhouse- Verify Chrome browser is installed

│   ├── scraper_punjab.py         # Punjab- Run individual scrapers for more details

│   └── scraper_ashby.py          # Ashby

├── utilities/**Q: Selenium errors?**

│   ├── consolidator.py           # Data consolidation- ChromeDriver may need updating

│   └── verifier.py               # Verification- Check if Chrome version matches Selenium version

└── data/

    ├── raw/                      # Links**Q: CSV not opening in Excel?**

    └── final/                    # Job details- Files are UTF-8 encoded

```- Excel may need to import as Text file



## Next Steps## Statistics



1. Run `python -m scrapers.scraper_greenhouse`- **Total Jobs:** 103

2. Check `data/final/jobs_greenhouse.csv`- **Total Links:** 104

3. Run other scrapers- **Success Rate:** 98%

4. Consolidate with `python -m utilities.consolidator`- **Data Sources:** 2 active (Punjab, Greenhouse)

5. Verify with `python -m utilities.verifier`- **Unique Companies:** 2

- **Unique Locations:** 20

See `docs/IMPLEMENTATION_GUIDE.md` for full documentation.- **Dataset Size:** 165 KB


## For More Information

See `PROJECT_DESCRIPTION.md` for:
- Complete technical documentation
- Architecture and design
- Data extraction methods
- Known limitations
- Future enhancements
