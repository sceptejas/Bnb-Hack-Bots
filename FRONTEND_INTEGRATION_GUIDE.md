# Frontend Integration Guide for Trading Bots

A comprehensive guide for building a web interface for the Arbitrage and Market Making bots.

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Backend API Requirements](#backend-api-requirements)
4. [Frontend Components](#frontend-components)
5. [Real-Time Updates](#real-time-updates)
6. [Security Considerations](#security-considerations)
7. [Implementation Guide](#implementation-guide)
8. [Example Code](#example-code)

---

## Overview

### What You're Building

A web dashboard that allows users to:
- Configure and launch trading bots
- Monitor bot performance in real-time
- View trading history and statistics
- Manage API credentials securely
- Control bot operations (start/stop/pause)

### Tech Stack Recommendations

**Frontend:**
- React.js or Next.js (recommended)
- TypeScript for type safety
- TailwindCSS for styling
- Chart.js or Recharts for visualizations
- Socket.io-client for real-time updates

**Backend:**
- Node.js + Express (for API wrapper)
- Python FastAPI (alternative, direct integration)
- WebSocket server for real-time data
- Redis for caching and session management

---

## Architecture

### System Overview

```
┌─────────────────┐
│   Web Browser   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/WebSocket
         ↓
┌─────────────────┐
│   API Server    │
│  (Node/Python)  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Trading Bots   │
│ (Python/Node)   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Exchanges     │
│ (Polymarket,    │
│  Kalshi, etc.)  │
└─────────────────┘
```

### Data Flow

1. **User Input** → Frontend → API Server
2. **Bot Control** → API Server → Bot Process
3. **Bot Status** → Bot Process → WebSocket → Frontend
4. **Trade Data** → Exchange → Bot → WebSocket → Frontend

---

## Backend API Requirements

### API Endpoints Needed

#### 1. Bot Management

```typescript
// Start a bot
POST /api/bots/start
Body: {
  botType: "arbitrage" | "market-making",
  config: BotConfig
}
Response: {
  botId: string,
  status: "starting" | "running"
}

// Stop a bot
POST /api/bots/:botId/stop
Response: {
  botId: string,
  status: "stopped"
}

// Get bot status
GET /api/bots/:botId/status
Response: {
  botId: string,
  status: "running" | "stopped" | "error",
  uptime: number,
  stats: BotStats
}

// List all bots
GET /api/bots
Response: {
  bots: Bot[]
}
```

#### 2. Configuration

```typescript
// Save bot configuration
POST /api/config
Body: {
  botType: string,
  config: BotConfig
}

// Get saved configurations
GET /api/config
Response: {
  configs: SavedConfig[]
}

// Validate configuration
POST /api/config/validate
Body: {
  config: BotConfig
}
Response: {
  valid: boolean,
  errors?: string[]
}
```

#### 3. Credentials Management

```typescript
// Save API credentials (encrypted)
POST /api/credentials
Body: {
  platform: string,
  credentials: {
    apiKey?: string,
    apiSecret?: string,
    privateKey?: string
  }
}

// Test credentials
POST /api/credentials/test
Body: {
  platform: string,
  credentials: Credentials
}
Response: {
  valid: boolean,
  balance?: number
}
```

#### 4. Trading Data

```typescript
// Get trading history
GET /api/trades?botId=xxx&limit=100
Response: {
  trades: Trade[]
}

// Get bot statistics
GET /api/stats/:botId
Response: {
  totalTrades: number,
  totalProfit: number,
  winRate: number,
  avgProfit: number,
  currentInventory: number
}

// Get market data
GET /api/markets?platform=polymarket&query=Trump
Response: {
  markets: Market[]
}
```

#### 5. Real-Time Updates (WebSocket)

```typescript
// Connect to WebSocket
ws://api.example.com/ws

// Subscribe to bot updates
{
  type: "subscribe",
  botId: "bot-123"
}

// Receive updates
{
  type: "bot-update",
  botId: "bot-123",
  data: {
    status: "running",
    currentPrice: 0.52,
    inventory: 10,
    lastTrade: Trade
  }
}
```

---

## Frontend Components

### 1. Dashboard Layout

```
┌─────────────────────────────────────────┐
│  Header (Logo, User, Notifications)    │
├──────────┬──────────────────────────────┤
│          │                              │
│ Sidebar  │   Main Content Area          │
│          │                              │
│ - Bots   │   ┌──────────────────────┐  │
│ - Config │   │  Bot Cards Grid      │  │
│ - Trades │   │  ┌────┐  ┌────┐      │  │
│ - Stats  │   │  │Bot1│  │Bot2│      │  │
│ - Docs   │   │  └────┘  └────┘      │  │
│          │   └──────────────────────┘  │
│          │                              │
└──────────┴──────────────────────────────┘
```

### 2. Key Components to Build

#### A. Bot Card Component
```jsx
<BotCard
  botId="bot-123"
  type="arbitrage"
  status="running"
  stats={{
    profit: 125.50,
    trades: 45,
    uptime: "2h 15m"
  }}
  onStop={() => {}}
  onRestart={() => {}}
/>
```

#### B. Configuration Form
```jsx
<BotConfigForm
  botType="market-making"
  onSubmit={(config) => {}}
  initialValues={savedConfig}
/>
```

#### C. Live Chart Component
```jsx
<LiveChart
  botId="bot-123"
  metric="profit"
  timeRange="1h"
/>
```

#### D. Trade History Table
```jsx
<TradeHistory
  botId="bot-123"
  limit={50}
  onLoadMore={() => {}}
/>
```

#### E. Market Selector
```jsx
<MarketSelector
  platform="polymarket"
  onSelect={(market) => {}}
/>
```

---

## Real-Time Updates

### WebSocket Integration

#### Client-Side Setup (React)

```typescript
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

function useBotUpdates(botId: string) {
  const [botData, setBotData] = useState(null);
  
  useEffect(() => {
    const socket = io('ws://localhost:3001');
    
    socket.emit('subscribe', { botId });
    
    socket.on('bot-update', (data) => {
      setBotData(data);
    });
    
    socket.on('trade-executed', (trade) => {
      // Handle new trade
    });
    
    return () => {
      socket.emit('unsubscribe', { botId });
      socket.disconnect();
    };
  }, [botId]);
  
  return botData;
}
```

#### Server-Side Setup (Node.js)

```javascript
const io = require('socket.io')(server);

io.on('connection', (socket) => {
  socket.on('subscribe', ({ botId }) => {
    socket.join(`bot-${botId}`);
  });
  
  socket.on('unsubscribe', ({ botId }) => {
    socket.leave(`bot-${botId}`);
  });
});

// Emit updates from bot
function emitBotUpdate(botId, data) {
  io.to(`bot-${botId}`).emit('bot-update', data);
}
```

---

## Security Considerations

### 1. API Key Storage

**NEVER store API keys in:**
- Frontend code
- LocalStorage
- Cookies (unless encrypted)
- Git repositories

**DO store API keys:**
- Backend database (encrypted)
- Environment variables
- Secure key management service (AWS KMS, HashiCorp Vault)

### 2. Authentication

```typescript
// Use JWT tokens
POST /api/auth/login
Body: {
  email: string,
  password: string
}
Response: {
  token: string,
  user: User
}

// Protect all bot endpoints
Headers: {
  Authorization: "Bearer <token>"
}
```

### 3. Rate Limiting

```javascript
// Implement rate limiting
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

---

## Implementation Guide

### Phase 1: Basic Setup (Week 1)

**Goals:**
- Set up React project
- Create basic layout
- Implement authentication
- Build configuration forms

**Tasks:**
1. Initialize React app with TypeScript
2. Set up routing (React Router)
3. Create layout components
4. Build login/register pages
5. Create bot configuration forms

### Phase 2: Bot Integration (Week 2)

**Goals:**
- Connect to backend API
- Start/stop bots
- Display bot status
- Show basic statistics

**Tasks:**
1. Create API client service
2. Build bot management components
3. Implement bot control functions
4. Display real-time status

### Phase 3: Data Visualization (Week 3)

**Goals:**
- Add charts and graphs
- Show trading history
- Display performance metrics
- Real-time updates

**Tasks:**
1. Integrate charting library
2. Build profit/loss charts
3. Create trade history table
4. Implement WebSocket updates

### Phase 4: Advanced Features (Week 4)

**Goals:**
- Multi-bot management
- Advanced analytics
- Alerts and notifications
- Mobile responsiveness

**Tasks:**
1. Support multiple bots
2. Add performance analytics
3. Implement alert system
4. Optimize for mobile

---

## Example Code

### 1. Complete Bot Dashboard Component

```typescript
// BotDashboard.tsx
import React, { useState, useEffect } from 'react';
import { BotCard } from './components/BotCard';
import { BotConfigModal } from './components/BotConfigModal';
import { useBots } from './hooks/useBots';

export function BotDashboard() {
  const { bots, startBot, stopBot, loading } = useBots();
  const [showConfig, setShowConfig] = useState(false);
  
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Trading Bots</h1>
        <button onClick={() => setShowConfig(true)}>
          + New Bot
        </button>
      </header>
      
      <div className="bot-grid">
        {bots.map(bot => (
          <BotCard
            key={bot.id}
            bot={bot}
            onStop={() => stopBot(bot.id)}
            onRestart={() => startBot(bot.id)}
          />
        ))}
      </div>
      
      {showConfig && (
        <BotConfigModal
          onClose={() => setShowConfig(false)}
          onSubmit={(config) => {
            startBot(config);
            setShowConfig(false);
          }}
        />
      )}
    </div>
  );
}
```

### 2. Bot Card Component

```typescript
// BotCard.tsx
import React from 'react';
import { Bot } from '../types';
import { useBotUpdates } from '../hooks/useBotUpdates';

interface BotCardProps {
  bot: Bot;
  onStop: () => void;
  onRestart: () => void;
}

export function BotCard({ bot, onStop, onRestart }: BotCardProps) {
  const liveData = useBotUpdates(bot.id);
  
  return (
    <div className="bot-card">
      <div className="bot-header">
        <h3>{bot.name}</h3>
        <span className={`status ${bot.status}`}>
          {bot.status}
        </span>
      </div>
      
      <div className="bot-stats">
        <div className="stat">
          <label>Profit</label>
          <value className={liveData?.profit >= 0 ? 'positive' : 'negative'}>
            ${liveData?.profit?.toFixed(2) || '0.00'}
          </value>
        </div>
        
        <div className="stat">
          <label>Trades</label>
          <value>{liveData?.trades || 0}</value>
        </div>
        
        <div className="stat">
          <label>Inventory</label>
          <value>{liveData?.inventory || 0}</value>
        </div>
      </div>
      
      <div className="bot-actions">
        {bot.status === 'running' ? (
          <button onClick={onStop} className="btn-danger">
            Stop
          </button>
        ) : (
          <button onClick={onRestart} className="btn-primary">
            Start
          </button>
        )}
      </div>
    </div>
  );
}
```

### 3. Configuration Form

```typescript
// BotConfigForm.tsx
import React from 'react';
import { useForm } from 'react-hook-form';

interface ConfigFormData {
  botType: 'arbitrage' | 'market-making';
  platform: string;
  marketQuery: string;
  targetSpread?: number;
  orderSize: number;
  maxInventory: number;
  dryRun: boolean;
}

export function BotConfigForm({ onSubmit }) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<ConfigFormData>();
  
  const botType = watch('botType');
  
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="config-form">
      <div className="form-group">
        <label>Bot Type</label>
        <select {...register('botType', { required: true })}>
          <option value="arbitrage">Arbitrage</option>
          <option value="market-making">Market Making</option>
        </select>
      </div>
      
      <div className="form-group">
        <label>Platform</label>
        <select {...register('platform', { required: true })}>
          <option value="polymarket">Polymarket</option>
          <option value="kalshi">Kalshi</option>
          <option value="limitless">Limitless</option>
        </select>
      </div>
      
      <div className="form-group">
        <label>Market Search</label>
        <input
          type="text"
          {...register('marketQuery', { required: true })}
          placeholder="e.g., Trump"
        />
      </div>
      
      {botType === 'market-making' && (
        <div className="form-group">
          <label>Target Spread</label>
          <input
            type="number"
            step="0.01"
            {...register('targetSpread', { required: true, min: 0.01 })}
            placeholder="0.04"
          />
        </div>
      )}
      
      <div className="form-group">
        <label>Order Size</label>
        <input
          type="number"
          {...register('orderSize', { required: true, min: 1 })}
          placeholder="10"
        />
      </div>
      
      <div className="form-group">
        <label>Max Inventory</label>
        <input
          type="number"
          {...register('maxInventory', { required: true, min: 1 })}
          placeholder="100"
        />
      </div>
      
      <div className="form-group">
        <label>
          <input type="checkbox" {...register('dryRun')} />
          Dry Run (Test Mode)
        </label>
      </div>
      
      <button type="submit" className="btn-primary">
        Start Bot
      </button>
    </form>
  );
}
```

### 4. API Client Service

```typescript
// api/botService.ts
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:3001';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const botService = {
  // Start a bot
  async startBot(config: BotConfig) {
    const response = await api.post('/api/bots/start', config);
    return response.data;
  },
  
  // Stop a bot
  async stopBot(botId: string) {
    const response = await api.post(`/api/bots/${botId}/stop`);
    return response.data;
  },
  
  // Get bot status
  async getBotStatus(botId: string) {
    const response = await api.get(`/api/bots/${botId}/status`);
    return response.data;
  },
  
  // List all bots
  async listBots() {
    const response = await api.get('/api/bots');
    return response.data;
  },
  
  // Get bot statistics
  async getBotStats(botId: string) {
    const response = await api.get(`/api/stats/${botId}`);
    return response.data;
  },
  
  // Get trade history
  async getTradeHistory(botId: string, limit = 100) {
    const response = await api.get(`/api/trades?botId=${botId}&limit=${limit}`);
    return response.data;
  },
};
```

### 5. Custom Hooks

```typescript
// hooks/useBots.ts
import { useState, useEffect } from 'react';
import { botService } from '../api/botService';

export function useBots() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadBots();
  }, []);
  
  async function loadBots() {
    try {
      const data = await botService.listBots();
      setBots(data.bots);
    } catch (error) {
      console.error('Failed to load bots:', error);
    } finally {
      setLoading(false);
    }
  }
  
  async function startBot(config) {
    try {
      const bot = await botService.startBot(config);
      setBots([...bots, bot]);
      return bot;
    } catch (error) {
      console.error('Failed to start bot:', error);
      throw error;
    }
  }
  
  async function stopBot(botId) {
    try {
      await botService.stopBot(botId);
      setBots(bots.map(b => 
        b.id === botId ? { ...b, status: 'stopped' } : b
      ));
    } catch (error) {
      console.error('Failed to stop bot:', error);
      throw error;
    }
  }
  
  return { bots, loading, startBot, stopBot, reload: loadBots };
}

