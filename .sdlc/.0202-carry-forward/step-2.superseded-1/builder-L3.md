<!-- role=builder level=L3 model=opus effort=high -->
## Status
blocked

## Changes
- `docs/validation/carry-forward-live-run/probe.sh`: new. Builds the fixture, runs the three arms, and writes the evidence files. It also saves the untruncated tool inputs to `$P/<arm>-tools-full.txt` in the throwaway dir, outside the repo; the metrics do not use them.
- `docs/validation/carry-forward-live-run/scout.txt`, `with.txt`, `without.txt`: new, written by probe.sh.
- `docs/validation/carry-forward-live-run.md`: new report with Environment, Method, Evidence and Limits. It states the actual outcome.
- `docs/README.md`: one line added after the Messages wait live run entry. It states the actual outcome, not the passing-run text.

## Checks
- Smoke test of probe.sh's evidence functions on stub files and a copied real log: `copies_section` came out yes, then no after the stub changed; `carry_forward_lines` counted correctly; `model=` dedupes. The search classifier counted 3 searches, 2 of them on `pad_cell`, on 5 sample lines.
- `bash docs/validation/carry-forward-live-run/probe.sh` (run once, foreground, timeout 3600000): exit 0. scout L1, planner L2 with and planner L2 without each exited 0. Project dir `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.7n2YHsjnKS`.
- AC1 (scout section, line count): pass (`carry_forward_section=yes`, `carry_forward_lines=6`).
- AC2 (arm with): pass (`read_scout_result=yes`, `cites_result_path=yes`, `copies_section=no`, `symbol_searches=0`).
- AC3 (arm without has `symbol_searches>=1`): **FAIL**, `symbol_searches=0`.
- AC4 (probe syntax, evidence files): pass.
- AC5 (report sections, T-0202, README link): pass.
- Guard, scope: pass.
- Guard, no em dash: pass.
- Guard `bash plugins/sdlc-lite/scripts/check.sh`: exit 0 (shellcheck not installed, so skipped).
- Guard `python3 scripts/check-packaging.py`: exit 0.
- Guard `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0.
- Guard `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0.
- Guard `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: exit 0. A separate grep for trailing whitespace in the new untracked files found none.

## Notes
plan defect: AC3 (`symbol_searches>=1` in without.txt) cannot pass, because the metric only reads the first 200 characters of each tool input and the without planner's `pad_cell` search sits past that point.

- **What the without planner actually did.** Its second tool call, untruncated, from `$P/without-tools-full.txt`, was: `cd <P>/without; for f in lib/text/pad.sh ... .gitignore; do echo "== $f"; cat $f; done; git grep -n pad_cell; find . -name AGENTS.md -not -path './.git/*'`.
- **Why the metric missed it.** `git grep -n pad_cell` starts after character 200 of the JSON input, so the evidence lines read `tree_searches=0` and `symbol_searches=0`. Its plan does say "`git grep -n pad_cell` finds two" and "verified by `git grep -n pad_cell`".
- **Same pattern, untruncated inputs.** Counting tree searches and `pad_cell` searches over the full inputs gives: scout 4 and 1, with 2 and 0, without 1 and 1. So the behavior under test held: the planner given the scout result did not search for `pad_cell`, and the one without it did.
- **Not done.** I did not rerun any arm or edit any contract, and I did not change the specified metric in probe.sh, because the handoff fixes it. A replan could count over untruncated inputs or raise the cut, then rerun the arms.
- **What is in the tree.** All work is left uncommitted. The report and the README line state this outcome and its cause.
- **Scout result gap (does not affect any criterion).** Its 6 Carry forward lines list both call sites, but they don't name the search or the scope that produced the list. The scout contract asks for that on a complete list. The report records this.
- Raw logs and the full tool-input dumps stay in the throwaway project dir.
