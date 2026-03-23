"""
.claude/skills/chart_builder.py

Pre-built skill: generate risk charts and dashboards from a DataFrame.
Claude Code calls this — no matplotlib knowledge needed.

Usage:
    import sys; sys.path.insert(0, ".claude/skills")
    import chart_builder
    chart_builder.risk_chart(df, "outputs/risk_chart.png")
    chart_builder.dashboard(df, "outputs/dashboard.png")
"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os

_DARK  = '#0d0d14'
_PANEL = '#13131c'
_GRID  = '#222230'
_TEXT  = '#cccccc'
_MUT   = '#888888'

PANEL_CONFIG = {
    "DRCCLACBS":      ("Delinquency rate",  "#e05a5a", "up_bad"),
    "UNRATE":         ("Unemployment",      "#5b9bd5", "up_bad"),
    "FEDFUNDS":       ("Fed funds rate",    "#9b7fd4", "neutral"),
    "T10Y2Y":         ("Yield curve",       "#f0a500", "watch"),
    "CPIAUCSL":       ("CPI inflation",     "#e07a30", "neutral"),
    "DPSACBW027SBOG": ("Savings rate",      "#4caf7d", "down_bad"),
    "MORTGAGE30US":   ("Mortgage rate",     "#e08080", "up_bad"),
    "BAMLH0A0HYM2":   ("Credit spread",     "#d4a0f0", "up_bad"),
}

def _rag(series: pd.Series, direction: str) -> str:
    d = series.iloc[-1] - series.iloc[-4]
    if direction == "up_bad":   return "RED" if d > 0.12 else ("AMBER" if d > 0 else "GREEN")
    if direction == "down_bad": return "RED" if d < -0.12 else ("AMBER" if d < 0 else "GREEN")
    return "AMBER" if abs(d) > 0.3 else "GREEN"

def _ax_style(ax):
    ax.set_facecolor(_PANEL)
    ax.tick_params(colors=_MUT, labelsize=8)
    for s in ax.spines.values(): s.set_color(_GRID)

def risk_chart(df: pd.DataFrame, path: str = "outputs/risk_chart.png",
               primary: str = "DRCCLACBS", secondary: list = None):
    """Two-panel chart: primary signal on top, 1–2 supporting indicators below."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    secondary = secondary or ["UNRATE", "T10Y2Y"]
    cfg = PANEL_CONFIG.get(primary, (primary, "#e05a5a", "up_bad"))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    fig.patch.set_facecolor(_DARK)
    _ax_style(ax1); _ax_style(ax2)

    col = cfg[1]
    ax1.plot(df.index, df[primary], color=col, lw=2.5, label=cfg[0])
    ax1.fill_between(df.index, df[primary], alpha=0.12, color=col)
    mean_val = df[primary].mean()
    ax1.axhline(mean_val * 1.15, color=col, ls="--", alpha=0.35, lw=1)
    ax1.text(df.index[-1], mean_val * 1.16, "  alert level", color=col, fontsize=8, alpha=0.7)
    ax1.set_ylabel(cfg[0], color=_MUT, fontsize=9)
    ax1.legend(facecolor='#1a1a26', edgecolor=_GRID, labelcolor=_TEXT, fontsize=8)
    ax1.set_title("Fintech credit risk — macro monitor", color="#eeeeee", fontsize=12, pad=10)

    colors2 = ["#5b9bd5", "#f0a500", "#4caf7d"]
    for i, s in enumerate(secondary):
        if s in df.columns:
            scfg = PANEL_CONFIG.get(s, (s, colors2[i % 3], "neutral"))
            ax2.plot(df.index, df[s], color=scfg[1], lw=2.0,
                     label=scfg[0], linestyle="--" if i > 0 else "-")
    ax2.axhline(0, color=_GRID, ls=":", lw=1)
    ax2.set_ylabel("Rate (%)", color=_MUT, fontsize=9)
    ax2.legend(facecolor='#1a1a26', edgecolor=_GRID, labelcolor=_TEXT, fontsize=8)
    ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b '%y"))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha='right')

    plt.tight_layout(pad=1.8)
    plt.savefig(path, dpi=150, facecolor=_DARK, bbox_inches='tight')
    plt.close()
    print(f"Risk chart saved → {path}")

def dashboard(df: pd.DataFrame, path: str = "outputs/dashboard.png"):
    """6-panel normalized dashboard with RAG status per indicator."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    cols = [c for c in df.columns if c in PANEL_CONFIG][:6]

    fig = plt.figure(figsize=(14, 7))
    fig.patch.set_facecolor(_DARK)
    fig.suptitle("Macro risk dashboard — indicators normalised (z-score)",
                 color="#eeeeee", fontsize=12, y=0.99)
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.32)

    RAG_C = {"RED": "#e05a5a", "AMBER": "#f0a500", "GREEN": "#4caf7d"}

    for i, col in enumerate(cols):
        label, color, direction = PANEL_CONFIG[col]
        ax = fig.add_subplot(gs[i // 3, i % 3])
        _ax_style(ax)
        ax.tick_params(colors='#555', labelsize=7)

        z = (df[col] - df[col].mean()) / df[col].std()
        ax.plot(df.index, z, color=color, lw=1.8)
        ax.fill_between(df.index, z, alpha=0.1, color=color)
        ax.axhline(0, color="#33334a", lw=0.7, ls="--")

        rag = _rag(df[col], direction)
        ax.set_title(f"{label}  {df[col].iloc[-1]:.2f}",
                     color=_TEXT, fontsize=9, loc="left", pad=5)
        ax.text(0.97, 1.04, rag, transform=ax.transAxes,
                fontsize=8, color=RAG_C[rag], ha="right", va="bottom", fontweight="bold")
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("'%y"))

    plt.savefig(path, dpi=150, facecolor=_DARK, bbox_inches='tight')
    plt.close()
    print(f"Dashboard saved → {path}")

def scorecard(df: pd.DataFrame) -> list:
    """Return a list of dicts with RAG scoring for each column."""
    rows = []
    for col in df.columns:
        if col not in PANEL_CONFIG: continue
        label, _, direction = PANEL_CONFIG[col]
        latest = df[col].iloc[-1]
        delta  = latest - df[col].iloc[-4]
        rag    = _rag(df[col], direction)
        rows.append({"indicator": label, "series": col,
                     "current": round(latest, 2), "delta_3m": round(delta, 2),
                     "rag": rag})
    return rows
