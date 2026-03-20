"""
Selenium module entry point

Allows running scrapers as: python -m selenium.scraper_NAME
"""

import sys
from pathlib import Path

# Add selenium directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

# Handle different scrapers
if len(sys.argv) > 1:
    scraper = sys.argv[1]
    
    if scraper == 'punjab':
        from scraper_punjab import main
        main()
    elif scraper == 'greenhouse':
        from scraper_greenhouse import main
        main()
    elif scraper == 'ashby':
        from scraper_ashby import main
        main()
    else:
        print(f"Unknown scraper: {scraper}")
        print("Available: punjab, greenhouse, ashby")
        sys.exit(1)
else:
    print("Usage: python -m selenium <scraper_name>")
    print("Available scrapers: punjab, greenhouse, ashby")
    sys.exit(1)
