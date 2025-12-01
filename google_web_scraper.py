"""
Google Web Search Scraper for Lead Generation
Searches Google (not just Maps) to find businesses across the web and extract information.
"""

import time
import re
import os
import urllib.parse
from typing import Dict, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


class GoogleWebScraper:
    """Scraper for extracting business information from Google web search results."""
    
    def __init__(self, headless: bool = False, wait_time: int = 10):
        """
        Initialize the Google web scraper.
        
        Args:
            headless: Run browser in headless mode (default: False)
            wait_time: Maximum wait time for elements to load (default: 10 seconds)
        """
        self.wait_time = wait_time
        self.driver = None
        self.setup_driver(headless)
    
    def setup_driver(self, headless: bool):
        """Setup Chrome WebDriver with appropriate options for production."""
        chrome_options = Options()
        
        # Production-ready Chrome options for EC2/server environment
        # Always use headless mode on server (EC2 doesn't have display)
        chrome_options.add_argument('--headless=new')  # Use new headless mode
        chrome_options.add_argument('--no-sandbox')  # Required for Docker/EC2
        chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        chrome_options.add_argument('--disable-gpu')  # Required for headless
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        
        # Anti-detection options
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use Linux user-agent for server environment
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            raise Exception(f"Failed to initialize Chrome driver. Make sure ChromeDriver is installed. Error: {str(e)}")
    
    def search_google(self, query: str, max_results: Optional[int] = None, max_pages: int = 8) -> List[Dict[str, Optional[str]]]:
        """
        Search Google for businesses and extract information.
        
        Args:
            query: Search query (e.g., "veterinary doctors in Lahore")
            max_results: Maximum number of results to extract (None = no limit, extract all)
            max_pages: Maximum number of Google search pages to search (default: 8)
        
        Returns:
            List of dictionaries containing business information
        """
        try:
            # Navigate to Google
            self.driver.get("https://www.google.com")
            time.sleep(2)
            
            # Accept cookies if present
            try:
                accept_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'I agree')]"))
                )
                accept_button.click()
                time.sleep(1)
            except:
                pass
            
            # Find search box and enter query
            try:
                search_box = WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                time.sleep(3)
            except TimeoutException:
                raise Exception("Could not find Google search box")
            
            # Extract search results from all pages
            results = []
            page_num = 1
            
            while page_num <= max_pages:
                print(f"Extracting results from page {page_num}...")
                
                # Wait for results to load
                time.sleep(2)
                
                # Extract organic search results
                page_results = self._extract_search_results()
                
                if page_results:
                    results.extend(page_results)
                    print(f"Found {len(page_results)} results on page {page_num}. Total: {len(results)}")
                else:
                    print(f"No results found on page {page_num}.")
                
                # Try to go to next page
                if page_num < max_pages:
                    if not self._go_to_next_page():
                        print("No more pages available. Stopping.")
                        break
                    page_num += 1
                else:
                    print(f"Reached maximum pages ({max_pages}). Stopping.")
                    break
            
            # Only limit if max_results is specified and less than total results
            if max_results and len(results) > max_results:
                print(f"Limiting results to {max_results} (found {len(results)} total)")
                results = results[:max_results]
            
            # Extract detailed information from each result
            print(f"\nExtracting detailed information from {len(results)} results...")
            detailed_results = []
            
            for idx, result in enumerate(results, 1):
                try:
                    title = result.get('title', result.get('name', 'N/A'))
                    print(f"Processing result {idx}/{len(results)}: {title}")
                    
                    # Try to extract detailed info from website
                    detailed_info = self._extract_website_info(result)
                    
                    # Always add result - prefer detailed info if available, otherwise use original
                    if detailed_info and (detailed_info.get('phone') or detailed_info.get('email') or detailed_info.get('address')):
                        # Use detailed info if it has additional data
                        detailed_results.append(detailed_info)
                    else:
                        # Use original result (might have snippet data from Google)
                        detailed_results.append(result)
                    
                    time.sleep(1)  # Be respectful with delays
                except Exception as e:
                    print(f"Error processing result {idx}: {str(e)}")
                    # Always add result, even if there was an error
                    detailed_results.append(result)
                    continue
            
            print(f"Total results after processing: {len(detailed_results)}")
            return detailed_results if detailed_results else results
            
        except Exception as e:
            print(f"Error searching Google: {str(e)}")
            return []
    
    def _extract_search_results(self) -> List[Dict[str, Optional[str]]]:
        """Extract basic information from Google search results page."""
        results = []
        try:
            # Wait a bit for page to load
            time.sleep(1)
            
            # Find all search result containers - try multiple selectors
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g, div[data-ved], div[class*='g '], div.tF2Cxc")
            
            # If no results with first selector, try alternative
            if not result_elements:
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-sokoban-container] > div, div[jscontroller]")
            
            for element in result_elements:
                try:
                    result_info = {
                        "title": None,
                        "url": None,
                        "snippet": None,
                        "name": None,
                        "address": None,
                        "phone": None,
                        "email": None,
                        "website": None,
                        "category": None,
                        "rating": None,
                        "reviews_count": None,
                        "lead_score": 0,
                        "lead_status": "New",
                        "lead_source": "Google Search"
                    }
                    
                    # Extract title
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, "h3, a h3")
                        result_info["title"] = title_elem.text.strip()
                        result_info["name"] = result_info["title"]  # Use title as name initially
                    except:
                        pass
                    
                    # Extract URL
                    try:
                        link_elem = element.find_element(By.CSS_SELECTOR, "a[href^='http']")
                        url = link_elem.get_attribute("href")
                        if url and not url.startswith("https://www.google.com"):
                            result_info["url"] = url
                            result_info["website"] = url
                    except:
                        pass
                    
                    # Extract snippet/description
                    try:
                        snippet_elem = element.find_element(By.CSS_SELECTOR, "span[style*='-webkit-line-clamp'], .VwiC3b, .s")
                        result_info["snippet"] = snippet_elem.text.strip()
                    except:
                        pass
                    
                    # Try to extract phone and address from snippet
                    if result_info["snippet"]:
                        # Extract phone
                        phone_match = re.search(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', result_info["snippet"])
                        if phone_match:
                            result_info["phone"] = phone_match.group()
                        
                        # Extract email
                        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', result_info["snippet"])
                        if email_match:
                            result_info["email"] = email_match.group()
                        
                        # Try to extract address patterns
                        address_patterns = [
                            r'(\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl)[\s,]*[A-Za-z\s,]+)',
                            r'([A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5})',
                            r'([A-Za-z\s]+,\s*Lahore[,\s]*Pakistan)'
                        ]
                        for pattern in address_patterns:
                            addr_match = re.search(pattern, result_info["snippet"])
                            if addr_match:
                                result_info["address"] = addr_match.group(1).strip()
                                break
                    
                    # Extract rating if present (from Google knowledge panel or snippets)
                    try:
                        rating_elem = element.find_element(By.CSS_SELECTOR, "[aria-label*='stars'], [aria-label*='rating']")
                        rating_text = rating_elem.get_attribute("aria-label")
                        rating_match = re.search(r'(\d+\.?\d*)\s*(?:stars?|rating)', rating_text, re.IGNORECASE)
                        if rating_match:
                            result_info["rating"] = rating_match.group(1)
                    except:
                        pass
                    
                    if result_info["url"] or result_info["title"]:
                        results.append(result_info)
                        
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"Error extracting search results: {str(e)}")
        
        return results
    
    def _go_to_next_page(self) -> bool:
        """Navigate to the next page of search results."""
        try:
            # Scroll to bottom to ensure next button is visible
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Look for "Next" button with multiple selectors
            next_selectors = [
                "a[aria-label='Next']",
                "a#pnnext",
                "a[aria-label*='Next']",
                "a[id='pnnext']",
                "td[style*='text-align:left'] a[aria-label='Next']"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button and next_button.is_displayed():
                        # Scroll to button
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(0.5)
                        next_button.click()
                        time.sleep(3)  # Wait for page to load
                        return True
                except:
                    continue
            
            # Alternative: try clicking on page number
            try:
                # Get current page number and try to click next number
                current_url = self.driver.current_url
                if 'start=' in current_url:
                    # Extract current start value
                    import re
                    match = re.search(r'start=(\d+)', current_url)
                    if match:
                        current_start = int(match.group(1))
                        next_start = current_start + 10
                        # Modify URL directly
                        new_url = re.sub(r'start=\d+', f'start={next_start}', current_url)
                        self.driver.get(new_url)
                        time.sleep(3)
                        return True
            except:
                pass
                
        except Exception as e:
            print(f"Error navigating to next page: {str(e)}")
        return False
    
    def _extract_website_info(self, result: Dict[str, Optional[str]]) -> Optional[Dict[str, Optional[str]]]:
        """Extract detailed information from a website."""
        if not result.get("url"):
            return result
        
        url = result["url"]
        
        try:
            # Navigate to the website
            self.driver.get(url)
            time.sleep(3)
            
            page_source = self.driver.page_source
            
            # Extract phone number
            if not result.get("phone"):
                phone_patterns = [
                    r'[\+]?92[\s\-]?[0-9]{2}[\s\-]?[0-9]{7,8}',  # Pakistan format
                    r'[\+]?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',  # US format
                    r'tel:[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}',
                    r'phone[:\s]+([\d\s\-\(\)\+]{10,15})',
                    r'call[:\s]+([\d\s\-\(\)\+]{10,15})'
                ]
                for pattern in phone_patterns:
                    phone_matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if phone_matches:
                        phone = phone_matches[0] if isinstance(phone_matches[0], str) else ''.join(phone_matches[0])
                        # Clean up phone number
                        phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone).strip()
                        # Validate phone length (10-15 digits is reasonable)
                        digits_only = re.sub(r'[^\d]', '', phone)
                        if 10 <= len(digits_only) <= 15 and not digits_only.startswith('000'):
                            result["phone"] = phone
                            break
            
            # Extract email
            if not result.get("email"):
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                email_matches = re.findall(email_pattern, page_source)
                # Filter out common non-business emails and tracking services
                filtered_emails = [e for e in email_matches if not any(x in e.lower() for x in [
                    'google', 'gmail', 'example', 'test', 'noreply', 'no-reply', 
                    'facebook', 'twitter', 'sentry', 'analytics', 'tracking',
                    'pixel', 'beacon', 'doubleclick', 'googletagmanager'
                ])]
                # Prefer emails with business-like domains
                business_emails = [e for e in filtered_emails if '.' in e.split('@')[1] and len(e.split('@')[1].split('.')[0]) > 2]
                if business_emails:
                    result["email"] = business_emails[0]
                elif filtered_emails:
                    result["email"] = filtered_emails[0]
            
            # Extract address
            if not result.get("address"):
                address_selectors = [
                    "[itemprop='address']",
                    "[class*='address']",
                    "[id*='address']",
                    "[class*='location']",
                    "[id*='location']"
                ]
                
                for selector in address_selectors:
                    try:
                        addr_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        addr_text = addr_elem.text.strip()
                        if addr_text and len(addr_text) > 10:
                            result["address"] = addr_text
                            break
                    except:
                        continue
                
                # Fallback: regex search
                if not result.get("address"):
                    address_patterns = [
                        r'(\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl)[\s,]*[A-Za-z\s,]+)',
                        r'([A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5})',
                        r'([A-Za-z\s]+,\s*Lahore[,\s]*Pakistan)',
                        r'address[:\s]+([A-Za-z0-9\s,]+)'
                    ]
                    for pattern in address_patterns:
                        addr_matches = re.findall(pattern, page_source, re.IGNORECASE)
                        if addr_matches:
                            result["address"] = addr_matches[0].strip()
                            break
            
            # Extract business name (if not already set)
            if not result.get("name") or result.get("name") == result.get("title"):
                name_selectors = [
                    "h1",
                    "[class*='business-name']",
                    "[class*='company-name']",
                    "[itemprop='name']",
                    "title"
                ]
                
                for selector in name_selectors:
                    try:
                        name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        name_text = name_elem.text.strip()
                        if name_text and len(name_text) < 100:
                            result["name"] = name_text
                            break
                    except:
                        continue
            
            # Extract category/business type
            if not result.get("category"):
                category_selectors = [
                    "[itemprop='category']",
                    "[class*='category']",
                    "[class*='business-type']"
                ]
                
                for selector in category_selectors:
                    try:
                        cat_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        result["category"] = cat_elem.text.strip()
                        break
                    except:
                        continue
            
            # Extract social media links
            try:
                social_links = self._extract_social_media_links(page_source)
                result.update(social_links)
                
                # Create combined social media links string
                social_list = []
                if result.get("facebook"):
                    social_list.append(f"Facebook: {result['facebook']}")
                if result.get("instagram"):
                    social_list.append(f"Instagram: {result['instagram']}")
                if result.get("linkedin"):
                    social_list.append(f"LinkedIn: {result['linkedin']}")
                if result.get("twitter"):
                    social_list.append(f"Twitter: {result['twitter']}")
                if result.get("youtube"):
                    social_list.append(f"YouTube: {result['youtube']}")
                if result.get("tiktok"):
                    social_list.append(f"TikTok: {result['tiktok']}")
                
                if social_list:
                    result["social_media_links"] = " | ".join(social_list)
                    
            except Exception as e:
                print(f"Error extracting social media links: {str(e)}")
            
            # Calculate lead score
            lead_score = 0
            if result.get("name"):
                lead_score += 10
            if result.get("address"):
                lead_score += 15
            if result.get("phone"):
                lead_score += 20
            if result.get("email"):
                lead_score += 25
            if result.get("website") or result.get("url"):
                lead_score += 15
            if result.get("rating"):
                lead_score += 10
            if result.get("category"):
                lead_score += 5
            
            # Social media presence adds value
            social_count = sum(1 for key in ["facebook", "instagram", "linkedin", "twitter", "youtube", "tiktok"] if result.get(key))
            if social_count > 0:
                lead_score += min(social_count * 2, 10)  # Max 10 points for social media
            
            result["lead_score"] = min(lead_score, 100)
            
            # Determine lead status
            if lead_score >= 70:
                result["lead_status"] = "Hot"
            elif lead_score >= 50:
                result["lead_status"] = "Warm"
            elif lead_score >= 30:
                result["lead_status"] = "Cold"
            else:
                result["lead_status"] = "New"
            
        except Exception as e:
            print(f"Error extracting info from {url}: {str(e)}")
        
        return result
    
    def close(self):
        """Close the browser driver."""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
    
    def _extract_social_media_links(self, page_source: str) -> Dict[str, Optional[str]]:
        """
        Extract social media links from page source and visible links.
        
        Args:
            page_source: HTML page source to search
            
        Returns:
            Dictionary with social media links (facebook, instagram, linkedin, twitter, youtube, tiktok)
        """
        social_links = {
            "facebook": None,
            "instagram": None,
            "linkedin": None,
            "twitter": None,
            "youtube": None,
            "tiktok": None
        }
        
        try:
            # Find all links on the page
            all_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
            
            # Patterns for social media URLs
            patterns = {
                "facebook": [
                    r'https?://(?:www\.)?(?:facebook\.com|fb\.com)/[^\s<>"{}|\\^`\[\]]+',
                    r'https?://(?:www\.)?facebook\.com/[^\s<>"{}|\\^`\[\]]+',
                    r'fb\.com/[^\s<>"{}|\\^`\[\]]+'
                ],
                "instagram": [
                    r'https?://(?:www\.)?instagram\.com/[^\s<>"{}|\\^`\[\]]+',
                    r'instagram\.com/[^\s<>"{}|\\^`\[\]]+'
                ],
                "linkedin": [
                    r'https?://(?:www\.)?linkedin\.com/[^\s<>"{}|\\^`\[\]]+',
                    r'linkedin\.com/[^\s<>"{}|\\^`\[\]]+'
                ],
                "twitter": [
                    r'https?://(?:www\.)?(?:twitter\.com|x\.com)/[^\s<>"{}|\\^`\[\]]+',
                    r'twitter\.com/[^\s<>"{}|\\^`\[\]]+',
                    r'x\.com/[^\s<>"{}|\\^`\[\]]+'
                ],
                "youtube": [
                    r'https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s<>"{}|\\^`\[\]]+',
                    r'youtube\.com/[^\s<>"{}|\\^`\[\]]+',
                    r'youtu\.be/[^\s<>"{}|\\^`\[\]]+'
                ],
                "tiktok": [
                    r'https?://(?:www\.)?tiktok\.com/[^\s<>"{}|\\^`\[\]]+',
                    r'tiktok\.com/[^\s<>"{}|\\^`\[\]]+'
                ]
            }
            
            # Extract from visible links
            for link in all_links:
                try:
                    href = link.get_attribute("href")
                    if not href:
                        continue
                    
                    href_lower = href.lower()
                    
                    # Check each social media platform
                    for platform, platform_patterns in patterns.items():
                        if not social_links[platform]:  # Only get first match
                            for pattern in platform_patterns:
                                match = re.search(pattern, href_lower, re.IGNORECASE)
                                if match:
                                    # Clean up the URL
                                    url = match.group(0)
                                    # Remove query parameters and fragments for cleaner URLs
                                    url = url.split('?')[0].split('#')[0]
                                    # Ensure it starts with http
                                    if not url.startswith('http'):
                                        url = 'https://' + url
                                    social_links[platform] = url
                                    break
                except Exception:
                    continue
            
            # Also search in page source for any missed links
            for platform, platform_patterns in patterns.items():
                if not social_links[platform]:  # Only if not found in visible links
                    for pattern in platform_patterns:
                        matches = re.findall(pattern, page_source, re.IGNORECASE)
                        if matches:
                            url = matches[0]
                            # Clean up the URL
                            url = url.split('?')[0].split('#')[0]
                            if not url.startswith('http'):
                                url = 'https://' + url
                            social_links[platform] = url
                            break
            
        except Exception as e:
            print(f"Error in _extract_social_media_links: {str(e)}")
        
        return social_links


