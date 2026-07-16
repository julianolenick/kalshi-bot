/**
 * Kalshi Trading Bot Dashboard - Frontend JavaScript
 * Handles real-time updates and user interactions
 */

// API Configuration
const API_BASE = '/api';
const UPDATE_INTERVAL = 5000;  // Update every 5 seconds

let updateInterval;
let botRunning = false;

// ========================
// DOM Element References
// ========================

const elements = {
    startBtn: document.getElementById('start-btn'),
    stopBtn: document.getElementById('stop-btn'),
    botStatus: document.getElementById('bot-status'),
    lastUpdate: document.getElementById('last-update'),
    availableCapital: document.getElementById('available-capital'),
    dailyPnL: document.getElementById('daily-pnl'),
    totalPnL: document.getElementById('total-pnl'),
    tradesCount: document.getElementById('trades-count'),
    lossRemaining: document.getElementById('loss-remaining'),
    capitalPercentage: document.getElementById('capital-percentage'),
    capitalProgress: document.getElementById('capital-progress'),
    marketsMonitored: document.getElementById('markets-monitored'),
    signalsDetected: document.getElementById('signals-detected'),
    tradesToday: document.getElementById('trades-today'),
    lastCheck: document.getElementById('last-check'),
    tradesTbody: document.getElementById('trades-tbody')
};

// ========================
// Event Listeners
// ========================

elements.startBtn.addEventListener('click', startBot);
elements.stopBtn.addEventListener('click', stopBot);

// ========================
// Bot Control Functions
// ========================

async function startBot() {
    try {
        const response = await fetch(`${API_BASE}/bot/start`, { method: 'POST' });
        if (response.ok) {
            botRunning = true;
            updateBotUI();
            startDashboardUpdates();
        }
    } catch (error) {
        console.error('Error starting bot:', error);
    }
}

async function stopBot() {
    try {
        const response = await fetch(`${API_BASE}/bot/stop`, { method: 'POST' });
        if (response.ok) {
            botRunning = false;
            updateBotUI();
            stopDashboardUpdates();
        }
    } catch (error) {
        console.error('Error stopping bot:', error);
    }
}

function updateBotUI() {
    if (botRunning) {
        elements.botStatus.textContent = 'Bot: Running';
        elements.botStatus.classList.remove('stopped');
        elements.botStatus.classList.add('running');
        elements.startBtn.disabled = true;
        elements.stopBtn.disabled = false;
    } else {
        elements.botStatus.textContent = 'Bot: Stopped';
        elements.botStatus.classList.remove('running');
        elements.botStatus.classList.add('stopped');
        elements.startBtn.disabled = false;
        elements.stopBtn.disabled = true;
    }
}

// ========================
// Dashboard Update Functions
// ========================

async function updateDashboard() {
    try {
        const [statusResponse, tradesResponse] = await Promise.all([
            fetch(`${API_BASE}/status`),
            fetch(`${API_BASE}/trades?limit=10`)
        ]);
        
        if (!statusResponse.ok || !tradesResponse.ok) {
            console.error('Failed to fetch data');
            return;
        }
        
        const status = await statusResponse.json();
        const trades = await tradesResponse.json();
        
        // Update portfolio metrics
        elements.availableCapital.textContent = formatCurrency(status.available_capital);
        elements.dailyPnL.textContent = formatCurrency(status.daily_pnl);
        elements.totalPnL.textContent = formatCurrency(status.total_pnl);
        elements.tradesCount.textContent = status.trades_executed || 0;
        
        // Update risk metrics
        const riskMetrics = status.risk_metrics;
        if (riskMetrics) {
            elements.lossRemaining.textContent = formatCurrency(riskMetrics.loss_remaining);
            elements.capitalPercentage.textContent = riskMetrics.capital_percentage.toFixed(1) + '%';
            elements.capitalProgress.style.width = Math.max(0, riskMetrics.capital_percentage) + '%';
        }
        
        // Update activity metrics
        elements.marketsMonitored.textContent = status.markets_monitored || 0;
        elements.signalsDetected.textContent = status.signals_detected || 0;
        elements.tradesToday.textContent = status.trades_executed || 0;
        
        // Update last check time
        if (status.last_check) {
            const lastCheckTime = new Date(status.last_check);
            elements.lastCheck.textContent = lastCheckTime.toLocaleTimeString();
        }
        
        // Update last update timestamp
        elements.lastUpdate.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
        
        // Update trades table
        updateTradesTable(trades);
        
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

function updateTradesTable(trades) {
    if (!trades || trades.length === 0) {
        elements.tradesTbody.innerHTML = '<tr class="empty-state"><td colspan="6">No trades yet</td></tr>';
        return;
    }
    
    const rows = trades.map(trade => `
        <tr>
            <td>${formatTime(trade.timestamp)}</td>
            <td>${trade.market_name || 'Unknown'}</td>
            <td><span class="badge">${trade.signal_type || 'N/A'}</span></td>
            <td>${trade.direction === 'yes' ? '✅ YES' : '❌ NO'}</td>
            <td>$${trade.trade_size.toFixed(2)}</td>
            <td><span class="status ${trade.status}">${trade.status}</span></td>
        </tr>
    `).join('');
    
    elements.tradesTbody.innerHTML = rows;
}

// ========================
// Utility Functions
// ========================

function formatCurrency(value) {
    if (value === null || value === undefined) return '$0.00';
    const num = parseFloat(value);
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(num);
}

function formatTime(isoString) {
    if (!isoString) return '--';
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function startDashboardUpdates() {
    // Update immediately
    updateDashboard();
    
    // Then update periodically
    if (updateInterval) clearInterval(updateInterval);
    updateInterval = setInterval(updateDashboard, UPDATE_INTERVAL);
}

function stopDashboardUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// ========================
// Initialization
// ========================

window.addEventListener('load', () => {
    console.log('Kalshi Trading Bot Dashboard loaded');
    updateBotUI();
    updateDashboard();
    // Don't auto-start updates; wait for user to start bot
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    stopDashboardUpdates();
});
