# Lane — notes for Claude

A browser MOBA prototype that ships as one file, `index.html`, plus a
dependency-free Node simulation harness in `sim/`. Read `README.md` first;
`docs/SIM.md` explains how to run experiments and what the numbers should
look like.

## Test build: publish an artifact for every change

The owner tests every change by hand before approving it. Do this without
being asked, every time:

1. **Whenever `index.html` changes** — a local edit you want tried out, a
   commit, or a pull request — publish the resulting file as a Claude
   Artifact and hand over the link.
2. **Build the copy with the helper, never by hand:**
   `node tools/artifact-html.js <out.html>`. It strips only the document
   skeleton that the artifact host supplies itself and leaves everything else
   byte for byte identical. If it refuses to run, fix `index.html`'s shape or
   the helper; do not publish an edited copy.
3. **One artifact per pull request.** Name the file `lane-pr<N>.html` and
   republish that same path on every push, so the link in the PR keeps
   pointing at the current head. Before a PR exists, use
   `lane-<branch>.html` and share the link in chat.
4. **Publish settings:** favicon `⚔️`; description naming the PR number and
   the commit the build came from; keep the game's own `<title>`.
5. **The PR description opens with a "Test build" section:** the artifact
   link, the commit it was built from, and — when the PR does not touch
   `index.html` — one line saying the build is identical to `main`. Refresh
   that section on every push.
6. **Also attach the raw `index.html` in chat** so it can be opened straight
   from disk.

## Screenshots: show the change working

The artifact link proves it builds. A screenshot proves it works, and it is the
first thing anyone looks at. So whenever the game changes, drive it and send
pictures of the thing you changed — without being asked, every time.

1. **Send the PNGs in chat, with the artifact link.** One per state the change
   actually alters — the new screen, the new marker, the phone layout if it has
   one. Three or four beats twenty.
2. **Photograph the change, not the game.** If you moved a label, the picture
   is of the label. If you changed something that already existed, send the
   before and the after, and say which is which.
3. **Play to the state, do not force it.** Reach it the way a player would, by
   clicking the buttons and pressing the keys. A state you set by reaching into
   the game's internals proves nothing about whether a player can get there.
4. **Caption every one.** A picture with no sentence attached is a puzzle.
5. **Look at them before sending.** Half the bugs worth catching are visible and
   nowhere else: text under a button, a marker that renders seven pixels tall, a
   hero standing in a river. Fix what the picture shows, then take it again.
6. **If a change genuinely cannot be seen, say that** instead of sending a
   screenshot of something adjacent to it.

### Driving the game

Chromium is pre-installed and `PLAYWRIGHT_BROWSERS_PATH` points at it — never
run `playwright install`. Playwright itself goes in a scratch directory, never
in the repo: `README.md` promises no dependencies and `package.json` has none.

```bash
cd "$SCRATCH" && npm init -y
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i playwright
ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome     # pass this as executablePath
```

`chromium.executablePath()` reports a version that may not be the one on disk,
so read the path off the filesystem rather than asking the library for it.

```js
await page.goto('file:///…/index.html');
await page.waitForFunction(() => window.__laneLoaded === true);
```

- `window.__laneLoaded` is the last line the game runs. Wait on it, not on a
  fixed sleep.
- Listen for `pageerror` and console errors and report what they say. The
  webfont cannot load offline, so `net::ERR_*` is noise; nothing else is.
- The frame loop caps `dt` at 0.05s, so headless (~8fps) advances game time at
  a fraction of real time — a nine-second fade can need twenty-odd seconds of
  waiting. Poll for the state you want; never compute the delay.
- Anything on a cooldown or a dwell needs a generous wait before you conclude
  it did not happen. A step that looks broken is usually a wait that was 200ms
  short.
- `devices['iPhone 13']` for the touch layout. The copy and the controls really
  do differ, and it is where the layout bugs are.

## Before pushing

- `node sim/run.js 3` must exit on its own and print the headline table.
  A hang means a timer is keeping Node alive; see `sim/stub.js`.
- For anything that touches balance, run `node sim/run.js 40` and compare
  with the "Known state" table in `README.md`; `docs/SIM.md` explains why
  smaller samples are only indicative.