def export_leads_to_csv(results: List[Dict[str, Optional[str]]], filename: str = "google_search_leads.csv", output_folder: str = "excel_results"):
    """Export leads to CSV format for CRM import."""
    import csv
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    filepath = os.path.join(output_folder, filename)
    
    fieldnames = [
        "Company Name", "Title", "Address", "Phone", "Email", "Website",
        "Category", "Rating", "Reviews Count", "Snippet",
        "Facebook", "Instagram", "LinkedIn", "Twitter", "YouTube", "TikTok", "Social Media Links",
        "Lead Score", "Lead Status", "Lead Source", "URL"
    ]
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                "Company Name": result.get('name', ''),
                "Title": result.get('title', ''),
                "Address": result.get('address', ''),
                "Phone": result.get('phone', ''),
                "Email": result.get('email', ''),
                "Website": result.get('website', result.get('url', '')),
                "Category": result.get('category', ''),
                "Rating": result.get('rating', ''),
                "Reviews Count": result.get('reviews_count', ''),
                "Snippet": result.get('snippet', ''),
                "Facebook": result.get('facebook', ''),
                "Instagram": result.get('instagram', ''),
                "LinkedIn": result.get('linkedin', ''),
                "Twitter": result.get('twitter', ''),
                "YouTube": result.get('youtube', ''),
                "TikTok": result.get('tiktok', ''),
                "Social Media Links": result.get('social_media_links', ''),
                "Lead Score": result.get('lead_score', 0),
                "Lead Status": result.get('lead_status', 'New'),
                "Lead Source": result.get('lead_source', 'Google Search'),
                "URL": result.get('url', '')
            })
    
    print(f"Leads exported to CSV: {filepath}")


