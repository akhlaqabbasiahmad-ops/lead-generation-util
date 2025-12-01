# Google Web Search Scraper

A Python utility to search Google (not just Maps) and extract business information from websites across the internet for lead generation.

## Features

- **Broad Web Search**: Searches Google web results (not limited to Google Maps)
- **Website Scraping**: Visits individual websites to extract detailed information
- **Multi-page Results**: Can extract results from multiple Google search pages
- **Lead Generation**: Includes lead scoring, status classification, and CRM-ready exports
- **Data Extraction**:
  - Business name and title
  - Address
  - Phone number
  - Email address
  - Website URL
  - Business category
  - Ratings (when available)
  - Search snippet/description

## Prerequisites

Same as the Google Maps scraper:
- Python 3.7+
- Google Chrome browser
- ChromeDriver (automatically managed by webdriver-manager)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Basic search
python google_web_scraper.py "veterinary doctors in Lahore"

# Search with max results limit
python google_web_scraper.py "veterinary doctors in Lahore" 20
```

### Python Module

```python
from google_web_scraper import search_businesses_web

# Search and export
results = search_businesses_web(
    "veterinary doctors in Lahore",
    max_results=20,
    export_excel=True,
    export_csv=True
)

# Access results
for result in results:
    print(f"Name: {result.get('name')}")
    print(f"Phone: {result.get('phone')}")
    print(f"Email: {result.get('email')}")
    print(f"Website: {result.get('website')}")
    print(f"Lead Score: {result.get('lead_score')}/100")
    print(f"Lead Status: {result.get('lead_status')}")
```

## How It Works

1. **Google Search**: Performs a Google web search with your query
2. **Result Extraction**: Extracts basic information from search result snippets
3. **Website Visits**: Visits each website to extract detailed information:
   - Phone numbers
   - Email addresses
   - Physical addresses
   - Business names
   - Categories
4. **Lead Scoring**: Calculates lead scores based on data completeness
5. **Export**: Saves results to Excel and CSV files

## Output Files

Results are saved in the `excel_results/` folder:

- **Excel File**: `{query}_web_results.xlsx` - Full data with formatting
- **CSV File**: `{query}_web_leads.csv` - CRM-ready format

## Lead Scoring

Same scoring system as the Maps scraper:
- Name: +10 points
- Address: +15 points
- Phone: +20 points
- Email: +25 points
- Website: +15 points
- Rating: +10 points
- Category: +5 points

**Lead Status:**
- **Hot**: 70+ points
- **Warm**: 50-69 points
- **Cold**: 30-49 points
- **New**: <30 points

## Differences from Google Maps Scraper

| Feature | Google Maps Scraper | Google Web Scraper |
|---------|-------------------|-------------------|
| Search Source | Google Maps only | Entire Google web search |
| Results | Maps listings | Websites, directories, listings |
| Data Source | Google Maps data | Individual websites |
| Coverage | Maps-registered businesses | All web-visible businesses |
| Speed | Faster (single source) | Slower (visits multiple sites) |

## Use Cases

**Google Web Scraper is better for:**
- Finding businesses not on Google Maps
- Getting information from business websites directly
- Finding businesses in directories and listings
- Broader market research
- Finding contact information from official websites

**Google Maps Scraper is better for:**
- Quick location-based searches
- Getting verified business information
- Finding businesses with physical locations
- Getting ratings and reviews

## Important Notes

1. **Rate Limiting**: The scraper visits individual websites, so it's slower than Maps scraping. Be respectful with delays.

2. **Data Quality**: Information quality varies as it comes from different websites with different structures.

3. **Legal Considerations**: 
   - Respect robots.txt files
   - Don't overload servers with requests
   - Use responsibly and ethically
   - Check website terms of service

4. **Deduplication**: The scraper automatically removes duplicate results based on URL.

5. **Filtering**: Phone numbers and emails are filtered to remove tracking/analytics services.

## Troubleshooting

### No Results Found
- Try different search terms
- Check your internet connection
- Google may have changed their page structure

### Slow Performance
- Reduce `max_results` parameter
- The scraper visits each website, which takes time
- Consider using headless mode for faster execution

### Missing Data
- Some websites may block automated access
- Some websites may not have structured data
- Try the Google Maps scraper for more consistent data

## Example

```bash
python google_web_scraper.py "restaurants in Lahore" 15
```

This will:
1. Search Google for "restaurants in Lahore"
2. Extract up to 15 results
3. Visit each website to get detailed information
4. Calculate lead scores
5. Export to Excel and CSV files

## License

This utility is provided as-is for educational and personal use. Please use responsibly and in accordance with website terms of service.

