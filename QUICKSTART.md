# Quick Start Guide

## One-Minute Setup

### Prerequisites
- Python 3.9+
- Chrome or Firefox browser
- ~2GB disk space

### Installation
```powershell
# Clone repository
git clone https://github.com/YOUR-USERNAME/job-scraper.git
cd job-scraper

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Everything
```powershell
python run_pipeline.py
```

That's it! The pipeline will:
1. ✅ Extract job links from 3 websites (5-15 min)
2. ✅ Extract job data from all links (1-2 hours)
3. ✅ Clean and normalize data (<1 min)
4. ✅ Generate analysis (<2 min)

## Output Files

After running, you'll have:
- `data/raw/job_links.csv` - All extracted job links
- `data/final/jobs.csv` - Raw job data
- `data/final/jobs_cleaned.csv` - Cleaned, ready-to-use data
- `analysis/analysis_results.json` - Market analysis

## Run Individual Steps

```powershell
# Extract links only
cd selenium
python extract_links.py

# Extract job data only
python extract_job_data.py

# Clean data only
cd ..
python data_cleaning.py

# Analyze data only
cd analysis
python analysis.py
```

## What Gets Scraped

### Job Fields
- Job Title
- Company Name  
- Location
- Employment Type (Full-time, Part-time, Contract, etc.)
- Job Description
- Required Skills
- Experience Level
- And more...

### Websites
1. **Greenhouse** - greenhouse.com/careers/opportunities
2. **Ashby** - ashbyhq.com/careers
3. **Punjab Jobs** - jobs.punjab.gov.pk/new_recruit/jobs

## Key Files

- `README.md` - Quick overview
- `COMPLETE_GUIDE.md` - Full documentation
- `PROJECT_COMPLETION_SUMMARY.md` - Project details
- `selenium/` - Web scraping code
- `analysis/` - Data analysis code
- `data_cleaning.py` - Data cleaning

## Troubleshooting

### Issue: "Module not found"
```powershell
pip install -r requirements.txt
```

### Issue: "No links extracted"
- Check internet connection
- Website structure may have changed
- Try running with `headless=False` to debug

### Issue: "Slow execution"
This is normal! The pipeline:
- Adds 2-5 second delays between requests (responsible scraping)
- Visits 500+ job pages (1-2 hours total)
- Extracts detailed data from each page

## Next Steps

1. Check output in `data/final/` folder
2. View analysis in `analysis/analysis_results.json`
3. Edit CSV files in Excel/Pandas
4. Extend the project (see COMPLETE_GUIDE.md)

## Git Workflow

```powershell
# View history
git log --oneline --all --graph

# Create feature branch
git checkout -b feature/my-feature

# Push to GitHub
git push -u origin feature/my-feature

# Merge to main
git checkout main
git merge feature/my-feature
git push origin main
```

## Performance

| Step | Time |
|------|------|
| Link extraction | 5-15 min |
| Job data extraction | 1-2 hours |
| Data cleaning | <1 min |
| Analysis | <2 min |
| **Total** | **2-3 hours** |

## Supported Python Versions
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

## Support

- See `README.md` for overview
- See `COMPLETE_GUIDE.md` for detailed help
- Check logs: `extraction.log`, `job_extraction.log`
- Review code comments for details

## License

MIT License - See `LICENSE` file

---

**Ready to scrape? Start with:** `python run_pipeline.py`
