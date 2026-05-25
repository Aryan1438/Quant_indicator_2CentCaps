"""Configuration helpers for the Aryan Price Action Framework backtester."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
import json


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "trading_config.json"


@dataclass(slots=True)
class StrategySettings:
    symbol: str = "BTCUSDT"
    timeframe: str = "1H"
    higher_timeframes: list[str] = field(default_factory=lambda: ["4H", "1D"])
    capital: float = 100_000.0
    risk_per_trade: float = 0.01
    reward_risk: float = 2.5
    atr_period: int = 14
    swing_window: int = 3
    structure_window: int = 5
    ob_lookback: int = 12
    require_fvg_confirmation: bool = True
    use_dynamic_rr: bool = True
    allow_long: bool = True
    allow_short: bool = True
    max_open_trades: int = 1
    trailing_stop_atr: float = 1.5
    liquidity_sweep_buffer_atr: float = 0.15
    mtf_alignment_required: bool = True
    log_level: str = "INFO"


@dataclass(slots=True)
class ProjectPaths:
    root_dir: Path = ROOT_DIR
    data_dir: Path = ROOT_DIR / "data"
    reports_dir: Path = ROOT_DIR / "reports"
    docs_dir: Path = ROOT_DIR / "docs"
    pine_dir: Path = ROOT_DIR / "pine-script"


@dataclass(slots=True)
class AppConfig:
    strategy: StrategySettings = field(default_factory=StrategySettings)
    paths: ProjectPaths = field(default_factory=ProjectPaths)


def load_json_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load JSON overrides from disk if the file exists."""

    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def merge_config(overrides: dict[str, Any] | None = None) -> AppConfig:
    """Merge JSON overrides into the default application config."""

    config = AppConfig()
    overrides = overrides or {}
    strategy_overrides = overrides.get("strategy", overrides)

    for field_name, field_value in strategy_overrides.items():
        if hasattr(config.strategy, field_name):
            setattr(config.strategy, field_name, field_value)

    return config


def load_config(config_path: str | Path | None = None) -> AppConfig:
    """Load the default config and apply JSON overrides if present."""

    return merge_config(load_json_config(config_path))


def dump_config(config: AppConfig, output_path: str | Path) -> None:
    """Persist a configuration snapshot as JSON for reproducible research runs."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "strategy": asdict(config.strategy),
        "paths": {
            "root_dir": str(config.paths.root_dir),
            "data_dir": str(config.paths.data_dir),
            "reports_dir": str(config.paths.reports_dir),
            "docs_dir": str(config.paths.docs_dir),
            "pine_dir": str(config.paths.pine_dir),
        },
    }
    with output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
