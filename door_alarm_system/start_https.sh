#!/bin/bash
# eDOMOS v2.1 - HTTPS Server Startup Script
# Uses mkcert-generated SSL certificates

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  eDOMOS v2.1 - HTTPS Server Startup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if SSL certificates exist
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo -e "${RED}❌ SSL certificates not found!${NC}"
    echo -e "${YELLOW}Expected locations:${NC}"
    echo "  - ssl/cert.pem"
    echo "  - ssl/key.pem"
    echo ""
    echo -e "${YELLOW}Please generate certificates using mkcert:${NC}"
    echo "  mkcert -install"
    echo "  mkcert -cert-file ssl/cert.pem -key-file ssl/key.pem 192.168.31.227 localhost 127.0.0.1"
    exit 1
fi

echo -e "${GREEN}✅ SSL certificates found${NC}"
echo -e "${BLUE}📁 Certificate: ssl/cert.pem${NC}"
echo -e "${BLUE}🔑 Private Key: ssl/key.pem${NC}"
echo ""

# Check if server is already running
if pgrep -f "python app.py" > /dev/null; then
    echo -e "${YELLOW}⚠️  Server is already running!${NC}"
    echo -e "${YELLOW}Stopping existing server...${NC}"
    pkill -f "python app.py"
    sleep 2
fi

echo -e "${GREEN}🚀 Starting HTTPS server...${NC}"
echo ""
echo -e "${BLUE}Server will be available at:${NC}"
echo -e "  ${GREEN}https://192.168.31.227:5000${NC}"
echo -e "  ${GREEN}https://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}Note: If accessing from a different device, install mkcert's root CA${NC}"
echo -e "${YELLOW}      to avoid browser security warnings.${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Start the server with SSL enabled
USE_SSL=true python app.py
