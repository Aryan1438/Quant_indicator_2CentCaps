# Research Notes

## Working Hypothesis

A structure-plus-liquidity model should outperform naive trend-following systems when entries are filtered by order-block confirmation, liquidity sweeps, and higher-timeframe alignment.

## Research Methodology

1. Convert TradingView OHLCV data into a normalized pandas dataframe.
2. Engineer market-structure features: swing highs/lows, BOS, CHoCH, FVG, liquidity sweeps, and higher-timeframe trend state.
3. Define confluence-based entry rules for long and short trades.
4. Apply ATR-based stops, fixed or dynamic reward-to-risk targets, and trailing stops.
5. Evaluate performance using win rate, profit factor, Sharpe ratio, Sortino ratio, CAGR, max drawdown, and expectancy.

## Data Considerations

- Use liquid instruments with reliable bar history.
- Align all timestamps to a single timezone.
- Confirm that the data source does not introduce lookahead bias.
- Segment performance by regime: trending, mean-reverting, and high-volatility periods.

## Initial Findings To Validate

- Liquidity sweep entries may reduce false breakouts.
- Order-block alignment should improve average trade quality.
- Higher-timeframe bias is expected to lower trade frequency but improve expectancy.

## Next Experiments

- Compare fixed versus dynamic reward-to-risk logic.
- Test the strategy across BTC, FX, and index futures.
- Run walk-forward validation and out-of-sample analysis.
- Add regime filters based on volatility and session structure.
