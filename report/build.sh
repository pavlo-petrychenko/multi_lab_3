#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

(cd ../backend && uv run python -m scripts.report_figures > /dev/null)

pandoc звіт.md --standalone --math-method=mathml --css style.css --embed-resources \
  --metadata pagetitle="Звіт ЛР3" -o звіт.html

"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PWD/звіт.pdf" "file://$PWD/звіт.html" 2> /dev/null

rm звіт.html
echo "Saved $PWD/звіт.pdf"
