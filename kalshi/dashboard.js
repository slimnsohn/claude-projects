// Kalshi PNL Dashboard JavaScript

let currentData = null;
let pnlChart = null;
let winRateChart = null;

// File upload handler
document.getElementById('dataFile').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        loadFile(file);
    }
});

function showStatus(message, type = 'success') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';
    
    setTimeout(() => {
        status.style.display = 'none';
    }, 5000);
}

function showError(message) {
    showStatus(message, 'error');
}

async function loadFile(file) {
    try {
        showStatus('Loading file...', 'info');
        
        const text = await file.text();
        let data;
        
        if (file.name.endsWith('.json')) {
            data = JSON.parse(text);
        } else if (file.name.endsWith('.csv')) {
            // For CSV, we'll parse it as trades data
            data = parseCSV(text);
        } else {
            throw new Error('Unsupported file format. Please use JSON or CSV.');
        }
        
        currentData = data;
        await processAndDisplayData(data);
        
        document.getElementById('refreshBtn').disabled = false;
        showStatus('Data loaded successfully!');
        
    } catch (error) {
        console.error('Error loading file:', error);
        showError(`Error loading file: ${error.message}`);
    }
}

function parseCSV(csvText) {
    // Simple CSV parser for Kalshi data
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    
    const trades = [];
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        const trade = {};
        headers.forEach((header, index) => {
            trade[header] = values[index]?.trim();
        });
        trades.push(trade);
    }
    
    return { fills: trades };
}

async function processAndDisplayData(data) {
    try {
        // Process the data to calculate PNL
        const analysis = await calculatePNL(data);
        
        // Display the results
        displayMetrics(analysis.summary);
        displayCharts(analysis);
        displayTables(analysis);
        
        // Show dashboard
        document.getElementById('loading').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        
    } catch (error) {
        console.error('Error processing data:', error);
        showError(`Error processing data: ${error.message}`);
    }
}

async function calculatePNL(data) {
    // Extract fills/trades data
    let trades = [];
    
    if (data.fills && Array.isArray(data.fills)) {
        trades = data.fills;
    } else if (Array.isArray(data)) {
        trades = data;
    } else {
        throw new Error('No trades data found in the file');
    }
    
    if (trades.length === 0) {
        throw new Error('No trades found in the data');
    }
    
    // Process trades and calculate PNL
    const processedTrades = trades.map(trade => {
        const processed = { ...trade };
        
        // Convert numeric fields
        const numericFields = ['cost', 'payout', 'price', 'size', 'fees'];
        numericFields.forEach(field => {
            if (processed[field]) {
                processed[field] = parseFloat(processed[field]) || 0;
            }
        });
        
        // Calculate PNL
        if (processed.cost && processed.payout) {
            processed.gross_pnl = processed.payout - processed.cost;
        } else if (processed.price && processed.size) {
            processed.gross_pnl = processed.price * processed.size;
        } else {
            processed.gross_pnl = 0;
        }
        
        processed.fees = processed.fees || 0;
        processed.net_pnl = processed.gross_pnl - processed.fees;
        processed.is_win = processed.net_pnl > 0;
        
        // Parse date
        const dateFields = ['created_at', 'timestamp', 'ts', 'date'];
        for (const field of dateFields) {
            if (processed[field]) {
                processed.date = new Date(processed[field]);
                break;
            }
        }
        
        return processed;
    }).filter(trade => !isNaN(trade.net_pnl));
    
    // Calculate summary metrics
    const summary = calculateSummaryMetrics(processedTrades);
    
    // Calculate daily PNL
    const dailyPnl = calculateDailyPNL(processedTrades);
    
    // Calculate position PNL
    const positionPnl = calculatePositionPNL(processedTrades);
    
    // Get best/worst trades
    const bestWorst = getBestWorstTrades(processedTrades);
    
    return {
        summary,
        daily_pnl: dailyPnl,
        position_pnl: positionPnl,
        best_worst: bestWorst,
        trades: processedTrades
    };
}

