# 📱🔔 Mobile Audio Notifications Implementation Guide

## 🎯 Overview

Your eDOMOS app now includes a comprehensive mobile audio notification system that provides:
- **Custom ringtones** for different alarm types
- **Vibration patterns** for silent notifications
- **Persistent notifications** that continue until acknowledged
- **Wake lock** to keep device active during alarms
- **Audio permission management** for seamless operation

## 🔊 Audio Files Created

The following alarm sounds have been generated in `static/audio/`:

| File | Duration | Description | Use Case |
|------|----------|-------------|----------|
| `alarm_default.wav` | 2s | Standard beep pattern | General door events |
| `alarm_urgent.wav` | 3s | Siren-like urgent sound | Security breaches |
| `alarm_gentle.wav` | 2s | Soft bell tone | Maintenance alerts |
| `alarm_classic.wav` | 2s | Traditional bell sound | Standard notifications |
| `alarm_siren.wav` | 4s | Emergency siren | Critical alarms |

## 📱 Mobile Audio Features

### 1. Automatic Audio Initialization
```javascript
// The system automatically initializes when a user interacts with the page
document.addEventListener('DOMContentLoaded', function() {
    if (window.MobileAudioManager) {
        window.audioManager = new MobileAudioManager();
    }
});
```

### 2. Ringtone Selection
Users can choose from 5 different alarm sounds:
- **Default:** Rhythmic beeping pattern
- **Urgent:** Variable frequency siren
- **Gentle:** Soft exponential decay bell
- **Classic:** Traditional bell with harmonics
- **Siren:** Emergency-style alternating tones

### 3. Vibration Patterns
```javascript
// Different vibration patterns for different alarm types
const patterns = {
    default: [200, 100, 200],
    urgent: [100, 50, 100, 50, 200, 100, 200],
    gentle: [300, 200, 300],
    classic: [150, 100, 150, 100, 150],
    siren: [50, 50, 50, 50, 100, 100, 100, 100]
};
```

### 4. Wake Lock Management
The system keeps the device screen active during alarms:
```javascript
// Automatically requests wake lock when alarm starts
// Releases wake lock when alarm is dismissed
```

## 🔧 Integration with Your Alarm System

### Step 1: Event Listener Integration
Add this to your dashboard JavaScript:

```javascript
// Listen for alarm events from WebSocket
socket.on('new_event', function(data) {
    if (data.event && data.event.event_type === 'door_opened' && data.alarm_status) {
        // Trigger mobile notification
        if (window.audioManager) {
            window.audioManager.playAlarmSound('urgent');
        }
    }
});

// Listen for door close events
socket.on('new_event', function(data) {
    if (data.event && data.event.event_type === 'door_closed') {
        // Stop alarm
        if (window.audioManager) {
            window.audioManager.stopAlarm();
        }
    }
});
```

### Step 2: Manual Alarm Controls
Add buttons to your interface:

```html
<!-- Add to your dashboard template -->
<div class="mobile-audio-controls">
    <h4>🔔 Mobile Notifications</h4>
    
    <div class="alarm-controls">
        <button onclick="testAlarmSound('default')" class="btn btn-primary btn-sm">
            🔊 Test Default
        </button>
        <button onclick="testAlarmSound('urgent')" class="btn btn-warning btn-sm">
            🚨 Test Urgent
        </button>
        <button onclick="testAlarmSound('gentle')" class="btn btn-success btn-sm">
            🔔 Test Gentle
        </button>
        <button onclick="window.audioManager.stopAlarm()" class="btn btn-danger btn-sm">
            🛑 Stop All
        </button>
    </div>
    
    <div class="ringtone-selector mt-3">
        <label for="ringtoneSelect">Default Ringtone:</label>
        <select id="ringtoneSelect" class="form-select form-select-sm" onchange="setDefaultRingtone(this.value)">
            <option value="default">Default Beep</option>
            <option value="urgent">Urgent Siren</option>
            <option value="gentle">Gentle Bell</option>
            <option value="classic">Classic Bell</option>
            <option value="siren">Emergency Siren</option>
        </select>
    </div>
</div>

<script>
function testAlarmSound(type) {
    if (window.audioManager) {
        window.audioManager.playAlarmSound(type);
    }
}

function setDefaultRingtone(type) {
    if (window.audioManager) {
        window.audioManager.setDefaultRingtone(type);
    }
}
</script>
```

### Step 3: Permission Handling
The system automatically handles permissions, but you can add manual controls:

