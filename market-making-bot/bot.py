"""
Market Making Bot for Prediction Markets
Provides liquidity by maintaining bid-ask spreads and managing inventory
"""

import pmxt
import time
from datetime import datetime
from config import config


class MarketMaker:
    def __init__(self, config):
        self.config = config
        self.exchange = None
        self.market = None
        self.outcome = None
        self.current_inventory = 0
        self.open_orders = {'bid': None, 'ask': None}
        self.total_profit = 0
        self.trades_completed = 0
        
        self._initialize_exchange()
        
    def _initialize_exchange(self):
        """Initialize the exchange client"""
        platform = self.config['platform']
        
        # Validate platform before accessing credentials
        if platform not in ['polymarket', 'kalshi', 'limitless']:
            raise ValueError(f"Unsupported platform: {platform}")
        
        creds = self.config['credentials'][platform]
        
        print(f"\n{'='*60}")
        print(f"  MARKET MAKING BOT - {platform.upper()}")
        print(f"{'='*60}\n")
        
        if platform == 'polymarket':
            self.exchange = pmxt.Polymarket(private_key=creds['private_key'])
        elif platform == 'kalshi':
            self.exchange = pmxt.Kalshi(
                api_key=creds['api_key'],
                api_secret=creds['api_secret']
            )
        elif platform == 'limitless':
            self.exchange = pmxt.Limitless(
                api_key=creds['api_key'],
                private_key=creds['private_key']
            )
        
        print(f"✓ Connected to {platform}")
        
    def find_market(self):
        """Find and select a market to make"""
        query = self.config['market_query']
        index = self.config['market_index']
        
        print(f"\nSearching for markets: '{query}'...")
        markets = self.exchange.fetch_markets(query=query)
        
        if not markets:
            raise ValueError(f"No markets found for query: {query}")
        
        if index >= len(markets):
            raise ValueError(f"Market index {index} out of range (found {len(markets)} markets)")
        
        self.market = markets[index]
        self.outcome = self.market.yes  # Focus on YES outcome
        
        print(f"✓ Selected market: {self.market.title}")
        print(f"  Market ID: {self.market.market_id}")
        print(f"  Outcome ID: {self.outcome.outcome_id}")
        print(f"  Current Price: ${self.outcome.price:.2f}")
        print(f"  Volume: ${self.market.volume:,.0f}")
        print(f"  Liquidity: ${self.market.liquidity:,.0f}")
        
    def get_current_position(self):
        """Get current inventory position"""
        try:
            positions = self.exchange.fetch_positions()
            
            for pos in positions:
                if pos.outcome_id == self.outcome.outcome_id:
                    self.current_inventory = pos.size
                    return pos.size
            
            self.current_inventory = 0
            return 0
        except Exception as e:
            print(f"Warning: Could not fetch positions: {e}")
            return self.current_inventory
    
    def get_order_book(self):
        """Fetch current order book"""
        try:
            book = self.exchange.fetch_order_book(self.outcome.outcome_id)
            return book
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None
    
    def calculate_fair_price(self, book):
        """Calculate fair price from order book"""
        if not book or not book.bids or not book.asks:
            return self.outcome.price
        
        best_bid = book.bids[0].price if book.bids else 0
        best_ask = book.asks[0].price if book.asks else 1
        
        # Mid price
        fair_price = (best_bid + best_ask) / 2
        return fair_price
    
    def calculate_quote_prices(self, fair_price):
        """Calculate bid and ask prices with inventory adjustment"""
        base_spread = self.config['target_spread']
        inventory = self.current_inventory
        threshold = self.config['rebalance_threshold']
        adjustment_factor = self.config['inventory_adjustment_factor']
        
        # Inventory adjustment
        inventory_skew = 0
        if abs(inventory) > threshold:
            # If long (positive inventory), lower prices to encourage selling
            # If short (negative inventory), raise prices to encourage buying
            inventory_skew = -inventory * adjustment_factor
        
        # Calculate bid and ask with inventory adjustment
        adjusted_fair = fair_price + inventory_skew
        bid_price = adjusted_fair - (base_spread / 2)
        ask_price = adjusted_fair + (base_spread / 2)
        
        # Ensure valid prices (between 0.01 and 0.99)
        bid_price = max(0.01, min(0.99, bid_price))
        ask_price = max(0.01, min(0.99, ask_price))
        
        # Ensure minimum spread is maintained after bounds checking
        current_spread = ask_price - bid_price
        if current_spread < self.config['min_spread']:
            # Recalculate to maintain minimum spread
            mid = (bid_price + ask_price) / 2
            half_spread = self.config['min_spread'] / 2
            bid_price = max(0.01, mid - half_spread)
            ask_price = min(0.99, mid + half_spread)
            
            # If we still can't maintain spread due to bounds, adjust
            if ask_price - bid_price < self.config['min_spread']:
                if bid_price <= 0.01:
                    bid_price = 0.01
                    ask_price = min(0.99, bid_price + self.config['min_spread'])
                elif ask_price >= 0.99:
                    ask_price = 0.99
                    bid_price = max(0.01, ask_price - self.config['min_spread'])
        
        return bid_price, ask_price
    
    def cancel_open_orders(self):
        """Cancel all open orders"""
        try:
            open_orders = self.exchange.fetch_open_orders(self.market.market_id)
            
            for order in open_orders:
                if order.outcome_id == self.outcome.outcome_id:
                    if self.config['dry_run']:
                        print(f"  [DRY RUN] Would cancel order {order.id}")
                    else:
                        self.exchange.cancel_order(order.id)
                        print(f"  Cancelled order {order.id}")
            
            self.open_orders = {'bid': None, 'ask': None}
        except Exception as e:
            print(f"Error cancelling orders: {e}")
    
    def place_order(self, side, price, size):
        """Place a limit order"""
        try:
            if self.config['dry_run']:
                print(f"  [DRY RUN] {side.upper()} {size} @ ${price:.2f}")
                return {'id': f'dry-run-{side}-{time.time()}', 'status': 'open'}
            
            order = self.exchange.create_order(
                market_id=self.market.market_id,
                outcome_id=self.outcome.outcome_id,
                side=side,
                type='limit',
                amount=size,
                price=price
            )
            
            print(f"  {side.upper()} {size} @ ${price:.2f} (Order: {order.id})")
            return order
        except Exception as e:
            print(f"  Error placing {side} order: {e}")
            return None
    
    def update_quotes(self):
        """Main quoting logic"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{timestamp}] Updating quotes...")
        
        # Get current position
        inventory = self.get_current_position()
        print(f"  Inventory: {inventory:+.0f} contracts")
        
        # Check inventory limits
        if abs(inventory) >= self.config['max_inventory']:
            print(f"  ⚠ Max inventory reached! Pausing market making.")
            self.cancel_open_orders()
            return
        
        # Get order book
        book = self.get_order_book()
        if not book:
            print(f"  ⚠ Could not fetch order book")
            return
        
        # Calculate fair price
        fair_price = self.calculate_fair_price(book)
        print(f"  Fair Price: ${fair_price:.3f}")
        
        # Calculate quote prices
        bid_price, ask_price = self.calculate_quote_prices(fair_price)
        spread = ask_price - bid_price
        print(f"  Target Spread: ${spread:.3f} ({spread*100:.1f}%)")
        
        # Cancel existing orders
        self.cancel_open_orders()
        
        # Place new orders
        order_size = self.config['order_size']
        
        print(f"  Placing orders:")
        bid_order = self.place_order('buy', bid_price, order_size)
        ask_order = self.place_order('sell', ask_price, order_size)
        
        if bid_order:
            self.open_orders['bid'] = bid_order
        if ask_order:
            self.open_orders['ask'] = ask_order
        
        # Show stats
        if self.trades_completed > 0:
            print(f"\n  Stats:")
            print(f"    Trades: {self.trades_completed}")
            print(f"    Total Profit: ${self.total_profit:.2f}")
            print(f"    Avg Profit/Trade: ${self.total_profit/self.trades_completed:.3f}")
    
    def check_fills(self):
        """Check if orders were filled and update stats"""
        if self.config['dry_run']:
            return
        
        try:
            for side, order in self.open_orders.items():
                if order and order['id']:
                    updated_order = self.exchange.fetch_order(order['id'])
                    
                    if updated_order.status == 'filled':
                        print(f"\n  ✓ {side.upper()} order filled!")
                        
                        # Update inventory
                        if side == 'bid':
                            self.current_inventory += updated_order.filled
                        else:
                            self.current_inventory -= updated_order.filled
                        
                        # Track profit (simplified)
                        if side == 'ask' and self.trades_completed > 0:
                            spread = self.config['target_spread']
                            profit = spread * updated_order.filled
                            self.total_profit += profit
                            print(f"  Profit: ${profit:.2f}")
                        
                        self.trades_completed += 1
                        self.open_orders[side] = None
        except Exception as e:
            print(f"Error checking fills: {e}")
    
    def run(self):
        """Main bot loop"""
        print(f"\nBot Configuration:")
        print(f"  Target Spread: ${self.config['target_spread']:.2f}")
        print(f"  Order Size: {self.config['order_size']} contracts")
        print(f"  Max Inventory: {self.config['max_inventory']} contracts")
        print(f"  Update Interval: {self.config['update_interval']}s")
        print(f"  Dry Run: {'YES' if self.config['dry_run'] else 'NO'}")
        
        if self.config['dry_run']:
            print(f"\n⚠ DRY RUN MODE - No real trades will be executed")
        
        print(f"\n{'='*60}")
        print(f"  STARTING MARKET MAKING")
        print(f"{'='*60}")
        
        try:
            while True:
                self.check_fills()
                self.update_quotes()
                time.sleep(self.config['update_interval'])
        except KeyboardInterrupt:
            print(f"\n\n{'='*60}")
            print(f"  BOT STOPPED")
            print(f"{'='*60}\n")
            
            # Cancel remaining orders
            print("Cancelling open orders...")
            self.cancel_open_orders()
            
            # Final stats
            print(f"\nFinal Statistics:")
            print(f"  Total Trades: {self.trades_completed}")
            print(f"  Total Profit: ${self.total_profit:.2f}")
            print(f"  Final Inventory: {self.current_inventory:+.0f} contracts")
            
            if self.trades_completed > 0:
                print(f"  Avg Profit/Trade: ${self.total_profit/self.trades_completed:.3f}")


def main():
    try:
        bot = MarketMaker(config)
        bot.find_market()
        bot.run()
    except Exception as e:
        print(f"\nFatal Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