function calculateSummaryMetrics(trades) {
    const totalTrades = trades.length;
    const totalPnl = trades.reduce((sum, trade) => sum + trade.net_pnl, 0);
    const grossPnl = trades.reduce((sum, trade) => sum + trade.gross_pnl, 0);
    
    const wins = trades.filter(trade => trade.is_win);
    const losses = trades.filter(trade => !trade.is_win && trade.net_pnl < 0);
    
    const winCount = wins.length;
    const lossCount = losses.length;
    const winRate = totalTrades > 0 ? (winCount / totalTrades) * 100 : 0;
    
    const avgWin = winCount > 0 ? wins.reduce((sum, trade) => sum + trade.net_pnl, 0) / winCount : 0;
    const avgLoss = lossCount > 0 ? losses.reduce((sum, trade) => sum + trade.net_pnl, 0) / lossCount : 0;
    
    const profitFactor = (lossCount > 0 && avgLoss !== 0) ? Math.abs(wins.reduce((sum, trade) => sum + trade.net_pnl, 0) / losses.reduce((sum, trade) => sum + trade.net_pnl, 0)) : Infinity;
    
    return {
        total_trades: totalTrades,
        total_pnl: totalPnl,
        gross_pnl: grossPnl,
        win_count: winCount,
        loss_count: lossCount,
        win_rate: winRate,
        avg_win: avgWin,
        avg_loss: avgLoss,
        profit_factor: profitFactor
    };
}

function calculateDailyPNL(trades) {
    const dailyMap = new Map();
    
    trades.forEach(trade => {
        if (trade.date) {
            const dateStr = trade.date.toISOString().split('T')[0];
            if (!dailyMap.has(dateStr)) {
                dailyMap.set(dateStr, { date: dateStr, pnl: 0, trades: 0 });
            }
            const daily = dailyMap.get(dateStr);
            daily.pnl += trade.net_pnl;
            daily.trades += 1;
        }
    });
    
    const dailyArray = Array.from(dailyMap.values()).sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Calculate cumulative PNL
    let cumulative = 0;
    dailyArray.forEach(daily => {
        cumulative += daily.pnl;
        daily.cumulative_pnl = cumulative;
    });
    
    return dailyArray;
}

function calculatePositionPNL(trades) {
    const positionMap = new Map();
    
    trades.forEach(trade => {
        const market = trade.ticker || trade.market_ticker || trade.market || 'Unknown';
        if (!positionMap.has(market)) {
            positionMap.set(market, {
                market,
                total_pnl: 0,
                trades: 0,
                wins: 0,
                losses: 0,
                win_pnl: 0,
                loss_pnl: 0
            });
        }
        
        const position = positionMap.get(market);
        position.total_pnl += trade.net_pnl;
        position.trades += 1;
        
        if (trade.is_win) {
            position.wins += 1;
            position.win_pnl += trade.net_pnl;
        } else if (trade.net_pnl < 0) {
            position.losses += 1;
            position.loss_pnl += trade.net_pnl;
        }
    });
    
    return Array.from(positionMap.values()).map(position => ({
        ...position,
        win_rate: position.trades > 0 ? (position.wins / position.trades) * 100 : 0,
        avg_win: position.wins > 0 ? position.win_pnl / position.wins : 0,
        avg_loss: position.losses > 0 ? position.loss_pnl / position.losses : 0
    })).sort((a, b) => b.total_pnl - a.total_pnl);
}

function getBestWorstTrades(trades) {
    const sortedTrades = [...trades].sort((a, b) => b.net_pnl - a.net_pnl);
    
    return {
        best: sortedTrades.slice(0, 5),
        worst: sortedTrades.slice(-5).reverse()
    };
}

function displayMetrics(summary) {
    const metricsGrid = document.getElementById('metricsGrid');
    
    const metrics = [
        { label: 'Total PNL', value: formatCurrency(summary.total_pnl), positive: summary.total_pnl >= 0 },
        { label: 'Total Trades', value: summary.total_trades, positive: null },
        { label: 'Win Rate', value: `${summary.win_rate.toFixed(1)}%`, positive: summary.win_rate >= 50 },
        { label: 'Avg Win', value: formatCurrency(summary.avg_win), positive: true },
        { label: 'Avg Loss', value: formatCurrency(summary.avg_loss), positive: false },
        { label: 'Profit Factor', value: summary.profit_factor === Infinity ? '∞' : summary.profit_factor.toFixed(2), positive: summary.profit_factor > 1 }
    ];
    
    metricsGrid.innerHTML = metrics.map(metric => `
        <div class="metric-card">
            <div class="metric-value ${metric.positive === null ? '' : metric.positive ? 'positive' : 'negative'}">
                ${metric.value}
            </div>
            <div class="metric-label">${metric.label}</div>
        </div>
    `).join('');
}

