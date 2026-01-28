"""
Live trading executor for Binance Spot.

IMPORTANT:
- This executor MAY place REAL trades depending on configuration.
- Supports DRY_RUN, SPOT_TESTNET, and SPOT_MAINNET.
- Assumes LONG-ONLY, one position at a time.
- Assumes NO open position on startup.
- If the process restarts, the system assumes a FLAT state.

Responsibilities:
- Fetch closed candles
- Feed candles bar-by-bar into strategy logic
- Execute BUY / SELL decisions
- Persist completed trades to CSV
"""

import time
import numpy as np
from typing import Dict, List

from config.config import (
    SYMBOL,
    STRATEGY_PARAMS,
    POSITION_SIZE,
    LIVE_TRADES_CSV,
    ENTRY_TIMEFRAME,
    ENABLE_LIVE_TRADING,
    DRY_RUN,
    BINANCE,
)

from src.strategy.multi_tf import MultiTFTrendPullbackLogic
from src.exchange.binance_spot import BinanceSpotExchange
from src.utils.data import write_trades_to_csv
from src.utils.logger import get_logger
from src.validation.config_checks import validate_config


class LiveTradingExecutor:
    """
    Live execution engine.

    Contract:
    - One decision per CLOSED candle
    - Strategy emits intent only ("BUY", "SELL", None)
    - Executor owns all side effects (orders, state, persistence)
    """

    def __init__(self, poll_interval_seconds: int = 30):
        self.logger = get_logger("EXECUTOR")

        # ==================================================
        # Execution mode logging
        # ==================================================

        if DRY_RUN:
            self.logger.warning("[MODE] DRY_RUN enabled — no real orders will be sent")
        else:
            self.logger.warning(
                f"[MODE] LIVE execution enabled | env={BINANCE.get('ENV')}"
            )

        # ==================================================
        # Initialize exchange (fail-fast)
        # ==================================================

        self.exchange = BinanceSpotExchange()

        # ==================================================
        # Initialize strategy logic
        # ==================================================

        self.logic = MultiTFTrendPullbackLogic(
            entry_ema=STRATEGY_PARAMS["entry_ema"],
            rsi_period=STRATEGY_PARAMS["rsi_period"],
            rsi_entry=STRATEGY_PARAMS["rsi_entry"],
            confirm_ema_fast=STRATEGY_PARAMS["confirm_ema_fast"],
            confirm_ema_slow=STRATEGY_PARAMS["confirm_ema_slow"],
            exit_bars=STRATEGY_PARAMS["exit_bars"],
            confirm_tf_multiple=3,  # 15m trend derived from 5m bars
        )

        # ==================================================
        # Runtime configuration
        # ==================================================

        self.poll_interval = poll_interval_seconds

        # ==================================================
        # Candle state
        # ==================================================

        self.entry_tf_candles: List[Dict] = []
        self.last_close_time = None

        # ==================================================
        # Position & trade tracking
        # ==================================================

        self.in_position = False
        self.bars_in_trade = 0

        self.trades: List[Dict] = []
        self.trade_counter = 0
        self.current_trade: Dict = {}

        self.logger.warning(
            f"[EXECUTOR READY] symbol={SYMBOL} | timeframe={ENTRY_TIMEFRAME}"
        )
        self.logger.warning(
            "[ASSUMPTION] Executor assumes NO open position on startup."
        )

    # ==================================================
    # Candle Fetching
    # ==================================================

    def _fetch_new_closed_candle(self) -> Dict | None:
        """
        Fetch latest candles and return a newly closed candle only once.

        Ensures:
        - No lookahead bias
        - One decision per closed bar
        """
        candles = self.exchange.get_klines(
            interval=ENTRY_TIMEFRAME,
            limit=200,
        )

        if not candles:
            return None

        latest = candles[-1]

        if latest["close_time"] == self.last_close_time:
            return None

        self.last_close_time = latest["close_time"]
        self.entry_tf_candles = candles
        return latest

    # ==================================================
    # Main Execution Loop
    # ==================================================

    def run(self):
        self.logger.info("Execution loop started")

        try:
            while True:
                candle = self._fetch_new_closed_candle()

                if candle is None:
                    time.sleep(self.poll_interval)
                    continue

                self.logger.info(
                    f"[CANDLE] close_time={candle['close_time']} close={candle['close']}"
                )

                opens = np.array([c["open"] for c in self.entry_tf_candles])
                closes = np.array([c["close"] for c in self.entry_tf_candles])

                # Strategy decision
                decision = self.logic.on_bar(
                    opens=opens,
                    closes=closes,
                    in_position=self.in_position,
                )

                self.logger.info(
                    f"[DECISION] decision={decision} in_position={self.in_position}"
                )

                # ==================================================
                # ENTRY
                # ==================================================

                if decision == "BUY" and not self.in_position:
                    self.logger.info("[SIGNAL] BUY")

                    execution = self.exchange.place_market_order(
                        side="BUY",
                        quantity=POSITION_SIZE,
                    )

                    self.in_position = True
                    self.bars_in_trade = 0
                    self.trade_counter += 1

                    self.current_trade = {
                        "trade_id": f"T{self.trade_counter:03d}",
                        "symbol": SYMBOL,
                        "direction": "LONG",
                        "entry_time": candle["close_time"],
                        "entry_price": execution["price"],
                        "quantity": execution["executed_qty"],
                    }

                # ==================================================
                # EXIT
                # ==================================================

                elif decision == "SELL" and self.in_position:
                    self.logger.info("[SIGNAL] SELL")

                    execution = self.exchange.place_market_order(
                        side="SELL",
                        quantity=POSITION_SIZE,
                    )

                    self.in_position = False

                    self.current_trade.update({
                        "exit_time": candle["close_time"],
                        "exit_price": execution["price"],
                        "bars_held": self.bars_in_trade,
                        "environment": (
                            "DRY_RUN"
                            if DRY_RUN
                            else BINANCE.get("ENV")
                        ),
                    })

                    self.trades.append(self.current_trade)
                    write_trades_to_csv(LIVE_TRADES_CSV, self.trades)

                    self.current_trade = {}
                    self.bars_in_trade = 0

                # ==================================================
                # Position tracking
                # ==================================================

                if self.in_position:
                    self.bars_in_trade += 1

                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            self.logger.warning("Execution interrupted by user (Ctrl+C)")
            self.logger.warning(
                "If a position is open, it remains open on the exchange."
            )
        except Exception as e:
            self.logger.error(f"Fatal error in executor | {e}")
            raise


if __name__ == "__main__":
    validate_config()
    executor = LiveTradingExecutor()
    executor.run()
