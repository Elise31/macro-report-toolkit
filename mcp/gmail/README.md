---
name: gmail-sender
description: >
  Envoie le rapport PDF macro par email via Gmail MCP. Utilise ce skill
  dès que l'utilisateur veut envoyer un rapport, distribuer un PDF,
  emailer des résultats macro, ou mentionner "envoyer à" + une adresse email.
  Nécessite le MCP Gmail connecté dans Claude Code.
---

# Gmail Sender

Envoie le rapport PDF via le MCP Gmail natif de Claude.

## Prérequis

Le MCP Gmail doit être configuré dans `.claude/settings.json` :

```json
{
  "mcpServers": {
    "gmail": {
      "type": "url",
      "url": "https://gmail.mcp.claude.com/mcp"
    }
  }
}
```

## Usage dans Claude Code

Une fois le MCP connecté, Claude envoie directement l'email.
Dire simplement :

> "Envoie le rapport outputs/macro_report.pdf à john@example.com
>  avec le sujet 'Macro Risk Report — [mois]'"

Claude utilise le MCP Gmail pour :
1. Lire le fichier PDF en base64
2. Créer le draft avec pièce jointe
3. Envoyer

## Template email standard

**Sujet** : `Macro Risk Report — {mois} {année}`

**Corps** :
```
Bonjour,

Veuillez trouver en pièce jointe le rapport macro mensuel.

Points d'attention ce mois-ci :
- [indicateurs RED du scorecard]
- [tendances AMBER à surveiller]

Sources : Federal Reserve Bank of St. Louis (FRED)
Généré automatiquement via macro-report-toolkit.

Cordialement
```

## Workflow complet automatisé

```python
# Après generate_report(), dire à Claude :
# "Envoie outputs/macro_report.pdf à team@example.com"
# Claude gère l'envoi via MCP Gmail directement.
```

## Notes

- La pièce jointe est limitée à 25 MB (limite Gmail) — les rapports
  PDF macro restent généralement sous 5 MB.
- Pour envoyer à plusieurs destinataires : lister les emails séparés par virgule.
- Pour programmer l'envoi : utiliser Gmail "Schedule send" via MCP.
