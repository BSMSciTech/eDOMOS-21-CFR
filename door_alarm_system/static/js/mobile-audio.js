// Enhanced Audio Manager for Mobile Notifications
class MobileAudioManager {
    constructor() {
        this.audioContext = null;
        this.ringtones = new Map();
        this.isPlaying = false;
        this.currentAudio = null;
        this.vibrationPattern = [200, 100, 200, 100, 200];
        this.defaultRingtone = 'default';
        this.vibrationEnabled = true;
        this.persistentNotifications = true;
        this.wakeLock = null;
        this.vibrationInterval = null;
        this.autoStopTimeout = null;
        this.activeNotifications = []; // Track notifications to close them
        this.isAlarmTriggered = false; // Track if this is a triggered alarm vs door sound
        this.init();
    }

    async init() {
        // Initialize Web Audio API for better mobile support
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Web Audio API not supported, falling back to HTML5 Audio');
        }

        // Load default ringtones
        await this.loadRingtones();
        
        // Request notification permissions
        await this.requestPermissions();
    }

    async requestPermissions() {
        // Note: Don't auto-request permissions in constructor
        // Let user explicitly request them via button
        console.log('MobileAudioManager ready - permissions can be requested via UI');
    }

    async loadRingtones() {
        const ringtones = {
            'default': '/static/audio/alarm_default.wav',
            'urgent': '/static/audio/alarm_urgent.wav',
            'gentle': '/static/audio/alarm_gentle.wav',
            'classic': '/static/audio/alarm_classic.wav',
            'siren': '/static/audio/alarm_siren.wav'
        };

        for (const [name, url] of Object.entries(ringtones)) {
            try {
                const audio = new Audio(url);
                audio.preload = 'auto';
                audio.loop = true;
                this.ringtones.set(name, audio);
            } catch (e) {
                console.warn(`Failed to load ringtone: ${name}`);
            }
        }
    }

    async playAlarmRingtone(ringtoneType = 'default', duration = 30000, isTriggeredAlarm = false) {
        // Stop any currently playing alarms first
        if (this.isPlaying) {
            this.stopAlarm();
        }

        const audio = this.ringtones.get(ringtoneType) || this.ringtones.get('default');
        if (!audio) return;

        try {
            // Resume audio context if suspended (mobile requirement)
            if (this.audioContext && this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            // Set maximum volume
            audio.volume = 1.0;
            
            // Determine if this should loop based on duration
            // Short durations (< 5 seconds) = single play, longer = loop
            const shouldLoop = duration >= 5000;
            audio.loop = shouldLoop;
            
            // Track if this is a triggered alarm
            this.isAlarmTriggered = isTriggeredAlarm;
            
            console.log(`🔊 Playing alarm: ${ringtoneType} for ${duration}ms (loop: ${shouldLoop}, triggered: ${isTriggeredAlarm})`);
            
            // Play audio
            await audio.play();
            this.currentAudio = audio;
            this.isPlaying = true;

            // Start vibration pattern (if supported)
            this.startVibration();

            // Show persistent notification
            this.showAlarmNotification(ringtoneType);

            // Auto-stop after duration
            this.autoStopTimeout = setTimeout(() => {
                console.log('⏰ Auto-stopping alarm after duration');
                this.stopAlarm();
            }, duration);

            return true;
        } catch (error) {
            console.error('Failed to play alarm:', error);
            // Fallback to system notification
            this.showAlarmNotification(ringtoneType);
            return false;
        }
    }

    stopAlarm() {
        console.log('🛑 Stopping all alarms...');
        
        // Stop current audio
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            this.currentAudio.loop = false; // Disable loop
            this.currentAudio = null;
        }
        
        // Stop ALL ringtone audio elements (belt and suspenders approach)
        this.ringtones.forEach((audio, name) => {
            try {
                audio.pause();
                audio.currentTime = 0;
                audio.loop = false;
                console.log(`🔇 Stopped ringtone: ${name}`);
            } catch (e) {
                console.warn(`⚠️ Error stopping ${name}:`, e);
            }
        });
        
        this.isPlaying = false;
        this.isAlarmTriggered = false; // Reset alarm triggered state
        this.stopVibration();
        
        // Clear any auto-stop timeouts
        if (this.autoStopTimeout) {
            clearTimeout(this.autoStopTimeout);
            this.autoStopTimeout = null;
        }
        
        // Release wake lock
        if (this.wakeLock) {
            this.wakeLock.release().catch(e => console.warn('Wake lock release error:', e));
            this.wakeLock = null;
        }
        
        // Close any existing notifications
        this.closeAllNotifications();
        
        console.log('✅ All alarms stopped');
    }

    startVibration() {
        if (this.vibrationEnabled && 'vibrate' in navigator) {
            // Different vibration patterns based on audio duration/type
            if (this.currentAudio && this.currentAudio.loop) {
                // Continuous vibration pattern for looping alarms
                this.vibrationInterval = setInterval(() => {
                    navigator.vibrate(this.vibrationPattern);
                }, 1000);
            } else {
                // Single vibration for single-play sounds
                navigator.vibrate(this.vibrationPattern);
            }
        }
    }

    // Method to play single sound (no loop, short duration)
    async playSingleSound(ringtoneType = 'default', vibrate = true) {
        const audio = this.ringtones.get(ringtoneType) || this.ringtones.get('default');
        if (!audio) return false;

        try {
            // Resume audio context if suspended
            if (this.audioContext && this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            // Clone audio for single play to avoid interfering with looped versions
            const singleAudio = audio.cloneNode();
            singleAudio.volume = 1.0;
            singleAudio.loop = false;

            console.log(`🔊 Playing single sound: ${ringtoneType}`);

            await singleAudio.play();

            // Single vibration if enabled
            if (vibrate && this.vibrationEnabled && 'vibrate' in navigator) {
                navigator.vibrate(this.vibrationPattern);
            }

            return true;
        } catch (error) {
            console.error('Failed to play single sound:', error);
            return false;
        }
    }

    stopVibration() {
        if (this.vibrationInterval) {
            clearInterval(this.vibrationInterval);
            this.vibrationInterval = null;
        }
        if ('vibrate' in navigator) {
            navigator.vibrate(0); // Stop vibration
        }
    }

    closeAllNotifications() {
        // Close all tracked notifications
        this.activeNotifications.forEach(notification => {
            try {
                notification.close();
            } catch (e) {
                console.warn('Error closing notification:', e);
            }
        });
        this.activeNotifications = [];
    }

    showAlarmNotification(ringtoneType) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification('🚨 eDOMOS DOOR ALARM!', {
                body: `Door security breach detected! Alarm type: ${ringtoneType}`,
                icon: '/static/icons/icon-192x192.png',
                badge: '/static/icons/icon-72x72.png',
                tag: 'door-alarm',
                requireInteraction: true, // Keeps notification until user interacts
                vibrate: this.vibrationPattern,
                actions: [
                    {
                        action: 'stop',
                        title: 'Stop Alarm'
                    },
                    {
                        action: 'view',
                        title: 'View Dashboard'
                    }
                ]
            });

            // Track notification for later cleanup
            this.activeNotifications.push(notification);

            notification.onclick = () => {
                this.stopAlarm(); // Stop alarm when notification is clicked
                window.focus();
                notification.close();
            };

            // Handle notification actions
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.addEventListener('message', (event) => {
                    if (event.data && event.data.action === 'stop') {
                        this.stopAlarm();
                    }
                });
            }
        }
    }

    // Method to test ringtones
    async testRingtone(ringtoneType) {
        await this.playAlarmRingtone(ringtoneType, 5000); // Play for 5 seconds
    }

    // Alias method for compatibility with dashboard calls
    async playAlarmSound(ringtoneType = 'default', duration = 3000) {
        return await this.playAlarmRingtone(ringtoneType, duration);
    }

    // Method to set default ringtone
    setDefaultRingtone(ringtoneType) {
        this.defaultRingtone = ringtoneType;
        localStorage.setItem('edomos_default_ringtone', ringtoneType);
        console.log(`Default ringtone set to: ${ringtoneType}`);
    }

    // Method to request notification permission
    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            console.log(`Notification permission: ${permission}`);
            return permission === 'granted';
        }
        return false;
    }

    // Method to initialize audio context (for user gesture requirement)
    async initializeAudio() {
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                console.log('Audio context created');
            } catch (e) {
                console.warn('Web Audio API not supported, using fallback');
            }
        }

        if (this.audioContext && this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
            console.log('Audio context resumed');
        }

        return this.audioContext && this.audioContext.state === 'running';
    }

    // Method to show notification (used by dashboard)
    showNotification(title, body, persistent = false) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification(title, {
                body: body,
                icon: '/static/icons/icon-192x192.png',
                badge: '/static/icons/icon-72x72.png',
                tag: persistent ? 'persistent-alarm' : 'notification',
                requireInteraction: persistent,
                vibrate: this.vibrationPattern
            });

            notification.onclick = () => {
                window.focus();
                notification.close();
            };

            return notification;
        }
        return null;
    }

    // Method to check if there's an active triggered alarm
    hasActiveTriggeredAlarm() {
        return this.isPlaying && this.isAlarmTriggered;
    }

    // Get list of available ringtones
    getAvailableRingtones() {
        return Array.from(this.ringtones.keys());
    }

    // Set custom ringtone from user's device
    async setCustomRingtone(file) {
        if (file && file.type.startsWith('audio/')) {
            const url = URL.createObjectURL(file);
            const audio = new Audio(url);
            audio.preload = 'auto';
            audio.loop = true;
            this.ringtones.set('custom', audio);
            
            // Save to localStorage
            localStorage.setItem('customRingtone', url);
            return true;
        }
        return false;
    }
}

