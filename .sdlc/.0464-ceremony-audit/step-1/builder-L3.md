<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout41/w/docs/reports/2026-10-12-ceremony-audit.md (new): the 135-line report. It starts with front matter `doc-type: report`, then a one-line result, `## Method`, and the six required headings in order. It uses 3 `[propose a ticket]` markers.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout41/w/docs/reports/2026-10-12-ceremony-audit/count.py (new): a read-only script that produces every count the report cites.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout41/w/docs/reports/2026-10-12-ceremony-audit/counts.txt (new): the script's captured output, sections A to J.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout41/w/docs/reports/2026-10-12-ceremony-audit/fleet-collect.txt (new): a trimmed summary of one `fleet_collect.py collect . --since 2026-10-10` run.

## Checks
- `redck.py record .sdlc/0464-ceremony-audit/step-1/handoff.md` before the first edit: 1 pre-edit control recorded red, exit 0.
- C1 `test -f docs/reports/2026-10-12-ceremony-audit.md`: pass.
- C2 `head -5 ... | grep -qx 'doc-type: report'`: pass.
- C3 docs_check output names no `2026-10-12-ceremony-audit` finding: pass. Rerun after the last edit gave 0 matches.
- C4 (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py >/dev/null`: exit 0 (0 errors, 26 warnings, none about the report).
- C5 six exact headings: pass.
- C6 site words (plan-reviewer, filer, second verifier, full chain, inherited red, gate-lock, replan, question): pass.
- C7 `[propose a ticket]` count is 5 or fewer: pass (3, recounted after the last edit).
- C8 T-0428, T-0456, T-0459, T-0446, T-0445, T-0457, T-0461, T-0462 all named: pass.
- C9 a `.sdlc/.04NN-` pointer and `[U]` are both present: pass.
- C10 no em dash: pass (0 matches after the last edit; also 0 in the evidence files).
- C12 (guard) changed files outside `.sdlc` are only the report and its sibling folder: pass, with `SDLC_BASE_SHA=46a1f500`.
- Negative control for S-6: I appended a span naming a ticket folder that does not exist to the report. docs_check then reported `error S-6 ... .sdlc/.0999-nope/handoff.md` against the report. I restored the file from a byte copy, and docs_check afterwards named no report finding.
- Hygiene: no trailing whitespace in any new file. The report is 135 lines (limit 400).
- Reproducibility: rerunning `count.py` and diffing against `counts.txt` gave identical output.

## Notes
- Criterion 11 (the verifier reruns three counts from `## Method`) was not run by me; it is for the verifier. Suggested picks:
  - First case: the `grep -ho ... filer warnings are open ... | sort -u | wc -l` pipeline should print 8, and the `find .sdlc -maxdepth 2 -path '.sdlc/.04*' -name 'filer-L1*.md' | wc -l` command should print 11.
  - Per-site: the plan-reviewer verdict loop should print pass 17 and replan 7.
  - Prompt lint: `prompt_lint.py | grep -c '^info P-6'` should print 72; the loop, re-verify and re-run greps should print 36, 9 and 55.
- `count.py` also reads `/tmp/fanout-f5N.log` and the three other repos (read-only), so its first-case rows depend on this host.
- `fleet-collect.txt` is a trimmed copy of one collector run. The collector reads every worktree's runs, so a later rerun gives larger totals.
- Corrections to the handoff's claims:
  - "9 of 11 filers" was a count per file. Per ticket it is 6 of 7 tickets with a filer since T-0431.
  - "About 6 lane stalls" is 8 distinct tickets refused for open filer warnings. 6 of them are closed in this tree, all cleared with `--ack-warnings`. T-0458 and T-0460 are still open here.
- Minutes lost are an upper bound: 547 wall minutes, median 50, measured from the last recorded run to the close commit. They are marked `[U]` because the logs carry no timestamps.
- Changes marked `[propose a ticket]`:
  1. A retrospective red-checkpoint on a later step should stop blocking close when the step verifier recorded its own red control.
  2. `steps.py lint` should stop refusing test-fixture paths.
  3. Trial solo L3 with one independent verifier per ticket.
- I did not run `fleet_collect.py` on the other three repos, to stay inside the $8 cap. The report lists this under `## Unverified`.
