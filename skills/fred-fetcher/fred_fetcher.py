"""
skills/fred-fetcher/fred_fetcher.py

Fetch macro indicators from the FRED API (St. Louis Fed) and return
a clean pandas DataFrame ready for chart_builder.

Usage:
    import sys; sys.path.insert(0, ".claude/skills")
    import fred_fetcher
    df = fred_fetcher.fetch(api_key="YOUR_KEY")
    df = fred_fetcher.fetch(api_key="YOUR_KEY", series=["UNRATE", "FEDFUNDS"], years=3)
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta

DEFAULT_SERIES = [
    "DRCCLACBS",
    "UNRATE",
    "FEDFUNDS",
    "T10Y2Y",
    "CPIAUCSL",
    "DPSACBW027SBOG",
    "MORTGAGE30US",
    "BAMLH0A0HYM2",
]

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def fetch(api_key: str = None, series: list = None, years: int = 5, freq: str = "m") -> pd.DataFrame:
    """
    Fetch FRED series and return a merged DataFrame.

    Parameters
    ----------
    api_key : str       FRED API key. Falls back to FRED_API_KEY env variable.
    series  : list      FRED series IDs. Defaults to DEFAULT_SERIES (8 macro indicators).
    years   : int       Years of history (default 5).
    freq    : str       'm' monthly | 'q' quarterly | 'a' annual

    Returns
    -------
    pd.DataFrame  DatetimeIndex (Month Start), one column per series. Forward-filled.
    """
    api_key = api_key or os.environ.get("FRED_API_KEY")
    if not api_key:
        raise ValueError(
            "FRED API key required. Pass api_key= or set FRED_API_KEY env variable.\n"
            "Free key: https://fred.stlouisfed.org/docs/api/api_key.html"
        )

    series = series or DEFAULT_SERIES
    start_date = (datetime.today() - timedelta(days=365 * years)).strftime("%Y-%m-%d")
    frames, errors = {}, []

    for sid in series:
        try:
            resp = requests.get(FRED_BASE, params={
                "series_id": sid, "api_key": api_key, "file_type": "json",
                "observation_start": start_date, "frequency": freq,
                "aggregation_method": "avg",
            }, timeout=10)
            resp.raise_for_status()
            data = resp.json().get("observations", [])
            if not data:
                errors.append(f"{sid}: no data"); continue

            s = (pd.DataFrame(data)[["date", "value"]]
                 .replace(".", float("nan"))
                 .assign(date=lambda d: pd.to_datetime(d["date"]),
                         value=lambda d: pd.to_numeric(d["value"], errors="coerce"))
                 .set_index("date")["value"].rename(sid))
            frames[sid] = s
            print(f"  ✓ {sid:30} {len(s):4d} obs")

        except requests.RequestException as e:
            errors.append(f"{sid}: {e}")
            print(f"  ✗ {sid:30} failed — {e}")

    if not frames:
        raise RuntimeError(f"No data fetched. Errors: {errors}")

    df = pd.concat(frames.values(), axis=1)
    df.index = pd.to_datetime(df.index).to_period("M").to_timestamp("MS")
    df = df.ffill().bfill()

    print(f"\nDataFrame: {len(df)} rows × {len(df.columns)} cols "
          f"| {df.index[0].date()} → {df.index[-1].date()}")
    if errors:
        print(f"Warnings: {errors}")
    return df


def fetch_single(series_id: str, api_key: str = None, years: int = 5) -> pd.Series:
    """Fetch a single FRED series as pd.Series."""
    return fetch(api_key=api_key, series=[series_id], years=years)[series_id]


def describe(df: pd.DataFrame) -> None:
    """Print a quick summary table of a fetched DataFrame."""
    print(f"\n{'Series':<30} {'Latest':>8} {'Min':>8} {'Max':>8} {'NaN%':>6}")
    print("-" * 65)
    for col in df.columns:
        s = df[col].dropna()
        print(f"{col:<30} {s.iloc[-1]:>8.2f} {s.min():>8.2f} {s.max():>8.2f} "
              f"{100 * df[col].isna().mean():>5.1f}%")
