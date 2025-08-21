#!/usr/bin/env python3
"""
Simple HTTP server for the Fantasy Basketball Analysis web interface.
Run this script to serve the HTML interface locally.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_interface():
    """Start a local HTTP server for the web interface"""
    
    # Change to html_reports directory
    html_dir = Path(__file__).parent
    os.chdir(html_dir)
    
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"Fantasy Basketball Analysis Server")
    print(f"Starting server on port {PORT}...")
    print(f"Serving from: {html_dir}")
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            url = f"http://localhost:{PORT}"
            print(f"Server running at: {url}")
            print(f"Opening browser automatically...")
            print(f"Press Ctrl+C to stop server")
            
            # Open browser automatically
            webbrowser.open(url)
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\nServer stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} is already in use")
            print(f"Try a different port or stop other servers")
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    serve_interface()