"""
Test runner with coverage reporting
"""

import unittest
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests_with_coverage():
    """Run tests with coverage reporting"""
    try:
        import coverage
        
        # Start coverage
        cov = coverage.Coverage(source=['bot', 'config'])
        cov.start()
        
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = 'tests'
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Stop coverage
        cov.stop()
        cov.save()
        
        # Print coverage report
        print("\n" + "="*70)
        print("COVERAGE REPORT")
        print("="*70)
        cov.report()
        
        # Generate HTML report
        print("\nGenerating HTML coverage report...")
        cov.html_report(directory='htmlcov')
        print("HTML report generated in: htmlcov/index.html")
        
        return result.wasSuccessful()
        
    except ImportError:
        print("Coverage module not installed. Running tests without coverage.")
        print("Install with: pip install coverage")
        return run_tests_without_coverage()


def run_tests_without_coverage():
    """Run tests without coverage"""
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def print_test_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("TEST SUITE SUMMARY")
    print("="*70)
    
    test_files = [
        ('test_market_maker.py', 'Unit tests for MarketMaker class'),
        ('test_integration.py', 'Integration tests for workflows'),
        ('test_config.py', 'Configuration validation tests'),
    ]
    
    print("\nTest Files:")
    for filename, description in test_files:
        print(f"  • {filename}: {description}")
    
    print("\nTest Categories:")
    print("  • Initialization: Platform setup and configuration")
    print("  • Price Calculation: Fair price and quote calculation")
    print("  • Inventory Management: Position tracking and rebalancing")
    print("  • Order Management: Placement, cancellation, fill detection")
    print("  • Risk Management: Limits and safety checks")
    print("  • Error Handling: Exception handling and recovery")
    print("  • Multi-Platform: Support for different exchanges")
    print("  • Configuration: Config validation and structure")


if __name__ == '__main__':
    print_test_summary()
    print("\n" + "="*70)
    print("RUNNING TESTS")
    print("="*70 + "\n")
    
    success = run_tests_with_coverage()
    
    sys.exit(0 if success else 1)
