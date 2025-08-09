class CreditCardAnalyzer {
    constructor() {
        this.transactions = [];
        this.loadedFiles = [];
        this.categoryChart = null;
        this.trendChart = null;
        this.currentTimePeriod = 'day';
        this.initializeEventListeners();
    }

    formatCurrency(amount) {
        return '$' + Math.round(amount).toLocaleString();
    }

    initializeEventListeners() {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');

        // Prevent default drag behaviors only when files are being dragged
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, (e) => {
                // Only prevent default if files are being dragged
                if (e.dataTransfer && e.dataTransfer.items && e.dataTransfer.items.length > 0) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }, false);
        });

        dropZone.addEventListener('dragover', this.handleDragOver.bind(this));
        dropZone.addEventListener('dragenter', this.handleDragEnter.bind(this));
        dropZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        dropZone.addEventListener('drop', this.handleDrop.bind(this));
        dropZone.addEventListener('click', () => fileInput.click());
        
        browseBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Browse button clicked');
            fileInput.click();
        });
        
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // Time period filter buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('period-btn')) {
                this.handleTimePeriodChange(e.target.dataset.period);
            } else if (e.target.id === 'addMoreFilesBtn') {
                fileInput.click();
            } else if (e.target.classList.contains('remove-file-btn')) {
                const fileId = e.target.dataset.fileId;
                this.removeFile(fileId);
            }
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDragEnter(e) {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.add('drag-over');
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        // Only remove drag-over if we're actually leaving the drop zone
        if (!e.currentTarget.contains(e.relatedTarget)) {
            e.currentTarget.classList.remove('drag-over');
        }
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        e.currentTarget.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files);
        this.processFiles(files);
    }

    handleFileSelect(e) {
        console.log('File input changed', e.target.files);
        const files = Array.from(e.target.files);
        console.log('Processing files:', files.length);
        this.processFiles(files);
        // Clear the input so the same files can be selected again
        e.target.value = '';
    }

    async processFiles(files) {
        const csvFiles = files.filter(file => 
            file.name.toLowerCase().endsWith('.csv')
        );

        if (csvFiles.length === 0) {
            alert('Please select CSV files only');
            return;
        }

        if (csvFiles.length !== files.length) {
            alert('Some files were skipped (only CSV files are supported)');
        }

        for (const file of csvFiles) {
            await this.processFile(file);
        }

        this.aggregateTransactions();
        this.displayAnalysis();
    }

    async processFile(file) {
        // File validation
        if (!file || !file.name) {
            alert('Invalid file selected');
            return;
        }
        
        if (!file.name.toLowerCase().endsWith('.csv')) {
            alert('Please select a CSV file');
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            alert('File too large. Please select a smaller CSV file.');
            return;
        }

        if (file.size === 0) {
            alert('File is empty. Please select a valid CSV file.');
            return;
        }

        // Check if file is already loaded
        if (this.loadedFiles.some(f => f.name === file.name && f.size === file.size)) {
            alert(`File "${file.name}" is already loaded`);
            return;
        }

        try {
            const text = await this.readFile(file);
            const transactions = this.parseCSV(text);
            this.categorizeTransactions(transactions);
            
            // Store file info
            const fileInfo = {
                id: Date.now() + Math.random(),
                name: file.name,
                size: file.size,
                transactionCount: transactions.length,
                transactions: transactions
            };
            
            this.loadedFiles.push(fileInfo);
            return fileInfo;
        } catch (error) {
            alert(`Error reading file "${file.name}". Please try again.`);
        }
    }

    readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    parseCSV(text) {
        // Input validation
        if (!text || typeof text !== 'string') return [];
        if (text.length > 10 * 1024 * 1024) { // 10MB limit
            alert('File too large. Please select a smaller CSV file.');
            return [];
        }

        const lines = text.split('\n').filter(line => line.trim());
        if (lines.length < 2) return [];
        if (lines.length > 50000) { // Limit number of transactions
            alert('File contains too many rows. Please select a smaller CSV file.');
            return [];
        }

        const headers = this.parseCSVLine(lines[0]).map(h => h.toLowerCase().trim());
        const transactions = [];

        for (let i = 1; i < lines.length; i++) {
            const values = this.parseCSVLine(lines[i]);
            if (values.length < headers.length) continue;

            const transaction = {};
            headers.forEach((header, index) => {
                const value = values[index]?.trim() || '';
                // Sanitize input - remove potentially dangerous characters
                transaction[header] = value.replace(/[<>'"&]/g, '');
            });

            const parsedTransaction = this.normalizeTransaction(transaction);
            if (parsedTransaction) {
                transactions.push(parsedTransaction);
            }
        }

        return transactions;
    }

    parseCSVLine(line) {
        // Input validation
        if (!line || typeof line !== 'string') return [];
        if (line.length > 10000) return []; // Prevent extremely long lines

        const result = [];
        let current = '';
        let inQuotes = false;

        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            const nextChar = line[i + 1];

            if (char === '"') {
                if (inQuotes && nextChar === '"') {
                    current += '"';
                    i++;
                } else {
                    inQuotes = !inQuotes;
                }
            } else if (char === ',' && !inQuotes) {
                result.push(current);
                current = '';
            } else {
                current += char;
            }
        }

        result.push(current);
        return result;
    }

    normalizeTransaction(transaction) {
        const dateFields = ['date', 'transaction date', 'posted date', 'transaction_date'];
        const descriptionFields = ['description', 'transaction', 'merchant', 'memo'];
        const amountFields = ['amount', 'debit', 'credit', 'transaction amount'];

        let date = null;
        let description = '';
        let amount = 0;

        for (const field of dateFields) {
            if (transaction[field]) {
                date = this.parseDate(transaction[field]);
                break;
            }
        }

        for (const field of descriptionFields) {
            if (transaction[field]) {
                description = transaction[field];
                break;
            }
        }

        for (const field of amountFields) {
            if (transaction[field]) {
                amount = this.parseAmount(transaction[field]);
                break;
            }
        }

        if (!transaction['credit'] && transaction['debit']) {
            amount = -Math.abs(this.parseAmount(transaction['debit']));
        } else if (transaction['credit'] && !transaction['debit']) {
            amount = Math.abs(this.parseAmount(transaction['credit']));
        }

        if (!date || !description) return null;

        return {
            date,
            description: description.trim(),
            amount,
            category: 'Uncategorized'
        };
    }

    parseDate(dateStr) {
        const cleanDate = dateStr.replace(/[^\d\/\-\.]/g, '');
        const date = new Date(cleanDate);
        return isNaN(date.getTime()) ? null : date;
    }

    parseAmount(amountStr) {
        const cleaned = amountStr.replace(/[$,\s]/g, '');
        const amount = parseFloat(cleaned);
        return isNaN(amount) ? 0 : amount;
    }

    categorizeTransactions(transactions = this.transactions) {
        const categories = {
            'Food & Dining': ['restaurant', 'food', 'cafe', 'pizza', 'burger', 'starbucks', 'mcdonalds', 'subway', 'chipotle', 'panera'],
            'Groceries': ['grocery', 'supermarket', 'walmart', 'target', 'costco', 'safeway', 'kroger', 'whole foods', 'trader joe'],
            'Gas & Transportation': ['gas', 'fuel', 'shell', 'exxon', 'chevron', 'bp', 'uber', 'lyft', 'taxi', 'parking'],
            'Shopping': ['amazon', 'ebay', 'shopping', 'store', 'mall', 'retail', 'clothing', 'shoes'],
            'Entertainment': ['movie', 'theater', 'netflix', 'spotify', 'gaming', 'entertainment', 'concert', 'bar'],
            'Utilities': ['electric', 'gas company', 'water', 'internet', 'phone', 'cable', 'utility'],
            'Healthcare': ['pharmacy', 'doctor', 'hospital', 'medical', 'cvs', 'walgreens', 'health'],
            'Travel': ['hotel', 'airline', 'airport', 'travel', 'booking', 'airbnb'],
            'Subscriptions': ['subscription', 'monthly', 'annual', 'membership']
        };

        transactions.forEach(transaction => {
            const description = transaction.description.toLowerCase();
            
            for (const [category, keywords] of Object.entries(categories)) {
                if (keywords.some(keyword => description.includes(keyword))) {
                    transaction.category = category;
                    break;
                }
            }
        });
    }

    aggregateTransactions() {
        this.transactions = [];
        this.loadedFiles.forEach(file => {
            this.transactions.push(...file.transactions);
        });
        this.updateFilesDisplay();
    }

    removeFile(fileId) {
        this.loadedFiles = this.loadedFiles.filter(file => file.id !== fileId);
        this.aggregateTransactions();
        if (this.loadedFiles.length > 0) {
            this.displayAnalysis();
        } else {
            document.getElementById('analysisSection').style.display = 'none';
        }
    }

    updateFilesDisplay() {
        const filesList = document.getElementById('filesList');
        
        if (this.loadedFiles.length === 0) {
            filesList.innerHTML = '<p style="color: #6c757d; text-align: center; padding: 20px;">No files loaded</p>';
            return;
        }

        filesList.innerHTML = this.loadedFiles.map(file => `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-stats">${file.transactionCount.toLocaleString()} transactions • ${this.formatFileSize(file.size)}</div>
                </div>
                <button class="remove-file-btn" data-file-id="${file.id}">Remove</button>
            </div>
        `).join('');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    displayAnalysis() {
        document.getElementById('analysisSection').style.display = 'block';
        
        this.updateSummaryCards();
        this.createCategoryChart();
        this.createTrendChart();
        this.populateRestaurantsTable();
        this.populateTransactionsTable();
        
        document.getElementById('analysisSection').scrollIntoView({ 
            behavior: 'smooth' 
        });
    }

    updateSummaryCards() {
        const expenses = this.transactions.filter(t => t.amount < 0);
        const totalSpent = Math.abs(expenses.reduce((sum, t) => sum + t.amount, 0));
        const totalTransactions = this.transactions.length;
        
        const categoryTotals = {};
        expenses.forEach(t => {
            categoryTotals[t.category] = (categoryTotals[t.category] || 0) + Math.abs(t.amount);
        });
        
        const topCategory = Object.keys(categoryTotals).reduce((a, b) => 
            categoryTotals[a] > categoryTotals[b] ? a : b, 'None');

        document.getElementById('totalSpent').textContent = this.formatCurrency(totalSpent);
        document.getElementById('totalTransactions').textContent = totalTransactions.toLocaleString();
        document.getElementById('topCategory').textContent = topCategory;
    }

    createCategoryChart() {
        const ctx = document.getElementById('categoryChart').getContext('2d');
        
        if (this.categoryChart) {
            this.categoryChart.destroy();
        }

        const expenses = this.transactions.filter(t => t.amount < 0);
        const categoryTotals = {};
        
        expenses.forEach(transaction => {
            const amount = Math.abs(transaction.amount);
            categoryTotals[transaction.category] = (categoryTotals[transaction.category] || 0) + amount;
        });

        const sortedCategories = Object.entries(categoryTotals)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 8);

        this.categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: sortedCategories.map(([category]) => category),
                datasets: [{
                    data: sortedCategories.map(([, amount]) => amount),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    handleTimePeriodChange(period) {
        this.currentTimePeriod = period;
        
        // Update active button
        document.querySelectorAll('.period-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-period="${period}"]`).classList.add('active');
        
        // Recreate chart with new period
        this.createTrendChart();
        this.populateRestaurantsTable();
    }

    groupTransactionsByPeriod(transactions, period) {
        const groups = {};
        
        transactions.filter(t => t.amount < 0).forEach(transaction => {
            let key;
            const date = transaction.date;
            
            switch (period) {
                case 'day':
                    key = date.toISOString().split('T')[0];
                    break;
                case 'week':
                    const weekStart = new Date(date);
                    weekStart.setDate(date.getDate() - date.getDay());
                    key = weekStart.toISOString().split('T')[0];
                    break;
                case 'month':
                    key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                    break;
            }
            
            groups[key] = (groups[key] || 0) + Math.abs(transaction.amount);
        });
        
        return groups;
    }

    formatDateLabel(dateKey, period) {
        const date = new Date(dateKey);
        
        switch (period) {
            case 'day':
                return date.toLocaleDateString();
            case 'week':
                const weekEnd = new Date(date);
                weekEnd.setDate(date.getDate() + 6);
                return `${date.toLocaleDateString()} - ${weekEnd.toLocaleDateString()}`;
            case 'month':
                return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
            default:
                return dateKey;
        }
    }

    createTrendChart() {
        const ctx = document.getElementById('trendChart').getContext('2d');
        
        if (this.trendChart) {
            this.trendChart.destroy();
        }

        const groupedData = this.groupTransactionsByPeriod(this.transactions, this.currentTimePeriod);
        const sortedKeys = Object.keys(groupedData).sort();
        
        // Limit the number of periods shown
        const maxPeriods = this.currentTimePeriod === 'day' ? 30 : 
                          this.currentTimePeriod === 'week' ? 12 : 6;
        const displayKeys = sortedKeys.slice(-maxPeriods);

        const labels = displayKeys.map(key => this.formatDateLabel(key, this.currentTimePeriod));
        const data = displayKeys.map(key => groupedData[key] || 0);

        const periodLabel = this.currentTimePeriod.charAt(0).toUpperCase() + this.currentTimePeriod.slice(1) + 'ly Spending';

        this.trendChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: periodLabel,
                    data,
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: '#36A2EB',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => {
                                return this.formatCurrency(value);
                            }.bind(this)
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `${context.dataset.label}: ${this.formatCurrency(context.parsed.y)}`;
                            }.bind(this)
                        }
                    }
                }
            }
        });
    }

    getDateRange(transactions) {
        if (!transactions.length) return { start: null, end: null };
        
        const dates = transactions.map(t => t.date).sort((a, b) => a - b);
        return {
            start: dates[0],
            end: dates[dates.length - 1]
        };
    }

    getRestaurantTransactions() {
        const restaurantKeywords = [
            'restaurant', 'cafe', 'pizza', 'burger', 'starbucks', 'mcdonalds', 'subway', 
            'chipotle', 'panera', 'taco bell', 'kfc', 'wendys', 'chick-fil-a', 'dominos',
            'papa johns', 'olive garden', 'applebees', 'chilis', 'outback', 'red lobster',
            'denny\'s', 'ihop', 'cracker barrel', 'sonic', 'dairy queen', 'five guys',
            'in-n-out', 'shake shack', 'whataburger', 'popeyes', 'panda express',
            'food', 'grill', 'diner', 'bistro', 'eatery', 'kitchen', 'tavern', 'pub'
        ];

        return this.transactions.filter(t => {
            if (t.amount >= 0) return false; // Only expenses
            const description = t.description.toLowerCase();
            return restaurantKeywords.some(keyword => description.includes(keyword)) ||
                   t.category === 'Food & Dining';
        });
    }

    populateRestaurantsTable() {
        const restaurantTransactions = this.getRestaurantTransactions();
        const dateRange = this.getDateRange(restaurantTransactions);
        
        // Update date range display
        const dateRangeElement = document.getElementById('restaurantDateRange');
        if (dateRange.start && dateRange.end) {
            const startStr = dateRange.start.toLocaleDateString();
            const endStr = dateRange.end.toLocaleDateString();
            dateRangeElement.textContent = `${startStr} - ${endStr}`;
        } else {
            dateRangeElement.textContent = 'No restaurant transactions found';
        }

        // Group by restaurant name
        const restaurantData = {};
        restaurantTransactions.forEach(transaction => {
            const name = this.extractRestaurantName(transaction.description);
            if (!restaurantData[name]) {
                restaurantData[name] = {
                    total: 0,
                    visits: 0,
                    transactions: []
                };
            }
            restaurantData[name].total += Math.abs(transaction.amount);
            restaurantData[name].visits++;
            restaurantData[name].transactions.push(transaction);
        });

        // Sort by total spending and get top 10
        const sortedRestaurants = Object.entries(restaurantData)
            .sort(([,a], [,b]) => b.total - a.total)
            .slice(0, 10);

        // Populate table
        const tbody = document.getElementById('restaurantsBody');
        tbody.innerHTML = '';

        sortedRestaurants.forEach(([name, data]) => {
            const row = tbody.insertRow();
            const avgPerVisit = data.total / data.visits;
            
            row.insertCell(0).textContent = name;
            row.insertCell(1).textContent = this.formatCurrency(data.total);
            row.insertCell(2).textContent = data.visits;
            row.insertCell(3).textContent = this.formatCurrency(avgPerVisit);
        });
    }

    extractRestaurantName(description) {
        // Clean up common transaction description patterns
        let cleaned = description
            .replace(/^\d+\s*/, '') // Remove leading numbers
            .replace(/\s*#\d+.*$/, '') // Remove transaction IDs
            .replace(/\s*\*+.*$/, '') // Remove asterisks and everything after
            .replace(/\s*-.*$/, '') // Remove dashes and everything after
            .replace(/\bQPS\b|\bQSR\b|\bPOS\b/gi, '') // Remove common POS terms
            .trim();

        // Capitalize first letter of each word
        return cleaned.split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }

    populateTransactionsTable() {
        const tbody = document.getElementById('transactionsBody');
        tbody.innerHTML = '';

        const sortedTransactions = [...this.transactions]
            .sort((a, b) => b.date - a.date)
            .slice(0, 50);

        sortedTransactions.forEach(transaction => {
            const row = tbody.insertRow();
            
            row.insertCell(0).textContent = transaction.date.toLocaleDateString();
            row.insertCell(1).textContent = transaction.description;
            row.insertCell(2).textContent = transaction.category;
            
            const amountCell = row.insertCell(3);
            const amount = transaction.amount;
            amountCell.textContent = (amount >= 0 ? '+' : '') + this.formatCurrency(Math.abs(amount));
            amountCell.className = amount >= 0 ? 'amount-positive' : 'amount-negative';
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CreditCardAnalyzer();
});