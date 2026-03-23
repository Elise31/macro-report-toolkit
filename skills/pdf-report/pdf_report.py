"""
.claude/skills/pdf_report.py

Generate a professional macro PDF report from FRED data + charts.
Requires: pip install weasyprint jinja2
"""
import os
import base64
from datetime import datetime

STYLES = """
:root {
    --bg: #ffffff;
    --dark: #0d0d14;
    --accent: #1a1a2e;
    --text: #1a1a2e;
    --muted: #666680;
    --border: #e0e0ec;
    --red: #e05a5a;
    --amber: #f0a500;
    --green: #4caf7d;
    --red-bg: #fdf0f0;
    --amber-bg: #fdf8e6;
    --green-bg: #f0faf4;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Helvetica Neue', Arial, sans-serif; color: var(--text);
       font-size: 10pt; line-height: 1.5; background: white; }

/* ── Cover page ── */
.cover { page-break-after: always; height: 100vh; display: flex;
         flex-direction: column; justify-content: center;
         padding: 60px; background: var(--accent); color: white; }
.cover h1 { font-size: 28pt; font-weight: 300; letter-spacing: -0.5px; margin-bottom: 12px; }
.cover .subtitle { font-size: 13pt; opacity: 0.7; margin-bottom: 40px; }
.cover .meta { font-size: 9pt; opacity: 0.5; border-top: 1px solid rgba(255,255,255,0.2);
               padding-top: 20px; }
.cover .logo { position: absolute; top: 40px; right: 60px;
               max-height: 48px; opacity: 0.9; }

/* ── Section headers ── */
h2 { font-size: 13pt; font-weight: 600; color: var(--accent);
     border-bottom: 2px solid var(--accent); padding-bottom: 6px;
     margin: 28px 0 16px; }
h3 { font-size: 10pt; font-weight: 600; color: var(--muted);
     text-transform: uppercase; letter-spacing: 0.5px; margin: 20px 0 10px; }

/* ── Page layout ── */
@page { size: A4; margin: 20mm 18mm 20mm 18mm; }
.page { padding: 0; }

/* ── Scorecard table ── */
table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 9.5pt; }
thead tr { background: var(--accent); color: white; }
th { padding: 8px 12px; text-align: left; font-weight: 500; font-size: 8.5pt;
     text-transform: uppercase; letter-spacing: 0.4px; }
td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
tr:last-child td { border-bottom: none; }

.rag { display: inline-block; padding: 2px 10px; border-radius: 12px;
       font-size: 8pt; font-weight: 700; letter-spacing: 0.5px; }
.RED    { background: var(--red-bg);   color: var(--red);   }
.AMBER  { background: var(--amber-bg); color: var(--amber); }
.GREEN  { background: var(--green-bg); color: var(--green); }

.delta-pos { color: var(--red);   }
.delta-neg { color: var(--green); }
.delta-neu { color: var(--muted); }

/* ── Charts ── */
.chart-container { margin: 16px 0; page-break-inside: avoid; }
.chart-container img { width: 100%; border-radius: 4px; }
.chart-label { font-size: 8pt; color: var(--muted); margin-top: 6px;
               text-align: center; font-style: italic; }

/* ── Notes ── */
.notes { font-size: 8pt; color: var(--muted); margin-top: 32px;
         border-top: 1px solid var(--border); padding-top: 12px; }
.notes p { margin-bottom: 6px; }

/* ── Extra sections ── */
.extra-section { margin: 24px 0; }
.extra-section p { font-size: 9.5pt; line-height: 1.6; color: var(--text); }
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8">
<style>{styles}</style>
</head>
<body>

<!-- Cover -->
<div class="cover">
  {logo_html}
  <h1>{title}</h1>
  <div class="subtitle">{subtitle}</div>
  <div class="meta">
    {author_line}
    Generated on {date}
  </div>
</div>

<!-- Content -->
<div class="page">

  <h2>Executive Summary — RAG Scorecard</h2>
  <table>
    <thead>
      <tr>
        <th>Indicator</th>
        <th>Series</th>
        <th>Current</th>
        <th>Δ 3 months</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {scorecard_rows_html}
    </tbody>
  </table>

  {charts_html}

  {extra_sections_html}

  <div class="notes">
    <p><strong>Sources :</strong> Federal Reserve Bank of St. Louis (FRED) — fred.stlouisfed.org</p>
    <p><strong>RAG methodology :</strong> RED = 3-month delta exceeds alert threshold in adverse direction.
       AMBER = adverse trend within threshold. GREEN = stable or improving.</p>
    <p><strong>Series :</strong> DRCCLACBS (delinquency rate, consumer loans), UNRATE (unemployment),
       FEDFUNDS (fed funds effective rate), T10Y2Y (10Y-2Y spread), CPIAUCSL (CPI all items),
       DPSACBW027SBOG (personal savings rate), MORTGAGE30US (30Y fixed mortgage),
       BAMLH0A0HYM2 (ICE BofA HY OAS).</p>
  </div>

</div>
</body>
</html>"""

