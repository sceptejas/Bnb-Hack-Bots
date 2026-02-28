# Market Making Strategy Guide

## Core Concept

Market making is about providing liquidity by simultaneously offering to buy (bid) and sell (ask) at different prices. The difference is your profit.

## How It Works

### 1. Basic Spread Capture

```
Current Market Price: $0.52

Your Orders:
- BID: Buy 10 contracts @ $0.50
- ASK: Sell 10 contracts @ $0.54

If both fill:
- You bought at $0.50
- You sold at $0.54
- Profit: $0.04 per contract × 10 = $0.40
```

### 2. Inventory Management

The key challenge is staying neutral. If you only buy or only sell, you accumulate risk.

#### Example: Getting Long

```
Time 0: Inventory = 0
  BID @ $0.50, ASK @ $0.54

Time 1: BID fills, bought 10
  Inventory = +10 (LONG)
  Problem: You're exposed to price drops!

Solution: Adjust prices DOWN
  BID @ $0.49, ASK @ $0.53
  
This encourages others to buy from you (hit your ask)
```

#### Example: Getting Short

```
Time 0: Inventory = 0
  BID @ $0.50, ASK @ $0.54

Time 1: ASK fills, sold 10
  Inventory = -10 (SHORT)
  Problem: You're exposed to price rises!

Solution: Adjust prices UP
  BID @ $0.51, ASK @ $0.55
  
This encourages others to sell to you (hit your bid)
```

## Bot Parameters Explained

### `target_spread`
The difference between your bid and ask.
- Larger spread = More profit per trade, but fewer fills
- Smaller spread = More fills, but less profit per trade
- Typical: 2-5 cents (0.02-0.05)

### `order_size`
How many contracts per order.
- Larger size = More profit per round trip, but more risk
- Smaller size = Less risk, but more orders needed
- Start small: 5-10 contracts

### `max_inventory`
Maximum position you'll hold.
- Safety limit to prevent excessive exposure
- If reached, bot stops quoting
- Typical: 50-100 contracts

### `rebalance_threshold`
When to start adjusting prices.
- If inventory > threshold, start skewing prices
- Lower threshold = More aggressive rebalancing
- Typical: 50% of max_inventory

### `inventory_adjustment_factor`
How much to adjust prices per contract of inventory.
- Higher = More aggressive price adjustments
- Lower = Gentler adjustments
- Typical: 0.01 (1 cent per contract)

## Example Scenarios

### Scenario 1: Balanced Trading

```
[12:00] Inventory: 0
  BID @ $0.50, ASK @ $0.54

[12:05] BID fills → Inventory: +10
  Adjust: BID @ $0.49, ASK @ $0.53

[12:10] ASK fills → Inventory: 0
  Profit: $0.03 × 10 = $0.30
  Back to: BID @ $0.50, ASK @ $0.54
```

### Scenario 2: Accumulating Inventory

```
[12:00] Inventory: 0
  BID @ $0.50, ASK @ $0.54

[12:05] BID fills → Inventory: +10
  Adjust: BID @ $0.49, ASK @ $0.53

[12:10] BID fills again → Inventory: +20
  Adjust: BID @ $0.48, ASK @ $0.52

[12:15] BID fills again → Inventory: +30
  Adjust: BID @ $0.47, ASK @ $0.51

[12:20] ASK fills → Inventory: +20
[12:25] ASK fills → Inventory: +10
[12:30] ASK fills → Inventory: 0
  Back to neutral!
```

### Scenario 3: Hit Max Inventory

```
[12:00] Inventory: 0
  BID @ $0.50, ASK @ $0.54

... multiple BID fills ...

[12:30] Inventory: +100 (MAX!)
  ⚠ Stop quoting - too much risk
  Wait for inventory to decrease
```

## Risk Management

### 1. Adverse Selection
You get filled when the market moves against you.
- Market drops → Your bids fill (you're buying high)
- Market rises → Your asks fill (you're selling low)
- Mitigation: Wider spreads, faster updates

### 2. Inventory Risk
Holding a position exposes you to price moves.
- Long position → Lose if price drops
- Short position → Lose if price rises
- Mitigation: Aggressive rebalancing, max inventory limits

### 3. Market Volatility
Fast-moving markets can cause losses.
- Prices gap through your orders
- Can't rebalance fast enough
- Mitigation: Pause during high volatility

## Optimization Tips

### Start Conservative
```python
config = {
    'target_spread': 0.05,  # Wide spread
    'order_size': 5,  # Small size
    'max_inventory': 50,  # Low limit
    'rebalance_threshold': 25,  # Aggressive rebalancing
}
```

### After Gaining Experience
```python
config = {
    'target_spread': 0.03,  # Tighter spread
    'order_size': 20,  # Larger size
    'max_inventory': 100,  # Higher limit
    'rebalance_threshold': 50,  # Less aggressive
}
```

## Monitoring

Watch these metrics:
- **Inventory**: Should oscillate around 0
- **Fill Rate**: % of orders that fill
- **Profit per Trade**: Should be close to target_spread
- **Inventory Duration**: How long you hold positions

## Common Issues

### Issue: Orders never fill
- Spread too wide
- Prices not competitive
- Solution: Reduce target_spread

### Issue: Inventory keeps growing
- Rebalancing not aggressive enough
- Market trending strongly
- Solution: Increase adjustment_factor or pause

### Issue: Losing money
- Adverse selection
- Spread too narrow
- Solution: Widen spread, update faster

## Advanced: Dynamic Spreads

Future enhancement - adjust spread based on:
- Market volatility (wider when volatile)
- Order book depth (tighter when deep)
- Inventory level (wider when imbalanced)

```python
# Pseudocode
volatility = calculate_volatility()
base_spread = 0.03
dynamic_spread = base_spread * (1 + volatility)
```

## Conclusion

Market making is about:
1. Capturing spreads consistently
2. Managing inventory actively
3. Controlling risk carefully

Start small, monitor closely, and adjust parameters based on results!
