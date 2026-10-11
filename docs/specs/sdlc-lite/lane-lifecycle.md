# Lane lifecycle: open, close, wait

Status: design, not built, awaiting the maintainer's approval (ticket T-0422, 2026-10-10). Version 0.1. Targets 0.22.4 unless the maintainer says otherwise. Nothing in section 13 is built by T-0422, and nothing in section 14 is removed by it. Evidence labels: [V] read in the file or command named, [I] inferred, [D] a decision this design makes for approval. Plugin paths are under `plugins/sdlc-lite/` unless they start with `docs/`.

## 1. Answer in one paragraph

Lanes pile up because nothing closes them, more than because of where they live. On 2026-10-10 this repo held 146 worktrees and 254 local branches; 142 of the 145 lane and host worktrees sit on a branch main already contains, and 251 of the 254 branches are ancestors of main [V]. The last step anyone owns is the `git merge --ff-only <integration>` in fanout step 5; fanout's contract says "the worktrees stay for inspection", and the host keeps a sub-agent worktree that has commits. This design adds one script, `scripts/lanes.py`, as the only home of the lane lifecycle. `open` makes a lane and writes its `.lane.json` (kind, branch, target, tickets, port). `close` removes a lane only when its tree is clean and its branch has landed, either as an ancestor of its target or with every changed file equal to the target's (which catches squash merges); it records the branch sha first and deletes the branch by its full ref name. `sweep` closes every landed plugin lane and leaves everything else. `list`, `check` and `port` report. fanout.py, solo_run.py, tickets.py and dispatch.py call it, and nothing else creates or removes a lane. Lanes stay under `.worktrees/` by default, because once lanes close the in-tree copies are bounded by `--max-lanes`; one config line moves them outside the checkout, as gen-ui-kit needs. `lanes.py wait` polls a PR and closes the lane on MERGED; it calls `gh pr merge --auto` only under a written opt-in, because that merge acts as the owner's account. The existing pile here was removed by a maintainer-authorized cleanup later the same day; section 14 keeps the proposal as the procedure for a consumer repo's pile and for what remains here.

## 2. Sources and measurements

Read for this design [V]: the gen-ui-kit spec and scripts attached to T-0422 (`SPEC.md`, `env.sh`, `lane-open.sh`, `lane-close.sh`, `lane-wait.sh`), [fanout.py](../../../plugins/sdlc-lite/scripts/fanout.py) (docstring for `run`, `prep`, `land`, `roll`; `HOST_WORKTREES`, `queue_prune`, `cmd_land`), [dispatch.py](../../../plugins/sdlc-lite/scripts/dispatch.py) (prune docstring, `prune_add`, `remove_tmp`, `strays`), [tickets.py](../../../plugins/sdlc-lite/scripts/tickets.py) (close usage), [solo_run.py](../../../plugins/sdlc-lite/scripts/solo_run.py) (`ensure_worktree`, `auto_worktree`), [gate_lock.py](../../../plugins/sdlc-lite/scripts/gate_lock.py) (docstring), [block-stray-worktree.sh](../../../plugins/sdlc-lite/hooks/block-stray-worktree.sh), [the hook reference](../../references/claude-hooks.md), [the fanout skill](../../../plugins/sdlc-lite/skills/fanout/SKILL.md), [Codex execution](../../references/codex-role-execution.md), and the [root guidance](../../../AGENTS.md) invariant to preserve unrelated worktrees, branches and stashes.

Measured on 2026-10-10 with read-only git commands in this repository, before the cleanup recorded in `.sdlc/notes.md` (section 14) [V]:

