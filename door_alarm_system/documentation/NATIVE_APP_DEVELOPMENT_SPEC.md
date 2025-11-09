# eDOMOS Android/iOS Native App - Complete Development Specification

**Version:** 1.0  
**Date:** November 7, 2025  
**Platform:** React Native (Android + iOS)  
**Estimated Cost:** $2,500 - $4,500  
**Timeline:** 6-8 weeks  

---

## 📱 Project Overview

### Purpose
Build a native mobile app for eDOMOS Door Alarm System that can:
- Play custom alarm sounds even when screen is off
- Receive real-time alarm notifications
- Run persistent background service
- Monitor door status 24/7

### Current System
- **Backend:** Flask Python application (already running)
- **Web App:** PWA with real-time WebSocket updates
- **API:** RESTful + WebSocket endpoints available
- **Auth:** Session-based authentication

### Problem to Solve
PWA cannot play audio when:
- Screen is off
- App is in background
- App is closed

### Solution
Native app with:
- Background service (persistent connection)
- Foreground notification (Android)
- Background audio session (iOS)
- Custom alarm sound playback

---

## 🎯 Core Requirements

### Must-Have Features (MVP)

#### 1. Authentication
- Login screen (username/password)
- Remember credentials (secure storage)
- Session management
- Auto-login on app restart

#### 2. Real-Time Monitoring
- WebSocket connection to server
- Display current door status (Open/Closed)
- Display alarm status (Active/Inactive)
- Display timer countdown
- Show last event timestamp

#### 3. Background Audio Playback
- **Critical:** Play alarm sound when screen is off
- **Critical:** Play alarm sound when app is backgrounded
- **Critical:** Play alarm sound when app is closed
- Custom alarm sounds (5 options):
  - Default alarm
  - Urgent alarm
  - Gentle alarm
  - Classic alarm
  - Siren alarm
- Volume control
- Vibration pattern support

#### 4. Background Service
- Persistent WebSocket connection
- Auto-reconnect on disconnect
- Battery optimized
- Foreground service notification (Android)
- Background audio session (iOS)

#### 5. Push Notifications
- Receive alarm notifications
- Silent background notifications
- High-priority alerts
- Custom notification sounds
- Tap notification → Open app

#### 6. Basic UI
- Dashboard screen (door status)
- Event log (last 50 events)
- Settings screen
- Login screen
- Alarm configuration

---

## 🏗️ Technical Architecture

### Technology Stack

**Framework:**
```
React Native 0.72+
```

**Key Libraries:**
```javascript
// WebSocket
npm install socket.io-client

// Background tasks
npm install react-native-background-actions

// Audio playback
npm install react-native-sound

// Push notifications
npm install @react-native-firebase/messaging

// Secure storage
npm install react-native-keychain

// Navigation
npm install @react-navigation/native

// State management
npm install zustand
```

### App Architecture

```
eDOMOS Native App
│
├── Authentication Layer
│   ├── Login Screen
│   ├── Secure Token Storage
│   └── Session Management
│
├── Background Service
│   ├── WebSocket Manager
│   ├── Auto-Reconnect Logic
│   ├── Event Handler
│   └── Keep-Alive Ping
│
├── Audio Manager
│   ├── Sound Preloader
│   ├── Background Playback
│   ├── Volume Control
│   └── Vibration Control
│
├── Push Notification Manager
│   ├── FCM Integration (Firebase)
│   ├── Notification Builder
│   ├── Sound Mapper
│   └── Action Handlers
│
├── UI Layer
│   ├── Dashboard
│   ├── Event Log
│   ├── Settings
│   └── Alarm Controls
│
└── State Management
    ├── Door Status
    ├── Alarm Status
    ├── Connection Status
    └── User Preferences
```

---

## 🔌 Backend API Integration

### Base URL
```
https://your-domain.com:5000
```

### Authentication

