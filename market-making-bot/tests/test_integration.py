"""
Integration tests for market making bot
Tests end-to-end workflows with mocked exchange
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot import MarketMaker


class TestMarketSelection(unittest.TestCase):
    """Test market finding and selection"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'market_query': 'Trump',
            'market_index': 0,
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_find_market_success(self, mock_poly):
        """Test successful market finding"""
        bot = MarketMaker(self.config)
        
        # Mock market
        mock_market = Mock()
        mock_market.title = "Will Trump win 2024?"
        mock_market.market_id = "market_123"
        mock_market.volume = 1000000
        mock_market.liquidity = 50000
        mock_market.yes = Mock(outcome_id='outcome_yes', price=0.52)
        
        bot.exchange.fetch_markets = Mock(return_value=[mock_market])
        
        bot.find_market()
        
        self.assertEqual(bot.market, mock_market)
        self.assertEqual(bot.outcome, mock_market.yes)
    
    @patch('bot.pmxt.Polymarket')
    def test_find_market_no_results(self, mock_poly):
        """Test market finding with no results"""
        bot = MarketMaker(self.config)
        bot.exchange.fetch_markets = Mock(return_value=[])
        
        with self.assertRaises(ValueError):
            bot.find_market()
    
    @patch('bot.pmxt.Polymarket')
    def test_find_market_invalid_index(self, mock_poly):
        """Test market finding with invalid index"""
        self.config['market_index'] = 10
        bot = MarketMaker(self.config)
        
        mock_market = Mock()
        bot.exchange.fetch_markets = Mock(return_value=[mock_market])
        
        with self.assertRaises(ValueError):
            bot.find_market()


class TestQuotingWorkflow(unittest.TestCase):
    """Test complete quoting workflow"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'target_spread': 0.04,
            'order_size': 10,
            'max_inventory': 100,
            'rebalance_threshold': 50,
            'inventory_adjustment_factor': 0.01,
            'dry_run': True,
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_full_quote_cycle_neutral(self, mock_poly):
        """Test full quote cycle with neutral inventory"""
        bot = MarketMaker(self.config)
        
        # Setup market
        bot.market = Mock(market_id='market_123')
        bot.outcome = Mock(outcome_id='outcome_yes', price=0.52)
        bot.current_inventory = 0
        
        # Mock order book
        mock_book = Mock()
        mock_book.bids = [Mock(price=0.50, size=10)]
        mock_book.asks = [Mock(price=0.54, size=10)]
        
        bot.exchange.fetch_positions = Mock(return_value=[])
        bot.exchange.fetch_order_book = Mock(return_value=mock_book)
        bot.exchange.fetch_open_orders = Mock(return_value=[])
        
        # Run update
        bot.update_quotes()
        
        # Verify orders were placed
        self.assertIsNotNone(bot.open_orders['bid'])
        self.assertIsNotNone(bot.open_orders['ask'])
    
    @patch('bot.pmxt.Polymarket')
    def test_full_quote_cycle_with_inventory(self, mock_poly):
        """Test full quote cycle with inventory"""
        bot = MarketMaker(self.config)
        
        # Setup market
        bot.market = Mock(market_id='market_123')
        bot.outcome = Mock(outcome_id='outcome_yes', price=0.52)
        
        # Mock position with inventory
        mock_position = Mock(outcome_id='outcome_yes', size=60)
        
        # Mock order book
        mock_book = Mock()
        mock_book.bids = [Mock(price=0.50, size=10)]
        mock_book.asks = [Mock(price=0.54, size=10)]
        
        bot.exchange.fetch_positions = Mock(return_value=[mock_position])
        bot.exchange.fetch_order_book = Mock(return_value=mock_book)
        bot.exchange.fetch_open_orders = Mock(return_value=[])
        
        # Run update
        bot.update_quotes()
        
        # Verify inventory was updated
        self.assertEqual(bot.current_inventory, 60)
        
        # Verify orders were placed (with adjustment)
        self.assertIsNotNone(bot.open_orders['bid'])
        self.assertIsNotNone(bot.open_orders['ask'])
    
    @patch('bot.pmxt.Polymarket')
    def test_quote_cycle_at_max_inventory(self, mock_poly):
        """Test quote cycle stops at max inventory"""
        bot = MarketMaker(self.config)
        
        # Setup market
        bot.market = Mock(market_id='market_123')
        bot.outcome = Mock(outcome_id='outcome_yes', price=0.52)
        
        # Mock position at max inventory
        mock_position = Mock(outcome_id='outcome_yes', size=100)
        
        bot.exchange.fetch_positions = Mock(return_value=[mock_position])
        bot.exchange.fetch_open_orders = Mock(return_value=[])
        
        # Run update
        bot.update_quotes()
        
        # Verify no orders were placed
        self.assertIsNone(bot.open_orders['bid'])
        self.assertIsNone(bot.open_orders['ask'])


class TestOrderFillDetection(unittest.TestCase):
    """Test order fill detection and handling"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'target_spread': 0.04,
            'order_size': 10,
            'dry_run': False,
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_bid_fill_detection(self, mock_poly):
        """Test detection of filled bid order"""
        bot = MarketMaker(self.config)
        bot.current_inventory = 0
        
        # Setup open bid order
        bot.open_orders['bid'] = {'id': 'order_123'}
        
        # Mock filled order
        mock_filled_order = Mock(
            id='order_123',
            status='filled',
            filled=10
        )
        
        bot.exchange.fetch_order = Mock(return_value=mock_filled_order)
        
        # Check fills
        bot.check_fills()
        
        # Verify inventory updated
        self.assertEqual(bot.current_inventory, 10)
        self.assertEqual(bot.trades_completed, 1)
    
    @patch('bot.pmxt.Polymarket')
    def test_ask_fill_detection(self, mock_poly):
        """Test detection of filled ask order"""
        bot = MarketMaker(self.config)
        bot.current_inventory = 10
        bot.trades_completed = 1  # Simulate previous bid fill
        
        # Setup open ask order
        bot.open_orders['ask'] = {'id': 'order_456'}
        
        # Mock filled order
        mock_filled_order = Mock(
            id='order_456',
            status='filled',
            filled=10
        )
        
        bot.exchange.fetch_order = Mock(return_value=mock_filled_order)
        
        # Check fills
        bot.check_fills()
        
        # Verify inventory updated
        self.assertEqual(bot.current_inventory, 0)
        self.assertGreater(bot.total_profit, 0)
    
    @patch('bot.pmxt.Polymarket')
    def test_partial_fill_detection(self, mock_poly):
        """Test detection of partially filled order"""
        bot = MarketMaker(self.config)
        bot.current_inventory = 0
        
        # Setup open bid order
        bot.open_orders['bid'] = {'id': 'order_123'}
        
        # Mock partially filled order
        mock_partial_order = Mock(
            id='order_123',
            status='open',
            filled=5
        )
        
        bot.exchange.fetch_order = Mock(return_value=mock_partial_order)
        
        # Check fills
        bot.check_fills()
        
        # Order should still be tracked
        self.assertIsNotNone(bot.open_orders['bid'])


