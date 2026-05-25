"""Backtesting.py strategy implementation for the Aryan Price Action Framework."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd
from backtesting import Strategy

from risk_management import position_size, stop_and_target, trailing_stop


def build_trade_frame(feature_frame: pd.DataFrame, settings: Any) -> pd.DataFrame:
    """Convert engineered features into executable trade signals and levels."""

    result = feature_frame.copy()
    result["direction"] = 0
    result.loc[result["signal_long"], "direction"] = 1
    result.loc[result["signal_short"], "direction"] = -1

    entries = []
    stops = []
    targets = []

    for _, row in result.iterrows():
        direction = int(row["direction"])
        entry_price = float(row["close"])
        atr_value = float(row.get("atr", 0) or 0)

        if direction == 0:
            entries.append(False)
            stops.append(float("nan"))
            targets.append(float("nan"))
            continue

        stop_price, take_price = stop_and_target(
            entry_price=entry_price,
            atr_value=atr_value,
            direction=direction,
            reward_risk=settings.strategy.reward_risk,
            atr_multiplier=1.0,
        )
        entries.append(True)
        stops.append(stop_price)
        targets.append(take_price)

    result["entry_signal"] = entries
    result["stop_loss"] = stops
    result["take_profit"] = targets
    result["trailing_stop"] = result["close"] - result["atr"] * settings.strategy.trailing_stop_atr
    result.loc[result["direction"] < 0, "trailing_stop"] = result["close"] + result["atr"] * settings.strategy.trailing_stop_atr
    return result


class AryanPriceActionStrategy(Strategy):
    """Institutional-style structure, liquidity, and order-block strategy."""

    risk_per_trade = 0.01
    reward_risk = 2.5
    trailing_stop_atr = 1.5

    def init(self) -> None:
        self._last_direction = 0

    def _trade_size(self, entry_price: float, stop_price: float) -> float:
        capital = float(self.equity)
        return position_size(capital, self.risk_per_trade, entry_price, stop_price)

    def next(self) -> None:
        entry_price = float(self.data.Close[-1])
        close = float(self.data.Close[-1])

        entry_signal = bool(self.data.entry_signal[-1]) if hasattr(self.data, "entry_signal") else False
        direction = int(self.data.direction[-1]) if hasattr(self.data, "direction") else 0
        long_signal = entry_signal and direction > 0
        short_signal = entry_signal and direction < 0

        if self.position:
            if direction > 0 and close < float(self.data.trailing_stop[-1]):
                self.position.close()
            elif direction < 0 and close > float(self.data.trailing_stop[-1]):
                self.position.close()
            elif direction < 0 and self.position.is_long:
                self.position.close()
            elif direction > 0 and self.position.is_short:
                self.position.close()

        if self.position:
            return

        if long_signal:
            stop_price = float(self.data.stop_loss[-1])
            take_price = float(self.data.take_profit[-1])
            trade_size = self._trade_size(entry_price, stop_price)
            if trade_size > 0:
                self.buy(size=trade_size, sl=stop_price, tp=take_price)
                self._last_direction = 1

        elif short_signal:
            stop_price = float(self.data.stop_loss[-1])
            take_price = float(self.data.take_profit[-1])
            trade_size = self._trade_size(entry_price, stop_price)
            if trade_size > 0:
                self.sell(size=trade_size, sl=stop_price, tp=take_price)
                self._last_direction = -1
