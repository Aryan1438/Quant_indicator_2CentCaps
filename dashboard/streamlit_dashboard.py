"""Institutional Streamlit dashboard for the Aryan Price Action Framework."""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"
DATA_DIR = PROJECT_ROOT / "data"


st.set_page_config(
    page_title="Aryan Price Action Framework",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        :root {
            --bg: #07111f;
            --panel: #0e1726;
            --panel-2: #111b2e;
            --text: #e5eef8;
            --muted: #8ea4c1;
            --accent: #00d084;
            --accent-2: #2b7fff;
            --danger: #ff5c7a;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(43,127,255,0.16), transparent 30%),
                radial-gradient(circle at top right, rgba(0,208,132,0.10), transparent 25%),
                linear-gradient(180deg, #07111f 0%, #091423 100%);
            color: var(--text);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #08101b 0%, #0d1727 100%);
            border-right: 1px solid rgba(255,255,255,0.06);
        }
        .metric-card {
            background: rgba(14, 23, 38, 0.92);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 18px 18px 12px 18px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.18);
        }
        .section-card {
            background: rgba(14, 23, 38, 0.75);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 18px;
            margin-bottom: 16px;
        }
        .title {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.15rem;
        }
        .subtitle {
            color: var(--muted);
            margin-bottom: 1rem;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            color: #cfe7ff;
            background: rgba(43,127,255,0.12);
            border: 1px solid rgba(43,127,255,0.22);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_frame(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


metrics = load_frame(REPORTS_DIR / "performance_metrics.csv")
trades = load_frame(REPORTS_DIR / "trade_log.csv")
feature_frame = load_frame(REPORTS_DIR / "feature_frame.csv")
monthly_perf = load_frame(REPORTS_DIR / "monthly_performance.csv")

st.sidebar.markdown("## Strategy Console")
st.sidebar.markdown("<span class='badge'>Institutional research dashboard</span>", unsafe_allow_html=True)
selected_symbol = st.sidebar.selectbox("Symbol", ["BTCUSDT", "ETHUSDT", "EURUSD", "NAS100"], index=0)
selected_timeframe = st.sidebar.selectbox("Timeframe", ["15m", "1H", "4H", "1D"], index=1)
risk_per_trade = st.sidebar.slider("Risk per trade", 0.25, 3.0, 1.0, 0.25)
reward_risk = st.sidebar.slider("Reward / Risk", 1.0, 5.0, 2.5, 0.1)
require_fvg = st.sidebar.toggle("Require FVG confirmation", value=True)
show_trades = st.sidebar.toggle("Show trade history", value=True)

st.markdown("<div class='title'>Aryan Price Action Framework</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Quant research dashboard for Smart Money Concepts, liquidity, and institutional execution research.</div>", unsafe_allow_html=True)

if metrics.empty:
    c1, c2, c3, c4 = st.columns(4)
    for column, label, value in [
        (c1, "Total Trades", "0"),
        (c2, "Win Rate", "0.0%"),
        (c3, "Profit Factor", "0.00"),
        (c4, "Max Drawdown", "0.0%"),
    ]:
        column.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>{label}</div><div style='font-size:1.7rem;font-weight:700'>{value}</div></div>", unsafe_allow_html=True)
else:
    row = metrics.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>Total Trades</div><div style='font-size:1.7rem;font-weight:700'>{int(row.get('total_trades', 0))}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>Win Rate</div><div style='font-size:1.7rem;font-weight:700'>{row.get('win_rate', 0):.1%}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>Profit Factor</div><div style='font-size:1.7rem;font-weight:700'>{row.get('profit_factor', 0):.2f}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>Max Drawdown</div><div style='font-size:1.7rem;font-weight:700'>{row.get('max_drawdown', 0):.1%}</div></div>", unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)
if not metrics.empty:
    c5.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>Sharpe</div><div style='font-size:1.4rem;font-weight:700'>{metrics.iloc[0].get('sharpe', 0):.2f}</div></div>", unsafe_allow_html=True)
    c6.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>Sortino</div><div style='font-size:1.4rem;font-weight:700'>{metrics.iloc[0].get('sortino', 0):.2f}</div></div>", unsafe_allow_html=True)
    c7.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>CAGR</div><div style='font-size:1.4rem;font-weight:700'>{metrics.iloc[0].get('cagr', 0):.1%}</div></div>", unsafe_allow_html=True)
    c8.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>Average RR</div><div style='font-size:1.4rem;font-weight:700'>{metrics.iloc[0].get('average_rr', 0):.2f}</div></div>", unsafe_allow_html=True)
else:
    for column, label, value in [
        (c5, "Sharpe", "0.00"),
        (c6, "Sortino", "0.00"),
        (c7, "CAGR", "0.0%"),
        (c8, "Average RR", "0.00"),
    ]:
        column.markdown(f"<div class='metric-card'><div style='color:#8ea4c1'>{label}</div><div style='font-size:1.4rem;font-weight:700'>{value}</div></div>", unsafe_allow_html=True)

left, right = st.columns([1.6, 1])

with left:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Equity Curve")
    if not trades.empty and {"PnL", "EntryBar"}.issubset(trades.columns):
        trades["equity"] = trades["PnL"].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=trades["equity"], mode="lines", line=dict(color="#00d084", width=2), name="Equity"))
        fig.update_layout(template="plotly_dark", height=360, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run the backtester first to populate the equity curve.")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Research Inputs")
    st.write(f"Symbol: **{selected_symbol}**")
    st.write(f"Timeframe: **{selected_timeframe}**")
    st.write(f"Risk / Trade: **{risk_per_trade:.2f}%**")
    st.write(f"Reward / Risk: **{reward_risk:.2f}R**")
    st.write(f"FVG Confirmation: **{'Required' if require_fvg else 'Optional'}**")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Monthly Performance Heatmap")
if not feature_frame.empty and "index" in feature_frame.columns:
    feature_frame["index"] = pd.to_datetime(feature_frame["index"], errors="coerce")
    feature_frame = feature_frame.dropna(subset=["index"])
    if "close" in feature_frame.columns:
        monthly = feature_frame.set_index("index")["close"].resample("M").last().pct_change().fillna(0)
        heatmap = monthly.to_frame(name="return")
        heatmap["year"] = heatmap.index.year
        heatmap["month"] = heatmap.index.month_name().str[:3]
        pivot = heatmap.pivot(index="year", columns="month", values="return").fillna(0)
        fig = px.imshow(pivot, color_continuous_scale="RdYlGn", aspect="auto", text_auto=True)
        fig.update_layout(template="plotly_dark", height=360, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Monthly heatmap will appear after the backtest generates feature_frame.csv.")
st.markdown("</div>", unsafe_allow_html=True)

if show_trades:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Trade History")
    if not trades.empty:
        display_cols = [col for col in ["EntryTime", "ExitTime", "Size", "PnL", "ReturnPct", "EntryPrice", "ExitPrice"] if col in trades.columns]
        st.dataframe(trades[display_cols] if display_cols else trades, use_container_width=True, height=320)
    else:
        st.info("No trade history available yet.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Monthly Performance")
if not monthly_perf.empty:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_perf["month"],
        y=monthly_perf["net_pnl"],
        marker_color=["#00d084" if value >= 0 else "#ff5c7a" for value in monthly_perf["net_pnl"]],
        name="Net PnL",
    ))
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(monthly_perf, use_container_width=True, height=260)
else:
    st.info("Monthly performance will appear after the backtester exports monthly_performance.csv.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.subheader("Market Data Preview")
if (DATA_DIR / "sample_data.csv").exists():
    data = pd.read_csv(DATA_DIR / "sample_data.csv")
    st.dataframe(data.head(12), use_container_width=True)
else:
    st.info("Sample data not found.")
st.markdown("</div>", unsafe_allow_html=True)