// Initialize global audio manager
window.mobileAudioManager = new MobileAudioManager();

// Global emergency stop function
window.emergencyStopAllAlarms = function() {
    console.log('🚨 EMERGENCY STOP ALL ALARMS TRIGGERED');
    
    if (window.mobileAudioManager) {
        window.mobileAudioManager.stopAlarm();
    }
    
    // Also stop any HTML5 audio elements on the page
    const allAudioElements = document.querySelectorAll('audio');
    allAudioElements.forEach(audio => {
        audio.pause();
        audio.currentTime = 0;
    });
    
    // Show confirmation
    if (typeof showNotification === 'function') {
        showNotification('🛑 All alarms stopped!', 'success');
    }
    
    console.log('✅ Emergency stop complete');
};

// Make emergency stop available globally
window.stopAllAlarms = window.emergencyStopAllAlarms;

// Enhanced WebSocket handler for mobile alerts
function handleDoorAlarmMobile(eventData) {
    if (eventData.event_type === 'door_opened' || eventData.alarm_status === true) {
        // Get user's preferred ringtone
        const preferredRingtone = localStorage.getItem('preferredRingtone') || 'urgent';
        
        // Play alarm with vibration and notifications
        window.mobileAudioManager.playAlarmRingtone(preferredRingtone, 60000); // 1 minute
        
        // Wake up the device screen
        if ('screen' in navigator && 'orientation' in screen) {
            screen.orientation.lock('portrait').catch(() => {});
        }
    }
}

