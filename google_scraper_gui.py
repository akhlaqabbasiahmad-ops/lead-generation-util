"""
Google Maps & Web Scraper - Desktop Application
GUI version of the scraper tools
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import sys
import io
from datetime import datetime

# Import scrapers (will be imported after tkinter is initialized)
SCRAPERS_AVAILABLE = False
CLAY_FEATURES_AVAILABLE = False
try:
    from google_maps_scraper import scrape_business_info
    from google_web_scraper import search_businesses_web
    from social_media_search_scraper import SocialMediaSearchScraper, export_social_media_to_excel
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    SCRAPERS_AVAILABLE = False

try:
    from clay_integration import IntegratedScraper, export_enriched_leads_to_excel
    CLAY_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"Clay features import error: {e}")
    CLAY_FEATURES_AVAILABLE = False

# License validation removed - app is now free to use


class GoogleScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Business Scraper & Enrichment Platform - Clay-like GTM Tool")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)
        
        # Variables
        self.is_running = False
        self.scraper_thread = None
        self.integrated_scraper = None
        if CLAY_FEATURES_AVAILABLE:
            self.integrated_scraper = IntegratedScraper()
        
        # Fix Windows console encoding (only if buffer exists)
        if sys.platform == 'win32':
            try:
                if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
                    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                if hasattr(sys.stderr, 'buffer') and sys.stderr.buffer is not None:
                    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
            except (AttributeError, ValueError):
                # In GUI mode, stdout/stderr might not have buffer, which is fine
                pass
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Scraping
        self.scraping_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.scraping_frame, text="🔍 Scraping")
        self.create_scraping_tab()
        
        # Tab 2: Enrichment (Clay-like)
        if CLAY_FEATURES_AVAILABLE:
            self.enrichment_frame = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(self.enrichment_frame, text="✨ Enrichment")
            self.create_enrichment_tab()
            
            # Tab 3: Workflows
            self.workflows_frame = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(self.workflows_frame, text="⚙️ Workflows")
            self.create_workflows_tab()
            
            # Tab 4: Audiences
            self.audiences_frame = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(self.audiences_frame, text="👥 Audiences")
            self.create_audiences_tab()
        
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def create_scraping_tab(self):
        """Create the scraping tab (existing functionality)."""
        main_frame = self.scraping_frame
        
        # Scraper type selection
        scraper_frame = ttk.LabelFrame(main_frame, text="Scraper Type", padding="10")
        scraper_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.scraper_type = tk.StringVar(value="maps")
        ttk.Radiobutton(scraper_frame, text="Google Maps Scraper", 
                       variable=self.scraper_type, value="maps", command=self.on_scraper_type_change).grid(row=0, column=0, padx=10)
        ttk.Radiobutton(scraper_frame, text="Google Web Scraper", 
                       variable=self.scraper_type, value="web", command=self.on_scraper_type_change).grid(row=0, column=1, padx=10)
        ttk.Radiobutton(scraper_frame, text="Social Media Scraper", 
                       variable=self.scraper_type, value="social", command=self.on_scraper_type_change).grid(row=0, column=2, padx=10)
        
        # Search parameters
        params_frame = ttk.LabelFrame(main_frame, text="Search Parameters", padding="10")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Business name
        self.business_name_label = ttk.Label(params_frame, text="Business Name/Query:")
        self.business_name_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.business_name = ttk.Entry(params_frame, width=50)
        self.business_name.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.business_name.insert(0, "medical stores")
        
        # Location
        self.location_label = ttk.Label(params_frame, text="Location:")
        self.location_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.location = ttk.Entry(params_frame, width=50)
        self.location.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.location.insert(0, "Lahore")
        
        # Max results (for web scraper)
        self.web_params_frame = ttk.Frame(params_frame)
        self.web_params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.web_params_frame, text="Max Results (0 = unlimited):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.max_results = ttk.Entry(self.web_params_frame, width=10)
        self.max_results.grid(row=0, column=1, padx=5)
        self.max_results.insert(0, "0")
        
        ttk.Label(self.web_params_frame, text="Max Pages:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.max_pages = ttk.Entry(self.web_params_frame, width=10)
        self.max_pages.grid(row=0, column=3, padx=5)
        self.max_pages.insert(0, "8")
        
        # Social media params
        self.social_params_frame = ttk.Frame(params_frame)
        self.social_params_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.social_params_frame, text="Platform:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.social_platform = tk.StringVar(value="facebook")
        ttk.Radiobutton(self.social_params_frame, text="Facebook", 
                       variable=self.social_platform, value="facebook").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(self.social_params_frame, text="Instagram", 
                       variable=self.social_platform, value="instagram").grid(row=0, column=2, padx=5)
        
        ttk.Label(self.social_params_frame, text="Max Results:").grid(row=0, column=3, sticky=tk.W, padx=5)
        self.social_max_results = ttk.Entry(self.social_params_frame, width=10)
        self.social_max_results.grid(row=0, column=4, padx=5)
        self.social_max_results.insert(0, "10")
        
        # Initially hide social media params
        self.social_params_frame.grid_remove()
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.export_excel = tk.BooleanVar(value=True)
        self.export_csv = tk.BooleanVar(value=True)
        self.headless = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="Export to Excel", 
                       variable=self.export_excel).grid(row=0, column=0, padx=10)
        ttk.Checkbutton(options_frame, text="Export to CSV", 
                       variable=self.export_csv).grid(row=0, column=1, padx=10)
        ttk.Checkbutton(options_frame, text="Headless Mode (Hide Browser)", 
                       variable=self.headless).grid(row=0, column=2, padx=10)
        
        # Output folder
        ttk.Label(options_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_folder = ttk.Entry(options_frame, width=40)
        self.output_folder.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.output_folder.insert(0, "excel_results")
        
        ttk.Button(options_frame, text="Browse", 
                  command=self.browse_folder).grid(row=1, column=2, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", 
                                       command=self.start_scraping, width=20)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                      command=self.stop_scraping, 
                                      state=tk.DISABLED, width=20)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Open Output Folder", 
                  command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Output log
        log_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="10")
        log_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for scraping tab
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        params_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(1, weight=1)
    
    def create_enrichment_tab(self):
        """Create the enrichment tab (Clay-like features)."""
        main_frame = self.enrichment_frame
        
        # Title
        title_label = ttk.Label(main_frame, text="Data Enrichment & Waterfall Enrichment", 
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Enrichment input
        input_frame = ttk.LabelFrame(main_frame, text="Enrichment Input", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="Lead Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.enrich_name = ttk.Entry(input_frame, width=40)
        self.enrich_name.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="Location (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.enrich_location = ttk.Entry(input_frame, width=40)
        self.enrich_location.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Fields to enrich
        ttk.Label(input_frame, text="Fields to Enrich:").grid(row=2, column=0, sticky=tk.W, pady=5)
        fields_frame = ttk.Frame(input_frame)
        fields_frame.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.enrich_email = tk.BooleanVar(value=True)
        self.enrich_phone = tk.BooleanVar(value=True)
        self.enrich_website = tk.BooleanVar(value=True)
        self.enrich_social = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(fields_frame, text="Email", variable=self.enrich_email).grid(row=0, column=0, padx=5)
        ttk.Checkbutton(fields_frame, text="Phone", variable=self.enrich_phone).grid(row=0, column=1, padx=5)
        ttk.Checkbutton(fields_frame, text="Website", variable=self.enrich_website).grid(row=0, column=2, padx=5)
        ttk.Checkbutton(fields_frame, text="Social Media", variable=self.enrich_social).grid(row=0, column=3, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Enrich Lead", 
                  command=self.enrich_single_lead, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Bulk Enrich (from CSV)", 
                  command=self.bulk_enrich_from_csv, width=20).pack(side=tk.LEFT, padx=5)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Enrichment Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.enrichment_log = scrolledtext.ScrolledText(results_frame, height=20, width=80)
        self.enrichment_log.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        input_frame.columnconfigure(1, weight=1)
    
    def create_workflows_tab(self):
        """Create the workflows tab."""
        main_frame = self.workflows_frame
        
        title_label = ttk.Label(main_frame, text="GTM Workflow Automation", 
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Workflow list
        list_frame = ttk.LabelFrame(main_frame, text="Workflows", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.workflow_listbox = tk.Listbox(list_frame, height=10)
        self.workflow_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        workflow_buttons = ttk.Frame(main_frame)
        workflow_buttons.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(workflow_buttons, text="Create Standard Enrichment Workflow", 
                  command=self.create_standard_workflow).pack(side=tk.LEFT, padx=5)
        ttk.Button(workflow_buttons, text="Execute Workflow", 
                  command=self.execute_selected_workflow).pack(side=tk.LEFT, padx=5)
        
        # Workflow details
        details_frame = ttk.LabelFrame(main_frame, text="Workflow Details", padding="10")
        details_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.workflow_details = scrolledtext.ScrolledText(details_frame, height=15, width=80)
        self.workflow_details.pack(fill=tk.BOTH, expand=True)
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def create_audiences_tab(self):
        """Create the audiences tab."""
        main_frame = self.audiences_frame
        
        title_label = ttk.Label(main_frame, text="Dynamic Audience Builder", 
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Audience criteria
        criteria_frame = ttk.LabelFrame(main_frame, text="Audience Criteria", padding="10")
        criteria_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(criteria_frame, text="Audience Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.audience_name = ttk.Entry(criteria_frame, width=30)
        self.audience_name.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.audience_name.insert(0, "High Intent Leads")
        
        # Criteria
        ttk.Label(criteria_frame, text="Lead Score >").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.audience_score = ttk.Entry(criteria_frame, width=10)
        self.audience_score.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.audience_score.insert(0, "60")
        
        ttk.Checkbutton(criteria_frame, text="Must have email", 
                       variable=tk.BooleanVar(value=True)).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(criteria_frame, text="Must have phone", 
                       variable=tk.BooleanVar(value=True)).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons
        audience_buttons = ttk.Frame(main_frame)
        audience_buttons.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(audience_buttons, text="Create Audience", 
                  command=self.create_audience).pack(side=tk.LEFT, padx=5)
        ttk.Button(audience_buttons, text="Match Records", 
                  command=self.match_audience).pack(side=tk.LEFT, padx=5)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Audience Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.audience_results = scrolledtext.ScrolledText(results_frame, height=20, width=80)
        self.audience_results.pack(fill=tk.BOTH, expand=True)
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        criteria_frame.columnconfigure(1, weight=1)
    
    def on_scraper_type_change(self):
        """Show/hide relevant parameter fields based on scraper type."""
        scraper_type = self.scraper_type.get()
        
        if scraper_type == "web":
            self.web_params_frame.grid()
            self.social_params_frame.grid_remove()
            self.location_label.grid()
            self.location.grid()
        elif scraper_type == "social":
            self.web_params_frame.grid_remove()
            self.social_params_frame.grid()
            self.location_label.grid_remove()
            self.location.grid_remove()
        else:  # maps
            self.web_params_frame.grid_remove()
            self.social_params_frame.grid_remove()
            self.location_label.grid()
            self.location.grid()
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_folder.get())
        if folder:
            self.output_folder.delete(0, tk.END)
            self.output_folder.insert(0, folder)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_status(self, message, color="black"):
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def start_scraping(self):
        if not SCRAPERS_AVAILABLE:
            messagebox.showerror("Error", "Scraper modules not available. Please ensure google_maps_scraper.py and google_web_scraper.py are in the same folder.")
            return
        
        if self.is_running:
            messagebox.showwarning("Already Running", "Scraping is already in progress!")
            return
        
        business_name = self.business_name.get().strip()
        if not business_name:
            messagebox.showerror("Error", "Please enter a business name/query!")
            return
        
        location = self.location.get().strip()
        scraper_type = self.scraper_type.get()
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start()
        self.log_text.delete(1.0, tk.END)
        
        self.update_status("Starting scraper...", "blue")
        
        # Start scraping in separate thread
        self.scraper_thread = threading.Thread(
            target=self.run_scraper,
            args=(business_name, location, scraper_type),
            daemon=True
        )
        self.scraper_thread.start()
    
    def run_scraper(self, business_name, location, scraper_type):
        try:
            output_folder = self.output_folder.get().strip() or "excel_results"
            
            if scraper_type == "maps":
                self.log(f"Searching Google Maps for: {business_name} in {location}")
                self.log("-" * 50)
                
                results = scrape_business_info(
                    business_name=business_name,
                    location=location if location else None,
                    headless=self.headless.get(),
                    export_excel=self.export_excel.get(),
                    export_leads=self.export_csv.get(),
                    output_folder=output_folder
                )
                
            elif scraper_type == "web":
                max_results_str = self.max_results.get().strip() or "0"
                max_results = None if max_results_str == "0" else int(max_results_str)
                max_pages = int(self.max_pages.get().strip() or "8")
                
                query = f"{business_name} {location}" if location else business_name
                
                self.log(f"Searching Google Web for: {query}")
                self.log(f"Max results: {'UNLIMITED' if max_results is None else max_results}")
                self.log(f"Max pages: {max_pages}")
                self.log("-" * 50)
                
                results = search_businesses_web(
                    query=query,
                    max_results=max_results,
                    max_pages=max_pages,
                    headless=self.headless.get(),
                    export_excel=self.export_excel.get(),
                    export_csv=self.export_csv.get(),
                    output_folder=output_folder
                )
            
            else:  # social media scraper
                platform = self.social_platform.get()
                max_results = int(self.social_max_results.get().strip() or "10")
                
                self.log(f"Searching {platform.capitalize()} for: {business_name}")
                self.log(f"Max results: {max_results}")
                self.log("-" * 50)
                
                scraper = SocialMediaSearchScraper(headless=self.headless.get())
                try:
                    if platform == "facebook":
                        results = scraper.search_facebook(business_name, max_results)
                    else:  # instagram
                        results = scraper.search_instagram(business_name, max_results)
                    
                    # Export to Excel if requested
                    if self.export_excel.get() and results:
                        safe_name = "".join(c for c in business_name if c.isalnum() or c in (' ', '-', '_')).strip()
                        excel_filename = f"{platform}_{safe_name}_results.xlsx"
                        export_social_media_to_excel(results, excel_filename, output_folder, platform)
                        self.log(f"✓ Excel file exported to: {output_folder}/{excel_filename}")
                    
                finally:
                    scraper.close()
            
            self.log(f"\n✓ Scraping completed!")
            self.log(f"✓ Found {len(results)} results")
            
            if self.export_excel.get():
                self.log(f"✓ Excel file exported to: {output_folder}")
            if self.export_csv.get() and scraper_type != "social":
                self.log(f"✓ CSV file exported to: {output_folder}")
            
            self.log("\nResults Summary:")
            self.log("-" * 50)
            
            if scraper_type == "social":
                # Social media results format
                for i, result in enumerate(results[:10], 1):
                    if self.social_platform.get() == "facebook":
                        name = result.get('name', 'N/A')
                        url = result.get('url', 'N/A')
                        followers = result.get('followers', result.get('likes', 'N/A'))
                        category = result.get('category', 'N/A')
                        self.log(f"{i}. {name}")
                        self.log(f"   URL: {url}")
                        self.log(f"   Followers/Likes: {followers} | Category: {category}")
                    else:  # instagram
                        username = result.get('username', result.get('full_name', 'N/A'))
                        url = result.get('url', 'N/A')
                        followers = result.get('followers', 'N/A')
                        posts = result.get('posts', 'N/A')
                        self.log(f"{i}. {username}")
                        self.log(f"   URL: {url}")
                        self.log(f"   Followers: {followers} | Posts: {posts}")
            else:
                # Maps/Web results format
                for i, result in enumerate(results[:10], 1):
                    name = result.get('name', result.get('title', 'N/A'))
                    phone = result.get('phone', 'N/A')
                    email = result.get('email', 'N/A')
                    score = result.get('lead_score', 0)
                    status = result.get('lead_status', 'N/A')
                    self.log(f"{i}. {name}")
                    self.log(f"   Phone: {phone} | Email: {email} | Score: {score}/100 ({status})")
            
            if len(results) > 10:
                self.log(f"\n... and {len(results) - 10} more results (see Excel/CSV files)")
            
            self.update_status(f"Completed! Found {len(results)} results", "green")
            messagebox.showinfo("Success", f"Scraping completed!\n\nFound {len(results)} results.\n\nFiles saved to: {output_folder}")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log(f"\n✗ {error_msg}")
            self.update_status("Error occurred", "red")
            messagebox.showerror("Error", error_msg)
        finally:
            self.is_running = False
            self.progress.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def stop_scraping(self):
        if self.is_running:
            self.log("\n⚠ Stopping scraper...")
            self.is_running = False
            self.update_status("Stopped", "orange")
            # Note: Actual stopping would require more complex thread management
    
    def open_output_folder(self):
        folder = self.output_folder.get().strip() or "excel_results"
        if os.path.exists(folder):
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')
        else:
            messagebox.showwarning("Folder Not Found", f"Folder does not exist: {folder}")
    
    # Clay-like enrichment methods
    def enrich_single_lead(self):
        """Enrich a single lead using waterfall enrichment."""
        if not CLAY_FEATURES_AVAILABLE or not self.integrated_scraper:
            messagebox.showerror("Error", "Enrichment features not available!")
            return
        
        name = self.enrich_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a lead name!")
            return
        
        location = self.enrich_location.get().strip()
        
        # Determine fields to enrich
        fields = []
        if self.enrich_email.get():
            fields.append('email')
        if self.enrich_phone.get():
            fields.append('phone')
        if self.enrich_website.get():
            fields.append('website')
        if self.enrich_social.get():
            fields.extend(['facebook_url', 'instagram_url', 'linkedin_url'])
        
        self.enrichment_log.delete(1.0, tk.END)
        self.enrichment_log.insert(tk.END, f"Enriching lead: {name}\n")
        self.enrichment_log.insert(tk.END, f"Fields to enrich: {', '.join(fields)}\n")
        self.enrichment_log.insert(tk.END, "-" * 50 + "\n")
        
        try:
            lead = {'name': name}
            if location:
                lead['location'] = location
            
            enriched = self.integrated_scraper.enrich_lead(lead, fields)
            
            self.enrichment_log.insert(tk.END, "\n✓ Enrichment completed!\n")
            self.enrichment_log.insert(tk.END, "-" * 50 + "\n")
            self.enrichment_log.insert(tk.END, "Enriched Data:\n")
            for key, value in enriched.items():
                if value:
                    self.enrichment_log.insert(tk.END, f"  {key}: {value}\n")
            
            # Export to Excel
            output_folder = self.output_folder.get().strip() or "excel_results"
            from clay_integration import export_enriched_leads_to_excel
            export_enriched_leads_to_excel([enriched], f"enriched_{name.replace(' ', '_')}.xlsx", output_folder)
            self.enrichment_log.insert(tk.END, f"\n✓ Exported to Excel: {output_folder}\n")
            
        except Exception as e:
            self.enrichment_log.insert(tk.END, f"\n✗ Error: {str(e)}\n")
            messagebox.showerror("Error", f"Enrichment failed: {str(e)}")
    
    def bulk_enrich_from_csv(self):
        """Bulk enrich leads from CSV file."""
        if not CLAY_FEATURES_AVAILABLE or not self.integrated_scraper:
            messagebox.showerror("Error", "Enrichment features not available!")
            return
        
        csv_file = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not csv_file:
            return
        
        try:
            import csv
            leads = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('name') or row.get('Name'):
                        leads.append(row)
            
            if not leads:
                messagebox.showwarning("No Leads", "No leads found in CSV file!")
                return
            
            self.enrichment_log.delete(1.0, tk.END)
            self.enrichment_log.insert(tk.END, f"Found {len(leads)} leads in CSV\n")
            self.enrichment_log.insert(tk.END, "Starting bulk enrichment...\n")
            self.enrichment_log.insert(tk.END, "-" * 50 + "\n")
            
            # Determine fields to enrich
            fields = []
            if self.enrich_email.get():
                fields.append('email')
            if self.enrich_phone.get():
                fields.append('phone')
            if self.enrich_website.get():
                fields.append('website')
            if self.enrich_social.get():
                fields.extend(['facebook_url', 'instagram_url', 'linkedin_url'])
            
            enriched_leads = self.integrated_scraper.enrich_bulk(leads, fields)
            
            # Export results
            output_folder = self.output_folder.get().strip() or "excel_results"
            from clay_integration import export_enriched_leads_to_excel
            filename = f"bulk_enriched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            export_enriched_leads_to_excel(enriched_leads, filename, output_folder)
            
            self.enrichment_log.insert(tk.END, f"\n✓ Bulk enrichment completed!\n")
            self.enrichment_log.insert(tk.END, f"✓ Exported {len(enriched_leads)} leads to: {output_folder}/{filename}\n")
            
            messagebox.showinfo("Success", f"Bulk enrichment completed!\n\nEnriched {len(enriched_leads)} leads.\n\nSaved to: {output_folder}")
            
        except Exception as e:
            self.enrichment_log.insert(tk.END, f"\n✗ Error: {str(e)}\n")
            messagebox.showerror("Error", f"Bulk enrichment failed: {str(e)}")
    
    def create_standard_workflow(self):
        """Create a standard enrichment workflow."""
        if not CLAY_FEATURES_AVAILABLE or not self.integrated_scraper:
            messagebox.showerror("Error", "Workflow features not available!")
            return
        
        workflow = self.integrated_scraper.create_enrichment_workflow()
        self.workflow_listbox.insert(tk.END, workflow['name'])
        self.workflow_details.delete(1.0, tk.END)
        self.workflow_details.insert(tk.END, f"Workflow: {workflow['name']}\n")
        self.workflow_details.insert(tk.END, f"Created: {workflow['created_at']}\n")
        self.workflow_details.insert(tk.END, f"Steps: {len(workflow['steps'])}\n\n")
        for i, step in enumerate(workflow['steps'], 1):
            self.workflow_details.insert(tk.END, f"Step {i}: {step.get('type', 'unknown')}\n")
        
        messagebox.showinfo("Success", f"Workflow '{workflow['name']}' created!")
    
    def execute_selected_workflow(self):
        """Execute selected workflow."""
        selection = self.workflow_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a workflow!")
            return
        
        workflow_name = self.workflow_listbox.get(selection[0])
        messagebox.showinfo("Info", f"Workflow execution would happen here for: {workflow_name}\n\nThis feature requires a lead to process.")
    
    def create_audience(self):
        """Create a new audience."""
        if not CLAY_FEATURES_AVAILABLE or not self.integrated_scraper:
            messagebox.showerror("Error", "Audience features not available!")
            return
        
        name = self.audience_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter an audience name!")
            return
        
        try:
            score_threshold = int(self.audience_score.get().strip() or "60")
            criteria = {
                'lead_score': {'operator': 'greater_than', 'value': score_threshold}
            }
            
            audience = self.integrated_scraper.platform.build_audience(name, criteria)
            self.audience_results.delete(1.0, tk.END)
            self.audience_results.insert(tk.END, f"✓ Audience '{name}' created!\n")
            self.audience_results.insert(tk.END, f"Criteria: Lead Score > {score_threshold}\n")
            
            messagebox.showinfo("Success", f"Audience '{name}' created!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create audience: {str(e)}")
    
    def match_audience(self):
        """Match records against audience."""
        messagebox.showinfo("Info", "Audience matching requires leads to match.\n\nLoad leads from CSV or scrape first, then match.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GoogleScraperApp(root)
    root.mainloop()