// hooks/useBotUpdates.ts
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

export function useBotUpdates(botId: string) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    const socket = io(process.env.REACT_APP_WS_URL || 'ws://localhost:3001');
    
    socket.emit('subscribe', { botId });
    
    socket.on('bot-update', (update) => {
      setData(update);
    });
    
    return () => {
      socket.emit('unsubscribe', { botId });
      socket.disconnect();
    };
  }, [botId]);
  
  return data;
}
```

### 6. Styling Example (TailwindCSS)

```css
/* styles/dashboard.css */
.dashboard {
  @apply min-h-screen bg-gray-100;
}

.dashboard-header {
  @apply flex justify-between items-center p-6 bg-white shadow;
}

.bot-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6;
}

.bot-card {
  @apply bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition;
}

.bot-header {
  @apply flex justify-between items-center mb-4;
}

.status {
  @apply px-3 py-1 rounded-full text-sm font-semibold;
}

.status.running {
  @apply bg-green-100 text-green-800;
}

.status.stopped {
  @apply bg-red-100 text-red-800;
}

.bot-stats {
  @apply grid grid-cols-3 gap-4 mb-4;
}

.stat {
  @apply text-center;
}

.stat label {
  @apply block text-sm text-gray-600 mb-1;
}

.stat value {
  @apply block text-2xl font-bold;
}

