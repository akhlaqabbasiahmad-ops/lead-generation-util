# Google Business Scraper - Web Application

A web-based interface for the Google Business Scraper tool. Access it through any web browser!

## Features

- 🌐 **Web-Based Interface**: Access from any device with a web browser
- 📊 **Real-Time Progress**: See scraping progress in real-time
- 📁 **File Management**: View and download generated Excel/CSV files
- 🔍 **Dual Scrapers**: Google Maps and Google Web scrapers
- 📈 **Lead Generation**: Automatic lead scoring and classification
- 💾 **Export Options**: Excel and CSV export formats

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Web Application

### Option 1: Using the batch file (Windows)
```bash
start_web_server.bat
```

### Option 2: Manual start
```bash
python app.py
```

### Option 3: Custom port
Edit `app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change 5000 to your preferred port
```

## Accessing the Application

Once started, open your web browser and navigate to:
- **Local access**: http://localhost:5000
- **Network access**: http://YOUR_IP_ADDRESS:5000

## Usage

1. **Select Scraper Type**:
   - Google Maps Scraper: Searches Google Maps listings
   - Google Web Scraper: Searches entire Google web results

2. **Enter Search Parameters**:
   - Business Name/Query: What to search for
   - Location: Optional location to narrow search
   - Max Results/Pages: For web scraper only

3. **Configure Options**:
   - Export to Excel: Generate Excel file
   - Export to CSV: Generate CSV file
   - Headless Mode: Hide browser window

4. **Start Scraping**: Click "Start Scraping" button

5. **View Results**: Results appear in real-time as they're found

6. **Download Files**: Click "Download" on any generated file

## API Endpoints

The web application also provides REST API endpoints:

- `POST /api/scrape` - Start a scraping job
- `GET /api/status` - Get current scraping status
- `GET /api/results` - Get scraping results
- `GET /api/files` - List available output files
- `GET /api/download/<filename>` - Download a file

## Example API Usage

```javascript
// Start scraping
fetch('/api/scrape', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        scraper_type: 'maps',
        business_name: 'medical stores',
        location: 'Lahore',
        export_excel: true,
        export_csv: true
    })
});

// Check status
fetch('/api/status')
    .then(res => res.json())
    .then(data => console.log(data));
```

## Network Access

To access from other devices on your network:

1. Find your IP address:
   - Windows: `ipconfig` (look for IPv4 Address)
   - Mac/Linux: `ifconfig` or `ip addr`

2. Start the server with:
   ```python
   app.run(host='0.0.0.0', port=5000)
   ```

3. Access from other devices:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

## Security Notes

⚠️ **Important**: This is a development server. For production use:
- Use a production WSGI server (Gunicorn, uWSGI)
- Add authentication/authorization
- Use HTTPS
- Configure firewall rules
- Set up proper logging

## Troubleshooting

### Port already in use
Change the port in `app.py`:
```python
app.run(port=8080)  # Use a different port
```

### Cannot access from other devices
- Check firewall settings
- Ensure host is set to `0.0.0.0`
- Verify IP address is correct

### Scraping not working
- Ensure Chrome is installed
- Check internet connection
- Review browser console for errors

## Requirements

- Python 3.7+
- Google Chrome browser
- All dependencies from requirements.txt

## License

This utility is provided as-is for educational and personal use.

