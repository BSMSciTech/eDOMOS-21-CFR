/* Real-Time Analytics Updates - Advanced Implementation */

// Add this JavaScript to analytics.html for smooth real-time updates without page reload

// Store current time range
let currentTimeRange = new URLSearchParams(window.location.search).get('range') || 'month';

// Function to update KPI values with animation
function updateKPIValue(elementId, newValue, suffix = '') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const currentValue = parseFloat(element.textContent) || 0;
    
    // Animate value change
    const duration = 500; // milliseconds
    const steps = 20;
    const increment = (newValue - currentValue) / steps;
    let step = 0;
    
    const interval = setInterval(() => {
        step++;
        const value = currentValue + (increment * step);
        element.textContent = Math.round(value) + suffix;
        
        if (step >= steps) {
            clearInterval(interval);
            element.textContent = Math.round(newValue) + suffix;
            
            // Add flash effect
            element.style.transition = 'all 0.3s';
            element.style.color = '#10b981';
            setTimeout(() => {
                element.style.color = '';
            }, 300);
        }
    }, duration / steps);
}

// Function to fetch updated analytics data
async function fetchAnalyticsData() {
    try {
        const response = await fetch(`/api/analytics/data?range=${currentTimeRange}`);
        const data = await response.json();
        
        if (data.success) {
            updateAnalyticsDisplay(data);
            console.log('[ANALYTICS] Data updated:', new Date().toLocaleTimeString());
        }
    } catch (error) {
        console.error('[ANALYTICS] Error fetching data:', error);
    }
}

// Function to update all analytics displays
function updateAnalyticsDisplay(data) {
    // Update door metrics
    updateKPIValue('door-open-day', data.door_metrics.door_open_count_day);
    updateKPIValue('door-open-week', data.door_metrics.door_open_count_week);
    updateKPIValue('door-open-month', data.door_metrics.door_open_count_month);
    
    // Update alarm metrics
    updateKPIValue('total-alarms', data.alarm_metrics.total_alarms);
    updateKPIValue('avg-alarm-duration', data.alarm_metrics.avg_alarm_duration, 's');
    updateKPIValue('longest-alarm', data.alarm_metrics.longest_alarm_duration, 's');
    updateKPIValue('unack-alarms', data.alarm_metrics.unacknowledged_alarms);
    
    // Update performance metrics
    updateKPIValue('mttr-value', data.performance_metrics.mttr, 's');
    updateKPIValue('compliance-percent', data.performance_metrics.compliance_percentage, '%');
    updateKPIValue('alarm-reduction', Math.abs(data.performance_metrics.alarm_reduction_percent), '%');
    
    // Show subtle update indicator
    showQuickFlash();
}

// Quick flash to indicate update
function showQuickFlash() {
    const indicator = document.getElementById('realtime-indicator');
    if (indicator) {
        indicator.style.background = 'rgba(59, 130, 246, 0.9)';
        setTimeout(() => {
            indicator.style.background = 'rgba(16, 185, 129, 0.9)';
        }, 200);
    }
}

// Listen for WebSocket events
socket.on('new_event', function(data) {
    if (data.event && (
        data.event.event_type === 'door_open' || 
        data.event.event_type === 'door_close' || 
        data.event.event_type === 'alarm_triggered'
    )) {
        console.log('[ANALYTICS] Relevant event, fetching updated data...');
        
        // Show notification
        showUpdateNotification(data.event.event_type);
        
        // Fetch and update data (no page reload!)
        setTimeout(() => {
            fetchAnalyticsData();
        }, 500); // Small delay to ensure event is processed in DB
    }
});

// Update notification function (improved)
function showUpdateNotification(eventType) {
    let notification = document.getElementById('analytics-notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'analytics-notification';
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 9999;
            display: none;
            animation: slideInRight 0.3s ease-out;
        `;
        document.body.appendChild(notification);
    }
    
    let icon = '📊';
    let message = 'Updating';
    if (eventType === 'door_open') {
        icon = '🚪';
        message = 'Door opened';
    } else if (eventType === 'door_close') {
        icon = '🔒';
        message = 'Door closed';
    } else if (eventType === 'alarm_triggered') {
        icon = '🔔';
        message = 'Alarm triggered';
    }
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px; font-size: 13px;">
            <span style="font-size: 20px;">${icon}</span>
            <span><strong>${message}</strong> - Analytics updated</span>
        </div>
    `;
    
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            notification.style.display = 'none';
            notification.style.animation = '';
        }, 300);
    }, 2000);
}

// Optional: Periodic refresh (every 30 seconds as backup)
setInterval(() => {
    fetchAnalyticsData();
}, 30000);

console.log('[ANALYTICS] Real-time updates initialized');