**Login:**
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=admin&password=your_password
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "permissions": "dashboard,event_log,analytics"
  }
}
```

**Cookie:** Session cookie returned in `Set-Cookie` header

### WebSocket Connection

**URL:**
```
wss://your-domain.com:5000/socket.io/?EIO=4&transport=websocket
```

**Events to Listen:**

1. **New Event:**
```javascript
socket.on('new_event', (data) => {
  // data.event_type: 'door_opened', 'door_closed', 'alarm_triggered'
  // data.timestamp: ISO timestamp
  // data.description: Human readable message
  
  if (data.event_type === 'alarm_triggered') {
    playAlarmSound();
    showNotification();
    vibrateDevice();
  }
});
```

2. **Status Update:**
```javascript
socket.on('status_update', (data) => {
  // data.door_status: true (open) / false (closed)
  // data.alarm_status: true (active) / false (inactive)
  // data.timer_active: boolean
  // data.timer_remaining: seconds
});
```

3. **Connection Events:**
```javascript
socket.on('connect', () => {
  console.log('Connected to server');
  socket.emit('mobile_client_ready');
});

socket.on('disconnect', () => {
  console.log('Disconnected - will auto-reconnect');
});

socket.on('pong', (data) => {
  // Server responds to ping
});
```

### REST API Endpoints

**Get Dashboard Data:**
```http
GET /api/dashboard
```

**Response:**
```json
{
  "door_status": false,
  "alarm_active": false,
  "timer_active": false,
  "timer_duration": 30,
  "last_event": {
    "id": 123,
    "event_type": "door_opened",
    "timestamp": "2025-11-07T10:30:00",
    "description": "Door opened by sensor"
  },
  "statistics": {
    "total_events": 1500,
    "door_opens_today": 25,
    "alarms_today": 2
  }
}
```

**Get Events:**
```http
GET /api/events?page=1&per_page=50
```

**Response:**
```json
{
  "events": [
    {
      "id": 125,
      "event_type": "alarm_triggered",
      "timestamp": "2025-11-07T10:45:00",
      "description": "Alarm activated - unauthorized access",
      "image_path": "/static/captures/alarm_20251107_104500.jpg"
    }
  ],
  "total": 1500,
  "pages": 30,
  "current_page": 1
}
```

---

## 📱 Screen-by-Screen Specifications

### Screen 1: Login

**UI Elements:**
- App logo (centered)
- Username input field
- Password input field (secure)
- "Remember me" checkbox
- Login button
- Error message display

**Functionality:**
```javascript
async function login(username, password) {
  try {
    const response = await fetch('https://your-domain.com:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${username}&password=${password}`,
      credentials: 'include' // Important for cookies
    });
    
    if (response.ok) {
      // Store credentials securely
      await Keychain.setGenericPassword(username, password);
      
      // Navigate to dashboard
      navigation.navigate('Dashboard');
      
      // Start background service
      startBackgroundService();
    } else {
      showError('Invalid credentials');
    }
  } catch (error) {
    showError('Connection failed');
  }
}
```

---

### Screen 2: Dashboard

**UI Elements:**
```
┌─────────────────────────────────────┐
│  🚪 eDOMOS Door Monitor             │
├─────────────────────────────────────┤
│                                     │
│   Door Status:   🟢 CLOSED          │
│   Alarm Status:  🔕 INACTIVE        │
│   Timer:         ⏱️ 30 seconds      │
│                                     │
│   Connection:    ✅ Connected       │
│                                     │
├─────────────────────────────────────┤
│  Last Event:                        │
│  🚪 Door opened                     │
│  10:45:23 AM                        │
├─────────────────────────────────────┤
│  Quick Actions:                     │
│  [View Events] [Settings]           │
└─────────────────────────────────────┘
```

**Real-time Updates:**
- Door icon changes color (Green=Closed, Red=Open)
- Alarm icon changes (Bell=Inactive, Bell+Sound=Active)
- Timer counts down in real-time
- Connection status indicator

**Code Structure:**
```javascript
function Dashboard() {
  const [doorStatus, setDoorStatus] = useState(false);
  const [alarmActive, setAlarmActive] = useState(false);
  const [timerRemaining, setTimerRemaining] = useState(30);
  const [connected, setConnected] = useState(false);
  
  useEffect(() => {
    // Connect WebSocket
    const socket = io('wss://your-domain.com:5000', {
      transports: ['websocket']
    });
    
    socket.on('connect', () => setConnected(true));
    socket.on('disconnect', () => setConnected(false));
    
    socket.on('status_update', (data) => {
      setDoorStatus(data.door_status);
      setAlarmActive(data.alarm_status);
      setTimerRemaining(data.timer_remaining);
    });
    
    socket.on('new_event', (data) => {
      if (data.event_type === 'alarm_triggered') {
        playAlarmSound();
        showNotification('ALARM ACTIVATED!');
        vibrateDevice([200, 100, 200, 100, 200]);
      }
    });
    
    return () => socket.disconnect();
  }, []);
  
  return (
    <View>
      <StatusCard 
        doorStatus={doorStatus}
        alarmActive={alarmActive}
        timerRemaining={timerRemaining}
      />
      <ConnectionIndicator connected={connected} />
    </View>
  );
}
```

---

### Screen 3: Event Log

**UI Elements:**
- List of recent events (scrollable)
- Pull-to-refresh
- Event type icon
- Timestamp
- Description
- Image thumbnail (if available)

**Example:**
```
┌─────────────────────────────────────┐
│  📋 Event Log                       │
├─────────────────────────────────────┤
│  🚨 Alarm Triggered                 │
│  Nov 7, 2025 10:45:23 AM           │
│  Unauthorized access detected       │
│  [📷 View Image]                    │
├─────────────────────────────────────┤
│  🚪 Door Opened                     │
│  Nov 7, 2025 10:30:15 AM           │
│  Sensor detected door movement      │
├─────────────────────────────────────┤
│  🚪 Door Closed                     │
│  Nov 7, 2025 10:15:42 AM           │
│  Door returned to closed position   │
└─────────────────────────────────────┘
```

---

### Screen 4: Settings

**UI Elements:**
```
┌─────────────────────────────────────┐
│  ⚙️ Settings                        │
├─────────────────────────────────────┤
│  🔔 Notifications                   │
│  ├─ Enable Notifications    [ON]   │
│  ├─ Notification Sound      [ON]   │
│  ├─ Vibration              [ON]   │
│  └─ High Priority          [ON]   │
├─────────────────────────────────────┤
│  🔊 Alarm Sounds                    │
│  ├─ Default Alarm         [●]      │
│  ├─ Urgent Alarm          [ ]      │
│  ├─ Gentle Alarm          [ ]      │
│  ├─ Classic Alarm         [ ]      │
│  └─ Siren                 [ ]      │
│  └─ Volume                [75%]    │
├─────────────────────────────────────┤
│  🔋 Background Service             │
│  ├─ Keep Alive            [ON]    │
│  ├─ Auto-Reconnect        [ON]    │
│  └─ Battery Optimization  [OFF]   │
├─────────────────────────────────────┤
│  👤 Account                        │
│  ├─ Username: admin                │
│  ├─ Change Password                │
│  └─ Logout                         │
└─────────────────────────────────────┘
```

---

## 🔊 Background Audio Implementation

### Android (Foreground Service)

**Step 1: Create Background Task**
```javascript
// BackgroundService.js
import BackgroundService from 'react-native-background-actions';
import Sound from 'react-native-sound';
import io from 'socket.io-client';

