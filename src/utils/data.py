import csv
import os
from datetime import datetime, timezone
from typing import Dict, List


# ==============================
# Candle Utilities
# ==============================

def to_utc_datetime(timestamp_ms: int) -> datetime:
    """
    Convert millisecond timestamp to UTC datetime.
    """
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)


def normalize_kline(kline: List) -> Dict:
    """
    Normalize a Binance kline (candlestick) into a standard dict.
    """
    return {
        "open_time": to_utc_datetime(kline[0]),
        "close_time": to_utc_datetime(kline[6]),
        "open": float(kline[1]),
        "high": float(kline[2]),
        "low": float(kline[3]),
        "close": float(kline[4]),
        "volume": float(kline[5]),
    }


# ==============================
# CSV Utilities
# ==============================

CSV_FIELDS = [
    "trade_id",
    "symbol",
    "direction",
    "entry_time",
    "entry_price",
    "exit_time",
    "exit_price",
    "bars_held",
    "environment",
]


def write_trades_to_csv(file_path: str, trades: List[Dict]) -> None:
    """
    Append completed trades to a CSV file.

    This function is NON-FATAL:
    - CSV write failures must never crash live trading.
    """
    if not trades:
        return

    file_exists = os.path.exists(file_path)

    try:
        with open(file_path, mode="a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)

            if not file_exists:
                writer.writeheader()

            # Write only the most recent trade
            trade = trades[-1]

            writer.writerow({
                "trade_id": trade.get("trade_id"),
                "symbol": trade.get("symbol"),
                "direction": trade.get("direction"),
                "entry_time": (
                    trade["entry_time"].isoformat()
                    if trade.get("entry_time") else None
                ),
                "entry_price": trade.get("entry_price"),
                "exit_time": (
                    trade["exit_time"].isoformat()
                    if trade.get("exit_time") else None
                ),
                "exit_price": trade.get("exit_price"),
                "bars_held": trade.get("bars_held"),
                "environment": trade.get("environment"),
            })

    except Exception as e:
        # Intentionally swallow exceptions to avoid crashing live trading
        print(f"[WARN] Failed to write trades to CSV: {e}")
