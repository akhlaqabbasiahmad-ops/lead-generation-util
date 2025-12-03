"""
Google Maps Scraper Utility
Scrapes business information (location, phone number, email) from Google Maps by business name.
"""

import time
import re
import os
from typing import Dict, Optional, List, Tuple
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


class GoogleMapsScraper:
    """Scraper for extracting business information from Google Maps."""
    
    def __init__(self, headless: bool = False, wait_time: int = 10):
        """
        Initialize the Google Maps scraper.
        
        Args:
            headless: Run browser in headless mode (default: False)
            wait_time: Maximum wait time for elements to load (default: 10 seconds)
        """
        self.wait_time = wait_time
        self.driver = None
        self.setup_driver(headless)
    
    def setup_driver(self, headless: bool):
        """Setup Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        
        # Basic options for all environments
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
        import platform
        is_windows = platform.system() == 'Windows'
        is_linux = platform.system() == 'Linux'
        
        if headless:
            # Headless mode options
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            if is_linux:
                # Linux-specific headless options
                chrome_options.add_argument('--disable-setuid-sandbox')
                chrome_options.add_argument('--remote-debugging-port=9222')
                chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            else:
                # Windows headless options (more minimal)
                chrome_options.add_argument('--disable-software-rasterizer')
        else:
            # Non-headless mode (Windows GUI)
            if is_windows:
                # Windows-specific options for GUI mode
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            elif is_linux:
                # Linux GUI mode (if X server available)
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                # Use webdriver-manager to automatically handle ChromeDriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Fallback: use system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
        except Exception as e:
            error_msg = str(e)
            # Provide more helpful error messages
            if "session not created" in error_msg.lower() or "unable to connect to renderer" in error_msg.lower():
                raise Exception(
                    f"Failed to initialize Chrome driver. This may be due to:\n"
                    f"1. Chrome browser not installed or outdated\n"
                    f"2. ChromeDriver version mismatch\n"
                    f"3. Chrome process already running\n"
                    f"4. Insufficient system resources\n\n"
                    f"Try:\n"
                    f"- Update Chrome browser to latest version\n"
                    f"- Close all Chrome windows and try again\n"
                    f"- Restart your computer\n"
                    f"- Check if Chrome is installed correctly\n\n"
                    f"Original error: {error_msg}"
                )
            else:
                raise Exception(f"Failed to initialize Chrome driver. Make sure ChromeDriver is installed. Error: {error_msg}")
    
    def search_business(self, business_name: str, location: Optional[str] = None) -> List[Dict[str, Optional[str]]]:
        """
        Search for a business on Google Maps and extract information.
        
        Args:
            business_name: Name of the business to search for
            location: Optional location to narrow down search (e.g., "New York, NY")
        
        Returns:
            List of dictionaries containing business information (name, address, phone, email)
        """
        try:
            # Construct search query
            if location:
                query = f"{business_name} {location}"
            else:
                query = business_name
            
            # Navigate to Google Maps
            self.driver.get("https://www.google.com/maps")
            time.sleep(2)
            
            # Find search box and enter query
            try:
                search_box = WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located((By.ID, "searchboxinput"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                time.sleep(3)
            except TimeoutException:
                raise Exception("Could not find Google Maps search box")
            
            # Wait for results to load
            time.sleep(4)
            
            # Extract ALL business information from sidebar results
            results = self._extract_all_sidebar_results()
            
            return results if results else [{"name": business_name, "address": None, "phone": None, "email": None, "rating": None, "reviews_count": None}]
            
        except Exception as e:
            print(f"Error searching for business: {str(e)}")
            return [{"name": business_name, "address": None, "phone": None, "email": None, "error": str(e)}]
    
    def _extract_business_info(self) -> Optional[Dict[str, Optional[str]]]:
        """Extract business information from the main business panel."""
        try:
            # Wait a bit for page to fully load
            time.sleep(3)
            
            info = {
                "name": None,
                "address": None,
                "phone": None,
                "email": None,
                "rating": None,
                "reviews_count": None,
                "website": None,
                "category": None,
                "business_hours": None,
                "facebook": None,
                "instagram": None,
                "linkedin": None,
                "twitter": None,
                "youtube": None,
                "tiktok": None,
                "social_media_links": None,  # Combined string of all social links
                "lead_score": 0,
                "lead_status": "New",
                "lead_source": "Google Maps"
            }
            
            # Extract business name - try multiple selectors
            name_selectors = [
                "h1[data-attrid='title']",
                "h1.DUwDvf",
                "h1.fontHeadlineLarge",
                "h1[class*='fontHeadline']",
                "h1",
                "[data-value='Directions']",
                "button[data-value='Directions']"
            ]
            
            for selector in name_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 0 and len(text) < 100:
                            # Check if it's likely a business name (not a button label)
                            if selector.startswith("h1") or (text not in ["Directions", "Save", "Share"]):
                                info["name"] = text
                                break
                    if info["name"]:
                        break
                except NoSuchElementException:
                    continue
            
            # Get page source for more comprehensive extraction
            page_source = self.driver.page_source
            
            # Extract address - try multiple methods
            try:
                address_selectors = [
                    "button[data-item-id='address']",
                    "[data-item-id='address']",
                    "button[aria-label*='Address']",
                    "[aria-label*='Address']",
                    "[data-value*='address']",
                    "div[class*='Io6YTe']",
                    "span[class*='Io6YTe']"
                ]
                
                for selector in address_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            address_text = element.text.strip()
                            # Clean up any special characters and validate it looks like an address
                            if address_text:
                                # Remove common Unicode artifacts
                                address_text = re.sub(r'[\ue000-\uf8ff]', '', address_text).strip()
                                if len(address_text) > 10 and any(char.isdigit() for char in address_text):
                                    info["address"] = address_text
                                    break
                        if info["address"]:
                            break
                    except NoSuchElementException:
                        continue
                
                # Fallback: search in page source with regex
                if not info["address"]:
                    # More flexible address pattern
                    address_patterns = [
                        r'(\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl)[\s,]*[A-Za-z\s,]+(?:[A-Z]{2})?\s+\d{5})',
                        r'(\d+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd)[\s,]*[A-Za-z\s,]+)',
                        r'([A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5})'
                    ]
                    for pattern in address_patterns:
                        matches = re.findall(pattern, page_source)
                        if matches:
                            info["address"] = matches[0].strip()
                            break
                        
            except Exception as e:
                print(f"Error extracting address: {str(e)}")
            
            # Extract phone number - try multiple methods
            try:
                phone_selectors = [
                    "button[data-item-id*='phone']",
                    "[data-item-id*='phone']",
                    "button[aria-label*='Phone']",
                    "[aria-label*='Phone']",
                    "[data-value*='phone']",
                    "span[class*='phone']",
                    "a[href^='tel:']"
                ]
                
                for selector in phone_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            phone_text = element.text.strip()
                            # Extract phone using regex
                            phone_match = re.search(r'[\+]?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', phone_text)
                            if phone_match:
                                info["phone"] = phone_match.group()
                                break
                            # Also check href for tel: links
                            if selector.startswith("a[href"):
                                href = element.get_attribute("href")
                                if href and href.startswith("tel:"):
                                    phone_match = re.search(r'[\+]?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', href)
                                    if phone_match:
                                        info["phone"] = phone_match.group()
                                        break
                        if info["phone"]:
                            break
                    except NoSuchElementException:
                        continue
                
                # Fallback: search in page source with better regex
                if not info["phone"]:
                    # Better phone pattern that avoids false positives
                    phone_pattern = r'[\+]?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
                    phone_matches = re.findall(phone_pattern, page_source)
                    # Filter out invalid phone numbers (like coordinates or IDs)
                    for match in phone_matches:
                        phone_str = ''.join(match)
                        # Validate it's a reasonable phone number
                        if len(phone_str) == 10 and not phone_str.startswith('000'):
                            # Format it nicely
                            if len(match) == 3:
                                info["phone"] = f"({match[0]}) {match[1]}-{match[2]}"
                            else:
                                info["phone"] = phone_str
                            break
                        
            except Exception as e:
                print(f"Error extracting phone: {str(e)}")
            
            # Extract website URL FIRST (needed for email extraction)
            try:
                website_selectors = [
                    "a[data-item-id='authority']",
                    "a[href^='http']",
                    "button[data-item-id='authority']",
                    "[data-item-id='authority']",
                    "a[aria-label*='Website']",
                    "a[aria-label*='website']",
                    "button[aria-label*='Website']",
                    "button[aria-label*='website']"
                ]
                
                for selector in website_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            # Try to get href first
                            href = element.get_attribute("href")
                            if not href:
                                # If it's a button, try clicking it to get the URL
                                try:
                                    if element.tag_name == 'button':
                                        # Click button to reveal link
                                        element.click()
                                        time.sleep(1)
                                        # Try to find the link after clicking
                                        link_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='http']")
                                        for link in link_elements:
                                            href = link.get_attribute("href")
                                            if href and (href.startswith("http://") or href.startswith("https://")):
                                                if "google.com" not in href.lower() and "maps.google" not in href.lower():
                                                    info["website"] = href
                                                    break
                                        if info["website"]:
                                            break
                                except:
                                    pass
                            
                            if href and (href.startswith("http://") or href.startswith("https://")):
                                # Filter out Google Maps URLs
                                if "google.com" not in href.lower() and "maps.google" not in href.lower():
                                    info["website"] = href
                                    print(f"  ✓ Found website: {info['website']}")
                                    break
                        if info["website"]:
                            break
                    except NoSuchElementException:
                        continue
                
                # Also search in page source
                if not info["website"]:
                    url_pattern = r'https?://(?!maps\.google|google\.com)[^\s<>"{}|\\^`\[\]]+'
                    url_matches = re.findall(url_pattern, page_source)
                    for url in url_matches:
                        if "google.com" not in url.lower() and "maps.google" not in url.lower():
                            info["website"] = url
                            print(f"  ✓ Found website in page source: {info['website']}")
                            break
                
                if not info["website"]:
                    print(f"  ⊗ No website found for this business")
                            
            except Exception as e:
                print(f"Error extracting website: {str(e)}")
            
            # Extract email (rarely available on Google Maps, but we'll try)
            try:
                # Multiple email patterns for better detection
                email_patterns = [
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard email
                    r'[a-zA-Z0-9._%+-]+\[?@\]?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email with [at] protection
                    r'[a-zA-Z0-9._%+-]+\s*\(at\)\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email with (at) protection
                    r'[a-zA-Z0-9._%+-]+\s*at\s*[a-zA-Z0-9.-]+\s*dot\s*[a-zA-Z]{2,}',  # Email with "at" and "dot"
                ]
                
                all_email_matches = []
                for pattern in email_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    all_email_matches.extend(matches)
                
                # Also check for mailto links in visible elements
                try:
                    mailto_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='mailto:'], *[href^='mailto:']")
                    for elem in mailto_elements:
                        href = elem.get_attribute("href")
                        if href and href.startswith("mailto:"):
                            email = href.replace("mailto:", "").split("?")[0].split("&")[0].strip()
                            if email and '@' in email:
                                all_email_matches.append(email)
                except:
                    pass
                
                # Filter out common non-business emails
                exclude_patterns = [
                    'google', 'gmail', 'example', 'test', 'noreply', 'no-reply',
                    'facebook', 'twitter', 'instagram', 'linkedin', 'youtube',
                    'sentry', 'analytics', 'tracking', 'pixel', 'cdn',
                    'wix', 'squarespace', 'wordpress', 'shopify', 'privacy',
                    'terms', 'legal', 'cookie', 'newsletter', 'unsubscribe',
                    'doubleclick', 'googletagmanager', 'adservice', 'adsystem'
                ]
                
                filtered_emails = []
                for email in all_email_matches:
                    # Clean email (remove [at] and (at) replacements)
                    email = email.replace('[at]', '@').replace('(at)', '@').replace(' at ', '@')
                    email = email.replace('[dot]', '.').replace('(dot)', '.').replace(' dot ', '.')
                    email = email.strip()
                    
                    # Validate email format
                    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
                        continue
                    
                    email_lower = email.lower()
                    # Skip if contains excluded patterns
                    if any(pattern in email_lower for pattern in exclude_patterns):
                        continue
                    # Skip if too long (likely not a real email)
                    if len(email) > 60:
                        continue
                    # Skip if already in list
                    if email not in filtered_emails:
                        filtered_emails.append(email)
                
                if filtered_emails:
                    # Prefer business-like emails
                    business_keywords = ['info', 'contact', 'hello', 'support', 'sales', 'admin', 'business', 'office', 'inquiry', 'enquiry', 'help']
                    business_emails = [e for e in filtered_emails if any(x in e.lower().split('@')[0] for x in business_keywords)]
                    if business_emails:
                        info["email"] = business_emails[0]
                    else:
                        info["email"] = filtered_emails[0]
                    print(f"  ✓ Found email on Google Maps: {info['email']}")
            except Exception as e:
                print(f"Error extracting email: {str(e)}")
            
            # Extract social media links from Google Maps FIRST (before visiting website)
            try:
                social_links = self._extract_social_media_links(page_source)
                info.update(social_links)
            except Exception as e:
                print(f"Error extracting social media links from Google Maps: {str(e)}")
            
            # If email not found or social links missing, visit website and extract email and social links
            if info["website"]:
                try:
                    # Always visit website for better data extraction (even if we have some data)
                    has_email = bool(info.get("email"))
                    has_social = any([info.get("facebook"), info.get("instagram"), info.get("linkedin"), info.get("twitter"), info.get("youtube"), info.get("tiktok")])
                    
                    if not has_email:
                        print(f"  Email not found on Google Maps. Visiting website to find email and social links: {info['website']}")
                    elif not has_social:
                        print(f"  Social links not found on Google Maps. Visiting website to find social media links: {info['website']}")
                    else:
                        print(f"  Visiting website to enhance data extraction (email and social links): {info['website']}")
                    
                    website_email, website_social = self._extract_email_from_website(info["website"])
                    
                    # Update email if found (website email takes priority if it's from same domain)
                    if website_email:
                        if not info["email"]:
                            info["email"] = website_email
                            print(f"  ✓ Found email on website: {website_email}")
                        else:
                            # Prefer website email if it's from the same domain
                            try:
                                from urllib.parse import urlparse
                                parsed_url = urlparse(info["website"])
                                website_domain = parsed_url.netloc.replace('www.', '')
                                if website_domain.lower() in website_email.lower():
                                    info["email"] = website_email
                                    print(f"  ✓ Updated email from website (same domain): {website_email}")
                            except:
                                pass
                    elif not info["email"]:
                        print(f"  ✗ No email found on website")
                    
                    # Merge social media links (website links take priority and supplement existing)
                    for platform in ["facebook", "instagram", "linkedin", "twitter", "youtube", "tiktok"]:
                        if website_social.get(platform):
                            if not info.get(platform):
                                info[platform] = website_social[platform]
                                print(f"  ✓ Found {platform} on website: {website_social[platform]}")
                            # Website links are generally more reliable, so update if found
                            elif website_social[platform] != info.get(platform):
                                info[platform] = website_social[platform]
                                print(f"  ✓ Updated {platform} from website: {website_social[platform]}")
                            
                except Exception as e:
                    print(f"  Error extracting data from website: {str(e)}")
            
            # Create combined social media links string (after all extraction)
            try:
                social_list = []
                if info.get("facebook"):
                    social_list.append(f"Facebook: {info['facebook']}")
                if info.get("instagram"):
                    social_list.append(f"Instagram: {info['instagram']}")
                if info.get("linkedin"):
                    social_list.append(f"LinkedIn: {info['linkedin']}")
                if info.get("twitter"):
                    social_list.append(f"Twitter: {info['twitter']}")
                if info.get("youtube"):
                    social_list.append(f"YouTube: {info['youtube']}")
                if info.get("tiktok"):
                    social_list.append(f"TikTok: {info['tiktok']}")
                
                if social_list:
                    info["social_media_links"] = " | ".join(social_list)
            except Exception as e:
                print(f"Error creating social media links string: {str(e)}")
            
            # Extract rating and reviews count
            try:
                rating_selectors = [
                    "span[class*='MW4etd']",
                    "span[aria-label*='stars']",
                    "div[class*='fontDisplayLarge']",
                    "span[class*='fontDisplayLarge']",
                    "[aria-label*='rating']",
                    "div[jsaction*='rating']"
                ]
                
                for selector in rating_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            rating_text = element.text.strip()
                            # Look for rating pattern (e.g., "4.5", "4.5 stars")
                            rating_match = re.search(r'(\d+\.?\d*)\s*(?:stars?|rating)?', rating_text, re.IGNORECASE)
                            if rating_match:
                                rating_value = rating_match.group(1)
                                try:
                                    rating_float = float(rating_value)
                                    if 0 <= rating_float <= 5:
                                        info["rating"] = rating_value
                                        break
                                except ValueError:
                                    pass
                        if info["rating"]:
                            break
                    except NoSuchElementException:
                        continue
                
                # Also search in page source
                if not info["rating"]:
                    rating_pattern = r'(\d+\.?\d*)\s*(?:stars?|rating)'
                    rating_matches = re.findall(rating_pattern, page_source, re.IGNORECASE)
                    for match in rating_matches:
                        try:
                            rating_float = float(match)
                            if 0 <= rating_float <= 5:
                                info["rating"] = str(rating_float)
                                break
                        except ValueError:
                            continue
                
                # Extract reviews count
                try:
                    reviews_selectors = [
                        "span[class*='UY7F9']",
                        "span[aria-label*='reviews']",
                        "button[aria-label*='reviews']",
                        "[aria-label*='review']"
                    ]
                    
                    for selector in reviews_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                reviews_text = element.text.strip()
                                # Look for number pattern (e.g., "1,234 reviews", "(1234)")
                                reviews_match = re.search(r'\(?([\d,]+)\s*(?:reviews?|ratings?)\)?', reviews_text, re.IGNORECASE)
                                if reviews_match:
                                    reviews_count = reviews_match.group(1).replace(',', '')
                                    info["reviews_count"] = reviews_count
                                    break
                            if info["reviews_count"]:
                                break
                        except NoSuchElementException:
                            continue
                except Exception as e:
                    print(f"Error extracting reviews count: {str(e)}")
                    
            except Exception as e:
                print(f"Error extracting rating: {str(e)}")
            
            # Extract business category/type
            try:
                category_selectors = [
                    "button[jsaction*='category']",
                    "[data-value*='category']",
                    "span[class*='DkE0']",
                    "button[aria-label*='Category']",
                    "[aria-label*='category']"
                ]
                
                for selector in category_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            category_text = element.text.strip()
                            if category_text and len(category_text) > 0 and len(category_text) < 100:
                                info["category"] = category_text
                                break
                        if info["category"]:
                            break
                    except NoSuchElementException:
                        continue
                
                # Also try to find category in page source
                if not info["category"]:
                    # Look for common category patterns
                    category_patterns = [
                        r'Category[:\s]+([A-Za-z\s&]+)',
                        r'Type[:\s]+([A-Za-z\s&]+)',
                        r'Business type[:\s]+([A-Za-z\s&]+)'
                    ]
                    for pattern in category_patterns:
                        matches = re.findall(pattern, page_source, re.IGNORECASE)
                        if matches:
                            info["category"] = matches[0].strip()
                            break
                            
            except Exception as e:
                print(f"Error extracting category: {str(e)}")
            
            # Extract business hours (if available)
            try:
                hours_selectors = [
                    "[data-item-id='hours']",
                    "button[data-item-id='hours']",
                    "[aria-label*='Hours']",
                    "[aria-label*='hours']",
                    "div[class*='t39EBf']"
                ]
                
                for selector in hours_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            hours_text = element.text.strip()
                            if hours_text and ("AM" in hours_text or "PM" in hours_text or "Open" in hours_text or "Closed" in hours_text):
                                info["business_hours"] = hours_text
                                break
                        if info["business_hours"]:
                            break
                    except NoSuchElementException:
                        continue
                        
            except Exception as e:
                print(f"Error extracting business hours: {str(e)}")
            
            # Calculate lead score based on data completeness
            lead_score = 0
            if info["name"]:
                lead_score += 10
            if info["address"]:
                lead_score += 15
            if info["phone"]:
                lead_score += 20
            if info["email"]:
                lead_score += 25
            if info["website"]:
                lead_score += 15
            if info["rating"]:
                lead_score += 10
            if info["category"]:
                lead_score += 5
            
            # Social media presence adds value
            social_count = sum(1 for key in ["facebook", "instagram", "linkedin", "twitter", "youtube", "tiktok"] if info.get(key))
            if social_count > 0:
                lead_score += min(social_count * 2, 10)  # Max 10 points for social media
            
            # Bonus points for high ratings
            if info["rating"]:
                try:
                    rating_float = float(info["rating"])
                    if rating_float >= 4.5:
                        lead_score += 5
                    elif rating_float >= 4.0:
                        lead_score += 3
                except ValueError:
                    pass
            
            info["lead_score"] = min(lead_score, 100)  # Cap at 100
            
            # Determine lead status based on score
            if lead_score >= 70:
                info["lead_status"] = "Hot"
            elif lead_score >= 50:
                info["lead_status"] = "Warm"
            elif lead_score >= 30:
                info["lead_status"] = "Cold"
            else:
                info["lead_status"] = "New"
            
            return info if any(info.values()) else None
            
        except Exception as e:
            print(f"Error in _extract_business_info: {str(e)}")
            return None
    
    def _extract_all_sidebar_results(self) -> List[Dict[str, Optional[str]]]:
        """Extract ALL results from the sidebar by scrolling and clicking each one."""
        results = []
        try:
            # Wait for sidebar to load
            time.sleep(3)
            
            # First, scroll to load all results in sidebar
            print("Scrolling to load all results...")
            self._scroll_sidebar_to_load_all()
            
            # Now find all result items in sidebar (after scrolling)
            # Get items multiple times to ensure we have the complete list
            result_items = []
            for attempt in range(3):
                items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                if len(items) > len(result_items):
                    result_items = items
                time.sleep(0.5)
            
            print(f"Found {len(result_items)} total results. Extracting information...")
            
            # Use set to track processed items and avoid duplicates
            processed_names = set()
            processed_addresses = set()  # Also track by address to catch duplicates with different names
            
            for idx, item in enumerate(result_items, 1):
                try:
                    print(f"Processing result {idx}/{len(result_items)}...")
                    
                    # Scroll item into view
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", item)
                    time.sleep(0.8)
                    
                    # Click on the item to open business details
                    try:
                        item.click()
                    except:
                        # Try alternative click method
                        try:
                            self.driver.execute_script("arguments[0].click();", item)
                        except:
                            # Try clicking on a child element
                            try:
                                clickable = item.find_element(By.CSS_SELECTOR, "a, button, div[role='button']")
                                clickable.click()
                            except:
                                print(f"  Could not click result {idx}, skipping...")
                                continue
                    
                    # Wait for business details to load
                    time.sleep(2.5)
                    
                    # Extract information
                    business_info = self._extract_business_info()
                    if business_info:
                        # Check for duplicates by name and address
                        name = business_info.get('name', '')
                        address = business_info.get('address', '')
                        
                        # Create unique identifier
                        unique_id = None
                        if name:
                            unique_id = name.lower().strip()
                        elif address:
                            unique_id = address.lower().strip()
                        
                        # Check if we've seen this before
                        is_duplicate = False
                        if unique_id:
                            if unique_id in processed_names:
                                is_duplicate = True
                            else:
                                processed_names.add(unique_id)
                        
                        # Also check by address if name is different
                        if address and not is_duplicate:
                            address_normalized = address.lower().strip()
                            if address_normalized in processed_addresses:
                                is_duplicate = True
                            else:
                                processed_addresses.add(address_normalized)
                        
                        if not is_duplicate:
                            results.append(business_info)
                            display_name = name if name else f"Business #{idx}"
                            print(f"  ✓ Extracted: {display_name}")
                        else:
                            print(f"  ⊗ Skipped duplicate: {name if name else 'Unknown'}")
                    else:
                        print(f"  ⊗ No data extracted for result {idx}")
                    
                    # Scroll back to sidebar to see next items
                    # Find sidebar element and scroll it
                    try:
                        sidebar = self.driver.find_element(By.CSS_SELECTOR, "div[role='main'] div[role='feed'], div[aria-label*='Results']")
                        self.driver.execute_script("arguments[0].scrollTop = 0;", sidebar)
                    except:
                        # Fallback: scroll window
                        self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  Error processing result {idx}: {str(e)}")
                    continue
            
            print(f"\n✓ Extracted {len(results)} unique results")
                    
        except Exception as e:
            print(f"Error extracting sidebar results: {str(e)}")
        
        return results
    
    def _scroll_sidebar_to_load_all(self):
        """Scroll the sidebar to load ALL available results - ensures no records are missed."""
        try:
            # Find the sidebar scrollable container
            sidebar_selectors = [
                "div[role='main'] div[role='feed']",
                "div[aria-label*='Results']",
                "div[role='feed']",
                "div.m6QErb.DxyBCb.kA9KIf.dS8AEf",  # Google Maps sidebar container
                "div[jsaction*='pane.resultContainer']"
            ]
            
            sidebar = None
            for selector in sidebar_selectors:
                try:
                    sidebar = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if sidebar:
                        break
                except:
                    continue
            
            if not sidebar:
                print("  Warning: Could not find sidebar container, using window scroll")
                sidebar = self.driver
            
            # Enhanced scroll strategy: Keep scrolling until absolutely no new results appear
            last_count = 0
            no_change_count = 0
            max_no_change = 5  # Increased: Stop after 5 scrolls with no new results (was 3)
            scroll_attempts = 0
            max_scrolls = 200  # Increased: Allow up to 200 scrolls to ensure we get everything (was 50)
            consecutive_same_count = 0
            max_consecutive_same = 5  # Additional check: 5 consecutive identical counts
            
            print("  Scrolling sidebar to load ALL results (this may take a while)...")
            
            while scroll_attempts < max_scrolls:
                scroll_attempts += 1
                
                # Get current count of results - check multiple times to ensure accuracy
                current_items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                current_count = len(current_items)
                
                # Try multiple scroll strategies for better coverage
                if sidebar == self.driver:
                    # Strategy 1: Scroll to bottom
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.5)
                    # Strategy 2: Scroll by large amount
                    self.driver.execute_script("window.scrollBy(0, 10000);")
                else:
                    # Strategy 1: Scroll sidebar container to bottom
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight;",
                        sidebar
                    )
                    time.sleep(0.3)
                    # Strategy 2: Scroll by large amount
                    try:
                        scroll_height = self.driver.execute_script("return arguments[0].scrollHeight;", sidebar)
                        scroll_top = self.driver.execute_script("return arguments[0].scrollTop;", sidebar)
                        client_height = self.driver.execute_script("return arguments[0].clientHeight;", sidebar)
                        # Scroll down by client height
                        self.driver.execute_script(
                            f"arguments[0].scrollTop = {scroll_top + client_height};",
                            sidebar
                        )
                    except:
                        pass
                
                # Wait longer for results to load (some results load slowly)
                time.sleep(2.0)  # Increased from 1.5 to 2.0 seconds
                
                # Check multiple times if new results appeared (some load asynchronously)
                for check_attempt in range(3):
                    new_items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                    new_count = len(new_items)
                    
                    if new_count > current_count:
                        print(f"  Loaded {new_count} results so far...")
                        last_count = new_count
                        no_change_count = 0
                        consecutive_same_count = 0
                        break
                    elif new_count == current_count:
                        if check_attempt < 2:  # Wait a bit more if first check shows no change
                            time.sleep(1.0)
                        else:
                            # Count didn't change after multiple checks
                            if new_count == last_count:
                                consecutive_same_count += 1
                            else:
                                consecutive_same_count = 0
                            no_change_count += 1
                            break
                
                # Check for end of results indicators
                try:
                    page_source = self.driver.page_source.lower()
                    # Look for indicators that we've reached the end
                    end_indicators = [
                        "no more results",
                        "end of results",
                        "showing all results",
                        "all results shown"
                    ]
                    if any(indicator in page_source for indicator in end_indicators):
                        print(f"  Reached end of results. Total: {new_count} results")
                        break
                except:
                    pass
                
                # Multiple exit conditions to ensure we've got everything
                if no_change_count >= max_no_change:
                    # Double-check: scroll one more time and wait longer
                    if sidebar == self.driver:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    else:
                        self.driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollHeight;",
                            sidebar
                        )
                    time.sleep(3.0)  # Wait longer for final check
                    
                    final_items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                    final_count = len(final_items)
                    
                    if final_count > new_count:
                        # Found more! Continue scrolling
                        print(f"  Found more results after final check! Now at {final_count} results...")
                        last_count = final_count
                        no_change_count = 0
                        continue
                    else:
                        print(f"  No more results loading. Total: {final_count} results")
                        break
                
                # Additional check: if we've had many consecutive identical counts
                if consecutive_same_count >= max_consecutive_same:
                    # Final verification scroll
                    if sidebar == self.driver:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    else:
                        self.driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollHeight;",
                            sidebar
                        )
                    time.sleep(2.0)
                    final_check = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                    if len(final_check) == new_count:
                        print(f"  Confirmed end of results. Total: {new_count} results")
                        break
            
            # Final comprehensive scroll to ensure we didn't miss anything
            print("  Performing final comprehensive scroll check...")
            for final_scroll in range(3):
                if sidebar == self.driver:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                else:
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight;",
                        sidebar
                    )
                time.sleep(1.5)
            
            # Get final count
            final_items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            final_count = len(final_items)
            print(f"  ✓ Final count: {final_count} results loaded")
            
            # Final scroll to top
            if sidebar != self.driver:
                self.driver.execute_script("arguments[0].scrollTop = 0;", sidebar)
            else:
                self.driver.execute_script("window.scrollTo(0, 0);")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error during scrolling: {str(e)}")
            # Continue anyway - we'll extract what we can
    
    def _extract_sidebar_results(self) -> List[Dict[str, Optional[str]]]:
        """Extract results from the sidebar when multiple results are shown (legacy method)."""
        return self._extract_all_sidebar_results()
    
    def _extract_email_from_website(self, website_url: str) -> Tuple[Optional[str], Dict[str, Optional[str]]]:
        """
        Visit the business website and extract email addresses and social media links.
        Tries multiple pages (home, contact, about) to find email and social links.
        Enhanced with better extraction methods.
        
        Args:
            website_url: URL of the business website
            
        Returns:
            Tuple of (email address if found, dictionary of social media links)
        """
        try:
            # Store current window handle and URL
            original_window = self.driver.current_window_handle
            original_url = self.driver.current_url
            
            # Clean and normalize website URL
            if not website_url.startswith('http://') and not website_url.startswith('https://'):
                website_url = 'https://' + website_url
            website_url = website_url.rstrip('/')
            
            # Extract domain for better email filtering
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(website_url)
                domain = parsed_url.netloc.replace('www.', '')
            except:
                domain = None
            
            # Pages to try (homepage, contact, about) - expanded list
            pages_to_try = [
                website_url,  # Homepage
                f"{website_url}/contact",
                f"{website_url}/contact-us",
                f"{website_url}/contact.html",
                f"{website_url}/about",
                f"{website_url}/about-us",
                f"{website_url}/get-in-touch",
                f"{website_url}/reach-us",
                f"{website_url}/contactus",
                f"{website_url}/contact-us.html"
            ]
            
            all_emails = []
            website_social_links = {
                "facebook": None,
                "instagram": None,
                "linkedin": None,
                "twitter": None,
                "youtube": None,
                "tiktok": None
            }
            exclude_patterns = [
                'google', 'gmail', 'example', 'test', 'noreply', 'no-reply',
                'facebook', 'twitter', 'instagram', 'linkedin', 'youtube',
                'sentry', 'analytics', 'tracking', 'pixel', 'cdn',
                'wix', 'squarespace', 'wordpress', 'shopify', 'privacy',
                'terms', 'legal', 'cookie', 'newsletter', 'unsubscribe',
                'doubleclick', 'googletagmanager', 'adservice', 'adsystem',
                'cloudflare', 'amazonaws', 'azure', 'github', 'stackoverflow'
            ]
            
            # Try each page (increased to 5 pages for better coverage)
            for page_url in pages_to_try[:5]:
                try:
                    # Open website in new tab
                    self.driver.execute_script(f"window.open('{page_url}', '_blank');")
                    time.sleep(2)
                    
                    # Switch to new tab
                    windows = self.driver.window_handles
                    if len(windows) > 1:
                        self.driver.switch_to.window(windows[-1])
                    else:
                        # If new tab didn't open, navigate directly
                        self.driver.get(page_url)
                    
                    # Wait for page to load and JavaScript to execute
                    time.sleep(5)
                    
                    # Wait for dynamic content to load
                    try:
                        WebDriverWait(self.driver, 5).until(
                            lambda d: d.execute_script('return document.readyState') == 'complete'
                        )
                    except:
                        pass
                    
                    # Get page source (includes JavaScript-rendered content)
                    page_source = self.driver.page_source
                    
                    # Also get text content from visible elements (catches JavaScript-rendered emails)
                    try:
                        body_text = self.driver.find_element(By.TAG_NAME, "body").text
                        page_source += " " + body_text
                    except:
                        pass
                    
                    # Multiple email patterns for better detection
                    email_patterns = [
                        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard email
                        r'[a-zA-Z0-9._%+-]+\[?@\]?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email with [at] protection
                        r'[a-zA-Z0-9._%+-]+\s*\(at\)\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email with (at) protection
                        r'[a-zA-Z0-9._%+-]+\s*at\s*[a-zA-Z0-9.-]+\s*dot\s*[a-zA-Z]{2,}',  # Email with "at" and "dot"
                        r'[a-zA-Z0-9._%+-]+\s*\[at\]\s*[a-zA-Z0-9.-]+\s*\[dot\]\s*[a-zA-Z]{2,}',  # Email with [at] and [dot]
                    ]
                    
                    for pattern in email_patterns:
                        email_matches = re.findall(pattern, page_source, re.IGNORECASE)
                        for email in email_matches:
                            # Clean email (remove [at] and (at) replacements)
                            email = email.replace('[at]', '@').replace('(at)', '@').replace(' at ', '@')
                            email = email.replace('[dot]', '.').replace('(dot)', '.').replace(' dot ', '.')
                            email = email.strip()
                            
                            # Validate email format
                            if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
                                continue
                            
                            email_lower = email.lower()
                            # Skip if contains excluded patterns
                            if any(pattern in email_lower for pattern in exclude_patterns):
                                continue
                            # Skip if too long (likely not a real email)
                            if len(email) > 60:
                                continue
                            # Prefer emails from the same domain
                            if domain and domain.lower() in email_lower:
                                # Prioritize same-domain emails
                                if email not in all_emails:
                                    all_emails.insert(0, email)
                            elif email not in all_emails:
                                all_emails.append(email)
                    
                    # Also check for mailto links (more thorough)
                    try:
                        mailto_selectors = [
                            "a[href^='mailto:']",
                            "*[href^='mailto:']",
                            "a[href*='mailto']",
                            "*[href*='mailto']"
                        ]
                        for selector in mailto_selectors:
                            mailto_links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for link in mailto_links:
                                href = link.get_attribute("href")
                                if href and "mailto:" in href.lower():
                                    email = href.split("mailto:")[-1].split("?")[0].split("&")[0].split("#")[0].strip()
                                    if email and '@' in email:
                                        # Validate
                                        if re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
                                            email_lower = email.lower()
                                            if not any(pattern in email_lower for pattern in exclude_patterns):
                                                if domain and domain.lower() in email_lower:
                                                    if email not in all_emails:
                                                        all_emails.insert(0, email)
                                                elif email not in all_emails:
                                                    all_emails.append(email)
                    except:
                        pass
                    
                    # Check text content of elements that might contain emails
                    try:
                        # Check footer, contact sections
                        contact_selectors = [
                            "footer", "[class*='contact']", "[id*='contact']",
                            "[class*='footer']", "[id*='footer']", "[class*='email']", "[id*='email']"
                        ]
                        for selector in contact_selectors:
                            try:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                for elem in elements:
                                    text = elem.text
                                    if text:
                                        email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
                                        for email in email_matches:
                                            email_lower = email.lower()
                                            if not any(pattern in email_lower for pattern in exclude_patterns):
                                                if domain and domain.lower() in email_lower:
                                                    if email not in all_emails:
                                                        all_emails.insert(0, email)
                                                elif email not in all_emails:
                                                    all_emails.append(email)
                            except:
                                continue
                    except:
                        pass
                    
                    # Extract social media links from website (enhanced)
                    try:
                        page_social_links = self._extract_social_media_links(page_source)
                        # Merge with existing social links (website links take priority)
                        for platform in website_social_links:
                            if page_social_links.get(platform) and not website_social_links[platform]:
                                website_social_links[platform] = page_social_links[platform]
                    except Exception as e:
                        print(f"  Error extracting social links from website: {str(e)}")
                    
                    # If we found good emails and social links, we can stop
                    if all_emails and domain and any(domain.lower() in e.lower() for e in all_emails[:3]):
                        if any(website_social_links.values()):
                            break
                    
                    # Close tab before trying next page
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(original_window)
                    
                except Exception as e:
                    # If page fails, try next one
                    try:
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                    except:
                        pass
                    continue
            
            # Make sure we're back on the original page
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                elif self.driver.current_url != original_url:
                    self.driver.back()
                    time.sleep(2)
            except:
                pass
            
            # Return best email found and social media links
            email_result = None
            if all_emails:
                # Prioritize: 1) Same domain emails, 2) Business-like emails, 3) First found
                same_domain_emails = []
                business_emails = []
                other_emails = []
                
                business_keywords = ['info', 'contact', 'hello', 'support', 'sales', 'admin', 'business', 'office', 'inquiry', 'enquiry', 'help', 'service']
                
                for email in all_emails:
                    email_lower = email.lower()
                    # Check if same domain
                    if domain and domain.lower() in email_lower:
                        if any(x in email_lower.split('@')[0] for x in business_keywords):
                            same_domain_emails.insert(0, email)  # Business emails from same domain first
                        else:
                            same_domain_emails.append(email)
                    # Check if business-like
                    elif any(x in email_lower.split('@')[0] for x in business_keywords):
                        business_emails.append(email)
                    else:
                        other_emails.append(email)
                
                # Priority order: same domain business > same domain > business > other
                if same_domain_emails:
                    email_result = same_domain_emails[0]
                elif business_emails:
                    email_result = business_emails[0]
                elif other_emails:
                    email_result = other_emails[0]
                else:
                    email_result = all_emails[0]
            
            return email_result, website_social_links
            
        except Exception as e:
            print(f"  Error visiting website for data extraction: {str(e)}")
            # Make sure we're back on the original page
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                elif self.driver.current_url != original_url:
                    self.driver.back()
                    time.sleep(2)
            except:
                pass
            return None, {
                "facebook": None,
                "instagram": None,
                "linkedin": None,
                "twitter": None,
                "youtube": None,
                "tiktok": None
            }
    
    def _extract_social_media_links(self, page_source: str) -> Dict[str, Optional[str]]:
        """
        Extract social media links from page source and visible links.
        Enhanced with better detection patterns and multiple extraction methods.
        
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
            # Find all links on the page (multiple selectors for better coverage)
            link_selectors = [
                "a[href]",
                "a[href*='facebook']",
                "a[href*='instagram']",
                "a[href*='linkedin']",
                "a[href*='twitter']",
                "a[href*='x.com']",
                "a[href*='youtube']",
                "a[href*='tiktok']",
                "*[href*='facebook']",
                "*[href*='instagram']",
                "*[href*='linkedin']",
                "*[href*='twitter']",
                "*[href*='x.com']",
                "*[href*='youtube']",
                "*[href*='tiktok']"
            ]
            
            all_links = []
            for selector in link_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    all_links.extend(links)
                except:
                    continue
            
            # Also check data attributes and other attributes that might contain social links
            try:
                # Check for social media icons/buttons
                social_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[class*='facebook'], [class*='instagram'], [class*='linkedin'], [class*='twitter'], [class*='youtube'], [class*='tiktok'], "
                    "[id*='facebook'], [id*='instagram'], [id*='linkedin'], [id*='twitter'], [id*='youtube'], [id*='tiktok']"
                )
                for elem in social_elements:
                    # Check various attributes
                    for attr in ['href', 'data-href', 'data-url', 'data-link', 'onclick']:
                        try:
                            value = elem.get_attribute(attr)
                            if value and any(platform in value.lower() for platform in ['facebook', 'instagram', 'linkedin', 'twitter', 'x.com', 'youtube', 'tiktok']):
                                all_links.append(elem)
                        except:
                            continue
            except:
                pass
            
            # Enhanced patterns for social media URLs (more comprehensive)
            patterns = {
                "facebook": [
                    r'https?://(?:www\.)?(?:facebook\.com|fb\.com)/(?:pages?/)?[^\s<>"{}|\\^`\[\]?&]+',
                    r'https?://(?:www\.)?facebook\.com/[^\s<>"{}|\\^`\[\]?&]+',
                    r'fb\.com/[^\s<>"{}|\\^`\[\]?&]+',
                    r'facebook\.com/[^\s<>"{}|\\^`\[\]?&]+',
                    r'/(?:pages?/)?[a-zA-Z0-9._-]+',  # Relative Facebook URLs
                ],
                "instagram": [
                    r'https?://(?:www\.)?instagram\.com/[^\s<>"{}|\\^`\[\]?&]+',
                    r'instagram\.com/[^\s<>"{}|\\^`\[\]?&]+',
                    r'instagr\.am/[^\s<>"{}|\\^`\[\]?&]+',
                ],
                "linkedin": [
                    r'https?://(?:www\.)?linkedin\.com/(?:company|in|pub|profile)/[^\s<>"{}|\\^`\[\]?&]+',
                    r'https?://(?:www\.)?linkedin\.com/[^\s<>"{}|\\^`\[\]?&]+',
                    r'linkedin\.com/[^\s<>"{}|\\^`\[\]?&]+',
                ],
                "twitter": [
                    r'https?://(?:www\.)?(?:twitter\.com|x\.com)/[^\s<>"{}|\\^`\[\]?&]+',
                    r'twitter\.com/[^\s<>"{}|\\^`\[\]?&]+',
                    r'x\.com/[^\s<>"{}|\\^`\[\]?&]+',
                ],
                "youtube": [
                    r'https?://(?:www\.)?(?:youtube\.com/(?:channel|c|user|@)|youtu\.be)/[^\s<>"{}|\\^`\[\]?&]+',
                    r'https?://(?:www\.)?youtube\.com/[^\s<>"{}|\\^`\[\]?&]+',
                    r'youtube\.com/[^\s<>"{}|\\^`\[\]?&]+',
                    r'youtu\.be/[^\s<>"{}|\\^`\[\]?&]+',
                ],
                "tiktok": [
                    r'https?://(?:www\.)?tiktok\.com/@?[^\s<>"{}|\\^`\[\]?&]+',
                    r'tiktok\.com/@?[^\s<>"{}|\\^`\[\]?&]+',
                ]
            }
            
            # Extract from visible links
            for link in all_links:
                try:
                    # Check multiple attributes
                    href = link.get_attribute("href") or link.get_attribute("data-href") or link.get_attribute("data-url") or link.get_attribute("data-link")
                    if not href:
                        # Check onclick attribute
                        onclick = link.get_attribute("onclick")
                        if onclick:
                            # Extract URL from onclick
                            url_match = re.search(r'https?://[^\s\'"<>]+', onclick)
                            if url_match:
                                href = url_match.group(0)
                            else:
                                continue
                        else:
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
                                    # Remove query parameters and fragments for cleaner URLs (but keep path)
                                    url = url.split('?')[0].split('#')[0]
                                    # Ensure it starts with http
                                    if not url.startswith('http'):
                                        url = 'https://' + url
                                    # Validate it's a proper social media URL
                                    if any(domain in url.lower() for domain in [
                                        'facebook.com', 'fb.com', 'instagram.com', 'linkedin.com',
                                        'twitter.com', 'x.com', 'youtube.com', 'youtu.be', 'tiktok.com'
                                    ]):
                                        social_links[platform] = url
                                        break
                except Exception:
                    continue
            
            # Also search in page source for any missed links (more thorough)
            for platform, platform_patterns in patterns.items():
                if not social_links[platform]:  # Only if not found in visible links
                    for pattern in platform_patterns:
                        matches = re.findall(pattern, page_source, re.IGNORECASE)
                        if matches:
                            for match in matches:
                                url = match
                                # Clean up the URL
                                url = url.split('?')[0].split('#')[0]
                                if not url.startswith('http'):
                                    url = 'https://' + url
                                # Validate it's a proper social media URL
                                if any(domain in url.lower() for domain in [
                                    'facebook.com', 'fb.com', 'instagram.com', 'linkedin.com',
                                    'twitter.com', 'x.com', 'youtube.com', 'youtu.be', 'tiktok.com'
                                ]):
                                    social_links[platform] = url
                                    break
                            if social_links[platform]:
                                break
            
            # Also check text content for social media mentions
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                for platform in ['facebook', 'instagram', 'linkedin', 'twitter', 'youtube', 'tiktok']:
                    if not social_links[platform]:
                        # Look for platform mentions followed by URLs
                        pattern = rf'{platform}\.com/[^\s]+'
                        matches = re.findall(pattern, body_text, re.IGNORECASE)
                        if matches:
                            url = matches[0]
                            if not url.startswith('http'):
                                url = 'https://' + url
                            url = url.split('?')[0].split('#')[0]
                            social_links[platform] = url
            except:
                pass
            
        except Exception as e:
            print(f"Error in _extract_social_media_links: {str(e)}")
        
        return social_links
    
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


