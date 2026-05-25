# Strategy Documentation

## Overview

Aryan Price Action Framework is an institutional-style Smart Money Concepts research system designed to study price structure, liquidity, and execution quality.

## Signal Model

### Long Setup

A long setup is valid when the following conditions align:

- Bullish BOS or CHoCH confirmation
- Bullish order-block confirmation
- Sell-side liquidity sweep confirmation
- Higher-timeframe trend is bullish or neutral
- Optional bullish FVG confirmation
- Price is in discount relative to the recent swing range

### Short Setup

A short setup is valid when the following conditions align:

- Bearish BOS or CHoCH confirmation
- Bearish order-block confirmation
- Buy-side liquidity sweep confirmation
- Higher-timeframe trend is bearish or neutral
- Optional bearish FVG confirmation
- Price is in premium relative to the recent swing range

## Risk Framework

- Fixed fractional risk per trade
- ATR-based stop loss
- Reward-to-risk targeting
- Trailing stop logic
- One open position at a time

## Execution Model

The Python backtester evaluates bar-by-bar signals and records trade outcomes. The Pine Script version is designed for chart-based research, live signal inspection, and TradingView alert generation.

## Trade Management

- The initial stop is set beyond recent structural extremes using ATR.
- The first profit target is computed from the configured reward-to-risk multiple.
- Trailing stops tighten as price moves favorably.
- Opposite structure breaks can be used as discretionary exits.

## Validation Checklist

- No lookahead bias in signal generation.
- Risk sizing respects account capital.
- Performance metrics are reproducible.
- Dashboard outputs match backtest exports.
- Results are documented with research assumptions.
