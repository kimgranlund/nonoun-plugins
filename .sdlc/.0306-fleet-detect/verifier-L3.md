<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
fail

## Criteria
No builder-*.md exists in the artifacts dir (solo lane per `skips.md`), so there was no builder claim to review. Everything below is from my own runs on the tree.

- C1 `fleet_detect.py selftest` prints `fleet_detect selftest: ok`: pass. Evidence: exit 0, 72 `ok:` lines, no `FAIL`. Bites: mutant A (`limit = 3` hardcoded in `rule_stall_attempts`) and mutant G (stall rule indexes `fp['runs']` directly) both give exit 1 on this criterion.
- C2 observed positive and negative per rule, for all 8 rules: pass. Evidence: loop exit 0. Bites: mutant B (`n >= limit` in the planner rule) prints `no observed positive and negative for planner_results_per_ticket`, exit 1.
- C3 negative control `raising stall_attempts in the table silences stall_attempts`: pass. Evidence: exit 0; on mutant A the line turns `FAIL:` and the criterion exits 1. All 9 threshold keys have a negative-control line, and `grep -n "THRESHOLDS\["` shows every rule reads the table (lines 137 to 213).
- C4 known findings in the selftest (agent-ui share, maison Chromium, gen-ui-kit Chromium): pass. Evidence: exit 0. Bites: mutant C (Chromium count rule dead) fails the maison and gen-ui-kit lines; mutant D (share rule dead) fails the agent-ui line. Fixture numbers checked at source:
  - agent-ui `.sdlc/root-cause-2026-10-06.md:28-30` has 193 runs, $787, planner $250, plan-reviewer $186, 55 percent.
  - maison `.sdlc/root-cause-2026-10-06.md:10` has 53 Chromium processes at about 10 GB.
  - The comment "gen-ui-kit report is not on this machine" is true: `/Users/kimgranlund/Projects/nonoun/gen-ui-kit` (the path in `.sdlc/fleet.json:6`) does not exist. Its fixture (31 processes) is therefore synthetic, not a report number.
  - The comment that no-barrels holds 6 planner results (the report says 12) is true: 6 `planner-*.md` files and 6 planner rows on disk.
