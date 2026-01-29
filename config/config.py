"""
Central configuration file for the trading system (BINANCE SPOT).

IMPORTANT:
- This system CAN place REAL trades on Binance Spot (MAINNET).
- There is NO leverage and NO margin.
- You trade actual crypto assets (e.g. ETH, BTC).
- Misconfiguration can result in real financial loss.
- You are solely responsible for your account and trades.

Edit ONLY this file to configure the system.
"""

# ==================================================
# EXECUTION MODE & SAFETY SWITCHES (MANDATORY)
# ==================================================

# ENABLE_LIVE_TRADING
# -------------------
# This MUST be set to True to allow ANY real order execution
# on Binance (MAINNET or TESTNET).
#
# Set this to True ONLY after:
# 1. You have reviewed the code
# 2. You understand the strategy
# 3. You have configured API credentials correctly
# 4. You accept the risks of automated trading
ENABLE_LIVE_TRADING = False


# DRY_RUN
# -------
# If True:
# - NO orders are sent to Binance
# - Strategy runs on REAL market data
# - Trades are SIMULATED and written to CSV
# - API keys are NOT required
#
# This is the SAFEST way to test the system.
#
# Typical usage:
# - First run:  DRY_RUN = True
# - Later:      DRY_RUN = False + SPOT_TESTNET
# - Final:      DRY_RUN = False + SPOT_MAINNET
DRY_RUN = True


# ==================================================
# Trading Instrument (SPOT)
# ==================================================

# Binance Spot symbol (examples: ETHUSDT, BTCUSDT)
SYMBOL = "BTCUSDT"


# ==================================================
# Timeframe Configuration
# ==================================================

# Base timeframe for execution.
# The strategy runs exactly once per CLOSED candle.
ENTRY_TIMEFRAME = "5m"


# ==================================================
# Strategy Parameters
# ==================================================

# These parameters control ONLY the strategy logic.
# They do NOT manage risk or capital allocation.

STRATEGY_PARAMS = {
    "entry_ema": 8,              # EMA period for pullback detection
    "rsi_period": 14,            # RSI lookback
    "rsi_entry": 50,             # Minimum RSI for long entry
    "confirm_ema_fast": 50,      # Fast EMA for higher timeframe trend
    "confirm_ema_slow": 200,     # Slow EMA for higher timeframe trend
    "exit_bars": 8,              # Time-based exit (number of bars)
}


# ==================================================
# Position Sizing (SPOT)
# ==================================================

# Fixed order quantity per trade.
# This is an ABSOLUTE quantity of the BASE asset.
#
# Example:
# - SYMBOL = ETHUSDT
# - POSITION_SIZE = 0.02
# → Each trade buys/sells 0.02 ETH
#
# IMPORTANT:
# - Ensure you have sufficient balance (MAINNET)
# - Start with the MINIMUM possible size when testing
POSITION_SIZE = 0.02


# ==================================================
# Binance Configuration (SPOT)
# ==================================================

# Supported environments:
# - SPOT_TESTNET  → Fake money, real execution (RECOMMENDED for testing)
# - SPOT_MAINNET  → Real money, real execution
#
# DRY_RUN overrides execution and prevents ALL orders.
BINANCE = {
    "ENV": "SPOT_TESTNET",   # SPOT_TESTNET or SPOT_MAINNET

    # API credentials:
    # - Required for SPOT_TESTNET and SPOT_MAINNET
    # - NOT required for DRY_RUN
    "API_KEY": "",
    "API_SECRET": "",
}

# Binance base URLs (DO NOT MODIFY)
BINANCE_SPOT_MAINNET_URL = "https://api.binance.com"
BINANCE_SPOT_TESTNET_URL = "https://testnet.binance.vision"


# ==================================================
# Trade Logging
# ==================================================

# CSV file where completed trades are recorded
# The file is created automatically if it does not exist
LIVE_TRADES_CSV = f"data/live_trades_{SYMBOL}.csv"


# ==================================================
# Logging Configuration
# ==================================================

# Logging level:
# DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"
