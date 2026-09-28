<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make fanout.py put lane worktrees under `<toplevel>/.worktrees/fanout/<lane>` by default. The dry run and the run both refuse (exit 2, naming the .gitignore fix) when `.worktrees/` is not ignored, and every in-repo doc must describe the new default and its caveats.

## Step 1: New default lanes dir and ignore preflight in fanout.py, with selftest
level: L3
### Do
In `plugins/sdlc-lite/scripts/fanout.py`:
- In `preflight()` (around line 214), replace the default `pathlib.Path(f'{top}-fanout')` with `top / '.worktrees' / 'fanout'`. Keep `--lanes-dir` as the override, resolved against the cwd as it is today.
- Replace the current "inside the work tree ... lanes live outside it" refusal with these rules:
  - `lanes_dir == top` is still refused.
  - When the default dir is used, run `git check-ignore -q .worktrees/x` from `top`. If it fails, raise `Refuse`, which exits 2 and creates nothing. The message names the fix: add `.worktrees/` to `.gitignore`.
  - When an explicit `--lanes-dir` lies inside `top`, run the same check on `<lanes_dir relative to top>/x`. If that path is not ignored, refuse and name the path to add to `.gitignore`.
  - An explicit `--lanes-dir` outside `top` needs no ignore check, exactly as today.
  - This preflight runs before any write, so `--dry-run` refuses too.
- Update the module docstring (line 18, "defaults to the sibling <toplevel>-fanout and must lie outside the toplevel") and the `--lanes-dir` argparse help (line 658) to name the new default, the ignore rule, and the refusal.
- Leave lane branch naming, sync, merge, gates, and close behavior unchanged.

Selftest changes, in `selftest()` case 2:
- Commit a `.gitignore` containing `.worktrees/` in the `rr` fixture, for example by extending `make_repo` with an optional extra-files argument.
- Change the default-dir dry-run expectation from `f'{rr}-fanout'` to `rr/.worktrees/fanout` (the integration path and `rr/.worktrees/fanout/alpha`).
- Change the "no lanes dir" expectation to check that `rr/.worktrees/fanout` does not exist.
- Add a new fixture repo with no `.gitignore`. A default-dir `--dry-run` there must exit 2, its stderr must name `.gitignore` and `.worktrees/`, it must have no Traceback, and it must create no `.worktrees` dir, no `fanout/*` branch, and no extra worktree.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- The default-dir dry run, in a repo whose committed `.gitignore` ignores `.worktrees/`, prints the integration and lane worktrees under `<repo>/.worktrees/fanout`: `f=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/fanout.py && d=$(cd "$(mktemp -d)" && pwd -P) && mkdir -p "$d/.sdlc/x" && printf -- '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n' > "$d/.sdlc/x/handoff.md" && printf '.worktrees/\n' > "$d/.gitignore" && git -C "$d" init -q -b main && git -C "$d" add -A && git -C "$d" -c user.name=t -c user.email=t@t.invalid commit -qm f && out=$(cd "$d" && python3 "$f" run --dry-run alpha=T-0001) && printf "%s\n" "$out" | grep -qF "$d/.worktrees/fanout/integration" && printf "%s\n" "$out" | grep -qF "$d/.worktrees/fanout/alpha"`
- In a repo that does not ignore `.worktrees/`, the default-dir dry run exits 2, names `.gitignore` and `.worktrees/` on stderr, and creates no `.worktrees`: `f=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/fanout.py && d=$(cd "$(mktemp -d)" && pwd -P) && mkdir -p "$d/.sdlc/x" && printf -- '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n' > "$d/.sdlc/x/handoff.md" && git -C "$d" init -q -b main && git -C "$d" add -A && git -C "$d" -c user.name=t -c user.email=t@t.invalid commit -qm f && (cd "$d" && python3 "$f" run --dry-run alpha=T-0001 >/dev/null 2>"$d.err"; test $? -eq 2) && grep -qF ".gitignore" "$d.err" && grep -qF ".worktrees/" "$d.err" && test ! -e "$d/.worktrees"`
- (guard) An explicit `--lanes-dir` outside the repo still works in an unignored repo and creates nothing on a dry run: `f=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/fanout.py && d=$(cd "$(mktemp -d)" && pwd -P) && mkdir -p "$d/.sdlc/x" && printf -- '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n' > "$d/.sdlc/x/handoff.md" && git -C "$d" init -q -b main && git -C "$d" add -A && git -C "$d" -c user.name=t -c user.email=t@t.invalid commit -qm f && out=$(cd "$d" && python3 "$f" run --dry-run --lanes-dir "$d-out" alpha=T-0001) && printf "%s\n" "$out" | grep -qF "$d-out/alpha" && test ! -e "$d-out"`
- The selftest no longer expects the sibling dir: `! grep -nE '\{rr\}-fanout' plugins/sdlc-lite/scripts/fanout.py`
- fanout.py no longer names the sibling default: `! grep -n '<toplevel>-fanout' plugins/sdlc-lite/scripts/fanout.py`
- Observable: `selftest()` contains an `expect` for the default dir under `.worktrees/fanout` and an `expect` for the unignored-`.worktrees/` refusal (exit 2, stderr naming `.gitignore`).

