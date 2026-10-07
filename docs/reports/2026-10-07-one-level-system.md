# One level system (T-0342)

Dated record, 2026-10-07, branch `onelevel` from main `a6d89eb8`. One scale, L1 to L5, now names role levels, ticket sizes, and solo agents on Claude Code and Codex. No model or effort changed. The ticket stays open for an independent verifier.

## What changed

- Solo agents: `solo-S`, `solo-M`, `solo-L` became `solo-L1`, `solo-L2`, `solo-L3` with the same rows (Sonnet low, Sonnet xhigh, Opus xhigh). `adapters/claude/levels.json` row `solo` is keyed L1 to L3; `claude_roles.py generate` removed the three old files as orphans and wrote the new ones. `evals.py` keeps the solo row out of the model-table lock, as before, so the lock hash did not move (`evals.py check` ok).
- Deprecated aliases kept for one release: `solo_run.py --tier S|M|L` (normalized to the level, with a stderr notice), `budget.py set --tier S|M|L`, the spawn hook and `_role.sh` accepting `sdlc-lite:solo-S|M|L`, and a 0.21.x fanout `land.jsonl` tier. The hook now denies any other solo name (`solo-L4`, `solo-X`).
- Ticket size: `tickets.py` sizes are L1 to L5 (L5 reserved). `parse` reads S, M, L, XL as L1 to L4; `new` and `close` store the level; `migrate-size` (dry run unless `--apply`) rewrites ticket and `_templates` front matter. Applied here: 335 handoffs rewritten and the roadmap regenerated; `tickets.py check` exits 0.
- Lane rules keep their thresholds: before planning, L1 and L2 (aliases S, M) are `solo`, L3 to L5 (aliases L, XL) are `full`, and the 20-criteria cap still applies to L1 and L2. Reason strings now name the level (`size L2 decides before planning ...`). `dispatch.py`, `run.sh`, and `fanout.py` read the level the same way.
- Codex: the solo TOMLs, conductor TOML, and planner TOMLs were regenerated from the reworded role and skill bodies; `docs/references/codex-role-execution.md` gained the solo row. `codex_roles.py` held no S/M/L mapping, so it did not change.
- One table: the level-rubric skill now opens with "One level scale" (level, scale, ticket lane, solo agent per host, budget). `docs/references/sdlc-internals.md` points to it.
- Guard: `check.py` item 43 fails on retired vocabulary in skills, agents, commands, hooks, the Codex prelude and TOMLs, and the alias-owning scripts. An `ALIAS_OK` line passes only in `ALIAS_FILES`.
- Onboard template: the managed `.sdlc` line now says ticket levels L1 and L2. A consumer's existing block will read as changed until `onboard.py setup` refreshes it.

## Inventory

Command: `grep -rInE "tier (S|M|L)\b|size (S|M|L|XL)\b|size S (and|or) M|solo-(S|M|L)\b|S\|M\|L|S, M, L|S/M/L" plugins/ docs/ --exclude-dir=reports`.

| Area | Before | After | What remains |
|---|---|---|---|
| plugin agents (incl. generated) | 28 | 0 | |
| plugin skills | 18 | 0 | |
| plugin adapters (Codex TOML) | 4 | 0 | |
| plugin AGENTS.md | 1 | 0 | |
| plugin hooks | 2 | 3 | the `ALIAS_OK` alias lines |
| plugin scripts | 92 | 38 | the guard's own regexes and controls, `ALIAS_OK` lines, alias selftests, fleet fixtures quoting consumer repos |
| docs (not reports) | 40 | 0 | |
| total | 185 | 41 | |

The done-when grep `grep -rIE "tier (S|M|L)\b|size (S|M|L|XL)\b|solo-(S|M|L)\b" plugins/sdlc-lite/{agents,skills}` returns nothing (no `commands/` folder exists).

## Checks

