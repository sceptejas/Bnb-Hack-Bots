# Testing Guide

## Quick Start

### Install Test Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
python run_tests.py
```

### Expected Output
```
TEST SUITE SUMMARY
======================================================================
Test Files:
  • test_market_maker.py: Unit tests for MarketMaker class
  • test_integration.py: Integration tests for workflows
  • test_config.py: Configuration validation tests

RUNNING TESTS
======================================================================

test_ask_fill_detection (tests.test_integration.TestOrderFillDetection) ... ok
test_bid_fill_detection (tests.test_integration.TestOrderFillDetection) ... ok
...
----------------------------------------------------------------------
Ran 67 tests in 0.234s

OK

======================================================================
COVERAGE REPORT
======================================================================
Name        Stmts   Miss  Cover
-------------------------------
bot.py        245     12    95%
config.py      28      0   100%
-------------------------------
TOTAL         273     12    95%
```

## Test Structure

### Directory Layout
```
market-making-bot/
├── tests/
│   ├── __init__.py
│   ├── test_market_maker.py    # Unit tests
│   ├── test_integration.py     # Integration tests
│   └── test_config.py           # Config tests
├── run_tests.py                 # Test runner
└── TEST_COVERAGE.md             # Coverage report
```

## Test Categories

### 1. Unit Tests (test_market_maker.py)

**TestMarketMakerInit** - Initialization
- Platform setup (Polymarket, Kalshi, Limitless)
- Configuration loading
- State initialization
- Error handling

**TestCalculateFairPrice** - Price Calculation
- Order book mid-price
- Empty book handling
- Fallback logic

**TestCalculateQuotePrices** - Quote Calculation
- Neutral inventory
- Long inventory (price adjustment down)
- Short inventory (price adjustment up)
- Price bounds
- Minimum spread

**TestInventoryManagement** - Position Tracking
- Position fetching
- Inventory updates
- Rebalancing logic

**TestOrderManagement** - Order Operations
- Order placement (dry run & live)
- Order cancellation
- Multiple orders

**TestRiskManagement** - Safety Controls
- Max inventory limits
- Minimum spread enforcement
- Price bounds

**TestStatistics** - Metrics Tracking
- Profit calculation
- Trade counting
- Averages

### 2. Integration Tests (test_integration.py)

**TestMarketSelection** - Market Finding
- Successful search
- No results handling
- Invalid index

**TestQuotingWorkflow** - End-to-End
- Full quote cycle (neutral)
- Full quote cycle (with inventory)
- Max inventory pause

**TestOrderFillDetection** - Fill Handling
- Bid fills
- Ask fills
- Partial fills
- Inventory updates

**TestErrorHandling** - Exception Handling
- API errors
- Network failures
- Graceful degradation

**TestMultiPlatform** - Platform Support
- Polymarket
- Kalshi
- Limitless

### 3. Configuration Tests (test_config.py)

**TestConfigValidation** - Structure
- Required fields
- Valid platforms
- Positive values
- Credential structure

**TestConfigValues** - Ranges
- Reasonable spreads
- Reasonable adjustments
- Reasonable intervals

## Running Specific Tests

### Single Test File
```bash
python -m unittest tests.test_market_maker
```

### Single Test Class
```bash
python -m unittest tests.test_market_maker.TestCalculateQuotePrices
```

### Single Test Method
```bash
python -m unittest tests.test_market_maker.TestCalculateQuotePrices.test_quote_prices_neutral_inventory
```

### With Verbose Output
```bash
python -m unittest tests.test_market_maker -v
```

## Coverage Analysis

### Generate Coverage Report
```bash
python run_tests.py
```

### View HTML Report
```bash
# After running tests
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage by File
```bash
coverage report
```

### Detailed Line Coverage
```bash
coverage report -m
```

## Writing New Tests

### Test Template
```python
import unittest
from unittest.mock import Mock, patch

class TestNewFeature(unittest.TestCase):
    """Test description"""
    
    def setUp(self):
        """Setup before each test"""
        self.config = {...}
    
    @patch('bot.pmxt.Polymarket')
    def test_feature_success(self, mock_poly):
        """Test successful case"""
        # Arrange
        bot = MarketMaker(self.config)
        
        # Act
        result = bot.some_method()
        
        # Assert
        self.assertEqual(result, expected)
    
    def test_feature_error(self):
        """Test error case"""
        with self.assertRaises(ValueError):
            # Code that should raise error
            pass
```

### Best Practices

1. **One concept per test**
   - Test one thing at a time
   - Clear test names
   - Descriptive docstrings

2. **Use mocks for external dependencies**
   ```python
   @patch('bot.pmxt.Polymarket')
   def test_something(self, mock_poly):
       # Mock external API
       mock_poly.return_value.fetch_markets = Mock(return_value=[...])
   ```

3. **Test edge cases**
   - Empty inputs
   - Null values
   - Extreme values
   - Error conditions

4. **Verify state changes**
   ```python
   self.assertEqual(bot.current_inventory, 10)
   self.assertIsNotNone(bot.open_orders['bid'])
   ```

5. **Use descriptive assertions**
   ```python
   self.assertGreater(ask, bid, "Ask should be higher than bid")
   self.assertAlmostEqual(spread, 0.04, places=2)
   ```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python run_tests.py
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Debugging Tests

### Run with Python Debugger
```python
import pdb; pdb.set_trace()  # Add to test
python -m unittest tests.test_market_maker
```

### Print Debug Info
```python
def test_something(self):
    result = bot.calculate_something()
    print(f"Debug: result = {result}")  # Will show in output
    self.assertEqual(result, expected)
```

### Run with Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Test Maintenance

### When to Update Tests

1. **Feature changes** - Update affected tests
2. **Bug fixes** - Add test for the bug
3. **Refactoring** - Ensure tests still pass
4. **New features** - Add new tests

### Keeping Tests Fast

- Mock external APIs
- Avoid sleep/delays
- Use in-memory data
- Parallel execution (if needed)

### Test Coverage Goals

- **Critical paths**: 100%
- **Overall code**: >90%
- **Edge cases**: Covered
- **Error handling**: Verified

## Common Issues

### Import Errors
```bash
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

### Mock Not Working
```python
# Use correct import path
@patch('bot.pmxt.Polymarket')  # Not 'pmxt.Polymarket'
```

### Test Isolation
```python
def setUp(self):
    # Reset state before each test
    self.bot = MarketMaker(self.config)
```

## Performance Testing

### Timing Tests
```python
import time

def test_performance(self):
    start = time.time()
    bot.update_quotes()
    duration = time.time() - start
    
    self.assertLess(duration, 1.0, "Should complete in <1s")
```

### Memory Testing
```python
import tracemalloc

def test_memory(self):
    tracemalloc.start()
    bot.run_cycle()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    self.assertLess(peak / 1024 / 1024, 100, "Should use <100MB")
```

## Summary

The test suite provides:
- **67+ test cases** covering all major functionality
- **~95% code coverage** of critical paths
- **Unit tests** for individual components
- **Integration tests** for workflows
- **Configuration tests** for validation
- **Error handling** verification
- **Multi-platform** support testing

Run `python run_tests.py` to verify everything works!
