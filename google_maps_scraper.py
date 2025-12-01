"""
Google Maps Scraper Utility
Scrapes business information (location, phone number, email) from Google Maps by business name.
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
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            raise Exception(f"Failed to initialize Chrome driver. Make sure ChromeDriver is installed. Error: {str(e)}")
    
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
            
            # Extract email (rarely available on Google Maps, but we'll try)
            try:
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                email_matches = re.findall(email_pattern, page_source)
                # Filter out common non-business emails
                filtered_emails = [e for e in email_matches if not any(x in e.lower() for x in ['google', 'gmail', 'example', 'test', 'noreply', 'no-reply'])]
                if filtered_emails:
                    info["email"] = filtered_emails[0]
            except Exception as e:
                print(f"Error extracting email: {str(e)}")
            
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
            
            # Extract website URL
            try:
                website_selectors = [
                    "a[data-item-id='authority']",
                    "a[href^='http']",
                    "button[data-item-id='authority']",
                    "[data-item-id='authority']",
                    "a[aria-label*='Website']",
                    "a[aria-label*='website']"
                ]
                
                for selector in website_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            href = element.get_attribute("href")
                            if href and (href.startswith("http://") or href.startswith("https://")):
                                # Filter out Google Maps URLs
                                if "google.com" not in href.lower() and "maps.google" not in href.lower():
                                    info["website"] = href
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
                            break
                            
            except Exception as e:
                print(f"Error extracting website: {str(e)}")
            
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
        """Extract ALL results from the sidebar by clicking each one."""
        results = []
        try:
            # Wait for sidebar to load
            time.sleep(2)
            
            # Find all result items in sidebar
            result_items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            
            print(f"Found {len(result_items)} results. Extracting information...")
            
            for idx, item in enumerate(result_items, 1):
                try:
                    print(f"Processing result {idx}/{len(result_items)}...")
                    
                    # Scroll item into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", item)
                    time.sleep(0.5)
                    
                    # Click on the item to open business details
                    try:
                        item.click()
                    except:
                        # Try alternative click method
                        self.driver.execute_script("arguments[0].click();", item)
                    
                    # Wait for business details to load
                    time.sleep(2)
                    
                    # Extract information
                    business_info = self._extract_business_info()
                    if business_info:
                        results.append(business_info)
                    
                    # Scroll back to see next items
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error processing result {idx}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error extracting sidebar results: {str(e)}")
        
        return results
    
    def _extract_sidebar_results(self) -> List[Dict[str, Optional[str]]]:
        """Extract results from the sidebar when multiple results are shown (legacy method)."""
        return self._extract_all_sidebar_results()
    
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
        total_fields = 7  # name, address, phone, email, website, rating, category
        
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
    fieldnames = [
        "Company Name", "Address", "Phone", "Email", "Website",
        "Category", "Rating", "Reviews Count", "Business Hours",
        "Lead Score", "Lead Status", "Lead Source", "Data Completeness"
    ]
    
    # Write to CSV
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                "Company Name": result.get('name', ''),
                "Address": result.get('address', ''),
                "Phone": result.get('phone', ''),
                "Email": result.get('email', ''),
                "Website": result.get('website', ''),
                "Category": result.get('category', ''),
                "Rating": result.get('rating', ''),
                "Reviews Count": result.get('reviews_count', ''),
                "Business Hours": result.get('business_hours', ''),
                "Lead Score": result.get('lead_score', 0),
                "Lead Status": result.get('lead_status', 'New'),
                "Lead Source": result.get('lead_source', 'Google Maps'),
                "Data Completeness": result.get('data_completeness', '0%')
            })
    
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
    
    # Define headers (including lead generation fields)
    headers = ["Name", "Address", "Phone", "Email", "Website", "Category", 
               "Rating", "Reviews Count", "Business Hours", "Lead Score", 
               "Lead Status", "Lead Source", "Data Completeness"]
    
    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Write data
    for row_num, result in enumerate(results, 2):
        ws.cell(row=row_num, column=1, value=result.get('name', ''))
        ws.cell(row=row_num, column=2, value=result.get('address', ''))
        ws.cell(row=row_num, column=3, value=result.get('phone', ''))
        ws.cell(row=row_num, column=4, value=result.get('email', ''))
        ws.cell(row=row_num, column=5, value=result.get('website', ''))
        ws.cell(row=row_num, column=6, value=result.get('category', ''))
        ws.cell(row=row_num, column=7, value=result.get('rating', ''))
        ws.cell(row=row_num, column=8, value=result.get('reviews_count', ''))
        ws.cell(row=row_num, column=9, value=result.get('business_hours', ''))
        ws.cell(row=row_num, column=10, value=result.get('lead_score', 0))
        ws.cell(row=row_num, column=11, value=result.get('lead_status', 'New'))
        ws.cell(row=row_num, column=12, value=result.get('lead_source', 'Google Maps'))
        ws.cell(row=row_num, column=13, value=result.get('data_completeness', '0%'))
    
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
        
        print(f"  Name: {name}")
        print(f"  Address: {address}")
        print(f"  Phone: {phone}")
        print(f"  Email: {email}")
        print(f"  Website: {website}")
        print(f"  Category: {category}")
        print(f"  Rating: {rating}")
        print(f"  Reviews: {reviews}")
        print(f"  Lead Score: {lead_score}/100")
        print(f"  Lead Status: {lead_status}")

