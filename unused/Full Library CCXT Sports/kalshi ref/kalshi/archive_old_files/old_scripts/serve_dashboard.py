#!/usr/bin/env python3
"""
Simple HTTP server to serve the dashboard with proper CORS headers
"""

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/dashboard.html'
        return super().do_GET()

def serve_dashboard(port=8000):
    """Serve the dashboard on localhost"""
    os.chdir(os.path.dirname(__file__))
    
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        print(f"Dashboard available at: http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    serve_dashboard()