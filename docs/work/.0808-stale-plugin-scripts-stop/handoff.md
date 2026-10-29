---
id: T-0808
title: "A conductor's pinned old plugin scripts keep running after an upgrade"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
claimed_by: sdlc-lite-author 2026-10-29
branch: lane/T-0808-t-0808-t0808
worktree: ../sdlc-lite.worktrees/T-0808-t-0808-t0808
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

## Acceptance criteria
- (red) A fanout.py run from an older plugin cache folder beside a newer one exits 2 naming the newer version: `python3 -c "import json,os,shutil,subprocess,sys,tempfile; t=tempfile.mkdtemp(); shutil.copytree('plugins/sdlc-lite', t+'/0.40.0', ignore=shutil.ignore_patterns('bench')); os.makedirs(t+'/99.0.0/.claude-plugin'); open(t+'/99.0.0/.claude-plugin/plugin.json','w').write(json.dumps({'version':'99.0.0'})); e={k:v for k,v in os.environ.items() if not k.startswith('SDLC_')}; e.update(SDLC_PLUGIN_CACHE=t, CLAUDE_PLUGIN_ROOT=''); r=subprocess.run([sys.executable, t+'/0.40.0/scripts/fanout.py', 'queue', '--lanes-dir', t], env=e, capture_output=True, text=True); sys.exit(0 if r.returncode == 2 and '99.0.0' in r.stderr else 1)"` exits 0.
- (red) The dispatch selftest has the refusal case (the guard below runs it): `grep -qF 'stale: dispatch.py in an older cache folder refuses' plugins/sdlc-lite/scripts/dispatch.py` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py` exits 0.

## Outcome

2026-10-29 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: c3046bc9cd9b
- Changed: see commits
- Commits: 9dd0d56 T-0808: record lane T-0808-t-0808-t0808
- Check: 1 (red) fanout.py from an older cache folder beside a newer one exits 2 naming the newer version: pass
- Check: 2 (red) the dispatch selftest has the refusal case: pass
- Check: 3 (guard) `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`: pass
- Check: 4 (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass
- Check: 5 (guard) `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`: pass
- Check: 6 (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass
- Follow-up: note: plugins/sdlc-lite/scripts/plugin_min.py:136 in_cache limits the... -> notes.md