| Check | Result |
|---|---|
| `check.py` | ok, 19 role levels, 22 generated definitions |
| Guard negative control | a planted `Run it at tier S.` line in `skills/fix/SKILL.md` (temp copy): exit 1, `FAIL skills/fix/SKILL.md:24: retired S/M/L vocabulary "tier S"`; restored: exit 0. In-script controls also flag planted `solo-M`, `size XL`, `S/M/L`, an `S $5, M $30` list, and an `ALIAS_OK` line outside `ALIAS_FILES` |
| `tickets.py check` / `selftest` | rc 0 / PASS (new size cases: aliases read as levels, `migrate-size` dry run and apply, close stores L4 for XL, XXL still fails) |
| `steps.py selftest` | PASS (lanes for L1 to L5 and for S, M, L, XL) |
| `dispatch.py selftest` | PASS (lane gate prints `--tier L1`, `--tier L2`; aliases S, M map to them; L3 and alias L not gated) |
| `solo_run.py selftest` | PASS (L1 to L3 dispatch; S, M, L alias dispatch as `solo-L1..L3`; CLI `--tier S` notice; L4 and XL refused) |
| `fanout.py selftest` | PASS (levels and aliases in lane lines, prep JSON, land report) |
| `hook-selftest.sh` | PASS (`solo-L1..L3` and `solo-S|M|L` allowed with a record, `solo-L4`, `solo-L0`, `solo-XL`, `solo-X` denied) |
| `budget.py`, `fleet_detect.py`, `fleet_collect.py`, `onboard.py`, `evals.py` selftests | PASS |
| `claude_roles.py generate --check` / `selftest` | verified, 22 files / PASS (a solo level `S` or `L4` exits 2) |
| `codex_roles.py generate --check` | verified |
| `codex-selftest.py` | exit 0 |
| `docs_check.py` | 0 errors, 12 warnings (preexisting kinds) |
| `scripts/check-packaging.py` | PASS |
| `git diff --check` | clean |
| `bash plugins/sdlc-lite/scripts/check.sh` | exit 0 in a `git archive` copy at `/tmp/onelevel-check2` (snapshot of this change before the report and its index line), ending `ok: shellcheck`, `ok: plugin validate` |

## Live proofs

Claude Code 2.1.292, throwaway project `/tmp/onelevel-live`, headless `claude -p --plugin-dir <worktree>/plugins/sdlc-lite --agent sdlc-lite:conductor`, `SDLC_HEADLESS=1`, session `0f3fb9ff`. A solo is not a `dispatch.py` row (prepare refuses `solo` by design), so its prepare and record halves are `solo_run.py run` and `solo_run.py complete`; the Agent spawn passes the spawn hook on its dispatch record.

| Ticket | Launch | Dispatch | Agent spawn | Transcript model (assistant turns) | Record | Check |
|---|---|---|---|---|---|---|
| `add-hello`, size L1 | `--tier L1` | `sdlc-lite:solo-L1`, sonnet, low | allowed, agent `add3f9113feae5820` | `claude-sonnet-5-5` (3 of 3) | `role solo`, level L1, sonnet low, transport subagent, priced $0.1137 | `HELLO_OK` |
| `add-bye`, size `S` (alias) | `--tier S` | notice `--tier S is deprecated; use --tier L1`, then `sdlc-lite:solo-L1`, sonnet, low | allowed, agent `a73709f00a860f4f0` | `claude-sonnet-5-5` (2 of 2) | level L1, sonnet low, priced $0.0763 | `BYE_OK` |

`steps.py lane` printed `solo` for both, the alias ticket with reason `size L1 decides before planning`. The deprecated `sdlc-lite:solo-S` subagent type itself is not spawnable live (no such definition ships); the hook's acceptance of it is shown by `hook-selftest.sh` only.

Codex CLI 0.160.1, throwaway project `/tmp/onelevel-codex`, ticket `add-hi` size L1: `solo_run.py run --backend codex --tier L1` ran `codex_exec.py solo L1` (`codex exec` with `sdlc-solo-l1`). Exit 0, `hi.txt` written, check passed, run record level L1, model `gpt-6.1-sol` low (declared by the definition; the raw output carries no model field, so the model is not observed), transport exec, cost null (`codex reports no cost`), 20.9 s. Observed: the run itself. Not observed: the model actually served.

## Limits

- The deprecated aliases are for one release; removing them is a later ticket.
- Consumer repos keep alias sizes until they run `tickets.py migrate-size --apply`; reading them stays valid.
- `fanout.py` report and lane lines now say `level L1` where they said `tier S`; a caller that parsed `tier` text would need the new word (none found in this repo).
