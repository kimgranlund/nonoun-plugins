# Release 0.20.8

Recorded: 2026-10-05 (UTC; the work and live runs were on 2026-10-04 local time). SDLC Lite 0.20.8. Progressive Context stays at 0.1.2. Previous release: SDLC Lite 0.20.7 (8d5afb7, tag `v0.20.7`). Built from main commit 2e91432; the release branch adds the manifest bump and this record. Main also holds 9146596, the docs-only correction of the 0.20.7 record, pushed after the 0.20.7 tag.

This record states only what a committed file or a command run for it shows. Where a record does not say something, it says so.

## What changed for consumers

| Change | Evidence | Ticket |
| --- | --- | --- |
| A solo session started through `solo_run.py` checks the ticket's budget first. At 80 percent of `budget_usd` with no ack it prints `solo_run.py: budget <pct>%: ask the user; budget.py ack`, exits 4, starts no session and writes no record. A ticket with no budget is not blocked. Fanout solo lanes inherit it and stop as `driver failed rc=4 (budget gate: budget.py ack)` | `solo_run.py`, `fanout.py`; live run `docs/validation/solo-budget-gate-live-run.md` | T-0229 |
| `solo_run.py run --new-task [slug]` creates a task folder from the brief, so `/agent solo` with no named ticket still writes a `role solo` record | same live run: `cost_usd` 0.121484 for the `--new-task` session | T-0229 |
| `agents/solo.md`, `skills/agent/SKILL.md` and `skills/fanout/SKILL.md` describe the gate, `--new-task`, `--lane`, `--max-lanes`, `--stagger` and which lanes are metered. `check.py` guard 28 requires the gate phrases in those files and in `solo_run.py` and `fanout.py`, with a negative control per phrase | the three files at the tag; `check.py` docstring item 28 | T-0229 |
| `onboard.py` writes a root `AGENTS.md` block that says to pick the lane first with `steps.py lane`, solo by default for size S and M, `/fix` only when asked or when the lane script prints `fix`. There is no template version bump: a block with the old route text reads `stale` by its text, and a hand-edited block stays `edited` unless `--force` is used | `onboard.py` selftest gate `lane-text`; `docs/validation/onboard-lane-text.md` | T-0228 |
| Root `AGENTS.md` gains a section "Map and how work is done here" (the file is 78 lines); `docs/AGENTS.md` (20 lines) and `docs/CLAUDE.md` (an `@AGENTS.md` import) are new | `wc -l` on the tagged tree; `git diff --stat` | T-0227 |
| Two Codex live runs, recorded as evidence, no code change: one fanout lane and one conductor start of solo | `docs/validation/codex-fanout-live-run.md`, `docs/validation/codex-conductor-solo-live-run.md` | none |

Three Codex agent files changed: `sdlc-solo-l1.toml`, `sdlc-solo-l2.toml`, `sdlc-solo-l3.toml` (one `developer_instructions` line each, from `git diff --stat`). No model or effort value was edited in this release.

## Live runs in this release

- Budget gate, Claude Code only, one trial per step: a ticket at 90 percent was refused with exit 4 and no new record; after `budget.py ack` a Sonnet low session ran and wrote `cost_usd` 0.1274452; the `--new-task` session wrote 0.121484. The record counts $0.2489 of spend. Plugin commit `1a1d903`.
- Codex fanout lane, one size S ticket: exit 0 in 39 seconds, hidden check 8 of 8, the run record shows `role solo` on `gpt-6.1-sol` low with `cost_usd` null. Plugin code was commit `8684437`, plugin version 0.20.7.
- Codex conductor start of solo, one size M ticket: exit 0 in 3 minutes 51 seconds, hidden check 12 of 12, one verifier on `gpt-6-astra` high with `shared_with_builder` false, verdict pass. Same plugin commit `8684437`.

## Upgrade notes

- Codex projects that installed the generated agents need `python3 plugins/sdlc-lite/scripts/codex_roles.py install <project>` to receive the three changed `sdlc-solo` agents.
- A repository onboarded earlier has the old route text in its root block. `onboard.py check` then reports `AGENTS.md` as `stale`; `onboard.py setup --dry-run` shows the change and `onboard.py setup` writes it. A read-only check against `ui-kit-maison` moved its `AGENTS.md` from `current` to `stale` (`docs/validation/onboard-lane-text.md`); nothing was written there.
- `solo_run.py` can now exit 4. A caller that treated every non-zero exit as a crash should treat 4 as "ask the user, then `budget.py ack`".

## Verification

- T-0227: the first L3 verifier (Fable) returned `fail` on criteria 3 and 4 (`.sdlc/verify-0227/verifier-L3.md`; it calls criterion 4 a plan defect); a narrow L3 returned `pass` (`.sdlc/verify-0227-b/verifier-L3.md`).
- T-0228: one L3 verifier passed (`.sdlc/verify-0228/verifier-L3.md`).
- T-0229: the first L3 returned `fail` on criteria 6 and 7 (`.sdlc/verify-0229/verifier-L3.md`; it calls criterion 7 a plan defect in the scope span); a narrow L3 returned `pass` (`.sdlc/verify-0229-b/verifier-L3.md`).
- The two Codex live-run records have no verifier result of their own in `.sdlc/`; the conductor run contains one verifier run (`verifier-L3.md` in its evidence folder).

## Known limits

- Evidence is one trial per live step on one machine. The budget gate was exercised live through `solo_run.py` only; a fanout lane hitting it is covered by fanout selftest case 18, not live. No model followed the new `/agent solo` skill text in the live run, which called the wrapper by hand.
- The gate reads recorded cost. It stops a start only after earlier runs pushed a ticket to 80 percent, and a running session is not capped. A Codex solo records cost null, so the gate cannot see its spend. A `full` fanout lane starts a conductor that neither passes the gate nor writes a record, and the raw command in `agents/solo.md` skips both.
- Codex conductor-started solo is unmetered: `runs.jsonl` holds only the verifier record, because the conductor used the native subagent path and not `solo_run.py`. The solo's model and agent role were not observed (no Codex rollout was found); the record rests on the tier table and `solo-report.md`.
- In the Codex fanout run the lane gate ran 0 tests (the fixture's `tests/` is not a package) and the report line said `tier S: sonnet low` on a Codex run. Both are filed as T-0230, which is in this tree as `proposed` and not fixed.
- The two Codex runs used plugin code at 0.20.7, not this release's commit. The Codex runs were one size S and one size M ticket; the size L tier, parallel Codex lanes and the interactive Codex conductor were not run.
- The committed verifier results above were run on each branch before its final merge of main; this record does not say they were rerun on the merged trees.
- The limits in `docs/validation/release-0.20.7.md` that this record does not mention were not re-checked for this release. `shellcheck` is not installed (`command -v shellcheck` prints nothing), so no shell script is shellchecked.
- Not in this release: T-0187, T-0200, T-0201, T-0205, T-0206, T-0207, T-0208, T-0211 and T-0213 are `blocked` in `.sdlc/`.

## Checks run for the release

(filled in after the checks run)