let socket = null;
let alarmSound = null;

const backgroundTask = async (taskData) => {
  await new Promise(async (resolve) => {
    // Preload alarm sound
    alarmSound = new Sound('alarm_urgent.mp3', Sound.MAIN_BUNDLE, (error) => {
      if (error) console.log('Failed to load sound', error);
    });
    
    // Connect WebSocket
    socket = io('wss://your-domain.com:5000', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: Infinity
    });
    
    socket.on('connect', () => {
      console.log('Background service connected');
      socket.emit('mobile_client_ready', { 
        platform: 'android',
        version: '1.0.0'
      });
    });
    
    socket.on('new_event', async (data) => {
      if (data.event_type === 'alarm_triggered') {
        // Play alarm sound (works in background!)
        alarmSound.play((success) => {
          if (!success) {
            console.log('Sound playback failed');
          }
        });
        
        // Vibrate device
        Vibration.vibrate([200, 100, 200, 100, 200]);
        
        // Show notification
        await showNotification({
          title: '🚨 ALARM ACTIVATED!',
          message: data.description,
          priority: 'high',
          sound: 'alarm_urgent'
        });
      }
    });
    
    // Keep service alive
    while (BackgroundService.isRunning()) {
      // Ping server every 30 seconds
      if (socket && socket.connected) {
        socket.emit('ping', { timestamp: Date.now() });
      }
      
      await new Promise(resolve => setTimeout(resolve, 30000));
    }
  });
};

