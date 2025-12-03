"""
Production server using Waitress WSGI server
Run this instead of app.py for production
"""
import os
import sys
from waitress import serve

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import app
from app import app

# Production configuration from environment variables
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', 80))
THREADS = int(os.getenv('WAITRESS_THREADS', 4))
CHANNEL_TIMEOUT = int(os.getenv('WAITRESS_CHANNEL_TIMEOUT', 300))  # 5 minutes for long scrapes

if __name__ == '__main__':
    print("=" * 60)
    print("Google Business Scraper - Production Server")
    print("=" * 60)
    print(f"Server: Waitress (Production WSGI)")
    print(f"Host: {HOST}")
    print(f"Port: {PORT}")
    print(f"Threads: {THREADS}")
    print(f"Channel Timeout: {CHANNEL_TIMEOUT}s")
    print(f"Access: http://{HOST}:{PORT}")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        # Start Waitress production server
        serve(
            app,
            host=HOST,
            port=PORT,
            threads=THREADS,
            channel_timeout=CHANNEL_TIMEOUT,
            cleanup_interval=30,
            asyncore_use_poll=True,
            connection_limit=100,
            cleanup_interval_seconds=30
        )
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

