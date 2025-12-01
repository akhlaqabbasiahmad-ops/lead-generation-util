@echo off
echo Building Google Business Scraper EXE...
echo.

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build the EXE
pyinstaller --name=GoogleBusinessScraper --onefile --windowed --hidden-import=selenium --hidden-import=webdriver_manager --hidden-import=openpyxl --hidden-import=tkinter --collect-all=selenium --collect-all=webdriver_manager google_scraper_gui.py

echo.
echo Build complete! EXE file is in the 'dist' folder.
echo File: dist\GoogleBusinessScraper.exe
pause


