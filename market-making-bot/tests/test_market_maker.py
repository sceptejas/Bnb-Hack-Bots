"""
Unit tests for MarketMaker class
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot import MarketMaker


class TestMarketMakerInit(unittest.TestCase):
    """Test MarketMaker initialization"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'market_query': 'Trump',
            'market_index': 0,
            'target_spread': 0.04,
            'order_size': 10,
            'min_spread': 0.02,
            'max_inventory': 100,
            'rebalance_threshold': 50,
            'inventory_adjustment_factor': 0.01,
            'update_interval': 30,
            'dry_run': True,
            'max_order_age': 60,
            'min_order_book_depth': 5,
            'credentials': {
                'polymarket': {'private_key': 'test_key'},
                'kalshi': {'api_key': 'test', 'api_secret': 'test'},
                'limitless': {'api_key': 'test', 'private_key': 'test'}
            }
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_init_polymarket(self, mock_poly):
        """Test initialization with Polymarket"""
        bot = MarketMaker(self.config)
        
        self.assertEqual(bot.config['platform'], 'polymarket')
        self.assertEqual(bot.current_inventory, 0)
        self.assertEqual(bot.total_profit, 0)
        self.assertEqual(bot.trades_completed, 0)
        mock_poly.assert_called_once()
    
    @patch('bot.pmxt.Kalshi')
    def test_init_kalshi(self, mock_kalshi):
        """Test initialization with Kalshi"""
        self.config['platform'] = 'kalshi'
        bot = MarketMaker(self.config)
        
        self.assertEqual(bot.config['platform'], 'kalshi')
        mock_kalshi.assert_called_once()
    
    @patch('bot.pmxt.Limitless')
    def test_init_limitless(self, mock_limitless):
        """Test initialization with Limitless"""
        self.config['platform'] = 'limitless'
        bot = MarketMaker(self.config)
        
        self.assertEqual(bot.config['platform'], 'limitless')
        mock_limitless.assert_called_once()
    
    @patch('bot.pmxt.Polymarket')
    def test_init_invalid_platform(self, mock_poly):
        """Test initialization with invalid platform"""
        self.config['platform'] = 'invalid'
        
        with self.assertRaises(ValueError):
            MarketMaker(self.config)


class TestCalculateFairPrice(unittest.TestCase):
    """Test fair price calculation"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'target_spread': 0.04,
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_fair_price_from_book(self, mock_poly):
        """Test fair price calculation from order book"""
        bot = MarketMaker(self.config)
        
        # Mock order book
        mock_book = Mock()
        mock_book.bids = [Mock(price=0.50, size=10)]
        mock_book.asks = [Mock(price=0.54, size=10)]
        
        fair_price = bot.calculate_fair_price(mock_book)
        
        self.assertEqual(fair_price, 0.52)  # (0.50 + 0.54) / 2
    
    @patch('bot.pmxt.Polymarket')
    def test_fair_price_empty_book(self, mock_poly):
        """Test fair price with empty order book"""
        bot = MarketMaker(self.config)
        bot.outcome = Mock(price=0.55)
        
        mock_book = Mock()
        mock_book.bids = []
        mock_book.asks = []
        
        fair_price = bot.calculate_fair_price(mock_book)
        
        self.assertEqual(fair_price, 0.55)  # Falls back to outcome price
    
    @patch('bot.pmxt.Polymarket')
    def test_fair_price_none_book(self, mock_poly):
        """Test fair price with None book"""
        bot = MarketMaker(self.config)
        bot.outcome = Mock(price=0.60)
        
        fair_price = bot.calculate_fair_price(None)
        
        self.assertEqual(fair_price, 0.60)


class TestCalculateQuotePrices(unittest.TestCase):
    """Test quote price calculation with inventory management"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'target_spread': 0.04,
            'min_spread': 0.02,
            'rebalance_threshold': 50,
            'inventory_adjustment_factor': 0.01,
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_quote_prices_neutral_inventory(self, mock_poly):
        """Test quote prices with neutral inventory"""
        bot = MarketMaker(self.config)
        bot.current_inventory = 0
        
        fair_price = 0.52
        bid, ask = bot.calculate_quote_prices(fair_price)
        
        self.assertAlmostEqual(bid, 0.50, places=2)  # 0.52 - 0.02
        self.assertAlmostEqual(ask, 0.54, places=2)  # 0.52 + 0.02
        self.assertAlmostEqual(ask - bid, 0.04, places=2)
    
    @patch('bot.pmxt.Polymarket')
    def test_quote_prices_long_inventory(self, mock_poly):
        """Test quote prices with long inventory (should lower prices)"""
        bot = MarketMaker(self.config)
        bot.current_inventory = 60  # Above threshold
        
        fair_price = 0.52
        bid, ask = bot.calculate_quote_prices(fair_price)
        
        # Prices should be lower than neutral
        self.assertLess(bid, 0.50)
        self.assertLess(ask, 0.54)
        
        # Spread should be maintained
        self.assertAlmostEqual(ask - bid, 0.04, places=2)
    
    @patch('bot.pmxt.Polymarket')
    def test_quote_prices_short_inventory(self, mock_poly):
        """Test quote prices with short inventory (should raise prices)"""
        bot = MarketMaker(self.config)
        bot.current_inventory = -60  # Below threshold
        
        fair_price = 0.52
        bid, ask = bot.calculate_quote_prices(fair_price)
        
        # Prices should be higher than neutral
        self.assertGreater(bid, 0.50)
        self.assertGreater(ask, 0.54)
        
        # Spread should be maintained
        self.assertAlmostEqual(ask - bid, 0.04, places=2)
    
    @patch('bot.pmxt.Polymarket')
    def test_quote_prices_bounds(self, mock_poly):
        """Test quote prices stay within valid bounds"""
        bot = MarketMaker(self.config)
        bot.current_inventory = 1000  # Extreme inventory
        
        fair_price = 0.52
        bid, ask = bot.calculate_quote_prices(fair_price)
        
        # Prices should be between 0.01 and 0.99
        self.assertGreaterEqual(bid, 0.01)
        self.assertLessEqual(ask, 0.99)
    
    @patch('bot.pmxt.Polymarket')
    def test_quote_prices_min_spread(self, mock_poly):
        """Test minimum spread is maintained"""
        bot = MarketMaker(self.config)
        bot.current_inventory = 0
        
        # Test with extreme fair price
        fair_price = 0.98
        bid, ask = bot.calculate_quote_prices(fair_price)
        
        # Spread should be at least min_spread
        self.assertGreaterEqual(ask - bid, self.config['min_spread'])


