"""
demo/run_pipeline.py

Full pipeline demo : FRED → Charts → PDF → Gmail
Run this for the Anthropic panel demo.

Usage:
    FRED_API_KEY=your_key python demo/run_pipeline.py
    FRED_API_KEY=your_key python demo/run_pipeline.py --mock   # no real API call
"""
import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "fred-fetcher"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "charts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "pdf-report"))

import pandas as pd
import numpy as np

os.makedirs("outputs", exist_ok=True)

def mock_data():
    """Synthetic data for demo without API key."""
    idx = pd.date_range("2021-01-01", periods=36, freq="MS")
    np.random.seed(42)
    return pd.DataFrame({
        "DRCCLACBS":      np.linspace(1.5, 2.9, 36) + np.random.normal(0, 0.1, 36),
        "UNRATE":         np.linspace(6.4, 4.1, 36) + np.random.normal(0, 0.15, 36),
        "FEDFUNDS":       np.linspace(0.07, 5.3, 36),
        "T10Y2Y":         np.linspace(1.5, -0.6, 36) + np.random.normal(0, 0.2, 36),
        "CPIAUCSL":       np.linspace(1.7, 3.2, 36) + np.random.normal(0, 0.3, 36),
        "DPSACBW027SBOG": np.linspace(8.0, 3.5, 36),
        "MORTGAGE30US":   np.linspace(2.7, 7.1, 36),
        "BAMLH0A0HYM2":   np.linspace(3.2, 4.8, 36) + np.random.normal(0, 0.3, 36),
    }, index=idx)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Use synthetic data (no API key needed)")
    parser.add_argument("--email", default=None, help="Send report to this email address")
    args = parser.parse_args()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  macro-report-toolkit — full pipeline")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # ── Step 1 : Data ──────────────────────────────────────────
    print("STEP 1 — Fetching macro data")
    if args.mock:
        print("  (mock mode — synthetic data)")
        df = mock_data()
        print(f"  ✓ {len(df)} rows × {len(df.columns)} indicators")
    else:
        from fred_fetcher import fetch_dashboard_data
        df = fetch_dashboard_data(start="2021-01-01")

    # ── Step 2 : Charts ────────────────────────────────────────
    print("\nSTEP 2 — Generating charts")
    import chart_builder
    chart_builder.dashboard(df, "outputs/dashboard.png")
    chart_builder.risk_chart(df, "outputs/risk_chart.png",
                              primary="DRCCLACBS",
                              secondary=["UNRATE", "T10Y2Y"])
    rows = chart_builder.scorecard(df)

    print("\n  Scorecard:")
    for r in rows:
        bar = {"RED": "🔴", "AMBER": "🟡", "GREEN": "🟢"}.get(r["rag"], "⚪")
        print(f"    {bar} {r['indicator']:25} {r['current']:6.2f}  Δ3m={r['delta_3m']:+.2f}")

    # ── Step 3 : PDF ───────────────────────────────────────────
    print("\nSTEP 3 — Building PDF report")
    from pdf_report import generate_report
    generate_report(
        scorecard_rows=rows,
        charts={
            "dashboard": "outputs/dashboard.png",
            "focus":     "outputs/risk_chart.png",
        },
        output_path="outputs/macro_report.pdf",
        title="Macro Risk Report",
        subtitle=f"Monthly update — {pd.Timestamp.today().strftime('%B %Y')}",
        author="macro-report-toolkit",
    )

    # ── Step 4 : Email ─────────────────────────────────────────
    print("\nSTEP 4 — Email delivery")
    if args.email:
        print(f"  → Send outputs/macro_report.pdf to {args.email}")
        print("  (In Claude Code : Gmail MCP handles this automatically)")
    else:
        print("  Skipped — pass --email your@address.com to send")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Pipeline complete!")
    print("  outputs/dashboard.png")
    print("  outputs/risk_chart.png")
    print("  outputs/macro_report.pdf")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

if __name__ == "__main__":
    main()
