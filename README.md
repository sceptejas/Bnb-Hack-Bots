# BNB Hack Bots - Prediction Market Trading Bots

A collection of automated trading bots for prediction markets, built for the BNB Hackathon. This repository contains two powerful bots for different trading strategies.

## 🤖 Bots Included

### 1. Multi-Platform Arbitrage Bot (JavaScript/Node.js)
**Location**: `prediction-market-arbitrage-bot/`

Automatically detects and executes arbitrage opportunities across 6 prediction market platforms.

**Supported Platforms**:
- Polymarket
- Kalshi
- Limitless
- Baozi
- Myriad
- Manifold

**Key Features**:
- ✅ Real-time arbitrage detection across all platform pairs
- ✅ Automatic market matching using fuzzy search
- ✅ Configurable profit thresholds
- ✅ Dry run mode for testing
- ✅ Comprehensive test suite (16 tests)

[📖 Read the full documentation →](prediction-market-arbitrage-bot/README.md)

### 2. Market Making Bot (Python)
**Location**: `market-making-bot/`

Provides liquidity to prediction markets by maintaining bid-ask spreads and managing inventory.

**Supported Platforms**:
- Polymarket
- Kalshi
- Limitless

**Key Features**:
- ✅ Spread capture strategy with inventory management
- ✅ Automatic rebalancing to stay inventory-neutral
- ✅ Risk controls (max inventory, min spread, price bounds)
- ✅ Dry run mode for testing
- ✅ Comprehensive test suite (52 tests, 100% pass rate)

[📖 Read the full documentation →](market-making-bot/README.md)

## 🚀 Quick Start

### Arbitrage Bot
```bash
cd prediction-market-arbitrage-bot
npm install
cp .env.example .env
# Edit .env with your API keys
npm start
```

### Market Making Bot
```bash
cd market-making-bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python bot.py
```

## 📊 Frontend Integration

Want to build a web interface for these bots? Check out the comprehensive guide:

[📖 Frontend Integration Guide →](FRONTEND_INTEGRATION_GUIDE.md)

This guide includes:
- Architecture overview
- API design
- React component examples
- WebSocket integration
- Deployment instructions

## 🧪 Testing

### Arbitrage Bot Tests
```bash
cd prediction-market-arbitrage-bot
npm test
```

**Results**: 16/16 tests passing ✅

### Market Making Bot Tests
```bash
cd market-making-bot
python run_tests.py
```

**Results**: 52/52 tests passing ✅

## 📁 Repository Structure

```
bnb-hack-bots/
├── prediction-market-arbitrage-bot/    # JavaScript arbitrage bot
│   ├── src/                            # Source code
│   ├── test/                           # Test suite
│   ├── README.md                       # Bot documentation
│   └── MULTI-PLATFORM-GUIDE.md         # Platform integration guide
│
├── market-making-bot/                  # Python market making bot
│   ├── tests/                          # Test suite
│   ├── bot.py                          # Main bot implementation
│   ├── config.py                       # Configuration
│   ├── README.md                       # Bot documentation
│   ├── QUICKSTART.md                   # Quick start guide
│   ├── STRATEGY.md                     # Strategy explanation
│   ├── TESTING.md                      # Testing guide
│   └── PROJECT_SUMMARY.md              # Project overview
│
├── FRONTEND_INTEGRATION_GUIDE.md       # Guide for building web UI
└── README.md                           # This file
```

## 🔑 API Keys Required

Both bots require API keys from the prediction market platforms you want to trade on.

### Polymarket
- Private key (wallet)

### Kalshi
- API key
- API secret

### Limitless
- API key
- Private key

See individual bot documentation for detailed setup instructions.

## ⚙️ Configuration

Each bot has its own configuration file:

- **Arbitrage Bot**: `prediction-market-arbitrage-bot/config.js`
- **Market Making Bot**: `market-making-bot/config.py`

Both support:
- Platform selection
- Trading parameters
- Risk limits
- Dry run mode

## 🛡️ Safety Features

Both bots include safety features:

- **Dry Run Mode**: Test without real trades
- **Risk Limits**: Max position sizes, min spreads
- **Error Handling**: Graceful recovery from API failures
- **Logging**: Detailed execution logs

## 📈 Performance

### Arbitrage Bot
- Scans all platform pairs in real-time
- Detects opportunities within seconds
- Configurable profit thresholds

### Market Making Bot
- Maintains tight spreads
- Automatic inventory rebalancing
- Profit tracking per trade

## 🤝 Contributing

This is a hackathon project. Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## 📄 License

See individual bot directories for license information.

## 🔗 Links

- **GitHub Repository**: https://github.com/sceptejas/Bnb-Hack-Bots
- **Arbitrage Bot Docs**: [prediction-market-arbitrage-bot/README.md](prediction-market-arbitrage-bot/README.md)
- **Market Making Bot Docs**: [market-making-bot/README.md](market-making-bot/README.md)
- **Frontend Guide**: [FRONTEND_INTEGRATION_GUIDE.md](FRONTEND_INTEGRATION_GUIDE.md)

## ⚠️ Disclaimer

These bots are for educational and hackathon purposes. Trading prediction markets involves risk. Always:
- Test in dry run mode first
- Start with small position sizes
- Understand the risks
- Comply with local regulations

## 🏆 BNB Hackathon

Built for the BNB Hackathon - showcasing automated trading strategies for prediction markets.

---

**Made with ❤️ for the BNB Hackathon**
