<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add `plugins/sdlc-lite/scripts/lanes.py`. It is the one script that owns the lane lifecycle: open, close, sweep, list, check, port, archive and selftest. It carries the landed test and truth table from `docs/specs/sdlc-lite/lane-lifecycle.md` sections 7, 8.1 and 17 (ticket A as amended in 17.9). `check.sh` runs its selftest, and `docs/references/sdlc-internals.md` documents the script and its `.sdlc/config` keys.
guard timeout: 1900

## Step 1: lanes.py with the truth table, controls and mutants
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Create `plugins/sdlc-lite/scripts/lanes.py`. Use only the Python 3.9 standard library plus git. The host `python3` is 3.9.6 from CommandLineTools, so do not use `match` and do not use `X | Y` annotations that are evaluated at runtime. Import `tickets` from the same directory, as `budget.py`, `board.py`, `dispatch.py` and `fanout.py` do. Depends on: none.

#### Scope

Sources, in order of precedence: section 17 wins over sections 1 to 16 where they differ (17.10 lists each place), and 17.9 row A defines this ticket.

Built here:
- open, close, sweep (with the 17.6 rows, dry run by default, `--apply` acts), list, check, port, `archive list`, `archive restore` and selftest.
- The 17.1 names and clash rule.
- 17.2 archive refs as annotated tag objects.
- The 17.5 branch description.
- The section 6 `.lane.json` record.
- The section 8.1 claim rule.

Not built here:
- `git worktree lock` at open, unlock at close, the finished-agent rule and `extensions.worktreeConfig`. These are ticket A2 (17.3 and 17.4).
- `wait` (ticket F).
- Checks C7, C8 and C14.
- Any caller wiring in fanout.py, solo_run.py, tickets.py or dispatch.py (tickets B and C).

Sweep and list still read the lock from `git worktree list --porcelain`, because the handoff says to keep locked lanes and sweep.py skips them.

#### Settled interface

Tickets B and C import these names, so do not rename them.

**CLI.** Use argparse with `description=__doc__` and `RawDescriptionHelpFormatter`, so `--help` prints the docstring. Usage errors exit 2.
- `open <name> [--base REF] [--into REF] [--ticket ID]... [--kind fanout|integration|solo] [--title TEXT] [--root .sdlc] [--dry-run]`
- `close <name|path> [--into REF] [--discard] [--dry-run]`
- `sweep [--apply]`
- `list [--all] [--stale [--fail]] [--json]`
- `check [--warn]`
- `port [<path>]`
- `archive list [<branch>]`
- `archive restore <date>/<branch>`
- `selftest`

**Python API.** The functions are `open_lane`, `close_lane`, `sweep`, `list_lanes`, `still_open(root, ticket)`, `landed` and `config`.
- Do not name them `open` or `list`: a module-level `open` shadows the builtin inside the module.
- `open_lane` and `close_lane` each return a dict with keys `rc`, `message`, `lane`, `path` and `branch`.
- `sweep` returns a list of those dicts plus its rc.
- `still_open` returns the `lane still open: <path> (branch <b>, <reason>)` lines from section 8 and prints nothing.

**Docstring.** It holds four things:
- the kinds table (section 3, with the 17.1 names);
- the truth table (section 7 plus the 17.6 rows);
- the close steps (section 7 as amended by 17.2);
- the record fields (section 6).

Copy the outcome strings exactly, for example `closed <lane> (ancestor)`, `not a plugin lane: <path>` and `cannot decide: <reason>`.

**Config.** `config(toplevel)` reads these `.sdlc/config` lines. Blank lines and `#` lines are ignored, as `tickets.config_numbered` does.

| Key | Default and meaning |
|---|---|
| `lanes_root:` | `.worktrees`, relative to the main worktree's toplevel |
| `lane_into:` | none |
| `lane_setup:` | none |
| `lane_ports: <lo>-<hi>` | off when absent |
| `lane_stale_days:` | 10 |
| `lane_min_age_hours:` | 2 |
| `lane_keep:` | branch names |
| `lane_names:`, `lane_sweep:` | read and returned only; their behavior belongs to fanout (ticket B) |