CHART_LABELS = {
    "dashboard": "Macro risk dashboard — 6 indicators normalised (z-score)",
    "focus":     "Primary signal with supporting indicators",
}


def _img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _scorecard_row_html(row: dict) -> str:
    delta = row["delta_3m"]
    if delta > 0.05:
        delta_class, delta_sign = "delta-pos", "+"
    elif delta < -0.05:
        delta_class, delta_sign = "delta-neg", ""
    else:
        delta_class, delta_sign = "delta-neu", ""
    rag = row["rag"]
    return f"""
      <tr>
        <td>{row['indicator']}</td>
        <td style="font-family:monospace;font-size:8.5pt;color:#888">{row['series']}</td>
        <td><strong>{row['current']:.2f}</strong></td>
        <td class="{delta_class}">{delta_sign}{delta:.2f}</td>
        <td><span class="rag {rag}">{rag}</span></td>
      </tr>"""


def generate_report(
    scorecard_rows: list,
    charts: dict,
    output_path: str = "outputs/macro_report.pdf",
    title: str = "Macro Risk Report",
    subtitle: str = "Monthly update",
    author: str = None,
    logo_path: str = None,
    extra_sections: dict = None,
):
    """
    Generate a PDF macro report.

    Args:
        scorecard_rows  : list of dicts from chart_builder.scorecard()
        charts          : dict of {label: png_path} — e.g. {"dashboard": "outputs/dashboard.png"}
        output_path     : output PDF path
        title           : report title
        subtitle        : report subtitle
        author          : author name (optional)
        logo_path       : path to logo PNG (optional)
        extra_sections  : dict of {section_title: html_content} (optional)
    """
    try:
        from weasyprint import HTML
    except ImportError:
        raise ImportError("Run: pip install weasyprint")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Scorecard rows
    rows_html = "".join(_scorecard_row_html(r) for r in scorecard_rows)

    # Charts
    charts_html_parts = []
    for key, path in charts.items():
        if not os.path.exists(path):
            print(f"  Warning: chart not found — {path}")
            continue
        b64 = _img_to_base64(path)
        label = CHART_LABELS.get(key, key)
        charts_html_parts.append(f"""
  <h2>{label}</h2>
  <div class="chart-container">
    <img src="data:image/png;base64,{b64}" alt="{label}"/>
  </div>""")
    charts_html = "\n".join(charts_html_parts)

    # Extra sections
    extra_html_parts = []
    for section_title, content in (extra_sections or {}).items():
        extra_html_parts.append(f"""
  <div class="extra-section">
    <h2>{section_title}</h2>
    <p>{content}</p>
  </div>""")
    extra_sections_html = "\n".join(extra_html_parts)

    # Logo
    logo_html = ""
    if logo_path and os.path.exists(logo_path):
        b64 = _img_to_base64(logo_path)
        logo_html = f'<img class="logo" src="data:image/png;base64,{b64}" alt="logo"/>'

    # Author
    author_line = f"Prepared by {author}<br>" if author else ""

    html = HTML_TEMPLATE.format(
        styles=STYLES,
        title=title,
        subtitle=subtitle,
        date=datetime.today().strftime("%B %d, %Y"),
        author_line=author_line,
        logo_html=logo_html,
        scorecard_rows_html=rows_html,
        charts_html=charts_html,
        extra_sections_html=extra_sections_html,
    )

    HTML(string=html).write_pdf(output_path)
    size_kb = os.path.getsize(output_path) // 1024
    print(f"PDF report saved → {output_path} ({size_kb} KB)")
    return output_path
