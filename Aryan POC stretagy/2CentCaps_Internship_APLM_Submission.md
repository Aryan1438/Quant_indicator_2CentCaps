# 2Cent Caps Internship Submission

## Project Title
Aryan POC Liquidity Model (APLM) for XAUUSD Intraday Trading

## Author
Aryan Govindbhai Patel

## Context
This file is prepared as part of the 2Cent Caps internship work submission. It consolidates the strategy thesis, operational framework, and performance backtesting outcomes for APLM.

## Research Scope
- Market: XAUUSD
- Timeframe: 5 Minute
- Trading Session Focus: New York Session
- Research/Backtest Period: March 2026 to June 2026
- Sample Size: 100+ trades (manual testing)

## Strategy Summary
The Aryan POC Liquidity Model (APLM) is a discretionary intraday framework built around:

1. Fixed Range Volume Profile
2. Point of Control (POC)
3. Smart Money Concepts (SMC)
4. Liquidity Theory
5. Session Analysis

Core idea: price tends to move from liquidity to liquidity, while POC acts as an institutional reference level and liquidity magnet.

## Session Logic
1. Asian Session: creates liquidity pools.
2. London Session: expands or sweeps liquidity and reveals intent.
3. New York Session: execution window for directional trades.

Execution window used in the model: 5:30 PM IST to 8:30 PM IST.

## Volume Profile Framework
Fixed Range Volume Profile is applied from:

- Start: 5:30 AM IST
- End: 5:30 PM IST

Derived levels:
- POC
- Value Area High (VAH)
- Value Area Low (VAL)

## Bias and Trade Qualification
Daily bias is defined using liquidity already taken and probable next liquidity objective:

- Bullish bias: focus on buys only.
- Bearish bias: focus on sells only.

Trade is qualified when:
- New York session is active.
- Price is interacting near volume profile levels.
- POC interaction is present.
- Bias aligns with setup direction.
- Conditions are not choppy and liquidity narrative is coherent.

## Risk Model
- Max risk per trade: 1%
- Typical stop range: 100 to 200 points (structure/volatility based)
- Preferred target: 1.5R to 2R
- Trade frequency: 1 to 2 high-quality trades per day

## Backtesting Results
- Win Rate: about 66%
- Average Risk-Reward: 2.2 : 1
- Maximum Consecutive Losses: 2

Expectancy calculation:

(0.66 x 2.2) - (0.34 x 1) = +1.11R

Positive expectancy indicates favorable long-term profitability under disciplined execution.

## Strengths
1. Simple and structured framework.
2. Session-based execution logic.
3. Institutional liquidity alignment.
4. High reward-to-risk profile.
5. Positive expectancy.
6. Adaptable to varying market conditions.

## Limitations
1. Requires liquidity and structure reading skill.
2. Includes discretionary decision points.
3. Execution quality depends on trader experience.
4. Lower performance in choppy conditions.

## Final Conclusion
APLM presents a repeatable intraday framework for XAUUSD centered on POC, session liquidity behavior, and smart money context. The manual test set (100+ trades) supports a positive expectancy model with controlled drawdown behavior, making it suitable for disciplined internship-grade research and practical deployment trials.

## Related Project Artifacts
- Strategy implementation references: [python-backtester](../python-backtester)
- Backtest artifacts: [reports/backtest_report.html](../reports/backtest_report.html), [reports/performance_metrics.csv](../reports/performance_metrics.csv)
- Existing research document: [docs/Aryan_Price_Action_Full_Research_Paper_v2.docx](./Aryan_Price_Action_Full_Research_Paper_v2.docx)
