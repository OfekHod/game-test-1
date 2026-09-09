#!/bin/bash
# Commit each hero's sheets as soon as all 24 land, so the branch never holds a
# set that is half old style and half new, and work is never left uncommitted.
cd "$(dirname "$0")/../../../../.."
SHEETS=assets/sprites/creeps/render3d/sheets
for hero in radiant_vanguard radiant_longbowman dire_ghoul dire_hexcaster neutral_rock_golem; do
  until [ "$(ls $SHEETS/$hero/*.png 2>/dev/null | wc -l)" -ge 24 ] && [ -f "$SHEETS/$hero/$hero.json" ]; do
    sleep 30
  done
  sleep 3
  git add "$SHEETS/$hero"
  git commit -q -m "Re-render $hero: painted style, fitted cell, steel blades

24 sheets: 8 facings x idle 6 / walk 12 / attack 8, with camera-relative
lights no longer counter-rotating and metals reading as metal.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018UXBRxutRyRF8K333N8SJb" || true
  git push -q origin claude/dota2-creep-sprites-z485y9 || true
  echo "committed $hero"
done
