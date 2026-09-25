# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

A plugin marketplace (`sdlc-lite`, `.claude-plugin/marketplace.json`) holding one plugin, `sdlc-lite`, in `plugins/sdlc-lite/`. Paths below are relative to that plugin folder unless they start with the repo root. Git remote: `kimgranlund/sdlc-lite` (private). Raw role transcripts (`*.log`) and `bench/logs/` are gitignored; results `.md` and `runs.jsonl` are committed. All roles, skills, and systems on the roadmap are built. Five benchmark tasks are in `bench/tasks/`; the first baseline ran 2026-09-24 (3 of 5 hidden checks passed, $37.13; both failures were task-spec gaps, since fixed).

## Commands

- Check everything: `scripts/check.sh` (level tables in run.sh, level-rubric, and this file agree; every agent has a run.sh case; the tickets, board, steps, and run selftests; shellcheck; `claude plugin validate`). Run it after any change to a level, model, effort, or role. The validate warning about this CLAUDE.md is expected: it guides work on this repo and is not shipped as context.
- Load it in a session: `claude --plugin-dir /Users/kimba/Projects/nonoun/sdlc-agents/plugins/sdlc-lite`, then `/sdlc-lite:<skill>`. Or install from this repo as a marketplace (`/plugin marketplace add /Users/kimba/Projects/nonoun/sdlc-agents`).
- This repo's own sessions run as `sdlc-lite-author` (`.claude/agents/sdlc-lite-author.md`, set in `.claude/settings.json`): the maintainer's invariants, after-change checks, and learned hazards. Keep it in sync with this file.
- Default agent: in a target repo's `.claude/settings.json`, `"agent": "sdlc-lite:conductor"` makes every session there the conductor (routes asks to skills, dispatches roles, reports with /board, makes only trivial edits itself). Declare it per repo, never in user settings.
- Run one role directly: `scripts/run.sh <role> <level> <handoff.md>` (writes `<role>-<level>.md`, `.log`, and a `runs.jsonl` line next to the handoff; a rerun writes `<role>-<level>-<k>.md` and never overwrites)
- Check a level mapping without a model call: `SDLC_DRY_RUN=1 scripts/run.sh builder L3 <handoff.md>`
- Benchmark: `scripts/bench.sh [task ...]` runs tasks headless (raises Bash timeouts so role runs stay in the foreground), then `scripts/bench-summary.sh`. The bench dir (tasks, results, logs) resolves in this order: `--bench-dir DIR`, then `SDLC_BENCH_DIR`, then `<project>/bench/` (git toplevel), then the plugin's `bench/`, via `scripts/bench-dir.sh`. This repo's root has no `bench/`, so the dev bench stays at `plugins/sdlc-lite/bench/`.

## Layout

