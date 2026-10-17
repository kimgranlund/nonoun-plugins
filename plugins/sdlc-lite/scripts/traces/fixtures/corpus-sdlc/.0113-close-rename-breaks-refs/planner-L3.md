<!-- role=planner level=L3 model=fable effort=xhigh -->
## Goal
In numbered mode, `tickets.py close` refuses to rename `NNNN-<slug>` to `.NNNN-<slug>` while files outside the ticket folder still cite the old path. It lists those files and offers `--rewrite-refs` (rewrite them) or `--force` (close anyway), so a close never silently leaves main with broken references.

## Step 1: close lists and refuses on outside references to the ticket folder, with a --rewrite-refs opt-in
level: L3
### Do
Edit `plugins/sdlc-lite/scripts/tickets.py` only.

1. In `cmd_close`, when `archive` is true, scan for references after the existing refusals (already-closed, target exists, problems, status done) and before anything is written. This applies to every close path: filer, `--reason`, `--ack-warnings` and `--dry-run`.
   - The scan runs `git grep --untracked -lF <rel>/<slug>` from the repo toplevel. `<rel>` is the ticket root relative to the toplevel, for example `.sdlc/0001-x`. Resolve the toplevel the way `worktree_pairs` does: `git -C <anchor> rev-parse --show-toplevel`, dropping `GIT_ENV_DROP`.
   - Leave out every file under the ticket's own folder and `<root>/roadmap.md`. The folder moves with the ticket, and close regenerates the roadmap.
   - Outside git, or when git fails, there is no scan. That is the same rule as `worktree_pairs`.
2. A new `rewrite_refs=False` kwarg and a `--rewrite-refs` CLI flag on the `close` subparser control what happens with the hits:
   - No hits: no change in behavior.
   - Hits, and neither `--rewrite-refs` nor `--force`: refuse with `Fail`, writing nothing. The message names each file (toplevel-relative) and says to rerun with `--rewrite-refs` (rewrite them to `.<slug>`) or `--force` (close anyway, leaving them).
   - Hits with `--rewrite-refs`: in each listed file, replace the text `<rel>/<slug>` with `<rel>/.<slug>`. Do this after the handoff write, with the rename. Append `; rewrote refs in <files>` to the output.
   - Hits with `--force`: close as today and leave the files as they are.
   - `--dry-run` applies the same refusal. With `--rewrite-refs` it prints one `rewrite <file>` line per hit, placed before the `expect` line, and writes nothing.
   - `--reason` closes with `--rewrite-refs` too. Since `--reason` is incompatible with `--force` by current code? No: `--force` with `--reason` is allowed today (selftest case (o)), so keep that.
   - Plain slug folders never scan. They never move.
3. Add selftest cases in the `(u)` block. They build a throwaway git repo the way the existing worktree cases do, and skip when `git` is missing. Cover:
   - A committed file refuses and writes nothing.
   - An untracked file refuses too.
   - `--reason` refuses.
   - `--rewrite-refs` rewrites and closes.
   - `--dry-run --rewrite-refs` lists the files and writes nothing.
   - `--force` closes and leaves the file.
   - Negative controls: a reference only inside the ticket's own folder closes; plain mode never refuses.
4. Update the module docstring's `close` paragraph and the `Usage:` line to cover the new refusal and `--rewrite-refs`.

