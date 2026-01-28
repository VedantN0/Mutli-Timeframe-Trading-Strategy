# DISCLAIMER & IMPORTANT NOTICE (READ FIRST)

This repository contains **automated trading software** that is capable of placing **real orders on Binance Spot using real funds**.

By using this software, you explicitly acknowledge and agree that:

- This project is **NOT financial advice**
- This project is **NOT an investment recommendation**
- This project is **NOT a signal service**
- This project **does NOT guarantee profits or positive returns**
- Trading cryptocurrencies involves **significant financial risk**, including the risk of **losing all deployed capital**

This software is provided **strictly for educational, research, and system-building purposes**.

You are **solely responsible** for:
- How you configure the system
- Which execution mode you enable
- The API permissions you grant
- The funds you deploy
- Any trades executed using this code

The author assumes **NO liability** for:
- Financial losses
- Exchange downtime or API changes
- Misconfiguration or misuse
- Unexpected market behavior

> **If you do not fully understand API-based trading, exchange permissions, or automated execution, DO NOT run this system on a live account.**

---

# What This Project Is (and Is Not)

## What this project **IS**

- A **baseline, rule-based trading system**
- Designed to demonstrate:
  - clean system architecture
  - deterministic execution
  - correct bar-by-bar logic
  - safe live-trading practices
- A **starting point** that you are expected to:
  - study
  - modify
  - extend
  - improve

This project intentionally focuses on **engineering correctness**, not profit optimization.

It is best thought of as:
> “A minimal but correct trading engine that you can build on.”

---

## What this project is **NOT**

- Not a “plug-and-play money bot”
- Not optimized for PnL
- Not a hedge-fund strategy
- Not a complete trading system
- Not suitable for blind deployment with real capital

If your goal is “turn this on and make money”, this project is **not for you**.

If your goal is to **learn how real trading systems are built**, this project is exactly that.

---

# High-Level Overview

- **Market:** Binance Spot
- **Leverage:** None
- **Margin:** None
- **Direction:** Long-only
- **Execution:** Market orders on candle close
- **Decision frequency:** Exactly once per closed candle
- **Core goal:** Correct execution, not performance

The system enforces a **strict separation** between:
- configuration
- strategy logic
- execution
- exchange interaction
- logging and persistence

This makes the system:
- easier to reason about
- safer to run
- easier to extend

---

# Execution Modes (VERY IMPORTANT)

This system supports **three execution modes**, designed to be used **in order**.

## 1. DRY_RUN (Safest – Recommended First)

**What it does:**
- Uses **real market data**
- Runs the **full strategy logic**
- Generates BUY / SELL signals
- **Does NOT place any orders**
- Writes **simulated trades** to CSV

**What it is for:**
- Understanding how the strategy behaves
- Verifying logic and signals
- Learning the system with **zero risk**

**Funds required:** None  
**API keys required:** No  

---

## 2. SPOT_TESTNET (Execution Testing)

**What it does:**
- Places **real orders** on Binance **Spot Testnet**
- Uses **fake money**
- Exercises the **full execution pipeline**
- Behaves like real trading without financial risk

**What it is for:**
- Testing order placement
- Testing exchange behavior
- Testing latency, fills, and errors

**Funds required:** Fake only  
**API keys required:** Testnet keys  

---

## 3. SPOT_MAINNET (REAL TRADING)

**What it does:**
- Places **real orders** on Binance Spot
- Trades **real crypto assets**
- Uses **real funds**

**What it is for:**
- Live trading with full responsibility

**Funds required:** Real  
**API keys required:** Real  

> **You should NEVER start directly on MAINNET.**

---

# Folder Structure (Simplified)

```
config/
 └── config.py              # USER-EDITABLE configuration (only file you change)

src/
 ├── exchange/              # Binance Spot API abstraction
 ├── execution/             # Live execution engine
 ├── strategy/              # Pure strategy logic
 ├── utils/                 # Logging & CSV persistence
 └── validation/            # Fail-fast config checks

data/
 └── live_trades_<SYMBOL>.csv   # Auto-generated trade log
```

> **Users only need to edit `config/config.py`.**  
> All other files should be treated as system code.

---

# How the Strategy Works (Conceptually)

## 1. Multi-Timeframe Design

The strategy separates:
- **market regime identification**
- from **entry timing**

- Lower timeframe (e.g. 5m): execution
- Higher timeframe (derived): trend filter

This avoids counter-trend entries while keeping logic simple.

---

## 2. Entry Conditions (Long-Only)

A BUY signal is generated **only on a fully closed candle** when:

1. Price pulls back to a short-term EMA  
2. Momentum (RSI) is above a threshold  
3. The candle closes bullish (close > open)  
4. The higher-timeframe trend is not bearish  

All conditions must be met **on the same candle**.

There is:
- no intrabar logic
- no prediction
- no lookahead

---

## 3. Exit Logic

- Fixed, time-based exit
- Positions are closed after `exit_bars` closed candles

This ensures:
- deterministic behavior
- identical logic across all execution modes
- no discretionary exits

---

# Step-by-Step Setup Guide (Beginner Friendly)

## Step 1: Download the Code

### Option A: Git
```bash
git clone <your-repo-url>
cd <repo-folder>
```

### Option B: ZIP
- Download ZIP from GitHub
- Extract it
- Open the folder

---

## Step 2: Install Python

- Required version: **Python 3.10+**

Check:
```bash
python --version
```

Download:
https://www.python.org/downloads/

> On Windows, ensure **“Add Python to PATH”** is checked.

---

## Step 3: Create a Virtual Environment (Recommended)

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (PowerShell)
```powershell
python -m venv venv
venv\Scripts\activate
```

---

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 5: Configure the System

Open:
```
config/config.py
```

### Safe first run (recommended):
```python
ENABLE_LIVE_TRADING = False
DRY_RUN = True
BINANCE["ENV"] = "SPOT_TESTNET"
```

Set:
```python
SYMBOL = "BTCUSDT"
```

---

## Step 6: Run the System

```bash
python -m src.execution.executor
```

If configuration is unsafe or incomplete, the system will **fail immediately** with a clear error message.

---

# Trade Logging & Monitoring

- All completed trades are written to:
```
data/live_trades_<SYMBOL>.csv
```

- Each trade is labeled as:
  - `DRY_RUN`
  - `SPOT_TESTNET`
  - `SPOT_MAINNET`

- Logs include:
  - candle closes
  - decisions
  - order placement
  - execution results

Logs are printed in **UTC time** for consistency.

---

# Known Limitations (Intentional)

This system intentionally does **NOT** include:

- Stop-loss logic
- Take-profit logic
- Risk management
- Dynamic position sizing
- Portfolio logic
- Multiple simultaneous positions
- Restart-safe position recovery

These omissions are **by design**, to keep the system:
- understandable
- auditable
- easy to extend

---

# How You Are Expected to Improve It

This project is a **foundation**, not a finished product.

Common extensions include:
- Stop-loss / take-profit rules
- Balance-aware position sizing
- Limit orders instead of market orders
- Persistent state recovery on restart
- Additional filters or confirmations
- Performance metrics & analytics
- Paper-trading dashboards

---

# Final Notes

This project prioritizes:
- correctness over profits
- clarity over complexity
- safety over automation

If you choose to trade real funds, do so **carefully**, **incrementally**, and **with full understanding of the risks**.

> Always test changes in DRY_RUN or TESTNET before MAINNET.
