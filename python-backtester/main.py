"""Command-line entry point for running the Aryan Price Action backtest."""

from __future__ import annotations

import argparse
from pathlib import Path
import logging
from typing import Any

import numpy as np
import pandas as pd
from backtesting import Backtest
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import load_config, dump_config
from indicators import build_feature_frame, validate_ohlcv_frame
from risk_management import trade_summary
from strategy import AryanPriceActionStrategy, build_trade_frame


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_DATA_PATH = DATA_DIR / "sample_data.csv"
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "trading_config.json"


def setup_logger(level: str) -> logging.Logger:
    logger = logging.getLogger("aryan_price_action")
    logger.setLevel(level.upper())
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)
    return logger


def load_market_data(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    return validate_ohlcv_frame(frame)


def _trade_direction(trade: pd.Series) -> str:
    size = float(trade.get("Size", 0) or 0)
    if size > 0:
        return "long"
    if size < 0:
        return "short"
    return "unknown"


def build_trade_log(trades: pd.DataFrame, frame: pd.DataFrame) -> pd.DataFrame:
    """Convert raw backtesting.py trades into an audit-friendly trade log."""

    if trades.empty:
        return pd.DataFrame(columns=[
            "trade_id", "direction", "entry_time", "exit_time", "holding_bars", "entry_price",
            "exit_price", "size", "pnl", "return_pct", "mfe", "mae", "result", "entry_month", "exit_month",
        ])

    records: list[dict[str, Any]] = []
    for trade_id, trade in trades.reset_index(drop=True).iterrows():
        entry_bar = int(trade.get("EntryBar", -1) or -1)
        exit_bar = int(trade.get("ExitBar", -1) or -1)
        entry_bar = max(0, min(entry_bar, len(frame) - 1))
        exit_bar = max(entry_bar, min(exit_bar, len(frame) - 1))

        price_slice = frame.iloc[entry_bar : exit_bar + 1]
        direction = _trade_direction(trade)
        entry_price = float(trade.get("EntryPrice", np.nan) or np.nan)
        exit_price = float(trade.get("ExitPrice", np.nan) or np.nan)
        pnl = float(trade.get("PnL", 0) or 0)
        return_pct = float(trade.get("ReturnPct", 0) or 0)
        size = float(trade.get("Size", 0) or 0)

        if price_slice.empty or pd.isna(entry_price):
            mfe = np.nan
            mae = np.nan
        elif direction == "long":
            mfe = (price_slice["high"].max() - entry_price) / entry_price
            mae = (price_slice["low"].min() - entry_price) / entry_price
        elif direction == "short":
            mfe = (entry_price - price_slice["low"].min()) / entry_price
            mae = (entry_price - price_slice["high"].max()) / entry_price
        else:
            mfe = np.nan
            mae = np.nan

        entry_time = frame.index[entry_bar] if len(frame.index) else pd.NaT
        exit_time = frame.index[exit_bar] if len(frame.index) else pd.NaT
        holding_bars = max(exit_bar - entry_bar, 0)
        result = "win" if pnl > 0 else "loss" if pnl < 0 else "flat"

        records.append({
            "trade_id": trade_id,
            "direction": direction,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "holding_bars": holding_bars,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "size": size,
            "pnl": pnl,
            "return_pct": return_pct,
            "mfe": mfe,
            "mae": mae,
            "result": result,
            "entry_month": pd.Timestamp(entry_time).to_period("M").strftime("%Y-%m") if pd.notna(entry_time) else None,
            "exit_month": pd.Timestamp(exit_time).to_period("M").strftime("%Y-%m") if pd.notna(exit_time) else None,
        })

    return pd.DataFrame(records)


def build_monthly_performance(trade_log: pd.DataFrame, equity_curve: pd.DataFrame) -> pd.DataFrame:
    """Aggregate monthly trade statistics for research reporting."""

    if trade_log.empty:
        return pd.DataFrame(columns=["month", "trade_count", "net_pnl", "gross_profit", "gross_loss", "win_rate", "average_return_pct"])

    monthly = trade_log.copy()
    monthly["exit_month"] = monthly["exit_month"].fillna("unknown")
    grouped = monthly.groupby("exit_month", dropna=False)

    monthly_perf = grouped.agg(
        trade_count=("trade_id", "count"),
        net_pnl=("pnl", "sum"),
        gross_profit=("pnl", lambda values: values[values > 0].sum()),
        gross_loss=("pnl", lambda values: values[values < 0].sum()),
        win_rate=("result", lambda values: (values == "win").mean()),
        average_return_pct=("return_pct", "mean"),
        average_holding_bars=("holding_bars", "mean"),
        average_mfe=("mfe", "mean"),
        average_mae=("mae", "mean"),
    ).reset_index().rename(columns={"exit_month": "month"})

    if not equity_curve.empty and "Equity" in equity_curve.columns:
        monthly_perf["equity_end"] = equity_curve["Equity"].reindex(equity_curve.index).iloc[-1]

    return monthly_perf.sort_values("month")


def compute_metrics(stats: pd.Series, trades: pd.DataFrame) -> dict[str, float]:
    equity_curve = stats["Equity Final [$]"] if "Equity Final [$]" in stats else np.nan
    total_return = stats["Return [%]"] / 100 if "Return [%]" in stats else np.nan
    annual_return = stats["CAGR [%]"] / 100 if "CAGR [%]" in stats else np.nan
    max_drawdown = abs(stats["Max. Drawdown [%]"] / 100) if "Max. Drawdown [%]" in stats else np.nan

    returns = trades["PnL"] / trades["EntryPrice"].replace(0, np.nan) if not trades.empty and "EntryPrice" in trades else pd.Series(dtype=float)
    return_std = returns.std(ddof=0) if not returns.empty else 0.0
    sharpe = (returns.mean() / return_std * np.sqrt(252)) if not returns.empty and return_std and not np.isnan(return_std) else 0.0
    downside = returns[returns < 0]
    downside_std = downside.std(ddof=0) if not downside.empty else 0.0
    sortino = (returns.mean() / downside_std * np.sqrt(252)) if not downside.empty and downside_std and not np.isnan(downside_std) else 0.0

    stats_map = {
        "equity_final": float(equity_curve) if pd.notna(equity_curve) else 0.0,
        "total_return": float(total_return) if pd.notna(total_return) else 0.0,
        "cagr": float(annual_return) if pd.notna(annual_return) else 0.0,
        "max_drawdown": float(max_drawdown) if pd.notna(max_drawdown) else 0.0,
        "sharpe": float(sharpe) if pd.notna(sharpe) else 0.0,
        "sortino": float(sortino) if pd.notna(sortino) else 0.0,
    }
    stats_map.update(trade_summary(trades))
    return stats_map


def save_reports(stats: pd.Series, metrics: dict[str, float], trades: pd.DataFrame, frame: pd.DataFrame) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics_frame = pd.DataFrame([metrics])
    metrics_frame.to_csv(REPORTS_DIR / "performance_metrics.csv", index=False)
    frame.to_csv(REPORTS_DIR / "feature_frame.csv")

    equity_curve = pd.DataFrame()
    if hasattr(stats, "_equity_curve"):
        equity_curve = getattr(stats, "_equity_curve")

    trade_log = build_trade_log(trades, frame)
    trade_log.to_csv(REPORTS_DIR / "trade_log.csv", index=False)

    monthly_perf = build_monthly_performance(trade_log, equity_curve)
    monthly_perf.to_csv(REPORTS_DIR / "monthly_performance.csv", index=False)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
    equity = equity_curve["Equity"] if not equity_curve.empty and "Equity" in equity_curve.columns else pd.Series(dtype=float)

    if not equity.empty:
        fig.add_trace(go.Scatter(y=equity.values, mode="lines", name="Equity Curve", line=dict(color="#00d084", width=2)), row=1, col=1)

    fig.add_trace(go.Candlestick(
        x=frame.index,
        open=frame["open"], high=frame["high"], low=frame["low"], close=frame["close"],
        name="Price", increasing_line_color="#00d084", decreasing_line_color="#ff4d4f"
    ), row=2, col=1)

    if not trades.empty and {"EntryBar", "ExitBar"}.issubset(trades.columns):
        entry_idx = trades["EntryBar"].clip(lower=0).astype(int)
        exit_idx = trades["ExitBar"].clip(lower=0).astype(int)
        fig.add_trace(go.Scatter(
            x=frame.index[entry_idx], y=frame["close"].iloc[entry_idx], mode="markers",
            marker=dict(color="#1f77ff", size=8, symbol="triangle-up"), name="Entries"
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=frame.index[exit_idx], y=frame["close"].iloc[exit_idx], mode="markers",
            marker=dict(color="#ffb020", size=8, symbol="triangle-down"), name="Exits"
        ), row=2, col=1)

    fig.update_layout(template="plotly_dark", height=900, title="Aryan Price Action Framework - Backtest Report")
    fig.write_html(REPORTS_DIR / "backtest_report.html", include_plotlyjs="cdn")

    plt.figure(figsize=(12, 4))
    if not equity.empty:
        plt.plot(equity.values, color="#00d084", linewidth=1.8)
    plt.title("Equity Curve")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "equity_curve.png", dpi=160)
    plt.close()

    if not monthly_perf.empty:
        plt.figure(figsize=(12, 4))
        plt.bar(monthly_perf["month"], monthly_perf["net_pnl"], color=np.where(monthly_perf["net_pnl"] >= 0, "#00d084", "#ff5c7a"))
        plt.xticks(rotation=45, ha="right")
        plt.title("Monthly Net PnL")
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "monthly_pnl.png", dpi=160)
        plt.close()


def run_backtest(data_path: Path, config_path: Path) -> dict[str, float]:
    config = load_config(config_path)
    logger = setup_logger(config.strategy.log_level)
    logger.info("Loading market data from %s", data_path)

    market_data = load_market_data(data_path)
    features = build_feature_frame(market_data, config)
    trade_frame = build_trade_frame(features, config)

    bt_data = trade_frame.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    }).copy()

    bt = Backtest(
        bt_data,
        AryanPriceActionStrategy,
        cash=config.strategy.capital,
        commission=0.0004,
        trade_on_close=True,
        exclusive_orders=True,
    )
    stats = bt.run()

    raw_trades = stats._trades.copy() if hasattr(stats, "_trades") else pd.DataFrame()
    metrics = compute_metrics(stats, raw_trades)
    save_reports(stats, metrics, raw_trades, trade_frame)
    dump_config(config, REPORTS_DIR / "run_config_snapshot.json")

    logger.info("Backtest completed. Total trades: %s", metrics.get("total_trades", 0))
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Aryan Price Action research backtest.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="Path to the OHLCV CSV file.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to the JSON config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics = run_backtest(args.data, args.config)
    print(pd.Series(metrics).to_string())


if __name__ == "__main__":
    main()
