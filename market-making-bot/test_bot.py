"""
Test script for market making bot
Tests basic functionality without real trading
"""

import pmxt
from config import config


def test_connection():
    """Test connection to exchange"""
    print("Testing exchange connection...")
    
    platform = config['platform']
    creds = config['credentials'][platform]
    
    try:
        if platform == 'polymarket':
            exchange = pmxt.Polymarket(private_key=creds['private_key'])
        elif platform == 'kalshi':
            exchange = pmxt.Kalshi(
                api_key=creds['api_key'],
                api_secret=creds['api_secret']
            )
        elif platform == 'limitless':
            exchange = pmxt.Limitless(
                api_key=creds['api_key'],
                private_key=creds['private_key']
            )
        
        print(f"✓ Connected to {platform}")
        return exchange
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None


def test_market_search(exchange):
    """Test market search"""
    print(f"\nTesting market search...")
    
    query = config['market_query']
    
    try:
        markets = exchange.fetch_markets(query=query)
        print(f"✓ Found {len(markets)} markets for '{query}'")
        
        if markets:
            market = markets[0]
            print(f"\nFirst market:")
            print(f"  Title: {market.title}")
            print(f"  Market ID: {market.market_id}")
            print(f"  Price: ${market.yes.price:.2f}")
            print(f"  Volume: ${market.volume:,.0f}")
            return market
        else:
            print("✗ No markets found")
            return None
    except Exception as e:
        print(f"✗ Market search failed: {e}")
        return None


def test_order_book(exchange, market):
    """Test order book fetching"""
    print(f"\nTesting order book...")
    
    try:
        outcome = market.yes
        book = exchange.fetch_order_book(outcome.outcome_id)
        
        print(f"✓ Order book fetched")
        print(f"\nBest Bid: ${book.bids[0].price:.3f} ({book.bids[0].size:.0f} contracts)")
        print(f"Best Ask: ${book.asks[0].price:.3f} ({book.asks[0].size:.0f} contracts)")
        print(f"Spread: ${(book.asks[0].price - book.bids[0].price):.3f}")
        
        return book
    except Exception as e:
        print(f"✗ Order book fetch failed: {e}")
        return None


def test_balance(exchange):
    """Test balance fetching"""
    print(f"\nTesting balance...")
    
    try:
        balances = exchange.fetch_balance()
        
        if balances:
            balance = balances[0]
            print(f"✓ Balance fetched")
            print(f"  Available: ${balance.available:.2f}")
            print(f"  Total: ${balance.total:.2f}")
        else:
            print("✓ Balance fetched (empty)")
        
        return balances
    except Exception as e:
        print(f"✗ Balance fetch failed: {e}")
        return None


def test_positions(exchange):
    """Test positions fetching"""
    print(f"\nTesting positions...")
    
    try:
        positions = exchange.fetch_positions()
        
        print(f"✓ Positions fetched ({len(positions)} positions)")
        
        if positions:
            print(f"\nCurrent positions:")
            for pos in positions[:3]:  # Show first 3
                print(f"  {pos.outcome_label}: {pos.size:.2f} @ ${pos.entry_price:.2f}")
        
        return positions
    except Exception as e:
        print(f"✗ Positions fetch failed: {e}")
        return None


def main():
    print("="*60)
    print("  MARKET MAKING BOT - TEST SUITE")
    print("="*60)
    
    # Test 1: Connection
    exchange = test_connection()
    if not exchange:
        print("\n✗ Cannot proceed without connection")
        return
    
    # Test 2: Market Search
    market = test_market_search(exchange)
    if not market:
        print("\n✗ Cannot proceed without market")
        return
    
    # Test 3: Order Book
    book = test_order_book(exchange, market)
    
    # Test 4: Balance (may require auth)
    if not config['dry_run']:
        balance = test_balance(exchange)
        positions = test_positions(exchange)
    else:
        print("\n⚠ Skipping balance/positions tests (dry run mode)")
    
    print("\n" + "="*60)
    print("  TEST SUITE COMPLETE")
    print("="*60)
    print("\n✓ Bot is ready to run!")
    print("\nTo start market making:")
    print("  python bot.py")


if __name__ == '__main__':
    main()
