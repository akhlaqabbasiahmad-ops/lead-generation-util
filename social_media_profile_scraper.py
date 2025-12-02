"""
Social Media Profile Scraper

This module provides functionality to scrape detailed information from social media profiles
including Facebook, Instagram, and LinkedIn.

Usage:
    from social_media_profile_scraper import SocialMediaProfileScraper
    
    with SocialMediaProfileScraper(driver) as scraper:
        fb_data = scraper.scrape_facebook_profile("https://facebook.com/page")
        ig_data = scraper.scrape_instagram_profile("https://instagram.com/profile")
        li_data = scraper.scrape_linkedin_profile("https://linkedin.com/company")
"""

from typing import Dict, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import time
import re


class SocialMediaProfileScraper:
    """
    Scraper for extracting detailed information from social media profiles.
    
    This class requires an active Selenium WebDriver instance to work.
    """
    
    def __init__(self, driver: WebDriver):
        """
        Initialize the social media profile scraper.
        
        Args:
            driver: Selenium WebDriver instance (must be already initialized)
        """
        self.driver = driver
    
    def scrape_facebook_profile(self, profile_url: str) -> Dict[str, Optional[str]]:
        """
        Scrape Facebook profile/page information.
        
        Args:
            profile_url: URL of the Facebook profile/page
            
        Returns:
            Dictionary with Facebook profile data:
            - facebook_followers: Number of followers/likes
            - facebook_bio: Bio/about section text
        """
        data = {
            "facebook_followers": None,
            "facebook_bio": None
        }
        
        try:
            # Store current window handle and URL
            original_window = self.driver.current_window_handle
            original_url = self.driver.current_url
            
            # Open Facebook profile in new tab
            self.driver.execute_script(f"window.open('{profile_url}', '_blank');")
            time.sleep(3)
            
            # Switch to new tab
            windows = self.driver.window_handles
            if len(windows) > 1:
                self.driver.switch_to.window(windows[-1])
            else:
                self.driver.get(profile_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Extract followers/likes count
            try:
                # Try multiple selectors for followers
                follower_selectors = [
                    "span[dir='auto']",
                    "div[role='main'] span",
                    "a[href*='/followers']",
                    "a[href*='/likes']",
                    "div[class*='x1i10hfl']"
                ]
                
                page_source = self.driver.page_source
                # Look for follower patterns in page source
                follower_patterns = [
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:followers|likes|people\s+like)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:people\s+follow)',
                    r'followed by\s+(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)'
                ]
                
                for pattern in follower_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        data["facebook_followers"] = matches[0]
                        print(f"    ✓ Found Facebook followers: {matches[0]}")
                        break
            except Exception as e:
                print(f"    Error extracting Facebook followers: {str(e)}")
            
            # Extract bio/about
            try:
                bio_selectors = [
                    "div[data-testid='about']",
                    "div[class*='about']",
                    "div[data-pagelet='ProfileTilesFeed']",
                    "span[dir='auto']"
                ]
                
                for selector in bio_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            bio_text = element.text.strip()
                            if bio_text and len(bio_text) > 20 and len(bio_text) < 500:
                                data["facebook_bio"] = bio_text
                                print(f"    ✓ Found Facebook bio")
                                break
                        if data["facebook_bio"]:
                            break
                    except:
                        continue
            except Exception as e:
                print(f"    Error extracting Facebook bio: {str(e)}")
            
            # Close tab and return to original
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(original_window)
            else:
                self.driver.back()
                time.sleep(2)
            
        except Exception as e:
            print(f"    Error scraping Facebook profile: {str(e)}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                elif self.driver.current_url != original_url:
                    self.driver.back()
                    time.sleep(2)
            except:
                pass
        
        return data
    
    def scrape_instagram_profile(self, profile_url: str) -> Dict[str, Optional[str]]:
        """
        Scrape Instagram profile information.
        
        Args:
            profile_url: URL of the Instagram profile
            
        Returns:
            Dictionary with Instagram profile data:
            - instagram_followers: Number of followers
            - instagram_posts: Number of posts
            - instagram_bio: Bio text
        """
        data = {
            "instagram_followers": None,
            "instagram_posts": None,
            "instagram_bio": None
        }
        
        try:
            # Store current window handle and URL
            original_window = self.driver.current_window_handle
            original_url = self.driver.current_url
            
            # Open Instagram profile in new tab
            self.driver.execute_script(f"window.open('{profile_url}', '_blank');")
            time.sleep(4)
            
            # Switch to new tab
            windows = self.driver.window_handles
            if len(windows) > 1:
                self.driver.switch_to.window(windows[-1])
            else:
                self.driver.get(profile_url)
            
            # Wait for page to load (Instagram may require login, so we'll try anyway)
            time.sleep(5)
            
            page_source = self.driver.page_source
            
            # Extract followers count
            try:
                # Instagram stores data in JSON-LD or meta tags
                follower_patterns = [
                    r'"edge_followed_by":\{"count":(\d+)\}',
                    r'"follower_count":(\d+)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:followers|follower)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:followers)'
                ]
                
                for pattern in follower_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        # Convert K/M/B to numbers if needed
                        if isinstance(count, str):
                            if 'K' in count.upper():
                                num = float(count.replace('K', '').replace(',', '')) * 1000
                                data["instagram_followers"] = str(int(num))
                            elif 'M' in count.upper():
                                num = float(count.replace('M', '').replace(',', '')) * 1000000
                                data["instagram_followers"] = str(int(num))
                            elif 'B' in count.upper():
                                num = float(count.replace('B', '').replace(',', '')) * 1000000000
                                data["instagram_followers"] = str(int(num))
                            else:
                                data["instagram_followers"] = count.replace(',', '')
                        else:
                            data["instagram_followers"] = str(count)
                        print(f"    ✓ Found Instagram followers: {data['instagram_followers']}")
                        break
            except Exception as e:
                print(f"    Error extracting Instagram followers: {str(e)}")
            
            # Extract posts count
            try:
                post_patterns = [
                    r'"edge_owner_to_timeline_media":\{"count":(\d+)\}',
                    r'"media_count":(\d+)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:posts|post)'
                ]
                
                for pattern in post_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        if isinstance(count, str):
                            data["instagram_posts"] = count.replace(',', '')
                        else:
                            data["instagram_posts"] = str(count)
                        print(f"    ✓ Found Instagram posts: {data['instagram_posts']}")
                        break
            except Exception as e:
                print(f"    Error extracting Instagram posts: {str(e)}")
            
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
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            bio_text = element.text.strip()
                            if bio_text and len(bio_text) > 5 and len(bio_text) < 500:
                                data["instagram_bio"] = bio_text
                                print(f"    ✓ Found Instagram bio")
                                break
                        if data["instagram_bio"]:
                            break
                    except:
                        continue
            except Exception as e:
                print(f"    Error extracting Instagram bio: {str(e)}")
            
            # Close tab and return to original
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(original_window)
            else:
                self.driver.back()
                time.sleep(2)
            
        except Exception as e:
            print(f"    Error scraping Instagram profile: {str(e)}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                elif self.driver.current_url != original_url:
                    self.driver.back()
                    time.sleep(2)
            except:
                pass
        
        return data
    
    def scrape_linkedin_profile(self, profile_url: str) -> Dict[str, Optional[str]]:
        """
        Scrape LinkedIn company/profile information.
        
        Args:
            profile_url: URL of the LinkedIn profile/company page
            
        Returns:
            Dictionary with LinkedIn profile data:
            - linkedin_followers: Number of followers
            - linkedin_employees: Number of employees
            - linkedin_about: About section text
        """
        data = {
            "linkedin_followers": None,
            "linkedin_employees": None,
            "linkedin_about": None
        }
        
        try:
            # Store current window handle and URL
            original_window = self.driver.current_window_handle
            original_url = self.driver.current_url
            
            # Open LinkedIn profile in new tab
            self.driver.execute_script(f"window.open('{profile_url}', '_blank');")
            time.sleep(4)
            
            # Switch to new tab
            windows = self.driver.window_handles
            if len(windows) > 1:
                self.driver.switch_to.window(windows[-1])
            else:
                self.driver.get(profile_url)
            
            # Wait for page to load (LinkedIn may require login)
            time.sleep(5)
            
            page_source = self.driver.page_source
            
            # Extract followers count
            try:
                follower_patterns = [
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:followers)',
                    r'"followerCount":(\d+)',
                    r'followers["\']?\s*[:\-]?\s*(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)'
                ]
                
                for pattern in follower_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        if isinstance(count, str):
                            data["linkedin_followers"] = count.replace(',', '')
                        else:
                            data["linkedin_followers"] = str(count)
                        print(f"    ✓ Found LinkedIn followers: {data['linkedin_followers']}")
                        break
            except Exception as e:
                print(f"    Error extracting LinkedIn followers: {str(e)}")
            
            # Extract employees count
            try:
                employee_patterns = [
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:employees|employee)',
                    r'"employeeCount":(\d+)',
                    r'employees["\']?\s*[:\-]?\s*(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)'
                ]
                
                for pattern in employee_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        if isinstance(count, str):
                            data["linkedin_employees"] = count.replace(',', '')
                        else:
                            data["linkedin_employees"] = str(count)
                        print(f"    ✓ Found LinkedIn employees: {data['linkedin_employees']}")
                        break
            except Exception as e:
                print(f"    Error extracting LinkedIn employees: {str(e)}")
            
            # Extract about section
            try:
                about_selectors = [
                    "section[data-test-id='about-us']",
                    "div[class*='about']",
                    "div[data-test-id='about']",
                    "p[class*='about']"
                ]
                
                for selector in about_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            about_text = element.text.strip()
                            if about_text and len(about_text) > 50 and len(about_text) < 2000:
                                data["linkedin_about"] = about_text[:500]  # Limit to 500 chars
                                print(f"    ✓ Found LinkedIn about section")
                                break
                        if data["linkedin_about"]:
                            break
                    except:
                        continue
            except Exception as e:
                print(f"    Error extracting LinkedIn about: {str(e)}")
            
            # Close tab and return to original
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(original_window)
            else:
                self.driver.back()
                time.sleep(2)
            
        except Exception as e:
            print(f"    Error scraping LinkedIn profile: {str(e)}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                elif self.driver.current_url != original_url:
                    self.driver.back()
                    time.sleep(2)
            except:
                pass
        
        return data


def scrape_all_social_profiles(driver: WebDriver, social_links: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """
    Convenience function to scrape all available social media profiles.
    
    Args:
        driver: Selenium WebDriver instance
        social_links: Dictionary containing social media URLs (facebook, instagram, linkedin keys)
        
    Returns:
        Dictionary with all scraped social media profile data
    """
    scraper = SocialMediaProfileScraper(driver)
    result = {}
    
    if social_links.get("facebook"):
        print(f"  Scraping Facebook profile: {social_links['facebook']}")
        fb_data = scraper.scrape_facebook_profile(social_links["facebook"])
        result.update(fb_data)
    
    if social_links.get("instagram"):
        print(f"  Scraping Instagram profile: {social_links['instagram']}")
        ig_data = scraper.scrape_instagram_profile(social_links["instagram"])
        result.update(ig_data)
    
    if social_links.get("linkedin"):
        print(f"  Scraping LinkedIn profile: {social_links['linkedin']}")
        li_data = scraper.scrape_linkedin_profile(social_links["linkedin"])
        result.update(li_data)
    
    return result

