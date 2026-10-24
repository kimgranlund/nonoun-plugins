# Lane lifecycle: open, close, wait

Status: design, not built, awaiting the maintainer's approval (ticket T-0422, 2026-10-10; git-native addendum T-0424, section 17, which wins where it differs). Version 0.2. Targets 0.22.4 unless the maintainer says otherwise. Nothing in section 13 is built by T-0422, and nothing in section 14 is removed by it. Evidence labels: [V] read in the file or command named, [I] inferred, [D] a decision this design makes for approval. Plugin paths are under `plugins/sdlc-lite/` unless they start with `docs/`.

## 1. Answer in one paragraph

Lanes pile up because nothing closes them, more than because of where they live. On 2026-10-10 this repo held 146 worktrees and 254 local branches; 142 of the 145 lane and host worktrees sit on a branch main already contains, and 251 of the 254 branches are ancestors of main [V]. The last step anyone owns is the `git merge --ff-only <integration>` in fanout step 5; fanout's contract says "the worktrees stay for inspection", and the host keeps a sub-agent worktree that has commits. This design adds one script, `scripts/lanes.py`, as the only home of the lane lifecycle. `open` makes a lane and writes its `.lane.json` (kind, branch, target, tickets, port). `close` removes a lane only when its tree is clean and its branch has landed, either as an ancestor of its target or with every changed file equal to the target's (which catches squash merges); it records the branch sha first and deletes the branch by its full ref name. `sweep` closes every landed plugin lane and leaves everything else. `list`, `check` and `port` report. fanout.py, solo_run.py, tickets.py and dispatch.py call it, and nothing else creates or removes a lane. Lanes stay under `.worktrees/` by default, because once lanes close the in-tree copies are bounded by `--max-lanes`; one config line moves them outside the checkout, as gen-ui-kit needs. `lanes.py wait` polls a PR and closes the lane on MERGED; it calls `gh pr merge --auto` only under a written opt-in, because that merge acts as the owner's account. The existing pile here was removed by a maintainer-authorized cleanup later the same day; section 14 keeps the proposal as the procedure for a consumer repo's pile and for what remains here.

## 2. Sources and measurements

Read for this design [V]: the gen-ui-kit spec and scripts attached to T-0422 (`SPEC.md`, `env.sh`, `lane-open.sh`, `lane-close.sh`, `lane-wait.sh`), [fanout.py](../../../plugins/sdlc-lite/scripts/fanout.py) (docstring for `run`, `prep`, `land`, `roll`; `HOST_WORKTREES`, `queue_prune`, `cmd_land`), [dispatch.py](../../../plugins/sdlc-lite/scripts/dispatch.py) (prune docstring, `prune_add`, `remove_tmp`, `strays`), [tickets.py](../../../plugins/sdlc-lite/scripts/tickets.py) (close usage), [solo_run.py](../../../plugins/sdlc-lite/scripts/solo_run.py) (`ensure_worktree`, `auto_worktree`), [gate_lock.py](../../../plugins/sdlc-lite/scripts/gate_lock.py) (docstring), [block-stray-worktree.sh](../../../plugins/sdlc-lite/hooks/block-stray-worktree.sh), [the hook reference](../../references/claude-hooks.md), [the fanout skill](../../../plugins/sdlc-lite/skills/fanout/SKILL.md), [Codex execution](../../references/codex-role-execution.md), and the [root guidance](../../../AGENTS.md) invariant to preserve unrelated worktrees, branches and stashes.

Measured on 2026-10-10 with read-only git commands in this repository, before the cleanup recorded in `docs/work/NOTES.md` (section 14) [V]:

