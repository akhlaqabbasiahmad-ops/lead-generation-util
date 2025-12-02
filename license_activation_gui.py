"""
License Activation GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
from license_manager import LicenseManager
from datetime import datetime

class LicenseActivationWindow:
    def __init__(self, parent, license_manager: LicenseManager):
        self.parent = parent
        self.license_manager = license_manager
        self.window = tk.Toplevel(parent)
        self.window.title("License Activation")
        self.window.geometry("550x450")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.check_existing_license()
    
    def setup_ui(self):
        # Header
        header = tk.Label(
            self.window,
            text="Google Business Scraper - License Activation",
            font=("Arial", 14, "bold"),
            pady=10
        )
        header.pack()
        
        # License key entry
        tk.Label(self.window, text="Enter License Key:", font=("Arial", 10)).pack(pady=5)
        self.license_entry = tk.Text(self.window, height=4, width=60, wrap=tk.WORD, font=("Courier", 9))
        self.license_entry.pack(pady=5, padx=20)
        
        # Activate button
        activate_btn = tk.Button(
            self.window,
            text="Activate License",
            command=self.activate_license,
            bg="#667eea",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        activate_btn.pack(pady=10)
        
        # Status frame
        self.status_frame = tk.Frame(self.window)
        self.status_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Purchase link
        purchase_label = tk.Label(
            self.window,
            text="Don't have a license? Contact support for purchase",
            fg="blue",
            cursor="hand2",
            font=("Arial", 9)
        )
        purchase_label.pack(pady=5)
        
        # Close button
        close_btn = tk.Button(
            self.window,
            text="Close",
            command=self.window.destroy,
            bg="#6c757d",
            fg="white",
            font=("Arial", 9),
            padx=15,
            pady=5
        )
        close_btn.pack(pady=5)
    
    def check_existing_license(self):
        """Check if license already exists and show status"""
        is_valid, license_data, message = self.license_manager.check_license_status()
        
        # Clear status frame
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        
        if is_valid:
            expiry_date = datetime.fromisoformat(license_data["expiry_date"])
            days_remaining = (expiry_date - datetime.now()).days
            
            tk.Label(
                self.status_frame,
                text="✓ License Active",
                fg="green",
                font=("Arial", 12, "bold")
            ).pack()
            
            tk.Label(
                self.status_frame,
                text=f"Tier: {license_data['tier'].upper()}",
                font=("Arial", 10)
            ).pack()
            
            tk.Label(
                self.status_frame,
                text=f"Email: {license_data.get('email', 'N/A')}",
                font=("Arial", 10)
            ).pack()
            
            tk.Label(
                self.status_frame,
                text=f"Expires: {expiry_date.strftime('%Y-%m-%d')}",
                font=("Arial", 10)
            ).pack()
            
            tk.Label(
                self.status_frame,
                text=f"Days Remaining: {days_remaining}",
                font=("Arial", 10, "bold"),
                fg="green" if days_remaining > 7 else "orange"
            ).pack()
        else:
            tk.Label(
                self.status_frame,
                text="No Active License",
                fg="red",
                font=("Arial", 12, "bold")
            ).pack()
            
            tk.Label(
                self.status_frame,
                text=message,
                font=("Arial", 10),
                wraplength=500,
                justify=tk.LEFT
            ).pack(pady=5)
    
    def activate_license(self):
        """Activate the entered license key"""
        license_key = self.license_entry.get("1.0", tk.END).strip()
        
        if not license_key:
            messagebox.showerror("Error", "Please enter a license key")
            return
        
        # Show processing
        self.window.config(cursor="wait")
        self.window.update()
        
        try:
            success, message = self.license_manager.activate_license(license_key)
            
            if success:
                messagebox.showinfo("Success", message)
                self.check_existing_license()
                # Don't close automatically - let user see the status
            else:
                messagebox.showerror("Activation Failed", message)
        finally:
            self.window.config(cursor="")
    
    def open_purchase_page(self):
        """Open purchase page in browser"""
        import webbrowser
        webbrowser.open("https://your-website.com/purchase")  # Change this