The failing tests land in the same step as the fix.
### Acceptance criteria
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && ! python3 "$T" close 0001-x 2>err && grep -q docs/spec.md err && test -d .sdlc/0001-x && ! test -e .sdlc/.0001-x)`
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && ! python3 "$T" close 0001-x 2>err && grep -q docs/spec.md err && test -d .sdlc/0001-x)`
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && ! python3 "$T" close 0001-x --reason done 2>err && grep -q docs/spec.md err && test -d .sdlc/0001-x)`
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close 0001-x --rewrite-refs >out 2>&1 && grep -q docs/spec.md out && grep -qF '.sdlc/.0001-x/handoff.md' docs/spec.md && ! grep -qF '.sdlc/0001-x/' docs/spec.md && test -d .sdlc/.0001-x)`
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close 0001-x --dry-run --rewrite-refs >out && grep -qx 'rewrite docs/spec.md' out && git diff --quiet && test -d .sdlc/0001-x)`
- (guard) `(T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close 0001-x --force >/dev/null && test -d .sdlc/.0001-x && grep -qF '.sdlc/0001-x/handoff.md' docs/spec.md)`
- (guard) `(T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && echo 'see .sdlc/0001-x/handoff.md' >> .sdlc/0001-x/handoff.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close 0001-x >/dev/null && test -d .sdlc/.0001-x)`
- (guard) `(T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/x/filer-L1.md && mkdir docs && echo 'see .sdlc/x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close x >/dev/null && test -d .sdlc/x)`
- (guard) `(T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py; d=$(mktemp -d) && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && echo 'see .sdlc/0001-x/handoff.md' > spec.md && python3 "$T" close 0001-x >/dev/null && test -d .sdlc/.0001-x)`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- `grep -qF -- '--rewrite-refs' plugins/sdlc-lite/scripts/tickets.py`
- Observable: the tickets.py selftest holds new `(u)` cases for the refusal, the untracked file, `--reason`, `--rewrite-refs`, the dry run, `--force`, and both negative controls. Deleting the new scan call from `cmd_close` makes `python3 plugins/sdlc-lite/scripts/tickets.py selftest` report FAIL. The verifier checks this in a throwaway copy, never in the tree.

## Step 2: Sync the docs and the /file flow with the reference refusal
level: L2
### Do
Document the refusal, `--rewrite-refs` and the `--force` escape wherever the numbered-mode dot-prefix rule is already described:
- `CLAUDE.md`: the `scripts/tickets.py` bullet, and the `close` numbered-mode sentence.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: the numbered-folders bullet.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the `.NNNN-<slug>` lines near 23 and 47.
- `.claude/agents/sdlc-lite-author.md`: add `--rewrite-refs` and the reference refusal to the sync line for the numbered-mode dot-prefix rule. Include the /file skill in that line.

In `plugins/sdlc-lite/skills/file/SKILL.md` step 3.1, add a branch for when the dry run refuses because files cite the ticket folder. Show the listed files, then ask with AskUserQuestion, options in this order:
1. "Rewrite references" (recommended): add `--rewrite-refs` to every later call.
2. "Leave open": stop.
3. "Close anyway": add `--force` to every later call.

An unattended run stops on this refusal and never rewrites or forces. No silent rewrite.

Change no code. Step 1's `plugins/sdlc-lite/scripts/tickets.py` change is uncommitted in the tree, because only a merge step commits, so `tickets.py` differs from HEAD by design: leave it exactly as step 1 left it, and never revert, restage, or commit it to satisfy a criterion. The tree may already hold these doc edits from a superseded attempt; then confirm each criterion, fix any gap, and report done.
### Acceptance criteria
- `grep -qF -- '--rewrite-refs' CLAUDE.md`
- `grep -qF -- '--rewrite-refs' plugins/sdlc-lite/skills/ticket/SKILL.md`
- `grep -qF -- '--rewrite-refs' plugins/sdlc-lite/skills/file/SKILL.md`
- `grep -qF -- '--rewrite-refs' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF -- '--rewrite-refs' .claude/agents/sdlc-lite-author.md`
- `grep -q 'Rewrite references' plugins/sdlc-lite/skills/file/SKILL.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `test -z "$(git diff --name-only HEAD -- plugins/sdlc-lite/scripts plugins/sdlc-lite/hooks | grep -v '^plugins/sdlc-lite/scripts/tickets.py$')"`: under `scripts/` and `hooks/`, the only file that differs from HEAD is step 1's `tickets.py`.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py close --help | grep -qF -- '--rewrite-refs'`: the flag the docs describe is in the tree's code, so step 1's change was not reverted to make `tickets.py` match HEAD.
- Observable: `git diff HEAD -- plugins/sdlc-lite/scripts/tickets.py` holds only step 1's work: the `outside_refs` helper, the `rewrite_refs` kwarg with its refusal, rewrite, and dry-run `rewrite <file>` lines in `cmd_close`, the `--rewrite-refs` flag in the parser and `main`, the `(u) refs:` selftest cases, and the docstring and `Usage:` edits. No hunk in that diff does anything else. The verifier reads the diff itself and never compares `tickets.py` against a commit, because step 1's change stays uncommitted until the lane's merge.

## Risks
- Step 2's six doc criteria are green in the current tree because the blocked attempt's doc edits are still there, uncommitted; each was red at HEAD (`git show HEAD:<file>` has no `--rewrite-refs` and no `Rewrite references`), so they discriminate. If the tree is reset before the rebuild they go red again and the builder redoes the edits.
- The scan matches the literal toplevel-relative path `<rel>/<slug>`. It misses references written relative to the ticket root (such as `../0001-x/` from another ticket's handoff) or with absolute paths, and it can over-match a longer name that starts with the same text, harmless because ids are unique.
- `--force` already means "override open warnings". Reusing it to skip the reference gate lets one flag bypass both gates. That is the handoff's option 1 wording; a separate flag would be a follow-up.
- `archive` renames folders too and gets no reference scan. It can still break references the same way; a follow-up ticket covers it.
- `fanout.py` closes tickets on the integration branch with a plain `close <slug>`; in a numbered-mode repo a hit now ends that ticket as `merged, close refused: <first line>` and the ticket stays open there for a person to rerun with `--rewrite-refs`. This repo uses plain slugs, so it is unaffected.