- `scripts/run.sh`: the one runner. Holds the role:level → model/effort table, a git preflight (exits 2 outside a git work tree or before the first commit), the Fable-never-verifies-Fable swap, and read-only enforcement (Edit/Write disallowed for every role except builder). Read-only does not block Bash, so the verifier's no-git-state-changes rule lives in its prompt.
- `hooks/block-publish.sh`: PreToolUse(Bash) hook. Inside a role run (`SDLC_ROLE`, set by run.sh) it blocks `git push`, `gh pr/issue` writes, `gh release`, mutating `gh api`, and package publishing. Your own session is not affected, so `/file` can publish after approval.
- Feed: `scripts/board.py` renders the status board from `.sdlc/` (skill `/board`; `/chain` reports with it); it adds ID and Ticket columns, read with `tickets.py`'s parser, when a rendered task has ticket front matter, and leaves off tasks whose ticket is `dropped` or `done` with no recorded step work; by default (no `--sort`) it orders by ticket id when any rendered task has ticket front matter (unticketed tasks follow by recency) and by recency otherwise; `--sort id|name|recent` overrides, and `--sort recent` restores recency; its "· changed" cache lives in a per-user cache dir outside the repo (`SDLC_BOARD_STATE_DIR` overrides it), so `/board` writes nothing into the tree; it prints a one-line hint when a legacy `.sdlc/.board-state.json` is present (never deleted automatically, never in `--summary`). `scripts/statusline.sh` shows line 1: model, dir, git (branch, dirty, ahead/behind, worktree), context % (🟡 at 70, 🔴 at 85), session cost and duration; line 2 only when `.sdlc/` has tasks: the live role run plus `board.py --summary` (task %, 🔴 count, ⚠ L5); it is wired in `~/.claude/settings.json` by absolute path to `plugins/sdlc-lite/scripts/statusline.sh` (backup: `settings.json.bak-statusline`). `output-styles/sdlc-feed.md` is an optional session style (`/output-style`). `run.sh` keeps `<role>-<level>.running` during a run so both can see live work.
- Agent skills: an agent's frontmatter `skills:` list is loaded by `run.sh` (appended with `--append-system-prompt-file`, plugin paths filled in), because `claude --agent` does not preload them (token probe with a positive control, 2026-09-24). planner ← `level-rubric`, architect ← `decompose`, verifier ← `checks-that-bite` (brought in from the user-level skill). `check.py` fails on a declared skill that does not exist.
- `scripts/tickets.py`: backs `/ticket`. `new <type> <slug> ["title"]` stamps a ticket with the next id, `close <slug> [--force]` (run by `/file`; `close <slug> --reason "<text>"` closes a ticket finished by other work, without a filer file) sets the ticket `done`, files its filer follow-ups as `proposed` idea tickets, skipping any that exactly duplicate an existing ticket (normalized title or slug), and refuses while Warnings are open unless forced; `close --dry-run` lists the proposed follow-ups with indices and duplicate marks and writes nothing, ending with an `expect <digest>` line of the ordered follow-ups, and `close --skip N[,N...]` files all but the named ones, requires `--expect <digest>`, and refuses, writing nothing, when the digest no longer matches (`/file` runs the dry run and confirms the follow-ups first; none of these flags combines with `--reason`), `roadmap` regenerates `.sdlc/roadmap.md` in dependency order, `check` fails on a bad ticket or a stale roadmap, `selftest` proves each check failure fires. `--root DIR` sets the ticket root (default `.sdlc`). Numbered folders are opt-in: `--numbered` on `new`/`close`/`roadmap`/`check` or a `ticket_folders: numbered` line in `<root>/config` names folders `NNNN-<slug>` from the stamped id and makes `check` enforce the prefix only then, and `roadmap` refuses on a prefix mismatch in numbered mode; a successful `new --numbered` or `close --numbered` also persists that config line, so a later plain `check` enforces it, and plain `check` warns, without failing, when every folder has an `NNNN-` prefix but the config lacks the line; plain slugs are the default. In numbered mode `close` also renames `NNNN-<slug>` to `.NNNN-<slug>` so Finder and `ls` hide finished work; every tool treats a `.NNNN-<slug>` folder as a closed ticket, `check` fails on a dot folder that is not done or dropped, and `archive [--dry-run]` renames existing done/dropped numbered folders; `_templates` and other dot entries stay skipped. Templates: `<root>/_templates/<type>.md` first, else `skills/ticket/templates/<type>.md`.
- `scripts/order.py`: the shared ordering rule for which result is newest (builder, verifier, planner): latest `runs.jsonl` record (run.sh records `file` on each line), else level then rerun index then name; never mtime. `check.sh` runs its selftest.
- `scripts/steps.py`: `split <planner.md | task dir> [--only N]` writes `step-<n>/handoff.md` per the step template, refuses a step dir holding builder or verifier output, and `selftest` proves each failure; `/chain` steps 3 and 4.2 run it.
- `agents/<role>.md`: one per role; each defines its output format as its final message, which the runner saves.
- `skills/level-rubric`, `skills/handoff-format`: reference skills (not commands) that the launcher skills and `/chain` read. The rubric must match the table in `run.sh`.
- Launcher skills: `/build`, `/plan`, `/verify`, `/research`, `/architect`, `/scout`, `/dig`, `/file`. Workflow skills: `/handoff`, `/chain`, `/bench`, `/board`, `/ticket`. Understand skills (run in your session, not headless): `/clarify` (sharpen an ask into the handoff's Intent), `/grill` (greenfield decisions in question rounds, writes `design.md`), `/decompose` (two-plane breakdown, `coverage_check.py` gate, writes `decompose/`; the planner turns its leaves into steps). Modernized from harness find-intent, teamwork grill-the-ask, and harness break-down-problem.

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

Backlog: one folder per ticket, `.sdlc/<slug>/handoff.md` with ticket front matter; `.sdlc/roadmap.md` is generated (`/ticket`, `tickets.py roadmap`), never hand-edited. Open: rerun the baseline with the fixed task specs; watch Planner L3 (Fable xhigh) cost, which dominated the two large tasks.

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

  Verifier level follows build level: builder L1 or L2 → verifier L1, L3 → L2, L4 or L5 → L3. A replan forces Planner L3. `run.sh` never lets a verifier run on the build's model family (user decision, T-0005): after a Fable build a Fable verifier becomes Opus at the same effort, and after a Sonnet build a Sonnet verifier becomes Opus medium.
- **Fable** is Builder L5, Verifier L2 and L3, Planner L3, and Architect. All models and efforts were confirmed by the user on 2026-09-24. There is no L6: when L5 fails, escalate to the user.
- **When `/build` gets no level**, the skill takes `level:` from the handoff if present. Otherwise it assesses the step against the rubric in `skills/level-rubric/SKILL.md` and picks the lowest fitting level. The same applies to every leveled role.
- **Headless runs use `--dangerously-skip-permissions`.** Every `claude -p` call includes it, so builders can edit files and run tests without prompts. (`auto` denied writes headless; `acceptEdits` needs allow rules for shell commands.) Run builders only in a repo or worktree you are willing to let them change.
- **A full-context fork (`subagent_type: "fork"`) is an exception.** Use one only with a stated reason. It always runs on the parent's model and inherits the parent's blind spots, so it is never an independent reviewer.