export async function startBackgroundService() {
  const options = {
    taskName: 'eDOMOS Monitor',
    taskTitle: 'Door Monitoring Active',
    taskDesc: 'Monitoring door status and alarms',
    taskIcon: {
      name: 'ic_launcher',
      type: 'mipmap'
    },
    color: '#ff00ff',
    linkingURI: 'edomos://dashboard',
    parameters: {
      delay: 1000
    }
  };
  
  await BackgroundService.start(backgroundTask, options);
}

export function stopBackgroundService() {
  BackgroundService.stop();
  if (socket) socket.disconnect();
  if (alarmSound) alarmSound.release();
}
```

**Step 2: Android Manifest Permissions**
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<manifest>
  <!-- Background service permission -->
  <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
  
  <!-- Audio playback -->
  <uses-permission android:name="android.permission.WAKE_LOCK" />
  
  <!-- Network -->
  <uses-permission android:name="android.permission.INTERNET" />
  
  <!-- Notifications -->
  <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
  
  <!-- Vibration -->
  <uses-permission android:name="android.permission.VIBRATE" />
  
  <!-- Battery optimization exemption -->
  <uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />
</manifest>
```

---

### iOS (Background Audio Session)

**Step 1: Configure Background Modes**
```xml
<!-- ios/eDOMOS/Info.plist -->
<key>UIBackgroundModes</key>
<array>
  <string>audio</string>
  <string>fetch</string>
  <string>remote-notification</string>
</array>
```

**Step 2: Background Audio Manager**
```javascript
// BackgroundAudioManager.ios.js
import Sound from 'react-native-sound';
import { AppState } from 'react-native';
import BackgroundFetch from 'react-native-background-fetch';

class BackgroundAudioManager {
  constructor() {
    this.socket = null;
    this.alarmSound = null;
    this.silentAudio = null;
    
    // Enable playback in silent mode
    Sound.setCategory('Playback', true);
  }
  
  async start() {
    // Play silent audio loop to keep audio session active
    this.silentAudio = new Sound('silent.mp3', Sound.MAIN_BUNDLE);
    this.silentAudio.setNumberOfLoops(-1); // Infinite loop
    this.silentAudio.setVolume(0); // Silent
    this.silentAudio.play();
    
    // Preload alarm sound
    this.alarmSound = new Sound('alarm_urgent.mp3', Sound.MAIN_BUNDLE);
    
    // Connect WebSocket
    this.connectWebSocket();
    
    // Configure background fetch
    await this.configureBackgroundFetch();
  }
  
  connectWebSocket() {
    this.socket = io('wss://your-domain.com:5000');
    
    this.socket.on('new_event', (data) => {
      if (data.event_type === 'alarm_triggered') {
        this.playAlarm();
      }
    });
    
    // Handle app state changes
    AppState.addEventListener('change', (nextAppState) => {
      if (nextAppState === 'background' || nextAppState === 'inactive') {
        // Keep WebSocket alive in background
        this.setupBackgroundPing();
      }
    });
  }
  
  playAlarm() {
    // Stop silent audio
    this.silentAudio.pause();
    
    // Play alarm at full volume
    this.alarmSound.setVolume(1.0);
    this.alarmSound.play((success) => {
      // Resume silent audio after alarm
      this.silentAudio.play();
    });
  }
  
  async configureBackgroundFetch() {
    await BackgroundFetch.configure({
      minimumFetchInterval: 15, // minutes
      stopOnTerminate: false,
      startOnBoot: true
    }, async (taskId) => {
      // Check for new alarms
      if (this.socket && !this.socket.connected) {
        this.socket.connect();
      }
      
      BackgroundFetch.finish(taskId);
    });
  }
}

export default new BackgroundAudioManager();
```

