#!/usr/bin/env python3
"""
Create complete standalone HTML with expandable player details and draft history.
"""

import json
import os

def create_complete_standalone():
    """Create standalone HTML with all features from original."""
    
    print("=== CREATING COMPLETE STANDALONE HTML ===\n")
    
    try:
        # Load all data files
        print("Loading data files...")
        
        with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
            players_data = json.load(f)
        print(f"  Players: {len(players_data.get('players', {}))} loaded")
        
        with open('html_reports/data/insights.json', 'r', encoding='utf-8') as f:
            insights_data = json.load(f)
        print(f"  Insights: {len(insights_data)} categories")
        
        with open('html_reports/data/metadata.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"  Metadata: {metadata.get('total_players', 'unknown')} players")
        
        with open('html_reports/data/player_index.json', 'r', encoding='utf-8') as f:
            player_index = json.load(f)
        print(f"  Index: {len(player_index)} entries")
        
        # Load CSS
        with open('html_reports/css/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Create complete JavaScript with expandable functionality
        js_content = '''
// Fantasy Basketball Analysis App - Complete Standalone Version
class FantasyAnalysisApp {
    constructor() {
        this.players = {};
        this.insights = {};
        this.metadata = {};
        this.playerIndex = [];
        this.filteredPlayers = [];
        this.currentSearch = '';
        this.currentFilter = 'all';
        this.sortField = 'player_name';
        this.sortDirection = 'asc';
        
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.setupTabs();
        this.renderPlayers();
        this.renderInsights();
    }
    
    async loadData() {
        try {
            console.log('Loading embedded data...');
            
            // Use embedded data instead of fetch
            if (window.EMBEDDED_DATA) {
                this.players = window.EMBEDDED_DATA.players;
                this.insights = window.EMBEDDED_DATA.insights;
                this.metadata = window.EMBEDDED_DATA.metadata;
                this.playerIndex = window.EMBEDDED_DATA.playerIndex;
                
                // Initialize filtered players
                this.filteredPlayers = Object.entries(this.players);
                
                console.log(`Loaded ${Object.keys(this.players).length} players from embedded data`);
            } else {
                throw new Error('No embedded data found');
            }
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load player data');
        }
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('player-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.currentSearch = e.target.value.toLowerCase();
                this.filterAndRenderPlayers();
            });
        }
        
        // Filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                // Remove active class from all chips
                document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked chip
                e.target.classList.add('active');
                
                // Update filter
                this.currentFilter = e.target.dataset.filter;
                this.filterAndRenderPlayers();
            });
        });
    }
    
    setupTabs() {
        // Tab functionality
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                // Skip if it's a link
                if (e.target.tagName === 'A') return;
                
                const targetTab = e.target.dataset.tab;
                if (!targetTab) return;
                
                // Remove active class from all tabs and content
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                e.target.classList.add('active');
                document.getElementById(targetTab).classList.add('active');
            });
        });
    }
    
    filterAndRenderPlayers() {
        const allPlayers = Object.entries(this.players);
        
        // Apply search filter
        let filtered = allPlayers;
        if (this.currentSearch) {
            filtered = filtered.filter(([id, player]) => 
                player.player_name && 
                player.player_name.toLowerCase().includes(this.currentSearch)
            );
        }
        
        // Apply category filter
        switch (this.currentFilter) {
            case 'drafted':
                filtered = filtered.filter(([id, player]) => 
                    player.yahoo_draft_history && player.yahoo_draft_history.length > 0
                );
                break;
            case 'high-value':
                filtered = filtered.filter(([id, player]) => 
                    player.value_analysis && player.value_analysis.value_score && player.value_analysis.value_score > 1.5
                );
                break;
            case 'consistent':
                filtered = filtered.filter(([id, player]) => 
                    player.career_summary && player.career_summary.total_seasons >= 5
                );
                break;
            case 'recent':
                filtered = filtered.filter(([id, player]) => 
                    player.seasons && Object.keys(player.seasons).some(year => parseInt(year) >= 2022)
                );
                break;
            default: // 'all'
                break;
        }
        
        this.filteredPlayers = filtered;
        this.renderPlayers();
    }
    
    sortPlayers(field) {
        if (this.sortField === field) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortField = field;
            this.sortDirection = 'asc';
        }
        this.renderPlayers();
    }
    
    renderPlayers() {
        const container = document.getElementById('player-grid');
        const countElement = document.getElementById('result-count');
        
        if (!container) return;
        
        if (this.filteredPlayers.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #666;">
                    <p>No players found matching your criteria.</p>
                </div>
            `;
            if (countElement) countElement.textContent = 'No players found';
            return;
        }
        
        // Update count
        if (countElement) {
            countElement.textContent = `${this.filteredPlayers.length} players found`;
        }
        
        // Sort players
        const sortedPlayers = this.filteredPlayers.sort(([aId, a], [bId, b]) => {
            let aVal, bVal;
            
            switch (this.sortField) {
                case 'player_name':
                    aVal = a.player_name || '';
                    bVal = b.player_name || '';
                    break;
                case 'draft_count':
                    aVal = a.yahoo_draft_history ? a.yahoo_draft_history.length : 0;
                    bVal = b.yahoo_draft_history ? b.yahoo_draft_history.length : 0;
                    break;
                case 'value_score':
                    aVal = a.value_analysis && a.value_analysis.value_score ? a.value_analysis.value_score : -999;
                    bVal = b.value_analysis && b.value_analysis.value_score ? b.value_analysis.value_score : -999;
                    break;
                case 'season_count':
                    aVal = a.career_summary ? a.career_summary.total_seasons : 0;
                    bVal = b.career_summary ? b.career_summary.total_seasons : 0;
                    break;
                case 'best_points':
                    aVal = a.career_summary ? a.career_summary.pts_pg_best : 0;
                    bVal = b.career_summary ? b.career_summary.pts_pg_best : 0;
                    break;
                default:
                    aVal = a.player_name || '';
                    bVal = b.player_name || '';
            }
            
            if (typeof aVal === 'string') {
                return this.sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            } else {
                return this.sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
            }
        });
        
        // Create table with expandable rows
        let tableHtml = `
            <div class="table-container">
                <table class="player-table">
                    <thead>
                        <tr>
                            <th class="sortable ${this.sortField === 'player_name' ? 'sort-' + this.sortDirection : ''}" 
                                onclick="app.sortPlayers('player_name')">Player</th>
                            <th>Position</th>
                            <th class="sortable ${this.sortField === 'draft_count' ? 'sort-' + this.sortDirection : ''}" 
                                onclick="app.sortPlayers('draft_count')">Drafted</th>
                            <th class="sortable ${this.sortField === 'value_score' ? 'sort-' + this.sortDirection : ''}" 
                                onclick="app.sortPlayers('value_score')">Value</th>
                            <th class="sortable ${this.sortField === 'season_count' ? 'sort-' + this.sortDirection : ''}" 
                                onclick="app.sortPlayers('season_count')">Seasons</th>
                            <th class="sortable ${this.sortField === 'best_points' ? 'sort-' + this.sortDirection : ''}" 
                                onclick="app.sortPlayers('best_points')">Best Pts</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        sortedPlayers.forEach(([playerId, player]) => {
            const playerName = player.player_name || `Player ${playerId}`;
            const position = player.position || '-';
            const draftCount = player.yahoo_draft_history ? player.yahoo_draft_history.length : 0;
            const valueScore = player.value_analysis && player.value_analysis.value_score ? player.value_analysis.value_score.toFixed(2) : '-';
            const seasonCount = player.career_summary ? player.career_summary.total_seasons : 0;
            const bestPoints = player.career_summary ? player.career_summary.pts_pg_best.toFixed(1) : '-';
            const yearsActive = player.career_summary ? player.career_summary.years_active : '';
            const isYahooOnly = player.data_source === 'yahoo_only';
            
            // Value color coding
            let valueClass = '';
            if (player.value_analysis && player.value_analysis.value_score) {
                if (player.value_analysis.value_score > 1.5) valueClass = 'value-high';
                else if (player.value_analysis.value_score < 0.8) valueClass = 'value-low';
                else valueClass = 'value-medium';
            }
            
            tableHtml += `
                <tr class="player-row ${isYahooOnly ? 'yahoo-only' : ''}" data-player-id="${playerId}">
                    <td class="player-name-cell">
                        <strong>${playerName}</strong>
                        <div class="player-meta">${yearsActive}${isYahooOnly ? ' (Draft history only)' : ''}</div>
                    </td>
                    <td>${position}</td>
                    <td>${draftCount > 0 ? draftCount + ' times' : 'Never'}</td>
                    <td class="${valueClass}">${valueScore}</td>
                    <td>${seasonCount}</td>
                    <td>${bestPoints}</td>
                    <td>
                        <span class="expand-btn">▼</span>
                    </td>
                </tr>
                <tr class="player-details-row">
                    <td colspan="7" class="player-details-cell">
                        ${this.renderPlayerDetails(playerId, player)}
                    </td>
                </tr>
            `;
        });
        
        tableHtml += `
                    </tbody>
                </table>
            </div>
        `;
        
        container.innerHTML = tableHtml;
        
        // Add click listeners to player rows
        container.querySelectorAll('.player-row').forEach(row => {
            row.addEventListener('click', () => {
                this.togglePlayerRow(row);
            });
        });
    }
    
    renderPlayerDetails(playerId, player) {
        const hasSeasons = player.seasons && Object.keys(player.seasons).length > 0;
        const hasDraftHistory = player.yahoo_draft_history && player.yahoo_draft_history.length > 0;
        
        let html = '<div class="player-details">';
        
        // Draft History Section
        if (hasDraftHistory) {
            html += `
                <div class="details-section">
                    <h4>📋 Draft History</h4>
                    <table class="draft-history-table">
                        <thead>
                            <tr>
                                <th>Year</th>
                                <th>Team</th>
                                <th>Pick #</th>
                                <th>Cost</th>
                                <th>Type</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            player.yahoo_draft_history.forEach(draft => {
                const cost = draft.is_snake_draft ? `Pick #${draft.pick_number}` : `$${draft.draft_cost}`;
                const type = draft.is_snake_draft ? 'Snake' : 'Auction';
                
                html += `
                    <tr>
                        <td>${draft.year}</td>
                        <td>${draft.fantasy_team}</td>
                        <td>#${draft.pick_number}</td>
                        <td>${cost}</td>
                        <td>${type}</td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
            
            // Value Analysis
            if (player.value_analysis && Object.keys(player.value_analysis).length > 0) {
                const va = player.value_analysis;
                html += `
                    <div class="details-section">
                        <h4>💰 Value Analysis</h4>
                        <div class="value-stats">
                            <div class="value-stat">
                                <span class="stat-label">Times Drafted:</span>
                                <span class="stat-value">${va.times_drafted || 0}</span>
                            </div>
                            <div class="value-stat">
                                <span class="stat-label">Average Cost:</span>
                                <span class="stat-value">$${va.avg_cost ? va.avg_cost.toFixed(1) : '0'}</span>
                            </div>
                            <div class="value-stat">
                                <span class="stat-label">Value Score:</span>
                                <span class="stat-value ${va.value_score > 1.5 ? 'value-high' : va.value_score < 0.8 ? 'value-low' : 'value-medium'}">
                                    ${va.value_score ? va.value_score.toFixed(2) : '-'}
                                </span>
                            </div>
                            <div class="value-stat">
                                <span class="stat-label">Cost Range:</span>
                                <span class="stat-value">${va.cost_range || '-'}</span>
                            </div>
                        </div>
                    </div>
                `;
            }
        }
        
        // Season Stats Section
        if (hasSeasons) {
            html += `
                <div class="details-section">
                    <h4>📊 Season Stats</h4>
                    <table class="season-stats-table">
                        <thead>
                            <tr>
                                <th>Season</th>
                                <th>Team</th>
                                <th>GP</th>
                                <th>PPG</th>
                                <th>RPG</th>
                                <th>APG</th>
                                <th>FG%</th>
                                <th>3PM</th>
                                <th>STL</th>
                                <th>BLK</th>
                                <th>TO</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            // Sort seasons by year (newest first)
            const seasons = Object.entries(player.seasons).sort(([a], [b]) => parseInt(b) - parseInt(a));
            
            seasons.forEach(([year, season]) => {
                html += `
                    <tr>
                        <td>${year}</td>
                        <td>${season.team || '-'}</td>
                        <td>${season.games_played || 0}</td>
                        <td>${season.pts_pg ? season.pts_pg.toFixed(1) : '-'}</td>
                        <td>${season.reb_pg ? season.reb_pg.toFixed(1) : '-'}</td>
                        <td>${season.ast_pg ? season.ast_pg.toFixed(1) : '-'}</td>
                        <td>${season.fg_pct ? (season.fg_pct * 100).toFixed(1) + '%' : '-'}</td>
                        <td>${season.threepm_pg ? season.threepm_pg.toFixed(1) : '-'}</td>
                        <td>${season.stl_pg ? season.stl_pg.toFixed(1) : '-'}</td>
                        <td>${season.blk_pg ? season.blk_pg.toFixed(1) : '-'}</td>
                        <td>${season.to_pg ? season.to_pg.toFixed(1) : '-'}</td>
                    </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
                </div>
            `;
            
            // Career Summary
            if (player.career_summary) {
                const cs = player.career_summary;
                html += `
                    <div class="details-section">
                        <h4>🏆 Career Summary</h4>
                        <div class="career-highlights">
                            <div class="highlight-stat">
                                <span class="stat-label">Total Games:</span>
                                <span class="stat-value">${cs.total_games || 0}</span>
                            </div>
                            <div class="highlight-stat">
                                <span class="stat-label">Best PPG:</span>
                                <span class="stat-value">${cs.pts_pg_best ? cs.pts_pg_best.toFixed(1) : '-'}</span>
                            </div>
                            <div class="highlight-stat">
                                <span class="stat-label">Best RPG:</span>
                                <span class="stat-value">${cs.reb_pg_best ? cs.reb_pg_best.toFixed(1) : '-'}</span>
                            </div>
                            <div class="highlight-stat">
                                <span class="stat-label">Best APG:</span>
                                <span class="stat-value">${cs.ast_pg_best ? cs.ast_pg_best.toFixed(1) : '-'}</span>
                            </div>
                        </div>
                    </div>
                `;
            }
        }
        
        if (!hasSeasons && !hasDraftHistory) {
            html += `
                <div class="details-section">
                    <p style="color: #666; font-style: italic;">No detailed stats or draft history available for this player.</p>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }
    
    togglePlayerRow(row) {
        const isExpanded = row.classList.contains('expanded');
        
        // Close all other expanded rows
        document.querySelectorAll('.player-row.expanded').forEach(r => {
            r.classList.remove('expanded');
        });
        
        // Toggle current row
        if (!isExpanded) {
            row.classList.add('expanded');
            
            // Scroll to row
            setTimeout(() => {
                row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        }
    }
    
    renderInsights() {
        this.renderSummaryCards();
        this.renderTopValues();
        this.renderConsistentPerformers();
        this.renderBiggestBusts();
    }
    
    renderSummaryCards() {
        const container = document.getElementById('summary-cards');
        if (!container || !this.metadata) return;
        
        const html = `
            <div class="summary-card">
                <div class="summary-number">${this.metadata.total_players || 0}</div>
                <div class="summary-label">Total Players</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">${this.metadata.players_with_drafts || 0}</div>
                <div class="summary-label">Drafted Players</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">${this.metadata.total_draft_entries || 0}</div>
                <div class="summary-label">Draft Picks</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">15</div>
                <div class="summary-label">Seasons</div>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    renderTopValues() {
        const container = document.getElementById('top-values-list');
        if (!container || !this.insights.top_values) return;
        
        const html = this.insights.top_values.map(player => `
            <li>
                <strong>${player.player_name}</strong>
                <span class="insight-value">${player.value_score.toFixed(2)}</span>
                <div class="insight-detail">${player.total_drafts} drafts, avg cost: $${player.avg_cost.toFixed(0)}</div>
            </li>
        `).join('');
        
        container.innerHTML = html;
    }
    
    renderConsistentPerformers() {
        const container = document.getElementById('consistent-list');
        if (!container || !this.insights.most_consistent) return;
        
        const html = this.insights.most_consistent.map(player => `
            <li>
                <strong>${player.player_name}</strong>
                <span class="insight-value">${player.variance.toFixed(1)} var</span>
                <div class="insight-detail">${player.seasons} seasons, avg: ${player.avg_points.toFixed(1)} pts</div>
            </li>
        `).join('');
        
        container.innerHTML = html;
    }
    
    renderBiggestBusts() {
        const container = document.getElementById('busts-list');
        if (!container || !this.insights.biggest_busts) return;
        
        const html = this.insights.biggest_busts.map(player => `
            <li>
                <strong>${player.player_name}</strong>
                <span class="insight-value">${player.value_score.toFixed(2)}</span>
                <div class="insight-detail">$${player.avg_cost.toFixed(0)} avg cost, ${player.avg_points.toFixed(1)} pts</div>
            </li>
        `).join('');
        
        container.innerHTML = html;
    }
    
    showError(message) {
        const container = document.getElementById('player-grid');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #d32f2f;">
                    <p><strong>Error:</strong> ${message}</p>
                    <p>Please check the console for more details.</p>
                </div>
            `;
        }
    }
}

// Global app instance
let app;

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    app = new FantasyAnalysisApp();
});
'''
        
        # Create the final HTML
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fantasy Basketball Analysis - Player Database</title>
    <style>
{css_content}

/* Additional styles for expandable functionality */
.sortable {{
    cursor: pointer;
    user-select: none;
}}

.sortable:hover {{
    background-color: #f0f0f0;
}}

.sort-asc::after {{
    content: ' ↑';
    color: #667eea;
}}

.sort-desc::after {{
    content: ' ↓';
    color: #667eea;
}}

.player-row {{
    cursor: pointer;
    transition: background-color 0.2s ease;
}}

.player-row:hover {{
    background-color: #f8f9fa;
}}

.player-row.expanded {{
    background-color: #e3f2fd;
}}

.player-row.yahoo-only {{
    background-color: #fafafa;
    font-style: italic;
}}

.player-row.yahoo-only .player-name-cell {{
    color: #666;
}}

.player-details-row {{
    display: none;
    background: #f8f9fa;
}}

.player-row.expanded + .player-details-row {{
    display: table-row;
}}

.player-details-cell {{
    padding: 20px;
    border-bottom: 1px solid #e9ecef;
}}

.expand-btn {{
    color: #667eea;
    font-size: 0.8em;
    transition: transform 0.3s ease;
}}

.player-row.expanded .expand-btn {{
    transform: rotate(180deg);
}}

.player-meta {{
    font-size: 0.8em;
    color: #666;
    font-weight: normal;
}}

.player-details {{
    max-width: 100%;
}}

.details-section {{
    margin-bottom: 30px;
}}

.details-section h4 {{
    color: #333;
    margin-bottom: 15px;
    font-size: 1.1em;
}}

.draft-history-table,
.season-stats-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 15px;
    font-size: 0.9em;
}}

