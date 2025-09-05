#!/usr/bin/env python3
"""
Simple HTTP server to serve the dashboard with proper CORS headers
"""

import http.server
import socketserver
import os
import json
import subprocess
import sys
from urllib.parse import urlparse

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/dashboard_improved.html'
        elif self.path == '/refresh':
            self.handle_refresh()
            return
        return super().do_GET()
    
    def handle_refresh(self):
        """Handle refresh data request"""
        try:
            print("REFRESH REQUEST RECEIVED!")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Get absolute paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            python_dir = os.path.join(current_dir, 'python')
            get_fills_path = os.path.join(python_dir, 'get_fills.py')
            generate_dashboard_path = os.path.join(python_dir, 'generate_dashboard.py')
            
            print(f"Working directory: {python_dir}")
            print(f"Looking for scripts:")
            print(f"   - get_fills.py: {os.path.exists(get_fills_path)}")
            print(f"   - generate_dashboard.py: {os.path.exists(generate_dashboard_path)}")
            
            # Force use of system python to avoid SSL issues
            python_executable = "python"
            
            # Test system python availability
            try:
                result_test = subprocess.run([python_executable, "--version"], 
                                           capture_output=True, text=True, timeout=5)
                if result_test.returncode == 0:
                    # Test if it can import ssl
                    ssl_test = subprocess.run([python_executable, "-c", "import ssl; print('SSL OK')"], 
                                            capture_output=True, text=True, timeout=5)
                    if ssl_test.returncode == 0:
                        print(f"Using system Python with SSL support: {python_executable}")
                    else:
                        print(f"System Python SSL test failed: {ssl_test.stderr}")
                        raise Exception("System python SSL not working")
                else:
                    print(f"System Python test failed: {result_test.stderr}")
                    raise Exception("System python not working")
            except Exception as e:
                print(f"Failed to use system Python: {e}")
                print("WARNING: Falling back to current Python executable (may have SSL issues)")
                python_executable = sys.executable
                
            print(f"Final Python executable: {python_executable}")
            
            # Run get_fills.py to fetch latest data
            print("Fetching latest data from Kalshi API...")
            result1 = subprocess.run([python_executable, get_fills_path], 
                                   cwd=python_dir, capture_output=True, text=True, timeout=60)
            
            print(f"get_fills.py result: return code {result1.returncode}")
            if result1.stdout:
                print(f"   stdout: {result1.stdout[:200]}...")
            if result1.stderr:
                print(f"   stderr: {result1.stderr[:200]}...")
            
            if result1.returncode != 0:
                error_msg = {"error": "Failed to fetch data", "details": result1.stderr, "stdout": result1.stdout}
                self.wfile.write(json.dumps(error_msg).encode())
                return
            
            # Run generate_dashboard.py to update dashboard
            print("Regenerating dashboard...")
            result2 = subprocess.run([python_executable, generate_dashboard_path], 
                                   cwd=python_dir, capture_output=True, text=True, timeout=30)
            
            print(f"generate_dashboard.py result: return code {result2.returncode}")
            if result2.stdout:
                print(f"   stdout: {result2.stdout[:200]}...")
            if result2.stderr:
                print(f"   stderr: {result2.stderr[:200]}...")
            
            if result2.returncode != 0:
                error_msg = {"error": "Failed to generate dashboard", "details": result2.stderr}
                self.wfile.write(json.dumps(error_msg).encode())
                return
            
            response = {"success": True, "message": "Data refreshed successfully"}
            self.wfile.write(json.dumps(response).encode())
            print("Data refresh completed successfully")
            
        except subprocess.TimeoutExpired:
            self.send_response(408)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_msg = {"error": "Refresh timed out"}
            self.wfile.write(json.dumps(error_msg).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_msg = {"error": str(e)}
            self.wfile.write(json.dumps(error_msg).encode())

def serve_dashboard(port=8000):
    """Serve the dashboard on localhost"""
    os.chdir(os.path.dirname(__file__))
    
    try:
        with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
            print(f"Dashboard available at: http://localhost:{port}")
            print("Press Ctrl+C to stop the server")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")
    except OSError as e:
        if "Address already in use" in str(e) or "10048" in str(e):
            print(f"Error: Port {port} is already in use.")
            print("Please close any other applications using this port or restart your computer.")
            print(f"You can also try running the dashboard on a different port.")
        else:
            print(f"Error starting server: {e}")
        raise

if __name__ == "__main__":
    import sys
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8000.")
    serve_dashboard(port)