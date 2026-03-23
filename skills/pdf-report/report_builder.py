"""
skills/pdf-report/report_builder.py

Generate a professional macro risk report PDF from chart images + scorecard data.
Uses WeasyPrint (HTML → PDF) for reliable layout and styling.

Usage:
    import sys; sys.path.insert(0, ".claude/skills")
    import report_builder
    report_builder.generate(
        scorecard_rows=rows,
        charts=["outputs/dashboard.png", "outputs/risk_chart.png"],
        output_path="outputs/macro_report.pdf",
        title="Macro Risk Monitor — March 2026",
    )
"""

import os
import base64
from datetime import datetime

try:
    from weasyprint import HTML
    WEASYPRINT_OK = True
except ImportError:
    WEASYPRINT_OK = False


RAG_COLORS = {
    "RED":   ("#fde8e8", "#c0392b", "▲"),
    "AMBER": ("#fef9e7", "#d68910", "◆"),
    "GREEN": ("#e9f7ef", "#1e8449", "●"),
}


def _img_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _scorecard_html(rows: list) -> str:
    if not rows:
        return ""
    html = """
    <table class="scorecard">
      <thead>
        <tr>
          <th>Indicator</th>
          <th>Series</th>
          <th class="num">Current</th>
          <th class="num">Δ 3M</th>
          <th class="center">Status</th>
        </tr>
      </thead>
      <tbody>
    """
    for r in rows:
        rag = r.get("rag", "GREEN")
        bg, fg, icon = RAG_COLORS.get(rag, RAG_COLORS["GREEN"])
        delta = r.get("delta_3m", 0)
        delta_str = f"+{delta:.2f}" if delta >= 0 else f"{delta:.2f}"
        html += f"""
        <tr>
          <td>{r.get('indicator', '')}</td>
          <td class="mono">{r.get('series', '')}</td>
          <td class="num">{r.get('current', ''):.2f}</td>
          <td class="num {'up' if delta > 0 else 'down'}">{delta_str}</td>
          <td class="center">
            <span class="badge" style="background:{bg};color:{fg}">
              {icon} {rag}
            </span>
          </td>
        </tr>"""
    html += "</tbody></table>"
    return html


def _build_html(title: str, subtitle: str, scorecard_rows: list,
                charts: list, footer_note: str) -> str:

    charts_html = ""
    for path in charts:
        if os.path.exists(path):
            b64 = _img_to_b64(path)
            label = os.path.basename(path).replace("_", " ").replace(".png", "").title()
            charts_html += f"""
            <div class="chart-block">
              <p class="chart-label">{label}</p>
              <img src="data:image/png;base64,{b64}" class="chart-img"/>
            </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<style>
  @page {{
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-center {{
      content: "Page " counter(page) " of " counter(pages);
      font-size: 9px;
      color: #888;
    }}
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 11px;
    color: #1a1a2e;
    background: #fff;
    line-height: 1.5;
  }}

  /* Header */
  .report-header {{
    border-bottom: 3px solid #1a1a2e;
    padding-bottom: 10px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}
  .report-title {{ font-size: 20px; font-weight: 700; color: #0d0d14; }}
  .report-subtitle {{ font-size: 11px; color: #555; margin-top: 3px; }}
  .report-meta {{ text-align: right; font-size: 9px; color: #888; }}

  /* Section titles */
  h2 {{
    font-size: 12px;
    font-weight: 700;
    color: #0d0d14;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 20px 0 10px;
    padding-bottom: 4px;
    border-bottom: 1px solid #e0e0e0;
  }}

  /* Scorecard table */
  .scorecard {{
    width: 100%;
    border-collapse: collapse;
    font-size: 10px;
    margin-bottom: 16px;
  }}
  .scorecard thead tr {{
    background: #0d0d14;
    color: #fff;
  }}
  .scorecard th {{
    padding: 7px 10px;
    text-align: left;
    font-weight: 600;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }}
  .scorecard td {{
    padding: 6px 10px;
    border-bottom: 1px solid #f0f0f0;
  }}
  .scorecard tbody tr:nth-child(even) {{ background: #fafafa; }}
  .scorecard .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .scorecard .center {{ text-align: center; }}
  .scorecard .mono {{ font-family: "Courier New", monospace; font-size: 9px; color: #555; }}
  .scorecard .up {{ color: #c0392b; }}
  .scorecard .down {{ color: #1e8449; }}

  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 9px;
    font-weight: 700;
  }}

  /* Charts */
  .chart-block {{ margin-bottom: 20px; }}
  .chart-label {{
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #888;
    margin-bottom: 5px;
  }}
  .chart-img {{
    width: 100%;
    border-radius: 6px;
  }}

  /* Footer note */
  .footer-note {{
    margin-top: 24px;
    padding-top: 10px;
    border-top: 1px solid #e0e0e0;
    font-size: 8.5px;
    color: #999;
    line-height: 1.6;
  }}
</style>
</head>
<body>

<div class="report-header">
  <div>
    <div class="report-title">{title}</div>
    <div class="report-subtitle">{subtitle}</div>
  </div>
  <div class="report-meta">
    Generated {datetime.today().strftime("%d %B %Y")}<br/>
    Source: Federal Reserve Bank of St. Louis (FRED)
  </div>
</div>

<h2>Indicator Scorecard</h2>
{_scorecard_html(scorecard_rows)}

<h2>Visualisations</h2>
{charts_html}

<div class="footer-note">
  {footer_note}
</div>

</body>
</html>"""


def generate(
    scorecard_rows: list,
    charts: list,
    output_path: str = "outputs/macro_report.pdf",
    title: str = "Macro Risk Monitor",
    subtitle: str = "Key indicators — Federal Reserve FRED data",
    footer_note: str = (
        "Data sourced from the Federal Reserve Bank of St. Louis (FRED API). "
        "All indicators are shown for informational purposes only. "
        "RAG status based on 3-month delta thresholds. Not investment advice."
    ),
) -> str:
    """
    Generate a PDF macro risk report.

    Parameters
    ----------
    scorecard_rows : list   Output of chart_builder.scorecard(df)
    charts         : list   Paths to PNG chart files (dashboard first, then risk charts)
    output_path    : str    Destination PDF path
    title          : str    Report title (appears in header)
    subtitle       : str    Subtitle line under the title
    footer_note    : str    Disclaimer / footnote at bottom of report

    Returns
    -------
    str   Absolute path to the generated PDF
    """
    if not WEASYPRINT_OK:
        raise ImportError("WeasyPrint not installed. Run: pip install weasyprint")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    html = _build_html(
        title=title,
        subtitle=subtitle,
        scorecard_rows=scorecard_rows,
        charts=charts,
        footer_note=footer_note,
    )

    HTML(string=html).write_pdf(output_path)
    abs_path = os.path.abspath(output_path)
    print(f"Report saved → {abs_path}")
    return abs_path
