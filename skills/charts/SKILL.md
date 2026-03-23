---
name: charts
description: >
  Génère des graphiques macro/financiers professionnels à partir d'un DataFrame pandas.
  Utilise ce skill dès que l'utilisateur demande un graphique, un dashboard, un chart,
  une visualisation, un diagramme à partir de données financières ou macro-économiques
  (FRED, indicateurs économiques, séries temporelles). Déclencher aussi pour toute
  demande de "risk chart", "tableau de bord", "scorecard", "RAG status" sur données macro.
  Le script chart_builder.py est prêt à l'emploi — ne pas réécrire la logique de style.
---

# Charts skill — macro & financial visualisations

Ce skill encapsule `chart_builder.py`, un module matplotlib pré-configuré avec un style
dark pro (fond `#0d0d14`, grilles `#222230`, palette cohérente par indicateur).

## Fichiers disponibles

- `chart_builder.py` — module principal, à placer dans `.claude/skills/`

## Import systématique

Toujours insérer ce bloc en tête de script avant d'utiliser le module :

```python
import sys
sys.path.insert(0, ".claude/skills")
import chart_builder
```

---

## Indicateurs FRED supportés nativement

| Série FRED         | Label affiché         | Couleur    | Logique RAG  |
|--------------------|-----------------------|------------|--------------|
| `DRCCLACBS`        | Delinquency rate      | `#e05a5a`  | up_bad       |
| `UNRATE`           | Unemployment          | `#5b9bd5`  | up_bad       |
| `FEDFUNDS`         | Fed funds rate        | `#9b7fd4`  | neutral      |
| `T10Y2Y`           | Yield curve           | `#f0a500`  | watch        |
| `CPIAUCSL`         | CPI inflation         | `#e07a30`  | neutral      |
| `DPSACBW027SBOG`   | Savings rate          | `#4caf7d`  | down_bad     |
| `MORTGAGE30US`     | Mortgage rate         | `#e08080`  | up_bad       |
| `BAMLH0A0HYM2`     | Credit spread         | `#d4a0f0`  | up_bad       |

Pour ajouter un indicateur non listé : voir section **Étendre PANEL_CONFIG** ci-dessous.

---

## Fonctions disponibles

### 1. `risk_chart(df, path, primary, secondary)`

Graphique 2 panneaux : signal principal (haut) + 1–2 indicateurs de support (bas).

```python
chart_builder.risk_chart(
    df,
    path="outputs/risk_chart.png",   # chemin de sortie
    primary="DRCCLACBS",             # indicateur principal
    secondary=["UNRATE", "T10Y2Y"]   # indicateurs secondaires (liste de 1 à 2)
)
```

**Quand l'utiliser** : focus sur un indicateur avec contexte macro.
**Format sortie** : PNG 150 dpi, 12×6 pouces.

---

### 2. `dashboard(df, path)`

Dashboard 6 panneaux, indicateurs normalisés en z-score, badge RAG (RED/AMBER/GREEN)
par panneau.

```python
chart_builder.dashboard(
    df,
    path="outputs/dashboard.png"
)
```

**Quand l'utiliser** : vue d'ensemble multi-indicateurs, rapport exécutif.
**Format sortie** : PNG 150 dpi, 14×7 pouces.
**Note** : prend les 6 premières colonnes du df présentes dans `PANEL_CONFIG`.

---

### 3. `scorecard(df)`

Retourne une liste de dicts avec statut RAG par indicateur — utile pour le rapport PDF.

```python
rows = chart_builder.scorecard(df)
# rows = [{"indicator": "Unemployment", "series": "UNRATE",
#           "current": 4.1, "delta_3m": 0.2, "rag": "AMBER"}, ...]
```

**Quand l'utiliser** : générer un tableau texte ou alimenter un rapport PDF.

---

## Structure attendue du DataFrame

```python
# Index : DatetimeIndex (fréquence mensuelle recommandée)
# Colonnes : noms des séries FRED (ex: "UNRATE", "FEDFUNDS")

import pandas as pd
df.index = pd.to_datetime(df.index)
df.index.freq = "MS"   # Month Start — important pour les formatters de date
```

Exemple minimal :

```python
df = pd.DataFrame({
    "UNRATE":   [3.5, 3.6, 3.7, 4.0, 4.1],
    "FEDFUNDS": [5.25, 5.25, 5.0, 4.75, 4.5],
}, index=pd.date_range("2024-01-01", periods=5, freq="MS"))
```

---

## Workflow type (avec données FRED réelles)

```python
import sys
sys.path.insert(0, ".claude/skills")
import chart_builder
import pandas as pd

# 1. Charger les données (ex: depuis fred_fetcher ou fichier CSV)
df = pd.read_csv("data/fred_data.csv", index_col=0, parse_dates=True)

# 2. Dashboard complet
chart_builder.dashboard(df, "outputs/dashboard.png")

# 3. Focus sur un indicateur
chart_builder.risk_chart(df, "outputs/unemployment_focus.png",
                          primary="UNRATE",
                          secondary=["FEDFUNDS", "T10Y2Y"])

# 4. Scorecard pour le rapport
rows = chart_builder.scorecard(df)
for r in rows:
    print(f"{r['indicator']:25} {r['current']:6.2f}  Δ3m={r['delta_3m']:+.2f}  [{r['rag']}]")
```

---

## Étendre PANEL_CONFIG

Pour ajouter un indicateur FRED non listé, modifier directement `chart_builder.py` :

```python
PANEL_CONFIG["RSAFS"] = ("Retail sales", "#50c8a0", "down_bad")
# Format : "SERIE_FRED": ("Label affiché", "couleur_hex", "direction_RAG")
# direction_RAG : "up_bad" | "down_bad" | "neutral" | "watch"
```

---

## Règles de style — ne pas overrider

Le style dark est intentionnel pour les rapports PDF sur fond sombre.
**Ne jamais** modifier `_DARK`, `_PANEL`, `_GRID`, `_TEXT` dans les scripts appelants.
Si un style clair est nécessaire (ex: rapport imprimable), créer `chart_builder_light.py`
en dupliquant le fichier et en swappant les constantes de couleur.

---

## Dépendances

```
pandas >= 1.5
matplotlib >= 3.6
numpy >= 1.23
```

Installation : `pip install pandas matplotlib numpy`
