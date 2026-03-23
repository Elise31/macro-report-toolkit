---
name: fred-fetcher
description: >
  Récupère des données macro-économiques depuis l'API FRED (Federal Reserve St. Louis)
  et retourne un DataFrame pandas propre. Utilise ce skill dès que l'utilisateur veut
  fetch, récupérer, télécharger ou importer des indicateurs macro (chômage, inflation,
  taux Fed, yield curve, spread crédit, etc.) depuis FRED. Toujours utiliser fred_fetcher.py
  plutôt que de réécrire des appels API manuels.
---

# FRED Fetcher skill

Wrapper propre autour de l'API FRED. Retourne un DataFrame prêt pour `chart_builder`.

## Import

```python
import sys; sys.path.insert(0, ".claude/skills")
import fred_fetcher
```

## Utilisation principale

```python
# Fetch les 8 indicateurs par défaut, 5 ans d'historique
df = fred_fetcher.fetch(api_key="YOUR_KEY")

# Ou via variable d'environnement (recommandé)
# export FRED_API_KEY=your_key
df = fred_fetcher.fetch()

# Sélection de séries et fenêtre personnalisée
df = fred_fetcher.fetch(series=["UNRATE", "FEDFUNDS", "T10Y2Y"], years=3)

# Série unique
s = fred_fetcher.fetch_single("UNRATE", years=2)

# Résumé rapide
fred_fetcher.describe(df)
```

## Séries par défaut

| Série FRED         | Indicateur            |
|--------------------|-----------------------|
| `DRCCLACBS`        | Delinquency rate      |
| `UNRATE`           | Unemployment          |
| `FEDFUNDS`         | Fed funds rate        |
| `T10Y2Y`           | Yield curve 10Y-2Y    |
| `CPIAUCSL`         | CPI inflation         |
| `DPSACBW027SBOG`   | Personal savings rate |
| `MORTGAGE30US`     | 30Y mortgage rate     |
| `BAMLH0A0HYM2`     | HY credit spread      |

## Clé API

Gratuite sur https://fred.stlouisfed.org/docs/api/api_key.html
Recommandé : stocker dans `.env` ou variable d'environnement `FRED_API_KEY`.

```bash
export FRED_API_KEY=your_key_here
```

Ne jamais hardcoder la clé dans un script.

## Output

- Index : `DatetimeIndex` fréquence mensuelle (Month Start)
- Colonnes : noms des séries FRED
- Valeurs manquantes : forward-fill puis back-fill automatique

## Enchaînement avec chart_builder

```python
import sys; sys.path.insert(0, ".claude/skills")
import fred_fetcher, chart_builder

df = fred_fetcher.fetch()
chart_builder.dashboard(df, "outputs/dashboard.png")
chart_builder.risk_chart(df, "outputs/risk.png", primary="UNRATE")
rows = chart_builder.scorecard(df)
```

## Dépendances

```
requests >= 2.28
pandas >= 1.5
```