function displayCharts(analysis) {
    // Cumulative PNL Chart
    const pnlCtx = document.getElementById('pnlChart').getContext('2d');
    
    if (pnlChart) {
        pnlChart.destroy();
    }
    
    pnlChart = new Chart(pnlCtx, {
        type: 'line',
        data: {
            labels: analysis.daily_pnl.map(d => d.date),
            datasets: [{
                label: 'Cumulative PNL',
                data: analysis.daily_pnl.map(d => d.cumulative_pnl),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Win Rate Chart
    const winRateCtx = document.getElementById('winRateChart').getContext('2d');
    
    if (winRateChart) {
        winRateChart.destroy();
    }
    
    const topPositions = analysis.position_pnl.slice(0, 10);
    
    winRateChart = new Chart(winRateCtx, {
        type: 'bar',
        data: {
            labels: topPositions.map(p => p.market.substring(0, 15)),
            datasets: [{
                label: 'Win Rate (%)',
                data: topPositions.map(p => p.win_rate),
                backgroundColor: topPositions.map(p => p.win_rate >= 50 ? '#28a745' : '#dc3545'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function displayTables(analysis) {
    // Positions table
    const positionsTableBody = document.getElementById('positionsTableBody');
    positionsTableBody.innerHTML = analysis.position_pnl.slice(0, 15).map(position => `
        <tr>
            <td>${position.market}</td>
            <td class="${position.total_pnl >= 0 ? 'positive' : 'negative'}">
                ${formatCurrency(position.total_pnl)}
            </td>
            <td>${position.trades}</td>
            <td>${position.win_rate.toFixed(1)}%</td>
            <td class="positive">${formatCurrency(position.avg_win)}</td>
            <td class="negative">${formatCurrency(position.avg_loss)}</td>
        </tr>
    `).join('');
    
    // Best trades table
    const bestTradesTableBody = document.getElementById('bestTradesTableBody');
    bestTradesTableBody.innerHTML = analysis.best_worst.best.map(trade => `
        <tr>
            <td>${trade.ticker || trade.market_ticker || 'Unknown'}</td>
            <td class="positive">${formatCurrency(trade.net_pnl)}</td>
            <td>${trade.date ? trade.date.toLocaleDateString() : 'N/A'}</td>
        </tr>
    `).join('');
    
    // Worst trades table
    const worstTradesTableBody = document.getElementById('worstTradesTableBody');
    worstTradesTableBody.innerHTML = analysis.best_worst.worst.map(trade => `
        <tr>
            <td>${trade.ticker || trade.market_ticker || 'Unknown'}</td>
            <td class="negative">${formatCurrency(trade.net_pnl)}</td>
            <td>${trade.date ? trade.date.toLocaleDateString() : 'N/A'}</td>
        </tr>
    `).join('');
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

function loadSampleData() {
    // Create sample data for demonstration
    const sampleData = {
        fills: [
            { ticker: 'PREZ24', cost: 45, payout: 100, created_at: '2024-01-15T10:00:00Z', fees: 2 },
            { ticker: 'PREZ24', cost: 60, payout: 0, created_at: '2024-01-16T14:30:00Z', fees: 1.5 },
            { ticker: 'ELEX24', cost: 30, payout: 100, created_at: '2024-01-17T09:15:00Z', fees: 1 },
            { ticker: 'ELEX24', cost: 25, payout: 100, created_at: '2024-01-18T16:45:00Z', fees: 0.8 },
            { ticker: 'WEATHER', cost: 40, payout: 0, created_at: '2024-01-19T11:20:00Z', fees: 1.2 },
            { ticker: 'SPORTS', cost: 35, payout: 100, created_at: '2024-01-20T13:10:00Z', fees: 1.1 }
        ]
    };
    
    currentData = sampleData;
    processAndDisplayData(sampleData);
    document.getElementById('refreshBtn').disabled = false;
    showStatus('Sample data loaded successfully!');
}

function refreshData() {
    if (currentData) {
        processAndDisplayData(currentData);
        showStatus('Data refreshed!');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Kalshi PNL Dashboard loaded');
});