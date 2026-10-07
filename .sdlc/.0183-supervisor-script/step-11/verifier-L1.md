<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -q 'scripts/supervisor.py' docs/references/sdlc-internals.md`: pass. Evidence: I ran it and it matched. The diff adds the `## scripts/supervisor.py` entry at line 41.
- `grep -q '.sdlc/supervisor/' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: I ran it and it matched. The diff adds a layout line, plus `.sdlc/supervisor/...` entries in the ignore list.
- `grep -q 'supervisor' plugins/sdlc-lite/AGENTS.md`: pass. Evidence: I ran it and it matched. The new bullet sits under Behavioral invariants.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I ran it and it exited rc=0, with no FAIL lines. The builder reported a `traces selftest` failure. It no longer reproduces here. The traces corpus reads `.sdlc`, and this tree has the `step-7.superseded-1` files deleted and a `step-7.superseded-2` dir added. That `.sdlc` movement happened outside the builder's three files. The gate is green on the built tree, so inherited red does not apply.
- (guard) `! grep -q "$(printf '\342\200\224')" docs/references/sdlc-internals.md`: pass. Evidence: I ran it and it printed `d`. The em-dash count in the other two files is 0.
- (guard) scope diff against `$SDLC_BASE_SHA`: pass. Evidence: I ran it with base 0e55731 and it printed `e`. Only the three allowed files changed outside `.sdlc`.

Bite check: the em-dash and scope guards are `! grep` or `grep -v | ! grep` forms with real file paths. I saw the scope guard's input list: it names the three files when the diff is non-empty, so a stray file would be listed and the guard would go red. Content checks: the entry names `docs/reports/supervisor-live-run.md`, which exists (`ls` found it), and covers the dry run unless `--run`, the modes, limits, the lock, `STOP`, `status.json`, and that the watcher never claims or moves a message. The ignore entries come from the `.gitignore` that `init` writes, as the builder said. The handoff's wording about a docstring ignore list was loose, so I accept the builder's substitution.

## Out of scope changes
None from the builder. The `.sdlc/` changes are the step-7 superseded-dir deletions and the new `step-7.superseded-2` dir. They are run-harness bookkeeping, and the scope guard excludes `.sdlc`. I judged them harmless because `git status` shows only `.sdlc` paths and the three docs files.

## For the next attempt
None
