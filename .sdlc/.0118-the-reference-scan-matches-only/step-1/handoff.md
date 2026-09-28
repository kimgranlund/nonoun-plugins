## Task goal
When `tickets.py close` (numbered mode) or `tickets.py archive` renames `NNNN-<slug>` to `.NNNN-<slug>`, its reference scan also finds (and with `--rewrite-refs` rewrites) references to the folder written as a path relative to the citing file (`../0003-x/`, `../../.sdlc/0003-x/handoff.md`) or as an absolute path (`/abs/toplevel/.sdlc/0003-x`), not only the literal toplevel-relative `<rel>/<slug>`, so those references no longer break silently on rename.

## Step 1: Resolve relative and absolute path tokens in the reference scan
level: L3
### Do
In `plugins/sdlc-lite/scripts/tickets.py`, extend `outside_refs` and `rewrite_files`. Both are shared by `cmd_close` (around line 641) and `cmd_archive` (around line 846).

Discovery:
- Keep a single `git grep --untracked -I -l -z --full-name -F` call from the toplevel, with the same GIT_ENV_DROP env.
- Grep on the folder name `<slug>` (for example `0003-x`) instead of `<rel>/<slug>`.
- Drop hits the same way as today: files under `<rel>/<slug>/` and `<rel>/roadmap.md`.
- Keep a hit file only if it holds at least one reference:
  - (a) Today's literal substring `<rel>/<slug>`. Keep this exact rule, so existing detection is unchanged.
  - (b) A path-like token that resolves to `<top>/<rel>/<slug>` or a path under it.
- A path-like token is a maximal run with no whitespace, quotes, backticks, parens, or angle or square brackets.
- Strip trailing sentence punctuation from a token before resolving it.
- A token resolves if it names `<slug>` as a whole path component and `os.path.normpath` of any of these lands on `<top>/<rel>/<slug>` or under it:
  - the token joined to the citing file's own directory;
  - the token as a toplevel-relative path;
  - the token as an absolute path.

Rewrite:
- `--rewrite-refs` keeps today's byte replace of `<rel>/<slug>` → `<rel>/.<slug>`.
- For each resolving token, it also turns only that token's `<slug>` path component into `.<slug>`, keeping the token's form. All other bytes stay unchanged.
- Adjust the `rewrite_files` signature and its two callers as needed.
- In archive, rewrites still run before any rename, and relative tokens resolve against each file's pre-rename location.

Must not change:
- Refusal text, the `rewrite <file>` dry-run lines, the `; rewrote refs in ...` suffix, CLI flags, and "every refusal writes nothing".
- Stdlib only.
- A bare `0003-x` word is not a reference.
- A path that resolves elsewhere is not a reference: `other/0003-x/...`, or `../0003-x/` written from `docs/`.
- Self-references from inside the moving folder stay out of scope.

Selftest: add cases next to the existing `(u) refs` and `archive refs` blocks (around lines 1567 and 1762). Prove all of the following:
- Each of these three references is refused without `--rewrite-refs`, listed by `--dry-run --rewrite-refs`, and rewritten correctly with `--rewrite-refs`, for both close and archive:
  - `../0003-x/filer-L1.md` from a file inside another ticket folder;
  - `./0003-x/handoff.md` from a file directly in the ticket root;
  - an absolute path.
- Negative controls leave the close unblocked and the file byte-identical: a bare `0003-x` word, `other/0003-x/handoff.md`, and `../0003-x/` written from `docs/spec.md`.

