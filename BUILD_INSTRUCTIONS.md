# Building Desktop Application (EXE)

## Prerequisites

1. Install Python 3.7 or higher
2. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Building the EXE

### Method 1: Using the build script

```bash
python build_exe.py
```

### Method 2: Manual PyInstaller command

```bash
pyinstaller --name=GoogleBusinessScraper ^
    --onefile ^
    --windowed ^
    --add-data="google_maps_scraper.py;." ^
    --add-data="google_web_scraper.py;." ^
    --hidden-import=selenium ^
    --hidden-import=webdriver_manager ^
    --hidden-import=openpyxl ^
    --hidden-import=tkinter ^
    --collect-all=selenium ^
    --collect-all=webdriver_manager ^
    google_scraper_gui.py
```

## Output

The EXE file will be created in the `dist` folder:
- `dist/GoogleBusinessScraper.exe`

## Distribution

1. Copy the EXE file to any Windows computer
2. The user needs Google Chrome installed (for Selenium)
3. No Python installation required on the target computer

## Notes

- The EXE will be large (50-100MB) because it includes Python and all dependencies
- First run may be slower as it extracts files
- ChromeDriver will be downloaded automatically on first use

## Troubleshooting

If the EXE doesn't work:
1. Check if Chrome is installed
2. Try running from command line to see error messages
3. Rebuild with `--console` flag to see errors:
   ```bash
   pyinstaller --onefile --console google_scraper_gui.py
   ```


