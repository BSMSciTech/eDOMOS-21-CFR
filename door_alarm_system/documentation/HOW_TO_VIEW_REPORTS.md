# How to View HTML Test Reports

## 🌐 Three Easy Ways to Open HTML Reports

### Method 1: Quick View Script (Recommended)
```bash
./view_test_reports.sh
```
This interactive script will:
- Find your latest test results automatically
- Let you choose which report to open
- Open reports in your default browser

### Method 2: Direct Browser Commands
```bash
# View unit tests
chromium-browser test_results_*/unit_tests_report.html &

# View integration tests
chromium-browser test_results_*/integration_tests_report.html &

# View security tests
chromium-browser test_results_*/security_tests_report.html &

# View code coverage
chromium-browser test_results_*/coverage_html/index.html &

# Open ALL reports at once
chromium-browser test_results_*/*.html test_results_*/coverage_html/index.html &
```

Replace `chromium-browser` with `firefox` if you prefer Firefox.

### Method 3: File Manager (GUI)
1. Open your file manager (File Explorer)
2. Navigate to your project directory:
   ```
   /home/bsm/WebApp/eDOMOS-21-CFR/eDOMOS-21-CFR/door_alarm_system/
   ```
3. Look for folders named `test_results_YYYYMMDD_HHMMSS/`
4. Double-click the most recent folder
5. Double-click any `.html` file to open in browser

---

## 📊 What Each Report Shows

### Unit Tests Report (`unit_tests_report.html`)
- Individual component testing results
- Tests for: User models, Events, Settings, Blockchain, AI, Licenses
- Pass/Fail status for each test
- Execution time for each test

### Integration Tests Report (`integration_tests_report.html`)
- Complete workflow testing results
- Tests for: Authentication, APIs, Change Control, Validation, Training
- API endpoint response codes
- WebSocket connection tests

### Security Tests Report (`security_tests_report.html`)
- Security vulnerability testing results
- Tests for: Password security, SQL injection, XSS, CSRF
- Input validation tests
- Authentication/authorization tests

### CFR Compliance Report (`cfr_compliance_report.html`)
- 21 CFR Part 11 compliance verification
- Electronic signatures testing
- Audit trail verification
- Data integrity checks

### Code Coverage Report (`coverage_html/index.html`)
- Percentage of code tested
- Line-by-line coverage visualization
- Untested code highlighting
- Coverage statistics per file

---

## 🔍 Understanding Test Results

### Green (PASSED) ✅
Test executed successfully, feature working as expected

### Red (FAILED) ❌
Test failed, issue needs to be fixed

### Yellow (SKIPPED) ⚠️
Test was skipped (usually dependency missing)

### Coverage Percentage
- **90-100%** = Excellent (recommended for critical modules)
- **80-89%** = Good (acceptable for most code)
- **70-79%** = Fair (needs improvement)
- **Below 70%** = Poor (more tests needed)

---

## 🚀 Quick Examples

### Open Latest Unit Test Report
```bash
# Find most recent test directory
LATEST=$(ls -td test_results_* | head -1)

# Open unit tests report
chromium-browser "$LATEST/unit_tests_report.html" &
```

### Open All Reports in Tabs
```bash
LATEST=$(ls -td test_results_* | head -1)
cd "$LATEST"
chromium-browser *.html coverage_html/index.html &
cd ..
```

### View from Remote Computer
If you're accessing the Raspberry Pi remotely:

1. **Using SSH with X-forwarding:**
   ```bash
   ssh -X bsm@192.168.31.xxx
   chromium-browser test_results_*/unit_tests_report.html
   ```

2. **Using SCP to copy reports to your computer:**
   ```bash
   # On your local computer
   scp -r bsm@192.168.31.xxx:/home/bsm/WebApp/eDOMOS-21-CFR/eDOMOS-21-CFR/door_alarm_system/test_results_* .
   ```

3. **Using HTTP server:**
   ```bash
   # On Raspberry Pi
   cd test_results_*
   python3 -m http.server 8000
   
   # On your computer's browser, open:
   http://192.168.31.xxx:8000/
   ```

---

## 📁 Report Locations

After running `./run_industrial_tests.sh`, reports are saved in:

```
door_alarm_system/
└── test_results_20251104_225122/    ← Timestamped folder
    ├── unit_tests_report.html       ← Unit test results
    ├── integration_tests_report.html ← Integration test results
    ├── security_tests_report.html   ← Security test results
    ├── cfr_compliance_report.html   ← Compliance verification
    ├── coverage_html/               ← Coverage report folder
    │   └── index.html               ← Coverage main page
    ├── bandit_security_report.txt   ← Security scan (text)
    ├── safety_report.txt            ← Dependency audit
    └── TEST_REPORT_SUMMARY.md       ← Executive summary
```

---

## 💡 Troubleshooting

### Browser Won't Open
```bash
# Check if browser is installed
which chromium-browser
which firefox

# Install if missing
sudo apt-get install chromium-browser
```

### Can't Find Reports
```bash
# List all test result directories
ls -ld test_results_*

# Find most recent
ls -ltd test_results_* | head -1
```

### Reports Are Empty
This means tests haven't run yet. First run:
```bash
./run_industrial_tests.sh
```

### Permission Denied
```bash
# Fix permissions
chmod +x view_test_reports.sh
chmod +x run_industrial_tests.sh
```

---

## 🎯 Recommended Workflow

1. **Run Tests:**
   ```bash
   ./run_industrial_tests.sh
   ```

2. **View Reports:**
   ```bash
   ./view_test_reports.sh
   ```

3. **Review Coverage:**
   - Open coverage report
   - Look for red (untested) lines
   - Add tests for critical untested code

4. **Check for Failures:**
   - Review failed tests in HTML reports
   - Fix issues in code
   - Re-run tests

5. **Document Results:**
   - Read `TEST_REPORT_SUMMARY.md`
   - Share with stakeholders
   - Archive reports for compliance

---

## 📞 Need Help?

If you're still having trouble viewing reports:

1. Check the exact path:
   ```bash
   pwd
   ls -l test_results_*
   ```

2. Try opening directly:
   ```bash
   LATEST=$(ls -td test_results_* | head -1)
   echo "Reports are in: $(pwd)/$LATEST"
   xdg-open "$LATEST"
   ```

3. Or just navigate manually in your file browser to the path shown above.

---

**Happy Testing! 🧪**
