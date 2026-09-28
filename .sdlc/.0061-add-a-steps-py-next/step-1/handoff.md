## Task goal
After any builder or verifier run, `/chain` and the conductor get the next escalation action from code (`steps.py next <step dir>`) instead of re-deriving it from prose, so a `plan defect:` tag or a blocked build can no longer be routed to a rebuild by mistake.

## Step 1: Add `steps.py next` and its selftest cases
level: L3
### Do
In `plugins/sdlc-lite/scripts/steps.py`, add a `next` subcommand (`next <step dir>`). Document it in the module docstring and in `main()`'s argparse. It writes nothing to disk and never reads file times. It uses `order.ordered`, `order.newest`, and `order.counts_after` (imported) as the only ordering rule. Do not change `order.py`.

Output: the first stdout line is `<action>`, or `<action> L<n>` when there is a level. The following lines are `reason: <text>` and one `read: <path>` per result file consulted. The exit code is 0.

The rules, evaluated in this order, mirror /chain step 4:
- Build level: the level of the newest `builder-*.md` by `order`. With no builder result, take the `level: L<n>` line of `<step dir>/handoff.md`.
- Verifier level from build level: L1 or L2 → L1, L3 → L2, L4 or L5 → L3.
- No builder result → `build L<handoff level>`.
- Newest builder `## Status` is `blocked` → `replan`. This holds whatever its Notes say.
- Newest builder is `done` and no verifier result counts after it (`order.counts_after(verifier, builder)` false, or no verifier file) → `verify L<derived>`.
- Newest verifier `## Verdict` is `pass` → `done`.
- Newest verifier is `fail` and the first non-blank line of its `## For the next attempt` starts with `plan defect:` → `replan`.
- Otherwise it is a counted fail. Count the fail verdicts that are not plan defects and that come after a builder result at the current build level (pair each verifier with the newest builder before it, via `order`).
  - Count 1 → `rebuild L<n>`.
  - Count 2 or more at L1 to L4 → `bump L<n+1>`.
  - Count 2 or more at L5 → `stop`.

Errors print one line on stderr starting with `steps next: `, print nothing on stdout, exit 1, and write nothing. They cover:
- a dir that does not exist
- a missing `handoff.md` (or one with no `level:` line) when no builder result exists
- a builder file with no `done`/`blocked` Status
- a verifier file with no `pass`/`fail` Verdict

Reuse the `Fail` pattern.

Extend `selftest()` with fixtures in its temp dir, one `check('next <case> ...', ...)` per case. Every such check name must start with `next `. The cases are:
- build
- verify at L2 (→ L1)
- verify at L4 (→ L3)
- replan on blocked
- replan on a plan-defect fail
- done
- rebuild
- bump
- rebuild at the bumped level after a bump
- stop at L5
- a stale verifier older than a rebuild (→ verify)
- each error kind
- a snapshot-equal check proving `next` writes nothing

Leave the existing split and lint cases and their check names unchanged.
### Acceptance criteria
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'build L2'`
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && printf '## Status\ndone\n' > "$d/builder-L2.md" && printf '{"file":"builder-L2.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'verify L1'`
- `d=$(mktemp -d) && printf 'level: L4\n' > "$d/handoff.md" && printf '## Status\ndone\n' > "$d/builder-L4.md" && printf '{"file":"builder-L4.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'verify L3'`
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && printf '## Status\nblocked\n\n## Notes\nplan defect: c1 bad\n' > "$d/builder-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'replan'`
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && printf '## Status\ndone\n' > "$d/builder-L2.md" && printf '## Verdict\npass\n\n## For the next attempt\nNone\n' > "$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'done'`
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && printf '## Status\ndone\n' > "$d/builder-L2.md" && printf '## Verdict\nfail\n\n## For the next attempt\nfix x\n' > "$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'rebuild L2'`
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && printf '## Status\ndone\n' > "$d/builder-L2.md" && printf '## Verdict\nfail\n\n## For the next attempt\nplan defect: c2 contradicts c1\n' > "$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'replan'`
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && printf '## Status\ndone\n' | tee "$d/builder-L2.md" > "$d/builder-L2-2.md" && printf '## Verdict\nfail\n\n## For the next attempt\nfix x\n' | tee "$d/verifier-L1.md" > "$d/verifier-L1-2.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n{"file":"builder-L2-2.md"}\n{"file":"verifier-L1-2.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'bump L3'`
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && printf '## Status\ndone\n' | tee "$d/builder-L2.md" "$d/builder-L2-2.md" > "$d/builder-L3.md" && printf '## Verdict\nfail\n\n## For the next attempt\nfix x\n' | tee "$d/verifier-L1.md" "$d/verifier-L1-2.md" > "$d/verifier-L2.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n{"file":"builder-L2-2.md"}\n{"file":"verifier-L1-2.md"}\n{"file":"builder-L3.md"}\n{"file":"verifier-L2.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'rebuild L3'`
- `d=$(mktemp -d) && printf 'level: L5\n' > "$d/handoff.md" && printf '## Status\ndone\n' | tee "$d/builder-L5.md" > "$d/builder-L5-2.md" && printf '## Verdict\nfail\n\n## For the next attempt\nfix x\n' | tee "$d/verifier-L3.md" > "$d/verifier-L3-2.md" && printf '{"file":"builder-L5.md"}\n{"file":"verifier-L3.md"}\n{"file":"builder-L5-2.md"}\n{"file":"verifier-L3-2.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'stop'`
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && printf '## Status\ndone\n' | tee "$d/builder-L2.md" > "$d/builder-L2-2.md" && printf '## Verdict\nfail\n\n## For the next attempt\nfix x\n' > "$d/verifier-L1.md" && printf '{"file":"builder-L2.md"}\n{"file":"verifier-L1.md"}\n{"file":"builder-L2-2.md"}\n' > "$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'verify L1'`
- `d=$(mktemp -d) && out=$(python3 plugins/sdlc-lite/scripts/steps.py next "$d" 2>"$d.err"); rc=$?; test $rc -eq 1 && test -z "$out" && grep -q '^steps next: ' "$d.err"` (a dir with no handoff.md and no results)
- `d=$(mktemp -d) && printf 'level: L2\n' > "$d/handoff.md" && printf '## Status\ndone\n' > "$d/builder-L2.md" && printf '## Verdict\nfail\n\n## For the next attempt\nfix x\n' > "$d/verifier-L1.md" && before=$(cd "$d" && ls -A | sort && cat ./* | cksum) && python3 plugins/sdlc-lite/scripts/steps.py next "$d" >/dev/null && after=$(cd "$d" && ls -A | sort && cat ./* | cksum) && test "$before" = "$after"` (writes nothing; red now because `next` exits nonzero)
- `test "$(python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -c '^ok: next ')" -ge 14`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -1 | grep -qx 'steps selftest: PASS'`
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/order.py`
- (guard) The split and lint cases are unchanged. Run `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep '^ok: ' | grep -v '^ok: next '` here, and the same command in a `git worktree add <tmp> HEAD` copy. The two outputs are identical.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
