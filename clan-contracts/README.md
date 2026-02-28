# Clan Contracts

Smart contracts for clan-based trading vaults with hierarchical permissions and profit sharing.

## Overview

The Clan Contracts system allows users to create trading clans where:
- **Members** can deposit funds and withdraw their share
- **Managers** can execute trades with allocated funds
- **Owners** control the clan and manage permissions

## Features

### 🏰 Clan Creation
- Deploy a new vault contract for each clan
- Owner automatically gets OWNER role
- Factory pattern for easy deployment

### 👥 Membership System
- **Members**: Can deposit and withdraw funds
- **Managers**: Can execute trades with allocated funds
- **Owners**: Full control over clan operations

### 💰 Fund Management
- Members deposit ETH into the shared vault
- Contributions tracked individually
- Profit/loss distributed proportionally
- Withdraw anytime based on contribution percentage

### 📊 Trading System
- Owner allocates funds to managers
- Managers execute trades within allocation
- Automatic profit/loss tracking
- Transparent trade history

### 🔒 Security Features
- ReentrancyGuard protection
- Role-based access control
- Contribution-based withdrawals
- Emergency withdraw for owner

## Smart Contracts

### Clan.sol
Single file containing both contracts (minimal NSLOC):

**ClanVault** - Main vault contract:
- Member management
- Fund deposits/withdrawals
- Manager allocations
- Trade recording
- Profit distribution

**ClanFactory** - Factory for deploying clans:
- Create new clan vaults
- Track all deployed clans
- Query clans by user

## Installation

```bash
cd clan-contracts
npm install
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Fill in your configuration:
```env
PRIVATE_KEY=your_private_key_here
BSC_TESTNET_RPC=https://data-seed-prebsc-1-s1.binance.org:8545
BSCSCAN_API_KEY=your_bscscan_api_key
```

## Compilation

```bash
npm run compile
```

## Testing

Run the test suite:
```bash
npm test
```

Expected output:
```
  ClanVault
    Deployment
      ✓ Should set the correct clan name
      ✓ Should set the owner as OWNER role
      ✓ Should have 1 member initially (owner)
    Joining Clan
      ✓ Should allow non-members to join
      ✓ Should not allow joining twice
    Deposits
      ✓ Should allow members to deposit
      ✓ Should not allow non-members to deposit
      ✓ Should track multiple deposits
    Withdrawals
      ✓ Should allow members to withdraw their share
      ✓ Should not allow withdrawing more than share
      ✓ Should calculate correct contribution percentage
    ... (more tests)
```

## Deployment

### Local Network

1. Start local Hardhat node:
```bash
npm run node
```

2. Deploy to local network:
```bash
npm run deploy:local
```

### BNB Chain Testnet

```bash
npm run deploy:testnet
```

### BNB Chain Mainnet

```bash
npm run deploy:mainnet
```

## Contract Verification

After deployment, verify on block explorer:

```bash
npx hardhat verify --network bscTestnet <FACTORY_ADDRESS>
```

## Usage Examples

### Creating a Clan

```javascript
const ClanFactory = await ethers.getContractAt("ClanFactory", factoryAddress);
const tx = await ClanFactory.createClan("My Trading Clan");
const receipt = await tx.wait();

// Get clan address from event
const event = receipt.events.find(e => e.event === "ClanCreated");
const clanAddress = event.args.clanAddress;
```

### Joining a Clan

```javascript
const ClanVault = await ethers.getContractAt("ClanVault", clanAddress);
await ClanVault.joinClan();
```

### Depositing Funds

```javascript
await ClanVault.deposit({ value: ethers.parseEther("1.0") });
```

### Withdrawing Funds

```javascript
// Check your share first
const myShare = await ClanVault.calculateMemberShare(myAddress);
console.log("My share:", ethers.formatEther(myShare), "ETH");

// Withdraw
await ClanVault.withdraw(ethers.parseEther("0.5"));
```

### Promoting to Manager (Owner Only)

```javascript
await ClanVault.promoteToManager(memberAddress);
```

### Allocating Funds to Manager (Owner Only)

```javascript
await ClanVault.allocateFunds(managerAddress, ethers.parseEther("5.0"));
```

### Recording a Trade (Manager Only)

```javascript
// Record a profitable trade
const tradeAmount = ethers.parseEther("2.0");
const profit = ethers.parseEther("0.5");
await ClanVault.recordTrade(tradeAmount, profit);