## Step 2: Repair docs for the new lanes dir
level: L2
### Do
- `CLAUDE.md`, the `scripts/fanout.py` bullet (line 31):
  - Replace "under the sibling `<toplevel>-fanout` (`--lanes-dir` overrides)" with the new default `<toplevel>/.worktrees/fanout/<lane>`, where `--lanes-dir` overrides.
  - State that preflight refuses (exit 2, naming the fix of adding `.worktrees/` to `.gitignore`) when `.worktrees/` is not git-ignored. An explicit `--lanes-dir` inside the tree must be ignored too.
  - Add the caveat: `.gitignore` does not exclude `.worktrees/` from vitest, tsc, or file watchers, so a project must exclude it in their config. Node module resolution walks up from a lane worktree into the main tree's `node_modules`.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`:
  - Near the "Run from the project root" paragraph, name the default lanes dir `.worktrees/fanout/<lane>`, the `.gitignore` requirement, and the refusal. Step 1 already shows a refusal from the dry run.
  - Add the same vitest/tsc/file-watcher and `node_modules` caveat.
  - Keep the words `interactive`, `run_in_background`, `notification`, `sleep`, and `SDLC_HEADLESS` intact, because check.py enforces them.
- `.claude/agents/sdlc-lite-author.md`: add a learned-hazard line saying fanout lanes live in the gitignored `<toplevel>/.worktrees/fanout`, not a sibling dir, and repeating the vitest/tsc/watcher and `node_modules` caveat. Keep the existing sync line (line 20).
- Do not edit the user-level git-bare-repo-setup skill.
### Acceptance criteria
- No tracked doc outside `.sdlc/` names the sibling default: `! git grep -n -e '<toplevel>-fanout' -- . ':!.sdlc'`
- `grep -q '\.worktrees/fanout' CLAUDE.md`
- `grep -q '\.worktrees/fanout' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -q '\.worktrees/fanout' .claude/agents/sdlc-lite-author.md`
- `grep -q 'vitest' CLAUDE.md`
- `grep -q 'node_modules' CLAUDE.md`
- `grep -q 'vitest' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -q 'node_modules' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -q 'tsc' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -q '\.gitignore' plugins/sdlc-lite/skills/fanout/SKILL.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- `<toplevel>` is the toplevel of the worktree fanout runs from. Run from a linked worktree (for example `.worktrees/tickets-17`), the lanes nest under that worktree's own `.worktrees/fanout`, not the main checkout's. That matches the handoff's wording but may surprise a user. It works only because the linked worktree's `.gitignore` also ignores `.worktrees/`.
- Relaxing the "lanes live outside the work tree" rule could let tree-walking tools descend into lane worktrees. The shipped scripts read fixed roots (`.sdlc`, `git worktree list`), and this repo already nests worktrees under `.worktrees/`, so the risk is low. Project tooling (vitest, tsc, watchers) is the documented caveat.
- The default-dir runtime check is a dry run only. A full default-dir run with the stub driver is not required, so git status cleanliness with lanes inside the tree relies on `.gitignore` working as git documents.
- The user-level git-bare-repo-setup skill may still describe the sibling convention. It is out of scope and must be listed for the user in the final report.
