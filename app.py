"""
Google Business Scraper - Web Application
Flask-based web interface for the scraper tools
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import threading
import json
from datetime import datetime

# Import scrapers
try:
    from google_maps_scraper import scrape_business_info
    from google_web_scraper import search_businesses_web
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    SCRAPERS_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Store scraping status
scraping_status = {
    'is_running': False,
    'progress': '',
    'results': [],
    'error': None
}


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/scrape', methods=['POST'])
def scrape():
    """API endpoint for scraping"""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({'error': 'Scraping is already in progress'}), 400
    
    data = request.json
    scraper_type = data.get('scraper_type', 'maps')
    business_name = data.get('business_name', '').strip()
    location = data.get('location', '').strip()
    max_results = data.get('max_results', '0')
    max_pages = data.get('max_pages', '8')
    export_excel = data.get('export_excel', True)
    export_csv = data.get('export_csv', True)
    headless = data.get('headless', False)
    output_folder = data.get('output_folder', 'excel_results')
    
    if not business_name:
        return jsonify({'error': 'Business name/query is required'}), 400
    
    # Reset status
    scraping_status = {
        'is_running': True,
        'progress': 'Starting scraper...',
        'results': [],
        'error': None
    }
    
    # Start scraping in background thread
    thread = threading.Thread(
        target=run_scraper,
        args=(scraper_type, business_name, location, max_results, max_pages, 
              export_excel, export_csv, headless, output_folder),
        daemon=True
    )
    thread.start()
    
    return jsonify({'message': 'Scraping started', 'status': 'running'})


def run_scraper(scraper_type, business_name, location, max_results, max_pages,
                export_excel, export_csv, headless, output_folder):
    """Run the scraper in background"""
    global scraping_status
    
    try:
        scraping_status['progress'] = f'Searching for: {business_name}'
        
        if scraper_type == 'maps':
            scraping_status['progress'] = f'Searching Google Maps for: {business_name} in {location}'
            
            results = scrape_business_info(
                business_name=business_name,
                location=location if location else None,
                headless=headless,
                export_excel=export_excel,
                export_leads=export_csv,
                output_folder=output_folder
            )
        else:  # web scraper
            max_results_int = None if max_results == '0' else int(max_results)
            max_pages_int = int(max_pages)
            query = f"{business_name} {location}" if location else business_name
            
            scraping_status['progress'] = f'Searching Google Web for: {query}'
            
            results = search_businesses_web(
                query=query,
                max_results=max_results_int,
                max_pages=max_pages_int,
                headless=headless,
                export_excel=export_excel,
                export_csv=export_csv,
                output_folder=output_folder
            )
        
        scraping_status['progress'] = f'Completed! Found {len(results)} results'
        scraping_status['results'] = results[:50]  # Limit to 50 for display
        scraping_status['is_running'] = False
        
    except Exception as e:
        scraping_status['error'] = str(e)
        scraping_status['progress'] = f'Error: {str(e)}'
        scraping_status['is_running'] = False


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_status)


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get scraping results"""
    return jsonify({
        'results': scraping_status.get('results', []),
        'total': len(scraping_status.get('results', []))
    })


@app.route('/api/files', methods=['GET'])
def list_files():
    """List available output files"""
    output_folder = request.args.get('folder', 'excel_results')
    
    if not os.path.exists(output_folder):
        return jsonify({'files': []})
    
    files = []
    for filename in os.listdir(output_folder):
        if filename.endswith(('.xlsx', '.csv')):
            filepath = os.path.join(output_folder, filename)
            file_info = {
                'name': filename,
                'size': os.path.getsize(filepath),
                'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
            }
            files.append(file_info)
    
    # Sort by modified date (newest first)
    files.sort(key=lambda x: x['modified'], reverse=True)
    
    return jsonify({'files': files})


@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download a file"""
    output_folder = request.args.get('folder', 'excel_results')
    filepath = os.path.join(output_folder, filename)
    
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    # Create output folder if it doesn't exist
    if not os.path.exists('excel_results'):
        os.makedirs('excel_results')
    
    # Create templates folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Starting Google Business Scraper Web Application...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

