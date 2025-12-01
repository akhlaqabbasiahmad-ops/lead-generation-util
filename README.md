# Google Maps Scraper Utility

A Python utility to scrape business information and generate leads from Google Maps by business name.

## Features

- Search businesses by name on Google Maps
- Extract business location/address
- Extract phone number
- Extract email (when available)
- Extract website URL
- Extract business category/type
- Extract business hours
- Extract ratings and reviews
- **Lead Generation Features:**
  - Automatic lead scoring (0-100)
  - Lead status classification (Hot/Warm/Cold/New)
  - Data completeness percentage
  - CSV export for CRM import
  - Excel export with all lead fields
- Support for location-based searches
- Multiple result handling
- All results exported to separate folder

## Prerequisites

1. **Python 3.7+**
2. **Google Chrome browser** installed on your system
3. **ChromeDriver** - The utility uses Selenium which requires ChromeDriver

### Installing ChromeDriver

**Option 1: Automatic (Recommended)**
The utility can work with `webdriver-manager` for automatic driver management. Install it:
```bash
pip install webdriver-manager
```

**Option 2: Manual**
1. Download ChromeDriver from https://chromedriver.chromium.org/
2. Make sure it's in your PATH or in the same directory as the script

## Installation

1. Clone or download this repository
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### As a Python Module

```python
from google_maps_scraper import scrape_business_info

# Simple search
results = scrape_business_info("Starbucks")

# Search with location
results = scrape_business_info("Starbucks", location="New York, NY")

# Print results
for result in results:
    print(f"Name: {result.get('name')}")
    print(f"Address: {result.get('address')}")
    print(f"Phone: {result.get('phone')}")
    print(f"Email: {result.get('email')}")
```

### Using the Class Directly

```python
from google_maps_scraper import GoogleMapsScraper

# Create scraper instance
with GoogleMapsScraper(headless=False) as scraper:
    results = scraper.search_business("Coffee Shop", location="San Francisco, CA")
    
    for result in results:
        print(result)
```

### Command Line Usage

```bash
# Basic search (exports to Excel and CSV automatically)
python google_maps_scraper.py "Starbucks"

# Search with location
python google_maps_scraper.py "Starbucks" "New York, NY"
```

### Lead Generation

The utility automatically includes lead generation features:

```python
from google_maps_scraper import scrape_business_info

# Export to both Excel and CSV for lead generation
results = scrape_business_info(
    "Coffee Shop", 
    location="New York, NY",
    export_excel=True,      # Creates Excel file with all data
    export_leads=True       # Creates CSV file for CRM import
)

# Each result includes:
# - Lead Score (0-100): Based on data completeness
# - Lead Status: Hot (70+), Warm (50-69), Cold (30-49), New (<30)
# - Data Completeness: Percentage of fields filled
# - Lead Source: "Google Maps"
```

**Lead Scoring Breakdown:**
- Name: +10 points
- Address: +15 points
- Phone: +20 points
- Email: +25 points
- Website: +15 points
- Rating: +10 points
- Category: +5 points
- High Rating Bonus: +3-5 points (for ratings ≥4.0)

## Example Output

```
Searching for: Starbucks in New York, NY
--------------------------------------------------

Result 1:
  Name: Starbucks
  Address: 123 Main Street, New York, NY 10001
  Phone: (212) 555-1234
  Email: contact@starbucks.com
  Website: https://www.starbucks.com
  Category: Coffee Shop
  Rating: 4.5
  Reviews: 1234
  Lead Score: 85/100
  Lead Status: Hot
```

## Output Files

All results are saved in the `excel_results/` folder:

1. **Excel File** (`{business_name}_results.xlsx`):
   - Contains all business data
   - Includes lead generation fields
   - Formatted with headers and auto-sized columns

2. **CSV File** (`{business_name}_leads.csv`):
   - CRM-ready format
   - UTF-8 encoded for easy import
   - Includes all lead fields for sales teams

## Important Notes

1. **Email Availability**: Email addresses are rarely displayed directly on Google Maps. The scraper attempts to find them, but they may not always be available. You may need to visit the business's website separately to find email addresses.

2. **Rate Limiting**: Be respectful when scraping. Google may rate-limit or block requests if you make too many in a short period. Consider adding delays between requests.

3. **Legal Considerations**: 
   - Always respect Google's Terms of Service
   - Use this tool responsibly and ethically
   - Consider using the official Google Maps API for production applications

4. **Browser Requirements**: The scraper uses Selenium with Chrome. Make sure Chrome is installed and up to date.

5. **Dynamic Content**: Google Maps uses dynamic content loading. The scraper includes wait times, but you may need to adjust them based on your internet connection speed.

## Troubleshooting

### ChromeDriver Issues
If you encounter ChromeDriver errors:
- Make sure Chrome is installed and updated
- Install `webdriver-manager`: `pip install webdriver-manager`
- Or manually download ChromeDriver matching your Chrome version

### No Results Found
- Try being more specific with the business name
- Add a location parameter to narrow down results
- Check your internet connection
- Google Maps structure may have changed - the selectors may need updating

### Timeout Errors
- Increase the `wait_time` parameter when creating the scraper
- Check your internet connection speed

## License

This utility is provided as-is for educational and personal use. Please use responsibly and in accordance with Google's Terms of Service.

