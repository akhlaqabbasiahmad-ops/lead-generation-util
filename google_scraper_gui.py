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

# Import scrapers (will be imported after tkinter is initialized)
SCRAPERS_AVAILABLE = False
try:
    from google_maps_scraper import scrape_business_info
    from google_web_scraper import search_businesses_web
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    SCRAPERS_AVAILABLE = False


class GoogleScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Business Scraper - Lead Generation Tool")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.is_running = False
        self.scraper_thread = None
        
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
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Google Business Scraper", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Scraper type selection
        scraper_frame = ttk.LabelFrame(main_frame, text="Scraper Type", padding="10")
        scraper_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.scraper_type = tk.StringVar(value="maps")
        ttk.Radiobutton(scraper_frame, text="Google Maps Scraper", 
                       variable=self.scraper_type, value="maps").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(scraper_frame, text="Google Web Scraper", 
                       variable=self.scraper_type, value="web").grid(row=0, column=1, padx=10)
        
        # Search parameters
        params_frame = ttk.LabelFrame(main_frame, text="Search Parameters", padding="10")
        params_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Business name
        ttk.Label(params_frame, text="Business Name/Query:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.business_name = ttk.Entry(params_frame, width=50)
        self.business_name.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.business_name.insert(0, "medical stores")
        
        # Location
        ttk.Label(params_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
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
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
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
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
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
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Output log
        log_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="10")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        params_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(1, weight=1)
        
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
                
            else:  # web scraper
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
            
            self.log(f"\n✓ Scraping completed!")
            self.log(f"✓ Found {len(results)} results")
            
            if self.export_excel.get():
                self.log(f"✓ Excel file exported to: {output_folder}")
            if self.export_csv.get():
                self.log(f"✓ CSV file exported to: {output_folder}")
            
            self.log("\nResults Summary:")
            self.log("-" * 50)
            for i, result in enumerate(results[:10], 1):  # Show first 10
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


if __name__ == "__main__":
    root = tk.Tk()
    app = GoogleScraperApp(root)
    root.mainloop()

