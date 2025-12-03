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

# Import email marketing
try:
    from email_marketing import EmailMarketing, EmailTemplates
    EMAIL_MARKETING_AVAILABLE = True
except ImportError as e:
    print(f"Email marketing import error: {e}")
    EMAIL_MARKETING_AVAILABLE = False

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

# Store email sending status
email_status = {
    'is_sending': False,
    'progress': '',
    'results': None,
    'error': None
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


# ==================== Email Marketing Endpoints ====================

@app.route('/api/email/save-config', methods=['POST'])
def save_smtp_config():
    """Save SMTP configuration"""
    try:
        data = request.json
        config = {
            'smtp_server': data.get('smtp_server'),
            'smtp_port': data.get('smtp_port'),
            'smtp_username': data.get('smtp_username'),
            'from_email': data.get('from_email'),
            'from_name': data.get('from_name'),
            'saved_at': datetime.now().isoformat()
        }
        
        # Save to file (password not saved for security)
        config_file = 'email_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({'success': True, 'message': 'SMTP configuration saved (password not saved for security)'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/email/load-config', methods=['GET'])
def load_smtp_config():
    """Load saved SMTP configuration"""
    try:
        config_file = 'email_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            return jsonify({'success': True, 'config': config})
        else:
            return jsonify({'success': False, 'message': 'No saved configuration found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/email/test-connection', methods=['POST'])
def test_email_connection():
    """Test SMTP connection"""
    if not EMAIL_MARKETING_AVAILABLE:
        return jsonify({'error': 'Email marketing module not available'}), 500
    
    data = request.json
    email_marketing = EmailMarketing(
        smtp_server=data.get('smtp_server'),
        smtp_port=int(data.get('smtp_port', 587)),
        smtp_username=data.get('smtp_username'),
        smtp_password=data.get('smtp_password'),
        from_email=data.get('from_email'),
        from_name=data.get('from_name')
    )
    
    result = email_marketing.test_connection()
    return jsonify(result)


@app.route('/api/email/templates', methods=['GET'])
def get_email_templates():
    """Get available email templates"""
    if not EMAIL_MARKETING_AVAILABLE:
        return jsonify({'error': 'Email marketing module not available'}), 500
    
    templates = {
        'intro': EmailTemplates.get_template('intro'),
        'followup': EmailTemplates.get_template('followup'),
        'partnership': EmailTemplates.get_template('partnership'),
        'custom': EmailTemplates.get_template('custom')
    }
    
    return jsonify({'templates': templates})


@app.route('/api/email/send', methods=['POST'])
def send_email():
    """Send email to leads"""
    global email_status
    
    if not EMAIL_MARKETING_AVAILABLE:
        return jsonify({'error': 'Email marketing module not available'}), 500
    
    if email_status['is_sending']:
        return jsonify({'error': 'Email sending is already in progress'}), 400
    
    data = request.json
    
    # Get SMTP configuration
    smtp_config = {
        'smtp_server': data.get('smtp_server'),
        'smtp_port': int(data.get('smtp_port', 587)),
        'smtp_username': data.get('smtp_username'),
        'smtp_password': data.get('smtp_password'),
        'from_email': data.get('from_email'),
        'from_name': data.get('from_name', 'Google Business Scraper')
    }
    
    # Get email content
    template_name = data.get('template', 'custom')
    subject = data.get('subject', '')
    body_html = data.get('body_html', '')
    body_text = data.get('body_text', '')
    
    # Get leads (from file or provided data)
    leads_source = data.get('leads_source', 'file')  # 'file' or 'data'
    leads_file = data.get('leads_file')
    leads_data = data.get('leads', [])
    
    # Initialize email status
    email_status = {
        'is_sending': True,
        'progress': 'Starting email campaign...',
        'results': None,
        'error': None
    }
    
    # Start email sending in background thread
    thread = threading.Thread(
        target=run_email_campaign,
        args=(smtp_config, template_name, subject, body_html, body_text, leads_source, leads_file, leads_data),
        daemon=True
    )
    thread.start()
    
    return jsonify({'message': 'Email campaign started', 'status': 'sending'})


def run_email_campaign(smtp_config, template_name, subject, body_html, body_text, 
                       leads_source, leads_file, leads_data):
    """Run email campaign in background"""
    global email_status
    
    try:
        # Initialize email marketing
        email_marketing = EmailMarketing(**smtp_config)
        
        # Get leads
        if leads_source == 'file' and leads_file:
            # Load leads from file
            filepath = os.path.join('excel_results', leads_file)
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
            
            leads = df.to_dict('records')
        elif leads_source == 'data' and leads_data:
            # Use provided leads data (selected recipients)
            leads = leads_data
        else:
            # Use provided leads data (fallback)
            leads = leads_data if leads_data else []
        
        # Get template if using predefined template
        if template_name != 'custom':
            template = EmailTemplates.get_template(template_name)
            if not subject:
                subject = template['subject']
            if not body_html:
                body_html = template['html']
            if not body_text:
                body_text = template['text']
        
        # Add sender name to templates
        sender_name = smtp_config.get('from_name', 'Google Business Scraper')
        body_html = body_html.replace('{sender_name}', sender_name)
        if body_text:
            body_text = body_text.replace('{sender_name}', sender_name)
        
        # Send emails
        email_status['progress'] = f'Sending emails to {len(leads)} leads...'
        result = email_marketing.send_to_leads(
            leads=leads,
            subject_template=subject,
            body_html_template=body_html,
            body_text_template=body_text
        )
        
        email_status['progress'] = f'Completed! Sent {result.get("successful", 0)} emails successfully'
        email_status['results'] = result
        email_status['is_sending'] = False
        
    except Exception as e:
        email_status['error'] = str(e)
        email_status['progress'] = f'Error: {str(e)}'
        email_status['is_sending'] = False


@app.route('/api/email/status', methods=['GET'])
def get_email_status():
    """Get email sending status"""
    return jsonify(email_status)


@app.route('/api/email/get-recipients', methods=['GET'])
def get_recipients_from_file():
    """Get list of recipients from a file"""
    if not EMAIL_MARKETING_AVAILABLE:
        return jsonify({'error': 'Email marketing module not available'}), 500
    
    filename = request.args.get('file')
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    try:
        filepath = os.path.join('excel_results', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Read file
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Find email column (case-insensitive)
        email_col = None
        name_col = None
        company_col = None
        phone_col = None
        address_col = None
        website_col = None
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if 'email' in col_lower and email_col is None:
                email_col = col
            if ('name' in col_lower or 'company' in col_lower) and name_col is None:
                name_col = col
            if 'company' in col_lower and company_col is None:
                company_col = col
            if 'phone' in col_lower and phone_col is None:
                phone_col = col
            if 'address' in col_lower and address_col is None:
                address_col = col
            if 'website' in col_lower and website_col is None:
                website_col = col
        
        if not email_col:
            return jsonify({'error': 'No email column found in file'}), 400
        
        # Extract recipients
        recipients = []
        for idx, row in df.iterrows():
            email = str(row[email_col]).strip() if pd.notna(row[email_col]) else ''
            
            if email and email != 'N/A' and '@' in email:
                recipient = {
                    'email': email,
                    'name': str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else '',
                    'company': str(row[company_col]).strip() if company_col and pd.notna(row[company_col]) else (str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else ''),
                    'phone': str(row[phone_col]).strip() if phone_col and pd.notna(row[phone_col]) else '',
                    'address': str(row[address_col]).strip() if address_col and pd.notna(row[address_col]) else '',
                    'website': str(row[website_col]).strip() if website_col and pd.notna(row[website_col]) else ''
                }
                recipients.append(recipient)
        
        return jsonify({
            'success': True,
            'recipients': recipients,
            'total': len(recipients)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500


@app.route('/api/email/send-test', methods=['POST'])
def send_test_email():
    """Send a test email"""
    if not EMAIL_MARKETING_AVAILABLE:
        return jsonify({'error': 'Email marketing module not available'}), 500
    
    data = request.json
    test_email = data.get('test_email')
    
    if not test_email:
        return jsonify({'error': 'Test email address required'}), 400
    
    email_marketing = EmailMarketing(
        smtp_server=data.get('smtp_server'),
        smtp_port=int(data.get('smtp_port', 587)),
        smtp_username=data.get('smtp_username'),
        smtp_password=data.get('smtp_password'),
        from_email=data.get('from_email'),
        from_name=data.get('from_name', 'Google Business Scraper')
    )
    
    subject = data.get('subject', 'Test Email from Google Business Scraper')
    body_html = data.get('body_html', '<p>This is a test email.</p>')
    body_text = data.get('body_text', 'This is a test email.')
    
    result = email_marketing.send_email(
        to_email=test_email,
        subject=subject,
        body_html=body_html,
        body_text=body_text
    )
    
    return jsonify(result)


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
    PORT = int(os.getenv('FLASK_PORT', 5000))  # Default to port 5000 (can be changed via environment variable)
    
    print("Starting Google Business Scraper Web Application...")
    print(f"Debug mode: {DEBUG}")
    print(f"Server listening on: http://{HOST}:{PORT}")
    print(f"Access the application at: http://localhost:{PORT} or http://<your-server-ip>:{PORT}")
    print("Press Ctrl+C to stop the server")
    print("\n⚠️  Note: Port 80 requires administrator/root privileges on most systems")
    print("   On Windows: Run as Administrator")
    print("   On Linux: Use 'sudo python app.py' or run as root")
    print("\n📡 Public Access Information:")
    print("   - Current IP (172.31.40.145) is a PRIVATE IP (local network only)")
    print("   - To make it public, you need:")
    print("     1. Get your PUBLIC IP address (run check_public_ip.bat)")
    print("     2. Configure firewall/security group to allow port 80")
    print("     3. Configure router port forwarding (if behind NAT)")
    print("   - Then access via: http://YOUR_PUBLIC_IP")
    
    # In production, Gunicorn handles the app, so this only runs in development
    app.run(debug=DEBUG, host=HOST, port=PORT)