**Record.**
- `.lane.json` sits at the tree root with the section 6 fields: `lane kind branch base base_sha into tickets port opened run_id setup`.
- Open adds `.lane.json` to `<git common dir>/info/exclude`.
- A host record is `<lanes root>/host/<name>.lane.json`. Ticket B writes it; this ticket reads it for ownership.

**Ownership (row 1).** A tree is a plugin lane when it has one of these:
- a `.lane.json` in the tree;
- a host record;
- a legacy fanout parent: its parent dir holds `merge.lock` and `logs/`.

For a legacy fanout lane, `into` is the branch checked out at `<that dir>/integration` when that tree exists, else main. The `integration` tree's own `into` is `lane_into:`, else main. Main is the branch of the first `git worktree list` entry. Every other tree is manual: `list --all` shows it, and nothing changes it.

**Names (17.1).**
- Kinds fanout and solo need `--ticket`. They get the branch `lane/<ticket>-<slug>` and the tree `<lanes root>/<ticket>-<slug>`.
- The slug is `<name>` lowercased, with every run of characters outside `[a-z0-9-]` replaced by `-`, cut to 40 characters.
- Kind integration uses `<name>` verbatim as its branch and `<lanes root>/<slug of name>` as its tree. A ticket is optional.

Before open creates anything, it runs three checks:
1. `git check-ref-format --branch`.
2. The clash test over `refs/heads`: a branch `lane` beside `lane/x`, and the reverse.
3. A refusal when the tree path is a lanes dir.

A refusal leaves no directory and no record.

`into` is `--into`, else the `--base` ref for kind fanout, else `lane_into:`, else main. `--base` defaults to main.

Open also does three things:
- It writes `branch.<b>.description` as `<ticket> <title>`, cut to 120 characters. The title comes from the local ticket's `title:`, else `--title`, else the id alone.
- When `lane_setup:` is set, it runs that command in the new tree. On failure it records `setup: failed rc=<n>` and keeps the lane.
- When `lane_ports:` is set, it picks the lowest port that no open record holds and that a `socket.bind` on 127.0.0.1 accepts, under `fcntl.flock` on `<lanes root>/lanes.lock`.

**Claim rule (8.1).**
- An id matching `T-\d+` is local. Resolve it through `tickets.ticket_dir` and `tickets.load` under `--root` (default `.sdlc`). Do not write a second front matter parser.
  - Found but with no non-empty `claimed_by:`: open refuses with `ticket <id> not claimed: set claimed_by: first`, exits 1 and creates nothing.
  - Not found while `--root` exists: open refuses with `no ticket <id>`.
- Any other id (`#123`, `123`, `ENG-45`), or a `T-` id when `--root` does not exist, prints `claim <id> in its tracker (assignee) before work; not checked here` and goes on. The branch leaf drops a leading `#`.
- After a close by row 9, row 10 or `pr merged`, close prints `ticket still open: <id>` for each local ticket in the record whose status is neither `done` nor `dropped`. The exit code does not change.

**Landed test.** Section 7 steps 1 to 4 name every ref in full. The 17.6 order is ancestor, then merged PR, then content.
- The PR check runs `gh pr list --state merged --head <b> --json headRefOid`, read-only. It is skipped when `gh` or a remote is absent.
- When `into` is a remote-tracking ref, its remote is fetched first.

**Truth table order** for close and sweep. The first match wins.

| Order | Row | Applies to | Outcome |
|---|---|---|---|
| 1 | rows 1 to 6 | close and sweep | as in section 7 |
| 2 | `locked` | sweep keeps; close refuses with the same reason in this ticket | `kept <lane>: locked: <reason>` |
| 3 | row 7 | sweep only | as in section 7 |
| 4 | row 8 | sweep only | reads `<toplevel>/.sdlc/runtime/prune.json`, the path in `dispatch.py` `PRUNE_REL` |
| 5 | `recent` | sweep only | tip younger than `lane_min_age_hours` |
| 6 | `in use` | sweep only | a `ps -axo pid=,command=` line, other than the script's own, names the lane path |
| 7 | row 9 | close and sweep | `closed <lane> (ancestor)` |
| 8 | `pr merged` | close and sweep | `closed <lane> (pr merged)` |
| 9 | row 10 | close and sweep | as in section 7 |
| 10 | row 11 | close and sweep | as in section 7 |
| 11 | row 12 | close `--discard` on rows 6, 7 and 11 | as in section 7 |

