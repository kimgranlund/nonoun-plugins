<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
A fanout lane whose chain stops mid-ticket ends with a clean lane tree: fanout.py commits the stopped work as a `wip(<id>): <outcome>` commit on the lane branch only. That commit is never merged, and the report names its short sha, so the next sync merge into that lane never fails with "commit your changes before you merge".

## Step 1: WIP-commit a stopped lane in fanout.py, with a failing-first selftest case
level: L3
### Do
In `plugins/sdlc-lite/scripts/fanout.py`:
- Add a helper, for example `wip_commit(wt, tid, outcome)`, that runs only in the lane worktree `wt`. It checks for tracked changes (`git diff --quiet HEAD`) and untracked files (`git ls-files --others --exclude-standard`). If the tree is clean it returns `''`. Otherwise it runs `git add -A`, then `git commit -q -m "wip(<id>): <outcome>"`, and returns the new short sha (7 chars). The message is exactly `wip(<id>): <outcome>`, for example `wip(T-0001): driver failed rc=3`. It never touches the integration worktree, main, or the stash. A failed add or commit returns `''` and never raises.
- In `run_lane`, after a ticket's outcome is anything other than `merged`, call the helper on the lane worktree. This covers the `error:` exception path too. It must run before the next ticket is marked `skipped`. When it returns a sha, record the row's Commit cell as `wip <sha7>` if that cell was empty. Keep an existing lane sha, because a red gate or merge conflict already committed and leaves a clean tree. Leave the outcome text unchanged. The lane still stops, later tickets are still `skipped`, and the exit code is still 1. Print a `[<lane>] <id> wip <sha7> on <lane branch>` line.
- In `run_ticket`, call the same helper under the lock before the sync `git merge --ff --no-edit <integration>`, so a lane tree that is already dirty gets WIP-committed and never fails the sync.
- Never merge a `wip(` commit into the integration branch. The stopped ticket's flow already returns before the locked merge, so keep it that way.
- The builder no-commit rule and the conductor's "never commit" driver prompt stay unchanged: the script commits, not the driver.

Add a selftest case to `selftest()`, in the same file, as its own block. Write it first and watch it fail on the old code before changing `run_ticket` and `run_lane`. The case uses a stub driver that writes a file in the lane worktree and exits nonzero, with one lane and one ticket. It expects all of the following:
- The lane tree is clean.
- The lane branch tip subject starts `wip(T-0001): driver failed rc=`.
- The lane branch holds the written file.
- The lane branch is not an ancestor of the integration branch.
- The integration branch and main still equal the fixture commit.
- The report row's Commit cell matches `wip <7 hex>`.

Update the `selftest` paragraph of the module docstring to list the case. The full docstring and doc updates happen in Step 2.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- `grep -qF "wip(" plugins/sdlc-lite/scripts/fanout.py`
- `F=$PWD/plugins/sdlc-lite/scripts/fanout.py; d=$(mktemp -d) && git init -q -b main "$d/r" && git -C "$d/r" config user.name t && git -C "$d/r" config user.email t@t.invalid && git -C "$d/r" config commit.gpgsign false && mkdir -p "$d/r/.sdlc/a" && printf -- '---\nid: T-0001\ntitle: "A"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\na\n' >"$d/r/.sdlc/a/handoff.md" && git -C "$d/r" add -A && git -C "$d/r" commit -qm fixture && (cd "$d/r" && python3 "$F" run alpha=T-0001 --integration fanout/w --lanes-dir "$d/l" --driver 'echo x >edit.txt; exit 3' >"$d/out" 2>&1); git -C "$d/l/alpha" diff --quiet HEAD && test -z "$(git -C "$d/l/alpha" ls-files --others --exclude-standard)" && git -C "$d/r" log -1 --format=%s fanout/w-alpha | grep -q '^wip(T-0001): driver failed rc=3$' && git -C "$d/r" cat-file -e fanout/w-alpha:edit.txt && ! git -C "$d/r" merge-base --is-ancestor fanout/w-alpha fanout/w && test "$(git -C "$d/r" rev-parse fanout/w)" = "$(git -C "$d/r" rev-parse main)" && grep -qE '^\| alpha \| T-0001 \| driver failed rc=3 \| wip [0-9a-f]{7} \|$' "$d/l/report.md"`
- The new selftest case fails against the pre-change `run_ticket` and `run_lane`. The verifier observes this in a `git worktree add <tmp> HEAD` copy: the copy's `fanout.py` gets only the new selftest block pasted in, then its `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 1 and names the new case.
- Observable in `run_ticket`: the WIP helper is called on the lane worktree before the sync `git merge --ff --no-edit`. No helper call runs `git` in the integration worktree or runs `git stash`.
- `pyflakes`-free is not required. `python3 -m py_compile plugins/sdlc-lite/scripts/fanout.py` exits 0.

## Step 2: Document where stopped work lands
level: L1
### Do
Update the docs to match Step 1, with no em dashes:
- `plugins/sdlc-lite/scripts/fanout.py` module docstring, the `run` section: on step 2 (driver non-zero exit) and on any outcome other than `merged`, a dirty lane tree is committed as `wip(<id>): <outcome>` on the lane branch only. It is never merged, and the report's Commit cell shows `wip <sha>`. Before each sync, a dirty lane tree is WIP-committed first. Replace "the tree left as is".
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: one sentence near the top saying the same, with the literal `wip(<id>): <outcome>`. Also say to inspect a stopped lane's `wip(` commit on its lane branch.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: one sentence saying a /chain run under fanout that stops mid-step leaves its work as a `wip(<id>): <outcome>` commit that fanout.py makes on the lane branch. A plain /chain outside fanout commits nothing and never commits on main.
- `CLAUDE.md`, the `scripts/fanout.py` bullet under Layout: add the `wip(<id>): <outcome>` lane commit on a stop and before a dirty sync, never merged, sha in the report. `.claude/agents/sdlc-lite-author.md` does not restate the stop behavior (it only says to keep them in sync), so leave it unless the builder finds a restatement.

`check.sh` takes about 11 minutes, longer than the 300s guard timeout, so it is a plain final criterion here, not a `(guard)`.
### Acceptance criteria
- `python3 -c 'import ast,sys; d=ast.get_docstring(ast.parse(open("plugins/sdlc-lite/scripts/fanout.py").read())); sys.exit(0 if "wip(<id>): <outcome>" in d else 1)'`
- `grep -qF 'wip(<id>): <outcome>' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -qF 'wip(<id>)' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF 'wip(<id>): <outcome>' CLAUDE.md`
- `! git diff HEAD -- CLAUDE.md plugins/sdlc-lite/skills/fanout/SKILL.md plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/scripts/fanout.py | grep -q '^+.*—'`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- `plugins/sdlc-lite/scripts/check.sh` exits 0.

## Risks
- The pre-sync WIP path cannot be reached in one fanout run: preflight refuses existing lane branches, and a `merged` ticket always leaves a clean tree. So the selftest can prove only the stop path end to end. Step 1 checks the pre-sync call by reading the code.
- check.py wording guards on the chain and fanout skills (the `interactive`, `run_in_background`, `sleep` words) could reject a careless edit. `check.sh` in Step 2 catches that.
- The Step 1 criterion needs a git identity in the fixture repo, and it sets one. A host with a global `commit.gpgsign` is also covered, because the fixture sets it false.
- A stray criterion line in Step 1 (the `py_compile` one) is worded awkwardly but is runnable and green after the build. It is not a guard.