.stat value.positive {
  @apply text-green-600;
}

.stat value.negative {
  @apply text-red-600;
}

.bot-actions {
  @apply flex gap-2;
}

.btn-primary {
  @apply flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700;
}

.btn-danger {
  @apply flex-1 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700;
}
```

---

## Backend API Implementation (Node.js + Express)

### Server Setup

```javascript
// server.js
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

app.use(cors());
app.use(express.json());

// Store active bots
const activeBots = new Map();

// Start bot endpoint
app.post('/api/bots/start', async (req, res) => {
  const { botType, config } = req.body;
  const botId = `bot-${Date.now()}`;
  
  // Spawn Python bot process
  const botProcess = spawn('python', [
    botType === 'arbitrage' ? 'arbitrage-bot/bot.py' : 'market-making-bot/bot.py',
    '--config', JSON.stringify(config)
  ]);
  
  // Capture bot output
  botProcess.stdout.on('data', (data) => {
    const output = data.toString();
    // Parse and emit updates
    io.to(`bot-${botId}`).emit('bot-update', {
      botId,
      output
    });
  });
  
  activeBots.set(botId, {
    id: botId,
    type: botType,
    process: botProcess,
    config,
    status: 'running',
    startTime: Date.now()
  });
  
  res.json({
    botId,
    status: 'running'
  });
});

