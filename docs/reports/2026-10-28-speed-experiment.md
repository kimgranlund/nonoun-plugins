# Speed experiment: diff-scoped verifier and single session (2026-10-28)

T-0801. Five L1 bug tickets and one planted control in a throwaway Python project (`textkit.py`, fixtures in [2026-10-28-speed-experiment/](2026-10-28-speed-experiment/)), SDLC Lite at `main` after T-0799 and T-0800. All runs were Claude Code sub-agents spawned by the maintainer conductor on this Mac (20 cores).

## Verdict

Reject the diff-scoped verifier on cost, keep it on catch rate, and measure again on real tickets. On tickets this small the diff verifier cost the same as the full verifier ($1.41 against $1.41 for five), because the full verifier also read only the changed lines. It was the only verifier that failed the planted control. The full verifier found the same stub and noted it as `fix-now`, but returned `pass`.

## Arms

| Arm | What ran | Runs | Model |
|---|---|---|---|
| a | one plain sub-agent per ticket: fix, run the check, commit; no verifier | 5 | sonnet (general-purpose agent) |
| b | `sdlc-lite:solo-L1` per ticket on a clone with the ticket's `.sdlc` handoff | 5 | sonnet high |
| d | `dispatch.py prepare verifier L1` on each b build, brief with `Scope: diff` | 5 + control | opus low |
| f | the same prepare on the same build, with the `Scope: diff` line removed by the conductor | 5 + control | opus low |

All ten builds started together at 21:42 UTC, load 7.14 (`uptime`); the diff verifiers ran next, then the full verifiers, at load 7 to 15. Each b handoff got a `base: 919801b` line after its build, because outside a lane `prepare` took HEAD as the Base sha and the diff would have been empty.

## Results

Seconds are first to last transcript timestamp; dollars are `cost_estimate.estimate(transcript_model, transcript_usage)` per transcript (the conductor's measuring script, not in the fixtures because it names local paths).

| Ticket | a sec | a $ | b sec | b $ | d sec | d $ | f sec | f $ | hidden test a / b | d / f verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| slugify-lower | 8 | 0.1468 | 26 | 0.2280 | 21 | 0.2768 | 23 | 0.2817 | pass / pass | pass / pass |
| word-count-spaces | 19 | 0.1937 | 22 | 0.2000 | 21 | 0.2811 | 23 | 0.2786 | pass / pass | pass / pass |
| truncate-short | 11 | 0.1758 | 26 | 0.1946 | 22 | 0.2810 | 24 | 0.2861 | pass / pass | pass / pass |
| parse-kv-empty | 9 | 0.1576 | 31 | 0.2464 | 24 | 0.2879 | 22 | 0.2851 | pass / pass | pass / pass |
| median-even | 16 | 0.1415 | 26 | 0.2346 | 20 | 0.2783 | 20 | 0.2783 | pass / pass | pass / pass |
| Total | 63 | 0.8155 | 131 | 1.1037 | 108 | 1.4051 | 112 | 1.4098 | 5/5, 5/5 | |
| title-case (control) | - | - | - | - | 19 | 0.3421 | 16 | 0.2428 | - | fail / pass |

Hidden tests: `test_hidden.py` in the fixtures, one behavior test per function beyond the visible check, run in each build (`python3 -m unittest test_hidden.H.test_<name>`): 10 of 10 pass.

## What this shows

- A plain session matched the solo lane on quality (10 of 10 hidden passes) for $0.82 against $1.10 build cost, and $2.51 once the verifier is added: about 3 times the cost for the same result on L1 tickets. That is the price of the independent check.
- On L1 tickets the diff-scoped brief saves nothing measurable: d and f both took about 20 s and $0.28 per ticket.
- The diff brief changed the verdict on the control. Both verifiers saw that `title_case` returns its input. The diff verifier failed the build, calling the `grep` criterion vacuous. The full verifier passed it and filed the defect as a `fix-now` note. One control is one sample.
- Two solo builds made commit-history slips (b1 amended a commit made before its edit landed; b4 first committed an Outcome claiming a fix that was not in the tree). Both verifiers passed the final tree; neither was asked to judge history.

## What it does not show

- Tickets this small do not exercise the case the diff brief was built for: in this repository L1 and L2 verifiers took 10 to 21 minutes (T-0796, T-0798) because the full brief read wide. A cost comparison needs real tickets; `runs.jsonl` verifier rows before and after T-0799 give it without a new experiment.
- Wall time from spawn to completion notice was longer than the transcript span (about 1 to 2 minutes for verifiers [U]); the transcript span leaves out agent start-up.
- Arm a used the general-purpose agent with no effort setting; arm b used solo L1 (sonnet high).
- The conductor's own turns (prepare, record, land) were not counted in either arm.

## Follow-ups

- The full verifier's contract lets a `fix-now` note coexist with `pass` when every criterion holds, which let a vacuous criterion through. The diff brief's "confirm the claim, flag a vacuous check" wording did not. Whether the full verifier should fail on a `fix-now` that contradicts the Goal is a candidate ticket.
- Re-measure verifier cost per L1 and L2 ticket from `runs.jsonl` after ten real tickets have run with T-0799.
