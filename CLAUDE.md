# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

A plugin marketplace (`sdlc-agents`, `.claude-plugin/marketplace.json`) holding one plugin, `sdlc-lite`, in `plugins/sdlc-lite/`. Paths below are relative to that plugin folder unless they start with the repo root. All roles, skills, and systems on the roadmap are built. Five benchmark tasks are in `bench/tasks/`; the first baseline ran 2026-09-24 (3 of 5 hidden checks passed, $37.13; both failures were task-spec gaps, since fixed).

## Commands

- Check everything: `scripts/check.sh` (level tables in run.sh, level-rubric, and this file agree; every agent has a run.sh case; shellcheck; `claude plugin validate`). Run it after any change to a level, model, effort, or role. The validate warning about this CLAUDE.md is expected: it guides work on this repo and is not shipped as context.
- Load it in a session: `claude --plugin-dir /Users/kimba/Projects/nonoun/sdlc-agents/plugins/sdlc-lite`, then `/sdlc-lite:<skill>`. Or install from this repo as a marketplace (`/plugin marketplace add /Users/kimba/Projects/nonoun/sdlc-agents`).
- Default agent: in a target repo's `.claude/settings.json`, `"agent": "sdlc-lite:conductor"` makes every session there the conductor (routes asks to skills, dispatches roles, reports with /board, makes only trivial edits itself). Declare it per repo, never in user settings.
- Run one role directly: `scripts/run.sh <role> <level> <handoff.md>` (writes `<role>-<level>.md`, `.log`, and a `runs.jsonl` line next to the handoff)
- Check a level mapping without a model call: `SDLC_DRY_RUN=1 scripts/run.sh builder L3 <handoff.md>`
- Benchmark: `scripts/bench.sh [task ...]` runs tasks headless (raises Bash timeouts so role runs stay in the foreground), then `scripts/bench-summary.sh`

## Layout