def export_to_excel(results: List[Dict[str, Optional[str]]], filename: str = "google_search_results.xlsx", output_folder: str = "excel_results"):
    """Export results to Excel file."""
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise ImportError("openpyxl is required for Excel export. Install it with: pip install openpyxl")
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    filepath = os.path.join(output_folder, filename)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Google Search Results"
    
    headers = [
        "Name", "Title", "Address", "Phone", "Email", "Website", "Category",
        "Rating", "Reviews Count", "Snippet",
        "Facebook", "Instagram", "LinkedIn", "Twitter", "YouTube", "TikTok", "Social Media Links",
        "Lead Score", "Lead Status", "Lead Source", "URL"
    ]
    
    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Write data
    for row_num, result in enumerate(results, 2):
        ws.cell(row=row_num, column=1, value=result.get('name', ''))
        ws.cell(row=row_num, column=2, value=result.get('title', ''))
        ws.cell(row=row_num, column=3, value=result.get('address', ''))
        ws.cell(row=row_num, column=4, value=result.get('phone', ''))
        ws.cell(row=row_num, column=5, value=result.get('email', ''))
        ws.cell(row=row_num, column=6, value=result.get('website', result.get('url', '')))
        ws.cell(row=row_num, column=7, value=result.get('category', ''))
        ws.cell(row=row_num, column=8, value=result.get('rating', ''))
        ws.cell(row=row_num, column=9, value=result.get('reviews_count', ''))
        ws.cell(row=row_num, column=10, value=result.get('snippet', ''))
        ws.cell(row=row_num, column=11, value=result.get('facebook', ''))
        ws.cell(row=row_num, column=12, value=result.get('instagram', ''))
        ws.cell(row=row_num, column=13, value=result.get('linkedin', ''))
        ws.cell(row=row_num, column=14, value=result.get('twitter', ''))
        ws.cell(row=row_num, column=15, value=result.get('youtube', ''))
        ws.cell(row=row_num, column=16, value=result.get('tiktok', ''))
        ws.cell(row=row_num, column=17, value=result.get('social_media_links', ''))
        ws.cell(row=row_num, column=18, value=result.get('lead_score', 0))
        ws.cell(row=row_num, column=19, value=result.get('lead_status', 'New'))
        ws.cell(row=row_num, column=20, value=result.get('lead_source', 'Google Search'))
        ws.cell(row=row_num, column=21, value=result.get('url', ''))
    
    # Auto-adjust column widths
    for col_num, header in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        max_length = len(header)
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col_num, max_col=col_num):
            if row[0].value:
                max_length = max(max_length, len(str(row[0].value)))
        ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
    
    try:
        wb.save(filepath)
        print(f"Results exported to Excel: {filepath}")
    except PermissionError:
        print(f"ERROR: Cannot save Excel file. The file may be open in another program.")
        print(f"Please close the file: {filepath}")
        print("Results will still be exported to CSV.")
        raise


