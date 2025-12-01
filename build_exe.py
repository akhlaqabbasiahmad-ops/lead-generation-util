"""
Build script to create EXE file using PyInstaller
Run: python build_exe.py
"""

import PyInstaller.__main__
import os

# PyInstaller arguments
args = [
    'google_scraper_gui.py',  # Main script
    '--name=GoogleBusinessScraper',  # Name of the executable
    '--onefile',  # Create a single executable file
    '--windowed',  # No console window (GUI only)
    '--icon=NONE',  # You can add an icon file here if you have one
    '--add-data=google_maps_scraper.py;.',  # Include maps scraper
    '--add-data=google_web_scraper.py;.',  # Include web scraper
    '--hidden-import=selenium',
    '--hidden-import=webdriver_manager',
    '--hidden-import=openpyxl',
    '--hidden-import=tkinter',
    '--collect-all=selenium',
    '--collect-all=webdriver_manager',
    '--collect-all=openpyxl',
]

PyInstaller.__main__.run(args)