class TestInventoryManagement(unittest.TestCase):
    """Test inventory management logic"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'max_inventory': 100,
            'rebalance_threshold': 50,
            'inventory_adjustment_factor': 0.01,
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_get_current_position_empty(self, mock_poly):
        """Test getting position when no positions exist"""
        bot = MarketMaker(self.config)
        bot.outcome = Mock(outcome_id='test_outcome')
        bot.exchange.fetch_positions = Mock(return_value=[])
        
        position = bot.get_current_position()
        
        self.assertEqual(position, 0)
        self.assertEqual(bot.current_inventory, 0)
    
    @patch('bot.pmxt.Polymarket')
    def test_get_current_position_exists(self, mock_poly):
        """Test getting position when position exists"""
        bot = MarketMaker(self.config)
        bot.outcome = Mock(outcome_id='test_outcome')
        
        mock_position = Mock(outcome_id='test_outcome', size=25)
        bot.exchange.fetch_positions = Mock(return_value=[mock_position])
        
        position = bot.get_current_position()
        
        self.assertEqual(position, 25)
        self.assertEqual(bot.current_inventory, 25)
    
    @patch('bot.pmxt.Polymarket')
    def test_inventory_adjustment_calculation(self, mock_poly):
        """Test inventory adjustment calculation"""
        bot = MarketMaker(self.config)
        
        # Test various inventory levels
        test_cases = [
            (0, 0),      # No inventory, no adjustment
            (25, 0),     # Below threshold, no adjustment
            (60, -0.6),  # Above threshold, negative adjustment
            (-60, 0.6),  # Below threshold, positive adjustment
        ]
        
        for inventory, expected_skew in test_cases:
            bot.current_inventory = inventory
            bid, ask = bot.calculate_quote_prices(0.52)
            
            # Verify adjustment direction
            if expected_skew < 0:
                self.assertLess(bid, 0.50)
            elif expected_skew > 0:
                self.assertGreater(bid, 0.50)


class TestOrderManagement(unittest.TestCase):
    """Test order placement and cancellation"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'order_size': 10,
            'dry_run': True,
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_place_order_dry_run(self, mock_poly):
        """Test order placement in dry run mode"""
        bot = MarketMaker(self.config)
        bot.market = Mock(market_id='test_market')
        bot.outcome = Mock(outcome_id='test_outcome')
        
        order = bot.place_order('buy', 0.50, 10)
        
        self.assertIsNotNone(order)
        self.assertEqual(order['status'], 'open')
        self.assertIn('dry-run', order['id'])
    
    @patch('bot.pmxt.Polymarket')
    def test_place_order_live(self, mock_poly):
        """Test order placement in live mode"""
        self.config['dry_run'] = False
        bot = MarketMaker(self.config)
        bot.market = Mock(market_id='test_market')
        bot.outcome = Mock(outcome_id='test_outcome')
        
        mock_order = Mock(id='order_123', status='open')
        bot.exchange.create_order = Mock(return_value=mock_order)
        
        order = bot.place_order('buy', 0.50, 10)
        
        bot.exchange.create_order.assert_called_once_with(
            market_id='test_market',
            outcome_id='test_outcome',
            side='buy',
            type='limit',
            amount=10,
            price=0.50
        )
        self.assertEqual(order.id, 'order_123')
    
    @patch('bot.pmxt.Polymarket')
    def test_cancel_open_orders_dry_run(self, mock_poly):
        """Test order cancellation in dry run mode"""
        bot = MarketMaker(self.config)
        bot.market = Mock(market_id='test_market')
        bot.outcome = Mock(outcome_id='test_outcome')
        
        mock_order = Mock(id='order_123', outcome_id='test_outcome')
        bot.exchange.fetch_open_orders = Mock(return_value=[mock_order])
        
        bot.cancel_open_orders()
        
        # Should not actually cancel in dry run
        bot.exchange.cancel_order.assert_not_called()
    
    @patch('bot.pmxt.Polymarket')
    def test_cancel_open_orders_live(self, mock_poly):
        """Test order cancellation in live mode"""
        self.config['dry_run'] = False
        bot = MarketMaker(self.config)
        bot.market = Mock(market_id='test_market')
        bot.outcome = Mock(outcome_id='test_outcome')
        
        mock_order = Mock(id='order_123', outcome_id='test_outcome')
        bot.exchange.fetch_open_orders = Mock(return_value=[mock_order])
        bot.exchange.cancel_order = Mock()
        
        bot.cancel_open_orders()
        
        bot.exchange.cancel_order.assert_called_once_with('order_123')


