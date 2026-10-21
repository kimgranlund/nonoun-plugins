---
id: T-0679
title: "scripts warn once on stderr when a newer plugin version is installed"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor or peer that keeps running scripts from an older plugin path after `/reload-plugins` learns it on the next script call: one stderr line names the version in use, the newer installed version, and the path to re-resolve.

## Intent
- Do: in `plugins/sdlc-lite/scripts/plugin_min.py`, add `newer_installed(plugin=PLUGIN)` returning `(have, newest, path)` when the newest version folder under the plugin cache (`$SDLC_PLUGIN_CACHE`, default `CACHE` near line 35) is above the running manifest version, skipping any folder that holds an `.orphaned_at` file, else None; and `stale_line()` returning `sdlc-lite <have> in use; <newest> installed: re-resolve the scripts path (<path>/scripts)`. Print that line once on stderr at the start of `main` in `dispatch.py`, `solo_run.py` and `fanout.py`; never change an exit code.
- Do: add one sentence to `plugins/sdlc-lite/agents/conductor.md` (the step list near line 39): after `/reload-plugins`, re-resolve `${CLAUDE_PLUGIN_ROOT}` before the next script call, since a pinned scripts path keeps the old version.
- Do: add selftest cases in `dispatch.py selftest` (beside the T-0593 plugin_min block near line 4132): a cache with a newer version folder prints the line on a `prepare --dry-run`; an equal or older one prints nothing; a newer folder holding `.orphaned_at` prints nothing.
- Non-goals: refusing on skew (plugin_min owns refusals); warning in every script; a once-per-session marker.
- Done when: the criteria pass.

## Context
Source: GitHub issue #33, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
After a reload the ux-designer peer ran all 49 script calls on the pinned 0.27.0 path, and the conductor kept running lands on 0.27.0. 0.28.0 was installed and orphaned in the same minute (`.orphaned_at` 2026-10-21 00:50Z), so a repo can skip a release silently. On main 8624f984, `plugin_min.hook_plugin` (`plugin_min.py` near line 90) already scans the cache for the newest folder but does not skip orphaned folders and is used only for refusals; the local cache holds 34 `.orphaned_at` markers, so the skip matters. `fleet_detect.py` `rule_plugin_version_stale` reports the same skew after the fact, not to the running session.

## Constraints
Selftest runs set `SDLC_PLUGIN_CACHE` to a temp dir, so a newer real install on the machine does not change any other case's stderr. No new line when no cache exists.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the new cases, and the newer-version case fails with the `main` call removed.
2. `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` and `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0.
3. `grep -n "reload-plugins" plugins/sdlc-lite/agents/conductor.md` prints the new sentence.
4. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
5. `git diff --check <base sha>` exits 0.
