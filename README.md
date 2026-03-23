# macro-report-toolkit

Claude Code skills + MCP tools for automated macro economic reporting.

**Pipeline** : FRED API → Charts → PDF Report → Gmail delivery

---

## Install (one command)

```bash
curl -s https://raw.githubusercontent.com/Elise31/macro-report-toolkit/main/install.sh | bash
```

Then set your FRED API key (free at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)):
```bash
export FRED_API_KEY="your_key_here"
```

---

## What's included

| Component | Type | What it does |
|-----------|------|--------------|
| `fred-fetcher` | Skill | Fetch macro series from FRED → clean DataFrame |
| `charts` | Skill | Generate risk charts & dashboards (matplotlib) |
| `pdf-report` | Skill | Assemble PDF report with scorecard + charts |
| `gmail` | MCP tool | Send report by email via Gmail MCP |

---

## Quick start in Claude Code

Once installed, just say:

> *"Fetch macro data from FRED, generate the dashboard, build the PDF report and send it to me"*

Claude Code handles the full pipeline automatically using the installed skills.

---

## Demo (no API key needed)

```bash
python demo/run_pipeline.py --mock
# → outputs/dashboard.png
# → outputs/risk_chart.png
# → outputs/macro_report.pdf
```

With real FRED data:
```bash
FRED_API_KEY=your_key python demo/run_pipeline.py
```

---

## Indicators tracked

| FRED Series | Indicator | RAG logic |
|-------------|-----------|-----------|
| DRCCLACBS | Delinquency rate | ↑ bad |
| UNRATE | Unemployment | ↑ bad |
| FEDFUNDS | Fed funds rate | neutral |
| T10Y2Y | Yield curve (10Y-2Y) | watch |
| CPIAUCSL | CPI inflation | neutral |
| DPSACBW027SBOG | Savings rate | ↓ bad |
| MORTGAGE30US | 30Y mortgage rate | ↑ bad |
| BAMLH0A0HYM2 | HY credit spread | ↑ bad |

---

## Repo structure

```
macro-report-toolkit/
├── install.sh                  ← one-command onboarding
├── skills/
│   ├── fred-fetcher/
│   │   ├── SKILL.md
│   │   └── fred_fetcher.py
│   ├── charts/
│   │   ├── SKILL.md
│   │   └── chart_builder.py
│   └── pdf-report/
│       ├── SKILL.md
│       └── pdf_report.py
├── mcp/
│   └── gmail/
│       └── README.md           ← Gmail MCP setup instructions
└── demo/
    └── run_pipeline.py         ← full pipeline demo script
```

---

## Contributing

Skills are governed by PR review — open a PR to modify any skill.
Changes affect all team members on next `git pull`.
