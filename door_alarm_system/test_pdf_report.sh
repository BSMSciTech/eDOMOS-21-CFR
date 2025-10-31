#!/bin/bash
# Quick test script for PDF report generation

echo "🔧 Testing eDOMOS PDF Report Generation..."
echo ""

# Test 1: Generate PDF for today
echo "Test 1: Generating PDF report for today..."
curl -X POST http://localhost:5000/api/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "start_date": "'$(date +%Y-%m-%d)'",
    "end_date": "'$(date +%Y-%m-%d)'",
    "event_types": []
  }' \
  -o test_report_today.json

if [ -f test_report_today.json ]; then
    echo "✅ Response received"
    
    # Extract and decode base64 PDF
    python3 << EOF
import json
import base64

with open('test_report_today.json', 'r') as f:
    data = json.load(f)
    
if 'pdf_data' in data:
    pdf_bytes = base64.b64decode(data['pdf_data'])
    with open('eDOMOS_Report_Today.pdf', 'wb') as pdf_file:
        pdf_file.write(pdf_bytes)
    print("✅ PDF saved as: eDOMOS_Report_Today.pdf")
elif 'error' in data:
    print(f"❌ Error: {data['error']}")
else:
    print("❌ Unexpected response format")
EOF
else
    echo "❌ Failed to get response"
fi

echo ""
echo "Test 2: Generating PDF with specific event types..."
curl -X POST http://localhost:5000/api/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "start_date": "'$(date -d "7 days ago" +%Y-%m-%d)'",
    "end_date": "'$(date +%Y-%m-%d)'",
    "event_types": ["door_open", "alarm_triggered"]
  }' \
  -o test_report_filtered.json

if [ -f test_report_filtered.json ]; then
    echo "✅ Response received"
    
    python3 << EOF
import json
import base64

with open('test_report_filtered.json', 'r') as f:
    data = json.load(f)
    
if 'pdf_data' in data:
    pdf_bytes = base64.b64decode(data['pdf_data'])
    with open('eDOMOS_Report_Filtered.pdf', 'wb') as pdf_file:
        pdf_file.write(pdf_bytes)
    print("✅ PDF saved as: eDOMOS_Report_Filtered.pdf")
elif 'error' in data:
    print(f"❌ Error: {data['error']}")
EOF
else
    echo "❌ Failed to get response"
fi

echo ""
echo "📊 Test Summary:"
echo "  - Check generated PDF files in current directory"
echo "  - eDOMOS_Report_Today.pdf (all events today)"
echo "  - eDOMOS_Report_Filtered.pdf (last 7 days, filtered)"
echo ""
echo "🧹 Cleanup test files with: rm test_report_*.json eDOMOS_Report_*.pdf"