class TestErrorHandling(unittest.TestCase):
    """Test error handling in various scenarios"""
    
    def setUp(self):
        self.config = {
            'platform': 'polymarket',
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
    
    @patch('bot.pmxt.Polymarket')
    def test_order_book_fetch_error(self, mock_poly):
        """Test handling of order book fetch error"""
        bot = MarketMaker(self.config)
        bot.outcome = Mock(outcome_id='test')
        
        bot.exchange.fetch_order_book = Mock(side_effect=Exception("API Error"))
        
        # Should not crash
        book = bot.get_order_book()
        self.assertIsNone(book)
    
    @patch('bot.pmxt.Polymarket')
    def test_position_fetch_error(self, mock_poly):
        """Test handling of position fetch error"""
        bot = MarketMaker(self.config)
        bot.outcome = Mock(outcome_id='test')
        bot.current_inventory = 10  # Previous value
        
        bot.exchange.fetch_positions = Mock(side_effect=Exception("API Error"))
        
        # Should return previous inventory
        position = bot.get_current_position()
        self.assertEqual(position, 10)
    
    @patch('bot.pmxt.Polymarket')
    def test_order_placement_error(self, mock_poly):
        """Test handling of order placement error"""
        bot = MarketMaker(self.config)
        bot.market = Mock(market_id='test')
        bot.outcome = Mock(outcome_id='test')
        
        bot.exchange.create_order = Mock(side_effect=Exception("Order Error"))
        
        # Should return None
        order = bot.place_order('buy', 0.50, 10)
        self.assertIsNone(order)


class TestMultiPlatform(unittest.TestCase):
    """Test multi-platform support"""
    
    def test_polymarket_initialization(self):
        """Test Polymarket initialization"""
        config = {
            'platform': 'polymarket',
            'credentials': {'polymarket': {'private_key': 'test'}}
        }
        
        with patch('bot.pmxt.Polymarket') as mock:
            bot = MarketMaker(config)
            mock.assert_called_once()
    
    def test_kalshi_initialization(self):
        """Test Kalshi initialization"""
        config = {
            'platform': 'kalshi',
            'credentials': {
                'kalshi': {
                    'api_key': 'test_key',
                    'api_secret': 'test_secret'
                }
            }
        }
        
        with patch('bot.pmxt.Kalshi') as mock:
            bot = MarketMaker(config)
            mock.assert_called_once_with(
                api_key='test_key',
                api_secret='test_secret'
            )
    
    def test_limitless_initialization(self):
        """Test Limitless initialization"""
        config = {
            'platform': 'limitless',
            'credentials': {
                'limitless': {
                    'api_key': 'test_key',
                    'private_key': 'test_private'
                }
            }
        }
        
        with patch('bot.pmxt.Limitless') as mock:
            bot = MarketMaker(config)
            mock.assert_called_once_with(
                api_key='test_key',
                private_key='test_private'
            )


if __name__ == '__main__':
    unittest.main()
