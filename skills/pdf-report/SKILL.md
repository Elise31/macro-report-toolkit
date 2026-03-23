---
name: pdf-report
description: >
  Génère des rapports PDF macro-économiques professionnels avec weasyprint :
  page de garde, scorecard RAG, graphiques intégrés, mise en page structurée.
  Utilise ce skill dès que l'utilisateur demande un rapport PDF, un document
  de synthèse macro, un rapport à envoyer, ou veut assembler charts + données
  en un document prêt à distribuer. Toujours utiliser avec fred-fetcher et charts.
---

# PDF Report skill

Génère un rapport macro PDF complet à partir d'un DataFrame FRED et des charts
produits par `chart_builder`. Utilise **weasyprint** pour le rendu HTML → PDF.

## Prérequis

```bash
pip install weasyprint jinja2
```

## Usage

```python
import sys
sys.path.insert(0, ".claude/skills")
from pdf_report import generate_report

generate_report(
    scorecard_rows=rows,           # liste de dicts de chart_builder.scorecard()
    charts={                       # dict nom → chemin fichier PNG
        "dashboard": "outputs/dashboard.png",
        "focus":     "outputs/risk_chart.png",
    },
    output_path="outputs/macro_report.pdf",
    title="Macro Risk Report",
    subtitle="Monthly update",     # optionnel
    author="Elise",                # optionnel
)
```

## Structure du rapport généré

1. **Page de garde** — titre, date, auteur
2. **Executive summary** — scorecard RAG tableau (RED / AMBER / GREEN)
3. **Dashboard** — graphique 6 panneaux normalisés
4. **Focus chart** — graphique signal principal + supports
5. **Notes méthodologiques** — sources FRED, définitions

## Format scorecard_rows

Produit par `chart_builder.scorecard(df)` :

```python
[
  {"indicator": "Unemployment", "series": "UNRATE",
   "current": 4.1, "delta_3m": +0.2, "rag": "AMBER"},
  {"indicator": "Delinquency rate", "series": "DRCCLACBS",
   "current": 2.8, "delta_3m": +0.3, "rag": "RED"},
  ...
]
```

## Workflow complet

```python
import sys
sys.path.insert(0, ".claude/skills")
from fred_fetcher import fetch_dashboard_data
import chart_builder
from pdf_report import generate_report
import os

os.makedirs("outputs", exist_ok=True)

# 1. Données
df = fetch_dashboard_data(start="2020-01-01")

# 2. Charts
chart_builder.dashboard(df, "outputs/dashboard.png")
chart_builder.risk_chart(df, "outputs/risk_chart.png")
rows = chart_builder.scorecard(df)

# 3. Rapport PDF
generate_report(
    scorecard_rows=rows,
    charts={"dashboard": "outputs/dashboard.png",
            "focus": "outputs/risk_chart.png"},
    output_path="outputs/macro_report.pdf",
    title="Macro Risk Report",
)
print("Rapport généré → outputs/macro_report.pdf")
```

## Personnalisation

**Changer le style** : modifier les variables CSS dans `pdf_report.py` — section `STYLES`.
Couleurs principales : `--accent: #1a1a2e`, `--red: #e05a5a`, `--amber: #f0a500`, `--green: #4caf7d`.

**Ajouter une section** : passer un dict `extra_sections` :
```python
generate_report(
    ...,
    extra_sections={"Contexte marché": "Texte libre ou HTML string"}
)
```

**Logo** : passer `logo_path="assets/logo.png"` — affiché en haut à droite de la page de garde.