def calculate_lead_quality(results: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
    """
    Calculate lead quality metrics for each result.
    
    Args:
        results: List of business information dictionaries
    
    Returns:
        List with added lead quality metrics
    """
    for result in results:
        # Lead score is already calculated, but we can add more metrics
        completeness = 0
        total_fields = 13  # name, address, phone, email, website, rating, category, facebook, instagram, linkedin, twitter, youtube, tiktok
        
        if result.get('name'):
            completeness += 1
        if result.get('address'):
            completeness += 1
        if result.get('phone'):
            completeness += 1
        if result.get('email'):
            completeness += 1
        if result.get('website'):
            completeness += 1
        if result.get('rating'):
            completeness += 1
        if result.get('category'):
            completeness += 1
        if result.get('facebook'):
            completeness += 1
        if result.get('instagram'):
            completeness += 1
        if result.get('linkedin'):
            completeness += 1
        if result.get('twitter'):
            completeness += 1
        if result.get('youtube'):
            completeness += 1
        if result.get('tiktok'):
            completeness += 1
        
        result['data_completeness'] = f"{(completeness/total_fields)*100:.1f}%"
        
    return results


def export_leads_to_csv(results: List[Dict[str, Optional[str]]], filename: str = "leads.csv", output_folder: str = "excel_results"):
    """
    Export leads to CSV format for CRM import.
    
    Args:
        results: List of dictionaries containing business information
        filename: Output CSV filename (default: leads.csv)
        output_folder: Folder name to store CSV files (default: excel_results)
    """
    import csv
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Join folder path with filename
    filepath = os.path.join(output_folder, filename)
    
    # Calculate lead quality
    results = calculate_lead_quality(results)
    
    # Define CSV headers (CRM-friendly format)
    # Check if batch processing fields exist
    has_batch_fields = any(result.get('search_keyword') for result in results)
    
    fieldnames = [
        "Company Name", "Address", "Phone", "Email", "Website",
        "Category", "Rating", "Reviews Count", "Business Hours",
        "Facebook", "Instagram", "LinkedIn", "Twitter", "YouTube", "TikTok", "Social Media Links",
        "Lead Score", "Lead Status", "Lead Source", "Data Completeness"
    ]
    
    # Add batch processing fields if they exist
    if has_batch_fields:
        fieldnames.insert(1, "Search Keyword")
        fieldnames.insert(2, "Search Location")
    
    # Write to CSV
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            row_data = {
                "Company Name": result.get('name', ''),
                "Address": result.get('address', ''),
                "Phone": result.get('phone', ''),
                "Email": result.get('email', ''),
                "Website": result.get('website', ''),
                "Category": result.get('category', ''),
                "Rating": result.get('rating', ''),
                "Reviews Count": result.get('reviews_count', ''),
                "Business Hours": result.get('business_hours', ''),
                "Facebook": result.get('facebook', ''),
                "Instagram": result.get('instagram', ''),
                "LinkedIn": result.get('linkedin', ''),
                "Twitter": result.get('twitter', ''),
                "YouTube": result.get('youtube', ''),
                "TikTok": result.get('tiktok', ''),
                "Social Media Links": result.get('social_media_links', ''),
                "Lead Score": result.get('lead_score', 0),
                "Lead Status": result.get('lead_status', 'New'),
                "Lead Source": result.get('lead_source', 'Google Maps'),
                "Data Completeness": result.get('data_completeness', '0%')
            }
            
            # Add batch processing fields if they exist
            if has_batch_fields:
                row_data["Search Keyword"] = result.get('search_keyword', '')
                row_data["Search Location"] = result.get('search_location', '')
            
            writer.writerow(row_data)
    
    print(f"Leads exported to CSV: {filepath}")


def export_to_excel(results: List[Dict[str, Optional[str]]], filename: str = "google_maps_results.xlsx", output_folder: str = "excel_results"):
    """
    Export search results to an Excel file in a separate folder.
    
    Args:
        results: List of dictionaries containing business information
        filename: Output Excel filename (default: google_maps_results.xlsx)
        output_folder: Folder name to store Excel files (default: excel_results)
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
    ws.title = "Google Maps Results"
    
    # Calculate lead quality
    results = calculate_lead_quality(results)
    
    # Check if batch processing fields exist
    has_batch_fields = any(result.get('search_keyword') for result in results)
    
    # Define headers (including lead generation fields)
    headers = ["Name", "Address", "Phone", "Email", "Website", "Category", 
               "Rating", "Reviews Count", "Business Hours", 
               "Facebook", "Instagram", "LinkedIn", "Twitter", "YouTube", "TikTok", "Social Media Links",
               "Lead Score", "Lead Status", "Lead Source", "Data Completeness"]
    
    # Add batch processing fields if they exist
    if has_batch_fields:
        headers.insert(1, "Search Keyword")
        headers.insert(2, "Search Location")
    
    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Write data
    for row_num, result in enumerate(results, 2):
        col = 1
        ws.cell(row=row_num, column=col, value=result.get('name', ''))
        col += 1
        
        # Add batch fields if they exist
        if has_batch_fields:
            ws.cell(row=row_num, column=col, value=result.get('search_keyword', ''))
            col += 1
            ws.cell(row=row_num, column=col, value=result.get('search_location', ''))
            col += 1
        
        ws.cell(row=row_num, column=col, value=result.get('address', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('phone', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('email', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('website', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('category', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('rating', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('reviews_count', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('business_hours', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('facebook', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('instagram', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('linkedin', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('twitter', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('youtube', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('tiktok', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('social_media_links', ''))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('lead_score', 0))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('lead_status', 'New'))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('lead_source', 'Google Maps'))
        col += 1
        ws.cell(row=row_num, column=col, value=result.get('data_completeness', '0%'))
    
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


def scrape_business_info(business_name: str, location: Optional[str] = None, headless: bool = False, export_excel: bool = False, excel_filename: str = None, output_folder: str = "excel_results", export_leads: bool = False) -> List[Dict[str, Optional[str]]]:
    """
    Convenience function to scrape business information from Google Maps.
    
    Args:
        business_name: Name of the business to search for
        location: Optional location to narrow down search
        headless: Run browser in headless mode
        export_excel: Whether to export results to Excel file
        excel_filename: Custom Excel filename (default: business_name_results.xlsx)
        output_folder: Folder name to store Excel files (default: excel_results)
        export_leads: Whether to export leads to CSV format for CRM import
    
    Returns:
        List of dictionaries containing business information
    """
    with GoogleMapsScraper(headless=headless) as scraper:
        results = scraper.search_business(business_name, location)
        
        if export_excel:
            if excel_filename is None:
                # Create safe filename from business name
                safe_name = "".join(c for c in business_name if c.isalnum() or c in (' ', '-', '_')).strip()
                excel_filename = f"{safe_name}_results.xlsx"
            export_to_excel(results, excel_filename, output_folder)
        
        if export_leads:
            safe_name = "".join(c for c in business_name if c.isalnum() or c in (' ', '-', '_')).strip()
            csv_filename = f"{safe_name}_leads.csv"
            export_leads_to_csv(results, csv_filename, output_folder)
        
        return results


if __name__ == "__main__":
    # Example usage
    import sys
    import io
    
    # Fix Windows console encoding issues
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python google_maps_scraper.py <business_name> [location]")
        print("Example: python google_maps_scraper.py 'Starbucks' 'New York, NY'")
        sys.exit(1)
    
    business_name = sys.argv[1]
    location = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Searching for: {business_name}" + (f" in {location}" if location else ""))
    print("-" * 50)
    
    # Scrape and export to Excel and CSV (saved in excel_results folder)
    results = scrape_business_info(business_name, location, headless=False, export_excel=True, export_leads=True, output_folder="excel_results")
    
    print(f"\nFound {len(results)} results\n")
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        # Safely print with encoding handling
        name = result.get('name', 'N/A') or 'N/A'
        address = result.get('address', 'N/A') or 'N/A'
        phone = result.get('phone', 'N/A') or 'N/A'
        email = result.get('email', 'N/A') or 'N/A'
        rating = result.get('rating', 'N/A') or 'N/A'
        reviews = result.get('reviews_count', 'N/A') or 'N/A'
        
        website = result.get('website', 'N/A') or 'N/A'
        category = result.get('category', 'N/A') or 'N/A'
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
        print(f"  Reviews: {reviews}")
        if social_links != 'N/A':
            print(f"  Social Media: {social_links}")
        print(f"  Lead Score: {lead_score}/100")
        print(f"  Lead Status: {lead_status}")