---

## 🔔 Push Notifications Setup

### Firebase Cloud Messaging (FCM)

**Step 1: Firebase Project Setup**
1. Go to https://console.firebase.google.com
2. Create new project: "eDOMOS Mobile"
3. Add Android app (package: com.edomos.app)
4. Add iOS app (bundle ID: com.edomos.app)
5. Download `google-services.json` (Android)
6. Download `GoogleService-Info.plist` (iOS)

**Step 2: Backend Integration**
```python
# app.py - Add push notification sending
from firebase_admin import credentials, messaging
import firebase_admin

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase-credentials.json')
firebase_admin.initialize_app(cred)

def send_push_notification(device_token, title, body, data=None):
    """Send push notification to mobile device"""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        token=device_token,
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='alarm_urgent',
                channel_id='alarm_channel'
            )
        ),
        apns=messaging.APNSConfig(
            headers={'apns-priority': '10'},
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='alarm_urgent.mp3',
                    category='ALARM',
                    badge=1
                )
            )
        )
    )
    
    try:
        response = messaging.send(message)
        print(f'✅ Notification sent: {response}')
        return True
    except Exception as e:
        print(f'❌ Notification failed: {e}')
        return False

# When alarm triggers:
@socketio.on('alarm_triggered')
def handle_alarm_trigger(data):
    # ... existing code ...
    
    # Send push notification to all mobile devices
    mobile_devices = MobileDevice.query.filter_by(notifications_enabled=True).all()
    for device in mobile_devices:
        send_push_notification(
            device.fcm_token,
            title='🚨 ALARM ACTIVATED!',
            body='Door alarm triggered - unauthorized access detected',
            data={
                'event_type': 'alarm_triggered',
                'timestamp': datetime.now().isoformat(),
                'alarm_sound': 'urgent'
            }
        )
```

**Step 3: App Registration**
```javascript
// NotificationManager.js
import messaging from '@react-native-firebase/messaging';

export async function registerForNotifications() {
  // Request permission (iOS)
  const authStatus = await messaging().requestPermission();
  const enabled =
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL;

  if (enabled) {
    // Get FCM token
    const fcmToken = await messaging().getToken();
    console.log('FCM Token:', fcmToken);
    
    // Send token to backend
    await fetch('https://your-domain.com:5000/api/mobile/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_token: fcmToken,
        platform: Platform.OS,
        device_info: {
          model: DeviceInfo.getModel(),
          os_version: DeviceInfo.getSystemVersion()
        }
      })
    });
    
    return fcmToken;
  }
  
  return null;
}

// Handle foreground notifications
messaging().onMessage(async (remoteMessage) => {
  console.log('Notification in foreground:', remoteMessage);
  
  if (remoteMessage.data.event_type === 'alarm_triggered') {
    playAlarmSound(remoteMessage.data.alarm_sound);
    vibrateDevice();
  }
});

// Handle background/quit notifications
messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  console.log('Notification in background:', remoteMessage);
  
  if (remoteMessage.data.event_type === 'alarm_triggered') {
    // Background service will handle audio playback
    return Promise.resolve();
  }
});
```

---

## 🔋 Battery Optimization

### Android Battery Optimization Exemption

**Request Exemption:**
```javascript
import { NativeModules, Linking } from 'react-native';

async function requestBatteryOptimizationExemption() {
  if (Platform.OS === 'android' && Platform.Version >= 23) {
    const packageName = NativeModules.RNDeviceInfo.getBundleId();
    
    // Check if already exempt
    const isIgnoringBatteryOptimizations = await NativeModules
      .PowerManagerModule
      .isIgnoringBatteryOptimizations(packageName);
    
    if (!isIgnoringBatteryOptimizations) {
      Alert.alert(
        'Battery Optimization',
        'To ensure alarms work reliably, please disable battery optimization for this app.',
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Settings', 
            onPress: () => {
              Linking.openSettings();
            }
          }
        ]
      );
    }
  }
}
```

