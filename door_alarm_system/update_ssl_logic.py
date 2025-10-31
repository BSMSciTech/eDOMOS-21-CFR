#!/usr/bin/env python3
"""Update SSL logic to use environment variable control"""

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace the if-else block (lines 3586-3594)
# The block starts with "    if ssl_enabled:"
for i in range(len(lines)):
    if i >= 3585 and i <= 3593:  # Lines 3586-3594 (0-indexed: 3585-3593)
        if i == 3585:  # "    if ssl_enabled:"
            lines[i] = "    if ssl_enabled:\n"
        elif i == 3586:  # SSL certificates found message
            lines[i] = "        print(\"🔐 SSL enabled - HTTPS mode\")\n"
        elif i == 3587:  # protocol = "https"
            lines[i] = "        protocol = \"https\"\n"
        elif i == 3588:  # ws_protocol = "wss"
            lines[i] = "        ws_protocol = \"wss\"\n"
        elif i == 3589:  # "    else:"
            # Replace else with elif for certs exist but SSL disabled
            lines[i] = "    elif ssl_certs_exist and not use_ssl_env:\n"
        elif i == 3590:  # First print in else
            lines[i] = "        print(\"🌐 SSL disabled - HTTP mode (default)\")\n"
        elif i == 3591:  # Second print in else
            lines[i] = "        print(\"💡 To enable HTTPS: USE_SSL=true python app.py\")\n"
        elif i == 3592:  # protocol = "http"
            lines[i] = "        protocol = \"http\"\n"
        elif i == 3593:  # ws_protocol = "ws"
            # Add the new else block after this
            lines[i] = "        ws_protocol = \"ws\"\n    else:\n        print(\"⚠️  SSL certificates not found - Running on HTTP\")\n        print(\"💡 Run './generate_ssl_cert.sh' to generate SSL certificates\")\n        protocol = \"http\"\n        ws_protocol = \"ws\"\n"

# Write the file back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ SSL logic updated successfully!")
print("   - SSL now controlled by USE_SSL environment variable")
print("   - Default: HTTP mode (USE_SSL=false)")
print("   - To enable HTTPS: USE_SSL=true python app.py")
