"""
Debug script for influencer discovery
Run this to test and debug the influencer discovery functionality
"""

import sys
import traceback
from influencer_discovery import InfluencerDiscovery, export_influencers_to_excel

def test_instagram_discovery():
    """Test Instagram creator discovery."""
    print("=" * 60)
    print("Testing Instagram Creator Discovery")
    print("=" * 60)
    
    scraper = None
    try:
        print("\n1. Initializing scraper (headless=False for debugging)...")
        scraper = InfluencerDiscovery(headless=False)
        print("   ✓ Scraper initialized successfully")
        
        print("\n2. Starting Instagram discovery...")
        niche = "mom"  # Changed to mom/parenting niche
        max_results = 100  # Increased to 100 to get more records
        print(f"   Niche: {niche}")
        print(f"   Max results: {max_results}")
        
        results = scraper.discover_instagram_creators(
            niche=niche,
            location=None,
            min_followers=None,  # No minimum - get all results
            max_followers=None,
            max_results=max_results
        )
        
        print(f"\n3. Discovery completed!")
        print(f"   Found {len(results)} creators")
        
        if results:
            print("\n4. Results:")
            for i, creator in enumerate(results, 1):
                print(f"\n   Creator {i}:")
                for key, value in creator.items():
                    if value:
                        print(f"     {key}: {value}")
            
            print("\n5. Exporting to Excel...")
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"test_instagram_influencers_{timestamp}.xlsx"
            export_influencers_to_excel(results, excel_filename, "excel_results")
            print(f"   ✓ Exported successfully to {excel_filename}")
        else:
            print("\n   ⚠ No results found")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)
    finally:
        if scraper:
            print("\n6. Closing scraper...")
            scraper.close()
            print("   ✓ Scraper closed")

def test_tiktok_discovery():
    """Test TikTok creator discovery."""
    print("\n" + "=" * 60)
    print("Testing TikTok Creator Discovery")
    print("=" * 60)
    
    scraper = None
    try:
        print("\n1. Initializing scraper...")
        scraper = InfluencerDiscovery(headless=False)
        print("   ✓ Scraper initialized")
        
        print("\n2. Starting TikTok discovery...")
        results = scraper.discover_tiktok_creators(
            niche="fitness",
            max_results=3
        )
        
        print(f"\n3. Found {len(results)} creators")
        if results:
            for i, creator in enumerate(results, 1):
                print(f"\n   Creator {i}: {creator.get('username', 'N/A')}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        traceback.print_exc()
    finally:
        if scraper:
            scraper.close()

def test_youtube_discovery():
    """Test YouTube creator discovery."""
    print("\n" + "=" * 60)
    print("Testing YouTube Creator Discovery")
    print("=" * 60)
    
    scraper = None
    try:
        print("\n1. Initializing scraper...")
        scraper = InfluencerDiscovery(headless=False)
        print("   ✓ Scraper initialized")
        
        print("\n2. Starting YouTube discovery...")
        results = scraper.discover_youtube_creators(
            niche="fitness",
            max_results=3
        )
        
        print(f"\n3. Found {len(results)} creators")
        if results:
            for i, creator in enumerate(results, 1):
                print(f"\n   Creator {i}: {creator.get('channel_name', creator.get('handle', 'N/A'))}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        traceback.print_exc()
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    print("Influencer Discovery Debug Test")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        if platform == "instagram":
            test_instagram_discovery()
        elif platform == "tiktok":
            test_tiktok_discovery()
        elif platform == "youtube":
            test_youtube_discovery()
        else:
            print(f"Unknown platform: {platform}")
            print("Usage: python test_influencer_debug.py [instagram|tiktok|youtube]")
    else:
        # Test Instagram by default
        test_instagram_discovery()

