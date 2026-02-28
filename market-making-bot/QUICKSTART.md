# Quick Start Guide

Get your market making bot running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Credentials

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials for the platform you want to use:

```bash
# For Polymarket
POLYMARKET_PRIVATE_KEY=your_private_key_here

# For Kalshi
KALSHI_API_KEY=your_api_key_here
KALSHI_API_SECRET=your_api_secret_here

# For Limitless
LIMITLESS_API_KEY=your_api_key_here
LIMITLESS_PRIVATE_KEY=your_private_key_here
```

## Step 3: Configure Bot Settings

Edit `config.py`:

```python
config = {
    # Choose your platform
    'platform': 'polymarket',  # or 'kalshi', 'limitless'
    
    # Choose your market
    'market_query': 'Trump',  # Search term
    'market_index': 0,  # First result
    
    # Set your strategy
    'target_spread': 0.04,  # 4 cent spread
    'order_size': 10,  # 10 contracts per order
    
    # Safety first!
    'dry_run': True,  # Start in test mode
}
```

## Step 4: Test Connection

Run the test suite to verify everything works:

```bash
python test_bot.py
```

You should see:
```
✓ Connected to polymarket
✓ Found 10 markets for 'Trump'
✓ Order book fetched
✓ Bot is ready to run!
```

## Step 5: Run in Dry Run Mode

Start the bot in test mode (no real trades):

```bash
python bot.py
```

You'll see output like:
```
MARKET MAKING BOT - POLYMARKET
✓ Connected to polymarket
✓ Selected market: Will Trump win 2024?

[12:00:00] Updating quotes...
  Inventory: 0 contracts
  Fair Price: $0.520
  Target Spread: $0.040 (4.0%)
  Placing orders:
  [DRY RUN] BUY 10 @ $0.50
  [DRY RUN] SELL 10 @ $0.54
```

## Step 6: Monitor Performance

Watch the bot for a while. Check:
- Are the prices reasonable?
- Is the spread appropriate?
- Would orders get filled?

## Step 7: Go Live (Optional)

When ready for real trading:

1. Edit `config.py`:
```python
'dry_run': False,  # Enable live trading
```

2. Start small:
```python
'order_size': 5,  # Small size
'max_inventory': 25,  # Low limit
```

3. Run the bot:
```bash
python bot.py
```

4. Monitor closely!

## Common Issues

### "No markets found"
- Check your `market_query` in config.py
- Try a different search term
- Verify the market exists on your platform

### "Connection failed"
- Check your credentials in .env
- Verify API keys are correct
- Check if you have network access

### "Order placement failed"
- Check if you have sufficient balance
- Verify market is open for trading
- Check if platform allows your order size

## Safety Tips

1. **Start in dry run mode** - Test without risk
2. **Use small sizes** - Start with 5-10 contracts
3. **Set low limits** - max_inventory of 25-50
4. **Monitor actively** - Watch the first hour closely
5. **Have an exit plan** - Know how to stop and unwind

## Next Steps

- Read [STRATEGY.md](STRATEGY.md) for detailed strategy explanation
- Adjust parameters based on your risk tolerance
- Monitor and optimize over time

## Getting Help

If you encounter issues:
1. Check the error message
2. Review the configuration
3. Test with dry_run = True
4. Check platform API documentation

## Stopping the Bot

Press `Ctrl+C` to stop. The bot will:
1. Cancel all open orders
2. Show final statistics
3. Exit cleanly

Your positions will remain - you'll need to close them manually if desired.

---

Happy market making! 🎯
