/**
 * DriveSafe AI - Main JavaScript
 * Handles real-time updates and UI interactions
 */

// Configuration
const UPDATE_INTERVAL = 500; // Update every 500ms
const API_BASE_URL = window.location.origin;

// State
let updateTimer = null;
let lastAlertSound = 0;
const AUDIO_COOLDOWN = 5000; // 5 seconds between audio alerts

// DOM Elements
const elements = {
    statusBadge: document.getElementById('status-badge'),
    statusCircle: document.getElementById('status-circle'),
    statusEmoji: document.getElementById('status-emoji'),
    statusLevel: document.getElementById('status-level'),
    statusDescription: document.getElementById('status-description'),
    drowsinessMeter: document.getElementById('drowsiness-meter'),
    drowsinessValue: document.getElementById('drowsiness-value'),
    blinkCount: document.getElementById('blink-count'),
    yawnCount: document.getElementById('yawn-count'),
    earValue: document.getElementById('ear-value'),
    marValue: document.getElementById('mar-value'),
    totalAlerts: document.getElementById('total-alerts'),
    lastAlert: document.getElementById('last-alert'),
    alertOverlay: document.getElementById('alert-overlay'),
    alertSound: document.getElementById('alert-sound'),
    connectionDot: document.getElementById('connection-dot')
};

/**
 * Initialize the application
 */
function init() {
    console.log('🚗 Initializing DriveSafe AI...');

    // Initialize chart
    initializeChart();

    // Start update loop
    startUpdates();

    // Handle visibility change (pause when tab is hidden)
    document.addEventListener('visibilitychange', handleVisibilityChange);

    console.log('✅ DriveSafe AI initialized successfully');
}

/**
 * Start periodic updates
 */
function startUpdates() {
    if (updateTimer) clearInterval(updateTimer);

    // Initial update
    updateStatus();

    // Set up periodic updates
    updateTimer = setInterval(updateStatus, UPDATE_INTERVAL);
}

/**
 * Stop periodic updates
 */
function stopUpdates() {
    if (updateTimer) {
        clearInterval(updateTimer);
        updateTimer = null;
    }
}

/**
 * Fetch and update drowsiness status
 */
async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/drowsiness_status`);

        if (!response.ok) {
            throw new Error('Failed to fetch status');
        }

        const data = await response.json();

        // Update UI
        updateStatusDisplay(data);
        updateMetrics(data.metrics);
        updateChart(data.drowsiness_score);

        // Handle alerts
        if (data.trigger_audio) {
            triggerAlert();
        }

        // Update visual alert overlay
        updateAlertOverlay(data.status);

        // Update connection indicator
        setConnectionStatus(true);

    } catch (error) {
        console.error('Error fetching status:', error);
        setConnectionStatus(false);
    }
}

/**
 * Update status display
 */
function updateStatusDisplay(data) {
    const { status, drowsiness_score } = data;

    // Update status badge
    elements.statusBadge.querySelector('.status-text').textContent = status;
    elements.statusBadge.className = 'status-badge ' + status.toLowerCase();

    // Update status circle and info
    elements.statusCircle.className = 'status-circle ' + status.toLowerCase();
    elements.statusLevel.textContent = status;

    // Update emoji and description
    const statusConfig = getStatusConfig(status);
    elements.statusEmoji.textContent = statusConfig.emoji;
    elements.statusDescription.textContent = statusConfig.description;

    // Update drowsiness meter
    elements.drowsinessMeter.style.width = drowsiness_score + '%';
    elements.drowsinessMeter.className = 'meter-fill ' + status.toLowerCase();
    elements.drowsinessValue.textContent = drowsiness_score + '%';
}

/**
 * Get status configuration
 */
function getStatusConfig(status) {
    const configs = {
        'Normal': {
            emoji: '😊',
            description: 'All systems operational'
        },
        'Warning': {
            emoji: '😐',
            description: 'Showing signs of fatigue'
        },
        'Alert': {
            emoji: '😴',
            description: 'DROWSINESS DETECTED!'
        }
    };

    return configs[status] || configs['Normal'];
}

/**
 * Update metrics display
 */
function updateMetrics(metrics) {
    elements.blinkCount.textContent = metrics.blink_count || 0;
    elements.yawnCount.textContent = metrics.yawn_count || 0;
    elements.earValue.textContent = (metrics.ear || 0).toFixed(2);
    elements.marValue.textContent = (metrics.mar || 0).toFixed(2);
}

/**
 * Update alert overlay
 */
function updateAlertOverlay(status) {
    if (status === 'Alert') {
        elements.alertOverlay.classList.remove('hidden');
    } else {
        elements.alertOverlay.classList.add('hidden');
    }
}

/**
 * Trigger audio and visual alert
 */
function triggerAlert() {
    const now = Date.now();

    // Check cooldown
    if (now - lastAlertSound < AUDIO_COOLDOWN) {
        return;
    }

    lastAlertSound = now;

    // Play audio alert
    if (elements.alertSound) {
        elements.alertSound.currentTime = 0;
        elements.alertSound.play().catch(err => {
            console.warn('Audio playback failed:', err);
            // Fallback: try to enable audio on user interaction
            document.addEventListener('click', enableAudio, { once: true });
        });
    }

    // Visual feedback (flash the screen red briefly)
    document.body.style.animation = 'flash-red 0.5s ease';
    setTimeout(() => {
        document.body.style.animation = '';
    }, 500);

    // Update alert history
    updateAlertHistory();
}

/**
 * Enable audio (for browsers that require user interaction)
 */
function enableAudio() {
    if (elements.alertSound) {
        elements.alertSound.play().then(() => {
            elements.alertSound.pause();
            elements.alertSound.currentTime = 0;
        }).catch(() => { });
    }
}

/**
 * Update alert history from session data
 */
async function updateAlertHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/session_data`);

        if (!response.ok) return;

        const data = await response.json();

        elements.totalAlerts.textContent = data.total_alerts || 0;

        if (data.alert_history && data.alert_history.length > 0) {
            const lastAlert = data.alert_history[data.alert_history.length - 1];
            const time = new Date(lastAlert.timestamp).toLocaleTimeString();
            elements.lastAlert.textContent = time;
        } else {
            elements.lastAlert.textContent = 'None';
        }

    } catch (error) {
        console.error('Error fetching alert history:', error);
    }
}

/**
 * Set connection status indicator
 */
function setConnectionStatus(isConnected) {
    if (isConnected) {
        elements.connectionDot.style.background = '#00f5a0';
    } else {
        elements.connectionDot.style.background = '#ff4757';
    }
}

/**
 * Handle visibility change (pause/resume updates)
 */
function handleVisibilityChange() {
    if (document.hidden) {
        stopUpdates();
        console.log('⏸️ Updates paused (tab hidden)');
    } else {
        startUpdates();
        console.log('▶️ Updates resumed');
    }
}

// Add flash animation to body
const style = document.createElement('style');
style.textContent = `
    @keyframes flash-red {
        0%, 100% { filter: none; }
        50% { filter: brightness(1.2) sepia(1) hue-rotate(-50deg) saturate(5); }
    }
`;
document.head.appendChild(style);

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Periodic alert history update (every 5 seconds)
setInterval(updateAlertHistory, 5000);
