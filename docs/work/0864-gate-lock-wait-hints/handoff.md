---
id: T-0864
title: "When gated checks queue for capacity on an idle machine, the operator sees how to raise the capacity, and a ca"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When gated checks queue for capacity on an idle machine, the operator sees how to raise the capacity, and a caller can batch many named gated runs without word-splitting mistakes.

## Intent
- Do: add a capacity hint to the waiting line and to `status`, say "command not run" in the timeout line, and document a safe batching shape in shipped files.
- Non-goals: changing the built-in capacity 6, the default need 3 or the queue order (#90's default and #94 wait on a user decision); a `--batch` mode.
- Done when: the criteria below hold.

## Context
- #90: "with the default policy (`compute_units: 6`, default need 3), only two heavy checks ran at once on an 18-core, 64 GB machine. The queue backed up for hours (up to 7 waiting) while load sat at 3-8." The issue accepts "document `policy set compute_units=N` where users will see it when the queue is long". The numbers are maintainer-approved (`docs/specs/sdlc/gate-lock-admission.md:194`), so they stay.
- #99: a zsh loop with `set -- $c` passed "keys app-shell" as one word to `gate_lock.py run --name "$1-$2" -- node scripts/$1.mjs $2`. zsh does not split an unquoted variable.
- #89: the reported exit 0 does not reproduce (HEAD exits 3), but the timeout line does not say the command never ran.
- `plugins/sdlc/scripts/gate_lock.py`: `run_top` (line 804) prints the waiting line every `SDLC_GATE_REPORT_SECS` (default 15) at lines 855-861; it already appends a load note when `max_load` blocks (`STALL-LINE`). The timeout line is built at line 843 and printed at line 879 (`gate_lock: timeout after ...`); selftests check it with `startswith('gate_lock: timeout after')`, so append, never reword the start. `cmd_status` (line 943) prints rows; `status_data` (line 910) has `load` only when `max_load` is set, but `host_load()` and `load_policy` give what you need.
- Hint rule: the queue waits on capacity (the head does not fit and the host load is at or below `max_load`, or no load is reported). The hint names the current capacity, the load and the command: `capacity compute_units=<C> is full while load <x> is under <max_load>; an operator can raise it: gate_lock.py policy set compute_units=<N>` with N = C + default need. Print it once per run (the first waiting line only), and as one `hint:` line at the end of `status` when the queue is not empty. Add `hint` to `status --json` only as a new optional key.
- Batching shape, for the docstring Usage section and `plugins/sdlc/skills/handoff-format/run-operations.md` (shipped; its gate_lock part is around lines 68-84): a function with explicit arguments, for example `gated() { local name=$1; shift; python3 <plugin-root>/scripts/gate_lock.py run --name "$name" -- "$@"; }` then `gated keys-app-shell node scripts/keys.mjs app-shell`; never split a command held in one variable (`set -- $c` does not split in zsh).
- Follow the selftest pattern: each new control is observed failing in a mutant copy of the script (see `selftest`, line 1801). Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Add the hint to the first waiting line and to `status` (text and an optional JSON key), and append `; command not run` to the timeout line.
2. Add selftest cases: a queue held by capacity at a quiet load shows the hint once; a queue held by load shows no capacity hint; the timeout line ends with `command not run`. Each with a mutant control.
3. Document the hint and the batching shape in the docstring, `run-operations.md`, the `gate_lock.py` entry of `docs/references/sdlc-internals.md`, and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- `python3 plugins/sdlc/scripts/gate_lock.py selftest` exits 0 and lists the three new cases; removing the hint line from the script makes the capacity case fail (state the observed red).
- With a temp `SDLC_GATE_DIR` and `SDLC_GATE_REPORT_SECS=1` (the waiting line first prints after that many seconds, default 15), one holder at `--need compute_units=6` and a second `run --timeout 4 -- true`: the second prints the hint once and exits 3 with a line ending `command not run`.
- `python3 plugins/sdlc/scripts/gate_lock.py status --json` still parses and has no `hint` key when the queue is empty.
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0, `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.

## Constraints
- Built-in policy numbers and queue order stay as they are.
- Exit codes stay: 3 for every admission failure.
- The ledger format does not change.
