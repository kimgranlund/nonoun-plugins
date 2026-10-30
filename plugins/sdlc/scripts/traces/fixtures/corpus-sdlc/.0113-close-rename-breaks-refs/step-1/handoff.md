## Task goal
Closing a ticket in numbered mode never leaves main with broken references to its folder.

## Step 1: close lists and refuses on outside references to the ticket folder, with a --rewrite-refs opt-in
level: L3
### Do
Edit `plugins/sdlc/scripts/tickets.py` only.

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
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && ! python3 "$T" close 0001-x 2>err && grep -q docs/spec.md err && test -d .sdlc/0001-x && ! test -e .sdlc/.0001-x)`
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && ! python3 "$T" close 0001-x 2>err && grep -q docs/spec.md err && test -d .sdlc/0001-x)`
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && ! python3 "$T" close 0001-x --reason done 2>err && grep -q docs/spec.md err && test -d .sdlc/0001-x)`
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close 0001-x --rewrite-refs >out 2>&1 && grep -q docs/spec.md out && grep -qF '.sdlc/.0001-x/handoff.md' docs/spec.md && ! grep -qF '.sdlc/0001-x/' docs/spec.md && test -d .sdlc/.0001-x)`
- `(T=$(git rev-parse --show-toplevel)/plugins/sdlc/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close 0001-x --dry-run --rewrite-refs >out && grep -qx 'rewrite docs/spec.md' out && git diff --quiet && test -d .sdlc/0001-x)`
- (guard) `(T=$(git rev-parse --show-toplevel)/plugins/sdlc/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && mkdir docs && echo 'see .sdlc/0001-x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close 0001-x --force >/dev/null && test -d .sdlc/.0001-x && grep -qF '.sdlc/0001-x/handoff.md' docs/spec.md)`
- (guard) `(T=$(git rev-parse --show-toplevel)/plugins/sdlc/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && echo 'see .sdlc/0001-x/handoff.md' >> .sdlc/0001-x/handoff.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close 0001-x >/dev/null && test -d .sdlc/.0001-x)`
- (guard) `(T=$(git rev-parse --show-toplevel)/plugins/sdlc/scripts/tickets.py; d=$(mktemp -d) && git -C "$d" init -q && cd "$d" && python3 "$T" new feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/x/filer-L1.md && mkdir docs && echo 'see .sdlc/x/handoff.md' > docs/spec.md && git add -A && git -c user.email=a@b -c user.name=a commit -qm x && python3 "$T" close x >/dev/null && test -d .sdlc/x)`
- (guard) `(T=$(git rev-parse --show-toplevel)/plugins/sdlc/scripts/tickets.py; d=$(mktemp -d) && cd "$d" && python3 "$T" new --numbered feature x >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > .sdlc/0001-x/filer-L1.md && echo 'see .sdlc/0001-x/handoff.md' > spec.md && python3 "$T" close 0001-x >/dev/null && test -d .sdlc/.0001-x)`
- (guard) `python3 plugins/sdlc/scripts/tickets.py selftest`
- `grep -qF -- '--rewrite-refs' plugins/sdlc/scripts/tickets.py`
- Observable: the tickets.py selftest holds new `(u)` cases for the refusal, the untracked file, `--reason`, `--rewrite-refs`, the dry run, `--force`, and both negative controls. Deleting the new scan call from `cmd_close` makes `python3 plugins/sdlc/scripts/tickets.py selftest` report FAIL. The verifier checks this in a throwaway copy, never in the tree.
