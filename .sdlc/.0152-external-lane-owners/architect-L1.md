<!-- role=architect level=L1 model=fable effort=high -->
Manifest passes (exit 0), report written. Composing the final design now.

## Approach

An external lane is a branch ref, not a worktree. Everything a regular lane's worktree exists for (the driver, the pre-driver sync, the lane commit, the wip commit on a stop) is exactly what the handoff rules out for a branch an outside agent owns. What remains per ticket is the locked merge into the integration worktree, the gates, and the close, and those need only the ref. So `fanout.py` gains one spec form, `<lane>@<branch>=<ids>`, that preflight marks `Lane.external`, setup skips (no `git worktree add`, no `<integration>-<lane>` branch), and `run_ticket` short-circuits to the locked merge. The outside branch is never written: no sync merge onto it, no ref update. A branch that has diverged from integration either merges cleanly (`--no-ff`) or reports `merge conflict`, and the outside agent reconciles on their side. This deviates from the handoff's default wording ("syncs ... like any lane") on purpose: the branch is typically still checked out in the outside agent's worktree, so `git worktree add` would refuse it (fanout's own preflight already states this for the integration branch) and updating the ref behind a checked-out worktree desyncs that agent's index. A second ticket on the same branch hits `Already up to date.` (rc 0, HEAD unchanged, verified); gates run only when the merge produced a new commit, so a multi-ticket external lane merges once, gates once, closes each ticket in order.

Registration is one line per branch in the file `config_numbered` already reads: `external_branch: <name>` in `<root>/config`. `tickets.py` gets two small readers, `external_branches(root)` and `branch_tickets(root, branch)`, the second reading `<branch>:<rel>/<dir>/handoff.md` blobs through `git ls-tree` plus `git cat-file --batch` with `load()`'s directory rules (skip `_`/`.` except `.NNNN-<slug>`). `id_floor` folds the registered branches' ids into its max next to the worktree roots, so both `new` and close's follow-up stamp above them; unregistered repos and non-git roots take the same code path as today (empty list, floor unchanged). `fanout.py` preflight refuses an external lane whose branch is not registered, so one record serves both the id guard and the lane join, and a branch can't be in fanout while its ids are unguarded. Preflight resolves an external lane's tickets from `branch_tickets` (they may exist only on that branch, which is the whole point) and checks the handoff at `<branch>:<path>` rather than at the integration start commit. `check` prints a warning (exit 0) for a registered name with no local ref, because a typo there would otherwise guard nothing silently.

The close stays the plain `tickets.py close <slug>` on the integration branch, run in the integration worktree after the merge brought the ticket folder in. A branch whose ticket has no `filer-L*.md` gets `merged, close refused: ...` exactly as a regular lane would, and the merge stands. Behavior lives in the shared scripts, so Codex gets it through the same skill text; no adapter work.

## Interfaces

- `plugins/sdlc-lite/scripts/tickets.py`
  - `EXTERNAL_RE`: `\s*external_branch\s*:\s*(\S+)\s*(?:#.*)?` (same shape as `CONFIG_RE`).
  - `external_branches(root) -> [str]`: branch names from `<root>/config`, in file order, deduplicated; `[]` when the file is missing.
  - `branch_tickets(root, branch) -> [(slug, meta)]`: ticket folders at `<branch>:<rel>` read from git objects with `load()`'s dir rules; anchor, `rel`, and `GIT_ENV_DROP` handling as in `worktree_pairs`; `[]` on any git failure, missing branch, or non-git root; a malformed handoff is skipped, never raised.
  - `id_floor(root)`: max over worktree roots and over `branch_tickets(root, b)` for every registered `b`.
  - `cmd_check`: appends `warning: external_branch <b> is not a local branch` (exit 0) per registered name without `refs/heads/<b>`.
  - Docstring: usage block gains the config line; the "Ids across git worktrees" paragraph gains the registered-branch sentence and drops "Branches not checked out in any worktree are not seen" for registered ones.
