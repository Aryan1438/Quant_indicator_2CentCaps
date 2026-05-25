"""Indicator and feature engineering utilities for the research backtester."""

from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

import numpy as np
import pandas as pd


PRICE_COLUMNS = ["open", "high", "low", "close", "volume"]


def validate_ohlcv_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize and validate a TradingView-exported OHLCV dataframe."""

    missing = [column for column in PRICE_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required OHLCV columns: {missing}")

    result = frame.copy()
    if "date" in result.columns and not isinstance(result.index, pd.DatetimeIndex):
        result["date"] = pd.to_datetime(result["date"], utc=True, errors="coerce")
        result = result.set_index("date")

    if not isinstance(result.index, pd.DatetimeIndex):
        result.index = pd.to_datetime(result.index, utc=True, errors="coerce")

    result = result.sort_index()
    result[PRICE_COLUMNS] = result[PRICE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    result = result.dropna(subset=PRICE_COLUMNS)
    return result


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = frame["high"] - frame["low"]
    high_close = (frame["high"] - frame["close"].shift(1)).abs()
    low_close = (frame["low"] - frame["close"].shift(1)).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def zscore(series: pd.Series, window: int = 20) -> pd.Series:
    mean = series.rolling(window).mean()
    std = series.rolling(window).std(ddof=0).replace(0, np.nan)
    return (series - mean) / std


def pivots(series: pd.Series, window: int = 3, kind: str = "high") -> pd.Series:
    """Confirm swing pivots with a centered window and shift to avoid lookahead in trading logic."""

    rolling = series.rolling(2 * window + 1, center=True)
    if kind == "high":
        pivot = series.eq(rolling.max())
    else:
        pivot = series.eq(rolling.min())
    return pivot.fillna(False).shift(window).fillna(False)


def detect_structure(frame: pd.DataFrame, swing_window: int = 3) -> pd.DataFrame:
    """Detect swing highs/lows, BOS, and CHoCH regimes."""

    result = frame.copy()
    result["atr"] = atr(result)
    result["rsi"] = rsi(result["close"])
    result["swing_high"] = pivots(result["high"], swing_window, kind="high")
    result["swing_low"] = pivots(result["low"], swing_window, kind="low")

    result["last_swing_high"] = result["high"].where(result["swing_high"]).ffill()
    result["last_swing_low"] = result["low"].where(result["swing_low"]).ffill()

    trend_state = 0
    bos_up = []
    bos_down = []
    choch_up = []
    choch_down = []

    for _, row in result.iterrows():
        break_up = bool(pd.notna(row["last_swing_high"]) and row["close"] > row["last_swing_high"])
        break_down = bool(pd.notna(row["last_swing_low"]) and row["close"] < row["last_swing_low"])

        bos_up.append(break_up and trend_state >= 0)
        bos_down.append(break_down and trend_state <= 0)
        choch_up.append(break_up and trend_state < 0)
        choch_down.append(break_down and trend_state > 0)

        if break_up:
            trend_state = 1
        elif break_down:
            trend_state = -1

    result["bos_up"] = bos_up
    result["bos_down"] = bos_down
    result["choch_up"] = choch_up
    result["choch_down"] = choch_down
    result["structure_bias"] = np.select(
        [result["bos_up"] | result["choch_up"], result["bos_down"] | result["choch_down"]],
        [1, -1],
        default=0,
    )
    return result


def detect_liquidity_sweeps(frame: pd.DataFrame, sweep_buffer_atr: float = 0.15) -> pd.DataFrame:
    result = frame.copy()
    buffer = result["atr"] * sweep_buffer_atr
    result["liquidity_sweep_low"] = (
        result["low"] < (result["last_swing_low"] - buffer)
    ) & (result["close"] > result["last_swing_low"])
    result["liquidity_sweep_high"] = (
        result["high"] > (result["last_swing_high"] + buffer)
    ) & (result["close"] < result["last_swing_high"])
    return result


def detect_fvg(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["bullish_fvg"] = (result["low"].shift(1) > result["high"].shift(2))
    result["bearish_fvg"] = (result["high"].shift(1) < result["low"].shift(2))
    result["fvg_mid"] = np.where(
        result["bullish_fvg"],
        (result["high"].shift(2) + result["low"].shift(1)) / 2,
        np.where(result["bearish_fvg"], (result["low"].shift(2) + result["high"].shift(1)) / 2, np.nan),
    )
    return result


def build_mtf_trend(frame: pd.DataFrame, higher_timeframes: Iterable[str] = ("4H", "1D")) -> pd.DataFrame:
    """Create a higher-timeframe trend ensemble using EMA alignment."""

    result = frame.copy()
    trend_columns = []

    for timeframe in higher_timeframes:
        resampled = (
            result[["open", "high", "low", "close", "volume"]]
            .resample(timeframe)
            .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
            .dropna()
        )
        fast = ema(resampled["close"], 20)
        slow = ema(resampled["close"], 50)
        trend = np.where(fast > slow, 1, np.where(fast < slow, -1, 0))
        aligned = pd.Series(trend, index=resampled.index).reindex(result.index, method="ffill")
        column = f"mtf_{timeframe.lower()}"
        result[column] = aligned.fillna(0).astype(int)
        trend_columns.append(column)

    if trend_columns:
        result["mtf_trend"] = result[trend_columns].sum(axis=1).apply(lambda value: 1 if value > 0 else -1 if value < 0 else 0)
    else:
        result["mtf_trend"] = 0
    return result


def build_feature_frame(frame: pd.DataFrame, settings: Any) -> pd.DataFrame:
    """Full feature pipeline used by both the backtester and the dashboard."""

    result = validate_ohlcv_frame(frame)
    result = detect_structure(result, swing_window=settings.strategy.swing_window)
    result = detect_liquidity_sweeps(result, sweep_buffer_atr=settings.strategy.liquidity_sweep_buffer_atr)
    result = detect_fvg(result)
    result = build_mtf_trend(result, settings.strategy.higher_timeframes)

    result["premium"] = (result["last_swing_high"] + result["last_swing_low"]) / 2
    result["discount"] = result["premium"]
    result["bullish_order_block"] = result["bos_up"] | result["choch_up"]
    result["bearish_order_block"] = result["bos_down"] | result["choch_down"]
    result["institutional_volume"] = zscore(result["volume"], 20).fillna(0) > 1.0
    result["signal_long"] = (
        (result["structure_bias"] >= 0)
        & result["bullish_order_block"]
        & result["liquidity_sweep_low"]
        & (result["mtf_trend"] >= 0)
        & (result["bullish_fvg"] | ~settings.strategy.require_fvg_confirmation)
    )
    result["signal_short"] = (
        (result["structure_bias"] <= 0)
        & result["bearish_order_block"]
        & result["liquidity_sweep_high"]
        & (result["mtf_trend"] <= 0)
        & (result["bearish_fvg"] | ~settings.strategy.require_fvg_confirmation)
    )
    result["trade_bias"] = np.select([result["signal_long"], result["signal_short"]], [1, -1], default=0)
    return result
