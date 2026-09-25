---
id: T-0057
title: "close --ack-warnings to record why stale filer warnings no longer apply, instead of --force"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
A resolved filer warning can be acknowledged with a reason instead of a blanket --force.

## Intent
Literal ask: `close --ack-warnings "<why>"` records why each warning no longer applies, instead of a blanket --force.
Deltas:
- One reason or one per warning: defaulted: one TEXT covers all open warnings; the record quotes the warnings verbatim next to it.
- Where it is recorded: defaulted: the ticket handoff.md gets a `## Closed` section (same heading as `--reason`) with the date, `warnings acknowledged: <why>`, and the acknowledged Warnings text quoted, so the record survives the filer file.
- Follow-ups: defaulted: unlike `--reason`, `--ack-warnings` still reads the filer and files follow-ups exactly as a normal close does (duplicates, `--skip`, `--expect`, numbered archive all unchanged).
- `--dry-run`: defaulted: `--dry-run --ack-warnings TEXT` passes the warnings gate, lists the plan, prints the digest, writes nothing.
- Combinations: defaulted: refuses (writes nothing) together with `--force` or `--reason`; an empty or whitespace-only TEXT refuses.
- No open warnings: defaulted: refuses and writes nothing (an ack of nothing would record a false statement); the error says to rerun without --ack-warnings.
- The open-warnings refusal: defaulted: it now names `--ack-warnings "<why>"` first and `--force` second.
- /file flow: defaulted: step 3.1 offers, via AskUserQuestion, "Leave open" (recommended), "Acknowledge with a reason" (user supplies the why, then `--ack-warnings` on every later call), and "Force close"; unattended it still stops on open warnings and never acks or forces.
Do: add `--ack-warnings TEXT` to `scripts/tickets.py close` per the deltas above; extend `tickets.py selftest` with cases proving each new behavior and refusal (writes nothing on refusal); update the usage docstring and argparse help, `skills/file/SKILL.md` step 3.1, the tickets.py paragraph in the repo `CLAUDE.md`, and `.claude/agents/sdlc-lite-author.md` if it describes close flags.
Non-goals: per-warning reasons; changing `--force` or `--reason` behavior; changing filer output format; any publish.
Done when: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes including the new cases, `plugins/sdlc-lite/scripts/check.sh` passes, and a close with open warnings plus `--ack-warnings "x"` sets the ticket done, files its follow-ups, and appends a `## Closed` section holding the reason and the quoted warnings.

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), on 0.6.0, 2026-09-24.

A stale warning ("nothing committed yet", later committed) makes close refuse, so --force is the only way through. Suggested: `close --ack-warnings "<why>"` records why each warning no longer applies.

## Constraints
Existing close behavior (plain, --force, --reason, --dry-run, --skip/--expect, numbered archive) and all existing selftest cases stay unchanged.
