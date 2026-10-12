<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/plugins/sdlc-lite/skills/report/SKILL.md: new file, copied from the draft, with these edits:
  - The `docs/specs/doc-standards/core.md` citation is now a link to `references/views.md#entry-grammar`.
  - The Codex host paragraph is kept. It now also says the Codex transcript mapping is unverified (the transcript is found only from Claude Code's session id or `SDLC_REPORT_TRANSCRIPT`, so on Codex the context fields go under `unknown`) and that AskUserQuestion becomes the host's question mechanism.
  - `AskUserQuestion` is added to `allowed-tools`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/plugins/sdlc-lite/skills/report/references/views.md: new file, the draft unchanged.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/plugins/sdlc-lite/skills/report/references/record-schema.md: new file, the draft rewritten to match step 1's `report.py`:
  - top-level keys `schema`, `generated_at`, `since` and `evidence`
  - the nine groups with their real field names, and `stalled` added to the states
  - the seven `health.context` keys
  - `unknown` as a list of dotted paths
  - a severity column (6 `problem`, 10 `likely`) and the grade bands
  - a threshold-key column with the `report.<key>` keys from `THRESHOLDS`; three limits are fixed (`dead`, `dead-end work`, `check first run late`)
  - the transcript-only signals read `n/a` when there is no transcript
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/plugins/sdlc-lite/skills/sdlc-lite/SKILL.md: routing row `| This thread's state: ... | report |` added after the fleet-status row.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/plugins/sdlc-lite/scripts/check.sh: `python3 "$root/scripts/report.py" selftest || fail=1` added after the fleet_status line, and `report.py` named in the header list.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/plugins/sdlc-lite/scripts/check.py: docstring item `54. Report (T-0460)` and a check block modeled on item 37:
  - `REPORT_NEEDS` pins the six skill phrases, the four script phrases and the check.sh selftest line.
  - `report_bad()` also flags a `harness:` reference and a missing `| report |` route in `skills/sdlc-lite/SKILL.md`.
  - Errors are prefixed `check.py: report:`.
  - Negative controls cover each phrase removed from each file, a planted harness reference and the route removed.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/plugins/sdlc-lite/AGENTS.md: Verification bullet `- Thread report: \`python3 plugins/sdlc-lite/scripts/report.py selftest\`.`
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/docs/references/sdlc-internals.md: a `## \`scripts/report.py\`` entry after fleet_status.py covering the subcommands, sources, snapshot path, `report.<key>` thresholds, exit 2 cases and check.py item 54.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/t/.sdlc/0460-report-skill/notes.md: new file with the live run: date, both commands, the printed summary, highlights from `full`, and the `unknown` list.

## Checks
- `redck.py record .sdlc/0460-report-skill/step-2/handoff.md`, run before the first step-2 edit: exit 0, 5 controls recorded red, stored as retrospective (see Notes).
- `python3 plugins/sdlc-lite/scripts/check.py`: rc 0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`.
- `python3 scripts/check-packaging.py`: rc 0, `PASS: catalog parity, identity, skill routes, hook isolation and context links`.
- `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`: rc 0, `0 errors, 26 warnings`. All 26 warnings are in files this step did not touch, the same count step 1 reported.
- `python3 plugins/sdlc-lite/scripts/report.py render`: rc 0, a 7-line summary, snapshot `20261012T123949Z.json` written.
- `python3 plugins/sdlc-lite/scripts/report.py render full`: rc 0, all 8 sections, snapshot `20261012T123953Z.json` written.
- The step's acceptance criteria, run as one block with `SDLC_BASE_SHA=ebac4973...` and `SDLC_TMP_WORKTREES` set to the brief's tmp prefix:
  - (red) skill phrases and reference files exist: rc 0
  - (red) no `docs/` in the skill folder: rc 0
  - (red) route, check.sh line, AGENTS.md line, internals entry: rc 0
  - (red) check.py item and pin: rc 0
  - (red) negative control (`Render, never compose` removed in a copied plugin gives `check.py: report:`): rc 0
  - (red) `notes.md` names `report.py render`: rc 0
  - scope check: rc 0
- `git diff --check "$SDLC_BASE_SHA"`: rc 0.
- `bash plugins/sdlc-lite/scripts/check.sh`: rc 0 in 1057 s. The log shows `report.py selftest: all cases passed`, `run selftest: PASS`, `hook selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
- No gate was red, so no base-worktree run was needed and none was made.

## Notes
- The red checkpoint ran before any step-2 edit, but `redck.py` stored it as retrospective because step 1's three uncommitted files (`report.py`, `core.md`, `glossary.md`) already differ from base. Only 5 of the 6 `(red)` criteria got a control line: the first one (the `for ph in ... done` loop) has none. I did not run `record` again.
- One adjustment the handoff did not list: `AskUserQuestion` is added to the skill's `allowed-tools`, because section 3 calls it and fleet-status does the same.
- The live render describes the conductor's thread (role `sdlc-lite:conductor`), not the builder's, because the sub-agent inherits `CLAUDE_PID` and `CLAUDE_CODE_SESSION_ID`.
- Two snapshots now sit in the gitignored `.sdlc/runtime/report/` (`20261012T123949Z.json` and `20261012T123953Z.json`). `git check-ignore` confirms `.gitignore:12:.sdlc/runtime/` covers them.
- In the `full` run the `tasks` view printed `recent: none` while the summary run listed two entries. This is expected: the default `--since last-report` window started at the snapshot the first run had just stored.
- `unknown` in both runs: `health.unpushed_commits`, `identity.level`, `identity.name`, `identity.parent`, `outcome.last_result`.
- For the planner: `views.md` and SKILL.md section 2 still describe the summary as "state, needs, now, next, grade", but step 1's summary also prints `recent:` and `unknown:` lines (still at most 8). The handoff asked to align only `record-schema.md`, so I left them as they are.
- The check.py item number is 54, the next free one at build time.
- `docs/README.md` is unchanged, as the handoff says.
- No commit. The throwaway dir under the tmp prefix and the check.sh log were removed.