def search_businesses_web(query: str, max_results: Optional[int] = None, max_pages: int = 8, headless: bool = False, export_excel: bool = True, export_csv: bool = True, output_folder: str = "excel_results") -> List[Dict[str, Optional[str]]]:
    """
    Search for businesses on Google web search and extract information.
    
    Args:
        query: Search query (e.g., "veterinary doctors in Lahore")
        max_results: Maximum number of results to extract (None = no limit, extract all from all pages)
        max_pages: Maximum number of Google search pages to search (default: 8)
        headless: Run browser in headless mode
        export_excel: Export to Excel file
        export_csv: Export to CSV file
        output_folder: Output folder for files
    
    Returns:
        List of business information dictionaries
    """
    with GoogleWebScraper(headless=headless) as scraper:
        results = scraper.search_google(query, max_results, max_pages)
        
        # Remove duplicates based on URL (but keep all results)
        seen_urls = set()
        seen_names = set()
        unique_results = []
        duplicates_removed = 0
        
        for result in results:
            url = result.get('url', '') or result.get('website', '')
            name = result.get('name', '') or result.get('title', '')
            
            # Check by URL first (most reliable)
            if url:
                # Normalize URL (remove query parameters for comparison)
                normalized_url = url.split('?')[0].split('#')[0].rstrip('/')
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    unique_results.append(result)
                else:
                    duplicates_removed += 1
            # If no URL, check by name
            elif name:
                normalized_name = name.strip().lower()
                if normalized_name not in seen_names:
                    seen_names.add(normalized_name)
                    unique_results.append(result)
                else:
                    duplicates_removed += 1
            else:
                # If no URL and no name, still include it (might have other useful info)
                unique_results.append(result)
        
        if duplicates_removed > 0:
            print(f"Removed {duplicates_removed} duplicate results. Keeping {len(unique_results)} unique results.")
        
        results = unique_results
        
        if export_excel or export_csv:
            # Create safe filename from query
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            safe_query = safe_query.replace(' ', '_')
            
            if export_excel:
                excel_filename = f"{safe_query}_web_results.xlsx"
                export_to_excel(results, excel_filename, output_folder)
            
            if export_csv:
                csv_filename = f"{safe_query}_web_leads.csv"
                export_leads_to_csv(results, csv_filename, output_folder)
        
        return results


