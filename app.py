"""
Google Business Scraper - Web Application
Flask-based web interface for the scraper tools
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import threading
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd

# Import scrapers
try:
    from google_maps_scraper import scrape_business_info
    from google_web_scraper import search_businesses_web
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    SCRAPERS_AVAILABLE = False

app = Flask(__name__)

# Production-ready configuration
import os
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'change-this-secret-key-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty printing in production

# Store scraping status
scraping_status = {
    'is_running': False,
    'progress': '',
    'results': [],
    'error': None,
    'current_pair': 0,
    'total_pairs': 0
}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
UPLOAD_FOLDER = 'uploads'


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle Excel file upload for batch processing"""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({'error': 'Scraping is already in progress'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload Excel (.xlsx, .xls) or CSV (.csv) file'}), 400
    
    # Get other parameters
    scraper_type = request.form.get('scraper_type', 'maps')
    export_excel = request.form.get('export_excel', 'true').lower() == 'true'
    export_csv = request.form.get('export_csv', 'true').lower() == 'true'
    headless = request.form.get('headless', 'false').lower() == 'true'
    output_folder = request.form.get('output_folder', 'excel_results')
    
    try:
        # Create upload folder if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{filename}")
        file.save(filepath)
        
        # Parse Excel file
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
        except Exception as e:
            return jsonify({'error': f'Error reading file: {str(e)}'}), 400
        
        # Find Keyword and Location columns (case-insensitive)
        keyword_col = None
        location_col = None
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if 'keyword' in col_lower or 'query' in col_lower or 'business' in col_lower or 'name' in col_lower:
                if keyword_col is None:
                    keyword_col = col
            if 'location' in col_lower or 'city' in col_lower or 'place' in col_lower:
                if location_col is None:
                    location_col = col
        
        if keyword_col is None:
            return jsonify({'error': 'Could not find "Keyword" column in the file. Please ensure your file has a "Keyword" column.'}), 400
        
        # Extract pairs
        pairs = []
        for idx, row in df.iterrows():
            keyword = str(row[keyword_col]).strip() if pd.notna(row[keyword_col]) else ''
            location = str(row[location_col]).strip() if location_col and pd.notna(row[location_col]) else ''
            
            if keyword:  # Only add if keyword is not empty
                pairs.append({
                    'keyword': keyword,
                    'location': location if location else None
                })
        
        if not pairs:
            return jsonify({'error': 'No valid keyword-location pairs found in the file'}), 400
        
        # Reset status
        scraping_status = {
            'is_running': True,
            'progress': f'Starting batch processing for {len(pairs)} keyword-location pairs...',
            'results': [],
            'error': None,
            'current_pair': 0,
            'total_pairs': len(pairs)
        }
        
        # Start batch processing in background thread
        thread = threading.Thread(
            target=run_batch_scraper,
            args=(scraper_type, pairs, export_excel, export_csv, headless, output_folder, filepath),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'message': 'Batch processing started',
            'status': 'running',
            'total_pairs': len(pairs)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


def run_batch_scraper(scraper_type, pairs, export_excel, export_csv, headless, output_folder, uploaded_file_path):
    """Run batch scraper for multiple keyword-location pairs"""
    global scraping_status
    
    all_results = []
    
    try:
        for idx, pair in enumerate(pairs, 1):
            keyword = pair['keyword']
            location = pair['location']
            
            scraping_status['current_pair'] = idx
            scraping_status['progress'] = f'Processing pair {idx}/{len(pairs)}: "{keyword}" in "{location or "Any Location"}"'
            
            try:
                if scraper_type == 'maps':
                    results = scrape_business_info(
                        business_name=keyword,
                        location=location,
                        headless=headless,
                        export_excel=False,  # Don't export individual files
                        export_leads=False,  # Don't export individual files
                        output_folder=output_folder
                    )
                else:  # web scraper
                    query = f"{keyword} {location}" if location else keyword
                    from google_web_scraper import search_businesses_web
                    results = search_businesses_web(
                        query=query,
                        max_results=None,
                        max_pages=8,
                        headless=headless,
                        export_excel=False,
                        export_csv=False,
                        output_folder=output_folder
                    )
                
                # Add keyword and location to each result for tracking
                for result in results:
                    result['search_keyword'] = keyword
                    result['search_location'] = location or 'Any Location'
                
                all_results.extend(results)
                scraping_status['progress'] = f'Completed pair {idx}/{len(pairs)}: Found {len(results)} results. Total so far: {len(all_results)}'
                
            except Exception as e:
                scraping_status['progress'] = f'Error processing pair {idx}/{len(pairs)}: {str(e)}. Continuing...'
                continue
        
        # Merge and export all results
        if all_results:
            scraping_status['progress'] = f'Merging {len(all_results)} total results and exporting...'
            
            # Export merged results
            from google_maps_scraper import export_to_excel, export_leads_to_csv
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_excel:
                excel_filename = f"batch_results_{timestamp}.xlsx"
                export_to_excel(all_results, excel_filename, output_folder)
            
            if export_csv:
                csv_filename = f"batch_results_{timestamp}.csv"
                export_leads_to_csv(all_results, csv_filename, output_folder)
            
            scraping_status['progress'] = f'Batch processing completed! Processed {len(pairs)} pairs, found {len(all_results)} total results'
        else:
            scraping_status['progress'] = f'Batch processing completed, but no results were found for any of the {len(pairs)} pairs'
        
        scraping_status['results'] = all_results[:100]  # Limit to 100 for display
        scraping_status['is_running'] = False
        
        # Clean up uploaded file
        try:
            if os.path.exists(uploaded_file_path):
                os.remove(uploaded_file_path)
        except:
            pass
        
    except Exception as e:
        scraping_status['error'] = str(e)
        scraping_status['progress'] = f'Error in batch processing: {str(e)}'
        scraping_status['is_running'] = False


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
    # Create necessary folders if they don't exist
    if not os.path.exists('excel_results'):
        os.makedirs('excel_results')
    
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Production settings
    import os
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')  # Listen on all interfaces for server access
    PORT = int(os.getenv('FLASK_PORT', 80))  # Default to port 80 for server
    
    print("Starting Google Business Scraper Web Application...")
    print(f"Debug mode: {DEBUG}")
    print(f"Server listening on: http://{HOST}:{PORT}")
    print(f"Access the application at: http://localhost:{PORT} or http://<your-server-ip>:{PORT}")
    print("Press Ctrl+C to stop the server")
    print("\n⚠️  Note: Port 80 requires administrator/root privileges on most systems")
    print("   On Windows: Run as Administrator")
    print("   On Linux: Use 'sudo python app.py' or run as root")
    
    # In production, Gunicorn handles the app, so this only runs in development
    app.run(debug=DEBUG, host=HOST, port=PORT)

