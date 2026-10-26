---
name: git-bare-repo-setup
description: >
  Set up, operate, and migrate to a bare-clone + sibling-worktrees local dev layout
  (git clone --bare, one worktree per branch, no privileged "main checkout"). Use when
  creating a bare layout for a repo, adding/removing branch worktrees, migrating an
  existing normal clone, or diagnosing tooling that breaks under the layout (branch -d
  refusals, lockfile/bootstrap assumptions, path-detection in scripts). Carries the
  gen-ui-kit reference implementation (LLD-0015) and its learned pitfalls.
---

# git-bare-repo-setup

A living record of the bare-clone + sibling-worktrees layout: the generic mechanics, the
gen-ui-kit reference implementation (gh#2578, LLD-0015, PRs #2579/#2582), and every pitfall
paid for so far. Update this file when a new lesson lands — stale context is a defect.

## The layout

    <project>/               # layout root — NOT a git repo itself
      .bare/                 # the bare clone (GIT_DIR); no working tree
      main/                  # worktree for main
      fix-1234-thing/        # one sibling worktree per branch
      2578-feature/          # ...

- `git clone --bare <url> <project>/.bare`, then `echo "gitdir: ./.bare" > <project>/.git`
  is the classic hand-rolled shape (per the metal3d "worktree like a boss" article); a repo
  with its own setup script (below) does this plus fetch-refspec repair in one command.
- **Fetch refspec must be fixed after a bare clone** — bare clones default to no
  `remote.origin.fetch` refspec, so `git fetch` updates nothing. Set:
  `git -C .bare config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"` then
  `git fetch`.
- Every worktree shares one object store and ref namespace via `.bare`
  (`git rev-parse --git-common-dir` from any sibling resolves into it).
- `main` is just another sibling — **no privileged checkout exists**. Any tooling that
  assumes "the main checkout" (to copy files from, to resolve paths against) must be
  reworked to resolve via `git-common-dir` or a file staged in `.bare` instead.

## Daily operations

- New branch worktree: `git worktree add ../<name> -b <branch>` from any sibling (or the
  repo's own wrapper, e.g. gen-ui-kit's `scripts/dev/add-branch-worktree.mjs <branch>
  [--base <ref>]`, runnable from anywhere in the layout).
- List everything: `git worktree list` from any sibling — shows the whole estate.
- Remove: `git worktree remove <path>` then `git branch -d <branch>`.
- Dev servers: one per worktree, foreground, each on its own port. A "live view of main"
  is the `main` sibling running dev on its reserved port; feature worktrees pick other
  ports. Never share a server across worktrees.
- Per-worktree installs: each sibling gets its own `node_modules`. With pnpm + a shared
  virtual store keyed off `git-common-dir` (gen-ui-kit: gh#1791,
  `<git-common-dir>/pnpm-virtual-store/<lockfile-hash>`), a fresh sibling's install is
  mostly hardlinks — cheap. Install-shape rules still apply per worktree (gen-ui-kit:
  dist-bundle regen only under an npm-ci-shaped install; keep one npm-shaped sibling for
  release work while the rest stay pnpm).

## Pitfalls (each one was paid for — do not relearn)

1. **`git branch -d` checks ancestry against HEAD, not origin/main.** A branch fully
   merged into `origin/main` still gets "not fully merged" if your current checkout sits
   behind (or off) main. Seen live in gen-ui-kit (repo-cleaner firing 2026-08-31: primary
   was on a stale PR branch, `main-latest` refused; returned to main → `-d` cleared).
   Under the bare layout this bites whenever the worktree you run from is behind — verify
   with `git merge-base --is-ancestor <branch> origin/main` before escalating to `-D`.
2. **Gitignored files are invisible to `git status --porcelain`.** A migration/cleanup
   script that gates on a "clean tree" via porcelain alone will silently delete untracked
   ignored files (`.env`, local configs) in its sweep. Check `git status --ignored` too
   and refuse on anything ignored-but-unaccounted-for. (P0 caught by code-checker in
   gen-ui-kit's `migrate-to-bare-clone.mjs`, reproduced live, fixed + selftested.)
3. **Gitignored-but-required files need a home outside every worktree.** gen-ui-kit's
   `pnpm-lock.yaml` is gitignored; the old bootstrap copied it "from the main checkout",
   which doesn't exist under this layout. Resolution order now: (1) the current worktree,
   (2) a copy staged in `.bare` itself (seeded at setup, refreshed on lockfile change),
   (3) fail with the existing error. Generalize: stage such files in `.bare`/layout root.
4. **Path-shape detection in scripts breaks.** Any script that detects "am I in a
   worktree of repo X" by path substring (`.claude/worktrees/`, nested-dir patterns) needs
   a sibling-layout branch added as an OR, not a replacement (gen-ui-kit: check-links.mjs,
   isolation-harness.mjs, check-no-live-readers.mjs). Prefer `git rev-parse
   --git-common-dir` comparisons over path-string matching for new code.
5. **`origin/HEAD` may not resolve in a bare clone** — deriving "the default branch's
   sibling name" from it can silently fall back wrong (mis-derivation defaulting to
   `main` found in gen-ui-kit's migrate script). Resolve explicitly
   (`git remote show origin`, or `git symbolic-ref refs/remotes/origin/HEAD` after
   `git remote set-head origin -a`) and fail loudly if unknown.
6. **Memoize git subprocess calls in hot loops** — per-file `git rev-parse` in a
   check-script loop is a real slowdown across many worktrees; resolve once per run.
7. **Migration is opt-in and dry-run by default.** Converting a live normal clone moves
   real state (stashes, untracked files, registered worktrees of the old `.git`). Run the
   dry-run, read the plan, then `--apply`. Migrate AFTER any in-flight release/campaign,
   not during.
8. **Fleet/agent tooling placement is an open risk**: Claude Code's
   `Agent(isolation:"worktree")` creates its worktrees relative to the session's repo —
   where those land under a bare layout (and whether cleanup finds them) is UNVERIFIED.
   Verify on the real layout post-migration before relying on it; until then, agent
   worktrees/clones stay on their own conventions. (Documented gap in gen-ui-kit's
   worktrees.md and PR #2582's body.)
9. **Independent clones are orthogonal.** A fleet of scratch clones (gen-ui-kit's
   `.scratch/gen-ui-kit-*`) are full clones, not worktrees — the bare layout neither
   helps nor hurts them. Don't fold them into a migration.

## Reference implementation (gen-ui-kit, LLD-0015)

- `docs/ops/lld/lld-0015-bare-clone-worktree-layout.md` — the ratified design (scope
  ruled option (b), operator ruling 2026-08-31: support the layout AND migrate the repo's
  own worktree machinery onto it).
- `scripts/dev/setup-bare-clone.mjs <repo-url> [<target-dir>]` — one-command fresh setup
  (bare clone, refspec, `main` sibling, lockfile seeding). Selftested.
- `scripts/dev/add-branch-worktree.mjs <branch> [--base <ref>]` — sibling minting.
- `scripts/dev/migrate-to-bare-clone.mjs [--apply]` — converts a normal clone; dry-run
  default; refuses on ignored-but-unaccounted files (pitfall 2); seeds the lockfile.
- `scripts/dev/bootstrap-worktree.mjs` — unchanged CLI; lockfile resolution per pitfall 3.
- Landed via PR #2579 (LLD) + PR #2582 (implementation, `Closes #2578`).

## Setup checklist (any repo)

1. `git clone --bare <url> <project>/.bare` (or the repo's setup script, which does 1-4).
2. Fix the fetch refspec (Pitfalls-free fetch) and `git fetch`.
3. Add the default-branch sibling: `git worktree add ../main main`.
4. Stage gitignored-but-required files (lockfiles, local env templates) in `.bare`.
5. Per new branch: add-worktree → bootstrap install → dev server on its own port.
6. Audit repo scripts for pitfalls 1/3/4/5 before trusting gates run from a sibling.

## Still to learn (update on migration)

- Real-world `migrate-to-bare-clone.mjs --apply` run on the primary gen-ui-kit checkout
  (planned post-v0.8.56): record what the dry-run missed, if anything.
- Pitfall 8's verification result: where `Agent(isolation:"worktree")` worktrees land
  under the bare layout, and whether hygiene tooling sees them.
- Whether the 7 retired `.claude/worktrees/` entries migrate or just get removed first.
