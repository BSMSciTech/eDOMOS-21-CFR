#!/bin/bash
# eDOMOS PDF Report Generator - Quick Test Script
# Version 2.1 - Industrial Audit Design

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   eDOMOS PDF Report Generator - Test Suite               ║"
echo "║   Version 2.1 - Industrial Audit-Ready Design            ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if server is running
echo -e "${BLUE}[1/5]${NC} Checking if eDOMOS server is running..."
if curl -s http://localhost:5000/api/dashboard > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Server is running on http://localhost:5000"
else
    echo -e "${RED}✗${NC} Server is not running!"
    echo "      Please start the server first: python3 app.py"
    exit 1
fi
echo ""

# Test 1: Today's Events Report
echo -e "${BLUE}[2/5]${NC} Generating report for TODAY'S events..."
TODAY=$(date +%Y-%m-%d)
curl -s -X POST http://localhost:5000/api/report \
  -H "Content-Type: application/json" \
  -d "{
    \"format\": \"pdf\",
    \"start_date\": \"$TODAY\",
    \"end_date\": \"$TODAY\",
    \"event_types\": []
  }" | jq -r '.pdf_data' | base64 -d > "eDOMOS_Report_Today_$TODAY.pdf" 2>/dev/null

if [ -f "eDOMOS_Report_Today_$TODAY.pdf" ]; then
    SIZE=$(du -h "eDOMOS_Report_Today_$TODAY.pdf" | cut -f1)
    echo -e "${GREEN}✓${NC} Generated: eDOMOS_Report_Today_$TODAY.pdf (${SIZE})"
else
    echo -e "${RED}✗${NC} Failed to generate today's report"
fi
echo ""

# Test 2: Last 7 Days Report
echo -e "${BLUE}[3/5]${NC} Generating report for LAST 7 DAYS..."
START_DATE=$(date -d "7 days ago" +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)
curl -s -X POST http://localhost:5000/api/report \
  -H "Content-Type: application/json" \
  -d "{
    \"format\": \"pdf\",
    \"start_date\": \"$START_DATE\",
    \"end_date\": \"$END_DATE\",
    \"event_types\": []
  }" | jq -r '.pdf_data' | base64 -d > "eDOMOS_Report_Last7Days_${START_DATE}_to_${END_DATE}.pdf" 2>/dev/null

if [ -f "eDOMOS_Report_Last7Days_${START_DATE}_to_${END_DATE}.pdf" ]; then
    SIZE=$(du -h "eDOMOS_Report_Last7Days_${START_DATE}_to_${END_DATE}.pdf" | cut -f1)
    echo -e "${GREEN}✓${NC} Generated: eDOMOS_Report_Last7Days_${START_DATE}_to_${END_DATE}.pdf (${SIZE})"
else
    echo -e "${RED}✗${NC} Failed to generate 7-day report"
fi
echo ""

# Test 3: Alarms Only Report
echo -e "${BLUE}[4/5]${NC} Generating ALARMS ONLY report (last 30 days)..."
START_DATE=$(date -d "30 days ago" +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)
curl -s -X POST http://localhost:5000/api/report \
  -H "Content-Type: application/json" \
  -d "{
    \"format\": \"pdf\",
    \"start_date\": \"$START_DATE\",
    \"end_date\": \"$END_DATE\",
    \"event_types\": [\"alarm_triggered\"]
  }" | jq -r '.pdf_data' | base64 -d > "eDOMOS_Report_AlarmsOnly_Last30Days.pdf" 2>/dev/null

if [ -f "eDOMOS_Report_AlarmsOnly_Last30Days.pdf" ]; then
    SIZE=$(du -h "eDOMOS_Report_AlarmsOnly_Last30Days.pdf" | cut -f1)
    echo -e "${GREEN}✓${NC} Generated: eDOMOS_Report_AlarmsOnly_Last30Days.pdf (${SIZE})"
else
    echo -e "${RED}✗${NC} Failed to generate alarms-only report"
fi
echo ""

# Test 4: Comprehensive Full Report (Last 60 Days)
echo -e "${BLUE}[5/5]${NC} Generating COMPREHENSIVE report (last 60 days)..."
START_DATE=$(date -d "60 days ago" +%Y-%m-%d)
END_DATE=$(date +%Y-%m-%d)
curl -s -X POST http://localhost:5000/api/report \
  -H "Content-Type: application/json" \
  -d "{
    \"format\": \"pdf\",
    \"start_date\": \"$START_DATE\",
    \"end_date\": \"$END_DATE\",
    \"event_types\": []
  }" | jq -r '.pdf_data' | base64 -d > "eDOMOS_Report_Comprehensive_Last60Days.pdf" 2>/dev/null

if [ -f "eDOMOS_Report_Comprehensive_Last60Days.pdf" ]; then
    SIZE=$(du -h "eDOMOS_Report_Comprehensive_Last60Days.pdf" | cut -f1)
    echo -e "${GREEN}✓${NC} Generated: eDOMOS_Report_Comprehensive_Last60Days.pdf (${SIZE})"
else
    echo -e "${RED}✗${NC} Failed to generate comprehensive report"
fi
echo ""

# Summary
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    GENERATION COMPLETE                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Generated PDF Reports:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ls -lh eDOMOS_Report_*.pdf 2>/dev/null | awk '{printf "  %-50s %8s\n", $9, $5}'
echo ""

# Offer to open reports
echo -e "${YELLOW}Options:${NC}"
echo "  1. Open today's report:        xdg-open eDOMOS_Report_Today_$TODAY.pdf"
echo "  2. Open all reports:           xdg-open eDOMOS_Report_*.pdf"
echo "  3. View in directory:          ls -lh eDOMOS_Report_*.pdf"
echo "  4. Clean up test files:        rm eDOMOS_Report_*.pdf"
echo ""

# Auto-open option
read -p "Would you like to open today's report now? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "eDOMOS_Report_Today_$TODAY.pdf" ]; then
        echo -e "${GREEN}Opening${NC} eDOMOS_Report_Today_$TODAY.pdf..."
        xdg-open "eDOMOS_Report_Today_$TODAY.pdf" 2>/dev/null || open "eDOMOS_Report_Today_$TODAY.pdf" 2>/dev/null
    else
        echo -e "${RED}File not found!${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✓${NC} Test script completed!"
echo ""