- `scripts/run.sh`: the one runner. Holds the role:level → model/effort table, the Fable-never-verifies-Fable swap, and read-only enforcement (Edit/Write disallowed for every role except builder). Read-only does not block Bash, so the verifier's no-git-state-changes rule lives in its prompt.
- `hooks/block-publish.sh`: PreToolUse(Bash) hook. Inside a role run (`SDLC_ROLE`, set by run.sh) it blocks `git push`, `gh pr/issue` writes, `gh release`, mutating `gh api`, and package publishing. Your own session is not affected, so `/file` can publish after approval.
- Feed: `scripts/board.py` renders the status board from `.sdlc/` (skill `/board`; `/chain` reports with it). `scripts/statusline.sh` shows line 1: model, dir, git (branch, dirty, ahead/behind, worktree), context % (🟡 at 70, 🔴 at 85), session cost and duration; line 2 only when `.sdlc/` has tasks: the live role run plus `board.py --summary` (task %, 🔴 count, ⚠ L5); it is wired in `~/.claude/settings.json` by absolute path to `plugins/sdlc-lite/scripts/statusline.sh` (backup: `settings.json.bak-statusline`). `output-styles/sdlc-feed.md` is an optional session style (`/output-style`). `run.sh` keeps `<role>-<level>.running` during a run so both can see live work.
- Agent skills: an agent's frontmatter `skills:` list is loaded by `run.sh` (appended with `--append-system-prompt-file`, plugin paths filled in), because `claude --agent` does not preload them (token probe with a positive control, 2026-09-24). planner ← `level-rubric`, architect ← `decompose`, verifier ← `checks-that-bite` (brought in from the user-level skill). `check.py` fails on a declared skill that does not exist.
- `agents/<role>.md`: one per role; each defines its output format as its final message, which the runner saves.
- `skills/level-rubric`, `skills/handoff-format`: reference skills (not commands) that the launcher skills and `/chain` read. The rubric must match the table in `run.sh`.
- Launcher skills: `/build`, `/plan`, `/verify`, `/research`, `/architect`, `/scout`, `/dig`, `/file`. Workflow skills: `/handoff`, `/chain`, `/bench`, `/board`. Understand skills (run in your session, not headless): `/clarify` (sharpen an ask into the handoff's Intent), `/grill` (greenfield decisions in question rounds, writes `design.md`), `/decompose` (two-plane breakdown, `coverage_check.py` gate, writes `decompose/`; the planner turns its leaves into steps). Modernized from harness find-intent, teamwork grill-the-ask, and harness break-down-problem.

## Purpose

A set of SDLC agents: declared Claude Code subagents, each launched by a `/command`.

## Roadmap

| Agent | Skill | Levels | Status |
|---|---|---|---|
| builder | `/build` | L1 to L5 | built |
| planner | `/plan` | L1 to L3 | built |
| verifier | `/verify` | L1 to L3 | built |
| researcher | `/research` | L1 to L3 | built |
| scout | `/scout` | L1 Haiku low | built |
| archaeologist | `/dig` | L1 Sonnet medium | built |
| architect | `/architect` | L1 Fable high | built |
| filer | `/file` | L1 Opus low; drafts only, the user approves publishing | built |

Systems: shared runner, handoff format, level rubrics, `/handoff`, `/chain` (escalation), `/bench` + `scripts/bench-summary.sh`: built. Escalation is enforced by `/chain` instructions, not by code.

Open: rerun the baseline with the fixed task specs; watch Planner L3 (Fable xhigh) cost, which dominated the two large tasks.

Later (decide from benchmark data, not before): a Bash write guard for read-only roles; a Stop hook that checks result format; a shared rules skill; a `## Checks` section in handoffs listing project lint/typecheck/test commands.

## Decisions

- **Clean context is the default.** Agents start with no conversation history. Everything an agent needs arrives through its prompt, `$ARGUMENTS`, or a handoff file on disk (goal, decisions, paths).
- **Launch pattern: every role runs headless through the runner**, because only `claude -p --model --effort` can set effort (skill and agent frontmatter cannot). A skill with `context: fork` plus `agent:` is used only where effort does not matter.
- **Builders have 5 levels, each with a fixed model and effort:**

  | Level | Model | Effort |
  |---|---|---|
  | L1 | Sonnet | low |
  | L2 | Opus | low |
  | L3 | Opus | high |
  | L4 | Opus | xhigh |
  | L5 | Fable | xhigh |

- **Builders run headless, not as in-session subagents.** Agent and skill frontmatter have no `effort` field (checked against the docs on 2026-09-24), so every launcher skill calls `scripts/run.sh`, which runs `claude -p --agent sdlc-lite:<role> --model <m> --effort <e>`. Input and output go through handoff files (see `skills/handoff-format`).
- **Researcher, Planner, and Verifier have L1 to L3:**

  | Role | L1 | L2 | L3 |
  |---|---|---|---|
  | Researcher | Sonnet medium | Opus medium | Opus high |
  | Planner | Sonnet medium | Opus medium | Fable xhigh |
  | Verifier | Sonnet medium | Fable medium | Fable xhigh |

  Verifier level follows build level: builder L1 or L2 → verifier L1, L3 → L2, L4 or L5 → L3. A replan forces Planner L3. `run.sh` swaps a Fable verifier to Opus (same effort) when the newest build ran on Fable, so Fable never verifies Fable.
- **Fable** is Builder L5, Verifier L2 and L3, Planner L3, and Architect. All models and efforts were confirmed by the user on 2026-09-24. There is no L6: when L5 fails, escalate to the user.
- **When `/build` gets no level**, the skill takes `level:` from the handoff if present. Otherwise it assesses the step against the rubric in `skills/level-rubric/SKILL.md` and picks the lowest fitting level. The same applies to every leveled role.
- **Headless runs use `--dangerously-skip-permissions`.** Every `claude -p` call includes it, so builders can edit files and run tests without prompts. (`auto` denied writes headless; `acceptEdits` needs allow rules for shell commands.) Run builders only in a repo or worktree you are willing to let them change.
- **A full-context fork (`subagent_type: "fork"`) is an exception.** Use one only with a stated reason. It always runs on the parent's model and inherits the parent's blind spots, so it is never an independent reviewer.
