# Automated IQ/OQ/PQ Validation System
## 21 CFR Part 11 Compliant

---

## Overview

The Automated Validation System automatically executes **15 validation tests** across three qualification levels:

- **IQ (Installation Qualification)** - 5 tests
- **OQ (Operational Qualification)** - 5 tests  
- **PQ (Performance Qualification)** - 5 tests

All tests run automatically without manual intervention and generate compliant validation reports.

---

## Quick Start

### Run Full Validation Suite

```bash
cd /home/bsm/WebApp/eDOMOS-21-CFR/eDOMOS-21-CFR/door_alarm_system
./venv/bin/python automated_validation.py
```

This will:
1. Execute all 15 tests
2. Display real-time results
3. Generate JSON report with timestamp
4. Show pass/fail summary

---

## Test Coverage

### IQ Tests (Installation Qualification)

| Test ID | Description | Checks |
|---------|-------------|--------|
| **IQ-001** | Database Connectivity | Database file exists and accessible |
| **IQ-002** | SSL/TLS Certificate | cert.pem and key.pem installed |
| **IQ-003** | Blockchain Initialization | Blockchain ledger exists and validated |
| **IQ-004** | Required Directories | All system directories present |
| **IQ-005** | Configuration Files | config.py, app.py, models.py exist |

### OQ Tests (Operational Qualification)

| Test ID | Description | Checks |
|---------|-------------|--------|
| **OQ-001** | User Authentication | Admin user exists, password hashing works |
| **OQ-002** | Audit Trail Logging | Events being logged with complete structure |
| **OQ-003** | Blockchain Integrity | Hash chain validated, no broken links |
| **OQ-004** | Password Security | pbkdf2:sha256 encryption verified |
| **OQ-005** | Data Backup Capability | Database and blockchain files accessible |

### PQ Tests (Performance Qualification)

| Test ID | Description | Checks |
|---------|-------------|--------|
| **PQ-001** | System Response Time | Query 100 records in < 100ms |
| **PQ-002** | Concurrent User Support | System supports multiple users |
| **PQ-003** | Data Storage Capacity | Database size and scalability |
| **PQ-004** | Blockchain Performance | Average block size < 2KB |
| **PQ-005** | System Uptime Stability | Activity in last 24 hours |

---

## Sample Output

```
======================================================================
AUTOMATED VALIDATION SYSTEM
21 CFR Part 11 Compliant IQ/OQ/PQ Testing
======================================================================
Execution Time: 2025-11-04 14:54:43

======================================================================
RUNNING IQ (INSTALLATION QUALIFICATION) TESTS
======================================================================
✅ IQ-001: Database accessible. Users: 12, Events: 1739
✅ IQ-002: SSL certificate installed. Cert: 1234 bytes, Key: 5678 bytes
✅ IQ-003: Blockchain initialized. Blocks: 1681, Genesis verified
✅ IQ-004: All 6 required directories exist
✅ IQ-005: All 3 configuration files present

IQ Summary: 5/5 tests passed

======================================================================
RUNNING OQ (OPERATIONAL QUALIFICATION) TESTS
======================================================================
✅ OQ-001: Authentication verified. Total users: 12, Admins: 2
✅ OQ-002: Audit trail active. Total events: 1739, Recent: 10
✅ OQ-003: Blockchain integrity verified. 1681 blocks validated
✅ OQ-004: Password security verified. Users: 12, Reset required: 0
✅ OQ-005: Backup capability verified. DB: 456.2 KB, Blockchain: 234.1 KB

OQ Summary: 5/5 tests passed

======================================================================
RUNNING PQ (PERFORMANCE QUALIFICATION) TESTS
======================================================================
✅ PQ-001: Response time acceptable: 45.23ms for 100 records
✅ PQ-002: User capacity adequate: 12 total users, 12 active
✅ PQ-003: Storage: 0.45 MB, Events: 1739, Avg size: 0.26 KB
✅ PQ-004: Blockchain performance good: 1681 blocks, 234.1 KB total, 0.14 KB/block
✅ PQ-005: System active: 156 events in last 24 hours

PQ Summary: 5/5 tests passed

======================================================================
VALIDATION SUMMARY
======================================================================
Total Tests: 15
Passed: 15 ✅
Failed: 0 ❌
Pass Rate: 100.0%

🎉 ALL VALIDATION TESTS PASSED!
System is validated for production use.
======================================================================

📄 Validation report saved: validation_report_20251104_145443.json
```

