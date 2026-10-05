# Agent command live run

Recorded: 2026-10-05. Live run for ticket T-0223: `/sdlc-lite:agent {agent-name} {instructions}` on Claude Code, in a throwaway Python project, four invocations: `scout` returns a result, `solo` delivers a size-M ticket that passes a hidden check, and `ghost` (unknown) and `conductor` are refused. Each arm ran once. Codex was not run.

## Environment

- `claude --version`: `2.1.289 (Claude Code)` ([`claude-version.txt`](agent-command-live-run/claude-version.txt)).
- Plugin commit `db21511` ([`plugin-commit.txt`](agent-command-live-run/plugin-commit.txt)), loaded with `--plugin-dir` from the `agent-cmd` worktree, with the T-0223 skill committed and a clean tree.
- Each outer session was `claude -p --model sonnet --effort medium --dangerously-skip-permissions --output-format stream-json --verbose -- "/sdlc-lite:agent ..."`, run through the env-wrapper from the earlier solo live run (no inherited Claude or SDLC variables), with `SDLC_HEADLESS=1` and the Bash timeouts raised. The outer session is a plain session, not a conductor.
- Models, from each session's own transcript ([`session-models.txt`](agent-command-live-run/session-models.txt)) and the run records:
  - Outer sessions: `claude-sonnet-5-5` in all four arms.
  - Scout role: `claude-haiku-4-5` low (`scout-runs.jsonl`; transcript agent `sdlc-lite:scout`).
  - Solo session: `claude-sonnet-5-5`, transcript agent `sdlc-lite:solo`, started with `--model sonnet --effort xhigh` (tier M). Effort is not recorded in the transcript; it comes from the launch flag.
  - Solo's verifier: `verifier L3`, `fable` `xhigh`, transcript model `claude-fable-5-1`, agent `sdlc-lite:verifier`.
- Working dir: one `mktemp -d` folder under `/tmp` holding a pristine fixture project (`mathkit`, one function `mean`, two tests, one ticket) and one copy per arm. The raw streams are copied under [`agent-command-live-run/arms/`](agent-command-live-run/arms/).

## Fixture and hidden check

[`fixture/`](agent-command-live-run/fixture/) holds the ticket ([`ticket-handoff.md`](agent-command-live-run/fixture/ticket-handoff.md), size M: add `median`, with stated edge cases), the pristine package, and `hidden_check.py`. The hidden check sits beside the project, outside every arm's working directory, and no prompt names it. It runs 13 cases (the list that follows names most of them: odd, even, single, float, tuple, generator, negatives, duplicates, no input mutation, empty raises ValueError, float on even, `mean` intact). On the pristine project it prints `hidden_check: 0/1 passed` ([`hidden-check-base.txt`](agent-command-live-run/fixture/hidden-check-base.txt)).

## Results

| Arm | Prompt | Result | Outer cost | Role cost |
| --- | --- | --- | --- | --- |
| scout | `/sdlc-lite:agent scout Where is mean implemented ...` | Printed `Lane: scout L1 because ...`, wrote a handoff under `.sdlc/where-is-mean/`, ran `run.sh scout L1`, returned `scout-L1.md` and a three-line summary that names `mathkit/stats.py:4-9`, `tests/test_stats.py`, and `ValueError` | $0.21 | $0.07 (scout) |
| solo | `/sdlc-lite:agent solo Deliver the ticket .sdlc/median/handoff.md ...` | `echo "Lane: solo M because ticket T-0001 is size M"`, then `SDLC_ROLE=solo claude -p ... --agent sdlc-lite:solo --model sonnet --effort xhigh ...`; the change is in [`solo-delivered.diff`](agent-command-live-run/arms/solo-delivered.diff) (trailing spaces on added blank lines stripped so `git diff --check` passes), 11 tests pass, hidden check 13 of 13, verifier L3 passed | $0.17 | $3.03 (verifier) |
| ghost | `/sdlc-lite:agent ghost do something` | Refused, launched nothing, printed the valid names and the pointers | $0.13 | none |
| conductor | `/sdlc-lite:agent conductor take over this ticket` | Refused: `conductor` is the current session | $0.13 | none |

- The solo session ran inside the outer session's Bash call, so its own cost is not in the outer cost or in any run record. Only the verifier is in `runs.jsonl`. Total counted spend is about $3.74 (outer sessions $0.21, $0.17, $0.13 and $0.13, scout $0.07, verifier $3.03).
- Tool calls: scout arm used `Read` and `Bash` only; solo arm used `Read` (1) and `Bash` (2); ghost and conductor made none. No arm called the Agent tool, so `hooks/block-role-spawn.sh` was not exercised.
- Grading: `python3 hidden_check.py` on the final tree printed `hidden_check: 13/13 passed` ([`solo-hidden-check.txt`](agent-command-live-run/arms/solo-hidden-check.txt)); the scout arm's tree is unchanged and fails it, as it should ([`scout-hidden-check-unchanged.txt`](agent-command-live-run/arms/scout-hidden-check-unchanged.txt)).
- Solo wrote acceptance criteria into the fixture ticket because it had none, as `agents/solo.md` says, and ran the batched verifier through `run.sh verifier L3`.

## Limits

- One run per arm, one machine, one tiny fixture. Quality of the answers is not compared with anything.
- Codex was not run: the `scout` and `solo` paths on Codex, and the Codex-host skill adapter, are unverified.
- The outer sessions were plain sessions, not conductor sessions. The conductor start rule (Bash, never the Agent tool) is stated in the skill but was not exercised under a conductor here; the solo start path under a conductor is in `docs/reports/solo-live-run.md`.
- Only `solo` and `scout` were run live; `researcher`, `architect`, and `archaeologist` share the scout path but were not launched.
- The interactive background launch was not exercised; every arm ran headless, in the foreground.
- The solo session's own cost was not captured.