- 146 worktrees: the main checkout; 124 under `.worktrees/fanout*/` (71 fanout lanes dirs); 15 host-owned trees under `.claude/worktrees/`; 6 made by hand under `.worktrees/` (`wave-b`, `ticket-stages-b`, `t0185`, `release-0.21.2`, `idle-host`, `haiku55`).
- Of the 124 fanout trees, 119 are clean on a branch main contains, 2 have uncommitted changes (`fanout-fleet/integration`, `fanout-fleet2/integration`), and 3 are clean on branches main lacks (`fanout-b5/ratelimit` on `batch5-ratelimit`, `fanout-b5/selfc` on `batch5-selfc`, `fanout-load/load` on `loadlanes-load`, tips 2026-10-06). Of the 15 host trees, 13 are clean and 2 have changes (`agent-a8796067dca9eb594`, `agent-ae9ec401bb7128396`), all on branches main contains. Of the 6 hand-made trees, 4 have changes (`idle-host`, `t0185`, `ticket-stages-b`, `wave-b`).
- 254 local branches: 146 checked out in a worktree, 108 with none; all 108 are ancestors of main.
- Disk: `du -sh` gives 4.5G for `.worktrees/` and 446M for the host-owned `.claude/worktrees/` (the ticket's 4.4 GB is an earlier reading).

Two gaps in the spec's `lane-close.sh`, reproduced in a throwaway repo [V]:

- With no `origin/main` ref, `git merge-base` fails, `git diff --name-only` exits 128 with an empty list, the per-file loop never runs, and the script goes on to remove the worktree and delete the branch. An unresolvable target must refuse.
- `git diff --name-only` detects renames by default, so a lane that renamed `old.txt` to `new.txt` lists only `new.txt`, and a target that still holds `old.txt` passes. `--no-renames` lists both paths.

Other facts the design leans on:

- fanout.py makes `<lanes-dir>/<lane>` on `<integration>-<lane>` and `<lanes-dir>/integration`, with the default lanes dir `<toplevel>/.worktrees/fanout`, and keeps them [V].
- The host makes its host-owned `.claude/worktrees/<name>` on `worktree-<name>` for `isolation: worktree`; prep names solo lanes `<id>-solo`, and land also resolves a host-named `worktree-agent-<hex>` branch through the agent id in `runs.jsonl` [V]; the printed `worktree-<id>-solo` land name, which is no branch, resolves to the host branch its host record names, else the one branch holding the ticket open (two are refused, T-0758). The plugin cannot choose that path [I: no host setting is known to this design].
- solo_run.py `--worktree NAME`, and its default when a second solo is live, makes `<toplevel>/.worktrees/<name>` on branch `<name>` and never removes it [V].
- run.sh and dispatch.py make detached `.worktrees/tmp/<role>-<pid>` trees and remove them; `reap-tmp-worktrees.sh` removes those of dead owners [V]. They are out of scope.
- `fanout.py land` queues a merged solo for `dispatch.py prune`; `prune --done` only edits the queue [V].
- gate_lock.py admits compute and browser weight per gate run, machine-wide, and has no port concept [V].
- block-stray-worktree.sh reads only Bash tool text from a role, and fanout.py's worktrees are not Bash calls [V]. Fanout skill step 5 has the parent run the `git worktree add -b` command prep prints for a `full` lane; a headless conductor (`SDLC_ROLE=conductor`, no `SDLC_TMP_WORKTREES`) is denied that command today [V, hook header].
- block-publish.sh blocks `gh pr` writes typed by a role [V], but cannot see a `gh` call made inside a script the role runs [I, by the same reading as the stray-worktree bypass note in the hook reference].

## 3. Worktree kinds

| Kind | Made by | Path | Branch | Target (`into`) | Closed by |
|---|---|---|---|---|---|
| fanout lane | fanout.py `run` setup; `lanes.py open` for a `full` lane from `prep` | `<lanes-dir>/<lane>` | `<integration>-<lane>` | the integration branch | fanout.py at the end of `run`, or after the lane's last `land` |
| integration | fanout.py `run`, `land` | `<lanes-dir>/integration` | `<integration>` | main, or `lane_into` | `lanes.py sweep`, run by fanout step 5 after the fast-forward and by the next `prep` or `run` |
| rolling scratch | fanout.py `roll` | `<lanes-dir>/rolling`, detached | none | none | `roll` itself, at its end |
| solo worktree | solo_run.py `--worktree`, or its second-live-solo default | `<lanes root>/<name>` | `<name>` | main, or `lane_into` | `lanes.py sweep` |
| host lane | the Claude host, `isolation: worktree` | `.claude/worktrees/<name>` (host-owned) | `worktree-<name>` | the integration branch it landed in | `dispatch.py prune --done <name>`; `sweep` never closes an `agent-*` tree (T-0564) |
| runner tmp | run.sh, dispatch.py | `<worktree root>/tmp/<name>`, the sibling root (T-0563; the legacy `.claude/worktrees/tmp/` and `.worktrees/tmp/` are read for one release), detached | none | none | unchanged: run.sh EXIT, `remove_tmp`, `reap-tmp-worktrees.sh`, the `wtroot.py` sweep |
| manual | a person | anywhere | any | none | the person; listed, never touched |

The first five kinds are plugin lanes. Ownership is what lets `close` and `sweep` act on a tree: a `.lane.json` in it (written by `open`), a host record under `<lanes root>/host/` (written by `prep`, section 6), or, for trees made before this build, membership in a fanout lanes dir (a directory holding `merge.lock` and `logs/`), or a host tree whose branch `fanout.py land` resolved to a ticket. Everything else is manual, which keeps the root invariant that unrelated worktrees, branches and stashes are preserved [D]. After the build this table lives in the `lanes.py` docstring, and this section points there.

## 4. Where lanes live (item 1)

Decision [D]: lanes stay inside the checkout by default, under one lanes root, and a repo moves the root outside with `lanes_root: <path>` in `.sdlc/config` (relative to the toplevel; a bare clone such as gen-ui-kit's needs no line since T-0561: the default resolves to `<bare parent>/lanes`, outside every lane). Reasons:

- The pile is a closing problem. With close and sweep, a run keeps at most `--max-lanes` lane copies (default 4, hard cap 16) plus one integration tree, so the 440-copy walk the spec describes does not recur.
- A session sandbox may not write outside its workspace. Codex headless conductors run inside their workspace sandbox [V, Codex execution]; making `../<repo>-lanes` from there is expected to fail [I]. Inside is the setting that works on both hosts.
- The default must not create a directory beside the user's checkout unasked.
- The host-owned `.claude/worktrees/` is inside the checkout whatever the plugin does; SDLC Lite lanes no longer are (T-0563).

What changes:

- Lanes root: `lanes_root:` defaults to the sibling `<main checkout parent>/<repo>.worktrees` (T-0563; the legacy `.claude/worktrees` of 0.23 and `.worktrees` before it are still read for one release and moved by `scripts/migrate-worktrees.sh`). With no line the default is `wtroot.py root`: a `worktree_root:` line, else the sibling root, else for a bare clone `<bare parent>/lanes` (T-0561). fanout's default `--lanes-dir` becomes `<lanes root>/fanout` (the same path as today for a repo without the line), and solo_run's `--worktree` tree goes to `<lanes root>/<name>`. Runner tmp is `<wtroot.py root>/tmp`: `run.sh` sets `SDLC_TMP_WORKTREES` under it, and both role hooks derive the sub-agent prefix from the same `wtroot.py root` (T-0561).
- Ignore rules: the legacy `.worktrees/` and the host-owned `.claude/worktrees/` stay gitignored, and `prep` refuses otherwise. A lanes root outside the toplevel needs no ignore entry, as for `--lanes-dir` today. `open` adds `.lane.json` to `<git common dir>/info/exclude`, as the spec does, so no tracked file changes and a lane's `git add -A` never stages it.
- Watcher exclusions: not needed for the sibling root, which is outside the repo (T-0563); the legacy and host-owned `.claude/worktrees/` keep theirs while they hold trees. An outside root needs `lane_setup:` (section 11).
- Hook: block-stray-worktree.sh keeps its logic, because lanes are made by scripts and the hook governs role Bash text. Its deny message adds that a lane comes from `lanes.py open`. fanout `prep` prints a `lanes.py open` command for a `full` lane instead of the raw `git worktree add -b`, so a headless conductor can make that lane. The hook reference gets one sentence.

## 5. One home: `scripts/lanes.py` (item 2)

Decision [D]: one new script, imported by fanout.py, solo_run.py, tickets.py, dispatch.py and board.py:

```
lanes.py open <name> [--base REF] [--into REF] [--ticket T-NNNN]... [--kind fanout|integration|solo] [--dry-run]
lanes.py close <name|path> [--into REF] [--discard] [--dry-run]
lanes.py sweep [--dry-run]
lanes.py wait <name> <pr> [--timeout SECS]
lanes.py list [--all] [--stale [--fail]] [--json]
lanes.py check [--warn]
lanes.py port [<path>]
lanes.py selftest
```

- Not three skills, as the spec has them: open, close and wait are deterministic, and a skill would wrap a script in prose that copies its rules. The fanout skill gains one paragraph and a `lanes.py` allowed-tools entry.
- Not fanout.py subcommands: fanout.py is 3808 lines and its docstring is the merge contract; tickets.py, dispatch.py and board.py need the lane lookup without importing the fanout runner; solo_run.py lanes have no fanout run at all.
- Not a port of the shell scripts: `env.sh` hard-codes gen-ui-kit's root, archive, repo, `gh` path and a Node binary from an npx cache, and the scripts parse JSON with grep and take no lock. The design keeps their behavior, not their text.
- The kinds table, the truth table and the record fields live in the `lanes.py` docstring; the internals reference, the fanout skill and this design point there and copy no table [D].
- Codex: lanes.py is plain Python and git, so a Codex conductor runs the same commands. Host lanes are a Claude-only kind.

## 6. The lane record and ports (item 4)

`.lane.json` sits at the lane tree's root, is written by `open`, and is read only through lanes.py:

```
{"lane": "ll", "kind": "fanout", "branch": "wave26-ll", "base": "wave26", "base_sha": "<sha>", "into": "wave26",
 "tickets": ["T-0422"], "port": 7412, "opened": "2026-10-10T13:04:00Z", "run_id": "fanout-<hex>", "setup": "ok"}
```

`into` is the ref the landed test reads: for a fanout lane its integration branch; for an integration tree the main branch (found as `roll` finds it) or `lane_into:` from `.sdlc/config` in a repo that lands through PRs (`origin/main`); for a solo worktree main or `lane_into`. A host lane has no tree before the spawn, so `prep` writes its record to `<lanes root>/host/<name>.lane.json` with the same fields.

Ports are off unless `.sdlc/config` has `lane_ports: 7400-7699`; the plugin starts no server and most repos need none [D]. With the line, `open` picks the lowest port in the range that no open lane record holds and that a `socket.bind` on 127.0.0.1 accepts (no `lsof` dependency), under an `fcntl.flock` on `<lanes root>/lanes.lock`. Two concurrent opens therefore cannot pick one port; the spec's script has no lock, so its two-lanes-on-7431 collision can recur. The port reaches the lane's processes three ways, all from the record: `SDLC_LANE_PORT` in fanout's driver and gate environment, a `Port: <n>` line in the solo brief, and `lanes.py port`, which prints the port of the lane holding a path (default the cwd) and is the one reader a probe calls. A probe never parses the file and never picks a port.

Relation to gate_lock: none in code [D]. gate_lock grants compute and browser weight to one gate run, machine-wide; a port is an identity a lane holds for its life. A gate that starts a dev server on `$SDLC_LANE_PORT` runs inside its grant's process group, and gate_lock drains that group at release, which frees the port. A server a solo starts outside a gate is not drained: `close` then prints `port <n> still listening (pid <p>)` and stops nothing, as the pattern-kill rule asks.

Across repos: records are per repository, and the bind test skips any port in use. Two repos with ports on set disjoint ranges; a machine-wide port ledger waits for an observed cross-repo collision [D].

## 7. Close: the landed test and the truth table (item 3)

The landed test names every ref in full (`refs/heads/<b>`, `refs/remotes/<r>/<b>`), so a local branch named like a remote-tracking ref (`pr/4297`) is never ambiguous:

1. `into` must resolve to a commit, else `cannot decide`. When `into` is a remote-tracking ref, its remote is fetched first; a failed fetch with a ref that still resolves goes on against the stale ref, which can only make the test stricter, and says so.
2. Ancestor: `git merge-base --is-ancestor refs/heads/<b> <into>` exit 0 means landed (`ancestor`). This is the fanout path: a lane merges `--no-ff` into the integration branch, and main moves by `--ff-only`.
3. Content: else `m = git merge-base <into> refs/heads/<b>` and `git diff --no-renames --name-only m refs/heads/<b>`; either command failing means `cannot decide`, never an empty list. Landed (`content`) when every listed path has the same blob id at `refs/heads/<b>:<path>` and `<into>:<path>`, absent on both counting as equal. This catches a squash merge, one made on another host, and a lane whose content reached main through `roll`.
4. Else not landed, naming the first path that differs.

Negative controls, in `lanes.py selftest`, each also run against a mutant copy that drops the guard and must then fail the case, as gate_lock's selftest does: a lane with one change the target lacks refuses; a lane that renamed a file whose old path the target keeps refuses (the mutant without `--no-renames` closes it); an unresolvable target refuses (the mutant that reads a failed diff as empty closes it, which is the shell script's behavior); a lane that deleted a file the target keeps refuses. Positive cases: a real `git merge --squash` on the target closes by content, and a `--no-ff` merge closes by ancestry.

Truth table for `close` and `sweep`; the first matching row wins:

| # | State | Outcome | Exit | Changes |
|---|---|---|---|---|
| 1 | Not a plugin lane (section 3) | `not a plugin lane: <path>` | 2 | nothing |
| 2 | Neither tree nor branch exists | `no lane <name>` | 1 | nothing |
| 3 | The branch is checked out in another worktree | `branch <b> checked out at <path>` | 1 | nothing |
| 4 | An integration tree with an open lane whose `into` is its branch | `lanes still open into <b>: <names>` | 1 | nothing |
| 5 | `into` does not resolve, or a git read fails | `cannot decide: <reason>` | 1 | nothing |
| 6 | Tracked changes, or untracked files outside `.sdlc/` and `.lane.json`, and no `--discard` | `uncommitted changes in <lane>: <first path>` | 1 | nothing |
| 7 | `sweep` only: no commit since `base_sha` | kept, `no commits` | 0 | nothing |
| 8 | `sweep` only: a host lane queued in `prune.json` less than 6 hours ago | kept, `agent not pruned` | 0 | nothing |
| 9 | Landed by ancestry | `closed <lane> (ancestor)` | 0 | record, archive, remove, delete, prune |
| 10 | Landed by content | `closed <lane> (content in <into>)` | 0 | as row 9 |
| 11 | Not landed, no `--discard` | `not landed in <into>: first <path>; merge it or --discard` | 1 | nothing |
| 12 | `--discard` on row 6, 7 or 11 | `closed <lane> (discarded <sha>)` | 0 | as row 9, plus `refs/sdlc/discarded/<b>` kept |

Rows 1 to 5 refuse even with `--discard`. Row 7 keeps a lane `prep` just made for a solo about to start; an explicit `close` of an empty lane goes on to row 9. The 6 hours in row 8 is the TTL of solo_run's live marker. In `sweep`, a refusing row prints `kept <lane>: <outcome>` and the sweep goes on; its exit is 0 unless a git command failed.

A close (rows 9, 10, 12) runs these steps in order, so a failure leaves a lane that a rerun closes:

1. Append `<utc> <branch> <sha> <reason> <into>` to `<lanes root>/closed-lanes.txt`. For `--discard`, also `git update-ref refs/sdlc/discarded/<b> <sha>`, so the commits survive gc (a deleted branch's objects are otherwise pruned after the grace period) and `git branch` does not list them.
2. Copy the tree's untracked and ignored `.sdlc/` files, which the branch does not hold, to `<lanes root>/archive/<lane>/`. A failed write stops the close here.
3. `git worktree remove --force <path>`; a missing tree skips this step.
4. `git update-ref -d refs/heads/<b> <sha>`: it deletes by full name, and only while the branch still points at the sha the test read, so a branch that moved since the test fails here and the close says so.
5. `git worktree prune`; remove a host record from `<lanes root>/host/`; print the port line when a listener holds the lane's port.

## 8. Who calls close, and `lane still open` (item 5)

- `fanout.py run`: setup opens each lane through `lanes.open`. After the run, every lane whose tickets all merged is closed. A lane that stopped keeps its tree and WIP commit for inspection, and the report adds `lane still open: <path> (<outcome>)`. The integration tree stays until main contains it, and the report says so.
- `fanout.py prep` and `run` begin with `lanes.sweep()`, which is the spec's "reaped on the next conductor run". `lane_sweep: off` in `.sdlc/config` turns it off [D]. Before touching a fanout lanes dir, `sweep` takes that dir's `merge.lock`, so it never closes a lane a `land` is merging.
- `fanout.py land`: on `merged` it queues the solo for prune as today and leaves the host lane open, because the sub-agent stays alive and the parent may still message it until it is stopped. A `full` lane closes after its last ticket lands. Fanout step 5 runs `lanes.py sweep` right after the user-approved `git merge --ff-only`, which closes the integration tree and every landed lane.
- `fanout.py roll`: removes `<lanes-dir>/rolling`, detached and without a branch, at the end of each roll.
- `dispatch.py prune --done <name>`: after the parent stopped the agent, closes that agent's host lane through `lanes.close` and prints `closed lane <path> (<reason>)` or `lane still open: <path> (<reason>)`. The prune listing adds `; lane open <path>` to an entry whose lane exists. This is the spec's "prune and close run together", ordered stop first, then remove [D].
- `tickets.py close`: after a successful close, prints one `lane still open: <path> (branch <b>, <reason>)` line per plugin lane whose record lists the ticket or whose host name is `<id>-solo`. Its exit code is unchanged. Inside `fanout.py land` the line names the host lane awaiting prune, which is the true state.
- `solo_run.py --worktree`: makes its tree through `lanes.open` with kind `solo`.

`lanes.still_open(root, ticket)` builds the line; the callers only print it. steps.py does not change: `tickets.py close` is the one place a ticket closes.

### 8.1 Every lane has a ticket (tracker-agnostic) [D]

The lane lifecycle skills and commands carry one directive, whatever tracker the repo uses (local `.sdlc` tickets, GitHub Issues, or Linear): no ticket, no lane.

| Phase | Directive |
|---|---|
| Open | Claim the existing ticket, or create one if none exists, before any lane, branch or worktree. A claim names who holds it and when: `claimed_by: <who> <date>` for local tickets, the assignee on GitHub or Linear. The branch carries the ticket id (`lane/<ticket>-<slug>`). |
| Work | One lane per ticket. A new idea becomes a new ticket, not a larger lane. |
| Finish | In a repo that uses pull requests, open a PR that links the ticket (`Closes #123`, `Fixes ENG-45`, or the local id). A repo with no PR flow merges the lane directly. |
| Close | After the work is merged, close the ticket with a one-line result and a link to the PR or commit, then close the lane (archive ref first). An unmerged lane keeps its ticket open. |
| Detect | Use the tracker the repo already has (`.sdlc/`, a Linear config, a GitHub remote). Never create a second tracker. With none, use local `.sdlc` tickets. |

The rule in four words: no ticket, no lane; no merge, no close. `lane-open` refuses a lane with no claimed ticket; `lane-close` prints `ticket still open` when it closes a merged lane whose ticket is open. Local tickets are enforced by `tickets.py` and `lanes.py`; for GitHub and Linear the skills carry the directive and call the repo's own CLI or MCP tool (`gh issue`, `gh pr`, the Linear tool) when present, and say `ticket not updated: <why>` when absent. This section adds scope to T-0422; the GitHub and Linear half is directive text in the skills only, with no new script.

### 8.2 Ticket fields on Linear and GitHub

How the local ticket fields map onto each tracker. This is mapping text only: no integration is built.

| Field | Linear | GitHub |
|---|---|---|
| status proposed | Backlog | open, label `status:proposed` |
| status ready | Todo | open, label `status:ready` |
| status claimed | In Progress, with the assignee | open, the assignee, label `status:claimed` |
| status paused | a `Paused` state when the team has one, else Backlog with label `paused` | open, label `status:paused`, the `paused_reason` as a comment |
| status blocked | label `blocked` (Linear has no default blocked state) | open, label `status:blocked` |
| status done | Done | closed as completed |
| status dropped | Canceled | closed as not planned |
| area | a team when the workspace has one team per area, else label `area:<name>` | label `area:<name>` |
| size L1 to L4 | estimate 1 to 4 on the linear scale | labels `size:L1` to `size:L4` |

L5 is reserved and unmapped. No migration: existing tickets need no migration, an absent `area` is valid and every existing status stays valid.

## 9. Wait and auto-merge

`lanes.py wait <name> <pr>` polls `gh pr view <pr> --json state` every 45 seconds up to `--timeout` (default 6 hours; the spec's loop has no limit and spins forever on a `gh` error). `MERGED` runs `close` with `into` the PR's base as a fetched remote-tracking ref, which closes by content after a squash merge. `CLOSED` prints `PR <n> closed, lane <name> left open` and exits 1. A timeout exits 3 and leaves the lane.

It calls `gh pr merge <pr> --auto --<method>` only when the caller passes `--auto-merge <method>` for that PR (17.8, which replaces the blanket `lane_auto_merge: on` of the first draft) [D]. That merge runs as the account `gh` is logged in as, the owner's, so it is a publish action: the flag is the owner's per-PR opt-in, and it is never a default. `wait` also refuses the merge call, and says why, when `SDLC_ROLE` is set or the caller is a role sub-agent, because block-publish.sh would not see a `gh` call made inside this script. Without the flag, `wait` only watches a PR a person merges.

## 10. Checks, each with a negative control (item 6)

Each check is a `lanes.py` mode with selftest cases in a throwaway repo; the selftest joins `check.sh` with ticket A.

| Check | Fails when | Negative control |
|---|---|---|
| C1 `check`, placement | a worktree nested inside another worktree's toplevel that is not a plugin lane, runner tmp or host tree; or a plugin lane outside the lanes root | `git worktree add -b x <top>/stray` exits 1 naming `stray`; a lane from `open` exits 0; a lane record under `<top>/elsewhere` exits 1 |
| C2 `check`, ports | two open lane records hold one port, or a port lies outside `lane_ports` | two hand-written records on 7400 exit 1; after one closes, exit 0 |
| C3 `check`, record drift | a record's branch or path disagrees with `git worktree list` | a record edited to another branch exits 1 |
| C4 `list --stale` | a report, exit 0 (`--fail` exits 1 when it lists any): a plugin lane landed but open (`closable`), or not landed with its tip older than `lane_stale_days` (default 10) and, where `gh` and a remote exist, no open PR (`stale`) | a lane whose tip is backdated 11 days is listed and one at 9 days is not; a landed lane of any age is `closable` |
| C5 `sweep`, scope | it closes a manual tree, an unlanded lane, an empty lane or a dirty one | a repo holding one of each beside one landed lane: after `sweep` only the landed lane is gone, and `closed-lanes.txt` gained one line |
| C6 `close`, truth table | any row of section 7 gives another outcome | one case per row; rows 5, 6 and 11 also run against the mutants of section 7 |
| C7 hook | a headless conductor running `lanes.py open` is denied, or the raw `git worktree add -b` that prep used to print passes | two cases in `hook-selftest.sh` |
| C8 fleet, `lane_pile` | a fingerprint whose closable plus stale lanes exceed 8 (twice the default `--max-lanes`) gives no finding | 9 gives one finding, 8 gives none |

The spec's rule "no lane worktree under any checkout" follows from C1 when `lanes_root` is outside the toplevel. Before the cleanup in section 14, C1 would have failed here on the six hand-made trees; after it, the trees left are fanout lanes, so ticket I can make C1 gate `check.sh` once ticket A exists. `board.py --lanes` shows each lane's state (`open`, `closable`, `stale`, `manual`) from `lanes.list`; the spec's "list stale lanes in board and fleet-retro" is C4 plus C8.

## 11. Consumer repos (item 7)

A conductor must change nothing to upgrade: the defaults keep lanes where fanout puts them today, the ignore and watcher rules are the ones prep already requires, and `sweep` closes only plugin lanes that landed.

Should do:

- A repo that lands through PRs adds `lane_into: origin/<default branch>`. Without it, the test reads the local main, and a squash-merged lane stays open until main is pulled.
- Run `lanes.py list --all` once after upgrading, and close any old pile with the maintainer's go, as in section 14.

Optional, each one `.sdlc/config` line:

- `lanes_root: ../lanes` moves lanes outside the checkout. Then also add `lane_setup: <cmd>`, which `open` runs in the new tree, because a sibling lane borrows no `node_modules`. A failed setup keeps the lane and records `setup: failed rc=<n>` in the record and the solo brief.
- `lane_ports: <lo>-<hi>` for lanes that run a dev server or browser probe; gates read `$SDLC_LANE_PORT` or call `lanes.py port`.
- `lane_stale_days: <n>` and `lane_sweep: off`.
- No config line for auto-merge: it is a per-PR `--auto-merge <method>` flag (section 9, 17.8).

The plugin pins no Node binary: `lane_setup` is the repo's own command and selects Node through the repo's version manager (`fnm exec --using .nvmrc`, `mise exec`, or a `.nvmrc`-aware script). For gen-ui-kit the lines would be `lane_ports: 7400-7699`, `lane_into: origin/main`, and `lane_setup:` running `pnpm install` then `node scripts/dev/bootstrap-worktree.mjs` under their Node 22 lookup, which replaces `~/.claude/lane/`; its lanes root is the bare-clone default (T-0561), so it sets no `lanes_root:`.

## 12. Risks and known gaps (item 8)

- `gh pr merge --auto --<method>` worked in gen-ui-kit's `lane-wait` (PR 425, per T-0424) but lanes.py's own call is unrun, and the merge acts as the owner's account. Mitigation: off by default, a per-PR flag, refused inside a role (section 9, 17.8). Authorization note: auto-merge acts under the owner account, so it needs the owner's per-PR flag and is never default; its live run on a throwaway GitHub repository needs the maintainer's authorization (ticket F), and until then the merge call is reported unverified.
- The hard-coded Node path in `env.sh` is not ported; `lane_setup` is the repo's own command (section 11).
- The branch-name-equals-remote-ref crash in `reap-branches.mjs` (`pr/4297` beside `refs/remotes/pr/4297`): lanes.py names every ref in full and deletes with `update-ref -d refs/heads/<b> <sha>`. A selftest case makes a local `pr/1` beside `refs/remotes/pr/1` and closes only the local branch.
- Two more gaps found here, both reproduced [V]: the shell close passes when its target does not resolve, and rename detection hides a deleted path. Row 5 and test step 3 cover them.
- The host may expect its host-owned `.claude/worktrees/<name>` to exist after its agent stops [I]. Closing only after `prune --done`, once the agent is stopped, limits that; live-run step 5 checks it.
- `sweep` deletes branches without a question. It touches only plugin lanes that are clean and landed, records each sha first, and `lane_sweep: off` disables it; any uncommitted file keeps a lane.
- An outside `lanes_root` may fail under a write-restricted sandbox [I]; `open` then refuses naming the path, and the default stays inside.
- `sweep` during a `run`: `close` refuses a branch that moved (step 4) and an integration tree with open lanes (row 4), and `sweep` holds the lanes dir's `merge.lock` while it acts there.

## 13. The build, split into tickets (item 9)

Filed after the maintainer approves this design, in this order. `check.sh`, `check.py` and `fanout.py` are shared hot files: one writer at a time, one lane.

| # | Ticket | Size | Files changed | Done when |
|---|---|---|---|---|
| A | `lanes.py` core | L3 | new `scripts/lanes.py` (open, close, sweep, list, check, port, selftest; the kinds table, truth table and record fields in its docstring); `scripts/check.sh` (the selftest line); `docs/references/sdlc-internals.md` (an entry pointing at the docstring, and the new `.sdlc/config` keys beside `hash_bound`) | `(red)` `python3 plugins/sdlc-lite/scripts/lanes.py selftest` fails now (no file); after, it exits 0 with one case per truth-table row and per C1 to C6 control, each mutant observed failing; `check.sh` exits 0 |
| B | fanout and solo_run use lanes | L3 | `scripts/fanout.py` (open in setup, close merged lanes, sweep at start, `lane still open` report lines, `SDLC_LANE_PORT`, `prep` prints `lanes.py open` for a `full` lane and writes the host record, `roll` removes its scratch, docstring and selftest cases); `scripts/solo_run.py` (`ensure_worktree` through `lanes.open`, selftest); `skills/fanout/SKILL.md` (a lifecycle paragraph replaces "Lane worktrees stay after the run", step 5 runs `lanes.py sweep`, allowed-tools; the `check.py` phrase list kept the then-current, now legacy `.claude/worktrees/`) | `(red)` a fanout selftest case that expects a merged lane's tree gone after `run` fails now; after, `fanout.py selftest` and `solo_run.py selftest` exit 0, and a stopped lane stays with its report line |
| C | close and prune report lanes | L2 | `scripts/tickets.py` (close prints `lane still open`); `scripts/dispatch.py` (`prune --done` closes the host lane, the listing names it); both selftests | `(red)` closing a ticket with an open lane prints no `lane still open` line now; after, `tickets.py selftest` and `dispatch.py selftest` exit 0 |
| D | hook message | L1 | `hooks/block-stray-worktree.sh` (message only), `scripts/hook-selftest.sh` (C7), `docs/references/claude-hooks.md` (one sentence) | `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0 with both C7 cases |
| E | board and fleet | L2 | `scripts/board.py` (`--lanes` state cell), `scripts/fleet_collect.py` (lane counts), `scripts/fleet_detect.py` (`lane_pile`, C8), their selftests; `skills/board/SKILL.md` if it lists the `--lanes` columns | each selftest exits 0 with the C8 control |
| F | `lanes.py wait` | L2 | `scripts/lanes.py` (wait, the opt-in, the role refusal, selftest with a stub `gh` on PATH) | the selftest covers MERGED, CLOSED, timeout, opt-in off (no merge call) and the role refusal; the live GitHub run stays unverified until authorized |
| G | docs | L1 | this file (status built); `docs/specs/sdlc-lite/README.md`; `docs/README.md`; `plugins/sdlc-lite/AGENTS.md` (the fanout worktrees invariant names `lanes.py`) | `docs_check.py` and `check.py` exit 0 |
| H | what remains of this repo's pile | L1 | no tracked file but the new `docs/reports/<date>-lane-cleanup.md`; re-measures with `lanes.py list --all` and runs section 14 only for what the maintainer approves | the report's counts; nothing removed outside the approved classes |
| I | gate C1 here | L1 | `scripts/check.sh` (`lanes.py check` against this repo) | `check.sh` exits 0, and exits 1 with a stray nested tree added (control) |

Order: A; D at any time; then B, C, E, F, G; H and I after A, H only with the maintainer's go. Not changed: model and effort rows, `levels.json`, `models.json`, `results.py`, `steps.py`, `gate_lock.py`, `run.sh`, `reap-tmp-worktrees.sh`, the host's worktree placement, any version number. Sizes are estimates.

### 13.1 Live-run plan on a throwaway repo

A repo under `mktemp -d` with a local bare repo as `origin` (no network) and the plugin from this checkout. Results go to `docs/reports/<date>-lane-lifecycle-live-run.md`; a step that cannot run is reported unverified, not substituted.

1. Two `lanes.py open` calls in parallel with `lane_ports` on: distinct ports, a record in each, `.lane.json` in `info/exclude`, `git status` clean in both.
2. `fanout.py run` with a stub driver over two lanes and a gate that reads `$SDLC_LANE_PORT`, one lane made to stop: merged lanes are gone after the run, the stopped lane stays with its `lane still open` line; after `git merge --ff-only <integration>` in main, `lanes.py sweep` closes the integration tree, and `git worktree list` shows only main and the stopped lane.
3. Squash: push a lane branch to the bare origin, `git merge --squash` it into main there, set `lane_into: origin/main`, and `close` closes by content. Negative: one more commit on another lane; `close` refuses, and its tree and branch remain.
4. Missing target (`--into refs/remotes/origin/nope`) and the rename case both refuse.
5. Claude host: one live L1 ticket through `fanout.py prep` and `land` in an interactive session. After `merged`, `tickets.py close` printed the `lane still open` line for the host tree; after TaskStop and `dispatch.py prune --done`, the tree and branch are gone and the session shows no host error.
6. `--discard` on an unlanded lane: the branch is gone, `refs/sdlc/discarded/<b>` exists, and `git branch <b> <sha>` with the sha from `closed-lanes.txt` recreates it.
7. `wait` against a stub `gh` (MERGED; CLOSED; an error, then MERGED). A real GitHub PR only with the maintainer's authorization.
8. Codex: `open`, `close` and `sweep` from a Codex headless conductor inside its workspace sandbox, default lanes root.

## 14. Cleanup proposal for this repo's pile (item 10)

Update, 2026-10-10, after this section was written: a maintainer-authorized cleanup removed 145 worktrees and 248 merged local branches here, logging each branch name and sha in `~/.claude/lane/closed-lanes-sdlc-lite.txt` and archiving the untracked records of the dirty trees in `~/.claude/lane/archive-sdlc-lite/` (`docs/work/NOTES.md`, main commit c5644268). It kept the running lane (`wave26`, `wave26-ll`) and two unmerged branches whose work conflicts with main (`batch5-ratelimit` for T-0301, `loadlanes-load` for T-0317); `batch5-selfc` went, its content being on main. When this design was verified the repo held 5 worktrees and 5 branches [V]. The table and steps below are the proposal as written against the state in section 2; they stay as the procedure for a consumer repo's pile, and here ticket H covers only what remains.

A proposal only. Nothing below runs without the maintainer's go, given class by class; T-0422 removes nothing. Counts are from section 2.

| Class | Count | Proposed action |
|---|---|---|
| Fanout lane and integration trees, clean, branch in main | 119 | close through `lanes.py sweep` once ticket A exists; they are plugin lanes by their lanes dir |
| Fanout integration trees with changes (`fanout-fleet`, `fanout-fleet2`) | 2 | show `git status` and the diff; `--discard` only on the maintainer's word |
| Fanout trees on branches main lacks (`batch5-ratelimit`, `batch5-selfc`, `loadlanes-load`) | 3 | keep; if dropped, `--discard`, which records the sha and keeps `refs/sdlc/discarded/<b>` |
| Host trees, clean, branch in main | 13 | close after confirming no live sub-agent holds them |
| Host trees with changes (`agent-a8796067dca9eb594`, `agent-ae9ec401bb7128396`) | 2 | show the diff; the maintainer decides |
| Hand-made trees (`wave-b`, `ticket-stages-b`, `t0185`, `release-0.21.2`, `idle-host`, `haiku55`; four dirty) | 6 | listed only; the maintainer keeps or removes them by hand |
| Branches with no worktree, all in main | 108 | delete in one batch on the maintainer's word, each sha appended to `closed-lanes.txt` first |

Steps:

1. Inventory, read only: `lanes.py list --all --json` after ticket A (until then, the git commands behind section 2), with counts and disk per class.
2. Stop check: no fanout run active (no `merge.lock` held, no `*.running` file in a lane, no live `land`), and no solo or sub-agent live in this checkout (`dispatch.py status`). The lane running a ticket at that moment is kept.
3. The maintainer picks classes in one question round, asked by the conductor, not by a solo.
4. `lanes.py sweep` for the approved plugin classes, then `lanes.py close` by name for any lane `sweep` kept as `no commits` in an approved class; branches with no worktree are deleted with `update-ref -d` by full name, each sha recorded first.
5. `git worktree prune`, measure again, and write the report. `git gc` is not run; the maintainer may run it to reclaim object space. Expected gain: most of the 4.5G and 446M, less the kept trees; the report gives the figure.

## 15. Rejected alternatives

- Lanes outside every checkout by default, as the spec has it: section 4.
- Three skills, or fanout.py subcommands: section 5.
- A port resource in gate_lock: a grant lives for one gate run, while a port must outlive gates and be readable by a probe outside any gate, so the ledger would gain a second meaning.
- A machine-wide port ledger: no cross-repo collision is observed, and it adds a second state file.
- Close a host lane at `fanout.py land`, the spec's order: the sub-agent is alive until it is stopped, so the lane closes after `prune --done`.
- Keep merged lanes for inspection: the integration branch holds every merged commit and `closed-lanes.txt` every tip; a stopped lane, the one worth inspecting, stays.
- A branch reaper apart from close, as `reap-branches.mjs`: after the build a plugin branch goes with its lane, so only the existing pile needs a batch, and section 14 covers it once.

## 16. Decisions for the maintainer

- Version: 0.22.4, as the ticket targets, not 0.22.3.
- Lanes root default: the sibling `<repo>.worktrees` outside the checkout (T-0563; the legacy `.claude/worktrees` in 0.23, `.worktrees` before 0.23.0).
- `sweep` at `prep` and `run` start: on by default with `lane_sweep: off` (recommended), or opt-in.
- Auto-merge in `wait`: off, written opt-in only (recommended; the authorization rule requires it).
- Where `closed-lanes.txt` and the archive live: under the lanes root (this design), or outside the repository as the 2026-10-10 cleanup did (`~/.claude/lane/`), which survives deleting the lanes root.
- What remains of this repo's pile (ticket H): the two kept unmerged branches and their trees.
- Archive expiry (T-0424): never (recommended), or an `archive prune --older-than <days>` the maintainer runs by hand (17.2).
- The maintainer's `~/.claude/lane/sweep.py` (T-0424): retire it, or keep a three-line shim that runs `lanes.py sweep` (17.6).

## 17. Git-native conventions (T-0424, addendum of 2026-10-11)

Maintainer decision 2026-10-10: adopt names, archive refs, the worktree lock, worktree config and branch descriptions, and fold the maintainer's `~/.claude/lane/sweep.py` into the plugin. Design only: no script is written and no branch or worktree is removed. Where this section differs from sections 1 to 16, this section wins; 17.10 lists each place. Labels as above, plus [T] observed in a throwaway repo with git 2.54.0 in this session. A role cannot create a worktree (block-stray-worktree.sh), so worktree and lock behavior is [I, git documentation] until the selftest of ticket A2 observes it.

### 17.1 Branch names and the clash rule (item 1)

| Namespace | Holds | Made by | Replaces |
|---|---|---|---|
| `lane/<ticket>-<slug>` | one lane's work, for example `lane/T-0424-git-native` | `lanes.py open`, kinds fanout and solo | `<integration>-<lane>` and a solo's `<name>` |
| `wave/<N>` | a fanout integration branch; N is one above the highest `wave/<N>`, legacy `wave<N>` or archived `wave/<N>` | fanout `run`, when `--integration` is not given | `fanout/<date>` |
| `release/<X.Y.Z>` | a release branch | a person or the release step; lanes.py only reads it | `release-X.Y.Z` |

The slug is lowercase `[a-z0-9-]`, at most 40 characters, from the ticket slug or the lane name; the ticket is `T-NNNN`. A lane that runs several tickets is named for its first. `open` refuses a `lane/` branch with no `--ticket` (section 8.1). The host's `worktree-<name>` stays, because the host names it [I]. Annotated tags `vX.Y.Z` are out of scope here.

Clash rule [T]: refs are paths, so `lane` and `lane/x` cannot both exist; creating `lane/x` fails with `'refs/heads/lane' exists`, and creating `lane` fails with `'refs/heads/lane/x' exists`.

- `lane`, `wave` and `release` are reserved. `open` runs `git check-ref-format --branch` and a `git for-each-ref` over the namespace before it creates anything, so a refusal leaves no directory and no record, and it names the flat branch to rename.
- The same rule covers `refs/archive/<date>/` (17.2).
- A worktree directory is a leaf, `<lanes root>/<ticket>-<slug>`, never `<lanes root>/lane/...`. An entry under the lanes root is a lane tree or a lanes dir (it holds `merge.lock`, like `fanout/`); `open` refuses a tree where a lanes dir exists and the reverse.

Migration: no branch is renamed, because a rename breaks open PRs, `into` records and `fanout land`'s lookup by branch. Ownership never came from a name (section 3), so `close`, `sweep` and `list` read old and new names alike. `list` marks a plugin lane whose branch lies outside the three namespaces `legacy`. A repo whose CI filters by branch pattern widens it to `lane/**`, `wave/**` and `release/**`, or sets `lane_names: legacy` in `.sdlc/config`, which keeps fanout's old names for new lanes [D].

### 17.2 Archive refs replace the text log (item 2)

`close` writes `refs/archive/<UTC date>/<branch>` before it removes anything, and `closed-lanes.txt` and `refs/sdlc/discarded/<b>` go away. The ref points at an annotated tag object, not at the bare commit, so its message carries what the branch loses on deletion: `<ticket> <title>`, the reason (`ancestor`, `content in <into>`, `discarded`), `into`, the tip sha and the UTC time. Git removes a branch's description with the branch [T], so this message is the one place the title survives. The ref keeps the objects through `git gc` and is not listed by `git branch`; a default `git push` and `git fetch` do not carry it [I].

- Recreate: `git branch <branch> refs/archive/<date>/<branch>`; git peels the tag to its commit [T]. `lanes.py archive list [<branch>]` prints date, branch, sha, reason and title; `lanes.py archive restore <date>/<branch>` runs that `git branch` and refuses when the branch exists.
- Never overwrite: the ref is created with an expected old value of zero. When it exists, or a directory clash fails it (`refs/archive/<date>/lane` against `lane/x`, observed [T]), the leaf becomes `<branch>.<sha7>`, which is a valid ref name [T].
- Order in the close of section 7: step 1 becomes this ref write, and a failed write stops the close with the branch intact. The `.sdlc/` copy of step 2 moves from `<lanes root>/archive/<lane>/` to `<git common dir>/sdlc-lane-archive/<lane>/`, so it survives deleting the lanes root and needs no ignore entry.
- The plugin never pushes, never expires and never deletes an archive ref. The objects of a landed lane are already in the target; only discarded work costs space. Expiry (`archive prune --older-than <days>`) waits for the maintainer's word (section 16).
- Existing history: `~/.claude/lane/closed-lanes-*.txt` and the archive folders stay as history and nothing reads them. The maintainer's sweep.py already writes plain commit refs under `refs/archive/<date>/<branch>` [V, its docstring]; `archive list` reads commit and tag targets alike.

### 17.3 Worktree lock (item 3)

- Set: `open` runs `git worktree lock --reason "<run_id> <tickets> <UTC>" <path>` right after it adds the worktree. A locked tree is a lane owned by a run.
- Cleared: `close` runs `git worktree unlock <path>` before `git worktree remove --force`; a locked tree needs a second `--force` otherwise, and `git worktree prune` skips it [I]. A run that ends with a stopped lane unlocks it, so a later `sweep` sees it and keeps it for its own reason.
- Skipped: `sweep` and `prep` read `git worktree list --porcelain` and skip a locked tree: `kept <lane>: locked: <reason>`, exit 0, row 8 of section 7 generalised. `prep` also does not reuse a locked lane's name or branch. Nothing passes an include-locked flag: a lock is cleared by its owner or by the rule below, never by the sweep.
- The finished-agent lock: the host may lock a sub-agent's tree with a reason that names the agent and a pid [I: no host lock exists in this checkout to read, and the maintainer's sweep.py skips locked trees]. After `dispatch.py prune --done <name>` has the agent stopped, `close` unlocks that lane only when the reason names a pid and `kill -0 <pid>` says it is gone. A live pid refuses with `locked by live pid <p>`, and a lock with no pid refuses with its reason, for the maintainer. Without this rule every host lane stays locked and unclosable after its agent ends.
- As built (T-0589): the reason is `<holder> <tickets>`, the holder from the ticket's claim (`refs/sdlc/claims/<id>`, else `claimed_by:`); `.lane.json` keeps it as `lock`, and only a plain `close` of a landed lane unlocks a lock equal to it (`--discard` and any other lock refuse). `list` shows a locked lane as `running (<reason>)`, never `closable`. The `lanes.py` docstring is the contract.
- Not a replacement: the `*.running` files and `merge.lock` stay as they are; the git lock is one more guard.

### 17.4 Worktree config replaces `.lane.json` (item 4)

With `extensions.worktreeConfig` on, each lane tree has its own config file in git's per-worktree admin directory, removed with the worktree [I]. `open` writes the record there:

```
git config --worktree lane.kind fanout        lane.into wave/26    lane.base wave/26   lane.baseSha <sha>
git config --worktree lane.port 7412          lane.runId fanout-<hex>   lane.opened <UTC>   lane.setup ok
git config --worktree --add lane.ticket T-0424
```

A probe in the lane reads `git config --worktree lane.port`, or `lanes.py port`, which wraps it. No file lands in the tree, so there is no `info/exclude` line and `git add -A` cannot stage a record. Port uniqueness reads each tree's value through `git -C <path> config --worktree` over `git worktree list --porcelain`, under the flock of section 6. A host lane has no tree before its spawn, so `prep` writes its record to a shared-config section `sdlc-host.<name>.*`, copied into the tree's config at spawn and unset at close [D].

Consumer setup cost, paid once per repo and printed by `open --dry-run`:

- `open` runs `git config extensions.worktreeConfig true` the first time. Git older than 2.20 [I] and tools that parse the config strictly may refuse a repo with that extension. The git here is 2.54.0 [T].
- A bare or `core.worktree` layout (gen-ui-kit's `<root>/main` toplevel with `core.bare = true`) needs `core.bare` and `core.worktree` moved into the main worktree's own config first [I, git-worktree documentation]. `open` reads both keys in the shared config and, when either is set, does not enable the extension.
- Fallback: with the extension off, or refused as above, `open` writes `.lane.json` as sections 6 and 7 describe, adds it to `info/exclude`, and prints `worktree config off: using .lane.json`. The reader tries worktree config, then `.lane.json`.
- The silent hazard [T]: with the extension off, `git config --worktree lane.port 7401` exits 0 and writes the shared config, so two lanes would overwrite each other. lanes.py therefore reads `git config --get extensions.worktreeConfig` and uses `--worktree` only when it prints `true`, on write and on read.

### 17.5 Branch description (item 5)

`open` runs `git config branch.<b>.description "<ticket> <title>"`: one line, the title cut to 120 characters, shared config, no extension needed [T]. `list` and `board.py --lanes` show it beside each lane, and `open` also sets it on a legacy-named branch it adopts. Git drops it when the branch is deleted [T], so `close` copies it into the archive tag message (17.2) first.

### 17.6 One authoritative sweep (item 6)

`~/.claude/lane/sweep.py` (183 lines, a maintainer tool outside any repo [V]) becomes `lanes.py sweep`, and lanes.py is the only script that closes a landed lane or deletes its branch. What sweep.py tests that section 7 did not is added to the truth table:

| Added to section 7 | Rule | Outcome |
|---|---|---|
| landed by pull request | `gh pr list --state merged --head <b> --json headRefOid` reports a head sha equal to the branch tip; read only, skipped when `gh` or a remote is absent | `closed <lane> (pr merged)`, as row 9 |
| age | `sweep` only: the tip is younger than `lane_min_age_hours` (default 2) | `kept <lane>: recent` |
| in use | `sweep` only: a running process mentions the lane path (`ps`) | `kept <lane>: in use by pid <p>` |
| locked | 17.3 | `kept <lane>: locked: <reason>` |

The age, in use and locked rows sit after row 6 and before row 9. The landed test of section 7 runs ancestor first, then merged PR, then content, and its negative controls stay.

Default mode: a bare `lanes.py sweep` is a dry run, as sweep.py is, and `--apply` acts; this replaces `--dry-run` in section 5. The callers pass `--apply`, and none of them copies a rule:

| Caller | Call | When |
|---|---|---|
| `fanout.py run`, `prep` | `lanes.sweep(apply=True)`, unless `lane_sweep: off` | start |
| `fanout.py land` | `lanes.close(lane)` for a `full` lane after its last ticket | after the ticket lands |
| fanout step 5 | `lanes.py sweep --apply` | after the user-approved `git merge --ff-only` |
| `tickets.py close` | `lanes.still_open(root, ticket)`, print only | after a successful close |
| `dispatch.py prune --done` | `lanes.close(host lane)` | after the agent is stopped |

sweep.py's `--discard-dirty` becomes `close --discard`, its `--keep` becomes a `lane_keep:` list in `.sdlc/config`, and its `--include-locked` is dropped (17.3). The maintainer's copy may stay as a three-line shim that runs `lanes.py sweep "$@"`, or be retired (section 16); no plugin script reads `~/.claude/lane`.

### 17.7 Checks (item 7)

Each is a `lanes.py` mode or selftest case in a throwaway repo, with a mutant that drops the guard and must then fail the case. C1 and C4 of section 10 are the two the ticket names; they are restated with the change.

| Check | Fails when | Negative control |
|---|---|---|
| C1 amended, no lane worktree under a checkout | with `lanes_root` outside the toplevel, a plugin lane (by record) lies under any worktree's toplevel, compared by real path | `lanes_root: ../lanes` and a lane at `<top>/.worktrees/x` exits 1 naming `x`; the same lane under `../lanes` exits 0; the mutant comparing unresolved strings passes a symlinked path and fails the case |
| C4 amended, stale lane report | a report, exit 0 (`--fail` exits 1 on any entry): `closable` (landed and open), `stale` (not landed, tip older than `lane_stale_days`, no open PR), and now `locked` with the reason | a tip 11 days old is `stale` and one at 9 is not; a landed lane of any age is `closable`; a stale lane whose lock names a live pid prints `stale, locked`, and `sweep --apply` still keeps it |
| C9 names | `open` accepts `lane` beside `lane/x`, `lane/x` beside `lane`, or a lane branch with no ticket | the three refuse with no directory and no record left; `lane/T-1-a` opens; the mutant that creates the directory first leaves one and fails |
| C10 archive | a close leaves no `refs/archive/<date>/<branch>` that `git branch` can restore, overwrites an earlier ref, or deletes the branch after a failed write | close, delete, `archive restore` returns the tip; two closes of one name on one date leave two refs (the mutant without the zero old value leaves one); a forced directory clash stops the close with the branch present (the mutant that ignores the failure deletes it) |
| C11 lock | `open` leaves a tree unlocked, `sweep` closes a locked lane, `close` leaves a lock behind, or a live pid's lock is cleared | `git worktree list --porcelain` shows `locked` after open and none after close; a landed locked lane survives `sweep --apply` (the mutant without the lock check closes it); a host-style lock naming a reaped child pid is cleared and one naming the test's own pid refuses |
| C12 worktree config | two lanes read one port, the main checkout reads a `lane.*` key, or the fallback is silent | with the extension on, two lanes read distinct ports and `git config --get lane.port` in main is empty; with it off or `core.bare` set, `.lane.json` appears and `worktree config off` is printed; the mutant that uses `--worktree` without the check gives two lanes one port [T] and fails the case |
| C13 description | the branch description is not `<ticket> <title>` after open, or the archive tag message lacks it after close | read back both; the mutant that skips the copy fails the second |
| C14 one home | a script other than lanes.py names `sweep.py`, `closed-lanes` or `~/.claude/lane`, or closes a landed lane without `lanes.close` | a `grep` in `check.sh`; a copy of fanout.py with one planted `sweep.py` line exits 1, the tree as built exits 0. fanout's own undo of a branch it just made in a failed start is not a close and stays [I] |

C1 gates `check.sh` here once ticket A exists, as section 10 says (ticket I). C14 lands with ticket G, after every caller moved.

### 17.8 Auto-merge is per pull request, with a merge method

Evidence from the ticket, gen-ui-kit, 2026-10-10 (the ticket's account, not re-run here): `lane-wait`'s `gh pr merge --auto` works, needs one of `--squash`, `--merge` or `--rebase`, and merged PR 425 once its checks were green. The owner approved each merge per PR. So the call is `gh pr merge <pr> --auto --<method>`, and section 9's blanket `lane_auto_merge: on` goes: the opt-in is per PR and per call, `lanes.py wait <name> <pr> --auto-merge squash|merge|rebase`, typed by the owner's conductor for that PR after the owner's go. There is no config line, no default and no default method; `wait` without the flag only watches. The role refusal of section 9 stays. Section 12 no longer lists the merge call as untested: it is observed in the upstream script. lanes.py's own call stays unverified until ticket F's live run on a throwaway repository, which the maintainer authorizes per run.

### 17.9 Build tickets and the files each changes (item 8)

Section 13's tickets stand except where these change. Order: A, A2; D at any time; then B, C, E, F, G; H and I after A, H only with the maintainer's go. Sizes are estimates. `check.sh`, `check.py`, `fanout.py` and `lanes.py` have one writer at a time.

| # | Ticket | Size | Files changed | Done when |
|---|---|---|---|---|
| A | `lanes.py` core, amended | L3 | new `scripts/lanes.py` (open, close, sweep with the 17.6 rows and `--apply`, list, check, port, archive list and restore, selftest; names, clash rule, archive refs, branch description, the `.lane.json` record; the tables in its docstring); `scripts/check.sh` (selftest line); `docs/references/sdlc-internals.md` (entry, and the keys `lane_names`, `lane_min_age_hours`, `lane_keep`) | `(red)` `python3 plugins/sdlc-lite/scripts/lanes.py selftest` fails now (no file); after, exit 0 with a case per truth-table row and per C1, C4, C9, C10, C13 control, each mutant observed failing; `check.sh` exits 0 |
| A2 | lock and worktree config | L2 | `scripts/lanes.py` (lock at open, unlock at close, the locked rows, the finished-agent rule, `extensions.worktreeConfig` setup, the `--worktree` record with the `.lane.json` fallback, `lanes.py port`); `docs/references/sdlc-internals.md` (setup cost and fallback) | `(red)` `lanes.py selftest` has no C11 or C12 case now; after, both pass with their mutants failing |
| B | fanout and solo_run use lanes, amended | L3 | as section 13, plus `scripts/fanout.py` (`wave/<N>` default, `lane/<ticket>-<slug>` lane branches, lock at open, `lane_names: legacy`) and `scripts/solo_run.py` (`--worktree` branch `lane/<ticket>-<NAME>` when the ticket is known, else the old name) | as section 13 |
| E | board and fleet, amended | L2 | as section 13; the `--lanes` cell also shows `legacy`, `locked` and the branch description | as section 13 |
| F | `lanes.py wait`, amended | L2 | `scripts/lanes.py` (wait, `--auto-merge <method>` per PR, the role refusal, a stub `gh` selftest) | the selftest covers MERGED, CLOSED, timeout, no flag (no merge call), each method passed through, and the role refusal; the live run stays unverified until authorized |
| G | docs and one home, amended | L1 | this file (status built); `docs/specs/sdlc-lite/README.md`; `docs/README.md`; `plugins/sdlc-lite/AGENTS.md` (the `## Lanes` interim directive and its `sweep.py` line replaced by a pointer to `lanes.py`); `scripts/check.sh` (the C14 grep) | `docs_check.py` and `check.py` exit 0, and the C14 control behaves |

C, D, H and I are as in section 13, except that H's report names the archive refs it wrote instead of lines in a text log. No ticket removes a worktree or branch here, and none writes `~/.claude/lane`.

### 17.10 Earlier text this section replaces

| Place | Was | Now |
|---|---|---|
| 1, 3, 8 (kinds, `into` names) | `<integration>-<lane>`, `<name>` | the namespaces of 17.1; old names read alike |
| 5 | `sweep [--dry-run]`, no archive command | `sweep` is a dry run by default with `--apply`; `archive list` and `restore` |
| 6, 7 row 6, 13.1 step 1 | `.lane.json`, in `info/exclude` | worktree config, with `.lane.json` as the fallback (17.4) |
| 7 step 1, row 12, 13.1 step 6, 14, 15 | `closed-lanes.txt`, `refs/sdlc/discarded/<b>` | `refs/archive/<date>/<branch>` annotated tags (17.2) |
| 7 step 2 | untracked copy under `<lanes root>/archive/<lane>/` | `<git common dir>/sdlc-lane-archive/<lane>/` |
| 7 row 8 | host lane queued in `prune.json` | and any locked tree (17.3) |
| 9, 11, 12, 13 F, 13.1 step 7 | `gh pr merge --auto`, `lane_auto_merge: on`, untested | per PR `--auto-merge <method>` (17.8) |
| 10 C1, C4 | placement and stale report | restated in 17.7 |
| 13 | tickets A to I | 17.9 |
| 16 | six decisions | two more, above; the archive location is settled by 17.2 |
