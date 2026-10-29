---
id: T-0808
title: "A conductor's pinned old plugin scripts keep running after an upgrade"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor whose helpers call an older installed plugin version's scripts stops, or is redirected to the current version, instead of running old behavior all night after a warning.

## Repro
1. Install plugin 0.40.0 while a helper script hard-codes `.../sdlc-lite/0.37.0/scripts`.
2. Run `fanout.py` land or close through that path.

## Expected
The script exits nonzero naming the installed version (unless an explicit flag allows it), or a version-free launcher (the `messages-run.py` pattern) resolves the newest installed scripts at call time.

## Actual
58 overnight logs print "sdlc-lite 0.37.0 in use; 0.40.0 installed: re-resolve the scripts path" and the run continued, so the T-0797 close fix never ran and `skips.md` was restored by hand 6 times (`docs/reports/2026-10-29-sdlc-retro-macbook-pro.md` Findings 2 and 3; `docs/reports/2026-10-29-sdlc-retro-macbook-pro/logs/version-mismatch-logs.txt`). The gen-ui-kit conductor on this Mac also runs 0.38.0 scripts with 0.40.0 installed (`docs/reports/2026-10-29-fleet-retro.md` row 11).

## Context
- Warning text: `plugins/sdlc-lite/scripts/plugin_min.py:128`, `plugins/sdlc-lite/scripts/dispatch.py` (`re-resolve the scripts path`).
- Precedent: `.sdlc/messages/messages-run.py`, a launcher with no version in its path.

## Constraints
- Red check: a selftest that runs a script from an older version folder beside a newer one; it continues today and stops (or resolves to the newer one) after the fix.
- outcome metric: logs printing the version-mismatch warning per overnight run, before: 58 (ultimate-tokens-color-science, 2026-10-29).