Sweep scope:
- Sweep keeps any branch listed in `lane_keep:`.
- Sweep acts only on plugin lanes.
- Unlike sweep.py, it deletes no branch that has no lane record, per the ownership rule in section 3.
- It never touches the main worktree or the current checkout.

**Close steps** (section 7 as amended by 17.2):
1. Write an annotated tag object. Its message holds the branch description `<ticket> <title>`, the reason (`ancestor`, `pr merged`, `content in <into>` or `discarded`), `into`, the tip sha and the UTC time.
   - Point the ref with `git update-ref refs/archive/<UTC date>/<branch> <tag> <zero sha>`, so the expected old value is zero.
   - If that fails, retry once with the leaf `<branch>.<sha7>`. A second failure stops the close with the branch intact.
   - Never create anything under `refs/tags`.
2. Copy the tree's untracked and ignored `.sdlc/` files to `<git common dir>/sdlc-lane-archive/<lane>/`. A failed write stops the close here.
3. Run `git worktree remove --force`.
4. Run `git update-ref -d refs/heads/<b> <sha>`.
5. Run `git worktree prune` and remove any host record. When a listener holds the lane's port, print `port <n> still listening (pid <p>)`.

Close writes no `closed-lanes.txt` and no `refs/sdlc/discarded/` (17.10).

`archive list` reads both tag and plain commit targets, because sweep.py wrote commit refs. `archive restore` runs `git branch <branch> <ref>` and refuses when the branch exists.

**check, list and port.**
- `check` runs C1 as amended in 17.7 (comparison by real path), plus the stray nested tree case from section 10, C2 and C3. With `--warn` it prints and exits 0.
- `list` shows each lane with its branch description and one of these states:
  - `open`, `closable`, `stale`, `locked`, `manual`;
  - `legacy`, for a plugin lane outside the `lane/`, `wave/` and `release/` namespaces.
- `list --stale` is C4 as amended: a locked stale lane shows `stale, locked`. `--json` prints one JSON array.
- `port` prints the port of the lane that holds the path. The path defaults to the cwd, and `port` walks up to the tree with `.lane.json`. It exits 1 when no lane holds the path.

#### Selftest contract

The verifier checks these exact labels.

Setup:
- Throwaway repos under `tempfile.TemporaryDirectory()`, as `gate_lock.py` (line 1297) and `fanout.py` (line 1641) do, with a local bare repo as `origin`.
- A stub `gh` on `PATH` for `pr merged`.
- `GIT_COMMITTER_DATE` to set commit age.
- A child process whose command line holds the lane path, for `in use`.
- `GIT_CONFIG_GLOBAL` set to an empty temp file, so the user's git config cannot leak in.
- The selftest never touches the repo it runs from.

It prints one line per passing case and exits 1 on the first failure, naming it. The required lines:
- `ok: row <n>: ...` for n from 1 to 12, plus `ok: row pr merged: ...`, `ok: row recent: ...`, `ok: row in use: ...` and `ok: row locked: ...`. Row 9 uses a real `--no-ff` merge and row 10 a real `git merge --squash`.
- `ok: C1: ...` through `ok: C6: ...`, plus `ok: C9: ...`, `ok: C10: ...` and `ok: C13: ...`: the section 10 and 17.7 controls, as amended.
- The 8.1 cases `ok: claim unclaimed: ...`, `ok: claim external: ...` and `ok: claim still open: ...`.
- `ok: still_open: ...` for the section 8 line.
- `ok: case pr ref: ...` (section 12): a local `pr/1` beside `refs/remotes/pr/1`, where close removes only the local branch.
- `ok: mutant <MARKER>: ...` for each marker in the table below.
- The last line is `ok: lanes.py selftest`.

Each mutant is a copy of lanes.py with the marked line replaced, and each must be observed failing its case. Follow `gate_lock.py`: its marker table is near line 966 and its mutant loop near lines 1301 to 1320.

| Marker | The mutant must fail because |
|---|---|
| `NO-RENAMES` | the rename case closes |
| `DIFF-FAIL` | a failed diff read as empty closes the row 5 case |
| `DIRTY-CHECK` | row 6 closes |
| `ABSENT-EQUAL` | the deleted-file case of row 11 closes |
| `ARCHIVE-ZERO` | two closes of one name on one date leave one ref |
| `ARCHIVE-STOP` | a forced ref directory clash deletes the branch |
| `NAME-FIRST` | a C9 refusal leaves a directory |
| `DESC-COPY` | the C13 tag message lacks the description |
| `REALPATH` | C1 passes a symlinked path |

