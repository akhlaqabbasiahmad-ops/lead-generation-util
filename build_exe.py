"""
Build script to create EXE file using PyInstaller
Run: python build_exe.py
"""

import PyInstaller.__main__
import os
import sys

# Check if running on Windows
if sys.platform != 'win32':
    print("Warning: This build script is optimized for Windows. PyInstaller will still work on other platforms.")

# PyInstaller arguments
args = [
    'google_scraper_gui.py',  # Main script
    '--name=GoogleBusinessScraper',  # Name of the executable
    '--onefile',  # Create a single executable file
    '--windowed',  # No console window (GUI only)
    '--icon=NONE',  # You can add an icon file here if you have one
    '--add-data=google_maps_scraper.py;.',  # Include maps scraper
    '--add-data=google_web_scraper.py;.',  # Include web scraper
    '--add-data=social_media_search_scraper.py;.',  # Include social media search scraper
    '--add-data=clay_like_enrichment.py;.',  # Include Clay-like enrichment
    '--add-data=clay_integration.py;.',  # Include Clay integration
    '--hidden-import=selenium',
    '--hidden-import=webdriver_manager',
    '--hidden-import=openpyxl',
    '--hidden-import=tkinter',
    '--collect-all=selenium',
    '--collect-all=webdriver_manager',
    '--collect-all=openpyxl',
    '--noconfirm',  # Overwrite output without asking
    '--clean',  # Clean PyInstaller cache before building
]

print("Building EXE file...")
print("This may take a few minutes...")
PyInstaller.__main__.run(args)
print("\nBuild complete! Check the 'dist' folder for GoogleBusinessScraper.exe")