if __name__ == "__main__":
    import sys
    import io
    
    # Fix Windows console encoding issues
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python google_web_scraper.py <search_query> [max_results] [max_pages]")
        print("Example: python google_web_scraper.py 'veterinary doctors in Lahore' 50 8")
        print("         python google_web_scraper.py 'medical stores in Lahore' 0 8  (0 = no limit, get all)")
        sys.exit(1)
    
    query = sys.argv[1]
    max_results_arg = sys.argv[2] if len(sys.argv) > 2 else "0"
    max_results = None if max_results_arg == "0" else int(max_results_arg)
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    
    print(f"Searching Google for: {query}")
    if max_results:
        print(f"Max results: {max_results}")
    else:
        print("Max results: UNLIMITED (all results from all pages)")
    print(f"Max pages: {max_pages}")
    print("-" * 50)
    
    results = search_businesses_web(query, max_results=max_results, max_pages=max_pages, headless=False, export_excel=True, export_csv=True)
    
    print(f"\nFound {len(results)} results\n")
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        name = result.get('name', result.get('title', 'N/A')) or 'N/A'
        address = result.get('address', 'N/A') or 'N/A'
        phone = result.get('phone', 'N/A') or 'N/A'
        email = result.get('email', 'N/A') or 'N/A'
        website = result.get('website', result.get('url', 'N/A')) or 'N/A'
        category = result.get('category', 'N/A') or 'N/A'
        rating = result.get('rating', 'N/A') or 'N/A'
        lead_score = result.get('lead_score', 0)
        lead_status = result.get('lead_status', 'N/A') or 'N/A'
        social_links = result.get('social_media_links', 'N/A') or 'N/A'
        
        print(f"  Name: {name}")
        print(f"  Address: {address}")
        print(f"  Phone: {phone}")
        print(f"  Email: {email}")
        print(f"  Website: {website}")
        print(f"  Category: {category}")
        print(f"  Rating: {rating}")
        if social_links != 'N/A':
            print(f"  Social Media: {social_links}")
        print(f"  Lead Score: {lead_score}/100")
        print(f"  Lead Status: {lead_status}")

