#!/usr/bin/env python3
"""
Remove mobile notification popups from socket.js while keeping audio functionality
"""

import re

socket_js_path = '/home/bsm/WebApp/eDOMOS-21-CFR/eDOMOS-21-CFR/door_alarm_system/static/js/socket.js'

# Read the file
with open(socket_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Comment out door_open notification (lines 885-892)
pattern1 = r"(\s+// Show brief notification for door open\s+if \(window\.mobileAudioManager\.showNotification\) \{\s+window\.mobileAudioManager\.showNotification\(\s+'[^']*Door Opened[^']*',\s+`Door opened at \$\{new Date\(\)\.toLocaleTimeString\(\)\}`[^}]+\}\s+\})"

replacement1 = r"""
                // Show brief notification for door open
                // DISABLED: Audio-only mode, no popups
                // if (window.mobileAudioManager.showNotification) {
                //     window.mobileAudioManager.showNotification(
                //         '🚪 Door Opened',
                //         `Door opened at ${new Date().toLocaleTimeString()}`,
                //         false // not persistent
                //     );
                // }"""

# Pattern 2: Comment out door_close notification (lines 932-939)
pattern2 = r"(\s+// Show brief notification for door close\s+if \(window\.mobileAudioManager\.showNotification\) \{\s+window\.mobileAudioManager\.showNotification\(\s+'[^']*Door Secured[^']*',\s+`Door closed at \$\{new Date\(\)\.toLocaleTimeString\(\)\}`[^}]+\}\s+\})"

replacement2 = r"""
                // Show brief notification for door close
                // DISABLED: Audio-only mode, no popups
                // if (window.mobileAudioManager.showNotification) {
                //     window.mobileAudioManager.showNotification(
                //         '🚪 Door Secured',
                //         `Door closed at ${new Date().toLocaleTimeString()}`,
                //         false // not persistent
                //     );
                // }"""

# Apply replacements
modified = re.sub(pattern1, replacement1, content, flags=re.MULTILINE | re.DOTALL)
modified = re.sub(pattern2, replacement2, modified, flags=re.MULTILINE | re.DOTALL)

# Write back
with open(socket_js_path, 'w', encoding='utf-8') as f:
    f.write(modified)

print("✅ Successfully commented out door_open and door_close notifications")
print("🔊 Audio sounds will still play")
print("🛑 Emergency stop controls preserved")
print("📵 No notification popups will appear")
