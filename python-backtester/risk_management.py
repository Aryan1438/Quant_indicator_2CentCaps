"""Risk and trade sizing utilities for the Aryan Price Action Framework."""

from __future__ import annotations

from dataclasses import dataclass
from math import floor

import pandas as pd


@dataclass(slots=True)
class RiskPlan:
    capital: float
    risk_per_trade: float
    reward_risk: float
    trailing_stop_atr: float = 1.5


def position_size(capital: float, risk_per_trade: float, entry_price: float, stop_price: float) -> float:
    """Size a position so the loss at the stop equals the risk budget."""

    risk_amount = capital * risk_per_trade
    stop_distance = abs(entry_price - stop_price)
    if stop_distance <= 0:
        return 0.0
    return max(0.0, risk_amount / stop_distance)


def stop_and_target(entry_price: float, atr_value: float, direction: int, reward_risk: float, atr_multiplier: float = 1.0) -> tuple[float, float]:
    """Build a volatility-adjusted stop and target."""

    risk_distance = max(atr_value * atr_multiplier, entry_price * 0.001)
    if direction > 0:
        stop = entry_price - risk_distance
        target = entry_price + (entry_price - stop) * reward_risk
    else:
        stop = entry_price + risk_distance
        target = entry_price - (stop - entry_price) * reward_risk
    return stop, target


def trailing_stop(current_stop: float, atr_value: float, close_price: float, direction: int, multiplier: float = 1.5) -> float:
    """Move a stop in the trade's favor using an ATR trail."""

    trail_distance = atr_value * multiplier
    if direction > 0:
        return max(current_stop, close_price - trail_distance)
    return min(current_stop, close_price + trail_distance)


def expectancy(win_rate: float, avg_win_rr: float, avg_loss_rr: float = 1.0) -> float:
    """Return expectancy in R units."""

    return (win_rate * avg_win_rr) - ((1 - win_rate) * avg_loss_rr)


def trade_summary(trades: pd.DataFrame) -> dict[str, float]:
    """Compact trade-statistics helper used in the report pipeline."""

    if trades.empty:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "average_rr": 0.0,
            "expectancy": 0.0,
        }

    wins = trades[trades["PnL"] > 0]
    losses = trades[trades["PnL"] <= 0]
    profit_factor = wins["PnL"].sum() / abs(losses["PnL"].sum()) if not losses.empty and abs(losses["PnL"].sum()) > 0 else float("inf")
    average_rr = trades["R"].mean() if "R" in trades else 0.0
    win_rate = len(wins) / len(trades)
    return {
        "total_trades": float(len(trades)),
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "average_rr": average_rr,
        "expectancy": expectancy(win_rate, average_rr or 0.0),
    }
