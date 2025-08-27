#!/usr/bin/env python3

import json
import os
from csv_parser import parse_all_portfolio_csvs
from data_model import load_ref_data

def create_raw_data_report():
    """Create a detailed report showing all parsed data for verification"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    ref_folder = os.path.join(parent_dir, "ref_data")
    account_data_folder = os.path.join(parent_dir, "account data")
    
    # Load reference data
    ref_data = load_ref_data(ref_folder)
    
    # Parse all holdings
    holdings = parse_all_portfolio_csvs(account_data_folder, ref_data)
    
    # Create detailed report
    report = {
        "summary": {
            "total_holdings": len(holdings),
            "total_accounts": len(ref_data),
            "files_processed": []
        },
        "by_file": {},
        "by_account": {},
        "by_brokerage": {},
        "by_owner": {},
        "all_holdings": []
    }
    
    # Track which files were processed
    for filename in os.listdir(account_data_folder):
        if filename.endswith('.csv'):
            report["summary"]["files_processed"].append(filename)
    
    # Group holdings by various dimensions
    for holding in holdings:
        # Use the owner and brokerage that were already correctly extracted during parsing
        owner = holding.owner
        brokerage = holding.brokerage
        
        # Convert holding to dict for JSON serialization
        holding_dict = {
            "account_id": holding.account_id,
            "account_name": holding.account_name,
            "ticker": holding.ticker,
            "shares": holding.shares,
            "market_value": holding.market_value,
            "account_type": holding.account_type,
            "tax_type": holding.tax_type,
            "asset_class": holding.asset_class,
            "owner": owner,
            "brokerage": brokerage
        }
        
        report["all_holdings"].append(holding_dict)
        
        # Group by account
        if holding.account_id not in report["by_account"]:
            report["by_account"][holding.account_id] = {
                "account_name": holding.account_name,
                "account_type": holding.account_type,
                "tax_type": holding.tax_type,
                "holdings": [],
                "total_value": 0
            }
        report["by_account"][holding.account_id]["holdings"].append(holding_dict)
        report["by_account"][holding.account_id]["total_value"] += holding.market_value
        
        # Group by brokerage
        if brokerage not in report["by_brokerage"]:
            report["by_brokerage"][brokerage] = {
                "total_value": 0,
                "accounts": set(),
                "holdings": []
            }
        report["by_brokerage"][brokerage]["holdings"].append(holding_dict)
        report["by_brokerage"][brokerage]["total_value"] += holding.market_value
        report["by_brokerage"][brokerage]["accounts"].add(holding.account_id)
        
        # Group by owner
        if owner not in report["by_owner"]:
            report["by_owner"][owner] = {
                "total_value": 0,
                "accounts": set(),
                "holdings": []
            }
        report["by_owner"][owner]["holdings"].append(holding_dict)
        report["by_owner"][owner]["total_value"] += holding.market_value
        report["by_owner"][owner]["accounts"].add(holding.account_id)
    
    # Convert sets to lists for JSON serialization
    for brokerage_data in report["by_brokerage"].values():
        brokerage_data["accounts"] = list(brokerage_data["accounts"])
    
    for owner_data in report["by_owner"].values():
        owner_data["accounts"] = list(owner_data["accounts"])
    
    return report

def generate_html_report():
    """Generate an HTML report for raw data verification"""
    
    report = create_raw_data_report()
    
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Raw Data Verification</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; }
        .summary { background: #f5f5f5; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f0f0f0; }
        .currency { text-align: right; }
        .file-list { list-style-type: none; }
        .file-list li { background: #e8f4f8; margin: 5px 0; padding: 5px; }
    </style>
</head>
<body>
    <h1>Portfolio Raw Data Verification Report</h1>
    
    <div class="section summary">
        <h2>Summary</h2>
        <p><strong>Total Holdings:</strong> {total_holdings}</p>
        <p><strong>Total Accounts:</strong> {total_accounts}</p>
        <p><strong>Files Processed:</strong></p>
        <ul class="file-list">
""".format(
        total_holdings=report["summary"]["total_holdings"],
        total_accounts=report["summary"]["total_accounts"]
    )
    
    for filename in report["summary"]["files_processed"]:
        html += f"            <li>{filename}</li>\n"
    
    html += """
        </ul>
    </div>
    
    <div class="section">
        <h2>By Owner</h2>
        <table>
            <tr><th>Owner</th><th>Total Value</th><th>Accounts</th><th>Holdings Count</th></tr>
"""
    
    for owner, data in report["by_owner"].items():
        html += f"""
            <tr>
                <td>{owner}</td>
                <td class="currency">${data['total_value']:,.2f}</td>
                <td>{', '.join(data['accounts'])}</td>
                <td>{len(data['holdings'])}</td>
            </tr>
"""
    
    html += """
        </table>
    </div>
    
    <div class="section">
        <h2>By Brokerage</h2>
        <table>
            <tr><th>Brokerage</th><th>Total Value</th><th>Accounts</th><th>Holdings Count</th></tr>
"""
    
    for brokerage, data in report["by_brokerage"].items():
        html += f"""
            <tr>
                <td>{brokerage}</td>
                <td class="currency">${data['total_value']:,.2f}</td>
                <td>{', '.join(data['accounts'])}</td>
                <td>{len(data['holdings'])}</td>
            </tr>
"""
    
    html += """
        </table>
    </div>
    
    <div class="section">
        <h2>By Account</h2>
        <table>
            <tr><th>Account ID</th><th>Account Name</th><th>Type</th><th>Tax Type</th><th>Total Value</th><th>Holdings Count</th></tr>
"""
    
    for account_id, data in sorted(report["by_account"].items()):
        html += f"""
            <tr>
                <td>{account_id}</td>
                <td>{data['account_name']}</td>
                <td>{data['account_type']}</td>
                <td>{data['tax_type']}</td>
                <td class="currency">${data['total_value']:,.2f}</td>
                <td>{len(data['holdings'])}</td>
            </tr>
"""
    
    html += """
        </table>
    </div>
    
    <div class="section">
        <h2>All Holdings Detail</h2>
        <table>
            <tr>
                <th>Owner</th><th>Brokerage</th><th>Account</th><th>Ticker</th>
                <th>Shares</th><th>Market Value</th><th>Account Type</th><th>Tax Type</th>
            </tr>
"""
    
    for holding in sorted(report["all_holdings"], key=lambda x: (x["owner"], x["brokerage"], x["account_name"], x["ticker"])):
        html += f"""
            <tr>
                <td>{holding['owner']}</td>
                <td>{holding['brokerage']}</td>
                <td>{holding['account_name']}</td>
                <td>{holding['ticker']}</td>
                <td>{holding['shares']:,.2f}</td>
                <td class="currency">${holding['market_value']:,.2f}</td>
                <td>{holding['account_type']}</td>
                <td>{holding['tax_type']}</td>
            </tr>
"""
    
    html += """
        </table>
    </div>
    
</body>
</html>
"""
    
    return html

if __name__ == "__main__":
    try:
        # Generate JSON report
        report = create_raw_data_report()
        with open("raw_data_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print("Generated raw_data_report.json")
        
        # Generate HTML report
        html = generate_html_report()
        with open("raw_data_verification.html", "w", encoding='utf-8') as f:
            f.write(html)
        print("Generated raw_data_verification.html")
        
        print(f"\nQuick Summary:")
        print(f"Total Holdings: {report['summary']['total_holdings']}")
        print(f"Files Processed: {', '.join(report['summary']['files_processed'])}")
        print(f"Owners: {', '.join(report['by_owner'].keys())}")
        print(f"Brokerages: {', '.join(report['by_brokerage'].keys())}")
        
    except Exception as e:
        print(f"Error: {e}")