#### Testing

The builder tests only through the selftest and through the CLI on throwaway repos. `hooks/block-stray-worktree.sh` denies role Bash text that runs `git worktree add`, so the selftest's own subprocess calls are the test path.

Validation scope:
- `lanes.py selftest`
- `lanes.py --help`
- a read-only `lanes.py list --all --json` on this checkout

Contract dependents: none yet. At base, `git grep -n lanes.py` finds only the design and ticket docs. Tickets B and C will import the API above.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/lanes.py selftest) && test "$(printf '%s\n' "$out" | tail -n1)" = "ok: lanes.py selftest"`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/lanes.py selftest) && for n in 1 2 3 4 5 6 7 8 9 10 11 12 "pr merged" recent "in use" locked; do printf '%s\n' "$out" | grep -qF "ok: row $n:" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/lanes.py selftest) && for c in C1 C2 C3 C4 C5 C6 C9 C10 C13 "claim unclaimed" "claim external" "claim still open" still_open "case pr ref"; do printf '%s\n' "$out" | grep -qF "ok: $c:" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/lanes.py selftest) && for m in NO-RENAMES DIFF-FAIL DIRTY-CHECK ABSENT-EQUAL ARCHIVE-ZERO ARCHIVE-STOP NAME-FIRST DESC-COPY REALPATH; do printf '%s\n' "$out" | grep -qF "ok: mutant $m:" || exit 1; done`
- (red) `h=$(python3 plugins/sdlc-lite/scripts/lanes.py --help) && for s in open close sweep list check port archive selftest; do printf '%s\n' "$h" | grep -qw "$s" || exit 1; done`
- (red) `h=$(python3 plugins/sdlc-lite/scripts/lanes.py --help) && for t in "closed <lane> (ancestor)" "not a plugin lane" "cannot decide" "rolling scratch" "runner tmp" "base_sha" "refs/archive/"; do printf '%s\n' "$h" | grep -qF "$t" || exit 1; done`
- (red) `python3 plugins/sdlc-lite/scripts/lanes.py list --all --json | python3 -c "import json,sys; json.load(sys.stdin)"`
- (red) `b=$(git worktree list --porcelain; git for-each-ref refs/heads refs/archive) && python3 plugins/sdlc-lite/scripts/lanes.py selftest >/dev/null && test "$b" = "$(git worktree list --porcelain; git for-each-ref refs/heads refs/archive)"`
- `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF plugins/sdlc-lite/scripts/lanes.py)"`

## Step 2: check.sh line, internals entry, gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Depends on: step 1.

1. In `plugins/sdlc-lite/scripts/check.sh`, add `python3 "$root/scripts/lanes.py" selftest || fail=1` among the other selftest lines, right after the `gate_lock.py` line. Also add `lanes.py` to the selftest list in the header comment. Only one writer at a time may change this file (handoff Context).
2. In `docs/references/sdlc-internals.md`, add a section headed ``## `scripts/lanes.py` ``. This matches the file's heading form, for example ``## `scripts/gate_lock.py` ``. Place it before the `scripts/fanout.py` section. The section:
   - states what the script owns;
   - says the kinds table, truth table, close steps and record fields live in the `lanes.py` docstring (`python3 plugins/sdlc-lite/scripts/lanes.py --help`), and copies no table (section 5);
   - names the importable API: `open_lane`, `close_lane`, `sweep`, `list_lanes` and `still_open`;
   - notes that ticket A2 adds the worktree lock and worktree config;
   - lists each `.sdlc/config` key in the form `<key>: <value>` with its default: `lanes_root:`, `lane_into:`, `lane_setup:`, `lane_ports:`, `lane_stale_days:`, `lane_min_age_hours:`, `lane_keep:`, `lane_names:` and `lane_sweep:` (fanout reads the last one, ticket B);
   - links the design `docs/specs/sdlc-lite/lane-lifecycle.md` with a relative link that resolves.
