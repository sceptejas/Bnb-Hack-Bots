"""
Tests for configuration validation
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation"""
    
    def test_config_has_required_fields(self):
        """Test that config has all required fields"""
        required_fields = [
            'platform',
            'market_query',
            'market_index',
            'target_spread',
            'order_size',
            'min_spread',
            'max_inventory',
            'rebalance_threshold',
            'inventory_adjustment_factor',
            'update_interval',
            'dry_run',
            'credentials'
        ]
        
        for field in required_fields:
            self.assertIn(field, config, f"Missing required field: {field}")
    
    def test_platform_is_valid(self):
        """Test that platform is one of supported platforms"""
        valid_platforms = ['polymarket', 'kalshi', 'limitless']
        self.assertIn(config['platform'], valid_platforms)
    
    def test_spreads_are_positive(self):
        """Test that spread values are positive"""
        self.assertGreater(config['target_spread'], 0)
        self.assertGreater(config['min_spread'], 0)
    
    def test_min_spread_less_than_target(self):
        """Test that min_spread is less than target_spread"""
        self.assertLess(config['min_spread'], config['target_spread'])
    
    def test_order_size_is_positive(self):
        """Test that order size is positive"""
        self.assertGreater(config['order_size'], 0)
    
    def test_max_inventory_is_positive(self):
        """Test that max inventory is positive"""
        self.assertGreater(config['max_inventory'], 0)
    
    def test_rebalance_threshold_valid(self):
        """Test that rebalance threshold is valid"""
        self.assertGreater(config['rebalance_threshold'], 0)
        self.assertLessEqual(config['rebalance_threshold'], config['max_inventory'])
    
    def test_update_interval_is_positive(self):
        """Test that update interval is positive"""
        self.assertGreater(config['update_interval'], 0)
    
    def test_dry_run_is_boolean(self):
        """Test that dry_run is a boolean"""
        self.assertIsInstance(config['dry_run'], bool)
    
    def test_credentials_structure(self):
        """Test that credentials have correct structure"""
        self.assertIn('credentials', config)
        self.assertIsInstance(config['credentials'], dict)
        
        # Check each platform has credentials
        for platform in ['polymarket', 'kalshi', 'limitless']:
            self.assertIn(platform, config['credentials'])
            self.assertIsInstance(config['credentials'][platform], dict)


class TestConfigValues(unittest.TestCase):
    """Test configuration value ranges"""
    
    def test_spread_reasonable(self):
        """Test that spreads are in reasonable range"""
        # Spreads should be between 0.1% and 10%
        self.assertGreaterEqual(config['target_spread'], 0.001)
        self.assertLessEqual(config['target_spread'], 0.10)
    
    def test_inventory_adjustment_reasonable(self):
        """Test that inventory adjustment factor is reasonable"""
        # Should be between 0.001 and 0.05
        self.assertGreaterEqual(config['inventory_adjustment_factor'], 0.001)
        self.assertLessEqual(config['inventory_adjustment_factor'], 0.05)
    
    def test_update_interval_reasonable(self):
        """Test that update interval is reasonable"""
        # Should be between 5 seconds and 5 minutes
        self.assertGreaterEqual(config['update_interval'], 5)
        self.assertLessEqual(config['update_interval'], 300)


if __name__ == '__main__':
    unittest.main()
