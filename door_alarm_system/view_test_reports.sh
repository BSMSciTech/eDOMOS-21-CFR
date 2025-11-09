#!/bin/bash

# eDOMOS Test Report Viewer
# Quick script to open HTML test reports in browser

echo "🌐 eDOMOS Test Report Viewer"
echo "=============================="
echo ""

# Find the most recent test results directory
LATEST_DIR=$(ls -td test_results_* 2>/dev/null | head -1)

if [ -z "$LATEST_DIR" ]; then
    echo "❌ No test results found!"
    echo ""
    echo "Run tests first: ./run_industrial_tests.sh"
    exit 1
fi

echo "📁 Opening reports from: $LATEST_DIR"
echo ""

# Detect available browser
if command -v chromium-browser >/dev/null 2>&1; then
    BROWSER="chromium-browser"
elif command -v google-chrome >/dev/null 2>&1; then
    BROWSER="google-chrome"
elif command -v firefox >/dev/null 2>&1; then
    BROWSER="firefox"
elif command -v x-www-browser >/dev/null 2>&1; then
    BROWSER="x-www-browser"
else
    echo "❌ No browser found!"
    echo ""
    echo "Manual path to reports:"
    echo "  $(pwd)/$LATEST_DIR/"
    echo ""
    echo "Files to open:"
    ls -1 "$LATEST_DIR"/*.html 2>/dev/null
    exit 1
fi

echo "🌐 Using browser: $BROWSER"
echo ""

# List available reports
echo "📊 Available Reports:"
echo ""
[ -f "$LATEST_DIR/unit_tests_report.html" ] && echo "  ✓ Unit Tests Report"
[ -f "$LATEST_DIR/integration_tests_report.html" ] && echo "  ✓ Integration Tests Report"
[ -f "$LATEST_DIR/security_tests_report.html" ] && echo "  ✓ Security Tests Report"
[ -f "$LATEST_DIR/cfr_compliance_report.html" ] && echo "  ✓ CFR Compliance Report"
[ -d "$LATEST_DIR/coverage_html" ] && echo "  ✓ Code Coverage Report"
echo ""

# Ask user what to open
echo "What would you like to view?"
echo ""
echo "  1) Unit Tests Report"
echo "  2) Integration Tests Report"
echo "  3) Security Tests Report"
echo "  4) CFR Compliance Report"
echo "  5) Code Coverage Report"
echo "  6) All Reports (open all in tabs)"
echo "  7) Just open the folder"
echo ""
read -p "Enter choice [1-7] (or press Enter for all): " choice

case "$choice" in
    1)
        echo "Opening Unit Tests Report..."
        $BROWSER "$LATEST_DIR/unit_tests_report.html" &
        ;;
    2)
        echo "Opening Integration Tests Report..."
        $BROWSER "$LATEST_DIR/integration_tests_report.html" &
        ;;
    3)
        echo "Opening Security Tests Report..."
        $BROWSER "$LATEST_DIR/security_tests_report.html" &
        ;;
    4)
        echo "Opening CFR Compliance Report..."
        $BROWSER "$LATEST_DIR/cfr_compliance_report.html" &
        ;;
    5)
        echo "Opening Code Coverage Report..."
        $BROWSER "$LATEST_DIR/coverage_html/index.html" &
        ;;
    6|"")
        echo "Opening all reports..."
        [ -f "$LATEST_DIR/unit_tests_report.html" ] && $BROWSER "$LATEST_DIR/unit_tests_report.html" &
        sleep 0.5
        [ -f "$LATEST_DIR/integration_tests_report.html" ] && $BROWSER "$LATEST_DIR/integration_tests_report.html" &
        sleep 0.5
        [ -f "$LATEST_DIR/security_tests_report.html" ] && $BROWSER "$LATEST_DIR/security_tests_report.html" &
        sleep 0.5
        [ -f "$LATEST_DIR/cfr_compliance_report.html" ] && $BROWSER "$LATEST_DIR/cfr_compliance_report.html" &
        sleep 0.5
        [ -d "$LATEST_DIR/coverage_html" ] && $BROWSER "$LATEST_DIR/coverage_html/index.html" &
        ;;
    7)
        echo "Opening folder..."
        xdg-open "$LATEST_DIR" 2>/dev/null || nautilus "$LATEST_DIR" 2>/dev/null || echo "Folder: $(pwd)/$LATEST_DIR"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done! Reports opened in $BROWSER"
echo ""
echo "💡 Tip: You can also manually navigate to:"
echo "   $(pwd)/$LATEST_DIR/"
echo ""
