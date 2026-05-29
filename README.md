# Aryan Price Action Framework

[![Pine Script](https://img.shields.io/badge/Pine%20Script-v5-blue)](https://www.tradingview.com/pine-script-docs/en/v5/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org/)
[![Backtesting.py](https://img.shields.io/badge/Backtesting.py-quant%20research-111827)](https://kernc.github.io/backtesting.py/)
[![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B)](https://streamlit.io/)
[![GitHub repo](https://img.shields.io/badge/GitHub-portfolio%20ready-24292F)](https://github.com/Aryan1438/Quant_indicator_2CentCaps)

Institutional-style Smart Money Concepts research workspace for quant internship presentation. The project is structured like a real quant research deliverable: a Pine Script strategy, a Python backtesting engine, a Streamlit dashboard, and research documentation packaged for a GitHub portfolio.

## Overview

This repository is designed to demonstrate a complete research workflow:

- chart-side signal generation in TradingView
- feature engineering and backtesting in Python
- performance analysis and monthly reporting
- portfolio-ready documentation and dashboard presentation

## Architecture

- Pine Script strategy for BOS, CHoCH, CHoCH+, liquidity sweeps, fair value gaps, premium/discount zones, and multi-timeframe structure.
- Python backtester based on `backtesting.py` with engineered market-structure features in pandas and numpy.
- Streamlit dashboard for performance analytics, monthly returns, and trade review.
- Research notes, strategy documentation, and internship reporting assets.

## Project Structure

- `pine-script/aryan_price_action.pine`
- `python-backtester/main.py`
- `python-backtester/strategy.py`
- `python-backtester/indicators.py`
- `python-backtester/config.py`
- `python-backtester/risk_management.py`
- `dashboard/streamlit_dashboard.py`
- `data/sample_data.csv`
- `reports/backtest_report.html`
- `reports/performance_metrics.csv`
- `reports/monthly_performance.csv`
- `reports/trade_log.csv`
- `docs/research_notes.md`
- `docs/strategy_documentation.md`
- `docs/internship_report.md`

## Research Output

The Python pipeline exports a research pack that can be reviewed independently of the code:

- `reports/performance_metrics.csv` for headline statistics
- `reports/trade_log.csv` for trade-level audit data
- `reports/monthly_performance.csv` for month-by-month analysis
- `reports/backtest_report.html` for a shareable visual summary
- `reports/equity_curve.png` and `reports/monthly_pnl.png` for presentation slides

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Python backtest:
   ```bash
   python python-backtester/main.py
   ```
4. Launch the dashboard:
   ```bash
   streamlit run dashboard/streamlit_dashboard.py
   ```
5. Open the Pine Script file in TradingView, copy the strategy into the Pine editor, and apply it to a chart.

## Research Workflow

1. Export TradingView OHLCV data into `data/sample_data.csv` or replace it with your own dataset.
2. Run the Python backtester to generate trade logs and performance metrics.
3. Review `reports/backtest_report.html`, `reports/performance_metrics.csv`, and the Streamlit dashboard.
4. Use the monthly performance export to evaluate regime consistency and drawdown behavior.
5. Update the docs with research conclusions, limitations, and next steps.

## Quant Methodology

The strategy uses a confluence model:

- BOS / CHoCH structure confirmation
- Institutional order-block confirmation
- Liquidity sweep confirmation
- Higher-timeframe alignment
- Optional fair value gap confirmation

Risk is controlled using fixed fractional sizing, ATR-based stops, reward-to-risk targeting, and trailing exits.

## Screenshots

Add finished images in the `screenshots/` folder for a polished portfolio presentation. Recommended files:

- `screenshots/dashboard-overview.png`
- `screenshots/equity-curve.png`
- `screenshots/monthly-performance.png`
- `screenshots/pine-strategy-overlay.png`

These screenshots should highlight the dashboard, the equity curve, the monthly performance view, and the TradingView chart overlay.

## Notes

- The included sample data is synthetic and meant only for testing the pipeline.
- The generated report files in `reports/` are overwritten by the backtest run.
- The Pine strategy is written to be readable, modular, and suitable for further research refinement.
- The project is intentionally structured to be easy to present in an internship or portfolio review.
