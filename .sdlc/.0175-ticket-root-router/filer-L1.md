<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

(Step 7 failed its first verification and passed on the second attempt. Its live-run result is recorded as `unverified`, with two stated reasons, so the fresh-role requirement was not fully met. See Follow-ups.)

## PR title
T-0175: Opt-in tickets/ root and generated .sdlc/AGENTS.md router

## PR body
### Summary
`tickets.py` can now keep tickets under `.sdlc/tickets/`. This is opt-in, through a `ticket_root: tickets` line in `<root>/config`. `tickets.py roadmap` also keeps a managed router block in `.sdlc/AGENTS.md`, with a one-line `@AGENTS.md` import in `.sdlc/CLAUDE.md`. An agent can read one short file and open only the tickets in the stage it needs. A repo with no `ticket_root` line behaves as before.

### Changes
- `tickets.py`
  - `ticket_dir(root)` reads `ticket_root:` from `<root>/config`. The only supported value is `tickets`. Any other value is refused and nothing is written.
  - `strays(root)` refuses when ticket folders sit outside the ticket root.
  - `new`, `close`, `roadmap`, `check`, `archive` and `number` follow the resolved root. `roadmap.md`, `config`, `notes.md` and `_templates/` stay at `<root>`.
  - Roadmap row links gain a `tickets/` prefix only in the `tickets` layout.
  - The cite scan no longer lists `roadmap.md` as a cite.
  - The id floor, the no-filer hint and the `close --dry-run` worktree lines follow each tree's own ticket root. `branch_tickets` reads the branch's own `config` blob for `external_branch:`.
  - The router block is built with `onboard`'s managed-block approach. It lists the stage counts. It also lists one `T-NNNN title (folder)` line per proposed, ready and blocked ticket (done and dropped get counts only), and it holds the create, claim and close procedures. It names `messages/` as the git-ignored mailbox.
  - A new `tickets/AGENTS.md` carries the full procedures. New tickets get a `router:` front matter line. The parser accepts `claimed_by:`, and the router shows it on the active line.
  - `new`, `close`, `roadmap`, `archive` and `number` refuse before writing when the router block is malformed.
  - `check` fails, and says which cause, on a missing block, a stale count, a stale ticket line or a missing `CLAUDE.md` import.
- `board.py`: `task_dirs(root)` makes task discovery follow the ticket root. It falls back to `root` on an unsupported value.
- `traces/ingest.py` and `traces/sources/tickets.py`: `task_dirs` and the ticket reader follow the ticket root. `tickets` stays a plain directory name when there is no config line.
- Selftests in `tickets.py`, `board.py` and `traces/selftest.py` add cases for each rule, with negative controls.
- Docs:
  - Updated `docs/references/sdlc-internals.md`, the `handoff-format` and `ticket` skills, `docs/specs/ticket-stages/design.md` and its `README.md`, and `docs/README.md`.
  - Added `docs/reports/ticket-root-router-live-run.md`, linked from `docs/README.md`.
- Generated `.sdlc/AGENTS.md` and `.sdlc/CLAUDE.md` for this repo's own `.sdlc` (no `ticket_root` line). `.sdlc/roadmap.md` shows no diff.
- No new skill, no migration command, no version bump.

### Verification
Each step was checked by an independent verifier against its acceptance criteria. The plan reviewer passed the plan.
- Step 1, ticket root resolution: pass. Verified by running `new`, `close --rewrite-refs`, `number` and `archive` under `tickets/`, and by the unsupported-value and stray refusals. Mutations of `ticket_dir` and `strays` made the selftest fail. `render` is byte-identical to base without a config line.
- Step 2, id floor and external branches: pass. At the pre-build SHA the same scenario minted a colliding `T-0002`. Mutations of `other_ticket_dirs` and the config-reading branch both failed the selftest. `fanout.py selftest` passes.
- Step 3, router, import and `check` causes: pass. All 21 criteria ran, and the 18 behavior criteria exited non-zero at the base SHA. Injected defects in `router_problems` and `write_router` each failed the selftest. A manual check showed a malformed block refuses without writing.
- Step 4, `board.py`: pass. A stubbed `ticket_dir` made the board selftest fail. A repo with no config line, and one with an unsupported value, did not list `tickets/`.
- Step 5, traces: pass. `traces.py selftest -k tickets` fails when `ticket_dir` is mutated, and the full `traces.py selftest` passes.
- Step 6, docs and skills: pass. The content greps, `check.py plugins/sdlc-lite` and `check-packaging.py` all passed, and `git diff --check` is clean.
- Step 7, live run and validation record: first attempt failed because `Result: verified` contradicted the doc's own limits. The rerun passed with `Result: unverified: <reasons>`.
- Step 8, repo gates: pass. `tickets.py --root .sdlc check` printed `ok: 179 tickets, roadmap current`. `bash plugins/sdlc-lite/scripts/check.sh` exited 0 with no `FAIL` lines; shellcheck was skipped because it is not installed. `check-packaging.py` and the em-dash scan are clean.

Limits:
- The fresh-role run is recorded as unverified. The role (`claude-sonnet-5-5`) claimed and closed a ticket with no skill call. It received `tickets/AGENTS.md` through Claude Code nested-memory loading, not through the handoff's `router:` line. The `, claimed by` router state before the close was reproduced only by replay, not captured live.
- The step 8 gate check (block and digest assert) had no negative control, but the underlying check is covered by the step 3 negative controls.
- This is Claude hook and memory behavior only. No Codex enforcement is claimed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py` supports an opt-in `ticket_root: tickets` line in `.sdlc/config`, which keeps ticket folders under `.sdlc/tickets/`. `tickets.py roadmap` keeps a managed router block in `.sdlc/AGENTS.md` and an `@AGENTS.md` import in `.sdlc/CLAUDE.md`. `check` fails on a missing or stale router. `board.py` and trace ingest follow the same root. A repo with no `ticket_root` line is unchanged.

## Follow-ups
- decide: `scripts/fanout.py` does not support `ticket_root` for regular lanes (builder step 8 and the verifier both flag it), so fanout lanes in a `tickets/` repo may miss tickets.
- note: the fresh-role live run in `docs/reports/ticket-root-router-live-run.md` is recorded unverified, because the role got `tickets/AGENTS.md` by nested-memory loading and the `, claimed by` state was only replayed.
- note: `render()` raises `Fail` for an external caller on an unsupported `ticket_root` value. All in-repo callers resolve the root first.
