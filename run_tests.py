#!/usr/bin/env python3
"""
Simple test runner for Jobéco application
Usage: python run_tests.py [options]
"""

import sys
import os
import argparse
from tests.test_app import run_tests, TestDatabaseService, TestUserService, TestGroupService, TestTradesmanService, TestJobService, TestIntegration
from tests.test_email import TestEmailService, TestInvitationService, TestEmailIntegration

def main():
    parser = argparse.ArgumentParser(description='Run Jobéco application tests')
    parser.add_argument('--service', choices=['database', 'user', 'group', 'tradesman', 'job', 'integration', 'email'], 
                       help='Run tests for specific service only')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    parser.add_argument('--quick', '-q', action='store_true', 
                       help='Run only basic tests (skip integration)')
    
    args = parser.parse_args()
    
    print("Jobéco Application Test Runner")
    print("=" * 40)
    
    if args.service:
        # Run specific service tests
        service_map = {
            'database': TestDatabaseService,
            'user': TestUserService,
            'group': TestGroupService,
            'tradesman': TestTradesmanService,
            'job': TestJobService,
            'integration': TestIntegration,
            'email': [TestEmailService, TestInvitationService, TestEmailIntegration]
        }
        
        test_classes = service_map[args.service]
        print(f"Running tests for {args.service} service...")
        
        import unittest
        suite = unittest.TestSuite()
        
        # Handle both single test class and list of test classes
        if isinstance(test_classes, list):
            for test_class in test_classes:
                tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
                suite.addTests(tests)
        else:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_classes)
            suite.addTests(tests)
        
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)
        
    elif args.quick:
        # Run basic tests only
        print("Running basic tests (excluding integration)...")
        import unittest
        suite = unittest.TestSuite()
        
        basic_test_classes = [
            TestDatabaseService,
            TestUserService,
            TestGroupService,
            TestTradesmanService,
            TestJobService
        ]
        
        for test_class in basic_test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
        result = runner.run(suite)
        
    else:
        # Run all tests
        print("Running all tests...")
        result = run_tests()
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    else:
        print("No tests were run.")
    
    print(f"{'='*50}")
    
    if result.wasSuccessful():
        print("\nâœ… All tests passed!")
        return 0
    else:
        print("\nâŒ Some tests failed!")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 
