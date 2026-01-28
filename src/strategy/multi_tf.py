import numpy as np


class MultiTFTrendPullbackLogic:
    """
    Pure strategy logic component.

    Characteristics:
    - Framework agnostic
    - No execution, no I/O
    - Operates strictly bar-by-bar
    - Maintains internal state across bars

    Contract:
    - Called exactly once per CLOSED base-timeframe candle
    - Consumes arrays of historical opens/closes (including latest bar)
    - Emits INTENT only (no orders)

    Returned signals:
    - "BUY"  -> request to open a long position
    - "SELL" -> request to exit an existing position
    - None   -> no action
    """

    def __init__(
        self,
        entry_ema: int,
        rsi_period: int,
        rsi_entry: float,
        confirm_ema_fast: int,
        confirm_ema_slow: int,
        exit_bars: int,
        confirm_tf_multiple: int,
    ):
        # ----------------------------
        # Strategy parameters
        # ----------------------------
        self.entry_ema = entry_ema
        self.rsi_period = rsi_period
        self.rsi_entry = rsi_entry
        self.confirm_ema_fast = confirm_ema_fast
        self.confirm_ema_slow = confirm_ema_slow
        self.exit_bars = exit_bars
        self.confirm_tf_multiple = confirm_tf_multiple

        # ----------------------------
        # Internal state
        # ----------------------------
        self.bar_index = 0
        self.bars_in_trade = 0

        # Higher-timeframe trend state
        self.htf_trend_bullish = None
        self.htf_closes = []

    # ==================================================
    # Indicator helpers
    # ==================================================

    @staticmethod
    def ema(values, period):
        """
        Compute EMA over given values.
        """
        if len(values) < period:
            return None

        alpha = 2 / (period + 1)
        ema_val = values[0]
        for v in values[1:]:
            ema_val = alpha * v + (1 - alpha) * ema_val
        return ema_val

    @staticmethod
    def rsi(values, period):
        """
        Compute RSI over given values.
        """
        if len(values) < period + 1:
            return None

        deltas = np.diff(values)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    # ==================================================
    # Higher timeframe logic
    # ==================================================

    def _update_confirm_trend(self, closes):
        """
        Update higher timeframe trend using aggregated closes.

        Assumes this method is called every `confirm_tf_multiple`
        base-timeframe bars.
        """
        self.htf_closes.append(closes[-1])

        if len(self.htf_closes) < self.confirm_ema_slow:
            self.htf_trend_bullish = None
            return

        fast = self.ema(
            self.htf_closes[-self.confirm_ema_fast:],
            self.confirm_ema_fast,
        )
        slow = self.ema(
            self.htf_closes[-self.confirm_ema_slow:],
            self.confirm_ema_slow,
        )

        self.htf_trend_bullish = fast > slow

    # ==================================================
    # Core logic
    # ==================================================

    def on_bar(self, opens, closes, in_position) -> str | None:
        """
        Process one CLOSED base-timeframe candle.

        Parameters
        ----------
        opens : array-like
            Historical open prices (including latest closed bar)
        closes : array-like
            Historical close prices (including latest closed bar)
        in_position : bool
            Whether the executor currently holds a position

        Returns
        -------
        str or None
            "BUY", "SELL", or None
        """

        self.bar_index += 1

        # Update higher timeframe trend periodically
        if self.bar_index % self.confirm_tf_multiple == 0:
            self._update_confirm_trend(closes)

        # ----------------------------
        # Exit logic (time-based)
        # ----------------------------
        if in_position:
            self.bars_in_trade += 1

            if self.bars_in_trade >= self.exit_bars:
                self.bars_in_trade = 0
                return "SELL"

            return None

        # ----------------------------
        # Entry logic
        # ----------------------------
        if self.htf_trend_bullish is False:
            return None

        if len(closes) < max(self.entry_ema, self.rsi_period) + 1:
            return None

        entry_ema = self.ema(closes[-self.entry_ema:], self.entry_ema)
        rsi_val = self.rsi(
            closes[-(self.rsi_period + 1):],
            self.rsi_period,
        )

        pullback = closes[-1] <= entry_ema
        rsi_ok = rsi_val >= self.rsi_entry
        bullish_candle = closes[-1] > opens[-1]

        if pullback and rsi_ok and bullish_candle:
            return "BUY"

        return None
