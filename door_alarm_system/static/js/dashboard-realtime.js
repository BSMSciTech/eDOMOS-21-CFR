/**
 * Real-Time Dashboard Updates System
 * Updates door status, alarm status, and total events in real-time
 */

class DashboardRealTime {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.updateInterval = null;
        this.pollingRate = 5000; // Optimized: Increased from 3000ms to 5000ms for better performance
        this.lastEventId = 0;
        this.connectionRetries = 0;
        this.maxRetries = 5;
        
        console.log('🚀 Dashboard Real-Time System Initializing...');
        this.initialize();
    }
    
    initialize() {
        // Initialize WebSocket connection
        this.initializeWebSocket();
        
        // Start polling as fallback
        this.startPolling();
        
        // Initialize manual refresh button
        this.initializeManualRefresh();
        
        // Update connection status
        this.updateConnectionIndicator();
    }
    
    initializeWebSocket() {
        if (typeof io === 'undefined') {
            console.warn('⚠️ Socket.IO not loaded, using polling only');
            return;
        }
        
        try {
            console.log('🔌 Initializing WebSocket connection...');
            
            this.socket = io('/events', {
                transports: ['websocket', 'polling'],
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionAttempts: this.maxRetries,
                timeout: 10000,
                forceNew: true
            });
            
            this.setupWebSocketHandlers();
            
        } catch (error) {
            console.error('❌ WebSocket initialization failed:', error);
            this.fallbackToPolling();
        }
    }
    
    setupWebSocketHandlers() {
        this.socket.on('connect', () => {
            console.log('✅ WebSocket Connected - Real-time updates active');
            this.isConnected = true;
            this.connectionRetries = 0;
            
            // Stop polling since WebSocket is active
            this.stopPolling();
            this.updateConnectionIndicator();
            
            // Send ready signal
            this.socket.emit('client_ready', {
                page: 'dashboard',
                timestamp: new Date().toISOString()
            });
        });
        
        this.socket.on('new_event', (data) => {
            console.log('🎯 Real-time event received:', data);
            this.processRealtimeUpdate(data);
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ WebSocket Disconnected - Falling back to polling');
            this.isConnected = false;
            this.updateConnectionIndicator();
            this.startPolling();
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('❌ WebSocket connection error:', error);
            this.connectionRetries++;
            
            if (this.connectionRetries >= this.maxRetries) {
                console.log('🔄 Max retries reached, using polling mode');
                this.fallbackToPolling();
            }
        });
    }
    
    processRealtimeUpdate(data) {
        console.log('🔄 Processing real-time dashboard update...');
        
        try {
            // Update Door Status
            if (data.door_status) {
                this.updateDoorStatus(data.door_status);
            }
            
            // Update Alarm Status
            if (data.alarm_status) {
                this.updateAlarmStatus(data.alarm_status);
            }
            
            // Update Statistics
            if (data.statistics) {
                this.updateStatistics(data.statistics);
            }
            
            // Update Timer
            if (data.timer_set !== undefined) {
                this.updateTimer(data.timer_set);
            }
            
            // Update System Uptime
            if (data.uptime) {
                this.updateUptime(data.uptime);
            }
            
            // Update last event timestamp
            this.updateLastEventTime();
            
            console.log('✅ Dashboard components updated successfully');
            
        } catch (error) {
            console.error('❌ Error processing real-time update:', error);
        }
    }
    
    updateDoorStatus(status) {
        const doorStatusEl = document.getElementById('door-status');
        if (doorStatusEl) {
            console.log(`🚪 Updating door status panel: ${status}`);
            doorStatusEl.textContent = status;
            
            // Update the status indicator bar
            const doorPanel = doorStatusEl.closest('.status-panel');
            const indicatorBar = doorPanel?.querySelector('.status-indicator-bar');
            if (indicatorBar) {
                indicatorBar.className = 'status-indicator-bar ' + (status === 'Closed' ? 'safe' : 'warning');
            }
            
            // Add animation effect
            this.addUpdateAnimation(doorStatusEl);
        }
        
        // Update Hero Section Door Status Indicator
        this.updateHeroDoorStatus(status);
    }
    
    updateHeroDoorStatus(status) {
        const heroStatusEl = document.querySelector('.status-indicator');
        if (!heroStatusEl) {
            console.warn('⚠️ Hero section status indicator not found');
            return;
        }
        
        console.log(`🎯 Updating hero section door status: ${status}`);
        
        // Update the status classes
        const isSecure = status === 'Closed';
        heroStatusEl.className = `status-indicator ${isSecure ? 'secure' : 'alert'}`;
        
        // Update the icon
        const iconEl = heroStatusEl.querySelector('i');
        if (iconEl) {
            iconEl.className = `fas fa-${isSecure ? 'lock' : 'unlock'}`;
        }
        
        // Update the text content
        const textContent = `DOOR ${status.toUpperCase()}`;
        
        // Preserve the icon and update only the text
        if (iconEl) {
            heroStatusEl.innerHTML = '';
            heroStatusEl.appendChild(iconEl);
            heroStatusEl.appendChild(document.createTextNode(textContent));
        } else {
            heroStatusEl.textContent = textContent;
        }
        
        // Add pulse animation effect for visual feedback
        this.addHeroUpdateAnimation(heroStatusEl);
    }
    
    addHeroUpdateAnimation(element) {
        if (!element) return;
        
        // Remove existing animation classes
        element.classList.remove('status-updated', 'pulse-animation');
        
        // Add update animation
        requestAnimationFrame(() => {
            element.classList.add('status-updated');
            
            // Remove the class after animation completes
            setTimeout(() => {
                element.classList.remove('status-updated');
            }, 1000);
        });
    }
    
    updateAlarmStatus(status) {
        const alarmStatusEl = document.getElementById('alarm-status');
        if (!alarmStatusEl) return;
        
        console.log(`🚨 Updating alarm status: ${status}`);
        
        alarmStatusEl.textContent = status;
        
        // Update the status indicator bar
        const alarmPanel = alarmStatusEl.closest('.status-panel');
        const indicatorBar = alarmPanel?.querySelector('.status-indicator-bar');
        if (indicatorBar) {
            indicatorBar.className = 'status-indicator-bar ' + (status === 'Inactive' ? 'safe' : 'danger');
        }
        
        // Add animation effect
        this.addUpdateAnimation(alarmStatusEl);
    }
    
    updateStatistics(statistics) {
        console.log('📊 Updating statistics:', statistics);
        
        // Update Total Events
        const totalEventsEl = document.getElementById('total-events');
        if (totalEventsEl && statistics.total_events !== undefined) {
            this.animateCounter(totalEventsEl, statistics.total_events);
        }
        
        // Update Door Open Events
        const doorOpenEl = document.getElementById('door-open-events');
        if (doorOpenEl && statistics.door_open_events !== undefined) {
            this.animateCounter(doorOpenEl, statistics.door_open_events);
        }
        
        // Update Door Close Events
        const doorCloseEl = document.getElementById('door-close-events');
        if (doorCloseEl && statistics.door_close_events !== undefined) {
            this.animateCounter(doorCloseEl, statistics.door_close_events);
        }
        
        // Update Alarm Events
        const alarmEventsEl = document.getElementById('alarm-events');
        if (alarmEventsEl && statistics.alarm_events !== undefined) {
            this.animateCounter(alarmEventsEl, statistics.alarm_events);
        }
    }
    
    updateTimer(timerValue) {
        const timerEl = document.getElementById('timer-set');
        if (!timerEl) return;
        
        console.log(`⏰ Updating timer: ${timerValue}s`);
        
        timerEl.textContent = `${timerValue}s`;
        this.addUpdateAnimation(timerEl);
    }
    
    updateUptime(uptimeData) {
        if (!uptimeData) return;
        
        console.log('⏱️ Updating system uptime:', uptimeData);
        
        const uptimeEl = document.getElementById('system-uptime');
        const availabilityEl = document.getElementById('uptime-availability');
        
        if (uptimeEl && uptimeData.uptime_string) {
            const currentUptime = uptimeEl.textContent;
            if (currentUptime !== uptimeData.uptime_string) {
                uptimeEl.textContent = uptimeData.uptime_string;
                this.addUpdateAnimation(uptimeEl);
                
                // Add tooltip with detailed information
                uptimeEl.title = `Server Started: ${new Date(uptimeData.start_time).toLocaleString()}\n` +
                               `Uptime: ${uptimeData.days}d ${uptimeData.hours}h ${uptimeData.minutes}m ${uptimeData.seconds}s\n` +
                               `Availability: ${uptimeData.availability_percent}%`;
            }
        }
        
        if (availabilityEl && uptimeData.availability_percent !== undefined) {
            const availabilityText = `${uptimeData.availability_percent}% Available`;
            if (availabilityEl.textContent !== availabilityText) {
                availabilityEl.textContent = availabilityText;
                this.addUpdateAnimation(availabilityEl);
                
                // Color code availability based on percentage
                if (uptimeData.availability_percent >= 99.5) {
                    availabilityEl.style.color = '#10b981'; // Green - Excellent
                } else if (uptimeData.availability_percent >= 99.0) {
                    availabilityEl.style.color = '#3b82f6'; // Blue - Good  
                } else if (uptimeData.availability_percent >= 95.0) {
                    availabilityEl.style.color = '#f59e0b'; // Yellow - Warning
                } else {
                    availabilityEl.style.color = '#ef4444'; // Red - Critical
                }
            }
        }
    }
    
    updateLastEventTime() {
        const timestampEl = document.querySelector('.last-updated');
        if (timestampEl) {
            timestampEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
    }
    
    animateCounter(element, newValue) {
        if (!element) return;
        
        const currentValue = parseInt(element.textContent) || 0;
        if (currentValue === newValue) return;
        
        // Add updating class
        element.classList.add('counter-updating');
        
        // Optimized: Use requestAnimationFrame instead of setInterval for smoother performance
        const startTime = performance.now();
        const duration = 500; // Fixed duration for consistent performance
        const startValue = currentValue;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease out quad for natural deceleration
            const easeProgress = progress * (2 - progress);
            const current = Math.round(startValue + (newValue - startValue) * easeProgress);
            
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = newValue;
                element.classList.remove('counter-updating');
                this.addUpdateAnimation(element);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    addUpdateAnimation(element) {
        if (!element) return;
        
        element.classList.add('updated');
        setTimeout(() => {
            element.classList.remove('updated');
        }, 800); // Reduced from 1000ms
    }
    
    // Polling fallback system
    startPolling() {
        if (this.updateInterval) return;
        
        console.log('🔄 Starting polling mode for dashboard updates');
        
        this.updateInterval = setInterval(() => {
            this.pollForUpdates();
        }, this.pollingRate);
        
        // Initial poll
        this.pollForUpdates();
    }
    
    stopPolling() {
        if (this.updateInterval) {
            console.log('🛑 Stopping polling mode');
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    async pollForUpdates() {
        try {
            console.log('📡 Polling for dashboard updates...');
            
            // Fetch current dashboard data using the unified endpoint
            const response = await fetch('/api/dashboard');
            
            if (response.ok) {
                const data = await response.json();
                
                // Process updates with the complete dashboard data
                this.processRealtimeUpdate({
                    door_status: data.door_status,
                    alarm_status: data.alarm_status,
                    timer_set: data.timer_set,
                    statistics: {
                        total_events: data.total_events,
                        door_open_events: data.door_open_events,
                        door_close_events: data.door_close_events,
                        alarm_events: data.alarm_events
                    }
                });
                
                console.log('✅ Polling update successful');
            } else {
                console.warn('⚠️ Dashboard API response not ok:', response.status);
            }
            
        } catch (error) {
            console.error('❌ Polling update failed:', error);
        }
    }
    
    fallbackToPolling() {
        this.isConnected = false;
        this.socket = null;
        this.startPolling();
        this.updateConnectionIndicator();
    }
    
    initializeManualRefresh() {
        // Find existing refresh button or create one
        let refreshBtn = document.querySelector('.manual-refresh-btn');
        if (!refreshBtn) {
            // Try to find the existing refresh button in the dashboard
            refreshBtn = document.querySelector('[onclick="manualRefresh()"]');
        }
        
        if (refreshBtn) {
            refreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('🔄 Manual refresh triggered');
                this.pollForUpdates();
                
                // Visual feedback
                const originalContent = refreshBtn.innerHTML;
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
                setTimeout(() => {
                    refreshBtn.innerHTML = originalContent;
                }, 1000);
            });
        }
    }
    
    updateConnectionIndicator() {
        let indicator = document.getElementById('connection-status');
        
        // Create indicator if it doesn't exist
        if (!indicator) {
            indicator = document.createElement('span');
            indicator.id = 'connection-status';
            indicator.className = 'badge bg-secondary me-2';
            
            // Try to add it to the header area
            const headerArea = document.querySelector('.col-md-4.text-end');
            if (headerArea) {
                headerArea.prepend(indicator);
            }
        }
        
        if (this.isConnected) {
            indicator.innerHTML = '<i class="fas fa-wifi text-success"></i> Real-time';
            indicator.className = 'badge bg-success me-2';
        } else if (this.updateInterval) {
            indicator.innerHTML = '<i class="fas fa-sync-alt text-info"></i> Polling';
            indicator.className = 'badge bg-info me-2';
        } else {
            indicator.innerHTML = '<i class="fas fa-exclamation-triangle text-danger"></i> Offline';
            indicator.className = 'badge bg-danger me-2';
        }
    }
    
    // Public methods for external use
    forceUpdate() {
        this.pollForUpdates();
    }
    
    getStatus() {
        return {
            websocket: this.isConnected,
            polling: !!this.updateInterval,
            retries: this.connectionRetries
        };
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        window.dashboardRealTime = new DashboardRealTime();
        
        // Expose debugging functions
        window.debugDashboard = () => {
            console.log('Dashboard Real-Time Status:', window.dashboardRealTime.getStatus());
        };
        
        window.forceDashboardUpdate = () => {
            window.dashboardRealTime.forceUpdate();
        };
        
        console.log('✅ Dashboard Real-Time System Initialized');
    }, 1000);
});