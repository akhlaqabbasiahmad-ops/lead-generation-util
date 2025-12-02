"""
Social Media Search Scraper

This module provides functionality to search and scrape data from social media platforms
(Facebook, Instagram) by name without requiring URLs.

Usage:
    from social_media_search_scraper import SocialMediaSearchScraper
    
    scraper = SocialMediaSearchScraper(headless=False)
    fb_results = scraper.search_facebook("business name")
    ig_results = scraper.search_instagram("business name")
    scraper.close()
"""

import time
import re
import os
from typing import Dict, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import platform

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


class SocialMediaSearchScraper:
    """
    Scraper for searching and extracting data from social media platforms.
    Can search Facebook pages and Instagram profiles by name.
    """
    
    def __init__(self, headless: bool = False, wait_time: int = 10):
        """
        Initialize the social media search scraper.
        
        Args:
            headless: Run browser in headless mode (default: False)
            wait_time: Maximum wait time for elements to load (default: 10 seconds)
        """
        self.wait_time = wait_time
        self.setup_driver(headless)
    
    def setup_driver(self, headless: bool):
        """Setup Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        # Anti-detection options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Platform-specific options
        is_windows = platform.system() == 'Windows'
        is_linux = platform.system() == 'Linux'
        
        if headless:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            if is_linux:
                chrome_options.add_argument('--remote-debugging-port=9222')
                chrome_options.add_argument('--single-process')
        else:
            # GUI mode - minimal options for Windows
            if is_windows:
                chrome_options.add_argument('--disable-gpu')
        
        # User agent
        if is_linux or headless:
            chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        else:
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(30)
            
        except Exception as e:
            raise Exception(f"Failed to initialize Chrome driver. Error: {str(e)}")
    
    def search_facebook(self, search_query: str, max_results: int = 10) -> List[Dict[str, Optional[str]]]:
        """
        Search Facebook for pages/profiles and extract data.
        
        Args:
            search_query: Name to search for
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            List of dictionaries containing Facebook page/profile data
        """
        results = []
        try:
            print(f"Searching Facebook for: {search_query}")
            
            # Navigate to Facebook search
            search_url = f"https://www.facebook.com/search/pages/?q={search_query.replace(' ', '%20')}"
            self.driver.get(search_url)
            time.sleep(5)
            
            # Handle login prompt if it appears
            try:
                # Try to find and close any login prompts
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label='Close'], [aria-label='close'], button[type='button']")
                for btn in close_buttons[:3]:  # Try first few close buttons
                    try:
                        if btn.is_displayed():
                            btn.click()
                            time.sleep(1)
                            break
                    except:
                        continue
            except:
                pass
            
            # Wait for results to load
            time.sleep(3)
            
            # Scroll to load more results
            for scroll in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find all result items
            result_selectors = [
                "div[role='article']",
                "div[data-pagelet='SearchResults'] div[role='article']",
                "div[class*='x1y1aw1k']",
                "div[class*='x1n2onr6']"
            ]
            
            result_items = []
            for selector in result_selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(items) > 0:
                        result_items = items
                        break
                except:
                    continue
            
            print(f"Found {len(result_items)} potential results")
            
            # Extract data from each result
            for idx, item in enumerate(result_items[:max_results], 1):
                try:
                    print(f"Processing Facebook result {idx}/{min(len(result_items), max_results)}...")
                    
                    # Scroll item into view
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", item)
                    time.sleep(1)
                    
                    # Extract data
                    page_data = self._extract_facebook_page_data(item)
                    if page_data:
                        results.append(page_data)
                        print(f"  ✓ Extracted: {page_data.get('name', 'Unknown')}")
                    
                except Exception as e:
                    print(f"  ⊗ Error processing result {idx}: {str(e)}")
                    continue
            
            print(f"\n✓ Extracted {len(results)} Facebook results")
            
        except Exception as e:
            print(f"Error searching Facebook: {str(e)}")
        
        return results
    
    def _extract_facebook_page_data(self, element) -> Optional[Dict[str, Optional[str]]]:
        """Extract data from a Facebook page result element."""
        try:
            data = {
                "name": None,
                "url": None,
                "followers": None,
                "likes": None,
                "category": None,
                "description": None,
                "location": None,
                "phone": None,
                "email": None,
                "website": None,
                "verified": False
            }
            
            # Extract name
            name_selectors = [
                "span[dir='auto']",
                "a[role='link'] span",
                "h2 span",
                "div[class*='x1heor9g'] span"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name_text = name_elem.text.strip()
                    if name_text and len(name_text) > 0 and len(name_text) < 200:
                        data["name"] = name_text
                        break
                except:
                    continue
            
            # Extract URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a[role='link']")
                href = link_elem.get_attribute("href")
                if href and "facebook.com" in href:
                    data["url"] = href
            except:
                pass
            
            # Extract followers/likes
            try:
                text = element.text
                # Look for follower patterns
                follower_patterns = [
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:followers|people\s+follow)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:likes|people\s+like)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:fans)'
                ]
                
                for pattern in follower_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        if 'followers' in text.lower() or 'people follow' in text.lower():
                            data["followers"] = count
                        elif 'likes' in text.lower() or 'people like' in text.lower():
                            data["likes"] = count
                        break
            except:
                pass
            
            # Extract category
            try:
                category_elem = element.find_element(By.CSS_SELECTOR, "span[class*='x1i10hfl'], div[class*='x1i10hfl']")
                category_text = category_elem.text.strip()
                if category_text and len(category_text) < 100:
                    data["category"] = category_text
            except:
                pass
            
            # Check if verified
            try:
                verified_icon = element.find_element(By.CSS_SELECTOR, "[aria-label*='Verified'], [aria-label*='verified']")
                data["verified"] = True
            except:
                pass
            
            # If we have a URL, try to get more details
            if data["url"]:
                try:
                    # Open the page in a new tab to get more details
                    original_window = self.driver.current_window_handle
                    self.driver.execute_script(f"window.open('{data['url']}', '_blank');")
                    time.sleep(3)
                    
                    windows = self.driver.window_handles
                    if len(windows) > 1:
                        self.driver.switch_to.window(windows[-1])
                        time.sleep(3)
                        
                        # Extract additional details
                        page_source = self.driver.page_source
                        
                        # Extract description
                        try:
                            desc_selectors = [
                                "div[data-testid='about']",
                                "div[class*='about']",
                                "div[data-pagelet='ProfileTilesFeed']"
                            ]
                            for selector in desc_selectors:
                                try:
                                    desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                                    desc_text = desc_elem.text.strip()
                                    if desc_text and len(desc_text) > 20 and len(desc_text) < 1000:
                                        data["description"] = desc_text[:500]
                                        break
                                except:
                                    continue
                        except:
                            pass
                        
                        # Extract location
                        try:
                            location_pattern = r'([A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}|[A-Za-z\s]+,\s*[A-Za-z\s]+)'
                            matches = re.findall(location_pattern, page_source)
                            if matches:
                                data["location"] = matches[0]
                        except:
                            pass
                        
                        # Extract phone
                        try:
                            phone_pattern = r'[\+]?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
                            matches = re.findall(phone_pattern, page_source)
                            if matches:
                                phone = f"({matches[0][0]}) {matches[0][1]}-{matches[0][2]}"
                                data["phone"] = phone
                        except:
                            pass
                        
                        # Extract email
                        try:
                            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                            matches = re.findall(email_pattern, page_source)
                            if matches:
                                # Filter out generic emails
                                valid_emails = [e for e in matches if not any(x in e.lower() for x in ['example.com', 'test.com', 'facebook.com'])]
                                if valid_emails:
                                    data["email"] = valid_emails[0]
                        except:
                            pass
                        
                        # Extract website
                        try:
                            website_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='http']")
                            for link in website_links:
                                href = link.get_attribute("href")
                                if href and "facebook.com" not in href.lower():
                                    data["website"] = href
                                    break
                        except:
                            pass
                        
                        # Close tab and return
                        self.driver.close()
                        self.driver.switch_to.window(original_window)
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"    Error extracting details from page: {str(e)}")
                    try:
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            windows = self.driver.window_handles
                            if windows:
                                self.driver.switch_to.window(windows[0])
                    except:
                        pass
            
            return data if data.get("name") else None
            
        except Exception as e:
            print(f"    Error extracting Facebook page data: {str(e)}")
            return None
    
    def search_instagram(self, search_query: str, max_results: int = 10) -> List[Dict[str, Optional[str]]]:
        """
        Search Instagram for profiles and extract data.
        
        Args:
            search_query: Name to search for
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            List of dictionaries containing Instagram profile data
        """
        results = []
        try:
            print(f"Searching Instagram for: {search_query}")
            
            # Navigate to Instagram search
            search_url = f"https://www.instagram.com/explore/tags/{search_query.replace(' ', '')}/"
            # Try direct profile search first
            self.driver.get("https://www.instagram.com")
            time.sleep(5)
            
            # Handle login prompt
            try:
                # Try to find search box without logging in
                search_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search'], input[aria-label*='Search']"))
                )
                search_input.click()
                time.sleep(1)
                search_input.send_keys(search_query)
                time.sleep(3)
            except:
                # If search doesn't work, try direct URL approach
                profile_url = f"https://www.instagram.com/{search_query.replace(' ', '').replace('@', '')}/"
                self.driver.get(profile_url)
                time.sleep(5)
                
                # Try to extract data from profile page
                profile_data = self._extract_instagram_profile_data()
                if profile_data:
                    results.append(profile_data)
                    return results
            
            # Find search results
            result_selectors = [
                "div[role='dialog'] a[href*='/']",
                "div[class*='_aagv'] a",
                "a[href*='/']"
            ]
            
            result_items = []
            for selector in result_selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    # Filter to only profile links
                    profile_items = [item for item in items if '/explore/' not in item.get_attribute('href') and '/p/' not in item.get_attribute('href')]
                    if len(profile_items) > 0:
                        result_items = profile_items[:max_results]
                        break
                except:
                    continue
            
            print(f"Found {len(result_items)} potential results")
            
            # Extract data from each result
            for idx, item in enumerate(result_items, 1):
                try:
                    print(f"Processing Instagram result {idx}/{len(result_items)}...")
                    
                    href = item.get_attribute("href")
                    if not href or '/explore/' in href or '/p/' in href:
                        continue
                    
                    # Visit profile
                    self.driver.get(href)
                    time.sleep(4)
                    
                    # Extract data
                    profile_data = self._extract_instagram_profile_data()
                    if profile_data:
                        profile_data["url"] = href
                        results.append(profile_data)
                        print(f"  ✓ Extracted: {profile_data.get('username', 'Unknown')}")
                    
                    # Go back to search
                    self.driver.back()
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"  ⊗ Error processing result {idx}: {str(e)}")
                    continue
            
            print(f"\n✓ Extracted {len(results)} Instagram results")
            
        except Exception as e:
            print(f"Error searching Instagram: {str(e)}")
        
        return results
    
    def _extract_instagram_profile_data(self) -> Optional[Dict[str, Optional[str]]]:
        """Extract data from current Instagram profile page."""
        try:
            data = {
                "username": None,
                "full_name": None,
                "url": None,
                "followers": None,
                "following": None,
                "posts": None,
                "bio": None,
                "website": None,
                "verified": False,
                "is_business": False
            }
            
            page_source = self.driver.page_source
            
            # Extract username from URL
            current_url = self.driver.current_url
            if "/" in current_url:
                username = current_url.split("/")[-2] if current_url.endswith("/") else current_url.split("/")[-1]
                if username and username != "explore" and username != "accounts":
                    data["username"] = username
                    data["url"] = current_url
            
            # Extract full name
            try:
                name_selectors = [
                    "h2[class*='_aacl']",
                    "h1",
                    "span[class*='_aacl']"
                ]
                for selector in name_selectors:
                    try:
                        name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        name_text = name_elem.text.strip()
                        if name_text and len(name_text) < 200:
                            data["full_name"] = name_text
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract followers, following, posts from page source
            try:
                # Followers
                follower_patterns = [
                    r'"edge_followed_by":\{"count":(\d+)\}',
                    r'"follower_count":(\d+)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:followers)'
                ]
                for pattern in follower_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        if isinstance(count, str):
                            if 'K' in count.upper():
                                num = float(count.replace('K', '').replace(',', '')) * 1000
                                data["followers"] = str(int(num))
                            elif 'M' in count.upper():
                                num = float(count.replace('M', '').replace(',', '')) * 1000000
                                data["followers"] = str(int(num))
                            elif 'B' in count.upper():
                                num = float(count.replace('B', '').replace(',', '')) * 1000000000
                                data["followers"] = str(int(num))
                            else:
                                data["followers"] = count.replace(',', '')
                        else:
                            data["followers"] = str(count)
                        break
            except:
                pass
            
            try:
                # Following
                following_patterns = [
                    r'"edge_follow":\{"count":(\d+)\}',
                    r'"following_count":(\d+)'
                ]
                for pattern in following_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        data["following"] = str(count) if isinstance(count, (int, str)) else str(count)
                        break
            except:
                pass
            
            try:
                # Posts
                post_patterns = [
                    r'"edge_owner_to_timeline_media":\{"count":(\d+)\}',
                    r'"media_count":(\d+)'
                ]
                for pattern in post_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        data["posts"] = str(count) if isinstance(count, (int, str)) else str(count)
                        break
            except:
                pass
            
            # Extract bio
            try:
                bio_selectors = [
                    "div[class*='-vDIg']",
                    "span[class*='-vDIg']",
                    "div[data-testid='user-bio']",
                    "h1 + div span"
                ]
                for selector in bio_selectors:
                    try:
                        bio_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        bio_text = bio_elem.text.strip()
                        if bio_text and len(bio_text) > 5 and len(bio_text) < 500:
                            data["bio"] = bio_text
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract website
            try:
                website_elem = self.driver.find_element(By.CSS_SELECTOR, "a[href^='http']")
                href = website_elem.get_attribute("href")
                if href and "instagram.com" not in href.lower():
                    data["website"] = href
            except:
                pass
            
            # Check if verified
            try:
                verified_icon = self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='Verified'], [aria-label*='verified']")
                data["verified"] = True
            except:
                pass
            
            # Check if business account
            try:
                if "business" in page_source.lower() or "contact" in page_source.lower():
                    data["is_business"] = True
            except:
                pass
            
            return data if data.get("username") or data.get("full_name") else None
            
        except Exception as e:
            print(f"    Error extracting Instagram profile data: {str(e)}")
            return None
    
    def close(self):
        """Close the browser driver."""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def search_facebook_pages(search_query: str, max_results: int = 10, headless: bool = False) -> List[Dict[str, Optional[str]]]:
    """
    Convenience function to search Facebook pages.
    
    Args:
        search_query: Name to search for
        max_results: Maximum number of results (default: 10)
        headless: Run browser in headless mode (default: False)
        
    Returns:
        List of dictionaries containing Facebook page data
    """
    with SocialMediaSearchScraper(headless=headless) as scraper:
        return scraper.search_facebook(search_query, max_results)


def search_instagram_profiles(search_query: str, max_results: int = 10, headless: bool = False) -> List[Dict[str, Optional[str]]]:
    """
    Convenience function to search Instagram profiles.
    
    Args:
        search_query: Name to search for
        max_results: Maximum number of results (default: 10)
        headless: Run browser in headless mode (default: False)
        
    Returns:
        List of dictionaries containing Instagram profile data
    """
    with SocialMediaSearchScraper(headless=headless) as scraper:
        return scraper.search_instagram(search_query, max_results)


def export_social_media_to_excel(results: List[Dict[str, Optional[str]]], filename: str = "social_media_results.xlsx", output_folder: str = "excel_results", platform: str = "facebook"):
    """
    Export social media search results to an Excel file.
    
    Args:
        results: List of dictionaries containing social media data
        filename: Output Excel filename (default: social_media_results.xlsx)
        output_folder: Folder name to store Excel files (default: excel_results)
        platform: Platform name (facebook or instagram) for headers
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise ImportError("openpyxl is required for Excel export. Install it with: pip install openpyxl")
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")
    
    # Join folder path with filename
    filepath = os.path.join(output_folder, filename)
    
    # Create workbook and worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{platform.capitalize()} Results"
    
    # Define headers based on platform
    if platform.lower() == "facebook":
        headers = ["Name", "URL", "Followers", "Likes", "Category", "Description", 
                   "Location", "Phone", "Email", "Website", "Verified"]
    else:  # instagram
        headers = ["Username", "Full Name", "URL", "Followers", "Following", "Posts", 
                   "Bio", "Website", "Verified", "Is Business"]
    
    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Write data
    for row_num, result in enumerate(results, 2):
        if platform.lower() == "facebook":
            ws.cell(row=row_num, column=1, value=result.get('name', ''))
            ws.cell(row=row_num, column=2, value=result.get('url', ''))
            ws.cell(row=row_num, column=3, value=result.get('followers', ''))
            ws.cell(row=row_num, column=4, value=result.get('likes', ''))
            ws.cell(row=row_num, column=5, value=result.get('category', ''))
            ws.cell(row=row_num, column=6, value=result.get('description', ''))
            ws.cell(row=row_num, column=7, value=result.get('location', ''))
            ws.cell(row=row_num, column=8, value=result.get('phone', ''))
            ws.cell(row=row_num, column=9, value=result.get('email', ''))
            ws.cell(row=row_num, column=10, value=result.get('website', ''))
            ws.cell(row=row_num, column=11, value="Yes" if result.get('verified') else "No")
        else:  # instagram
            ws.cell(row=row_num, column=1, value=result.get('username', ''))
            ws.cell(row=row_num, column=2, value=result.get('full_name', ''))
            ws.cell(row=row_num, column=3, value=result.get('url', ''))
            ws.cell(row=row_num, column=4, value=result.get('followers', ''))
            ws.cell(row=row_num, column=5, value=result.get('following', ''))
            ws.cell(row=row_num, column=6, value=result.get('posts', ''))
            ws.cell(row=row_num, column=7, value=result.get('bio', ''))
            ws.cell(row=row_num, column=8, value=result.get('website', ''))
            ws.cell(row=row_num, column=9, value="Yes" if result.get('verified') else "No")
            ws.cell(row=row_num, column=10, value="Yes" if result.get('is_business') else "No")
    
    # Auto-adjust column widths
    for col_num, header in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        max_length = len(header)
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col_num, max_col=col_num):
            if row[0].value:
                max_length = max(max_length, len(str(row[0].value)))
        ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
    
    # Save workbook
    wb.save(filepath)
    print(f"\nResults exported to {filepath}")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python social_media_search_scraper.py <platform> <search_query> [max_results]")
        print("Platform: facebook or instagram")
        print("Example: python social_media_search_scraper.py facebook 'Starbucks' 10")
        sys.exit(1)
    
    platform = sys.argv[1].lower()
    search_query = sys.argv[2]
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    scraper = SocialMediaSearchScraper(headless=False)
    
    try:
        if platform == "facebook":
            results = scraper.search_facebook(search_query, max_results)
        elif platform == "instagram":
            results = scraper.search_instagram(search_query, max_results)
        else:
            print(f"Unknown platform: {platform}. Use 'facebook' or 'instagram'")
            sys.exit(1)
        
        print(f"\n{'='*60}")
        print(f"Found {len(results)} results")
        print(f"{'='*60}\n")
        
        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            for key, value in result.items():
                if value:
                    print(f"  {key}: {value}")
            print()
        
        # Export to Excel
        safe_query = "".join(c for c in search_query if c.isalnum() or c in (' ', '-', '_')).strip()
        excel_filename = f"{platform}_{safe_query}_results.xlsx"
        export_social_media_to_excel(results, excel_filename, "excel_results", platform)
            
    finally:
        scraper.close()