// Settings UI for ringtone selection
function createRingtoneSettings() {
    const settingsHTML = `
        <div class="ringtone-settings" style="margin: 20px 0;">
            <h3>🔊 Alarm Settings</h3>
            
            <div class="setting-group">
                <label for="ringtone-select">Alarm Ringtone:</label>
                <select id="ringtone-select" class="form-control">
                    <option value="default">Default Alarm</option>
                    <option value="urgent">Urgent Siren</option>
                    <option value="gentle">Gentle Alert</option>
                    <option value="classic">Classic Bell</option>
                    <option value="siren">Emergency Siren</option>
                </select>
                <button onclick="testSelectedRingtone()" class="btn btn-secondary">Test Sound</button>
            </div>

            <div class="setting-group">
                <label for="custom-ringtone">Custom Ringtone:</label>
                <input type="file" id="custom-ringtone" accept="audio/*" onchange="handleCustomRingtone(this)">
            </div>

            <div class="setting-group">
                <label>
                    <input type="checkbox" id="vibration-enabled" checked> Enable Vibration
                </label>
            </div>

            <div class="setting-group">
                <label>
                    <input type="checkbox" id="persistent-notifications" checked> Persistent Notifications
                </label>
            </div>
        </div>
    `;
    
    return settingsHTML;
}

function testSelectedRingtone() {
    const select = document.getElementById('ringtone-select');
    const ringtoneType = select.value;
    window.mobileAudioManager.testRingtone(ringtoneType);
}

function handleCustomRingtone(input) {
    if (input.files && input.files[0]) {
        window.mobileAudioManager.setCustomRingtone(input.files[0]);
    }
}

// Auto-start on page load
document.addEventListener('DOMContentLoaded', function() {
    // Request permissions on first user interaction
    document.addEventListener('click', function() {
        window.mobileAudioManager.requestPermissions();
    }, { once: true });
});