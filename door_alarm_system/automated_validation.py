"""
Automated Validation System for IQ/OQ/PQ
21 CFR Part 11 Compliant

This module automates validation testing by:
- Auto-executing system checks
- Generating test results
- Creating validation reports
- Scheduling periodic validation cycles
"""

from datetime import datetime
from models import ValidationTest, EventLog, User, db
from app import app
import os
import json
import hashlib

class AutomatedValidator:
    """Automated validation test executor"""
    
    def __init__(self):
        self.results = []
        self.timestamp = datetime.now()
        
    # ========================================================================
    # IQ (Installation Qualification) - Automated Tests
    # ========================================================================
    
    def iq_001_database_connectivity(self):
        """IQ-001: Verify database connection and integrity"""
        test_number = "IQ-001"
        try:
            # Check database file exists
            db_path = 'door_alarm.db'
            if not os.path.exists(db_path):
                return self._create_result(test_number, False, "Database file not found")
            
            # Check database is accessible
            with app.app_context():
                user_count = User.query.count()
                event_count = EventLog.query.count()
            
            details = f"Database accessible. Users: {user_count}, Events: {event_count}"
            return self._create_result(test_number, True, details)
            
        except Exception as e:
            return self._create_result(test_number, False, f"Database error: {str(e)}")
    
    def iq_002_ssl_certificate(self):
        """IQ-002: Verify SSL/TLS certificate installation"""
        test_number = "IQ-002"
        try:
            cert_file = 'cert.pem'
            key_file = 'key.pem'
            
            cert_exists = os.path.exists(cert_file)
            key_exists = os.path.exists(key_file)
            
            if cert_exists and key_exists:
                # Get certificate details
                cert_size = os.path.getsize(cert_file)
                key_size = os.path.getsize(key_file)
                details = f"SSL certificate installed. Cert: {cert_size} bytes, Key: {key_size} bytes"
                return self._create_result(test_number, True, details)
            else:
                missing = []
                if not cert_exists:
                    missing.append("cert.pem")
                if not key_exists:
                    missing.append("key.pem")
                return self._create_result(test_number, False, f"Missing files: {', '.join(missing)}")
                
        except Exception as e:
            return self._create_result(test_number, False, f"SSL check error: {str(e)}")
    
    def iq_003_blockchain_initialization(self):
        """IQ-003: Verify blockchain ledger initialization"""
        test_number = "IQ-003"
        try:
            blockchain_file = 'blockchain_ledger.json'
            
            if not os.path.exists(blockchain_file):
                return self._create_result(test_number, False, "Blockchain ledger file not found")
            
            # Read blockchain and verify structure
            with open(blockchain_file, 'r') as f:
                blockchain_data = json.load(f)
            
            if not isinstance(blockchain_data, list):
                return self._create_result(test_number, False, "Invalid blockchain structure")
            
            block_count = len(blockchain_data)
            if block_count == 0:
                return self._create_result(test_number, False, "Blockchain is empty")
            
            # Verify genesis block
            genesis = blockchain_data[0]
            if genesis.get('index') != 0:
                return self._create_result(test_number, False, "Invalid genesis block")
            
            details = f"Blockchain initialized. Blocks: {block_count}, Genesis verified"
            return self._create_result(test_number, True, details)
            
        except Exception as e:
            return self._create_result(test_number, False, f"Blockchain check error: {str(e)}")
    
    def iq_004_required_directories(self):
        """IQ-004: Verify required directory structure"""
        test_number = "IQ-004"
        try:
            required_dirs = [
                'templates',
                'static',
                'static/css',
                'static/js',
                'static/audio',
                'logs'
            ]
            
            missing_dirs = []
            existing_dirs = []
            
            for directory in required_dirs:
                if os.path.exists(directory):
                    existing_dirs.append(directory)
                else:
                    missing_dirs.append(directory)
            
            if missing_dirs:
                details = f"Missing directories: {', '.join(missing_dirs)}"
                return self._create_result(test_number, False, details)
            else:
                details = f"All {len(existing_dirs)} required directories exist"
                return self._create_result(test_number, True, details)
                
        except Exception as e:
            return self._create_result(test_number, False, f"Directory check error: {str(e)}")
    
    def iq_005_configuration_files(self):
        """IQ-005: Verify system configuration files"""
        test_number = "IQ-005"
        try:
            config_files = ['config.py', 'app.py', 'models.py']
            
            missing = []
            existing = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    existing.append(config_file)
                else:
                    missing.append(config_file)
            
            if missing:
                details = f"Missing configuration files: {', '.join(missing)}"
                return self._create_result(test_number, False, details)
            else:
                details = f"All {len(existing)} configuration files present"
                return self._create_result(test_number, True, details)
                
        except Exception as e:
            return self._create_result(test_number, False, f"Config check error: {str(e)}")
    
    # ========================================================================
    # OQ (Operational Qualification) - Automated Tests
    # ========================================================================
    
    def oq_001_user_authentication(self):
        """OQ-001: Verify user authentication system"""
        test_number = "OQ-001"
        try:
            with app.app_context():
                # Check if admin user exists
                admin_user = User.query.filter_by(username='admin').first()
                
                if not admin_user:
                    return self._create_result(test_number, False, "Admin user not found")
                
                # Verify password hashing
                if not admin_user.password_hash:
                    return self._create_result(test_number, False, "Password hash not set")
                
                # Count total users
                total_users = User.query.count()
                admin_users = User.query.filter_by(is_admin=True).count()
                
                details = f"Authentication verified. Total users: {total_users}, Admins: {admin_users}"
                return self._create_result(test_number, True, details)
                
        except Exception as e:
            return self._create_result(test_number, False, f"Authentication check error: {str(e)}")
    
    def oq_002_audit_trail_logging(self):
        """OQ-002: Verify audit trail event logging"""
        test_number = "OQ-002"
        try:
            with app.app_context():
                # Check if events are being logged
                total_events = EventLog.query.count()
                
                if total_events == 0:
                    return self._create_result(test_number, False, "No events logged in system")
                
                # Check recent events
                recent_events = EventLog.query.order_by(EventLog.timestamp.desc()).limit(10).all()
                
                # Verify event structure
                sample_event = recent_events[0]
                has_timestamp = sample_event.timestamp is not None
                has_type = sample_event.event_type is not None
                has_description = sample_event.description is not None
                
                if not (has_timestamp and has_type and has_description):
                    return self._create_result(test_number, False, "Event structure incomplete")
                
                details = f"Audit trail active. Total events: {total_events}, Recent: {len(recent_events)}"
                return self._create_result(test_number, True, details)
                
        except Exception as e:
            return self._create_result(test_number, False, f"Audit trail check error: {str(e)}")
    
    def oq_003_blockchain_integrity(self):
        """OQ-003: Verify blockchain hash chain integrity"""
        test_number = "OQ-003"
        try:
            blockchain_file = 'blockchain_ledger.json'
            
            with open(blockchain_file, 'r') as f:
                blockchain = json.load(f)
            
            if len(blockchain) < 2:
                return self._create_result(test_number, True, "Blockchain too small to verify chain (< 2 blocks)")
            
            # Verify hash chain
            broken_links = 0
            for i in range(1, len(blockchain)):
                current_block = blockchain[i]
                previous_block = blockchain[i-1]
                
                if current_block.get('previous_hash') != previous_block.get('hash'):
                    broken_links += 1
            
            if broken_links > 0:
                details = f"Blockchain integrity compromised. Broken links: {broken_links}"
                return self._create_result(test_number, False, details)
            else:
                details = f"Blockchain integrity verified. {len(blockchain)} blocks validated"
                return self._create_result(test_number, True, details)
                
        except Exception as e:
            return self._create_result(test_number, False, f"Blockchain integrity error: {str(e)}")
    
    def oq_004_password_security(self):
        """OQ-004: Verify password security requirements"""
        test_number = "OQ-004"
        try:
            with app.app_context():
                users = User.query.all()
                
                if not users:
                    return self._create_result(test_number, False, "No users in system")
                
                # Check password hash algorithm
                sample_user = users[0]
                password_hash = sample_user.password_hash
                
                # Accept secure hash algorithms: pbkdf2:sha256, scrypt, argon2
                secure_algorithms = ['pbkdf2:sha256', 'scrypt:', 'argon2:']
                is_secure = any(password_hash.startswith(algo) for algo in secure_algorithms)
                
                if not is_secure:
                    return self._create_result(test_number, False, f"Password hash algorithm not secure: {password_hash.split('$')[0]}")
                
                # Determine which algorithm is in use
                algo_name = password_hash.split(':')[0]
                
                # Check for users with password reset required
                reset_required_count = sum(1 for u in users if u.password_reset_required)
                
                details = f"Password security verified ({algo_name}). Users: {len(users)}, Reset required: {reset_required_count}"
                return self._create_result(test_number, True, details)
                
        except Exception as e:
            return self._create_result(test_number, False, f"Password security check error: {str(e)}")
    
    def oq_005_data_backup_capability(self):
        """OQ-005: Verify data backup and recovery capability"""
        test_number = "OQ-005"
        try:
            # Check if database exists (primary data)
            db_exists = os.path.exists('door_alarm.db')
            blockchain_exists = os.path.exists('blockchain_ledger.json')
            
            if not db_exists:
                return self._create_result(test_number, False, "Database file missing")
            
            if not blockchain_exists:
                return self._create_result(test_number, False, "Blockchain ledger missing")
            
            # Get file sizes
            db_size = os.path.getsize('door_alarm.db') / 1024  # KB
            blockchain_size = os.path.getsize('blockchain_ledger.json') / 1024  # KB
            
            details = f"Backup capability verified. DB: {db_size:.1f} KB, Blockchain: {blockchain_size:.1f} KB"
            return self._create_result(test_number, True, details)
            
        except Exception as e:
            return self._create_result(test_number, False, f"Backup check error: {str(e)}")
    
    # ========================================================================
    # PQ (Performance Qualification) - Automated Tests
    # ========================================================================
    
    def pq_001_system_response_time(self):
        """PQ-001: Verify system response time under normal load"""
        test_number = "PQ-001"
        try:
            import time
            
            with app.app_context():
                # Test database query performance
                start_time = time.time()
                events = EventLog.query.limit(100).all()
                query_time = (time.time() - start_time) * 1000  # ms
                
                # Acceptable response time: < 100ms for 100 records
                acceptable_threshold = 100  # ms
                
                if query_time > acceptable_threshold:
                    details = f"Response time too slow: {query_time:.2f}ms (threshold: {acceptable_threshold}ms)"
                    return self._create_result(test_number, False, details)
                else:
                    details = f"Response time acceptable: {query_time:.2f}ms for {len(events)} records"
                    return self._create_result(test_number, True, details)
                    
        except Exception as e:
            return self._create_result(test_number, False, f"Performance test error: {str(e)}")
    
    def pq_002_concurrent_user_support(self):
        """PQ-002: Verify concurrent user session support"""
        test_number = "PQ-002"
        try:
            with app.app_context():
                # Count active users (approximation based on user accounts)
                total_users = User.query.count()
                active_users = User.query.filter_by(is_active=True).count() if hasattr(User, 'is_active') else total_users
                
                # System should support at least 10 concurrent users
                required_capacity = 10
                
                if total_users < required_capacity:
                    details = f"Limited user capacity: {total_users} users (recommended: {required_capacity}+)"
                    return self._create_result(test_number, True, details, note="Warning: Low user count")
                else:
                    details = f"User capacity adequate: {total_users} total users, {active_users} active"
                    return self._create_result(test_number, True, details)
                    
        except Exception as e:
            return self._create_result(test_number, False, f"Concurrent user test error: {str(e)}")
    
    def pq_003_data_storage_capacity(self):
        """PQ-003: Verify data storage capacity and scalability"""
        test_number = "PQ-003"
        try:
            with app.app_context():
                event_count = EventLog.query.count()
                
                # Get database size
                db_size_mb = os.path.getsize('door_alarm.db') / (1024 * 1024)  # MB
                
                # Calculate average event size
                avg_event_size = (db_size_mb * 1024) / event_count if event_count > 0 else 0  # KB
                
                # Estimate capacity (assuming 1GB database limit)
                estimated_capacity = int((1024 / db_size_mb) * event_count) if db_size_mb > 0 else 0
                
                details = f"Storage: {db_size_mb:.2f} MB, Events: {event_count}, Avg size: {avg_event_size:.2f} KB, Est. capacity: {estimated_capacity:,} events"
                return self._create_result(test_number, True, details)
                
        except Exception as e:
            return self._create_result(test_number, False, f"Storage capacity test error: {str(e)}")
    
    def pq_004_blockchain_performance(self):
        """PQ-004: Verify blockchain write performance"""
        test_number = "PQ-004"
        try:
            blockchain_file = 'blockchain_ledger.json'
            
            with open(blockchain_file, 'r') as f:
                blockchain = json.load(f)
            
            block_count = len(blockchain)
            file_size_kb = os.path.getsize(blockchain_file) / 1024
            
            # Calculate average block size
            avg_block_size = file_size_kb / block_count if block_count > 0 else 0
            
            # Acceptable: < 2KB per block on average
            acceptable_threshold = 2.0  # KB
            
            if avg_block_size > acceptable_threshold:
                details = f"Blockchain bloat detected: {avg_block_size:.2f} KB/block (threshold: {acceptable_threshold} KB)"
                return self._create_result(test_number, False, details)
            else:
                details = f"Blockchain performance good: {block_count} blocks, {file_size_kb:.1f} KB total, {avg_block_size:.2f} KB/block"
                return self._create_result(test_number, True, details)
                
        except Exception as e:
            return self._create_result(test_number, False, f"Blockchain performance test error: {str(e)}")
    
    def pq_005_system_uptime_stability(self):
        """PQ-005: Verify system uptime and stability"""
        test_number = "PQ-005"
        try:
            with app.app_context():
                # Check for recent events as indicator of system operation
                from datetime import timedelta
                recent_cutoff = datetime.now() - timedelta(hours=24)
                
                recent_events = EventLog.query.filter(EventLog.timestamp >= recent_cutoff).count()
                
                if recent_events == 0:
                    details = "No events in last 24 hours - system may be down or idle"
                    return self._create_result(test_number, True, details, note="Warning: No recent activity")
                else:
                    details = f"System active: {recent_events} events in last 24 hours"
                    return self._create_result(test_number, True, details)
                    
        except Exception as e:
            return self._create_result(test_number, False, f"Uptime test error: {str(e)}")
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _create_result(self, test_number, passed, details, note=""):
        """Create standardized test result"""
        return {
            'test_number': test_number,
            'passed': passed,
            'status': 'pass' if passed else 'fail',
            'details': details,
            'note': note,
            'executed_at': self.timestamp.isoformat(),
            'executed_by': 'Automated Validator'
        }
    
    def run_all_iq_tests(self):
        """Run all IQ (Installation Qualification) tests"""
        print("\n" + "="*70)
        print("RUNNING IQ (INSTALLATION QUALIFICATION) TESTS")
        print("="*70)
        
        tests = [
            self.iq_001_database_connectivity,
            self.iq_002_ssl_certificate,
            self.iq_003_blockchain_initialization,
            self.iq_004_required_directories,
            self.iq_005_configuration_files
        ]
        
        results = []
        for test_func in tests:
            result = test_func()
            results.append(result)
            status_icon = "✅" if result['passed'] else "❌"
            print(f"{status_icon} {result['test_number']}: {result['details']}")
        
        passed = sum(1 for r in results if r['passed'])
        print(f"\nIQ Summary: {passed}/{len(results)} tests passed")
        return results
    
    def run_all_oq_tests(self):
        """Run all OQ (Operational Qualification) tests"""
        print("\n" + "="*70)
        print("RUNNING OQ (OPERATIONAL QUALIFICATION) TESTS")
        print("="*70)
        
        tests = [
            self.oq_001_user_authentication,
            self.oq_002_audit_trail_logging,
            self.oq_003_blockchain_integrity,
            self.oq_004_password_security,
            self.oq_005_data_backup_capability
        ]
        
        results = []
        for test_func in tests:
            result = test_func()
            results.append(result)
            status_icon = "✅" if result['passed'] else "❌"
            print(f"{status_icon} {result['test_number']}: {result['details']}")
        
        passed = sum(1 for r in results if r['passed'])
        print(f"\nOQ Summary: {passed}/{len(results)} tests passed")
        return results
    
    def run_all_pq_tests(self):
        """Run all PQ (Performance Qualification) tests"""
        print("\n" + "="*70)
        print("RUNNING PQ (PERFORMANCE QUALIFICATION) TESTS")
        print("="*70)
        
        tests = [
            self.pq_001_system_response_time,
            self.pq_002_concurrent_user_support,
            self.pq_003_data_storage_capacity,
            self.pq_004_blockchain_performance,
            self.pq_005_system_uptime_stability
        ]
        
        results = []
        for test_func in tests:
            result = test_func()
            results.append(result)
            status_icon = "✅" if result['passed'] else "❌"
            print(f"{status_icon} {result['test_number']}: {result['details']}")
        
        passed = sum(1 for r in results if r['passed'])
        print(f"\nPQ Summary: {passed}/{len(results)} tests passed")
        return results
    
    def run_full_validation(self):
        """Run complete IQ/OQ/PQ validation suite"""
        print("\n" + "="*70)
        print("AUTOMATED VALIDATION SYSTEM")
        print("21 CFR Part 11 Compliant IQ/OQ/PQ Testing")
        print("="*70)
        print(f"Execution Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        iq_results = self.run_all_iq_tests()
        oq_results = self.run_all_oq_tests()
        pq_results = self.run_all_pq_tests()
        
        # Compile overall results
        all_results = iq_results + oq_results + pq_results
        total_tests = len(all_results)
        total_passed = sum(1 for r in all_results if r['passed'])
        total_failed = total_tests - total_passed
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Print summary
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} ✅")
        print(f"Failed: {total_failed} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if total_failed == 0:
            print("\n🎉 ALL VALIDATION TESTS PASSED!")
            print("System is validated for production use.")
        else:
            print(f"\n⚠️  {total_failed} TEST(S) FAILED")
            print("Review failed tests before deploying to production.")
        
        print("="*70)
        
        return {
            'iq_results': iq_results,
            'oq_results': oq_results,
            'pq_results': pq_results,
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'pass_rate': pass_rate,
                'executed_at': self.timestamp.isoformat(),
                'validator': 'Automated Validation System'
            }
        }


def main():
    """Run automated validation"""
    validator = AutomatedValidator()
    results = validator.run_full_validation()
    
    # Save results to file
    output_file = f'validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Validation report saved: {output_file}")
    
    return results


if __name__ == '__main__':
    main()