// Record a losing trade
const loss = ethers.parseEther("-0.3");
await ClanVault.recordTrade(tradeAmount, loss);
```

### Getting Vault Statistics

```javascript
const stats = await ClanVault.getVaultStats();
console.log("Balance:", ethers.formatEther(stats.balance));
console.log("Total Contributions:", ethers.formatEther(stats.contributions));
console.log("Profit/Loss:", ethers.formatEther(stats.profitLoss));
console.log("Members:", stats.memberCount.toString());
console.log("Managers:", stats.managerCount.toString());
```

### Getting Member Details

```javascript
const details = await ClanVault.getMemberDetails(memberAddress);
console.log("Role:", details.role); // 0=NONE, 1=MEMBER, 2=MANAGER, 3=OWNER
console.log("Total Contributed:", ethers.formatEther(details.totalContributed));
console.log("Current Share:", ethers.formatEther(details.currentShare));
console.log("Contribution %:", details.contributionPercentage / 100, "%");
console.log("Active:", details.isActive);
```

## Contract Architecture

```
ClanFactory
    │
    ├── createClan() → Deploys new ClanVault
    ├── getAllClans()
    ├── getOwnerClans()
    └── getMemberClans()

ClanVault (per clan)
    │
    ├── Member Functions
    │   ├── joinClan()
    │   ├── deposit()
    │   └── withdraw()
    │
    ├── Manager Functions
    │   └── recordTrade()
    │
    └── Owner Functions
        ├── promoteToManager()
        ├── demoteManager()
        ├── allocateFunds()
        └── removeMember()
```

## Hierarchy System

### Role Levels

1. **MEMBER (Level 1)**
   - Join clan
   - Deposit funds
   - Withdraw their share
   - View vault statistics

2. **MANAGER (Level 2)**
   - All member permissions
   - Record trades within allocation
   - Use allocated funds for trading

3. **OWNER (Level 3)**
   - All manager permissions
   - Promote/demote managers
   - Allocate funds to managers
   - Remove members
   - Emergency controls

## Profit Distribution

Profits and losses are distributed proportionally based on each member's contribution:

```
Member Share = (Member Contribution / Total Contributions) × Total Vault Balance
```

Example:
- Member A contributed 2 ETH
- Member B contributed 1 ETH
- Total contributions: 3 ETH
- Vault balance after trading: 4 ETH (1 ETH profit)

Member A's share: (2/3) × 4 = 2.67 ETH (0.67 ETH profit)
Member B's share: (1/3) × 4 = 1.33 ETH (0.33 ETH profit)

## Security Considerations

### ✅ Implemented
- ReentrancyGuard on all fund transfers
- Role-based access control
- Contribution tracking
- Allocation limits for managers
- Emergency withdraw for owner

### ⚠️ Important Notes
- Owner has significant control (emergency withdraw)
- Managers can lose allocated funds through bad trades
- No slippage protection on trades (implement in trading logic)
- No time locks on withdrawals (consider adding for stability)

## Gas Optimization

- Efficient storage patterns
- Minimal loops
- Optimized compiler settings
- Batch operations where possible

## Frontend Integration

See `FRONTEND_INTEGRATION_GUIDE.md` for detailed integration instructions.

Key endpoints for frontend:
- `createClan(name)` - Create new clan
- `joinClan()` - Join existing clan
- `deposit()` - Add funds
- `withdraw(amount)` - Remove funds
- `getMemberDetails(address)` - Get user info
- `getVaultStats()` - Get clan statistics

## Roadmap

### Phase 1 (Current)
- ✅ Basic vault functionality
- ✅ Hierarchical permissions
- ✅ Profit distribution
- ✅ Factory deployment

### Phase 2 (Planned)
- [ ] Time-locked withdrawals
- [ ] Voting system for major decisions
- [ ] Multi-signature for owner actions
- [ ] Trading strategy templates

### Phase 3 (Future)
- [ ] Cross-chain support
- [ ] NFT membership badges
- [ ] Reputation system
- [ ] Automated profit distribution

## License

MIT

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `/docs` folder
- Tests: See `/test` folder

## Contributing

1. Fork the repository
2. Create your feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

---

**⚠️ Disclaimer**: These contracts are for educational purposes. Audit thoroughly before using with real funds.
