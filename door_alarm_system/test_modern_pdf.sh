#!/bin/bash

# eDOMOS Industrial Audit PDF Report - Quick Test Script
# This script generates test PDFs to verify the modern design

echo "=================================================="
echo "  eDOMOS Industrial Audit PDF - Quick Test"
echo "=================================================="
echo ""

# Color codes for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if server is running
echo -e "${BLUE}[1/3]${NC} Checking if Flask server is running..."
if curl -s http://localhost:5000/api/dashboard > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Server is running"
else
    echo -e "${YELLOW}⚠${NC} Server may not be running. Start it with: python app.py"
    exit 1
fi

echo ""
echo -e "${BLUE}[2/3]${NC} Generating Modern Industrial Audit PDF Report..."

# Get today's date
TODAY=$(date +%Y-%m-%d)

# Generate PDF for today's events
RESPONSE=$(curl -s -X POST http://localhost:5000/api/report \
  -H "Content-Type: application/json" \
  -d "{\"start_date\": \"$TODAY\", \"end_date\": \"$TODAY\"}" \
  2>&1)

# Check if response contains PDF data
if echo "$RESPONSE" | grep -q "pdf_data"; then
    # Extract and decode PDF
    PDF_BASE64=$(echo "$RESPONSE" | grep -o '"pdf_data":"[^"]*"' | sed 's/"pdf_data":"//;s/"//')
    
    if [ ! -z "$PDF_BASE64" ]; then
        echo "$PDF_BASE64" | base64 -d > "eDOMOS_Modern_Audit_Report_${TODAY}.pdf"
        
        if [ -f "eDOMOS_Modern_Audit_Report_${TODAY}.pdf" ]; then
            FILE_SIZE=$(ls -lh "eDOMOS_Modern_Audit_Report_${TODAY}.pdf" | awk '{print $5}')
            echo -e "${GREEN}✓${NC} PDF generated successfully!"
            echo -e "  Filename: eDOMOS_Modern_Audit_Report_${TODAY}.pdf"
            echo -e "  Size: $FILE_SIZE"
        else
            echo -e "${YELLOW}⚠${NC} PDF file not created"
        fi
    else
        echo -e "${YELLOW}⚠${NC} No PDF data received"
    fi
else
    echo -e "${YELLOW}⚠${NC} Server response doesn't contain PDF"
    echo "Response: $RESPONSE"
fi

echo ""
echo -e "${BLUE}[3/3]${NC} Opening PDF (if viewer available)..."

# Try to open PDF with common viewers
if command -v xdg-open &> /dev/null; then
    xdg-open "eDOMOS_Modern_Audit_Report_${TODAY}.pdf" &> /dev/null &
    echo -e "${GREEN}✓${NC} PDF opened in default viewer"
elif command -v evince &> /dev/null; then
    evince "eDOMOS_Modern_Audit_Report_${TODAY}.pdf" &> /dev/null &
    echo -e "${GREEN}✓${NC} PDF opened in Evince"
elif command -v okular &> /dev/null; then
    okular "eDOMOS_Modern_Audit_Report_${TODAY}.pdf" &> /dev/null &
    echo -e "${GREEN}✓${NC} PDF opened in Okular"
else
    echo -e "${YELLOW}⚠${NC} No PDF viewer found. Please open manually:"
    echo -e "  File: $(pwd)/eDOMOS_Modern_Audit_Report_${TODAY}.pdf"
fi

echo ""
echo "=================================================="
echo "  Design Features to Verify:"
echo "=================================================="
echo "✓ Executive Summary cards (no overlapping text)"
echo "✓ Report Information in modern table format"
echo "✓ Event Log with blue gradient header"
echo "✓ Smooth alternating row colors"
echo "✓ Colored status indicators (●)"
echo "✓ Professional fonts and spacing"
echo "✓ Page headers and footers"
echo "✓ Signature fields at bottom"
echo ""
echo -e "${GREEN}Test complete!${NC}"
echo ""
