# Lane — notes for Claude

A browser MOBA prototype that ships as one file, `lane.html`, plus a
dependency-free Node simulation harness in `sim/`. Read `README.md` first;
`docs/SIM.md` explains how to run experiments and what the numbers should
look like.

## Test build: publish an artifact for every change

The owner tests every change by hand before approving it. Do this without
being asked, every time:

1. **Whenever `lane.html` changes** — a local edit you want tried out, a
   commit, or a pull request — publish the resulting file as a Claude
   Artifact and hand over the link.
2. **Build the copy with the helper, never by hand:**
   `node tools/artifact-html.js <out.html>`. It strips only the document
   skeleton that the artifact host supplies itself and leaves everything else
   byte for byte identical. If it refuses to run, fix `lane.html`'s shape or
   the helper; do not publish an edited copy.
3. **One artifact per pull request.** Name the file `lane-pr<N>.html` and
   republish that same path on every push, so the link in the PR keeps
   pointing at the current head. Before a PR exists, use
   `lane-<branch>.html` and share the link in chat.
4. **Publish settings:** favicon `⚔️`; description naming the PR number and
   the commit the build came from; keep the game's own `<title>`.
5. **The PR description opens with a "Test build" section:** the artifact
   link, the commit it was built from, and — when the PR does not touch
   `lane.html` — one line saying the build is identical to `main`. Refresh
   that section on every push.
6. **Also attach the raw `lane.html` in chat** so it can be opened straight
   from disk.

## Before pushing

- `node sim/run.js 3` must exit on its own and print the headline table.
  A hang means a timer is keeping Node alive; see `sim/stub.js`.
- For anything that touches balance, run `node sim/run.js 40` and compare
  with the "Known state" table in `README.md`; `docs/SIM.md` explains why
  smaller samples are only indicative.