// Stop bot endpoint
app.post('/api/bots/:botId/stop', (req, res) => {
  const { botId } = req.params;
  const bot = activeBots.get(botId);
  
  if (bot) {
    bot.process.kill();
    bot.status = 'stopped';
    
    res.json({
      botId,
      status: 'stopped'
    });
  } else {
    res.status(404).json({ error: 'Bot not found' });
  }
});

// Get bot status
app.get('/api/bots/:botId/status', (req, res) => {
  const { botId } = req.params;
  const bot = activeBots.get(botId);
  
  if (bot) {
    res.json({
      botId: bot.id,
      status: bot.status,
      uptime: Date.now() - bot.startTime,
      type: bot.type
    });
  } else {
    res.status(404).json({ error: 'Bot not found' });
  }
});

// List all bots
app.get('/api/bots', (req, res) => {
  const bots = Array.from(activeBots.values()).map(bot => ({
    id: bot.id,
    type: bot.type,
    status: bot.status,
    uptime: Date.now() - bot.startTime
  }));
  
  res.json({ bots });
});

// WebSocket connection
io.on('connection', (socket) => {
  console.log('Client connected');
  
  socket.on('subscribe', ({ botId }) => {
    socket.join(`bot-${botId}`);
  });
  
  socket.on('unsubscribe', ({ botId }) => {
    socket.leave(`bot-${botId}`);
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

---

## Deployment

### Frontend Deployment (Vercel/Netlify)

```bash
# Build for production
npm run build

# Deploy to Vercel
vercel deploy

# Or Netlify
netlify deploy --prod
```

### Backend Deployment (Heroku/Railway)

```bash
# Create Procfile
echo "web: node server.js" > Procfile

# Deploy to Heroku
heroku create
git push heroku main

# Or Railway
railway up
```

---

## Testing

### Frontend Tests

```typescript
// BotCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { BotCard } from './BotCard';

test('renders bot card with stats', () => {
  const bot = {
    id: 'bot-1',
    name: 'Test Bot',
    status: 'running',
    profit: 125.50,
    trades: 45
  };
  
  render(<BotCard bot={bot} onStop={() => {}} onRestart={() => {}} />);
  
  expect(screen.getByText('Test Bot')).toBeInTheDocument();
  expect(screen.getByText('$125.50')).toBeInTheDocument();
  expect(screen.getByText('45')).toBeInTheDocument();
});

test('calls onStop when stop button clicked', () => {
  const onStop = jest.fn();
  const bot = { id: 'bot-1', status: 'running' };
  
  render(<BotCard bot={bot} onStop={onStop} onRestart={() => {}} />);
  
  fireEvent.click(screen.getByText('Stop'));
  expect(onStop).toHaveBeenCalled();
});
```

---

## Resources

### Documentation
- React: https://react.dev
- Next.js: https://nextjs.org
- Socket.io: https://socket.io
- Chart.js: https://www.chartjs.org

### Design Inspiration
- TradingView: https://www.tradingview.com
- Binance: https://www.binance.com
- Coinbase Pro: https://pro.coinbase.com

### UI Libraries
- shadcn/ui: https://ui.shadcn.com
- Ant Design: https://ant.design
- Material-UI: https://mui.com

---

## Next Steps

1. **Set up development environment**
   - Install Node.js and npm
   - Create React app
   - Set up backend server

2. **Build core features**
   - Authentication
   - Bot management
   - Configuration forms

3. **Add real-time updates**
   - WebSocket integration
   - Live charts
   - Notifications

4. **Polish and deploy**
   - Responsive design
   - Error handling
   - Production deployment

---

## Support

For questions or issues:
- GitHub: https://github.com/sceptejas/Bnb-Hack-Bots
- Documentation: See individual bot READMEs

Good luck building! 🚀