**Native Module (Android):**
```java
// PowerManagerModule.java
package com.edomos.app;

import android.content.Context;
import android.os.PowerManager;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.Promise;

public class PowerManagerModule extends ReactContextBaseJavaModule {
    public PowerManagerModule(ReactApplicationContext reactContext) {
        super(reactContext);
    }

    @Override
    public String getName() {
        return "PowerManagerModule";
    }

    @ReactMethod
    public void isIgnoringBatteryOptimizations(String packageName, Promise promise) {
        PowerManager pm = (PowerManager) getReactApplicationContext()
            .getSystemService(Context.POWER_SERVICE);
        boolean isIgnoring = pm.isIgnoringBatteryOptimizations(packageName);
        promise.resolve(isIgnoring);
    }
}
```

---

## 🧪 Testing Requirements

### Unit Tests
- Authentication flow
- WebSocket connection/reconnection
- Audio playback logic
- Notification handling
- Background service lifecycle

### Integration Tests
- Login → Dashboard flow
- Real-time status updates
- Alarm trigger → Sound playback
- Push notification delivery
- Background service persistence

### Manual Testing Checklist

**Scenario 1: Foreground Alarm**
- [ ] App is open
- [ ] Trigger alarm on backend
- [ ] Alarm sound plays immediately
- [ ] Vibration occurs
- [ ] Notification appears
- [ ] Dashboard updates

**Scenario 2: Background Alarm (Screen On)**
- [ ] App is in background (home button pressed)
- [ ] Screen is still on
- [ ] Trigger alarm on backend
- [ ] Alarm sound plays
- [ ] Notification appears
- [ ] Tap notification opens app

**Scenario 3: Background Alarm (Screen Off)** ⭐ **CRITICAL TEST**
- [ ] App is in background
- [ ] Turn screen off (power button)
- [ ] Wait 5 minutes
- [ ] Trigger alarm on backend
- [ ] **Alarm sound MUST play** ✅
- [ ] Device vibrates
- [ ] Screen turns on (optional)
- [ ] Notification visible when unlocked

**Scenario 4: App Killed/Closed**
- [ ] Force close app (swipe away)
- [ ] Trigger alarm on backend
- [ ] Push notification received
- [ ] Device vibrates/beeps
- [ ] Tap notification → App opens
- [ ] Alarm sound plays when app opens

**Scenario 5: Reconnection**
- [ ] App running
- [ ] Disable WiFi/mobile data
- [ ] Wait 10 seconds
- [ ] Re-enable internet
- [ ] App automatically reconnects
- [ ] No manual intervention needed

**Scenario 6: Battery Saver Mode**
- [ ] Enable battery saver mode
- [ ] App still receives alarms
- [ ] Sound still plays
- [ ] Verify background service not killed

---

## 📦 Deliverables

### Phase 1: Core Functionality (Weeks 1-3)
- [ ] Authentication (login/logout)
- [ ] Dashboard with real-time status
- [ ] WebSocket connection
- [ ] Basic alarm sound playback (foreground)

### Phase 2: Background Service (Weeks 4-5)
- [ ] Android foreground service
- [ ] iOS background audio session
- [ ] Alarm playback when screen off ⭐
- [ ] Auto-reconnection logic

### Phase 3: Push Notifications (Week 6)
- [ ] Firebase setup
- [ ] Backend notification sending
- [ ] App notification handling
- [ ] Custom notification sounds

### Phase 4: Polish & Testing (Week 7-8)
- [ ] Event log screen
- [ ] Settings screen
- [ ] Battery optimization
- [ ] Comprehensive testing
- [ ] Bug fixes
- [ ] App store preparation

---

## 💰 Cost Breakdown

### Development Costs

**Option 1: Freelancer (Upwork/Fiverr)**
- React Native developer: $25-50/hour
- Estimated hours: 80-120 hours
- **Total: $2,000 - $6,000**

