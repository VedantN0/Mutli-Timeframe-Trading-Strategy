"""
Binance Spot exchange wrapper.

WARNING:
- This class MAY place REAL orders on Binance Spot.
- Depending on configuration, this can involve REAL funds.
- There is NO leverage and NO margin.
- You trade actual crypto assets on MAINNET.
- Misconfiguration may result in financial loss.

DESIGN NOTES:
- Binance Spot TESTNET does NOT support market data (klines).
- Therefore:
    * Market data is ALWAYS fetched from Spot MAINNET
    * Execution environment is controlled by API keys + config
- python-binance internally handles correct endpoint routing.
- We DO NOT manually override API_URL.

This class is intentionally strict and fail-fast.
"""

from typing import List, Dict

from binance.client import Client
from binance.exceptions import BinanceAPIException

from config.config import (
    BINANCE,
    SYMBOL,
    ENABLE_LIVE_TRADING,
    DRY_RUN,
)
from src.utils.data import normalize_kline
from src.utils.logger import get_logger


class BinanceSpotExchange:
    """
    Binance Spot exchange abstraction.

    Responsibilities:
    - Fetch closed market candles (Spot MAINNET only)
    - Place market orders (BUY / SELL)
    - Parse and return execution details

    This class does NOT:
    - Contain strategy logic
    - Run execution loops
    - Manage positions
    """

    def __init__(self):
        self.logger = get_logger("EXCHANGE")

        env = BINANCE.get("ENV")

        # ==================================================
        # Execution safety gates
        # ==================================================

        # Prevent ambiguous execution states:
        # - ENABLE_LIVE_TRADING=False AND DRY_RUN=False is invalid
        if not ENABLE_LIVE_TRADING and not DRY_RUN:
            raise RuntimeError(
                "Invalid execution state:\n"
                "- ENABLE_LIVE_TRADING is False\n"
                "- DRY_RUN is False\n\n"
                "Enable DRY_RUN for safe testing or "
                "set ENABLE_LIVE_TRADING=True for execution."
            )

        if env not in ("SPOT_TESTNET", "SPOT_MAINNET"):
            raise RuntimeError(
                f"Invalid BINANCE.ENV: {env}\n"
                "Valid values: 'SPOT_TESTNET', 'SPOT_MAINNET'."
            )

        # ==================================================
        # API credential checks
        # ==================================================

        api_key = BINANCE.get("API_KEY")
        api_secret = BINANCE.get("API_SECRET")

        # API keys are required ONLY if orders may be sent
        if not DRY_RUN:
            if not api_key or not api_secret:
                raise RuntimeError(
                    "Binance API credentials missing.\n"
                    "API_KEY and API_SECRET are required for "
                    "Spot execution (TESTNET or MAINNET)."
                )

        # ==================================================
        # Initialize Binance client
        # ==================================================

        # IMPORTANT:
        # - python-binance defaults to Spot MAINNET endpoints
        # - We intentionally DO NOT override API_URL
        # - Market data (klines) always comes from MAINNET
        # - Execution environment is determined by API keys
        self.client = Client(
            api_key=api_key if not DRY_RUN else None,
            api_secret=api_secret if not DRY_RUN else None,
        )

        self.logger.info(
            "[MARKET DATA] Binance Spot MAINNET (default python-binance routing)"
        )

        # ==================================================
        # Execution environment (logging only)
        # ==================================================

        if env == "SPOT_MAINNET":
            self.logger.warning(
                "[EXECUTION] Binance Spot MAINNET (REAL FUNDS)"
            )
        else:
            self.logger.warning(
                "[EXECUTION] Binance Spot TESTNET (PAPER FUNDS)"
            )

        if DRY_RUN:
            self.logger.warning(
                "[DRY_RUN] Orders will NOT be sent to Binance"
            )

        self.symbol = SYMBOL

        self.logger.info(
            f"[EXCHANGE READY] symbol={self.symbol} | env={env}"
        )

    # ==============================
    # Market Data
    # ==============================

    def get_klines(
        self,
        interval: str,
        limit: int = 200,
    ) -> List[Dict]:
        """
        Fetch latest CLOSED klines from Binance Spot MAINNET.

        Notes
        -----
        - Spot TESTNET does not provide klines
        - This method always uses MAINNET implicitly
        - No API key is required for this call

        Parameters
        ----------
        interval : str
            Binance kline interval (e.g. '5m', '15m')
        limit : int
            Number of candles to fetch

        Returns
        -------
        List[Dict]
            List of normalized candle dictionaries
        """
        try:
            klines = self.client.get_klines(
                symbol=self.symbol,
                interval=interval,
                limit=limit,
            )

            return [normalize_kline(k) for k in klines]

        except BinanceAPIException as e:
            self.logger.error(f"Failed to fetch klines | {e}")
            raise RuntimeError("Market data fetch failed") from e

    # ==============================
    # Order Execution
    # ==============================

    def place_market_order(
        self,
        side: str,
        quantity: float,
    ) -> Dict:
        """
        Place a market order on Binance Spot.

        In DRY_RUN mode:
        - No order is sent
        - A simulated execution is returned

        Parameters
        ----------
        side : str
            'BUY' or 'SELL'
        quantity : float
            Quantity of base asset to trade

        Returns
        -------
        Dict
            Executed (or simulated) order information
        """
        if side not in ("BUY", "SELL"):
            raise ValueError(f"Invalid order side: {side}")

        # ==================================================
        # DRY RUN — simulate execution
        # ==================================================

        if DRY_RUN:
            self.logger.warning(
                f"[DRY_RUN] Simulating market order | side={side} qty={quantity}"
            )

            return {
                "symbol": self.symbol,
                "side": side,
                "price": None,
                "executed_qty": quantity,
                "timestamp": None,
            }

        # ==================================================
        # REAL execution (TESTNET or MAINNET)
        # ==================================================

        try:
            self.logger.info(
                f"[ORDER] Placing market order | side={side} qty={quantity}"
            )

            order = self.client.create_order(
                symbol=self.symbol,
                side=side,
                type="MARKET",
                quantity=quantity,
            )

            fills = order.get("fills", [])
            if not fills:
                raise RuntimeError("Order executed but no fills returned")

            executed_qty = sum(float(f["qty"]) for f in fills)
            avg_price = (
                sum(float(f["price"]) * float(f["qty"]) for f in fills)
                / executed_qty
            )

            execution = {
                "symbol": self.symbol,
                "side": side,
                "price": avg_price,
                "executed_qty": executed_qty,
                "timestamp": order.get("transactTime"),
            }

            self.logger.info(
                f"[ORDER FILLED] side={side} qty={executed_qty} price={avg_price}"
            )

            return execution

        except BinanceAPIException as e:
            self.logger.error(f"Order placement failed | {e}")
            raise RuntimeError("Market order failed") from e
