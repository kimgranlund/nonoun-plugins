<!-- role=builder level=L3 model=opus effort=high -->
## Status
blocked

## Changes
- `docs/reports/carry-forward-live-run/probe.sh`: added `--evidence-only <project dir> <out dir>` (exits 2 with a usage line on any other argument count). Tool lines now keep the full input with no `.[0:200]` cut. `search=` lines are read from the log with the handoff's reference jq. `tree_searches` and `symbol_searches` now count `search=` lines. The `<arm>-tools-full.txt` dump is gone, the header comment shows both invocations, and the script ends with `exit 0`.
- `docs/reports/carry-forward-live-run/scout.txt`, `with.txt`, `without.txt`: rewritten by run 2.
- `docs/reports/carry-forward-live-run.md`: rewritten for run 2's actual outcome. Its two Environment blocks cover run 2 and run 1. Method covers both metrics, `--evidence-only`, and criterion 4's fixture. Evidence has the subsections `### Run 1: 200-character metric` (with the recount output) and `### Run 2: full-input metric`, and Limits is updated.
- `docs/README.md`: the carry forward line was replaced in place with run 2's actual outcome (not the criterion 9 text).

## Checks
- `bash -n docs/reports/carry-forward-live-run/probe.sh`: OK.
- `probe.sh --evidence-only x` and `probe.sh --bogus`: both print the usage line and exit 2.
- Criterion 4, run before any model call: PASS.
- Recount of run 1: `probe.sh --evidence-only .../carry-forward-probe.7n2YHsjnKS "$(mktemp -d)"` exits 0.
  - tree_searches and symbol_searches come out as scout 4 and 1, with 2 and 0, without 2 and 1.
  - Compared with the committed run 1 files, only the without arm's two counts changed (0 and 0 became 2 and 1).
- Run 2: `bash docs/reports/carry-forward-live-run/probe.sh`, in the foreground, 10:38 to 10:39 PDT. All three arms exited 0. Project dir is `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.3grTyXYGVo`.
- Criteria, each run verbatim from a scratch script in `$TMPDIR` (since removed):
  - 1: PASS
  - 2: FAIL (`read_scout_result=no`)
  - 3: PASS
  - 4: PASS
  - 5: PASS
  - 6: PASS
  - 7: PASS
  - 8: PASS
  - 9: FAIL (the README line states the actual outcome, so it does not match the success text)
  - 10: PASS
  - 11: PASS
- Rule 8 for criterion 2 (guard): it passes (exit 0) at `$SDLC_BASE_SHA` in `git worktree add --detach "$SDLC_TMP_WORKTREES/base" "$SDLC_BASE_SHA"`, so this is an ordinary failure, not inherited red. The worktree was removed.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (shellcheck not installed, so it was skipped).
- `python3 scripts/check-packaging.py`: exit 0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: "Codex agent definitions verified", exit 0.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: "ok: 208 tickets, roadmap current".
- `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: clean.

## Notes
plan defect: criterion 2 `read_scout_result=yes` only looks for the literal name `scout-L1.md` in tool inputs. A read through a glob does not contain that name, so the criterion is red even though the planner read the file.

- **What the with planner did in run 2.** Its first tool call was `cd <P>/with && cat .sdlc/cf/handoff.md; ls -la .sdlc/cf; for f in .sdlc/cf/*.md; do echo "=== $f"; cat "$f"; done; git ls-files | head -50`.
  - The tool result in its log prints `=== .sdlc/cf/scout-L1.md` and then the scout result, including `## Carry forward`.
  - Its plan cites the file: the Do says "Callers and the existing test come from the scout result `.sdlc/cf/scout-L1.md` (Carry forward)", and the Risks say "The scout's caller list is relied on without a second search."
  - Evidence lines in `with.txt`: `read_scout_result=no`, `cites_result_path=yes`, `copies_section=no`, `symbol_searches=0`, `tree_searches=1` (`search=Bash "find . -name AGENTS.md -not -path './.git/*'"`).
  - So the behavior the criterion is meant to measure did happen; this is a metric miss, the same kind as the 200-character cut.
- **Without arm.** `search=Bash "git grep -n pad_cell"`, `symbol_searches=1`, so criterion 3 passes.
- **Scout.** `carry_forward_section=yes`, `carry_forward_lines=5`, so criterion 1 passes.
- **What I did not do.** Per handoff item 4, I did not edit the metric or any contract and did not rerun; there is no run 3.
- **Criterion 9.** The report and the README line state the actual outcome, so criterion 9 fails as a consequence of criterion 2. If the replan fixes the read metric, `--evidence-only` can recount run 2 from the kept project dir (`.../carry-forward-probe.3grTyXYGVo`) with no model call.
- **The rest of the work is uncommitted in the tree.** It covers probe.sh, run 2's evidence files, the report, and the README line. Every other gate is green.
- **Em dash conflict.** Run 2's scout section held an em dash in its first line. The handoff asks for that text verbatim, and criterion 11 forbids the character in the report. The report writes it as `--` and says so under the quote. The same clash will recur whenever a role writes an em dash.
