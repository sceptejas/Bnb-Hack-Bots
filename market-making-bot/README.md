# Market Making Bot

A Python bot that provides liquidity to prediction markets by maintaining bid-ask spreads and managing inventory neutrality.

## What is Market Making?

Market makers provide liquidity by simultaneously placing:
- **Buy orders (Bids)** - Willing to buy at a lower price
- **Sell orders (Asks)** - Willing to sell at a higher price

The difference between bid and ask is the **spread**, which is the market maker's profit.

## Strategy

### Spread Capture
- Place a buy order at $0.50 and a sell order at $0.54
- If both fill, you pocket the $0.04 spread
- Continuously adjust orders based on market conditions

### Inventory Management
The bot stays "neutral" by:
- Tracking current inventory (net position)
- If holding too many YES shares → lower both bid and ask to encourage selling
- If holding too many NO shares → raise both bid and ask to encourage buying
- Target: maintain near-zero inventory

## Features

- Multi-platform support (Polymarket, Kalshi, Limitless)
- Configurable spread and order sizes
- Automatic inventory rebalancing
- Real-time order book monitoring
- Risk management with max position limits

## Installation

```bash
pip install pmxt python-dotenv
```

## Configuration

Create a `.env` file:

```bash
# Platform credentials
POLYMARKET_PRIVATE_KEY=your_private_key
KALSHI_API_KEY=your_api_key
KALSHI_API_SECRET=your_api_secret
LIMITLESS_API_KEY=your_api_key
LIMITLESS_PRIVATE_KEY=your_private_key
```

Edit `config.py` to set your parameters:

```python
config = {
    'platform': 'polymarket',  # or 'kalshi', 'limitless'
    'market_query': 'Trump',
    'target_spread': 0.04,  # 4 cent spread
    'order_size': 10,  # contracts per order
    'max_inventory': 100,  # max position size
    'rebalance_threshold': 50,  # when to adjust prices
    'update_interval': 30,  # seconds between updates
}
```

## Usage

```bash
python bot.py
```

## How It Works

1. **Initialize**: Connect to exchange and find target market
2. **Monitor**: Watch order book and current positions
3. **Quote**: Calculate fair price and place bid/ask orders
4. **Manage**: Adjust prices based on inventory
5. **Repeat**: Cancel old orders and place new ones

## Example Output

```
Market Making Bot - Polymarket
Market: Will Trump win 2024?
Current Price: $0.52

[12:00:00] Starting market making...
[12:00:01] Inventory: 0 | Fair Price: $0.52
[12:00:01] Placing BID at $0.50 for 10 contracts
[12:00:01] Placing ASK at $0.54 for 10 contracts

[12:01:30] BID filled! Bought 10 @ $0.50
[12:01:30] Inventory: +10 | Adjusting quotes...
[12:01:31] Placing BID at $0.49 for 10 contracts (inventory adjustment)
[12:01:31] Placing ASK at $0.53 for 10 contracts (inventory adjustment)

[12:03:15] ASK filled! Sold 10 @ $0.53
[12:03:15] Profit: $0.03 per contract = $0.30 total
[12:03:15] Inventory: 0 | Back to neutral
```

## Risk Management

- **Max Position**: Bot stops if inventory exceeds max_inventory
- **Spread Minimum**: Won't place orders if spread is too tight
- **Order Cancellation**: Cancels stale orders before placing new ones
- **Dry Run Mode**: Test without real trades

## Disclaimer

This is an educational project. Market making involves risk:
- You may accumulate unwanted inventory
- Adverse selection (getting filled on bad prices)
- Market volatility can cause losses
- Use at your own risk

## License

MIT