- C5 live agent-ui collect at the cutoff piped to detect gives `plan_review_share` over 0.40: pass. Evidence: exit 0. Unsuppressed run: `runs: 193 deduped, $786.95`, finding `plan_review_share` value 0.5546, threshold 0.4, detail planner 249.96, plan-reviewer 186.48, total 786.95. On mutant D the same fingerprint exits 1.
- C6 no-data fingerprint prints nothing on stdout: pass. Evidence: exit 0; unsuppressed run gives rc 0 and `fleet_detect: 0 findings in 1 fingerprints`. Goes red on `{"repo":"/x","processes":{"chromium":{"count":31}}}` (exit 1). The biting conjunct is stdout emptiness only: it also passes on crashing mutant G, and the crash is caught by C1's robustness line instead.
- C7 `THRESHOLDS` sits before the first `def rule_` and has 9 rows: pass. Evidence: exit 0; `THRESHOLDS` at line 49, first rule at line 136, 9 rows, a comment on each. Red on a 10-row mutant and on a copy with no `THRESHOLDS` line (exit 1 each).
- C8 (gate) `fleet_collect.py selftest`: pass. Evidence: `fleet_collect selftest: ok`, 46 `ok:` lines including the new tickets, by_ticket, processes and ci lines. Live `ps` with the new columns: 838 lines, 0 unparsed, 0 null etime.
- C9 no em dash in the three files and `git diff --check`: pass. Evidence: exit 0; all three paths exist, so the negated grep is not vacuous. `git diff --no-index --check /dev/null plugins/sdlc-lite/scripts/fleet_detect.py` prints no whitespace errors for the untracked file.
- C10 `check.sh` runs the selftest and the docs have the entry: pass. Evidence: exit 0; `check.sh:31`, `docs/maintenance/sdlc-internals.md:53`; `bash -n check.sh` exit 0.
- C11 (gate) `check.py`: pass. Evidence: `ok: 19 role levels, 9 agents checked`, exit 0.
- C12 (gate) `tickets.py --root .sdlc check`: pass. Evidence: `ok: 309 tickets, roadmap current`, exit 0.
- Rule 2, in-scope dependents run live (the Do's per-ticket rules, and Done-when 2 "running detect on the fingerprints of the three repos"): fail. No written criterion exercises this; the fail rests on the step's own new collector keys `runs.by_ticket` and `tickets`.
  - Live maison: `fleet_collect.py collect /Users/kimgranlund/Projects/maison/ui-kit-maison --du-timeout 5` piped to detect prints `planner_results_per_ticket runs.by_ticket["tickets"].planner 79 > 5`. "tickets" is not a ticket: maison's `.sdlc/config` has `ticket_root: tickets`, and the most planner rows in any one `tickets/*/runs.jsonl` in the main checkout is 3.
  - The same fingerprint has `tickets: {count: 18, items: []}` although `.sdlc/tickets/` holds 40 folders, so `size_m_criteria` can never fire on maison.
  - Minimal repro outside any git repo: two tickets with 3 planner rows each, one size M handoff with 25 criteria.
    - Under `.sdlc/tickets/` with `ticket_root: tickets`: `by_ticket {'tickets': {'planner': 6}}`, a false `planner_results_per_ticket 6 > 5`, `tickets {'count': 0, 'items': []}`, no `size_m_criteria`.
    - Flat control, same files: `by_ticket {'0001-a': {'planner': 3}, '0002-b': {'planner': 3}}`, no planner finding, `size_m_criteria 25 > 20`.
  - Steelman: the builder would say no criterion names the nested layout and "maison size M is not required". That does not hold. "Not required" means the finding need not fire, not that the collector may read zero tickets. The layout is the plugin's own (`tickets.py:308-329 ticket_dir`). The same collector already reports maison lane overrides as `tickets/.0021-...`, so `ticket_of` disagrees with its own file. Confirmed.

Constraints checked: `subprocess` in `fleet_detect.py` is used only by the selftest to call itself (line 496), so there is no model call, and the selftest's read-only line passes. No model or effort file is in the diff.

## Out of scope changes
None.
- `.sdlc/0306-fleet-detect/handoff.md`: the diff only adds the `## Acceptance criteria` section, which the solo lane writes.
- `plugins/sdlc-lite/scripts/fleet_collect.py`: sanctioned by the acceptance preamble as additive. The diff removes no key, and the live agent-ui fingerprint still carries every earlier documented key.
- `plugins/sdlc-lite/scripts/check.sh` and `docs/references/sdlc-internals.md`: named by C10.
- `base-sha`, `skips.md`, `verifier-L3.attempt.json`: runner records.
- Dependents: `git grep -E 'fleet_collect|fleet_detect'` finds no other consumer of the fingerprint besides `check.sh`, the docs entry and ticket handoffs.

## For the next attempt
All 12 written criteria pass. The defect is in this step's new collector code in `plugins/sdlc-lite/scripts/fleet_collect.py`, on the plugin's supported `ticket_root: tickets` layout, which maison uses.

1. `ticket_of` (line 275, `rel.split(os.sep)[0]` at line 278) takes the first path component under `.sdlc`. Every ticket under `.sdlc/tickets/` collapses into one `by_ticket["tickets"]` bucket, and `planner_results_per_ticket` then reports a false finding (79 on live maison).
2. `tickets_info` (line 430, `os.listdir(sd)` at line 437) lists only direct children of `.sdlc`. It sees none of the handoffs under `.sdlc/tickets/`, so `size_m_criteria` is silent there.

Fix both by resolving the ticket dir per root from that root's `.sdlc/config`, mirroring `tickets.py ticket_dir` (line 308). Add a nested-layout case with a flat control to the `fleet_collect.py` selftest, and update the `by_ticket` and `tickets` wording in the docstring and in `docs/references/sdlc-internals.md`.

After the fix, the repro above should give per-folder `by_ticket` keys, no planner finding, and `size_m_criteria 25 > 20` in both layouts. Live maison should show no `by_ticket["tickets"]` finding and a `tickets.count` near 40. The top-level `first-wave-components` planner 11 finding is legitimate and should remain.
