<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 onboard check reports `current` for docs/AGENTS.md, docs/specs/AGENTS.md, docs/references/AGENTS.md: pass. Evidence: ran the span; no FAIL line; `onboard.py check` prints `current docs/AGENTS.md`, `current docs/specs/AGENTS.md`, and the references line matched by `grep -qx`. At the base sha (throwaway worktree) the same loop is red for docs/AGENTS.md and docs/references/AGENTS.md, so the check bites. process-deviations.md records `red-checkpoint: retrospective` for all five (red) criteria; I ran each (red) check at the base sha myself (see #1, #2, #3, #5, #6) and each was red there.
- #2 docs/AGENTS.md managed block contains `specs/doc-standards/README.md`: pass. Evidence: span exit 0 on the built tree (docs/AGENTS.md diff shows item 5 inside the managed block); at base it raises AssertionError.
- #3 template names the registry as a code span and never as a link: pass. Evidence: span exit 0 on the built tree; at base the code-span assert raises AssertionError. onboard.py:443 adds item 5 as a code span; `TEMPLATE_VERSION` unchanged (diff touches only that one line).
- #4 (guard) onboard.py selftest: pass. Evidence: exit 0, output ends `gate check-mode: positive ok, negative ok`.
- #5 docs/README.md links `](specs/doc-standards/README.md)`: pass. Evidence: grep exit 0 on the built tree; exit 1 at base.
- #6 five skills cite their card: pass. Evidence: loop prints nothing on the built tree; at base it prints `base red C6` for all five. Each SKILL.md has one new first body line after the front matter as a code span with "when that file exists in this repository" (git diff for plan-goal, ticket, file, fleet-retro, plan-doc), no link.
- #7 (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: foreground run with SDLC_BASE_SHA set, exit 0, no failing line; `gate_lock selftest ... PASS` at log line 1085, and the log ends `ok: shellcheck`, `ok: plugin validate`. The builder's `inherited red: gate_lock selftest` did not reproduce, consistent with the conductor's note that it is flaky under concurrent gate-lock use. Not an inherited red now: the gate is green.
- #8 (guard) `python3 scripts/check-packaging.py`: pass. Evidence: `PASS: catalog parity, identity, skill routes, hook isolation and context links`, exit 0.
- #9 (guard) `docs_check.py --root .`: pass. Evidence: `docs_check: 0 errors, 24 warnings`, exit 0.
- #10 (guard) `git diff --check "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'`: pass. Evidence: no output, exit 0.
- #11 (guard) scope `test -z` filter: pass. Evidence: exit 0 with SDLC_BASE_SHA=ad35eaaa; no untracked non-.sdlc files exist, and every changed path matches the allowlist.
- Extra from the Do: `codex_roles.py generate --check` prints `Codex agent definitions verified`, `claude_roles.py generate --check` prints `Claude agent definitions verified (22 files)`, so neither is stale. No em or en dash in any added line (`git diff ad35eaaa -U0 -- . ':(exclude).sdlc'` filtered for U+2013/U+2014 prints nothing).

## Out of scope changes
None. The step's own edits are onboard.py (one line), the three managed blocks, docs/README.md, and five SKILL.md files. The other changed paths in the diff against base are steps 1 to 3 output, committed in the wip commit e2e43840, and all match the scope allowlist. The managed-block rewrites also added `goals/` and `kpi/` links, `assets/`, `glossary.md`, and `subagent-list-style.md`, which come from `onboard.plan` and are within the three owned files. The throwaway worktree was removed.

## For the next attempt
None
