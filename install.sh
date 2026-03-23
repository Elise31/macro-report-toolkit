#!/usr/bin/env bash
# macro-report-toolkit — one-command install
# Usage: curl -s https://raw.githubusercontent.com/YOUR_ORG/macro-report-toolkit/main/install.sh | bash

set -e

REPO="https://github.com/YOUR_ORG/macro-report-toolkit"
SKILLS_DIR="${HOME}/.claude/skills"
TOOLKIT_DIR="${SKILLS_DIR}/macro-report-toolkit"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  macro-report-toolkit installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Create skills dir
mkdir -p "$SKILLS_DIR"

# 2. Clone or update
if [ -d "$TOOLKIT_DIR/.git" ]; then
  echo "→ Updating existing installation..."
  git -C "$TOOLKIT_DIR" pull --quiet
else
  echo "→ Cloning macro-report-toolkit..."
  git clone --quiet "$REPO" "$TOOLKIT_DIR"
fi

# 3. Symlink skill modules to skills root (so Claude Code finds them)
echo "→ Linking skill modules..."
for skill in charts fred-fetcher pdf-report; do
  SRC="${TOOLKIT_DIR}/skills/${skill}"
  DEST="${SKILLS_DIR}/${skill}"
  if [ ! -L "$DEST" ]; then
    ln -sf "$SRC" "$DEST"
    echo "   ✓ ${skill}"
  else
    echo "   ✓ ${skill} (already linked)"
  fi
done

# 4. Install Python dependencies
echo "→ Installing Python dependencies..."
pip install fredapi pandas matplotlib numpy weasyprint jinja2 python-dotenv \
    --quiet --break-system-packages 2>/dev/null || \
pip install fredapi pandas matplotlib numpy weasyprint jinja2 python-dotenv \
    --quiet 2>/dev/null || \
echo "   ⚠ pip install failed — run manually: pip install fredapi pandas matplotlib numpy weasyprint jinja2"

# 5. FRED API key prompt
echo ""
if [ -z "$FRED_API_KEY" ]; then
  echo "→ FRED API key not found in environment."
  echo "  Get your free key at: https://fred.stlouisfed.org/docs/api/api_key.html"
  echo ""
  read -p "  Paste your FRED_API_KEY (or press Enter to skip): " FRED_KEY
  if [ -n "$FRED_KEY" ]; then
    # Add to shell profile
    PROFILE="${HOME}/.zshrc"
    [ -f "${HOME}/.bashrc" ] && PROFILE="${HOME}/.bashrc"
    echo "" >> "$PROFILE"
    echo "export FRED_API_KEY=\"${FRED_KEY}\"" >> "$PROFILE"
    export FRED_API_KEY="$FRED_KEY"
    echo "   ✓ FRED_API_KEY saved to ${PROFILE}"
  fi
else
  echo "→ FRED_API_KEY already set ✓"
fi

# 6. Gmail MCP reminder
echo ""
echo "→ Gmail MCP setup (for email delivery):"
echo "  Add to your project's .claude/settings.json :"
echo '  { "mcpServers": { "gmail": { "type": "url", "url": "https://gmail.mcp.claude.com/mcp" } } }'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installation complete!"
echo ""
echo "  Skills available in Claude Code:"
echo "   • fred-fetcher  — fetch macro data from FRED"
echo "   • charts        — generate risk charts & dashboards"
echo "   • pdf-report    — assemble PDF report"
echo "   • gmail (MCP)   — send report by email"
echo ""
echo "  Quick start:"
echo "   → Open Claude Code and say:"
echo '     "Fetch macro data from FRED, generate the dashboard,'
echo '      build the PDF report and send it to me"'
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
