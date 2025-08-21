// Fantasy Basketball Analysis App
class FantasyAnalysisApp {
    constructor() {
        this.players = {};
        this.insights = {};
        this.metadata = {};
        this.playerIndex = [];
        this.filteredPlayers = [];
        this.currentSearch = '';
        this.currentFilter = 'all';
        
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
            console.log('Loading data...');
            
            // Load all data files
            const [playersRes, insightsRes, metadataRes, indexRes] = await Promise.all([
                fetch('data/players.json'),
                fetch('data/insights.json'),
                fetch('data/metadata.json'),
                fetch('data/player_index.json')
            ]);
            
            const playersData = await playersRes.json();
            this.players = playersData.players;
            this.insights = await insightsRes.json();
            this.metadata = await metadataRes.json();
            this.playerIndex = await indexRes.json();
            
            // Initialize filtered players
            this.filteredPlayers = Object.entries(this.players);
            
            console.log(`Loaded ${Object.keys(this.players).length} players`);
            
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
                this.filterPlayers();
            });
        }
        
        // Filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                // Remove active from all chips
                document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                // Add active to clicked chip
                e.target.classList.add('active');
                
                this.currentFilter = e.target.dataset.filter;
                this.filterPlayers();
            });
        });
    }
    
    setupTabs() {
        const tabs = document.querySelectorAll('.nav-tab');
        const contents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetId = tab.dataset.tab;
                
                // Remove active class from all tabs and content
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                tab.classList.add('active');
                document.getElementById(targetId).classList.add('active');
            });
        });
    }
    
    filterPlayers() {
        let filtered = Object.entries(this.players);
        
        // Apply search filter
        if (this.currentSearch) {
            filtered = filtered.filter(([id, player]) => 
                player.player_name.toLowerCase().includes(this.currentSearch)
            );
        }
        
        // Apply category filter
        switch (this.currentFilter) {
            case 'drafted':
                filtered = filtered.filter(([id, player]) => 
                    player.yahoo_draft_history.length > 0
                );
                break;
            case 'high-value':
                filtered = filtered.filter(([id, player]) => 
                    player.value_analysis.value_score > 1.5
                );
                break;
            case 'consistent':
                filtered = filtered.filter(([id, player]) => 
                    player.seasons && Object.keys(player.seasons).length >= 5
                );
                break;
            case 'recent':
                filtered = filtered.filter(([id, player]) => 
                    player.seasons && Math.max(...Object.keys(player.seasons).map(Number)) >= 2022
                );
                break;
            // 'all' shows everything
        }
        
        this.filteredPlayers = filtered;
        this.renderPlayers();
        
        // Update result count
        const resultCount = document.getElementById('result-count');
        if (resultCount) {
            resultCount.textContent = `${filtered.length} players found`;
        }
    }
    
    renderPlayers() {
        const container = document.getElementById('player-grid');
        if (!container) return;
        
        if (this.filteredPlayers.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>No players found</h3>
                    <p>Try adjusting your search or filters</p>
                </div>
            `;
            return;
        }
        
        // Create table structure
        const tableHtml = `
            <div class="player-table-container">
                <table class="player-table">
                    <thead>
                        <tr>
                            <th class="sortable" data-sort="name">Player Name</th>
                            <th class="sortable" data-sort="seasons">Seasons</th>
                            <th class="sortable" data-sort="drafted">Drafted</th>
                            <th class="sortable" data-sort="avg_cost">Avg Cost</th>
                            <th class="sortable" data-sort="value_score">Value</th>
                            <th class="sortable" data-sort="pts">PTS</th>
                            <th class="sortable" data-sort="reb">REB</th>
                            <th class="sortable" data-sort="ast">AST</th>
                            <th class="sortable" data-sort="fg_pct">FG%</th>
                            <th class="sortable" data-sort="ft_pct">FT%</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.filteredPlayers.map(([id, player]) => 
                            this.createPlayerRow(id, player)
                        ).join('')}
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
        
        // Add sort listeners to headers
        container.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', () => {
                this.sortTable(header.dataset.sort);
            });
        });
    }
    
    createPlayerRow(playerId, player) {
        const seasons = Object.keys(player.seasons).length;
        const drafted = player.yahoo_draft_history.length;
        const avgPts = player.career_summary.pts_pg_avg || 0;
        const avgReb = player.career_summary.reb_pg_avg || 0;
        const avgAst = player.career_summary.ast_pg_avg || 0;
        const avgFgPct = player.career_summary.fg_pct_avg || 0;
        const avgFtPct = player.career_summary.ft_pct_avg || 0;
        
        const avgCost = player.value_analysis.avg_cost || 0;
        const valueScore = player.value_analysis.value_score || 0;
        const valueClass = valueScore > 1.5 ? 'value-good' : valueScore < 0.8 ? 'value-bad' : 'value-neutral';
        
        const yearsActive = player.career_summary.years_active || '';
        const isYahooOnly = player.data_source === 'yahoo_only';
        
        return `
            <tr class="player-row ${isYahooOnly ? 'yahoo-only' : ''}" data-player-id="${playerId}">
                <td class="player-name-cell">
                    ${player.player_name}
                    <div class="player-meta">
                        ${yearsActive}
                        ${isYahooOnly ? ' (Draft history only)' : ''}
                    </div>
                </td>
                <td class="stat-cell">${seasons || '-'}</td>
                <td class="stat-cell">${drafted > 0 ? `${drafted}x` : '-'}</td>
                <td class="stat-cell">${avgCost > 0 ? `$${avgCost.toFixed(0)}` : (drafted > 0 ? 'Snake' : '-')}</td>
                <td class="value-cell ${valueClass}">${valueScore > 0 ? valueScore.toFixed(1) : (drafted > 0 ? 'N/A' : '-')}</td>
                <td class="stat-cell">${avgPts > 0 ? avgPts.toFixed(1) : '-'}</td>
                <td class="stat-cell">${avgReb > 0 ? avgReb.toFixed(1) : '-'}</td>
                <td class="stat-cell">${avgAst > 0 ? avgAst.toFixed(1) : '-'}</td>
                <td class="stat-cell">${avgFgPct > 0 ? (avgFgPct * 100).toFixed(1) + '%' : '-'}</td>
                <td class="stat-cell">${avgFtPct > 0 ? (avgFtPct * 100).toFixed(1) + '%' : '-'}</td>
                <td class="expand-cell">
                    <button class="expand-btn">▼</button>
                </td>
            </tr>
            <tr class="player-details-row">
                <td colspan="11" class="player-details-cell">
                    ${this.createPlayerDetails(playerId, player)}
                </td>
            </tr>
        `;
    }
    
    createPlayerDetails(playerId, player) {
        return `
            <div class="details-grid">
                <div class="details-left">
                    ${this.createCareerSummary(player)}
                    ${this.createDraftHistory(player)}
                </div>
                <div class="details-right">
                    ${this.createSeasonStats(player)}
                </div>
            </div>
        `;
    }
    
    createCareerSummary(player) {
        return `
            <div class="details-section">
                <h4>Career Summary</h4>
                <div class="summary-stats">
                    <p><strong>Active Years:</strong> ${player.career_summary.years_active || 'N/A'}</p>
                    <p><strong>Total Games:</strong> ${player.career_summary.total_games || 0}</p>
                    <p><strong>Career Averages:</strong> 
                       ${(player.career_summary.pts_pg_avg || 0).toFixed(1)} PTS, 
                       ${(player.career_summary.reb_pg_avg || 0).toFixed(1)} REB, 
                       ${(player.career_summary.ast_pg_avg || 0).toFixed(1)} AST</p>
                    <p><strong>Shooting:</strong> 
                       ${((player.career_summary.fg_pct_avg || 0) * 100).toFixed(1)}% FG, 
                       ${((player.career_summary.ft_pct_avg || 0) * 100).toFixed(1)}% FT</p>
                </div>
            </div>
        `;
    }
    
    createDraftHistory(player) {
        if (player.yahoo_draft_history.length === 0) {
            return `
                <div class="details-section">
                    <h4>Draft History</h4>
                    <p style="color: #666; font-style: italic;">Never drafted in this league</p>
                </div>
            `;
        }
        
        const snakeDrafts = player.yahoo_draft_history.filter(d => d.draft_cost === 0);
        const auctionDrafts = player.yahoo_draft_history.filter(d => d.draft_cost > 0);
        
        return `
            <div class="details-section">
                <h4>Draft History</h4>
                <table class="draft-history-table">
                    <thead>
                        <tr>
                            <th>Year</th>
                            <th>Type</th>
                            <th>Cost/Pick</th>
                            <th>Team</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${player.yahoo_draft_history
                            .sort((a, b) => b.year - a.year)
                            .map(draft => `
                                <tr>
                                    <td>${draft.year}</td>
                                    <td>${draft.draft_cost > 0 ? 'Auction' : 'Snake'}</td>
                                    <td class="draft-cost">
                                        ${draft.draft_cost > 0 ? '$' + draft.draft_cost : '#' + draft.pick_number}
                                    </td>
                                    <td>${draft.fantasy_team}</td>
                                </tr>
                            `).join('')}
                    </tbody>
                </table>
                <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                    ${auctionDrafts.length > 0 ? 
                        `<p><strong>Auction years:</strong> Average cost $${player.value_analysis.avg_cost.toFixed(0)} • Value score ${player.value_analysis.value_score.toFixed(1)}</p>` : 
                        ''
                    }
                    <p><strong>Draft summary:</strong> ${snakeDrafts.length} snake drafts (2010-2015), ${auctionDrafts.length} auction drafts (2016-2024)</p>
                </div>
            </div>
        `;
    }
    
    createSeasonStats(player) {
        if (Object.keys(player.seasons).length === 0) {
            return `
                <div class="details-section">
                    <h4>Season Statistics</h4>
                    <p style="color: #666; font-style: italic;">No season data available</p>
                </div>
            `;
        }
        
        return `
            <div class="details-section">
                <h4>Season-by-Season Statistics</h4>
                <div style="overflow-x: auto;">
                    <table class="season-stats-table">
                        <thead>
                            <tr>
                                <th>Year</th>
                                <th>GP</th>
                                <th>Team</th>
                                <th>Pre-Rank</th>
                                <th>Cost</th>
                                <th>FG%</th>
                                <th>FT%</th>
                                <th>3PM</th>
                                <th>PTS</th>
                                <th>REB</th>
                                <th>AST</th>
                                <th>STL</th>
                                <th>BLK</th>
                                <th>TO</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(player.seasons)
                                .sort(([a], [b]) => b - a)
                                .map(([year, stats]) => {
                                    const preRank = stats.preseason_rank || '-';
                                    const draftCost = stats.draft_cost;
                                    const costDisplay = draftCost > 0 ? `$${draftCost}` : (draftCost === 0 ? 'Snake' : '-');
                                    
                                    return `
                                    <tr class="season-row">
                                        <td><strong>${year}</strong></td>
                                        <td>${stats.games_played}</td>
                                        <td>${stats.team}</td>
                                        <td class="rank-cell">${preRank !== '-' ? '#' + preRank : '-'}</td>
                                        <td class="cost-cell">${costDisplay}</td>
                                        <td>${(stats.fg_pct * 100).toFixed(1)}%</td>
                                        <td>${(stats.ft_pct * 100).toFixed(1)}%</td>
                                        <td>${stats.threepm_pg}</td>
                                        <td>${stats.pts_pg}</td>
                                        <td>${stats.reb_pg}</td>
                                        <td>${stats.ast_pg}</td>
                                        <td>${stats.stl_pg}</td>
                                        <td>${stats.blk_pg}</td>
                                        <td>${stats.to_pg}</td>
                                    </tr>
                                    `;
                                }).join('')
                        </tbody>
                    </table>
                </div>
            </div>
        `;
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
    
    sortTable(column) {
        const headers = document.querySelectorAll('.sortable');
        const currentHeader = document.querySelector(`[data-sort="${column}"]`);
        
        // Remove sort classes from all headers
        headers.forEach(h => {
            h.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Determine sort direction
        let isAscending = true;
        if (currentHeader.dataset.sortDir === 'asc') {
            isAscending = false;
        }
        
        // Add sort class to current header
        currentHeader.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        currentHeader.dataset.sortDir = isAscending ? 'asc' : 'desc';
        
        // Sort the filtered players
        this.filteredPlayers.sort(([idA, playerA], [idB, playerB]) => {
            let valueA, valueB;
            
            switch (column) {
                case 'name':
                    valueA = playerA.player_name.toLowerCase();
                    valueB = playerB.player_name.toLowerCase();
                    break;
                case 'seasons':
                    valueA = Object.keys(playerA.seasons).length;
                    valueB = Object.keys(playerB.seasons).length;
                    break;
                case 'drafted':
                    valueA = playerA.yahoo_draft_history.length;
                    valueB = playerB.yahoo_draft_history.length;
                    break;
                case 'avg_cost':
                    valueA = playerA.value_analysis.avg_cost || 0;
                    valueB = playerB.value_analysis.avg_cost || 0;
                    break;
                case 'value_score':
                    valueA = playerA.value_analysis.value_score || 0;
                    valueB = playerB.value_analysis.value_score || 0;
                    break;
                case 'pts':
                    valueA = playerA.career_summary.pts_pg_avg || 0;
                    valueB = playerB.career_summary.pts_pg_avg || 0;
                    break;
                case 'reb':
                    valueA = playerA.career_summary.reb_pg_avg || 0;
                    valueB = playerB.career_summary.reb_pg_avg || 0;
                    break;
                case 'ast':
                    valueA = playerA.career_summary.ast_pg_avg || 0;
                    valueB = playerB.career_summary.ast_pg_avg || 0;
                    break;
                case 'fg_pct':
                    valueA = playerA.career_summary.fg_pct_avg || 0;
                    valueB = playerB.career_summary.fg_pct_avg || 0;
                    break;
                case 'ft_pct':
                    valueA = playerA.career_summary.ft_pct_avg || 0;
                    valueB = playerB.career_summary.ft_pct_avg || 0;
                    break;
                default:
                    return 0;
            }
            
            if (typeof valueA === 'string') {
                return isAscending ? valueA.localeCompare(valueB) : valueB.localeCompare(valueA);
            } else {
                return isAscending ? valueA - valueB : valueB - valueA;
            }
        });
        
        // Re-render the table
        this.renderPlayers();
    }
    
    renderInsights() {
        // Render summary cards
        const summaryContainer = document.getElementById('summary-cards');
        if (summaryContainer) {
            summaryContainer.innerHTML = `
                <div class="summary-card">
                    <span class="summary-number">${this.metadata.total_players}</span>
                    <span class="summary-label">Total Players</span>
                </div>
                <div class="summary-card">
                    <span class="summary-number">${this.metadata.players_with_drafts}</span>
                    <span class="summary-label">Drafted Players</span>
                </div>
                <div class="summary-card">
                    <span class="summary-number">${this.insights.top_values.length}</span>
                    <span class="summary-label">Top Values</span>
                </div>
                <div class="summary-card">
                    <span class="summary-number">${this.insights.consistent_performers.length}</span>
                    <span class="summary-label">Consistent Players</span>
                </div>
            `;
        }
        
        // Render top values
        const topValuesContainer = document.getElementById('top-values-list');
        if (topValuesContainer && this.insights.top_values) {
            topValuesContainer.innerHTML = this.insights.top_values.map(player => `
                <li class="insight-item">
                    <span class="player-name">${player.player_name}</span>
                    <span class="insight-value value-good">
                        ${player.value_score.toFixed(1)} (Avg $${player.avg_cost})
                    </span>
                </li>
            `).join('');
        }
        
        // Render consistent performers
        const consistentContainer = document.getElementById('consistent-list');
        if (consistentContainer && this.insights.consistent_performers) {
            consistentContainer.innerHTML = this.insights.consistent_performers.map(player => `
                <li class="insight-item">
                    <span class="player-name">${player.player_name}</span>
                    <span class="insight-value value-neutral">
                        ${player.avg_pts} PPG (${player.seasons} seasons)
                    </span>
                </li>
            `).join('');
        }
        
        // Render biggest busts (if any)
        const bustsContainer = document.getElementById('busts-list');
        if (bustsContainer) {
            if (this.insights.biggest_busts && this.insights.biggest_busts.length > 0) {
                bustsContainer.innerHTML = this.insights.biggest_busts.map(player => `
                    <li class="insight-item">
                        <span class="player-name">${player.player_name}</span>
                        <span class="insight-value value-bad">
                            ${player.value_score.toFixed(1)} (Avg $${player.avg_cost})
                        </span>
                    </li>
                `).join('');
            } else {
                bustsContainer.innerHTML = `
                    <li class="insight-item">
                        <span class="player-name" style="color: #666; font-style: italic;">
                            No clear busts identified - all expensive players provided reasonable value
                        </span>
                    </li>
                `;
            }
        }
    }
    
    showError(message) {
        const container = document.getElementById('player-grid');
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3>Error</h3>
                    <p>${message}</p>
                </div>
            `;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FantasyAnalysisApp();
});