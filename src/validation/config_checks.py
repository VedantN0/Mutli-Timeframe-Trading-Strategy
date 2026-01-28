"""
Configuration validation for trading execution.

This module performs FAIL-FAST checks to prevent
unsafe, ambiguous, or accidental execution.

The goal is to:
- Stop the system BEFORE any orders are placed
- Force explicit user intent
- Catch misconfiguration early and loudly
"""

from config.config import (
    ENABLE_LIVE_TRADING,
    DRY_RUN,
    SYMBOL,
    ENTRY_TIMEFRAME,
    STRATEGY_PARAMS,
    POSITION_SIZE,
    BINANCE,
)


# ==================================================
# Supported Binance Spot timeframes
# ==================================================

VALID_SPOT_TIMEFRAMES = {
    "1m", "3m", "5m", "15m", "30m",
    "1h", "2h", "4h", "6h", "12h", "1d",
}


def validate_config():
    """
    Validate user configuration before execution starts.

    This function MUST be called before:
    - initializing the exchange
    - starting the execution loop

    Raises
    ------
    RuntimeError
        If configuration is invalid, unsafe, or ambiguous.
    """

    # ==================================================
    # Execution mode sanity
    # ==================================================

    # At least one execution mode must be explicitly enabled
    if not ENABLE_LIVE_TRADING and not DRY_RUN:
        raise RuntimeError(
            "Invalid execution mode:\n"
            "- ENABLE_LIVE_TRADING is False\n"
            "- DRY_RUN is False\n\n"
            "Enable DRY_RUN for safe testing, or set ENABLE_LIVE_TRADING=True "
            "for real execution."
        )

    # ==================================================
    # Symbol validation
    # ==================================================

    if not SYMBOL or not isinstance(SYMBOL, str):
        raise RuntimeError(
            "SYMBOL must be a non-empty string "
            "(e.g. 'ETHUSDT', 'BTCUSDT')."
        )

    # ==================================================
    # Timeframe validation
    # ==================================================

    if ENTRY_TIMEFRAME not in VALID_SPOT_TIMEFRAMES:
        raise RuntimeError(
            f"Invalid ENTRY_TIMEFRAME: {ENTRY_TIMEFRAME}\n"
            f"Valid values: {sorted(VALID_SPOT_TIMEFRAMES)}"
        )

    # ==================================================
    # Strategy parameter validation
    # ==================================================

    required_keys = {
        "entry_ema",
        "rsi_period",
        "rsi_entry",
        "confirm_ema_fast",
        "confirm_ema_slow",
        "exit_bars",
    }

    missing = required_keys - STRATEGY_PARAMS.keys()
    if missing:
        raise RuntimeError(
            f"Missing STRATEGY_PARAMS keys: {missing}"
        )

    if STRATEGY_PARAMS["confirm_ema_fast"] >= STRATEGY_PARAMS["confirm_ema_slow"]:
        raise RuntimeError(
            "Invalid strategy parameters:\n"
            "- confirm_ema_fast must be LESS than confirm_ema_slow."
        )

    if STRATEGY_PARAMS["exit_bars"] <= 0:
        raise RuntimeError(
            "Invalid strategy parameters:\n"
            "- exit_bars must be greater than 0."
        )

    # ==================================================
    # Position sizing validation
    # ==================================================

    if POSITION_SIZE <= 0:
        raise RuntimeError(
            "POSITION_SIZE must be greater than 0.\n"
            "Use a very small value when testing."
        )

    # ==================================================
    # Binance environment validation
    # ==================================================

    env = BINANCE.get("ENV")

    if env not in ("SPOT_TESTNET", "SPOT_MAINNET"):
        raise RuntimeError(
            f"Invalid BINANCE.ENV: {env}\n"
            "Valid values: 'SPOT_TESTNET', 'SPOT_MAINNET'."
        )

    # ==================================================
    # API credential validation
    # ==================================================

    # DRY_RUN does NOT require API keys
    if not DRY_RUN:
        if not BINANCE.get("API_KEY") or not BINANCE.get("API_SECRET"):
            raise RuntimeError(
                "Binance API credentials missing.\n"
                "API_KEY and API_SECRET are required for "
                "SPOT_TESTNET and SPOT_MAINNET execution."
            )
