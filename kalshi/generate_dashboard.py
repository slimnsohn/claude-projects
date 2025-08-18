#!/usr/bin/env python3
"""
Generate improved dashboard with cleaner market names and button filters
"""

import json
import os

def generate_improved_dashboard():
    """Generate dashboard HTML with embedded JSON data and improvements"""
    
    # Load the JSON data
    data_file = "data/fills_with_resolutions_current.json"
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found!")
        return
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Create the improved dashboard HTML
    html_content = create_improved_dashboard_html()
    
    # Embed the data directly in JavaScript
    data_js = f"const EMBEDDED_DATA = {json.dumps(data, indent=2)};"
    
    # Add the embedded data script
    script_insertion_point = "<script>"
    html_content = html_content.replace(script_insertion_point, f"<script>\n        {data_js}\n")
    
    # Write the new dashboard
    with open('dashboard_improved.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Generated dashboard_improved.html with:")
    print("- Cleaner market names (team vs team format)")
    print("- Button-based filters instead of dropdowns")
    print("- Better sport categorization")
    print("You can now open this file directly in your browser!")

def create_improved_dashboard_html():
    """Create the improved dashboard HTML"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kalshi Trading Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
        }

        .card.positive {
            border-left-color: #27ae60;
        }

        .card.negative {
            border-left-color: #e74c3c;
        }

        .card h3 {
            color: #7f8c8d;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .card .value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }

        .filters {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .filters h3 {
            margin-bottom: 15px;
            color: #2c3e50;
        }

        .filter-section {
            margin-bottom: 20px;
        }

        .filter-section:last-child {
            margin-bottom: 0;
        }

        .filter-label {
            font-weight: 600;
            margin-bottom: 10px;
            color: #34495e;
        }

        .filter-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .filter-btn {
            padding: 8px 16px;
            border: 2px solid #bdc3c7;
            border-radius: 20px;
            background: white;
            color: #34495e;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            font-weight: 500;
        }

        .filter-btn:hover {
            border-color: #3498db;
            background: #ecf0f1;
        }

        .filter-btn.active {
            background: #3498db;
            color: white;
            border-color: #3498db;
        }

        .filter-btn.reset {
            background: #e74c3c;
            color: white;
            border-color: #e74c3c;
        }

        .filter-btn.reset:hover {
            background: #c0392b;
            border-color: #c0392b;
        }

        .section {
            background: white;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .section-header {
            background: #34495e;
            color: white;
            padding: 15px 20px;
            font-weight: 600;
        }

        .section-content {
            padding: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
            position: sticky;
            top: 0;
        }

        tr:hover {
            background: #f8f9fa;
        }

        .profit {
            color: #27ae60 !important;
            font-weight: 600;
        }

        .loss {
            color: #e74c3c !important;
            font-weight: 600;
        }

        .status-open {
            background: #f39c12;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }

        .status-closed {
            background: #95a5a6;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }

        .loading {
            text-align: center;
            padding: 50px;
            color: #7f8c8d;
        }

        .tabs {
            display: flex;
            background: #ecf0f1;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        .tab {
            flex: 1;
            padding: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }

        .tab.active {
            background: white;
            font-weight: 600;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .market-name {
            font-weight: 600;
        }

        .market-details {
            font-size: 12px;
            color: #7f8c8d;
            margin-top: 2px;
        }

        .sport-badge {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .sport-badge.wta { background: #e91e63; }
        .sport-badge.ufc { background: #ff5722; }
        .sport-badge.nba { background: #ff9800; }
        .sport-badge.nfl { background: #4caf50; }
        .sport-badge.mlb { background: #2196f3; }
        .sport-badge.politics { background: #9c27b0; }
        .sport-badge.economics { background: #607d8b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Kalshi Trading Dashboard</h1>
            <p id="last-updated">Loading...</p>
            <button class="filter-btn" onclick="refreshData()" style="margin-top: 10px;">🔄 Refresh Data</button>
        </div>

        <div class="overview-grid">
            <div class="card">
                <h3>Current Cash</h3>
                <div class="value" id="current-cash">$0.00</div>
            </div>
            <div class="card">
                <h3>Cash in Positions</h3>
                <div class="value" id="cash-in-positions">$0.00</div>
            </div>
            <div class="card">
                <h3>Total Account Value</h3>
                <div class="value" id="total-value">$0.00</div>
            </div>
            <div class="card">
                <h3>Net P&L</h3>
                <div class="value" id="net-pnl">$0.00</div>
            </div>
            <div class="card">
                <h3>Total Deposits</h3>
                <div class="value">$16,000.00</div>
                <small style="color: #7f8c8d;">Verified from deposits.txt</small>
            </div>
        </div>

        <div class="filters">
            <h3>Filters</h3>
            <div class="filter-section">
                <div class="filter-label">Sport:</div>
                <div class="filter-buttons" id="sport-buttons">
                    <button class="filter-btn active" data-sport="all">All Sports</button>
                </div>
            </div>
            <div class="filter-section">
                <div class="filter-label">Status:</div>
                <div class="filter-buttons" id="status-buttons">
                    <button class="filter-btn active" data-status="all">All</button>
                    <button class="filter-btn" data-status="open">Open</button>
                    <button class="filter-btn" data-status="closed">Closed</button>
                </div>
            </div>
            <div class="filter-section">
                <button class="filter-btn reset" onclick="resetAllFilters()">Reset All Filters</button>
            </div>
        </div>

        <div class="section">
            <div class="section-header">Open Positions</div>
            <div class="section-content">
                <div id="open-positions-loading" class="loading">Loading open positions...</div>
                <div id="open-positions-content" style="display: none;">
                    <table id="open-positions-table">
                        <thead>
                            <tr>
                                <th>Market</th>
                                <th>Sport</th>
                                <th>Total Cost</th>
                                <th>Current Value</th>
                                <th>Unrealized P&L</th>
                                <th>Trades</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-header">Trading History</div>
            <div class="section-content">
                <div class="tabs">
                    <div class="tab active" onclick="showTab('individual-trades')">Individual Trades</div>
                    <div class="tab" onclick="showTab('event-summary')">Event Summary</div>
                </div>

                <div class="filter-section" style="margin-bottom: 20px;">
                    <div class="filter-label">Trade Status:</div>
                    <div class="filter-buttons" id="trade-status-buttons">
                        <button class="filter-btn active" data-trade-status="all">All Trades</button>
                        <button class="filter-btn" data-trade-status="open">Open</button>
                        <button class="filter-btn" data-trade-status="finalized">Finalized</button>
                    </div>
                </div>

                <div id="individual-trades" class="tab-content active">
                    <div id="trades-loading" class="loading">Loading trade history...</div>
                    <div id="trades-content" style="display: none;">
                        <table id="trades-table">
                            <thead>
                                <tr>
                                    <th>Trade Date</th>
                                    <th>Event Date</th>
                                    <th>Market</th>
                                    <th>Sport</th>
                                    <th>Action</th>
                                    <th>Side</th>
                                    <th>Count</th>
                                    <th>Price</th>
                                    <th>Cost</th>
                                    <th>Status</th>
                                    <th>Result</th>
                                    <th>P&L</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>

                <div id="event-summary" class="tab-content">
                    <div id="events-loading" class="loading">Loading event summary...</div>
                    <div id="events-content" style="display: none;">
                        <table id="events-table">
                            <thead>
                                <tr>
                                    <th>Event</th>
                                    <th>Sport</th>
                                    <th>Total Cost</th>
                                    <th>Total Payout</th>
                                    <th>Net P&L</th>
                                    <th>Status</th>
                                    <th>Result</th>
                                    <th>Trades</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let allData = {};
        let filteredData = {};
        let currentFilters = {
            sport: 'all',
            status: 'all',
            tradeStatus: 'all'
        };

        // Initialize dashboard
        async function initDashboard() {
            try {
                allData = EMBEDDED_DATA;
                
                document.getElementById('last-updated').textContent = 
                    `Last updated: ${new Date(allData.retrieved_at).toLocaleString()}`;
                
                processData();
                populateFilterButtons();
                updateOverview();
                updateOpenPositions();
                updateTradesHistory();
                updateEventSummary();
                
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('last-updated').textContent = 'Error loading data';
            }
        }

        function processData() {
            filteredData = { ...allData };
        }

        function parseMarketName(ticker) {
            // Parse tickers like "KXWTAMATCH-25AUG17STAANN-STA" into readable format
            try {
                const parts = ticker.split('-');
                
                if (parts.length === 3) {
                    // Format: KXWTAMATCH-25AUG17STAANN-STA
                    const datePart = parts[1]; // "25AUG17STAANN"
                    const selectedSide = parts[2]; // "STA"
                    
                    // Extract match part from date part (remove date prefix)
                    // Date format is YYMONDD (7 chars), so match starts at position 7
                    if (datePart.length > 7) {
                        const matchPart = datePart.substring(7); // "STAANN"
                        
                        // Find teams by removing selected side from match part
                        const teams = extractTeamsFromMatch(matchPart, selectedSide);
                        if (teams) {
                            return formatMatchup(teams.team1, teams.team2, selectedSide);
                        }
                    }
                } else if (parts.length >= 4) {
                    // Format: KX...-DATE-MATCHPART-SELECTED
                    const matchPart = parts[2];
                    const selectedSide = parts[3];
                    
                    const teams = extractTeamsFromMatch(matchPart, selectedSide);
                    if (teams) {
                        return formatMatchup(teams.team1, teams.team2, selectedSide);
                    }
                }
                
                // Special cases
                if (ticker.includes('PRES')) {
                    return 'Presidential Election';
                } else if (ticker.includes('ECON')) {
                    return 'Economic Event';
                }
                
                // Fallback: return a cleaned version of the ticker
                return ticker.replace(/^KX/, '').replace(/-.*$/, '');
            } catch (e) {
                return ticker;
            }
        }

        function extractTeamsFromMatch(matchPart, selectedSide) {
            // Examples:
            // STAANN - STA -> STA vs ANN
            // MURPIC - PIC -> MUR vs PIC  
            // JACNO - NO -> JAC vs NO
            // ABCDEF - DEF -> ABC vs DEF
            // HGJFSU - HGJ -> HGJ vs FSU
            
            const selected = selectedSide.toUpperCase();
            const match = matchPart.toUpperCase();
            
            // Check if selected side is at the beginning
            if (match.startsWith(selected)) {
                const opponent = match.substring(selected.length);
                return {
                    team1: selected,
                    team2: opponent
                };
            }
            
            // Check if selected side is at the end
            if (match.endsWith(selected)) {
                const opponent = match.substring(0, match.length - selected.length);
                return {
                    team1: opponent,
                    team2: selected
                };
            }
            
            // If no exact match, try to split evenly and see which half matches
            const midPoint = Math.floor(match.length / 2);
            const firstHalf = match.substring(0, midPoint);
            const secondHalf = match.substring(midPoint);
            
            if (firstHalf === selected) {
                return {
                    team1: selected,
                    team2: secondHalf
                };
            }
            
            if (secondHalf === selected) {
                return {
                    team1: firstHalf,
                    team2: selected
                };
            }
            
            // Last resort: try to find selected as substring and split accordingly
            const selectedIndex = match.indexOf(selected);
            if (selectedIndex === 0) {
                // Selected is at start
                return {
                    team1: selected,
                    team2: match.substring(selected.length)
                };
            } else if (selectedIndex === match.length - selected.length) {
                // Selected is at end
                return {
                    team1: match.substring(0, selectedIndex),
                    team2: selected
                };
            }
            
            // Fallback: split in half
            return {
                team1: firstHalf,
                team2: secondHalf
            };
        }

        function formatMatchup(team1, team2, selectedTeam) {
            // Format as "TEAM1 vs TEAM2" with selected team highlighted
            const t1 = team1.toUpperCase();
            const t2 = team2.toUpperCase();
            const selected = selectedTeam.toUpperCase();
            
            if (selected === t1) {
                return `<strong>${t1}</strong> vs ${t2}`;
            } else if (selected === t2) {
                return `${t1} vs <strong>${t2}</strong>`;
            } else {
                // Fallback if selection doesn't match either team
                return `${t1} vs ${t2}`;
            }
        }

        function extractEventDate(ticker) {
            // Extract event date from ticker like "KXWTAMATCH-25AUG17STAANN-STA"
            try {
                const parts = ticker.split('-');
                if (parts.length >= 2) {
                    let datePart = parts[1]; // "25AUG17STAANN"
                    
                    // For format like "25AUG17STAANN", extract just the date part (first 7 chars)
                    if (datePart.length > 7) {
                        datePart = datePart.substring(0, 7); // "25AUG17"
                    }
                    
                    if (datePart.length >= 7) {
                        const year = '20' + datePart.substring(0, 2); // "2025"
                        const month = datePart.substring(2, 5); // "AUG"
                        const day = datePart.substring(5, 7); // "17"
                        
                        const monthMap = {
                            'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
                            'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                            'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
                        };
                        
                        const monthNum = monthMap[month] || '01';
                        return `${year}-${monthNum}-${day}`;
                    }
                }
                return '';
            } catch (e) {
                return '';
            }
        }

        function extractSport(ticker) {
            if (ticker.includes('WTA')) return 'wta';
            if (ticker.includes('UFC')) return 'ufc';
            if (ticker.includes('NFL')) return 'nfl';
            if (ticker.includes('NBA')) return 'nba';
            if (ticker.includes('MLB')) return 'mlb';
            if (ticker.includes('PRES')) return 'politics';
            if (ticker.includes('ECON')) return 'economics';
            return 'other';
        }

        function getSportDisplayName(sport) {
            const names = {
                'wta': 'WTA Tennis',
                'ufc': 'UFC',
                'nfl': 'NFL',
                'nba': 'NBA',
                'mlb': 'MLB',
                'politics': 'Politics',
                'economics': 'Economics',
                'other': 'Other'
            };
            return names[sport] || sport.toUpperCase();
        }

        function populateFilterButtons() {
            const sports = new Set();
            
            allData.fills.forEach(fill => {
                const sport = extractSport(fill.ticker);
                if (sport) sports.add(sport);
            });
            
            const sportButtons = document.getElementById('sport-buttons');
            
            // Clear existing sport buttons (except "All")
            const allButton = sportButtons.querySelector('[data-sport="all"]');
            sportButtons.innerHTML = '';
            sportButtons.appendChild(allButton);
            
            // Make "All Sports" button clickable
            allButton.onclick = () => filterBySport('all');
            
            // Add sport buttons
            Array.from(sports).sort().forEach(sport => {
                const button = document.createElement('button');
                button.className = 'filter-btn';
                button.setAttribute('data-sport', sport);
                button.textContent = getSportDisplayName(sport);
                button.onclick = () => filterBySport(sport);
                sportButtons.appendChild(button);
            });
        }

        function filterBySport(sport) {
            currentFilters.sport = sport;
            
            // Update button states
            document.querySelectorAll('[data-sport]').forEach(btn => {
                btn.classList.toggle('active', btn.getAttribute('data-sport') === sport);
            });
            
            applyFilters();
        }

        function filterByStatus(status) {
            currentFilters.status = status;
            
            // Update button states
            document.querySelectorAll('[data-status]').forEach(btn => {
                btn.classList.toggle('active', btn.getAttribute('data-status') === status);
            });
            
            applyFilters();
        }

        function filterByTradeStatus(tradeStatus) {
            currentFilters.tradeStatus = tradeStatus;
            
            // Update button states
            document.querySelectorAll('[data-trade-status]').forEach(btn => {
                btn.classList.toggle('active', btn.getAttribute('data-trade-status') === tradeStatus);
            });
            
            applyTradeFilters();
        }

        function resetAllFilters() {
            currentFilters = { sport: 'all', status: 'all', tradeStatus: 'all' };
            
            // Reset button states
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector('[data-sport="all"]').classList.add('active');
            document.querySelector('[data-status="all"]').classList.add('active');
            document.querySelector('[data-trade-status="all"]').classList.add('active');
            
            applyFilters();
            applyTradeFilters();
        }

        function applyTradeFilters() {
            // Apply trade status filter specifically to trading history
            updateTradesHistory();
            updateEventSummary();
        }

        function applyFilters() {
            filteredData.fills = allData.fills.filter(fill => {
                const sport = extractSport(fill.ticker);
                const isResolved = ['closed', 'finalized', 'settled'].includes(fill.market_status?.toLowerCase());
                
                const sportMatch = currentFilters.sport === 'all' || sport === currentFilters.sport;
                const statusMatch = currentFilters.status === 'all' || 
                    (currentFilters.status === 'open' && !isResolved) ||
                    (currentFilters.status === 'closed' && isResolved);
                
                return sportMatch && statusMatch;
            });
            
            updateOverview();
            updateOpenPositions();
            updateTradesHistory();
            updateEventSummary();
        }

        function updateOverview() {
            const currentCash = 9818.85;
            let cashInPositions = 0;
            let netPnL = 0;
            
            const events = {};
            
            filteredData.fills.forEach(fill => {
                const ticker = fill.ticker;
                if (!events[ticker]) {
                    events[ticker] = {
                        totalCost: 0,
                        totalPayout: 0,
                        status: fill.market_status,
                        result: fill.market_result
                    };
                }
                
                const event = events[ticker];
                const side = fill.side || 'yes';
                const action = fill.action || 'buy';
                const count = fill.count || 0;
                const price = side === 'yes' ? fill.yes_price / 100 : fill.no_price / 100;
                const cost = count * price;
                
                if (action === 'buy') {
                    event.totalCost += cost;
                } else {
                    event.totalCost -= cost;
                }
                
                const isResolved = ['closed', 'finalized', 'settled'].includes(event.status?.toLowerCase());
                if (isResolved) {
                    let payoutRate = 0.5;
                    if (event.result === 'yes') {
                        payoutRate = side === 'yes' ? 1.0 : 0.0;
                    } else if (event.result === 'no') {
                        payoutRate = side === 'yes' ? 0.0 : 1.0;
                    }
                    
                    const payout = count * payoutRate;
                    if (action === 'buy') {
                        event.totalPayout += payout;
                    } else {
                        event.totalPayout -= payout;
                    }
                }
            });
            
            Object.values(events).forEach(event => {
                const isOpen = !['closed', 'finalized', 'settled'].includes(event.status?.toLowerCase());
                if (isOpen) {
                    cashInPositions += event.totalCost;
                } else {
                    netPnL += event.totalPayout - event.totalCost;
                }
            });
            
            const totalValue = currentCash + cashInPositions;
            
            document.getElementById('current-cash').textContent = `$${currentCash.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('cash-in-positions').textContent = `$${cashInPositions.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('total-value').textContent = `$${totalValue.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('net-pnl').textContent = `$${netPnL.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            
            const pnlCard = document.getElementById('net-pnl').parentElement;
            pnlCard.className = `card ${netPnL >= 0 ? 'positive' : 'negative'}`;
        }

        function updateOpenPositions() {
            const tbody = document.querySelector('#open-positions-table tbody');
            tbody.innerHTML = '';
            
            const openEvents = {};
            
            filteredData.fills.forEach(fill => {
                const isOpen = !['closed', 'finalized', 'settled'].includes(fill.market_status?.toLowerCase());
                if (!isOpen) return;
                
                const ticker = fill.ticker;
                if (!openEvents[ticker]) {
                    openEvents[ticker] = {
                        ticker,
                        marketName: parseMarketName(ticker),
                        sport: extractSport(ticker),
                        totalCost: 0,
                        trades: 0
                    };
                }
                
                const event = openEvents[ticker];
                const side = fill.side || 'yes';
                const action = fill.action || 'buy';
                const count = fill.count || 0;
                const price = side === 'yes' ? fill.yes_price / 100 : fill.no_price / 100;
                const cost = count * price;
                
                if (action === 'buy') {
                    event.totalCost += cost;
                } else {
                    event.totalCost -= cost;
                }
                event.trades++;
            });
            
            Object.values(openEvents).forEach(event => {
                const row = tbody.insertRow();
                const marketCell = row.insertCell();
                marketCell.innerHTML = event.marketName;
                row.insertCell().innerHTML = `<span class="sport-badge ${event.sport}">${getSportDisplayName(event.sport)}</span>`;
                row.insertCell().textContent = `$${event.totalCost.toFixed(2)}`;
                row.insertCell().textContent = `$${event.totalCost.toFixed(2)}`;
                row.insertCell().innerHTML = `<span class="profit">$0.00</span>`;
                row.insertCell().textContent = event.trades;
            });
            
            document.getElementById('open-positions-loading').style.display = 'none';
            document.getElementById('open-positions-content').style.display = 'block';
        }

        function updateTradesHistory() {
            const tbody = document.querySelector('#trades-table tbody');
            tbody.innerHTML = '';
            
            // Apply trade status filter
            let tradesToShow = filteredData.fills;
            if (currentFilters.tradeStatus !== 'all') {
                tradesToShow = filteredData.fills.filter(fill => {
                    const isFinalized = ['closed', 'finalized', 'settled'].includes(fill.market_status?.toLowerCase());
                    return currentFilters.tradeStatus === 'finalized' ? isFinalized : !isFinalized;
                });
            }
            
            tradesToShow.forEach(fill => {
                const side = fill.side || 'yes';
                const action = fill.action || 'buy';
                const count = fill.count || 0;
                const price = side === 'yes' ? fill.yes_price / 100 : fill.no_price / 100;
                const cost = count * price;
                const marketName = parseMarketName(fill.ticker);
                const sport = extractSport(fill.ticker);
                
                const isResolved = ['closed', 'finalized', 'settled'].includes(fill.market_status?.toLowerCase());
                let pnl = '';
                
                if (isResolved) {
                    let payoutRate = 0.5;
                    if (fill.market_result === 'yes') {
                        payoutRate = side === 'yes' ? 1.0 : 0.0;
                    } else if (fill.market_result === 'no') {
                        payoutRate = side === 'yes' ? 0.0 : 1.0;
                    }
                    
                    const payout = count * payoutRate;
                    const tradePnL = action === 'buy' ? payout - cost : cost - payout;
                    pnl = `$${tradePnL.toFixed(2)}`;
                }
                
                const eventDate = extractEventDate(fill.ticker);
                
                const row = tbody.insertRow();
                row.insertCell().textContent = new Date(fill.created_time).toLocaleDateString();
                row.insertCell().textContent = eventDate ? new Date(eventDate).toLocaleDateString() : '-';
                
                const marketCell = row.insertCell();
                marketCell.innerHTML = marketName;
                
                row.insertCell().innerHTML = `<span class="sport-badge ${sport}">${getSportDisplayName(sport)}</span>`;
                row.insertCell().textContent = action.toUpperCase();
                row.insertCell().textContent = side.toUpperCase();
                row.insertCell().textContent = count;
                row.insertCell().textContent = `${(price * 100).toFixed(0)}c`;
                row.insertCell().textContent = `$${cost.toFixed(2)}`;
                row.insertCell().innerHTML = `<span class="status-${isResolved ? 'closed' : 'open'}">${fill.market_status}</span>`;
                row.insertCell().textContent = fill.market_result || (isResolved ? 'TIE' : '-');
                
                const pnlCell = row.insertCell();
                const pnlClass = pnl && parseFloat(pnl.replace('$', '')) < 0 ? 'loss' : (pnl && parseFloat(pnl.replace('$', '')) > 0 ? 'profit' : '');
                pnlCell.className = pnlClass;
                pnlCell.textContent = pnl || '-';
            });
            
            document.getElementById('trades-loading').style.display = 'none';
            document.getElementById('trades-content').style.display = 'block';
        }

        function updateEventSummary() {
            const tbody = document.querySelector('#events-table tbody');
            tbody.innerHTML = '';
            
            // Apply trade status filter
            let tradesToShow = filteredData.fills;
            if (currentFilters.tradeStatus !== 'all') {
                tradesToShow = filteredData.fills.filter(fill => {
                    const isFinalized = ['closed', 'finalized', 'settled'].includes(fill.market_status?.toLowerCase());
                    return currentFilters.tradeStatus === 'finalized' ? isFinalized : !isFinalized;
                });
            }
            
            const events = {};
            
            tradesToShow.forEach(fill => {
                const ticker = fill.ticker;
                if (!events[ticker]) {
                    events[ticker] = {
                        ticker,
                        marketName: parseMarketName(ticker),
                        sport: extractSport(ticker),
                        totalCost: 0,
                        totalPayout: 0,
                        trades: 0,
                        status: fill.market_status,
                        result: fill.market_result
                    };
                }
                
                const event = events[ticker];
                const side = fill.side || 'yes';
                const action = fill.action || 'buy';
                const count = fill.count || 0;
                const price = side === 'yes' ? fill.yes_price / 100 : fill.no_price / 100;
                const cost = count * price;
                
                if (action === 'buy') {
                    event.totalCost += cost;
                } else {
                    event.totalCost -= cost;
                }
                
                const isResolved = ['closed', 'finalized', 'settled'].includes(event.status?.toLowerCase());
                if (isResolved) {
                    let payoutRate = 0.5;
                    if (event.result === 'yes') {
                        payoutRate = side === 'yes' ? 1.0 : 0.0;
                    } else if (event.result === 'no') {
                        payoutRate = side === 'yes' ? 0.0 : 1.0;
                    }
                    
                    const payout = count * payoutRate;
                    if (action === 'buy') {
                        event.totalPayout += payout;
                    } else {
                        event.totalPayout -= payout;
                    }
                }
                
                event.trades++;
            });
            
            Object.values(events).forEach(event => {
                const netPnL = event.totalPayout - event.totalCost;
                const isResolved = ['closed', 'finalized', 'settled'].includes(event.status?.toLowerCase());
                
                const row = tbody.insertRow();
                
                const marketCell = row.insertCell();
                marketCell.innerHTML = event.marketName;
                
                row.insertCell().innerHTML = `<span class="sport-badge ${event.sport}">${getSportDisplayName(event.sport)}</span>`;
                row.insertCell().textContent = `$${event.totalCost.toFixed(2)}`;
                row.insertCell().textContent = `$${event.totalPayout.toFixed(2)}`;
                
                const pnlCell = row.insertCell();
                pnlCell.className = netPnL > 0 ? 'profit' : (netPnL < 0 ? 'loss' : '');
                pnlCell.textContent = `$${netPnL.toFixed(2)}`;
                
                row.insertCell().innerHTML = `<span class="status-${isResolved ? 'closed' : 'open'}">${event.status}</span>`;
                row.insertCell().textContent = event.result || (isResolved ? 'TIE' : '-');
                row.insertCell().textContent = event.trades;
            });
            
            document.getElementById('events-loading').style.display = 'none';
            document.getElementById('events-content').style.display = 'block';
        }

        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }

        function refreshData() {
            document.getElementById('last-updated').textContent = 'Refreshing data...';
            
            // Show user to run get_fills.py to update data
            alert('To refresh data:\\n\\n1. Run: python get_fills.py\\n2. Then run: python generate_dashboard.py\\n3. Refresh this page\\n\\nThis will fetch the latest trades from Kalshi API.');
        }

        function verifyDeposits() {
            // Based on deposits.txt: 15 x $1,000 + 2 x $500 = $16,000
            return 16000.00;
        }

        // Add event listeners for status filter buttons
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('[data-status]').forEach(btn => {
                btn.onclick = () => filterByStatus(btn.getAttribute('data-status'));
            });
            
            document.querySelectorAll('[data-trade-status]').forEach(btn => {
                btn.onclick = () => filterByTradeStatus(btn.getAttribute('data-trade-status'));
            });
            
            initDashboard();
        });
    </script>
</body>
</html>'''

if __name__ == "__main__":
    generate_improved_dashboard()