Update the `outside_refs`, `rewrite_files` and `cmd_close` docstrings. Leave the module help text for Step 2.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 and prints `tickets selftest: PASS`
- Close refuses on a relative reference from another ticket folder and writes nothing: `d=$(mktemp -d) && r="$d/r" && mkdir -p "$r/docs" && git -C "$r" init -q && T=plugins/sdlc-lite/scripts/tickets.py && python3 "$T" --root "$r/.sdlc" new idea x --numbered >/dev/null && python3 "$T" --root "$r/.sdlc" new idea y --numbered >/dev/null && printf "see ../0001-x/filer-L1.md\n" > "$r/.sdlc/0002-y/notes.md" && ! python3 "$T" --root "$r/.sdlc" close 0001-x --reason r 2>"$d/err" && grep -qF .sdlc/0002-y/notes.md "$d/err" && test -d "$r/.sdlc/0001-x"`
- Close `--rewrite-refs` rewrites that relative reference and keeps its form: `d=$(mktemp -d) && r="$d/r" && mkdir -p "$r/docs" && git -C "$r" init -q && T=plugins/sdlc-lite/scripts/tickets.py && python3 "$T" --root "$r/.sdlc" new idea x --numbered >/dev/null && python3 "$T" --root "$r/.sdlc" new idea y --numbered >/dev/null && printf "see ../0001-x/filer-L1.md\n" > "$r/.sdlc/0002-y/notes.md" && python3 "$T" --root "$r/.sdlc" close 0001-x --reason r --rewrite-refs >/dev/null && test "$(cat "$r/.sdlc/0002-y/notes.md")" = "see ../.0001-x/filer-L1.md"`
- Archive `--dry-run --rewrite-refs` lists the relatively citing file: `d=$(mktemp -d) && r="$d/r" && mkdir -p "$r/docs" && git -C "$r" init -q && T=plugins/sdlc-lite/scripts/tickets.py && python3 "$T" --root "$r/.sdlc" new idea x --numbered >/dev/null && python3 "$T" --root "$r/.sdlc" new idea y --numbered >/dev/null && printf "see ../0001-x/filer-L1.md\n" > "$r/.sdlc/0002-y/notes.md" && perl -pi -e "s/^status:\s*\w+/status: done/" "$r/.sdlc/0001-x/handoff.md" && python3 "$T" --root "$r/.sdlc" archive --dry-run --rewrite-refs > "$d/out" && grep -qxF "rewrite .sdlc/0002-y/notes.md" "$d/out"`
- A `./`-relative link from a file in the ticket root is rewritten: `d=$(mktemp -d) && r="$d/r" && mkdir -p "$r/docs" && git -C "$r" init -q && T=plugins/sdlc-lite/scripts/tickets.py && python3 "$T" --root "$r/.sdlc" new idea x --numbered >/dev/null && python3 "$T" --root "$r/.sdlc" new idea y --numbered >/dev/null && printf "[x](./0001-x/handoff.md)\n" > "$r/.sdlc/index.md" && python3 "$T" --root "$r/.sdlc" close 0001-x --reason r --rewrite-refs >/dev/null && test "$(cat "$r/.sdlc/index.md")" = "[x](./.0001-x/handoff.md)"`
- (guard) An absolute reference is refused, then rewritten keeping its absolute form: `d=$(mktemp -d) && r="$d/r" && mkdir -p "$r/docs" && git -C "$r" init -q && T=plugins/sdlc-lite/scripts/tickets.py && python3 "$T" --root "$r/.sdlc" new idea x --numbered >/dev/null && python3 "$T" --root "$r/.sdlc" new idea y --numbered >/dev/null && printf "see %s\n" "$r/.sdlc/0001-x/handoff.md" > "$r/docs/spec.md" && ! python3 "$T" --root "$r/.sdlc" close 0001-x --reason r 2>"$d/err" && grep -qF docs/spec.md "$d/err" && python3 "$T" --root "$r/.sdlc" close 0001-x --reason r --rewrite-refs >/dev/null && test "$(cat "$r/docs/spec.md")" = "see $r/.sdlc/.0001-x/handoff.md"`
- (guard) Negative controls do not block and stay untouched: `d=$(mktemp -d) && r="$d/r" && mkdir -p "$r/docs" && git -C "$r" init -q && T=plugins/sdlc-lite/scripts/tickets.py && python3 "$T" --root "$r/.sdlc" new idea x --numbered >/dev/null && python3 "$T" --root "$r/.sdlc" new idea y --numbered >/dev/null && printf "see 0001-x and other/0001-x/handoff.md and ../0001-x/\n" > "$r/docs/spec.md" && python3 "$T" --root "$r/.sdlc" close 0001-x --reason r --rewrite-refs > "$d/out" && test "$(cat "$r/docs/spec.md")" = "see 0001-x and other/0001-x/handoff.md and ../0001-x/" && ! grep -q rewrote "$d/out" && test -d "$r/.sdlc/.0001-x"`
- Red before, green after: in a `git worktree add <tmp> HEAD` copy, replace only the copy's `outside_refs` and `rewrite_files` with the originals from HEAD. The new selftest cases for the two relative references must fail there. The existing cases must pass.
- The existing `(u) refs` and `archive refs` selftest expectations are not edited: `git diff HEAD -- plugins/sdlc-lite/scripts/tickets.py` shows only added lines inside those two blocks.
