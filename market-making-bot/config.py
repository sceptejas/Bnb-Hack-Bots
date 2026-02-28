"""
Configuration for the market making bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

config = {
    # Platform selection
    'platform': 'polymarket',  # 'polymarket', 'kalshi', or 'limitless'
    
    # Market selection
    'market_query': 'Trump',  # Search query to find market
    'market_index': 0,  # Which market from search results (0 = first)
    
    # Market making parameters
    'target_spread': 0.04,  # Target spread in dollars (e.g., 0.04 = 4 cents)
    'order_size': 10,  # Number of contracts per order
    'min_spread': 0.02,  # Minimum spread to maintain (safety)
    
    # Inventory management
    'max_inventory': 100,  # Maximum position size (contracts)
    'rebalance_threshold': 50,  # Start adjusting prices at this inventory level
    'inventory_adjustment_factor': 0.01,  # Price adjustment per contract of inventory
    
    # Bot behavior
    'update_interval': 30,  # Seconds between order updates
    'dry_run': True,  # Set to False for live trading
    
    # Risk management
    'max_order_age': 60,  # Cancel orders older than this (seconds)
    'min_order_book_depth': 5,  # Minimum contracts in order book to quote
    
    # Credentials (loaded from .env)
    'credentials': {
        'polymarket': {
            'private_key': os.getenv('POLYMARKET_PRIVATE_KEY'),
        },
        'kalshi': {
            'api_key': os.getenv('KALSHI_API_KEY'),
            'api_secret': os.getenv('KALSHI_API_SECRET'),
        },
        'limitless': {
            'api_key': os.getenv('LIMITLESS_API_KEY'),
            'private_key': os.getenv('LIMITLESS_PRIVATE_KEY'),
        }
    }
}
