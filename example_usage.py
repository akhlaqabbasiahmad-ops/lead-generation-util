"""
Example usage of the Google Maps Scraper utility.
"""

from google_maps_scraper import scrape_business_info, GoogleMapsScraper
import json
import time


def example_simple_search():
    """Example of a simple business search."""
    print("=" * 60)
    print("Example 1: Simple Business Search")
    print("=" * 60)
    
    results = scrape_business_info("Apple Store")
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(json.dumps(result, indent=2))


def example_search_with_location():
    """Example of searching with a specific location."""
    print("\n" + "=" * 60)
    print("Example 2: Search with Location")
    print("=" * 60)
    
    results = scrape_business_info("Starbucks", location="Times Square, New York")
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Name: {result.get('name', 'N/A')}")
        print(f"  Address: {result.get('address', 'N/A')}")
        print(f"  Phone: {result.get('phone', 'N/A')}")
        print(f"  Email: {result.get('email', 'N/A')}")


def example_using_class_directly():
    """Example of using the GoogleMapsScraper class directly."""
    print("\n" + "=" * 60)
    print("Example 3: Using Class Directly with Context Manager")
    print("=" * 60)
    
    with GoogleMapsScraper(headless=False) as scraper:
        # Search for multiple businesses
        businesses = ["McDonald's", "Subway"]
        
        for business in businesses:
            print(f"\nSearching for: {business}")
            results = scraper.search_business(business, location="Los Angeles, CA")
            
            if results:
                result = results[0]
                print(f"  Found: {result.get('name', 'N/A')}")
                print(f"  Address: {result.get('address', 'N/A')}")
                print(f"  Phone: {result.get('phone', 'N/A')}")
            print("-" * 40)


def example_batch_processing():
    """Example of processing multiple businesses."""
    print("\n" + "=" * 60)
    print("Example 4: Batch Processing")
    print("=" * 60)
    
    business_list = [
        ("Coffee Shop", "Seattle, WA"),
        ("Pizza Restaurant", "Chicago, IL"),
        ("Bookstore", "Portland, OR")
    ]
    
    all_results = []
    
    with GoogleMapsScraper(headless=False) as scraper:
        for business_name, location in business_list:
            print(f"\nProcessing: {business_name} in {location}")
            results = scraper.search_business(business_name, location)
            all_results.extend(results)
            time.sleep(2)  # Be respectful with delays
    
    # Save results to JSON
    with open('scraped_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nSaved {len(all_results)} results to scraped_results.json")


if __name__ == "__main__":
    # Run examples
    try:
        example_simple_search()
        time.sleep(3)
        
        example_search_with_location()
        time.sleep(3)
        
        example_using_class_directly()
        time.sleep(3)
        
        # Uncomment to run batch processing example
        # example_batch_processing()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {str(e)}")

