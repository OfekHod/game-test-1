#!/bin/bash
# Regenerates every side-view creep SVG into the parent directory.
set -e
cd "$(dirname "$0")"
for s in 0*.py; do python3 "$s"; done
mv out_vanguard.svg   ../radiant_vanguard.svg
mv out_longbowman.svg ../radiant_longbowman.svg
mv out_ghoul.svg      ../dire_ghoul.svg
mv out_hexcaster.svg  ../dire_hexcaster.svg
mv out_golem.svg      ../neutral_rock_golem.svg
