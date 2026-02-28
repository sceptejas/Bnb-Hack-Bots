# Clan Contracts - Quick Start

Minimal smart contracts for clan-based trading vaults (~100 NSLOC).

## Setup

```bash
npm install
cp .env.example .env
# Edit .env with your keys
```

## Compile

```bash
npm run compile
```

## Test

```bash
npm test
```

## Deploy

```bash
# Local
npm run node  # Terminal 1
npm run deploy:local  # Terminal 2

# Testnet
npm run deploy:testnet

# Mainnet
npm run deploy:mainnet
```

## Usage

### Create Clan
```javascript
const factory = await ethers.getContractAt("ClanFactory", FACTORY_ADDRESS);
const tx = await factory.create("My Clan");
const receipt = await tx.wait();
const clanAddress = receipt.logs[0].address;
```

### Join Clan
```javascript
const clan = await ethers.getContractAt("ClanVault", CLAN_ADDRESS);
await clan.join();
```

### Deposit
```javascript
await clan.deposit({ value: ethers.parseEther("1.0") });
```

### Withdraw
```javascript
const share = await clan.getShare(myAddress);
await clan.withdraw(ethers.parseEther("0.5"));
```

### Promote to Manager (Owner)
```javascript
await clan.promote(memberAddress);
```

### Allocate Funds (Owner)
```javascript
await clan.allocate(managerAddress, ethers.parseEther("5.0"));
```

### Record Trade (Manager)
```javascript
// Profit
await clan.trade(ethers.parseEther("2.0"), ethers.parseEther("0.5"));

// Loss
await clan.trade(ethers.parseEther("2.0"), ethers.parseEther("-0.3"));
```

## Contract Functions

### ClanVault

**Public:**
- `join()` - Join clan as member
- `deposit()` - Deposit ETH (members only)
- `withdraw(amount)` - Withdraw your share
- `getShare(address)` - Get member's current share

**Manager:**
- `trade(amount, pnl)` - Record trade result

**Owner:**
- `promote(address)` - Promote member to manager
- `allocate(address, amount)` - Allocate funds to manager

### ClanFactory

- `create(name)` - Deploy new clan
- `getClans()` - Get all clans
- `getUserClans(address)` - Get user's clans

## Roles

1. **MEMBER** - Deposit/withdraw only
2. **MANAGER** - Can trade with allocated funds
3. **OWNER** - Full control

## Profit Distribution

Share = (Your Contribution / Total Contributions) × Total Balance

Example:
- You: 2 ETH, Others: 1 ETH, Total: 3 ETH
- After profit: Balance = 4 ETH
- Your share: (2/3) × 4 = 2.67 ETH

## Gas Costs (Estimated)

- Create clan: ~500k gas
- Join: ~50k gas
- Deposit: ~45k gas
- Withdraw: ~50k gas
- Trade: ~40k gas

---

**Total NSLOC: ~100 lines** (excluding comments/blank lines)
