#!/usr/bin/env python3

import json
import os

def update_html_dashboard_with_prices():
    """Update the HTML dashboard to use real portfolio data with price integration"""
    
    # Load the real dashboard data and prices
    dashboard_data_path = "dashboard_data.json"
    prices_file_path = "current_prices.json"
    html_path = "portfolio_dashboard.html"
    
    if not os.path.exists(dashboard_data_path):
        print(f"Error: {dashboard_data_path} not found. Run 'python main_with_prices.py' first.")
        return
    
    with open(dashboard_data_path, 'r') as f:
        real_data = json.load(f)
    
    # Load prices if available
    prices = {}
    if os.path.exists(prices_file_path):
        with open(prices_file_path, 'r') as f:
            price_data = json.load(f)
            prices = price_data.get('prices', {})
        print(f"Loaded {len(prices)} ticker prices")
    else:
        print("No prices file found - dashboard will use placeholder prices")
    
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
    
    # Create new data string with price integration
    js_code = f"""const portfolioData = {json.dumps(real_data, indent=8)};

        // Current market prices
        const currentPrices = {json.dumps(prices, indent=8)};

        function getTickerPrice(ticker) {{
            // Return actual market price if available, otherwise default to $1
            return currentPrices[ticker] || 1.0;
        }}"""
    
    # Replace the old getTickerPrice function
    old_function_start = html_content.find("function getTickerPrice(ticker) {")
    if old_function_start != -1:
        old_function_end = html_content.find("}", old_function_start) + 1
        # Remove the old function since we're including it in the data section
        html_content = html_content[:old_function_start] + html_content[old_function_end:]
        
        # Adjust indices since we removed content
        start_idx = html_content.find(start_marker)
        end_idx = html_content.find(end_marker, start_idx) + len(end_marker)
    
    # Replace the data and function
    updated_html = (
        html_content[:start_idx] + 
        js_code + 
        html_content[end_idx:]
    )
    
    # Write back to file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"SUCCESS: Updated {html_path} with real portfolio data and current prices")
    
    if 'price_metadata' in real_data:
        metadata = real_data['price_metadata']
        print(f"Price data from: {metadata['timestamp']}")
        print(f"Price lookup success: {metadata['successful_lookups']}/{metadata['total_tickers']} tickers")
    
    print(f"Open {html_path} in your browser to view the dashboard with real-time pricing")

if __name__ == "__main__":
    update_html_dashboard_with_prices()