- `plugins/sdlc-lite/scripts/fanout.py`
  - Spec: `<lane>@<branch>=<id>[,<id>...]`; parse `rpartition('=')` for ids, then `partition('@')` for the branch. Lane name rules unchanged. `Lane.external` (branch name or `None`); `lane.branch` is the external branch, `lane.dir` is `None`.
  - Preflight (external): branch in `tickets.external_branches(root)` else refuse naming the line and the file; `refs/heads/<branch>` exists; not equal to the integration branch or any `<integration>-<lane>` of this run; no two lanes on one branch; tickets from `tickets.branch_tickets(root, branch)` with the same one-folder, not-done, once-across-lanes checks; handoff via `git cat-file -e <branch>:<rel>/<slug>/handoff.md`.
  - `print_plan`: `lane <name>: external branch <branch> (registered; no worktree, no driver)`.
  - `setup`: skips external lanes; the post-setup handoff check applies to regular lanes only.
  - `run_ticket`: external path enters at the merge lock: integration dirty check, `git merge --no-ff --no-edit -m "Merge <branch>: <id>" <branch>`, conflict → abort → `merge conflict`; when `HEAD == before` skip the gates; else gates as today; no `copytree` (no lane dir); close and `close <id>` commit as today. `run_lane` skips `wip_commit` when `lane.dir is None`.
  - `report`: `- Lane \`<name>\`: external branch \`<branch>\` at \`<sha>\``.
  - Docstring and `main()` usage line: the new form, preflight rules, per-ticket path, selftest cases.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: `argument-hint` adds `<lane>@<branch>=<ids>`; one paragraph on registration, no driver, never written, `merge conflict` means the outside agent merges integration themselves, and that an external lane appears in `report.md` but not in `board.py --lanes` (no worktree).
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: one sentence after the config-line sentence.
- `docs/references/sdlc-internals.md`: the `tickets.py` and `fanout.py` entries.
- Selftests: `fanout.py` case (a): registered `ext` branch made in a temporary checkout, `alpha@ext=T-0001,T-0002 --driver 'exit 9'`, gate present; asserts merged twice, one merge commit, one gate log per gate, no `fanout/test-alpha` ref, no `<lanes>/alpha` dir, `ext` tip unchanged, tickets done on integration, main clean; negative control: same repo without the config line refuses exit 2 and creates nothing; a mixed run with one regular lane still merges both. `tickets.py` case (b): `external_branch: ext`, T-0002 committed only on `ext` (not checked out), `new` in main mints T-0003; negative control without the line mints T-0002.

## Constraints and assumptions

- `git worktree add` refuses a branch already checked out elsewhere, so an external branch cannot get a lane worktree: verified by fanout.py preflight's own refusal text (lines 308-310) and git semantics | verified
- Merging an already-merged branch with `--no-ff` returns 0 and leaves HEAD unchanged, so gate-only-on-new-commit is a safe idempotence test: verified by a temp-repo probe (`Already up to date.`, rc=0, same HEAD)
- `git cat-file --batch` on `<branch>:<path>` yields `<sha> blob <size>\n<content>` and `<path> missing` for absent files, so a one-process branch read is possible: verified by the same probe
- `.sdlc/config` is a line file with one existing key, read by `config_numbered` and appended by `ensure_numbered_config`, so a second key fits without a parser change: verified by reading tickets.py lines 195-219
- `id_floor` is the single choke point for both `new` (line 593) and close's follow-up id (line 860): verified by grep
- fanout's close on the integration branch consults the merged `.sdlc/config`, so a follow-up filed there is also guarded: follows from the previous point | unverified until selftest
- An external lane's tickets may not exist in the local root, so resolution must read the branch, not `tickets.load(root)`: verified from the ticket goal text and preflight lines 253-262
- Nothing is fetched or pushed; only `refs/heads/<branch>` is consulted: by construction | unverified until selftest
- Codex parity needs no adapter change because the skill body and scripts are shared: verified by the Codex host line in skills/fanout/SKILL.md | not live-tested on Codex
- An outside agent's branch carries a `filer-L*.md` when its tickets should close plainly: unverified (evidence repo not present); without one the outcome is `merged, close refused`, same as today

## Rejected alternatives

- Reserved id ranges per owner: registration prevents the collision at mint time with one record and no id-space policy; ranges need allocation, exhaustion rules, and a second parser, and still miss an unregistered agent.
- Syncing the external branch (merge integration into it) as regular lanes do: writes a branch fanout does not own, usually one checked out in the outside agent's worktree; refused by git or corrupting to that worktree. Conflicts surface as `merge conflict` instead.
- A lane worktree for the external branch with no driver: adds a checkout that can fail (branch checked out elsewhere) for no gain; the merge, gates and close need only the ref.
- Registration-free fanout (`@<branch>` alone suffices, config only for `id_floor`): lets a branch join fanout while its ids stay unguarded; one record for both keeps the two tools in agreement.
- A `tickets.py register <branch>` subcommand: a hand-written line matches how `ticket_folders: numbered` is set today; a writer can come later if the line proves error-prone.
- Falling back to `close --reason` when an external ticket lacks a filer: changes the close contract for one lane kind; keeping the plain close keeps refusals uniform and visible in the report.

## Risks

- The evidence repo is absent, so how Codex lanes actually laid out their tickets (numbered folders, filer presence, branch names) is inferred; if those branches hold no filer, every external close refuses and the feature needs the `--reason` fallback after all.
- `id_floor` now runs git per `new`/`close` for each registered branch; with many registered branches and large roots this adds noticeable latency, and a stale registration (deleted branch) is only a `check` warning.
- The `merge conflict` outcome pushes reconciliation to the outside agent with no fanout-side help; if that is the common case, users will want the sync back in some ref-safe form (a temporary detached worktree on the branch tip, merging into a fanout-owned copy).
- Lane spec parsing on `@` and `=` assumes branch names contain no `=`; git allows it, so such a branch cannot be named in this form.
- `board.py --lanes` will not show external lanes; a user reading only the board misses them until they read `report.md`.