3. Run every gate:
   - `bash plugins/sdlc-lite/scripts/check.sh`, which runs `check.py`, `docs_check.py --root`, every selftest including the new line, shellcheck and plugin validate;
   - `python3 scripts/check-packaging.py`.

   Fix any red that step 1 or this step introduced, and only in lanes.py, check.sh or the internals entry. A gate already red at the build-start HEAD is reported as Status `inherited red`.

Left unchanged on purpose:
- The `## Lanes` section of `plugins/sdlc-lite/AGENTS.md` still names `~/.claude/lane/sweep.py` (line 43). Ticket G replaces it (17.9 row G).
- No `check.py` item is added. The ticket asks for none, and C14 lands with ticket G.
### Acceptance criteria
- (red) `grep -qF 'lanes.py" selftest' plugins/sdlc-lite/scripts/check.sh`
- (red) `grep -qE '^## .scripts/lanes\.py.$' docs/references/sdlc-internals.md`
- (red) `for k in lanes_root lane_into lane_setup lane_ports lane_stale_days lane_min_age_hours lane_keep lane_names lane_sweep; do grep -qF "$k:" docs/references/sdlc-internals.md || exit 1; done`
- (red) `grep -qF 'lanes.py --help' docs/references/sdlc-internals.md`
- `python3 scripts/check-packaging.py`
- `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/lanes.py -e plugins/sdlc-lite/scripts/check.sh -e docs/references/sdlc-internals.md)"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Assumptions
- Section 17 overrides sections 1 to 16, and 17.9 row A defines this ticket's scope together with the handoff's Do (`port`, C1 to C6 and the 8.1 rule): verified by `docs/specs/sdlc-lite/lane-lifecycle.md` lines 316 and 423 to 438, and by the handoff Intent.
- Setting the lock and worktree config belong to ticket A2, not this ticket: verified by 17.9 row A2. Sweep still skips a lock it reads, because the handoff says "keep dirty, locked, recent and unmerged lanes".
- `sweep` is a dry run by default and acts with `--apply`, and archive refs replace `closed-lanes.txt` and `refs/sdlc/discarded/`: verified by 17.6 and 17.10.
- The API uses `open_lane` and `list_lanes` instead of the design's loose `lanes.open` and `lanes.list`: settled here, because a module-level `open` shadows the builtin inside lanes.py. Tickets B and C import the names given in step 1's Do.
- The local ticket lookup reuses `tickets.ticket_dir` and `tickets.load`: verified at `plugins/sdlc-lite/scripts/tickets.py:345` and `:467`. The claim line format `claimed_by: <who> <date>` is verified at `.sdlc/AGENTS.md:49`.
- The host lane prune queue is `<project>/.sdlc/runtime/prune.json`: verified at `plugins/sdlc-lite/scripts/dispatch.py:879`.
- The selftest mutant mechanism follows `gate_lock.py`: verified at `plugins/sdlc-lite/scripts/gate_lock.py:966` and `:1301-1320`.
- `python3` on this host is 3.9: verified by the interpreter path in the probe output, `/Library/Developer/CommandLineTools/.../Python3.framework/Versions/3.9`.
- One probe run at HEAD 27130b4a, with `SDLC_BASE_SHA=HEAD`, verified the base state:
  - every `(red)` criterion in both steps is red for the right reason (lanes.py and the doc and check.sh entries do not exist yet);
  - both scope criteria, `check-packaging.py` and `git diff --check` are green.
- The 1900 s `check.sh` guard timeout is about three times the 615 s run recorded in `.sdlc/plan-reliability-docs/planner-L3.md`.

## Risks
- `check.sh` was not run while planning, because it takes about 10 minutes (rule 1). If it is red at base, step 2 reports `inherited red`.
- `pr merged` is proven only against a stub `gh`; the real `gh pr list` call has not been run here. The `in use` check depends on the `ps` output format, which is BSD on this host.
- Step 1 is one large file at L3: every subcommand plus about 30 selftest cases and 9 mutants. The design settles every edge. If the builder blocks on size, the replan should split open, port and check from close, sweep and archive rather than raise the level.
- Line 43 of `plugins/sdlc-lite/AGENTS.md` keeps pointing at `~/.claude/lane/sweep.py` until ticket G lands. This stale line is by design.
- Ticket B may need `open_lane` to adopt an existing legacy branch (`lane_names: legacy`). This ticket adds no `--branch` override, so B will have to extend the signature.
