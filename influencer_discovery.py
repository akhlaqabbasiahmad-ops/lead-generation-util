"""
Influencer Discovery & Analytics Platform (Modash-like)
Discovers and analyzes influencers/creators across Instagram, TikTok, and YouTube
"""

import time
import re
import os
from typing import Dict, Optional, List, Any
from datetime import datetime
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

try:
    from instagram_credentials import InstagramCredentialsManager
    CREDENTIALS_MANAGER_AVAILABLE = True
except ImportError:
    CREDENTIALS_MANAGER_AVAILABLE = False
    print("Warning: Instagram credentials manager not available")


class InfluencerDiscovery:
    """
    Discover and analyze influencers/creators across social media platforms.
    Similar to Modash functionality.
    """
    
    def __init__(self, headless: bool = False, wait_time: int = 10, auto_login: bool = True):
        """
        Initialize the influencer discovery platform.
        
        Args:
            headless: Run browser in headless mode (default: False)
            wait_time: Maximum wait time for elements to load (default: 10 seconds)
            auto_login: Automatically log in to Instagram if credentials are available (default: True)
        """
        self.wait_time = wait_time
        self.auto_login = auto_login
        self.is_logged_in = False
        self.setup_driver(headless)
        
        # Initialize credentials manager if available
        if CREDENTIALS_MANAGER_AVAILABLE:
            self.credentials_manager = InstagramCredentialsManager()
        else:
            self.credentials_manager = None
    
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
    
    def discover_instagram_creators(self, niche: str = None, location: str = None, 
                                   min_followers: int = None, max_followers: int = None,
                                   max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Discover Instagram creators/influencers.
        Uses Google search to find Instagram profiles since Instagram requires login.
        
        Args:
            niche: Niche/category (e.g., "fitness", "beauty", "tech")
            location: Location filter (e.g., "New York", "USA")
            min_followers: Minimum follower count
            max_followers: Maximum follower count
            max_results: Maximum number of results to return
            
        Returns:
            List of creator profiles with analytics
        """
        creators = []
        profile_links = []
        
        try:
            print(f"Discovering Instagram creators...")
            if niche:
                print(f"  Niche: {niche}")
            if location:
                print(f"  Location: {location}")
            
            # Login to Instagram if credentials are available
            if self.auto_login and self.credentials_manager:
                if self._login_to_instagram():
                    print(f"  ✓ Logged in to Instagram successfully")
                else:
                    print(f"  ⚠ Could not log in, continuing without login")
            
            profile_links = []
            
            # Method 1: If logged in, use Instagram's native search (best results)
            if self.is_logged_in:
                print(f"  Using Instagram native search (logged in)...")
                try:
                    self.driver.get("https://www.instagram.com")
                    time.sleep(3)
                    
                    # Find search box
                    search_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Search'], input[aria-label*='Search']"))
                    )
                    search_input.click()
                    time.sleep(1)
                    
                    # Build search query
                    query = niche or "influencer"
                    search_input.send_keys(query)
                    time.sleep(3)
                    
                    # Get search results from Instagram
                    try:
                        # Wait for results to appear
                        time.sleep(2)
                        
                        # Find profile links in search results
                        result_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/']")
                        instagram_profiles = []
                        
                        for link in result_links:
                            href = link.get_attribute("href")
                            if href and "instagram.com" in href:
                                if "/p/" not in href and "/reel/" not in href and "/tv/" not in href:
                                    if "/explore/" not in href and "/accounts/" not in href and "/direct/" not in href:
                                        if "?" in href:
                                            href = href.split("?")[0]
                                        if href.endswith("/"):
                                            href = href[:-1]
                                        if href not in instagram_profiles and href not in profile_links:
                                            instagram_profiles.append(href)
                                            if len(instagram_profiles) >= max_results * 2:
                                                break
                        
                        if instagram_profiles:
                            profile_links.extend(instagram_profiles)
                            print(f"  Found {len(instagram_profiles)} profiles from Instagram search")
                    except Exception as e:
                        print(f"  Warning: Error extracting from Instagram search: {str(e)}")
                        
                except Exception as e:
                    print(f"  Warning: Could not use Instagram search: {str(e)}")
            
            # Method 2: Use Google search to find Instagram profiles (both personal and business)
            if len(profile_links) < max_results:
                print(f"  Using Google search to find Instagram profiles (personal & business)...")
            
            # Try multiple search queries to get both personal and business profiles
            # Prioritize queries that find personal profiles
            # Add variations for better coverage
            niche_variations = [
                niche or 'influencer',
                f"{niche} influencer" if niche else 'influencer',
                f"{niche} mom" if niche else 'mom',
                f"{niche} parenting" if niche else 'parenting',
                f"{niche} lifestyle" if niche else 'lifestyle',
                f"{niche} content creator" if niche else 'content creator',
                f"{niche} vlogger" if niche else 'vlogger',
            ]
            
            search_queries = []
            for niche_var in niche_variations[:5]:  # Use first 5 variations for more coverage
                search_queries.extend([
                    f"site:instagram.com {niche_var} personal account",
                    f"site:instagram.com {niche_var} influencer",
                    f"site:instagram.com {niche_var} creator",
                    f"site:instagram.com {niche_var} blogger",
                    f"site:instagram.com {niche_var} content creator",
                ])
            
            # Add general searches
            search_queries.append(f"site:instagram.com {niche or 'influencer'}")
            search_queries.append(f"site:instagram.com {niche or 'influencer'} account")
            if location:
                for i in range(len(search_queries)):
                    search_queries[i] += f" {location}"
            
            profile_links = []
            
            # Search with each query to get diverse results (personal + business)
            for query_idx, search_query in enumerate(search_queries[:15], 1):  # Use first 15 queries for maximum coverage
                try:
                    print(f"  Search query {query_idx}: {search_query}")
                    google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                    self.driver.get(google_url)
                    time.sleep(3)
            
                    # Extract Instagram profile links from Google results
                    links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='instagram.com']")
                    
                    # Invalid Instagram usernames to skip
                    invalid_usernames = {
                        "explore", "accounts", "direct", "p", "reel", "tv", "stories", "tagged",
                        "servicelogin", "login", "logout", "signup", "accounts", "search",
                        "help", "about", "blog", "developers", "press", "api", "legal",
                        "privacy", "terms", "locations", "directory", "language", "hashtag"
                    }
                    
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "instagram.com" in href:
                            # Extract clean profile URL
                            if "/p/" in href or "/reel/" in href or "/tv/" in href or "/stories/" in href:
                                continue  # Skip posts
                            if "/explore/" in href or "/accounts/" in href or "/direct/" in href:
                                continue  # Skip non-profile pages
                            if "?" in href and "text=" in href:
                                continue  # Skip Google text fragments
                            
                            # Clean up URL
                            if "?" in href:
                                href = href.split("?")[0]
                            if "#" in href:
                                href = href.split("#")[0]
                            if href.endswith("/"):
                                href = href[:-1]
                            
                            # Extract username - skip /popular/ URLs
                            if "/popular/" in href:
                                continue  # Skip popular pages
                            
                            if "/" in href:
                                username = href.split("/")[-1].lower()
                                # Skip invalid usernames
                                if username and username not in invalid_usernames and len(username) > 1:
                                    # Check if it looks like a valid username (alphanumeric, dots, underscores)
                                    if re.match(r'^[a-z0-9._]+$', username):
                                        profile_url = f"https://www.instagram.com/{username}/"
                                        if profile_url not in profile_links:
                                            profile_links.append(profile_url)
                                            if len(profile_links) >= max_results * 3:  # Get more to filter
                                                break
                    
                    if len(profile_links) >= max_results * 3:
                        break
                        
                except Exception as e:
                    print(f"  Warning: Error in search query {query_idx}: {str(e)}")
                    continue
                except:
                    pass
            
            print(f"  Found {len(profile_links)} potential profiles from Google")
            
            # Method 2: Try hashtag pages (public, no login needed) - excellent for finding personal profiles
            # Always check hashtag pages as they're the best source for profiles
            if niche:
                try:
                    print(f"  Checking hashtag pages (excellent for personal profiles)...")
                    # Try multiple hashtag variations
                    hashtag_variations = [
                        niche.replace(" ", "").lower(),
                        f"{niche.replace(' ', '')}influencer",
                        f"{niche.replace(' ', '')}blogger",
                        f"{niche.replace(' ', '')}mom",
                        f"{niche.replace(' ', '')}parenting",
                        f"{niche.replace(' ', '')}lifestyle",
                        f"{niche.replace(' ', '')}contentcreator",
                        f"{niche.replace(' ', '')}vlogger",
                        f"{niche.replace(' ', '')}mama",
                        f"{niche.replace(' ', '')}motherhood",
                        f"{niche.replace(' ', '')}moms",
                        f"{niche.replace(' ', '')}momlife"
                    ]
                    
                    invalid_usernames = {
                        "explore", "accounts", "direct", "p", "reel", "tv", "stories", "tagged",
                        "servicelogin", "login", "logout", "signup", "accounts", "search",
                        "help", "about", "blog", "developers", "press", "api", "legal",
                        "privacy", "terms", "locations", "directory", "language", "hashtag"
                    }
                    
                    for hashtag in hashtag_variations[:10]:  # Try first 10 variations
                        try:
                            hashtag_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
                            self.driver.get(hashtag_url)
                            time.sleep(5)  # Wait longer for page load
                            
                            # Scroll to load more posts (personal profiles often appear in hashtag feeds)
                            for scroll in range(10):  # Scroll even more to get maximum profiles
                                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                time.sleep(2)
                                
                                # Also try clicking "Load More" if available
                                try:
                                    load_more_buttons = self.driver.find_elements(By.XPATH, 
                                        "//button[contains(text(), 'Load more') or contains(text(), 'Show more') or contains(text(), 'See more')]")
                                    for btn in load_more_buttons:
                                        if btn.is_displayed():
                                            btn.click()
                                            time.sleep(2)
                                            break
                                except:
                                    pass
                            
                            # Extract profile links from posts in hashtag page
                            # Posts have usernames in their links
                            try:
                                # Find all links on the page
                                all_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/']")
                                
                                for link in all_links:
                                    href = link.get_attribute("href")
                                    if href and "instagram.com" in href:
                                        # Skip invalid URLs
                                        if "/p/" in href or "/reel/" in href or "/tv/" in href:
                                            # Extract username from post URL
                                            parts = href.split("/")
                                            for i, part in enumerate(parts):
                                                if part == "p" or part == "reel" or part == "tv":
                                                    if i > 0 and parts[i-1] and "instagram.com" not in parts[i-1]:
                                                        username = parts[i-1].lower()
                                                        if username and username not in invalid_usernames and len(username) > 1:
                                                            if re.match(r'^[a-z0-9._]+$', username):
                                                                profile_url = f"https://www.instagram.com/{username}/"
                                                                if profile_url not in profile_links:
                                                                    profile_links.append(profile_url)
                                                                    if len(profile_links) >= max_results * 4:
                                                                        break
                                            continue
                                        
                                        if "/explore/" in href or "/accounts/" in href or "/direct/" in href:
                                            continue
                                        if "/popular/" in href:  # Skip popular pages
                                            continue
                                        
                                        # Extract username from profile URL
                                        if "/" in href:
                                            parts = [p for p in href.split("/") if p and "instagram.com" not in p and p not in ["", "explore", "tags"]]
                                            if parts:
                                                username = parts[-1].lower()
                                                if username and username not in invalid_usernames and len(username) > 1:
                                                    if re.match(r'^[a-z0-9._]+$', username):
                                                        profile_url = f"https://www.instagram.com/{username}/"
                                                        if profile_url not in profile_links:
                                                            profile_links.append(profile_url)
                                                            if len(profile_links) >= max_results * 4:
                                                                break
                                
                                print(f"    Found {len(profile_links)} total profiles from hashtag #{hashtag}")
                                
                            except Exception as e:
                                print(f"    Warning: Error extracting from hashtag #{hashtag}: {str(e)[:50]}")
                                pass
                            
                            if len(profile_links) >= max_results * 4:
                                print(f"  Reached target profile count, stopping hashtag search")
                                break
                        except Exception as e:
                            print(f"    Warning: Error accessing hashtag #{hashtag}: {str(e)[:50]}")
                            continue
                except Exception as e:
                    print(f"  Warning: Error accessing hashtag pages: {str(e)}")
            
            # Method 3: Search for personal profile patterns (usernames without business keywords)
            # This helps find personal accounts that might not show up in business searches
            print(f"  Total profiles found: {len(profile_links)} (mix of personal & business)")
            
            # Remove duplicates but keep order (personal profiles often come from hashtags)
            profile_links = list(dict.fromkeys(profile_links))
            
            # Don't limit here - we'll analyze more to get enough valid results
            # Prioritize profiles that look personal (not business-like usernames)
            # Personal profiles often don't have business keywords in username
            business_keywords = ['gym', 'fitness', 'club', 'official', 'center', 'center', 'studio', 'academy', 'pk', 'com']
            personal_profiles = []
            business_profiles = []
            
            for link in profile_links:
                username = link.split('/')[-2] if link.endswith('/') else link.split('/')[-1]
                username_lower = username.lower()
                
                # Check if username contains business keywords
                is_business_like = any(keyword in username_lower for keyword in business_keywords)
                
                if is_business_like:
                    business_profiles.append(link)
                else:
                    personal_profiles.append(link)
            
            # Mix: prioritize personal profiles but include business ones too
            # Put personal profiles first, then business profiles
            profile_links = personal_profiles + business_profiles
            # Analyze more profiles to ensure we get enough valid results
            profile_links = profile_links[:max_results * 4]  # Analyze 4x more to get enough valid ones
            
            print(f"  Found {len(personal_profiles)} personal-looking profiles, {len(business_profiles)} business-looking profiles")
            print(f"  Analyzing {len(profile_links)} unique profiles to find {max_results} valid ones...")
            
            # Analyze each profile - continue until we have enough valid results
            for idx, profile_url in enumerate(profile_links, 1):
                try:
                    print(f"  [{idx}/{len(profile_links)}] Analyzing: {profile_url}")
                    creator_data = self.analyze_instagram_profile(profile_url)
                    
                    if creator_data and creator_data.get('username'):
                        # Skip invalid/system accounts
                        username_lower = creator_data.get('username', '').lower()
                        invalid_usernames = {
                            "servicelogin", "login", "logout", "signup", "accounts", "search",
                            "help", "about", "blog", "developers", "press", "api", "legal",
                            "privacy", "terms", "locations", "directory", "language", "hashtag",
                            "explore", "direct", "p", "reel", "tv", "stories"
                        }
                        
                        if username_lower in invalid_usernames:
                            print(f"    ✗ Skipping invalid/system account")
                            continue
                        
                        # For personal profiles, be more lenient with follower count
                        # Personal profiles might have fewer followers but still be valid
                        if not creator_data.get('followers'):
                            # Check if it's a very new account or try to get followers from page
                            try:
                                # Give it another chance - might be a personal profile
                                time.sleep(1)
                                page_source = self.driver.page_source
                                # Try one more time to extract followers
                                follower_patterns = [
                                    r'"edge_followed_by":\{"count":(\d+)\}',
                                    r'"follower_count":(\d+)',
                                ]
                                for pattern in follower_patterns:
                                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                                    if matches:
                                        count = matches[0]
                                        creator_data['followers'] = self._format_follower_count(count)
                                        break
                                
                                # If still no followers, check if it looks like a personal profile
                                # Personal profiles might have posts but follower count might be hidden
                                if not creator_data.get('followers'):
                                    # Check if it has posts - if yes, it's likely a valid profile
                                    if creator_data.get('posts'):
                                        # Set a default small follower count for personal profiles
                                        creator_data['followers'] = "100"  # Estimate for personal profiles
                                        print(f"    ⚠ No follower data, but has posts (likely personal profile)")
                                    else:
                                        print(f"    ✗ No follower data and no posts (likely invalid)")
                                        continue
                            except:
                                # If it has posts, still consider it valid (personal profile)
                                if creator_data.get('posts'):
                                    creator_data['followers'] = "100"
                                    print(f"    ⚠ Using estimated followers for personal profile")
                                else:
                                    print(f"    ✗ No follower data (likely invalid)")
                                    continue
                        
                        # Apply filters
                        if min_followers and creator_data.get('followers'):
                            try:
                                followers_num = self._parse_follower_count(creator_data['followers'])
                                if followers_num < min_followers:
                                    print(f"    ✗ Below min followers threshold ({followers_num} < {min_followers})")
                                    continue
                            except:
                                pass
                        
                        if max_followers and creator_data.get('followers'):
                            try:
                                followers_num = self._parse_follower_count(creator_data['followers'])
                                if followers_num > max_followers:
                                    print(f"    ✗ Above max followers threshold ({followers_num} > {max_followers})")
                                    continue
                            except:
                                pass
                        
                        creators.append(creator_data)
                        print(f"    ✓ Extracted: {creator_data.get('username', 'Unknown')} ({creator_data.get('followers', 'N/A')} followers) [{len(creators)}/{max_results}]")
                        
                        if len(creators) >= max_results:
                            print(f"  ✓ Reached max results limit ({max_results})")
                            break
                    else:
                        print(f"    ✗ No data extracted")
                    
                    time.sleep(2)  # Be respectful with rate limiting
                    
                except Exception as e:
                    print(f"    ✗ Error: {str(e)[:100]}")
                    continue
            
            print(f"\n✓ Discovered {len(creators)} Instagram creators")
            
        except Exception as e:
            print(f"Error discovering Instagram creators: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return creators
    
    def analyze_instagram_profile(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """
        Analyze an Instagram profile and extract detailed analytics.
        
        Args:
            profile_url: URL of the Instagram profile
            
        Returns:
            Dictionary with creator analytics
        """
        try:
            # Navigate to profile
            self.driver.get(profile_url)
            time.sleep(4)
            
            data = {
                'platform': 'Instagram',
                'profile_url': profile_url,
                'username': None,
                'full_name': None,
                'followers': None,
                'following': None,
                'posts': None,
                'bio': None,
                'website': None,
                'is_verified': False,
                'is_business': False,
                'category': None,
                'engagement_rate': None,
                'avg_likes': None,
                'avg_comments': None,
                'hashtags': [],  # List of hashtags found
                'mentions': [],  # List of mentions (@username) found
                'scraped_at': datetime.now().isoformat()
            }
            
            page_source = self.driver.page_source
            
            # Extract username from URL
            if "/" in profile_url:
                username = profile_url.split("/")[-2] if profile_url.endswith("/") else profile_url.split("/")[-1]
                if username and username not in ["explore", "accounts", "direct"]:
                    data['username'] = username
            
            # Extract full name
            try:
                name_selectors = [
                    "h2[class*='_aacl']",
                    "h1",
                    "span[class*='_aacl']",
                    "header h1"
                ]
                for selector in name_selectors:
                    try:
                        name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        name_text = name_elem.text.strip()
                        if name_text and len(name_text) < 200:
                            data['full_name'] = name_text
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract followers, following, posts from page source
            try:
                # Followers - try multiple patterns
                follower_patterns = [
                    r'"edge_followed_by":\{"count":(\d+)\}',
                    r'"follower_count":(\d+)',
                    r'"edge_followed_by":\{[^}]*"count":(\d+)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:followers|follower)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*followers',
                    r'followers["\s]*:["\s]*(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)',
                ]
                for pattern in follower_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        # If it's a number, format it
                        if isinstance(count, str) and count.isdigit():
                            count = int(count)
                        data['followers'] = self._format_follower_count(count)
                        break
                
                # Also try to find in visible text
                if not data['followers']:
                    try:
                        follower_elements = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'followers') or contains(text(), 'follower')]")
                        for elem in follower_elements:
                            text = elem.text
                            match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)', text, re.IGNORECASE)
                            if match:
                                data['followers'] = match.group(1)
                                break
                    except:
                        pass
            except Exception as e:
                print(f"      Debug: Error extracting followers: {str(e)[:50]}")
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
                        data['following'] = str(count) if isinstance(count, (int, str)) else str(count)
                        break
            except:
                pass
            
            try:
                # Posts
                post_patterns = [
                    r'"edge_owner_to_timeline_media":\{"count":(\d+)\}',
                    r'"media_count":(\d+)',
                    r'"edge_owner_to_timeline_media":\{[^}]*"count":(\d+)',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:posts|post)',
                ]
                for pattern in post_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        count = matches[0]
                        data['posts'] = str(count) if isinstance(count, (int, str)) else str(count)
                        break
                
                # Also try visible text
                if not data['posts']:
                    try:
                        post_elements = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'posts') or contains(text(), 'post')]")
                        for elem in post_elements:
                            text = elem.text
                            match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)', text, re.IGNORECASE)
                            if match:
                                data['posts'] = match.group(1)
                                break
                    except:
                        pass
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
                            data['bio'] = bio_text
                            
                            # Extract hashtags from bio
                            hashtags = re.findall(r'#\w+', bio_text)
                            data['hashtags'] = list(set(hashtags))  # Remove duplicates
                            
                            # Extract mentions from bio
                            mentions = re.findall(r'@\w+', bio_text)
                            data['mentions'] = list(set(mentions))  # Remove duplicates
                            
                            break
                    except:
                        continue
            except:
                pass
            
            # Also extract hashtags and mentions from visible text (not CSS/HTML)
            try:
                # Get all visible text from the page
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    
                    # Extract hashtags from visible text (filter out color codes)
                    hashtag_pattern = r'#([a-zA-Z][a-zA-Z0-9_]{2,})'  # At least 3 chars, starts with letter
                    hashtags_in_text = re.findall(hashtag_pattern, body_text)
                    
                    # Filter out common color codes and technical terms
                    color_codes = {'1877F2', 'FFFFFF', '000000', 'ECF3FF', '444950', '77A7FF', '2851A3', '1D3C78', 'AAC9FF', 
                                  'FF0000', '00FF00', '0000FF', 'FFFF00', 'FF00FF', '00FFFF'}
                    
                    if hashtags_in_text:
                        filtered_hashtags = [f"#{tag}" for tag in hashtags_in_text 
                                           if tag.upper() not in color_codes 
                                           and len(tag) >= 3 
                                           and not tag.isdigit()]
                        # Combine with bio hashtags
                        all_hashtags = data.get('hashtags', []) + filtered_hashtags
                        data['hashtags'] = list(set(all_hashtags))[:20]  # Limit to 20 unique hashtags
                    
                    # Extract mentions from visible text
                    mention_pattern = r'@([a-zA-Z][a-zA-Z0-9_.]{1,})'  # At least 2 chars, starts with letter
                    mentions_in_text = re.findall(mention_pattern, body_text)
                    
                    if mentions_in_text:
                        # Filter out common technical mentions
                        filtered_mentions = [f"@{mention}" for mention in mentions_in_text 
                                            if len(mention) >= 2 
                                            and mention.lower() not in ['media', 'instagram', 'meta', 'facebook']]
                        # Combine with bio mentions
                        all_mentions = data.get('mentions', []) + filtered_mentions
                        data['mentions'] = list(set(all_mentions))[:20]  # Limit to 20 unique mentions
                except:
                    pass
            except:
                pass
            
            # Extract website
            try:
                website_elem = self.driver.find_element(By.CSS_SELECTOR, "a[href^='http']")
                href = website_elem.get_attribute("href")
                if href and "instagram.com" not in href.lower():
                    data['website'] = href
            except:
                pass
            
            # Check if verified
            try:
                verified_icon = self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='Verified'], [aria-label*='verified']")
                data['is_verified'] = True
            except:
                pass
            
            # Check if business account (but don't filter out personal accounts)
            try:
                # Look for business indicators
                business_indicators = [
                    "business account",
                    "contact button",
                    "category",
                    "business category"
                ]
                for indicator in business_indicators:
                    if indicator in page_source.lower():
                        data['is_business'] = True
                        break
                
                # If no business indicators, it's likely a personal account
                # We'll keep both types
            except:
                pass
            
            # Calculate engagement rate (if we have posts data)
            if data.get('followers') and data.get('posts'):
                try:
                    followers_num = self._parse_follower_count(data['followers'])
                    posts_num = int(data['posts']) if data['posts'] else 0
                    
                    # Estimate engagement (would need actual likes/comments for real calculation)
                    # This is a placeholder - real engagement requires analyzing posts
                    if followers_num > 0 and posts_num > 0:
                        # Rough estimate: assume 3% engagement rate
                        estimated_engagement = followers_num * 0.03
                        data['engagement_rate'] = f"{3.0:.2f}%"
                        data['estimated_engagement'] = int(estimated_engagement)
                except:
                    pass
            
            return data if data.get('username') or data.get('full_name') else None
            
        except Exception as e:
            print(f"    Error analyzing Instagram profile: {str(e)}")
            return None
    
    def discover_tiktok_creators(self, niche: str = None, location: str = None,
                                 min_followers: int = None, max_followers: int = None,
                                 max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Discover TikTok creators/influencers.
        
        Args:
            niche: Niche/category
            location: Location filter
            min_followers: Minimum follower count
            max_followers: Maximum follower count
            max_results: Maximum number of results
            
        Returns:
            List of TikTok creator profiles
        """
        creators = []
        try:
            print(f"Discovering TikTok creators...")
            
            # Navigate to TikTok search
            search_url = f"https://www.tiktok.com/search?q={niche or 'creator'}"
            self.driver.get(search_url)
            time.sleep(5)
            
            # Try to find creator profiles in search results
            try:
                # Scroll to load more results
                for scroll in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                # Find profile links
                profile_links = []
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/@']")
                for link in links:
                    href = link.get_attribute("href")
                    if href and "/@" in href and href not in profile_links:
                        profile_links.append(href)
                        if len(profile_links) >= max_results:
                            break
                
                print(f"  Found {len(profile_links)} profiles to analyze")
                
                # Analyze each profile
                for idx, profile_url in enumerate(profile_links[:max_results], 1):
                    try:
                        print(f"  Analyzing profile {idx}/{len(profile_links)}: {profile_url}")
                        creator_data = self.analyze_tiktok_profile(profile_url)
                        if creator_data:
                            # Apply filters
                            if min_followers and creator_data.get('followers'):
                                try:
                                    followers_num = self._parse_follower_count(creator_data['followers'])
                                    if followers_num < min_followers:
                                        continue
                                except:
                                    pass
                            
                            creators.append(creator_data)
                            print(f"    ✓ Extracted: {creator_data.get('username', 'Unknown')}")
                        
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"    ✗ Error: {str(e)}")
                        continue
                
            except Exception as e:
                print(f"  Error during TikTok search: {str(e)}")
            
            print(f"\n✓ Discovered {len(creators)} TikTok creators")
            
        except Exception as e:
            print(f"Error discovering TikTok creators: {str(e)}")
        
        return creators
    
    def analyze_tiktok_profile(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """Analyze a TikTok profile and extract analytics."""
        try:
            self.driver.get(profile_url)
            time.sleep(4)
            
            data = {
                'platform': 'TikTok',
                'profile_url': profile_url,
                'username': None,
                'display_name': None,
                'followers': None,
                'following': None,
                'likes': None,
                'videos': None,
                'bio': None,
                'is_verified': False,
                'engagement_rate': None,
                'hashtags': [],
                'mentions': [],
                'scraped_at': datetime.now().isoformat()
            }
            
            page_source = self.driver.page_source
            
            # Extract username from URL
            if "/@" in profile_url:
                username = profile_url.split("/@")[-1].split("/")[0]
                data['username'] = username
            
            # Extract display name
            try:
                name_elem = self.driver.find_element(By.CSS_SELECTOR, "h1, h2, [data-e2e='user-title']")
                data['display_name'] = name_elem.text.strip()
            except:
                pass
            
            # Extract followers, following, likes
            try:
                # Look for follower counts in page source
                follower_patterns = [
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:followers|follower)',
                    r'"followerCount":(\d+)'
                ]
                for pattern in follower_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        data['followers'] = self._format_follower_count(matches[0])
                        break
            except:
                pass
            
            try:
                following_patterns = [
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:following)',
                    r'"followingCount":(\d+)'
                ]
                for pattern in following_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        data['following'] = self._format_follower_count(matches[0])
                        break
            except:
                pass
            
            try:
                likes_patterns = [
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:likes|like)',
                    r'"heartCount":(\d+)'
                ]
                for pattern in likes_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        data['likes'] = self._format_follower_count(matches[0])
                        break
            except:
                pass
            
            # Extract bio
            try:
                bio_elem = self.driver.find_element(By.CSS_SELECTOR, "[data-e2e='user-bio'], h2 + div")
                bio_text = bio_elem.text.strip()
                data['bio'] = bio_text
                
                # Extract hashtags and mentions from bio
                if bio_text:
                    hashtags = re.findall(r'#\w+', bio_text)
                    data['hashtags'] = list(set(hashtags))
                    
                    mentions = re.findall(r'@\w+', bio_text)
                    data['mentions'] = list(set(mentions))
            except:
                pass
            
            # Extract from visible text (not CSS/HTML)
            try:
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    
                    # Extract hashtags from visible text
                    hashtag_pattern = r'#([a-zA-Z][a-zA-Z0-9_]{2,})'
                    hashtags_in_text = re.findall(hashtag_pattern, body_text)
                    
                    color_codes = {'1877F2', 'FFFFFF', '000000', 'ECF3FF', '444950', '77A7FF', '2851A3', '1D3C78', 'AAC9FF'}
                    
                    if hashtags_in_text:
                        filtered_hashtags = [f"#{tag}" for tag in hashtags_in_text 
                                           if tag.upper() not in color_codes 
                                           and len(tag) >= 3 
                                           and not tag.isdigit()]
                        all_hashtags = data.get('hashtags', []) + filtered_hashtags
                        data['hashtags'] = list(set(all_hashtags))[:20]
                    
                    # Extract mentions from visible text
                    mention_pattern = r'@([a-zA-Z][a-zA-Z0-9_.]{1,})'
                    mentions_in_text = re.findall(mention_pattern, body_text)
                    
                    if mentions_in_text:
                        filtered_mentions = [f"@{mention}" for mention in mentions_in_text 
                                            if len(mention) >= 2 
                                            and mention.lower() not in ['media', 'instagram', 'meta', 'facebook', 'tiktok']]
                        all_mentions = data.get('mentions', []) + filtered_mentions
                        data['mentions'] = list(set(all_mentions))[:20]
                except:
                    pass
            except:
                pass
            
            # Check verified
            try:
                verified = self.driver.find_element(By.CSS_SELECTOR, "[data-e2e='verified-icon']")
                data['is_verified'] = True
            except:
                pass
            
            return data if data.get('username') else None
            
        except Exception as e:
            print(f"    Error analyzing TikTok profile: {str(e)}")
            return None
    
    def discover_youtube_creators(self, niche: str = None, location: str = None,
                                  min_subscribers: int = None, max_subscribers: int = None,
                                  max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Discover YouTube creators/channels.
        
        Args:
            niche: Niche/category
            location: Location filter
            min_subscribers: Minimum subscriber count
            max_subscribers: Maximum subscriber count
            max_results: Maximum number of results
            
        Returns:
            List of YouTube channel profiles
        """
        creators = []
        try:
            print(f"Discovering YouTube creators...")
            
            # Build search query
            query = niche or "creator"
            if location:
                query += f" {location}"
            
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}&sp=EgIQAg%253D%253D"  # Filter to channels
            self.driver.get(search_url)
            time.sleep(5)
            
            # Find channel links
            try:
                # Scroll to load more
                for scroll in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                channel_links = []
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/channel/'], a[href*='/@'], a[href*='/c/']")
                for link in links:
                    href = link.get_attribute("href")
                    if href and ("/channel/" in href or "/@" in href or "/c/" in href):
                        if href not in channel_links:
                            channel_links.append(href)
                            if len(channel_links) >= max_results:
                                break
                
                print(f"  Found {len(channel_links)} channels to analyze")
                
                # Analyze each channel
                for idx, channel_url in enumerate(channel_links[:max_results], 1):
                    try:
                        print(f"  Analyzing channel {idx}/{len(channel_links)}: {channel_url}")
                        channel_data = self.analyze_youtube_channel(channel_url)
                        if channel_data:
                            # Apply filters
                            if min_subscribers and channel_data.get('subscribers'):
                                try:
                                    subs_num = self._parse_follower_count(channel_data['subscribers'])
                                    if subs_num < min_subscribers:
                                        continue
                                except:
                                    pass
                            
                            creators.append(channel_data)
                            print(f"    ✓ Extracted: {channel_data.get('channel_name', 'Unknown')}")
                        
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"    ✗ Error: {str(e)}")
                        continue
                
            except Exception as e:
                print(f"  Error during YouTube search: {str(e)}")
            
            print(f"\n✓ Discovered {len(creators)} YouTube creators")
            
        except Exception as e:
            print(f"Error discovering YouTube creators: {str(e)}")
        
        return creators
    
    def analyze_youtube_channel(self, channel_url: str) -> Optional[Dict[str, Any]]:
        """Analyze a YouTube channel and extract analytics."""
        try:
            self.driver.get(channel_url)
            time.sleep(4)
            
            data = {
                'platform': 'YouTube',
                'channel_url': channel_url,
                'channel_name': None,
                'handle': None,
                'subscribers': None,
                'videos': None,
                'total_views': None,
                'description': None,
                'location': None,
                'joined_date': None,
                'is_verified': False,
                'engagement_rate': None,
                'hashtags': [],
                'mentions': [],
                'scraped_at': datetime.now().isoformat()
            }
            
            page_source = self.driver.page_source
            
            # Extract channel name
            try:
                name_elem = self.driver.find_element(By.CSS_SELECTOR, "#channel-name, yt-formatted-string#text")
                data['channel_name'] = name_elem.text.strip()
            except:
                pass
            
            # Extract handle
            try:
                if "/@" in channel_url:
                    handle = channel_url.split("/@")[-1].split("/")[0]
                    data['handle'] = handle
            except:
                pass
            
            # Extract subscribers
            try:
                sub_patterns = [
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:subscribers)',
                    r'"subscriberCountText":\{"simpleText":"(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)'
                ]
                for pattern in sub_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        data['subscribers'] = self._format_follower_count(matches[0])
                        break
            except:
                pass
            
            # Extract video count
            try:
                video_patterns = [
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*(?:videos)',
                    r'"videosCountText":\{"runs":\[{"text":"(\d+)'
                ]
                for pattern in video_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    if matches:
                        data['videos'] = self._format_follower_count(matches[0])
                        break
            except:
                pass
            
            # Extract description
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, "#description, yt-formatted-string#description")
                desc_text = desc_elem.text.strip()[:500]
                data['description'] = desc_text
                
                # Extract hashtags and mentions from description
                if desc_text:
                    hashtags = re.findall(r'#\w+', desc_text)
                    data['hashtags'] = list(set(hashtags))
                    
                    mentions = re.findall(r'@\w+', desc_text)
                    data['mentions'] = list(set(mentions))
            except:
                pass
            
            # Extract from visible text (not CSS/HTML)
            try:
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    
                    # Extract hashtags from visible text
                    hashtag_pattern = r'#([a-zA-Z][a-zA-Z0-9_]{2,})'
                    hashtags_in_text = re.findall(hashtag_pattern, body_text)
                    
                    color_codes = {'1877F2', 'FFFFFF', '000000', 'ECF3FF', '444950', '77A7FF', '2851A3', '1D3C78', 'AAC9FF'}
                    
                    if hashtags_in_text:
                        filtered_hashtags = [f"#{tag}" for tag in hashtags_in_text 
                                           if tag.upper() not in color_codes 
                                           and len(tag) >= 3 
                                           and not tag.isdigit()]
                        all_hashtags = data.get('hashtags', []) + filtered_hashtags
                        data['hashtags'] = list(set(all_hashtags))[:20]
                    
                    # Extract mentions from visible text
                    mention_pattern = r'@([a-zA-Z][a-zA-Z0-9_.]{1,})'
                    mentions_in_text = re.findall(mention_pattern, body_text)
                    
                    if mentions_in_text:
                        filtered_mentions = [f"@{mention}" for mention in mentions_in_text 
                                            if len(mention) >= 2 
                                            and mention.lower() not in ['media', 'instagram', 'meta', 'facebook', 'tiktok']]
                        all_mentions = data.get('mentions', []) + filtered_mentions
                        data['mentions'] = list(set(all_mentions))[:20]
                except:
                    pass
            except:
                pass
            
            # Check verified
            try:
                verified = self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='Verified']")
                data['is_verified'] = True
            except:
                pass
            
            return data if data.get('channel_name') or data.get('handle') else None
            
        except Exception as e:
            print(f"    Error analyzing YouTube channel: {str(e)}")
            return None
    
    def _parse_follower_count(self, count_str: str) -> int:
        """Parse follower count string (e.g., '1.2M', '500K') to integer."""
        try:
            count_str = str(count_str).upper().replace(',', '').strip()
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            elif 'B' in count_str:
                return int(float(count_str.replace('B', '')) * 1000000000)
            else:
                return int(count_str)
        except:
            return 0
    
    def _format_follower_count(self, count) -> str:
        """Format follower count for display."""
        try:
            if isinstance(count, str):
                return count
            elif isinstance(count, (int, float)):
                if count >= 1000000:
                    return f"{count/1000000:.1f}M"
                elif count >= 1000:
                    return f"{count/1000:.1f}K"
                else:
                    return str(int(count))
            else:
                return str(count)
        except:
            return str(count)
    
    def _login_to_instagram(self) -> bool:
        """
        Log in to Instagram using stored credentials.
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.credentials_manager:
            print(f"    ⚠ No credentials manager available")
            return False
        
        username, password = self.credentials_manager.load_credentials()
        if not username or not password:
            print(f"    ⚠ No credentials found. Run 'python setup_instagram_login.py' to set up credentials.")
            return False
        
        try:
            print(f"  Attempting to log in to Instagram as {username}...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)  # Wait longer for page load
            
            # Try multiple selectors for username input
            username_input = None
            username_selectors = [
                "input[name='username']",
                "input[aria-label*='Phone number']",
                "input[aria-label*='Username']",
                "input[aria-label*='username']",
                "input[type='text']",
                "input[placeholder*='Phone number']",
                "input[placeholder*='Username']"
            ]
            
            for selector in username_selectors:
                try:
                    username_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if username_input.is_displayed():
                        print(f"    ✓ Found username field")
                        break
                except:
                    continue
            
            if not username_input:
                print(f"    ✗ Could not find username field")
                print(f"    💡 Tip: Run 'python setup_instagram_login.py' to set up credentials, or try logging in manually first.")
                return False
            
            # Enter username
            try:
                username_input.clear()
                time.sleep(0.5)
                username_input.click()
                time.sleep(0.5)
                username_input.send_keys(username)
                time.sleep(1)
                print(f"    ✓ Username entered")
            except Exception as e:
                print(f"    ✗ Error entering username: {str(e)}")
                return False
            
            # Try multiple selectors for password input
            password_input = None
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[aria-label*='Password']",
                "input[aria-label*='password']",
                "input[placeholder*='Password']"
            ]
            
            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if password_input.is_displayed():
                        print(f"    ✓ Found password field")
                        break
                except:
                    continue
            
            if not password_input:
                print(f"    ✗ Could not find password field")
                return False
            
            # Enter password
            try:
                password_input.clear()
                time.sleep(0.5)
                password_input.click()
                time.sleep(0.5)
                password_input.send_keys(password)
                time.sleep(1)
                print(f"    ✓ Password entered")
            except Exception as e:
                print(f"    ✗ Error entering password: {str(e)}")
                return False
            
            # Find and click login button
            login_button = None
            login_selectors = [
                "button[type='submit']",
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Log In')]",
            ]
            
            for selector in login_selectors:
                try:
                    if selector.startswith("//"):
                        login_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_button.is_displayed() and login_button.is_enabled():
                        print(f"    ✓ Found login button")
                        break
                except:
                    continue
            
            # If still not found, try finding by text
            if not login_button:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        btn_text = btn.text.strip().lower()
                        if "log" in btn_text or "sign in" in btn_text:
                            if btn.is_displayed() and btn.is_enabled():
                                login_button = btn
                                print(f"    ✓ Found login button by text")
                                break
                except:
                    pass
            
            # Submit form
            if login_button:
                try:
                    login_button.click()
                    print(f"    ✓ Login button clicked")
                    time.sleep(5)
                except Exception as e:
                    print(f"    ⚠ Error clicking button, trying Enter: {str(e)}")
                    try:
                        password_input.send_keys(Keys.RETURN)
                        time.sleep(5)
                    except:
                        pass
            else:
                # Fallback: press Enter
                try:
                    print(f"    ⚠ Login button not found, pressing Enter")
                    password_input.send_keys(Keys.RETURN)
                    time.sleep(5)
                except:
                    print(f"    ✗ Could not submit login form")
                    return False
            
            # Wait for navigation
            time.sleep(3)
            
            # Check if login was successful
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check for success indicators
            if "accounts/login" not in current_url and "challenge" not in current_url and "two_factor" not in current_url:
                # Additional check: look for home feed indicators
                if any(indicator in page_source for indicator in ["home", "feed", "explore", "reels"]) or "/" == current_url.split("instagram.com")[-1]:
                    self.is_logged_in = True
                    print(f"    ✓ Login successful! Current URL: {current_url[:80]}")
                    
                    # Handle "Save Your Login Info" or "Not Now" prompts
                    for attempt in range(3):
                        try:
                            not_now_buttons = self.driver.find_elements(By.XPATH, 
                                "//button[contains(text(), 'Not Now') or contains(text(), 'Not now') or contains(text(), 'Save Info')]")
                            for btn in not_now_buttons:
                                if btn.is_displayed():
                                    btn.click()
                                    time.sleep(2)
                                    break
                        except:
                            pass
                        time.sleep(1)
                    
                    return True
                else:
                    print(f"    ⚠ May need manual verification. Current URL: {current_url[:80]}")
                    return False
            else:
                # Check for error messages
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        "[role='alert'], .error, [class*='error'], [id*='error']")
                    for elem in error_elements:
                        if elem.is_displayed():
                            error_text = elem.text
                            if error_text:
                                print(f"    ✗ Login error: {error_text[:100]}")
                                break
                except:
                    pass
                
                print(f"    ✗ Login failed - still on login/challenge page")
                print(f"    Current URL: {current_url[:80]}")
                print(f"    💡 Tip: Instagram may require 2FA or manual verification. Try logging in manually in the browser.")
                return False
                
        except Exception as e:
            print(f"    ✗ Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_credentials(self, username: str, password: str) -> bool:
        """
        Save Instagram credentials for future logins.
        
        Args:
            username: Instagram username
            password: Instagram password
            
        Returns:
            True if saved successfully
        """
        if self.credentials_manager:
            return self.credentials_manager.save_credentials(username, password)
        return False
    
    def _login_to_instagram(self) -> bool:
        """
        Log in to Instagram using stored credentials.
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.credentials_manager:
            print(f"    ⚠ No credentials manager available")
            return False
        
        username, password = self.credentials_manager.load_credentials()
        if not username or not password:
            print(f"    ⚠ No credentials found. Run 'python setup_instagram_login.py' to set up credentials.")
            return False
        
        try:
            print(f"  Attempting to log in to Instagram as {username}...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)  # Wait longer for page load
            
            # Try multiple selectors for username input
            username_input = None
            username_selectors = [
                "input[name='username']",
                "input[aria-label*='Phone number']",
                "input[aria-label*='Username']",
                "input[aria-label*='username']",
                "input[type='text']",
                "input[placeholder*='Phone number']",
                "input[placeholder*='Username']"
            ]
            
            for selector in username_selectors:
                try:
                    username_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if username_input.is_displayed():
                        print(f"    ✓ Found username field")
                        break
                except:
                    continue
            
            if not username_input:
                print(f"    ✗ Could not find username field")
                print(f"    💡 Tip: Run 'python setup_instagram_login.py' to set up credentials, or try logging in manually first.")
                return False
            
            # Enter username
            try:
                username_input.clear()
                time.sleep(0.5)
                username_input.click()
                time.sleep(0.5)
                username_input.send_keys(username)
                time.sleep(1)
                print(f"    ✓ Username entered")
            except Exception as e:
                print(f"    ✗ Error entering username: {str(e)}")
                return False
            
            # Try multiple selectors for password input
            password_input = None
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[aria-label*='Password']",
                "input[aria-label*='password']",
                "input[placeholder*='Password']"
            ]
            
            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if password_input.is_displayed():
                        print(f"    ✓ Found password field")
                        break
                except:
                    continue
            
            if not password_input:
                print(f"    ✗ Could not find password field")
                return False
            
            # Enter password
            try:
                password_input.clear()
                time.sleep(0.5)
                password_input.click()
                time.sleep(0.5)
                password_input.send_keys(password)
                time.sleep(1)
                print(f"    ✓ Password entered")
            except Exception as e:
                print(f"    ✗ Error entering password: {str(e)}")
                return False
            
            # Find and click login button
            login_button = None
            login_selectors = [
                "button[type='submit']",
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Log In')]",
            ]
            
            for selector in login_selectors:
                try:
                    if selector.startswith("//"):
                        login_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_button.is_displayed() and login_button.is_enabled():
                        print(f"    ✓ Found login button")
                        break
                except:
                    continue
            
            # If still not found, try finding by text
            if not login_button:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        btn_text = btn.text.strip().lower()
                        if "log" in btn_text or "sign in" in btn_text:
                            if btn.is_displayed() and btn.is_enabled():
                                login_button = btn
                                print(f"    ✓ Found login button by text")
                                break
                except:
                    pass
            
            # Submit form
            if login_button:
                try:
                    login_button.click()
                    print(f"    ✓ Login button clicked")
                    time.sleep(5)
                except Exception as e:
                    print(f"    ⚠ Error clicking button, trying Enter: {str(e)}")
                    try:
                        password_input.send_keys(Keys.RETURN)
                        time.sleep(5)
                    except:
                        pass
            else:
                # Fallback: press Enter
                try:
                    print(f"    ⚠ Login button not found, pressing Enter")
                    password_input.send_keys(Keys.RETURN)
                    time.sleep(5)
                except:
                    print(f"    ✗ Could not submit login form")
                    return False
            
            # Wait for navigation
            time.sleep(3)
            
            # Check if login was successful
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check for success indicators
            if "accounts/login" not in current_url and "challenge" not in current_url and "two_factor" not in current_url:
                # Additional check: look for home feed indicators
                if any(indicator in page_source for indicator in ["home", "feed", "explore", "reels"]) or "/" == current_url.split("instagram.com")[-1]:
                    self.is_logged_in = True
                    print(f"    ✓ Login successful! Current URL: {current_url[:80]}")
                    
                    # Handle "Save Your Login Info" or "Not Now" prompts
                    for attempt in range(3):
                        try:
                            not_now_buttons = self.driver.find_elements(By.XPATH, 
                                "//button[contains(text(), 'Not Now') or contains(text(), 'Not now') or contains(text(), 'Save Info')]")
                            for btn in not_now_buttons:
                                if btn.is_displayed():
                                    btn.click()
                                    time.sleep(2)
                                    break
                        except:
                            pass
                        time.sleep(1)
                    
                    return True
                else:
                    print(f"    ⚠ May need manual verification. Current URL: {current_url[:80]}")
                    return False
            else:
                # Check for error messages
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        "[role='alert'], .error, [class*='error'], [id*='error']")
                    for elem in error_elements:
                        if elem.is_displayed():
                            error_text = elem.text
                            if error_text:
                                print(f"    ✗ Login error: {error_text[:100]}")
                                break
                except:
                    pass
                
                print(f"    ✗ Login failed - still on login/challenge page")
                print(f"    Current URL: {current_url[:80]}")
                print(f"    💡 Tip: Instagram may require 2FA or manual verification. Try logging in manually in the browser.")
                return False
                
        except Exception as e:
            print(f"    ✗ Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_credentials(self, username: str, password: str) -> bool:
        """
        Save Instagram credentials for future logins.
        
        Args:
            username: Instagram username
            password: Instagram password
            
        Returns:
            True if saved successfully
        """
        if self.credentials_manager:
            return self.credentials_manager.save_credentials(username, password)
        return False
    
    def calculate_engagement_rate(self, followers: int, avg_likes: int, avg_comments: int = 0) -> float:
        """
        Calculate engagement rate.
        
        Formula: ((Likes + Comments) / Followers) * 100
        """
        if followers == 0:
            return 0.0
        
        total_engagement = avg_likes + avg_comments
        engagement_rate = (total_engagement / followers) * 100
        return round(engagement_rate, 2)
    
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


def export_influencers_to_excel(creators: List[Dict[str, Any]], filename: str = "influencers.xlsx", 
                                output_folder: str = "excel_results"):
    """Export influencer data to Excel."""
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise ImportError("openpyxl is required. Install it with: pip install openpyxl")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    filepath = os.path.join(output_folder, filename)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Influencers"
    
    # Headers
    headers = [
        "Platform", "Username", "Full Name", "Profile URL",
        "Followers", "Following", "Posts/Videos", "Likes",
        "Bio/Description", "Website", "Verified", "Business Account",
        "Engagement Rate", "Category", "Hashtags", "Mentions", "Scraped At"
    ]
    
    # Write headers
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Write data
    for row_num, creator in enumerate(creators, 2):
        ws.cell(row=row_num, column=1, value=creator.get('platform', ''))
        ws.cell(row=row_num, column=2, value=creator.get('username', creator.get('handle', '')))
        ws.cell(row=row_num, column=3, value=creator.get('full_name', creator.get('display_name', creator.get('channel_name', ''))))
        ws.cell(row=row_num, column=4, value=creator.get('profile_url', creator.get('channel_url', '')))
        ws.cell(row=row_num, column=5, value=creator.get('followers', creator.get('subscribers', '')))
        ws.cell(row=row_num, column=6, value=creator.get('following', ''))
        ws.cell(row=row_num, column=7, value=creator.get('posts', creator.get('videos', '')))
        ws.cell(row=row_num, column=8, value=creator.get('likes', ''))
        ws.cell(row=row_num, column=9, value=creator.get('bio', creator.get('description', '')))
        ws.cell(row=row_num, column=10, value=creator.get('website', ''))
        ws.cell(row=row_num, column=11, value="Yes" if creator.get('is_verified') else "No")
        ws.cell(row=row_num, column=12, value="Yes" if creator.get('is_business') else "No")
        ws.cell(row=row_num, column=13, value=creator.get('engagement_rate', ''))
        ws.cell(row=row_num, column=14, value=creator.get('category', ''))
        # Hashtags - join list with comma
        hashtags_str = ', '.join(creator.get('hashtags', [])) if creator.get('hashtags') else ''
        ws.cell(row=row_num, column=15, value=hashtags_str)
        # Mentions - join list with comma
        mentions_str = ', '.join(creator.get('mentions', [])) if creator.get('mentions') else ''
        ws.cell(row=row_num, column=16, value=mentions_str)
        ws.cell(row=row_num, column=17, value=creator.get('scraped_at', ''))
    
    # Auto-adjust column widths
    for col_num, header in enumerate(headers, 1):
        column_letter = get_column_letter(col_num)
        max_length = len(header)
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col_num, max_col=col_num):
            if row[0].value:
                max_length = max(max_length, len(str(row[0].value)))
        ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
    
    wb.save(filepath)
    print(f"\nInfluencers exported to {filepath}")
    return filepath


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python influencer_discovery.py <platform> <niche> [location] [min_followers] [max_results]")
        print("Platform: instagram, tiktok, or youtube")
        print("Example: python influencer_discovery.py instagram fitness 'New York' 10000 20")
        sys.exit(1)
    
    platform = sys.argv[1].lower()
    niche = sys.argv[2] if len(sys.argv) > 2 else None
    location = sys.argv[3] if len(sys.argv) > 3 else None
    min_followers = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
    max_results = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5].isdigit() else 20
    
    scraper = InfluencerDiscovery(headless=False)
    
    try:
        if platform == "instagram":
            results = scraper.discover_instagram_creators(niche, location, min_followers, None, max_results)
        elif platform == "tiktok":
            results = scraper.discover_tiktok_creators(niche, location, min_followers, None, max_results)
        elif platform == "youtube":
            results = scraper.discover_youtube_creators(niche, location, min_followers, None, max_results)
        else:
            print(f"Unknown platform: {platform}. Use 'instagram', 'tiktok', or 'youtube'")
            sys.exit(1)
        
        # Export to Excel
        safe_niche = "".join(c for c in (niche or "influencers") if c.isalnum() or c in (' ', '-', '_')).strip()
        excel_filename = f"{platform}_{safe_niche}_influencers.xlsx"
        export_influencers_to_excel(results, excel_filename, "excel_results")
        
        print(f"\n{'='*60}")
        print(f"Found {len(results)} influencers")
        print(f"{'='*60}\n")
        
        for i, creator in enumerate(results, 1):
            print(f"Influencer {i}:")
            for key, value in creator.items():
                if value:
                    print(f"  {key}: {value}")
            print()
            
    finally:
        scraper.close()