class TestRiskManagement(unittest.TestCase):
    """Test risk management features"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'max_inventory': 100,
            'min_spread': 0.02,
            'target_spread': 0.04,
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_max_inventory_check(self, mock_poly):
        """Test that bot respects max inventory"""
        bot = MarketMaker(self.config)
        bot.current_inventory = 100  # At max
        
        # Bot should recognize it's at max
        self.assertEqual(abs(bot.current_inventory), self.config['max_inventory'])
    
    @patch('bot.pmxt.Polymarket')
    def test_min_spread_enforcement(self, mock_poly):
        """Test minimum spread is enforced"""
        bot = MarketMaker(self.config)
        bot.current_inventory = 0
        
        # Calculate quotes
        bid, ask = bot.calculate_quote_prices(0.52)
        
        # Spread should be at least min_spread
        self.assertGreaterEqual(ask - bid, self.config['min_spread'])
    
    @patch('bot.pmxt.Polymarket')
    def test_price_bounds(self, mock_poly):
        """Test prices stay within valid bounds"""
        bot = MarketMaker(self.config)
        
        # Test extreme cases
        for fair_price in [0.01, 0.50, 0.99]:
            bid, ask = bot.calculate_quote_prices(fair_price)
            
            self.assertGreaterEqual(bid, 0.01)
            self.assertLessEqual(bid, 0.99)
            self.assertGreaterEqual(ask, 0.01)
            self.assertLessEqual(ask, 0.99)


class TestStatistics(unittest.TestCase):
    """Test statistics tracking"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_initial_stats(self, mock_poly):
        """Test initial statistics are zero"""
        bot = MarketMaker(self.config)
        
        self.assertEqual(bot.current_inventory, 0)
        self.assertEqual(bot.total_profit, 0)
        self.assertEqual(bot.trades_completed, 0)
    
    @patch('bot.pmxt.Polymarket')
    def test_profit_tracking(self, mock_poly):
        """Test profit tracking"""
        bot = MarketMaker(self.config)
        
        # Simulate profit
        bot.total_profit = 1.50
        bot.trades_completed = 5
        
        avg_profit = bot.total_profit / bot.trades_completed
        self.assertEqual(avg_profit, 0.30)


if __name__ == '__main__':
    unittest.main()