.draft-history-table th,
.draft-history-table td,
.season-stats-table th,
.season-stats-table td {{
    padding: 8px 10px;
    text-align: center;
    border-bottom: 1px solid #e9ecef;
}}

.draft-history-table th,
.season-stats-table th {{
    background: #667eea;
    color: white;
    font-weight: 500;
}}

.value-stats,
.career-highlights {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 10px;
}}

.value-stat,
.highlight-stat {{
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background: white;
    border-radius: 5px;
    border-left: 4px solid #667eea;
}}

.stat-label {{
    font-weight: 500;
    color: #555;
}}

.stat-value {{
    font-weight: bold;
    color: #333;
}}

.value-high {{ color: #2e7d32; font-weight: bold; }}
.value-medium {{ color: #f57c00; }}
.value-low {{ color: #d32f2f; }}

.table-container {{
    overflow-x: auto;
    margin-top: 20px;
}}

.player-table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}

.player-table th,
.player-table td {{
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #eee;
}}

.player-table th {{
    background: #f5f5f5;
    font-weight: 600;
    color: #333;
}}

@media (max-width: 768px) {{
    .value-stats,
    .career-highlights {{
        grid-template-columns: 1fr;
    }}
    
    .season-stats-table {{
        font-size: 0.8em;
    }}
    
    .season-stats-table th,
    .season-stats-table td {{
        padding: 6px 5px;
    }}
}}

    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <!-- Page Header -->
            <div class="page-header">
                <h1>🏀 Fantasy Basketball Analysis</h1>
                <p>15-Year Player Database & Insights (2010-2024)</p>
            </div>
            
            <!-- Navigation Tabs -->
            <div class="nav-tabs">
                <button class="nav-tab active" data-tab="players-tab">Player Database</button>
                <button class="nav-tab" data-tab="insights-tab">Analysis & Insights</button>
                <a href="draft_results_standalone.html" class="nav-tab nav-link">📋 Draft Results by Year</a>
            </div>
            
            <!-- Players Tab Content -->
            <div id="players-tab" class="tab-content active">
                <!-- Search Section -->
                <div class="search-section">
                    <div class="search-box">
                        <input 
                            type="text" 
                            id="player-search" 
                            class="search-input" 
                            placeholder="Search players by name..."
                        >
                        <span class="search-icon">🔍</span>
                    </div>
                    
                    <div class="search-filters">
                        <span class="filter-chip active" data-filter="all">All Players</span>
                        <span class="filter-chip" data-filter="drafted">Drafted in League</span>
                        <span class="filter-chip" data-filter="high-value">High Value (>1.5)</span>
                        <span class="filter-chip" data-filter="consistent">Long Career (5+ seasons)</span>
                        <span class="filter-chip" data-filter="recent">Recent Players (2022+)</span>
                    </div>
                    
                    <div style="text-align: center; margin-top: 15px;">
                        <span id="result-count" style="color: #666; font-size: 0.9em;">Loading players...</span>
                    </div>
                </div>
                
                <!-- Player Table -->
                <div id="player-grid">
                    <div class="loading">Loading player data...</div>
                </div>
            </div>
            
            <!-- Insights Tab Content -->
            <div id="insights-tab" class="tab-content">
                <!-- Summary Cards -->
                <div id="summary-cards" class="summary-cards">
                    <div class="loading">Loading summary...</div>
                </div>
                
                <!-- Insights Grid -->
                <div class="insights-grid">
                    <!-- Top Values -->
                    <div class="insight-card">
                        <h3>🎯 Best Values</h3>
                        <p style="color: #666; margin-bottom: 15px; font-size: 0.9em;">
                            Players who provided the most production relative to their draft cost
                        </p>
                        <ul id="top-values-list" class="insight-list">
                            <li class="loading">Loading top values...</li>
                        </ul>
                    </div>
                    
                    <!-- Consistent Performers -->
                    <div class="insight-card">
                        <h3>📊 Most Consistent</h3>
                        <p style="color: #666; margin-bottom: 15px; font-size: 0.9em;">
                            Players with low variance in scoring, providing reliable production
                        </p>
                        <ul id="consistent-list" class="insight-list">
                            <li class="loading">Loading consistent performers...</li>
                        </ul>
                    </div>
                    
                    <!-- Biggest Disappointments -->
                    <div class="insight-card">
                        <h3>📉 Biggest Busts</h3>
                        <p style="color: #666; margin-bottom: 15px; font-size: 0.9em;">
                            Expensive players who underperformed relative to their draft cost
                        </p>
                        <ul id="busts-list" class="insight-list">
                            <li class="loading">Loading bust analysis...</li>
                        </ul>
                    </div>
                    
                    <!-- Draft Strategy Insights -->
                    <div class="insight-card">
                        <h3>💡 Key Insights</h3>
                        <div style="color: #666; font-size: 0.9em; line-height: 1.6;">
                            <h4 style="color: #333; margin: 15px 0 10px 0;">Player Value Patterns:</h4>
                            <ul style="padding-left: 20px;">
                                <li><strong>Value Score Formula:</strong> (Points + Rebounds + Assists - Turnovers) / Average Cost × 10</li>
                                <li><strong>High Value:</strong> Score > 1.5 indicates excellent value</li>
                                <li><strong>Poor Value:</strong> Score < 0.8 suggests overpaying</li>
                                <li><strong>Consistent Players:</strong> Low scoring variance over 3+ seasons</li>
                            </ul>
                            
                            <h4 style="color: #333; margin: 15px 0 10px 0;">Draft Strategy Recommendations:</h4>
                            <ul style="padding-left: 20px;">
                                <li>Target players with consistently high value scores across multiple seasons</li>
                                <li>Avoid paying premium prices for players with high variance</li>
                                <li>Look for players coming off "down" years who may be undervalued</li>
                                <li>Consider games played - availability is crucial for fantasy success</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <!-- Data Coverage Info -->
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 30px; text-align: center;">
                    <h4 style="color: #333; margin-bottom: 10px;">📈 Data Coverage</h4>
                    <p style="color: #666; font-size: 0.9em;">
                        Analysis based on 15 consecutive seasons (2010-2024) • 
                        2,376+ draft picks • 233 mapped players • 96.3% mapping accuracy
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Embed all data directly in the HTML
        console.log('Setting up embedded data...');
        
        window.EMBEDDED_DATA = {{
            players: {json.dumps(players_data['players'], separators=(',', ':'))},
            insights: {json.dumps(insights_data, separators=(',', ':'))},
            metadata: {json.dumps(metadata, separators=(',', ':'))},
            playerIndex: {json.dumps(player_index, separators=(',', ':'))}
        }};
        
        console.log('Embedded data ready. Players:', Object.keys(window.EMBEDDED_DATA.players).length);
        
        {js_content}
    </script>
</body>
</html>'''

        # Write the file
        output_file = 'html_reports/standalone_complete.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Complete standalone HTML created: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"Error creating complete standalone HTML: {e}")
        return False

if __name__ == "__main__":
    create_complete_standalone()