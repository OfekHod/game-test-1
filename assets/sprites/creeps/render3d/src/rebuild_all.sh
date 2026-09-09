#!/bin/bash
# Full asset rebuild: creep sheets, chibi hero sheets, showcase stills.
set -e
cd "$(dirname "$0")"
rm -rf ../sheets ../../heroes/chibi_marksman/*.png
echo "=== creep sheets ==="
python3 make_sheets.py
echo "=== chibi hero sheets ==="
python3 build_chibi.py
echo "=== showcase stills ==="
python3 render_all.py
echo "=== previews ==="
python3 build_previews.py
echo "=== rebuild complete ==="