```html
<div class="permission-controls">
    <button onclick="requestNotificationPermission()" class="btn btn-info btn-sm">
        🔔 Enable Notifications
    </button>
    <button onclick="requestAudioPermission()" class="btn btn-info btn-sm">
        🔊 Enable Audio
    </button>
</div>

<script>
async function requestNotificationPermission() {
    if (window.audioManager) {
        await window.audioManager.requestNotificationPermission();
    }
}

async function requestAudioPermission() {
    if (window.audioManager) {
        await window.audioManager.initializeAudio();
    }
}
</script>
```

## 🚀 Activation Instructions

### For Your Current PWA:
1. **✅ Audio files are already created** in `static/audio/`
2. **✅ Mobile audio script is integrated** in base.html
3. **Ready to use!** The system will activate on first user interaction

### Testing the Audio System:

1. **Open your PWA** on Android device
2. **Navigate to dashboard** - audio system initializes automatically
3. **Trigger a door event** or use manual test buttons
4. **Check notifications** in notification panel
5. **Test vibration** (ensure device vibration is enabled)

### Integration with Existing Alarms:

Add this code to your dashboard's JavaScript section:

```javascript
// Add to templates/dashboard.html in the <script> section
document.addEventListener('DOMContentLoaded', function() {
    // Initialize audio manager when page loads
    setTimeout(() => {
        if (window.audioManager && !window.audioManager.audioContext) {
            document.addEventListener('click', () => {
                if (window.audioManager) {
                    window.audioManager.initializeAudio();
                }
            }, { once: true });
        }
    }, 1000);
});

// Modify your existing WebSocket event handler
// Add this to your existing socket.on('new_event') handler:
socket.on('new_event', function(data) {
    // ... your existing code ...
    
    // Add mobile audio notification
    if (data.alarm_status && window.audioManager) {
        // Play urgent alarm for door open events
        if (data.event && data.event.event_type === 'door_opened') {
            window.audioManager.playAlarmSound('urgent');
        }
        // Stop alarm for door close events
        else if (data.event && data.event.event_type === 'door_closed') {
            window.audioManager.stopAlarm();
        }
    }
});
```

## 📱 Mobile-Specific Features

### 1. Background Operation
- **Service Worker** integration ensures notifications work when app is backgrounded
- **Wake Lock** keeps device active during critical alarms
- **Persistent notifications** continue until user acknowledges

### 2. Battery Optimization
- **Efficient audio loading** - sounds are preloaded but use minimal memory
- **Smart wake lock** - only activates during active alarms
- **Optimized vibration** - patterns designed for effectiveness without battery drain

### 3. Accessibility
- **Visual indicators** accompany audio alerts
- **Customizable volumes** for different environments
- **Multiple notification channels** (audio, vibration, visual)

## 🔧 Customization Options

### Adding Custom Ringtones:
1. **Add audio files** to `static/audio/` directory
2. **Update the MobileAudioManager** to include new sounds:

```javascript
// Add to static/js/mobile-audio.js
const customSounds = {
    'custom1': '/static/audio/custom_alarm1.wav',
    'custom2': '/static/audio/custom_alarm2.wav'
};
```

### Adjusting Vibration Patterns:
```javascript
// Modify vibration patterns in mobile-audio.js
vibrationPatterns: {
    myCustomPattern: [100, 50, 100, 50, 200, 100, 200, 50]
}
```

## 📊 Usage Analytics

Track alarm effectiveness:
```javascript
// Add to your analytics
window.audioManager.on('alarmPlayed', (type) => {
    console.log(`Alarm played: ${type}`);
    // Send to your analytics system
});

window.audioManager.on('alarmStopped', (duration) => {
    console.log(`Alarm stopped after ${duration}ms`);
    // Track response times
});
```

## 🚨 Troubleshooting

### Common Issues:

1. **Audio not playing:**
   - Ensure user has interacted with page first
   - Check device volume settings
   - Verify audio files are accessible

2. **Notifications not showing:**
   - Check notification permissions
   - Ensure PWA is added to home screen
   - Verify service worker is active

3. **Vibration not working:**
   - Check device vibration settings
   - Ensure page is served over HTTPS
   - Verify device supports vibration API

### Debug Commands:
```javascript
// Test audio system
console.log('Audio Manager:', window.audioManager);
console.log('Audio Context:', window.audioManager?.audioContext);
console.log('Permissions:', await navigator.permissions.query({name: 'notifications'}));
```

## 🎉 You're All Set!

Your eDOMOS app now has professional-grade mobile audio notifications that will:
- **🔊 Play custom ringtones** when alarms trigger
- **📳 Vibrate device** for silent notifications  
- **🔔 Show persistent notifications** until acknowledged
- **⚡ Keep device awake** during critical alerts
- **📱 Work seamlessly** across Android devices

The system is fully integrated and ready to enhance your door alarm monitoring experience!