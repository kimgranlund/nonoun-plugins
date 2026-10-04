# Solo live run

Recorded: 2026-10-04

Live run for ticket T-0216. One size-M ticket in a throwaway Python project went through `steps.py lane`, which printed `solo`. The `solo` agent then delivered it at tier M on Claude Code (Sonnet, xhigh) and on Codex (`sdlc-solo-l2`, gpt-6.1-sol high), and one independent batched verifier checked the whole ticket on a different model family. Both arms passed a hidden check the delivering agent never saw, and both verifiers returned pass. On Claude Code the solo launched its own verifier. On Codex it did not, so the verifier was launched from outside the session (see Limits). One trial per arm. Raw evidence is in [solo-live-run/](solo-live-run/).

## Environment

- `claude --version`: `2.1.289 (Claude Code)`.
- `codex --version`: `codex-cli 0.160.0`. `codex login status` printed `Logged in using ChatGPT`.
- Plugin commit `ff8b748` (`git rev-parse --short HEAD`), plugin version 0.20.3 (the Claude init event's `sdlc-lite` entry, source `sdlc-lite@inline`). `git status --porcelain -- plugins/` printed nothing. Every arm used this worktree's `plugins/sdlc-lite` (`--plugin-dir` on Claude Code, `codex_roles.py install` and `run.sh` paths on Codex), not an installed copy.
- Models, from each host's own records:
  - Claude solo: init event `model` `claude-sonnet-5-5`, and all 37 assistant events carry `claude-sonnet-5-5`. The stream does not record effort; it comes from the launch flag `--effort xhigh` below.
  - Claude verifier: result header `<!-- role=verifier level=L3 model=fable effort=xhigh -->`, the same model and effort in `runs.jsonl` and `verifier-L3.attempt.json`, and init event `model` `claude-fable-5-1` in `verifier-L3.log`.
  - Codex parent: rollout `turn_context` `gpt-6.1-sol`, effort `medium`, sandbox `workspace-write`, network off.
  - Codex solo: rollout `session_meta` `agent_role: sdlc-solo-l2` with `parent_thread_id` equal to the parent's thread, and `turn_context` `gpt-6.1-sol`, effort `high`, sandbox `workspace-write`, network off.
  - Codex verifier: result header `<!-- role=verifier level=L3 model=gpt-6-astra effort=high -->`, the same in `runs.jsonl` (`"backend":"codex"`, `"shared_with_builder":false`) and in `verifier-L3.attempt.json` (`"transport":"exec"`). `codex_exec.py` runs `codex exec --ephemeral`, so this run left no rollout file; the model rests on the runner's records.
- macOS, Darwin 25.6.0. Working dir `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/solo-live.WxYaOaJq96` (from `mktemp -d`), holding `project/` (the pristine fixture), `claude/` and `codex/` (one copy per arm), and `hidden_check.py`. The raw streams stay on this machine and are not in this repository.

## Method

Fixture: a Git project with one commit holding a package `strkit` (`__init__.py`, `slug.py`, `words.py`), `tests/test_slug.py` (4 tests), `README.md`, and the ticket [`.sdlc/slug-max-length/handoff.md`](solo-live-run/fixture/ticket-handoff.md) with front matter `size: M`. The ticket asks for a helper `truncate_at_boundary(slug, max_length, sep)` in `words.py`, exported from `__init__.py`, a `max_length=None` keyword on `slugify`, tests, and README text: four or five files.

Hidden check: [`hidden_check.py`](solo-live-run/fixture/hidden_check.py) sat beside `project/`, outside every arm's working dir, and no prompt named it. It runs 19 behavior cases (boundaries, hard cut of a long first word, custom `sep`, `ValueError` below 1 including empty text, the export) and the project's own test suite, and exits 0 only when all 20 pass. Against the pristine project it printed `hidden_check: 2/20 passed` and exited 1 ([`hidden-check-base.txt`](solo-live-run/fixture/hidden-check-base.txt)), so it bites.

Lane: `python3 <plugin>/scripts/steps.py lane .sdlc/slug-max-length` on a copy of the pristine project, and again in each arm's copy before delivery. All three printed ([`lane.txt`](solo-live-run/lane.txt)):

```
solo
reason: size M decides before planning (no planner result yet)
read: .sdlc/slug-max-length/handoff.md
```

Environment: every host command ran through [`env-wrapper.sh`](solo-live-run/fixture/env-wrapper.sh), which removes `CLAUDECODE`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, and every `CLAUDE_CODE_*` and `SDLC_*` variable, because this run was itself launched from a builder role.

The typed brief, the same on both hosts ([`brief.txt`](solo-live-run/fixture/brief.txt)):

```
Brief (tier M).
Ticket: .sdlc/slug-max-length/handoff.md (size M).
Files to read: strkit/__init__.py, strkit/words.py, strkit/slug.py, tests/test_slug.py, README.md.
Check commands: python3 -m unittest discover -s tests
Done criterion: the behavior in the ticket's Intent holds and python3 -m unittest discover -s tests passes.
```

Host commands, run with the arm's copy as cwd:

- Claude Code solo: `SDLC_HEADLESS=1 BASH_DEFAULT_TIMEOUT_MS=3600000 BASH_MAX_TIMEOUT_MS=3600000 claude -p --plugin-dir <plugin> --agent sdlc-lite:solo --model sonnet --effort xhigh --dangerously-skip-permissions --output-format stream-json --verbose --no-session-persistence -- "<brief>"`. `SDLC_HEADLESS=1` and the timeouts follow the headless rule in `agents/conductor.md`.
- Codex setup: `python3 <plugin>/scripts/codex_roles.py install <codex copy>`, which installed 28 project agents, `sdlc-solo-l2.toml` and `sdlc-verifier-l3.toml` among them.
- Codex solo, native subagent form as in the messages live run: `codex exec --json --color never -C <codex copy> -m gpt-6.1-sol -c model_reasoning_effort="medium" -c agents.enabled=true -c approval_policy="never" --sandbox workspace-write "<parent prompt>"`, where the [parent prompt](solo-live-run/codex/parent-prompt.txt) is: "Spawn the sdlc-solo-l2 agent and give it exactly the brief below as its prompt. Wait for its report, then print the report verbatim. Do not edit files, run checks, or spawn any other agent yourself." followed by the brief.
- Codex verifier, after the solo session ended without one: `SDLC_BACKEND=codex bash <plugin>/scripts/run.sh verifier L3 .sdlc/slug-max-length/handoff.md` from the codex copy.

After each arm, `python3 hidden_check.py <arm copy>` ran on the final tree.

## Claude Code

Evidence: [`solo-live-run/claude/`](solo-live-run/claude/): `session-trace.txt` (init, model ids, tool calls, result event, final report), `verifier-L3.md`, `runs.jsonl`, `verifier-L3.attempt.json`, `skips.md`, `solo.diff`, `hidden-check.txt`.

| Item | Value |
|---|---|
| Lane | `solo` |
| Tier and model | M: `claude-sonnet-5-5`, `--effort xhigh` |
| Files changed | `strkit/words.py`, `strkit/slug.py`, `strkit/__init__.py`, `tests/test_slug.py` (14 new tests), `README.md`, and the ticket's new `## Acceptance criteria` (9 items, one a scope guard) |
| Hidden check | `hidden_check: 20/20 passed`, exit 0 |
| Verifier | `run.sh verifier L3`, launched by the solo; `fable` `xhigh` (`claude-fable-5-1`); verdict pass |
| Cost | solo session `total_cost_usd` 1.114 (Sonnet 0.518; Fable 0.597, see Limits); verifier `cost_usd` 4.678; total 5.79 USD |
| Wall time | solo session `duration_ms` 613232 (20:25:56Z to 20:36:13Z), which includes the verifier's `duration_ms` 469786 |

The solo read the ticket and the five named files, ran the tests, edited the five files, and ran the tests and module doctests. It then read `agents/conductor.md`, the head of `run.sh`, and part of `skills/handoff-format/SKILL.md`, appended `## Acceptance criteria` to the ticket, and ran `<plugin>/scripts/run.sh verifier L3 .sdlc/slug-max-length/handoff.md` as one foreground Bash call with `timeout` 3000000. The agent body's `${CLAUDE_PLUGIN_ROOT}` had resolved to this worktree's plugin path. The verifier ran each criterion, checked red at the base commit, and mutated the code to show the tests bite. It reported one surviving mutant: no test pinned a whole-word prefix that fits `max_length` exactly. The solo added `test_max_length_prefix_fits_exactly`, showed it fails with an exclusive loop bound, restored the code, and did not run the verifier again. The hidden check ran on that final tree.

Result: pass

## Codex

Evidence: [`solo-live-run/codex/`](solo-live-run/codex/): `session-trace.txt` (both rollouts' `session_meta`, `turn_context`, function calls, token totals, the solo's messages, wall times), `parent-prompt.txt`, `verifier-L3.md`, `runs.jsonl`, `verifier-L3.attempt.json`, `skips.md`, `solo.diff`, `hidden-check.txt`.

| Item | Value |
|---|---|
| Lane | `solo` |
| Tier and model | M: `sdlc-solo-l2`, `gpt-6.1-sol` `high` (subagent rollout); parent `gpt-6.1-sol` `medium` |
| Files changed | `strkit/words.py`, `strkit/slug.py`, `strkit/__init__.py`, `tests/test_slug.py` (4 new tests), `README.md`, and the ticket's new `## Acceptance criteria` (6 items) |
| Hidden check | `hidden_check: 20/20 passed`, exit 0 |
| Verifier | not launched by the solo; launched from outside with `SDLC_BACKEND=codex run.sh verifier L3`; `gpt-6-astra` `high`, exec transport; verdict pass |
| Cost | no USD: the Codex login is ChatGPT and `runs.jsonl` has `"cost_usd":null`. Tokens: parent 139427, solo 107189, verifier 237215 input and 4620 output |
| Wall time | solo session 20:36:49Z to 20:38:49Z (about 120 s); verifier `duration_ms` 153621 |

The parent called `spawn_agent` with `agent_type: sdlc-solo-l2` and waited. The solo ran one `cat` of the ticket and the five files, one `apply_patch`, and `python3 -m unittest discover -s tests`, which ran 8 tests. It wrote the acceptance criteria, then sent the parent a message, and the parent answered with `send_message`. Both bodies are encrypted in the rollouts. Its final report says: "the required independent Tier M verifier was not run because the user prohibits spawning another agent." It ran no `run.sh` command. The external verifier mutated the code in memory for each criterion and executed the README examples. It returned pass.

Result: pass for delivery and verification. The solo's own verifier step was not exercised on Codex.

## Limits

- One trial per arm, on one machine and one account per host.
- Codex solo did not run its verifier. The parent prompt's "do not spawn any other agent yourself" was meant for the parent, but the solo cited it, so this run confounds the probe with the agent. Even without it, a Codex solo running as a native subagent may have no allowed path to a verifier. Its generated instructions say "Do not spawn further agents from an individual role" and "never start another Codex CLI from a sandboxed shell". Its sandbox had network off, which a nested `codex exec` from `run.sh` needs. Yet `solo.md` says "On Codex the verifier is `sdlc-verifier-l3`". Whether a Codex solo can launch its own verifier is unproven. The verifier here was launched from outside the session.
- On Claude Code the solo changed a test after the verifier passed and did not run the verifier again, so the verdict covers the tree before that one test-only addition. The hidden check covers the final tree.
- The Claude solo session's cost includes 0.597 USD of `claude-fable-5-1` with no Fable assistant event. The stream holds one `server_tool_use` named `advisor`, a tool from this machine's user setup, not from the plugin. Sonnet alone cost 0.518 USD.
- The Claude stream does not record effort. The solo's `xhigh` rests on the launch command. The verifier's `xhigh` rests on run.sh's header, `runs.jsonl`, and attempt record.
- The Codex verifier ran with `--ephemeral` through `codex_exec.py`, so no rollout file exists for it. Its model rests on the runner's records only.
- The Claude solo read three plugin files beyond the brief (`agents/conductor.md`, `run.sh`, `skills/handoff-format/SKILL.md`). `solo.md` says "Read nothing else unless a check failure points there", yet its verification step sends the reader to `agents/conductor.md` and asks for `## Acceptance criteria` with no format named.
- The arms wrote differently sized acceptance criteria (9 items with a scope guard on Claude, 6 prose items on Codex), so the two verifiers checked different criteria lists against the same ticket.
- `run.sh` left an empty `.run.lock` in each task dir (untracked).
- Evidence files have trailing whitespace stripped, so `solo.diff` may not apply as a patch. Quoted agent output keeps the agents' own punctuation.
