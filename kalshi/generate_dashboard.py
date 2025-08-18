#!/usr/bin/env python3
"""
Generate dashboard with embedded data to avoid CORS issues
"""

import json
import os

def generate_dashboard():
    """Generate dashboard HTML with embedded JSON data"""
    
    # Load the JSON data
    data_file = "data/fills_with_resolutions_current.json"
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found!")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Read the dashboard template
    with open('dashboard.html', 'r') as f:
        html_content = f.read()
    
    # Embed the data directly in JavaScript
    data_js = f"const EMBEDDED_DATA = {json.dumps(data, indent=2)};"
    
    # Replace the fetch call with embedded data
    old_init = """        async function initDashboard() {
            try {
                const response = await fetch('data/fills_with_resolutions_current.json');
                allData = await response.json();"""
    
    new_init = """        async function initDashboard() {
            try {
                allData = EMBEDDED_DATA;"""
    
    html_content = html_content.replace(old_init, new_init)
    
    # Add the embedded data script before the existing script
    script_insertion_point = "<script>"
    html_content = html_content.replace(script_insertion_point, f"<script>\n        {data_js}\n")
    
    # Write the new dashboard
    with open('dashboard_embedded.html', 'w') as f:
        f.write(html_content)
    
    print("Generated dashboard_embedded.html with embedded data")
    print("You can now open this file directly in your browser!")

if __name__ == "__main__":
    generate_dashboard()