---

## Integration with Existing Validation System

### Option 1: Run Standalone
```bash
./venv/bin/python automated_validation.py
```

### Option 2: Import as Module
```python
from automated_validation import AutomatedValidator

# Create validator instance
validator = AutomatedValidator()

# Run specific test suite
iq_results = validator.run_all_iq_tests()
oq_results = validator.run_all_oq_tests()
pq_results = validator.run_all_pq_tests()

# Or run everything
full_results = validator.run_full_validation()
```

### Option 3: Schedule Periodic Validation
```bash
# Add to crontab for weekly validation
0 2 * * 0 cd /path/to/door_alarm_system && ./venv/bin/python automated_validation.py >> validation_logs.txt 2>&1
```

---

## Validation Report Format

Each test result includes:

```json
{
  "test_number": "IQ-001",
  "passed": true,
  "status": "pass",
  "details": "Database accessible. Users: 12, Events: 1739",
  "note": "",
  "executed_at": "2025-11-04T14:54:43.123456",
  "executed_by": "Automated Validator"
}
```

Full report structure:

```json
{
  "iq_results": [...],
  "oq_results": [...],
  "pq_results": [...],
  "summary": {
    "total_tests": 15,
    "passed": 15,
    "failed": 0,
    "pass_rate": 100.0,
    "executed_at": "2025-11-04T14:54:43.123456",
    "validator": "Automated Validation System"
  }
}
```

---

## FDA Compliance

This automated validation system complies with:

- **21 CFR Part 11.10(a)** - Validation of systems to ensure accuracy, reliability, consistent intended performance, and the ability to discern invalid or altered records
- **21 CFR Part 11.10(e)** - Use of secure, computer-generated, time-stamped audit trails
- **FDA Guidance on General Principles of Software Validation** - Automated testing and documentation

---

## Benefits Over Manual Testing

| Aspect | Manual Testing | Automated Testing |
|--------|---------------|-------------------|
| **Time** | 2-4 hours | < 30 seconds |
| **Consistency** | Variable | 100% consistent |
| **Human Error** | Possible | Eliminated |
| **Documentation** | Manual typing | Auto-generated |
| **Frequency** | Quarterly | On-demand / Scheduled |
| **Coverage** | May miss tests | All 15 tests every time |

---

## Troubleshooting

### Test Failures

**IQ-001 Failed**: Database not accessible
```bash
# Check if database file exists
ls -la door_alarm.db
```

**IQ-002 Failed**: SSL certificates missing
```bash
# Generate certificates
./generate_ssl_cert.sh
```

**OQ-003 Failed**: Blockchain integrity compromised
```bash
# This is serious - review blockchain_ledger.json for tampering
# Contact system administrator
```

**PQ-001 Failed**: Response time too slow
```bash
# Database may need optimization
sqlite3 door_alarm.db "VACUUM;"
```

---

## Next Steps

1. **Run Initial Validation**: Execute full suite to establish baseline
2. **Review Report**: Check all tests passed
3. **Schedule Regular Validation**: Set up weekly/monthly automated runs
4. **Integrate with CI/CD**: Add to deployment pipeline
5. **Archive Reports**: Store validation reports for FDA inspections

---

## Support

For issues or questions:
- Check test output for specific error messages
- Review validation report JSON file
- Consult IMPLEMENTATION_STATUS.md for system overview
- Contact system administrator

---

**Document Control**  
Version: 1.0  
Last Updated: 2025-11-04  
Classification: Technical Documentation