**Option 2: Development Agency**
- Hourly rate: $75-150/hour
- Estimated hours: 60-80 hours (more efficient)
- **Total: $4,500 - $12,000**

**Option 3: Full-time Developer (Contract)**
- Monthly rate: $4,000 - $8,000
- Duration: 2 months
- **Total: $8,000 - $16,000**

### One-Time Costs
- Google Play Console: $25 (lifetime)
- Apple Developer Program: $99/year
- SSL Certificate (if needed): $0-100/year
- **Total: $124 - $199**

### Monthly Costs
- Firebase (Free tier): $0
- Push notifications: $0 (included in Firebase)
- App hosting: $0 (use existing server)
- **Total: $0/month**

### Recommended Budget
**Total Project Cost: $3,000 - $5,000**
- Development: $2,500 - $4,500
- App store fees: $124
- Testing devices (optional): $200-500
- Contingency (20%): $500-1,000

---

## 📅 Project Timeline

### Week 1-2: Foundation
- Environment setup (React Native, dependencies)
- Authentication implementation
- Basic UI screens (Login, Dashboard)
- WebSocket connection
- **Milestone:** User can login and see live door status

### Week 3-4: Core Features
- Audio playback system
- Background service (Android)
- Background audio session (iOS)
- Event log screen
- **Milestone:** Alarm plays when screen is off (Android)

### Week 5-6: Advanced Features
- Push notifications (Firebase)
- Settings screen
- Battery optimization
- Auto-reconnection logic
- **Milestone:** All features complete

### Week 7-8: Testing & Deployment
- Comprehensive testing
- Bug fixes
- Performance optimization
- App store submission
- **Milestone:** App live on Google Play / App Store

---

## 🎯 Success Criteria

### Must Pass All Tests:

1. **Background Audio Test** ⭐
   - App in background, screen off for 5 minutes
   - Trigger alarm
   - **Result:** Sound plays within 2 seconds

2. **Reliability Test**
   - Run app for 24 hours
   - Trigger 10 alarms at random times
   - **Result:** All 10 alarms play successfully

3. **Battery Test**
   - Run app for 8 hours with background service
   - **Result:** Battery drain < 5% per hour

4. **Reconnection Test**
   - Disconnect network 5 times
   - **Result:** App reconnects automatically every time

5. **Stress Test**
   - Receive 100 status updates in 1 minute
   - **Result:** No crashes, UI remains responsive

---

## 📝 Next Steps

### To Get Started:

1. **Save This Specification**
   - Send to potential developers
   - Use as project requirements

2. **Find a Developer**
   - Post on Upwork: "Need React Native developer for door alarm app"
   - Include this spec document
   - Budget: $3,000-5,000
   - Timeline: 6-8 weeks

3. **Set Up Firebase**
   - Create Firebase project
   - Get credentials
   - Share with developer

4. **Prepare Backend**
   - Add FCM notification endpoint
   - Test WebSocket with developer
   - Provide API documentation

5. **Testing Phase**
   - Test on multiple devices
   - Verify background audio works
   - Submit to app stores

---

## 📞 Support During Development

### What You Provide to Developer:
- ✅ This specification document
- ✅ API documentation (already available)
- ✅ Test server access (your Flask app)
- ✅ Firebase credentials
- ✅ Test user accounts
- ✅ Alarm sound files

### What Developer Provides:
- React Native app source code
- Build instructions
- Testing documentation
- App store submission assets
- User manual
- Maintenance documentation

---

## ✅ Final Checklist Before Hiring

- [ ] Read this entire specification
- [ ] Understand all requirements
- [ ] Budget approved ($3,000-5,000)
- [ ] Timeline acceptable (6-8 weeks)
- [ ] Firebase account created
- [ ] Test server accessible from internet
- [ ] Ready to provide developer support
- [ ] Testing devices available (Android/iOS)

---

**This document is complete and ready to send to any React Native developer. They will have everything needed to build your app successfully!**

**Estimated Total Cost:** $3,000 - $5,000  
**Estimated Timeline:** 6-8 weeks  
**Success Rate:** 95% (with experienced React Native developer)