- 146 worktrees: the main checkout; 124 under `.worktrees/fanout*/` (71 fanout lanes dirs); 15 host trees under `.claude/worktrees/`; 6 made by hand under `.worktrees/` (`wave-b`, `ticket-stages-b`, `t0185`, `release-0.21.2`, `idle-host`, `haiku55`).
- Of the 124 fanout trees, 119 are clean on a branch main contains, 2 have uncommitted changes (`fanout-fleet/integration`, `fanout-fleet2/integration`), and 3 are clean on branches main lacks (`fanout-b5/ratelimit` on `batch5-ratelimit`, `fanout-b5/selfc` on `batch5-selfc`, `fanout-load/load` on `loadlanes-load`, tips 2026-10-06). Of the 15 host trees, 13 are clean and 2 have changes (`agent-a8796067dca9eb594`, `agent-ae9ec401bb7128396`), all on branches main contains. Of the 6 hand-made trees, 4 have changes (`idle-host`, `t0185`, `ticket-stages-b`, `wave-b`).
- 254 local branches: 146 checked out in a worktree, 108 with none; all 108 are ancestors of main.
- Disk: `du -sh` gives 4.5G for `.worktrees/` and 446M for `.claude/worktrees/` (the ticket's 4.4 GB is an earlier reading).

Two gaps in the spec's `lane-close.sh`, reproduced in a throwaway repo [V]:

- With no `origin/main` ref, `git merge-base` fails, `git diff --name-only` exits 128 with an empty list, the per-file loop never runs, and the script goes on to remove the worktree and delete the branch. An unresolvable target must refuse.
- `git diff --name-only` detects renames by default, so a lane that renamed `old.txt` to `new.txt` lists only `new.txt`, and a target that still holds `old.txt` passes. `--no-renames` lists both paths.

Other facts the design leans on:

- fanout.py makes `<lanes-dir>/<lane>` on `<integration>-<lane>` and `<lanes-dir>/integration`, with the default lanes dir `<toplevel>/.worktrees/fanout`, and keeps them [V].
- The host makes `.claude/worktrees/<name>` on `worktree-<name>` for `isolation: worktree`; prep names solo lanes `<id>-solo`, and land also resolves a host-named `worktree-agent-<hex>` branch through the agent id in `runs.jsonl` [V]. The plugin cannot choose that path [I: no host setting is known to this design].
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
| host lane | the Claude host, `isolation: worktree` | `.claude/worktrees/<name>` | `worktree-<name>` | the integration branch it landed in | `dispatch.py prune --done <name>`, else `sweep` |
| runner tmp | run.sh, dispatch.py | `.worktrees/tmp/<role>-<pid>`, detached | none | none | unchanged: run.sh EXIT, `remove_tmp`, `reap-tmp-worktrees.sh` |
| manual | a person | anywhere | any | none | the person; listed, never touched |

The first five kinds are plugin lanes. Ownership is what lets `close` and `sweep` act on a tree: a `.lane.json` in it (written by `open`), a host record under `<lanes root>/host/` (written by `prep`, section 6), or, for trees made before this build, membership in a fanout lanes dir (a directory holding `merge.lock` and `logs/`), or a host tree whose branch `fanout.py land` resolved to a ticket. Everything else is manual, which keeps the root invariant that unrelated worktrees, branches and stashes are preserved [D]. After the build this table lives in the `lanes.py` docstring, and this section points there.

## 4. Where lanes live (item 1)

Decision [D]: lanes stay inside the checkout by default, under one lanes root, and a repo moves the root outside with `lanes_root: <path>` in `.sdlc/config` (relative to the toplevel; `../lanes` for gen-ui-kit's bare-repo layout, where the toplevel is `<root>/main`). Reasons:

- The pile is a closing problem. With close and sweep, a run keeps at most `--max-lanes` lane copies (default 4, hard cap 16) plus one integration tree, so the 440-copy walk the spec describes does not recur.
- A session sandbox may not write outside its workspace. Codex headless conductors run inside their workspace sandbox [V, Codex execution]; making `../<repo>-lanes` from there is expected to fail [I]. Inside is the setting that works on both hosts.
- The default must not create a directory beside the user's checkout unasked.
- `.claude/worktrees/` is inside the checkout whatever the plugin does, so watcher exclusions are needed anyway.

What changes:

- Lanes root: `lanes_root:` defaults to `.worktrees`. fanout's default `--lanes-dir` becomes `<lanes root>/fanout` (the same path as today for a repo without the line), and solo_run's `--worktree` tree goes to `<lanes root>/<name>`. Runner tmp stays at `<toplevel>/.worktrees/tmp`, because `SDLC_TMP_WORKTREES` and the hook's sub-agent prefix depend on that path.
- Ignore rules: unchanged. `.worktrees/` and `.claude/worktrees/` stay gitignored, and fanout preflight and `prep` already refuse otherwise. A lanes root outside the toplevel needs no ignore entry, as for `--lanes-dir` today. `open` adds `.lane.json` to `<git common dir>/info/exclude`, as the spec does, so no tracked file changes and a lane's `git add -A` never stages it.
- Watcher exclusions: unchanged for `.worktrees/` and `.claude/worktrees/`, and not needed for an outside lanes root. The fanout skill's caveat that Node resolution walks up into the main tree's `node_modules` stays true for in-tree lanes; an outside root removes it and needs `lane_setup:` (section 11).
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

## 9. Wait and auto-merge

`lanes.py wait <name> <pr>` polls `gh pr view <pr> --json state` every 45 seconds up to `--timeout` (default 6 hours; the spec's loop has no limit and spins forever on a `gh` error). `MERGED` runs `close` with `into` the PR's base as a fetched remote-tracking ref, which closes by content after a squash merge. `CLOSED` prints `PR <n> closed, lane <name> left open` and exits 1. A timeout exits 3 and leaves the lane.

It calls `gh pr merge <pr> --auto` only when `.sdlc/config` has `lane_auto_merge: on` [D]. That merge runs as the account `gh` is logged in as, the owner's, so it is a publish action: the line is a written opt-in the maintainer adds, and it is never a default. `wait` also refuses the merge call, and says why, when `SDLC_ROLE` is set or the caller is a role sub-agent, because block-publish.sh would not see a `gh` call made inside this script. Without the line, `wait` only watches a PR a person merges.

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
- `lane_auto_merge: on`, a written opt-in only the maintainer adds (section 9).

The plugin pins no Node binary: `lane_setup` is the repo's own command and selects Node through the repo's version manager (`fnm exec --using .nvmrc`, `mise exec`, or a `.nvmrc`-aware script). For gen-ui-kit the lines would be `lanes_root: ../lanes`, `lane_ports: 7400-7699`, `lane_into: origin/main`, and `lane_setup:` running `pnpm install` then `node scripts/dev/bootstrap-worktree.mjs` under their Node 22 lookup, which replaces `~/.claude/lane/`.

## 12. Risks and known gaps (item 8)

- `gh pr merge --auto` is untested (spec, known gaps), and the earlier waiter merged as the owner's account on green. Mitigation: off by default, a written opt-in, refused inside a role (section 9). Authorization note: auto-merge acts under the owner account, so it needs the maintainer's written opt-in in `.sdlc/config` and is never default; its live run on a throwaway GitHub repository needs the maintainer's authorization (ticket F), and until then the merge call is reported unverified.
- The hard-coded Node path in `env.sh` is not ported; `lane_setup` is the repo's own command (section 11).
- The branch-name-equals-remote-ref crash in `reap-branches.mjs` (`pr/4297` beside `refs/remotes/pr/4297`): lanes.py names every ref in full and deletes with `update-ref -d refs/heads/<b> <sha>`. A selftest case makes a local `pr/1` beside `refs/remotes/pr/1` and closes only the local branch.
- Two more gaps found here, both reproduced [V]: the shell close passes when its target does not resolve, and rename detection hides a deleted path. Row 5 and test step 3 cover them.
- The host may expect `.claude/worktrees/<name>` to exist after its agent stops [I]. Closing only after `prune --done`, once the agent is stopped, limits that; live-run step 5 checks it.
- `sweep` deletes branches without a question. It touches only plugin lanes that are clean and landed, records each sha first, and `lane_sweep: off` disables it; any uncommitted file keeps a lane.
- An outside `lanes_root` may fail under a write-restricted sandbox [I]; `open` then refuses naming the path, and the default stays inside.
- `sweep` during a `run`: `close` refuses a branch that moved (step 4) and an integration tree with open lanes (row 4), and `sweep` holds the lanes dir's `merge.lock` while it acts there.

## 13. The build, split into tickets (item 9)

Filed after the maintainer approves this design, in this order. `check.sh`, `check.py` and `fanout.py` are shared hot files: one writer at a time, one lane.

| # | Ticket | Size | Files changed | Done when |
|---|---|---|---|---|
| A | `lanes.py` core | L3 | new `scripts/lanes.py` (open, close, sweep, list, check, port, selftest; the kinds table, truth table and record fields in its docstring); `scripts/check.sh` (the selftest line); `docs/references/sdlc-internals.md` (an entry pointing at the docstring, and the new `.sdlc/config` keys beside `hash_bound`) | `(red)` `python3 plugins/sdlc-lite/scripts/lanes.py selftest` fails now (no file); after, it exits 0 with one case per truth-table row and per C1 to C6 control, each mutant observed failing; `check.sh` exits 0 |
| B | fanout and solo_run use lanes | L3 | `scripts/fanout.py` (open in setup, close merged lanes, sweep at start, `lane still open` report lines, `SDLC_LANE_PORT`, `prep` prints `lanes.py open` for a `full` lane and writes the host record, `roll` removes its scratch, docstring and selftest cases); `scripts/solo_run.py` (`ensure_worktree` through `lanes.open`, selftest); `skills/fanout/SKILL.md` (a lifecycle paragraph replaces "Lane worktrees stay after the run", step 5 runs `lanes.py sweep`, allowed-tools; the `check.py` phrase list keeps `.claude/worktrees/`) | `(red)` a fanout selftest case that expects a merged lane's tree gone after `run` fails now; after, `fanout.py selftest` and `solo_run.py selftest` exit 0, and a stopped lane stays with its report line |
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

Update, 2026-10-10, after this section was written: a maintainer-authorized cleanup removed 145 worktrees and 248 merged local branches here, logging each branch name and sha in `~/.claude/lane/closed-lanes-sdlc-lite.txt` and archiving the untracked records of the dirty trees in `~/.claude/lane/archive-sdlc-lite/` (`.sdlc/notes.md`, main commit c5644268). It kept the running lane (`wave26`, `wave26-ll`) and two unmerged branches whose work conflicts with main (`batch5-ratelimit` for T-0301, `loadlanes-load` for T-0317); `batch5-selfc` went, its content being on main. When this design was verified the repo held 5 worktrees and 5 branches [V]. The table and steps below are the proposal as written against the state in section 2; they stay as the procedure for a consumer repo's pile, and here ticket H covers only what remains.

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
- Lanes root default: `.worktrees`, inside (recommended), or outside the checkout.
- `sweep` at `prep` and `run` start: on by default with `lane_sweep: off` (recommended), or opt-in.
- Auto-merge in `wait`: off, written opt-in only (recommended; the authorization rule requires it).
- Where `closed-lanes.txt` and the archive live: under the lanes root (this design), or outside the repository as the 2026-10-10 cleanup did (`~/.claude/lane/`), which survives deleting the lanes root.
- What remains of this repo's pile (ticket H): the two kept unmerged branches and their trees.
