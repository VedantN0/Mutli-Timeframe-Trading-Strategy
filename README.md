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

> **“A minimal but correct trading engine that you can build on.”**

---

## What this project is **NOT**

- Not a “plug-and-play money bot”
- Not optimized for PnL
- Not a hedge-fund strategy
- Not a complete trading system
- Not suitable for blind deployment with real capital

If your goal is *“turn this on and make money”*, this project is **not for you**.

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
- Understanding strategy behavior
- Verifying signal correctness
- Learning the system with **zero risk**

**Funds required:** None  
**API keys required:** No  

---

## 2. SPOT_TESTNET (Execution Testing)

**What it does:**
- Places **real orders** on Binance **Spot Testnet**
- Uses **fake money**
- Exercises the **full execution pipeline**

**What it is for:**
- Testing order placement
- Testing exchange responses
- Understanding execution failures

**Important reality check:**
- Spot Testnet is **less stable** than Futures Testnet
- Balances and execution may be inconsistent
- This mode is for **API behavior testing**, not strategy validation

**Funds required:** Fake  
**API keys required:** Spot Testnet keys  

---

## 3. SPOT_MAINNET (REAL TRADING)

**What it does:**
- Places **real orders** on Binance Spot
- Trades **real crypto assets**
- Uses **real funds**

**What it is for:**
- Live trading with full responsibility

**Funds required:** Real  
**API keys required:** Mainnet API keys  

> **You should NEVER start directly on MAINNET.**

---

# Folder Structure (Simplified)

```
config/
 └── config.py                  # USER-EDITABLE configuration (only file you change)

src/
 ├── exchange/                  # Binance Spot API abstraction
 ├── execution/                 # Live execution engine
 ├── strategy/                  # Pure strategy logic
 ├── utils/                     # Logging & CSV persistence
 └── validation/                # Fail-fast config checks

data/
 └── live_trades_<SYMBOL>.csv   # Auto-generated trade log
```

> **Users only need to edit `config/config.py`.**  
> All other files should be treated as system code.

---

# Step-by-Step Setup Guide

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

# API Key Setup (READ CAREFULLY BEFORE RUNNING)

## A. Spot Testnet API Keys (Optional, Advanced)

### What Spot Testnet is (and is not)

- Spot Testnet is intended for **execution testing**
- It is **not guaranteed to behave like production**
- It may reject orders even when balances appear valid

### Step-by-step:

1. Visit:
   https://testnet.binance.vision

2. Log in using your **GitHub account**
   - This links your testnet identity to Binance

3. Create a **Spot Testnet API key**
   - Enable:
     - Reading
     - Spot Trading
   - Do NOT enable withdrawals

4. Copy the API key and secret

5. Paste them into `config/config.py`:
   ```python
   BINANCE["API_KEY"] = "..."
   BINANCE["API_SECRET"] = "..."
   BINANCE["ENV"] = "SPOT_TESTNET"
   ```

---

## B. Spot Mainnet API Keys (REAL FUNDS – HIGH RISK)

Proceed **only if you fully understand the risks**.

### Step-by-step:

1. Log in to your Binance account
2. Navigate to **API Management**
3. Create a **new API key**
4. Configure permissions:
   - Reading
   - Spot & Margin Trading
   - Withdrawals (DO NOT ENABLE)

5. **Enable IP restriction (STRONGLY RECOMMENDED)**
   - Add your current public IP address
   - This prevents unauthorized access if keys are leaked

6. Paste keys into `config/config.py`:
   ```python
   BINANCE["API_KEY"] = "..."
   BINANCE["API_SECRET"] = "..."
   BINANCE["ENV"] = "SPOT_MAINNET"
   ENABLE_LIVE_TRADING = True
   DRY_RUN = False
   ```

> **Always start with very small capital.**

---

# Step 6: Running the System

From the project root:

```bash
python -m src.execution.executor
```

The system will:
- validate configuration
- connect to the exchange
- wait for closed candles
- make exactly one decision per candle

---

# How to Stop the System (IMPORTANT)

### Graceful shutdown
- Press **CTRL + C** in the terminal
- The process exits immediately
- No new orders are placed after shutdown

---

## What Happens If You Stop While in a Position

This system intentionally does **NOT**:
- persist open positions across restarts
- auto-close positions on shutdown
- reconcile exchange state on startup

If you stop the system while in a position:
- The position **remains open on the exchange**
- On restart, the system **assumes no position**
- You must manually manage or close that position

This behavior is intentional to keep the system:
- simple
- deterministic
- easy to reason about

---

# Trade Logging

Trades are written to:
```
data/live_trades_<SYMBOL>.csv
```

Notes:
- The file is created automatically
- The `data/` folder must exist
- Trades are appended, not overwritten
- Each trade is tagged with its execution environment

---

# Known Limitations (Intentional)

This system does **NOT** include:
- Stop-loss logic
- Take-profit logic
- Risk management
- Dynamic position sizing
- Portfolio management
- Restart-safe position recovery

These omissions are **intentional** and left as exercises for extension.

---

# Final Notes

This project prioritizes:
- correctness over profits
- clarity over complexity
- safety over automation

> Always test **DRY_RUN → TESTNET → MAINNET**, in that order.
