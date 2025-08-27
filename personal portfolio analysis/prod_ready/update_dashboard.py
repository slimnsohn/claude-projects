#!/usr/bin/env python3

import json
import os

def update_html_dashboard():
    """Update the HTML dashboard to use real portfolio data"""
    
    # Load the real dashboard data
    dashboard_data_path = "dashboard_data.json"
    html_path = "portfolio_dashboard.html"
    
    if not os.path.exists(dashboard_data_path):
        print(f"Error: {dashboard_data_path} not found. Run 'python main.py' first.")
        return
    
    with open(dashboard_data_path, 'r') as f:
        real_data = json.load(f)
    
    # Read the HTML file
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find and replace the sample data
    start_marker = "const portfolioData = {"
    end_marker = "};"
    
    start_idx = html_content.find(start_marker)
    if start_idx == -1:
        print("Error: Could not find portfolio data in HTML file")
        return
    
    end_idx = html_content.find(end_marker, start_idx) + len(end_marker)
    
    # Create new data string
    new_data_js = f"const portfolioData = {json.dumps(real_data, indent=8)};"
    
    # Replace the data
    updated_html = (
        html_content[:start_idx] + 
        new_data_js + 
        html_content[end_idx:]
    )
    
    # Write back to file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"✓ Updated {html_path} with real portfolio data")
    print(f"Open {html_path} in your browser to view the dashboard")

if __name__ == "__main__":
    update_html_dashboard()