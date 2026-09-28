---
id: T-0111
title: "Pattern-kill hook misses forms it does not match: ps aux | grep x |..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0102
---

## Goal
Inside a role run, `hooks/block-pattern-kill.sh` also blocks the two pattern-kill forms that pass today (a process list filtered by name piped into `xargs kill`, and a kill word held in a shell variable), without blocking killing a PID the builder saved.

## Intent
Literal ask: Pattern-kill hook misses forms it does not match: `ps aux | grep x | awk ... | xargs kill` and a kill word held in a variable (`p=pkill; $p x`) pass inside role runs.
Deltas:
- Which kill sources count as "by name": defaulted: a pipeline or substitution that feeds `kill` (via `xargs kill` or `kill $(...)`/backticks) from `ps` or `pgrep` output is a pattern kill; `kill $(cat pidfile)`, `kill $pid`, `kill %1`, `echo $! | xargs kill` stay allowed.
- Variable-held kill word: defaulted: a variable expansion used as a command word (`$p`, `${p}`) where the command also assigns a value holding pkill, killall, or kill is blocked; a variable expansion as a command word with no such assignment stays allowed (no blanket ban on `$cmd args`).
- Precision vs fail-closed: defaulted: keep the hook's existing style (strict match on the masked text, loose match on the raw text when it fails closed) and extend both paths.
- Done-condition missing: defaulted: see Done when.
Do: extend `plugins/sdlc-lite/hooks/block-pattern-kill.sh` to block both forms (including close variants: `ps -ef | grep x | awk '{print $2}' | xargs kill -9`, `kill $(ps aux | grep x | awk '{print $2}')`, `p=pkill; $p x`, `k=killall; ${k} node`); add block and allow fixtures for them to `plugins/sdlc-lite/scripts/hook-selftest.sh`; update the hook's header comment and the hook's line in CLAUDE.md and `.claude/agents/sdlc-lite-author.md` if the described blocked set changes.
Non-goals: parsing arbitrary shell; catching kill words built by string concatenation or read from files; changing block-publish.sh or block-background.sh.
Done when: `bash plugins/sdlc-lite/scripts/hook-selftest.sh` passes with new fixtures proving each listed form exits 2 and each listed allowed form exits 0 under `SDLC_ROLE=builder`, and `plugins/sdlc-lite/scripts/check.sh` passes.

## Context
Follow-up from T-0102 (builder-scope-hygiene/filer-L1.md):

Pattern-kill hook misses forms it does not match: `ps aux | grep x | awk ... | xargs kill` and a kill word held in a variable (`p=pkill; $p x`) pass inside role runs.

## Constraints
Existing hook-selftest fixtures keep their results. Hook stays bash plus optional python3, no new dependencies. Never commit, push, or publish.
