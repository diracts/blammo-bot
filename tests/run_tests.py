#!/usr/bin/env python3
"""
Test runner for BlammoBot tests
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from test_points import TestPointsSystem, TestPointsValidation
from test_dbutils import TestDatabaseUtils, TestDatabaseHealth  
from test_submit import TestSubmissionValidation, TestSubmissionProcess
from test_timestamps import TestTimestamps, TestCooldowns

def run_all_tests():
    """Run all test suites"""
    print("🧪 Running BlammoBot Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestPointsSystem,
        TestPointsValidation,
        TestDatabaseUtils,
        TestDatabaseHealth,
        TestSubmissionValidation,
        TestSubmissionProcess,
        TestTimestamps,
        TestCooldowns
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Error:')[-1].strip()}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)