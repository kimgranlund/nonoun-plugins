<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `tickets.py close <slug> --dry-run` also list proposed, ready, and blocked tickets that exist only in another git worktree's same-relative ticket root, tagged with that worktree's name. Local lines and the `expect` digest stay unchanged, and the docs must say the listing covers other worktrees.

## Step 1: List other-worktree open tickets in the close dry run, with selftest
level: L2
### Do
In `plugins/sdlc-lite/scripts/tickets.py`, `cmd_close`, in the `if dry_run:` block (about lines 678 to 685):
- Keep the existing local `opens` lines exactly as they are: local tickets, id order, byte-identical.
- Build `other_opens` from `worktree_roots(root)`:
  - For each other root, `load(r)` inside `try/except (OSError, UnicodeDecodeError): continue`, the same way `id_floor` does, so another tree's problems never fail this one.
  - Skip any entry whose `id` is not a string matching `ID_RE`.
  - Skip any id that exists in the local `ts` at any status. The local copy decides, so a ticket that is done locally but still open in a stale worktree copy is not listed.
  - Skip the closing ticket's `pid`.
  - Keep only status proposed, ready, or blocked.
  - Across other worktrees, keep each id once: the first worktree in `worktree_roots` order wins.
  - Emit `open T-NNNN <title> [<folder>] (worktree <name>)`, where `<name>` is the basename of that worktree's toplevel (the path from `git worktree list`, not the ticket root). A small helper that returns (worktree dir, root) pairs, or deriving the name from the root minus its relative part, is fine. Keep `worktree_roots`' existing callers' behavior unchanged.
  - Sort the other-worktree lines by id.
- Output order: header, follow-up lines, local open lines, other-worktree open lines, the rename line if any, the ack line if any, then `expect <digest>`. The digest stays `follow_digest(items)` and stays unchanged. The dry run still writes nothing anywhere. Outside git, `worktree_roots` returns [], so the output is unchanged.

Update the module docstring (the close --dry-run paragraph, around lines 29 to 32) and the `--dry-run` argparse help (around line 1684). Each must say that open tickets found only in another git worktree's same-relative root are listed after the local ones as `open T-NNNN <title> [<slug>] (worktree <name>)`, and that a ticket whose id exists locally is decided by the local copy. Include that literal `(worktree <name>)` text.

Add selftest cases in the existing `# ---- worktrees` block, which already has `git`, `m_root`, `w_root`, and `filer`. Use a fresh sub-repo if the shared fixture state is awkward. The cases must prove:
- (a) An open ticket only in the other worktree is listed with `(worktree wt...)`.
- (b) A ticket present locally is not listed twice. A locally done ticket whose other-worktree copy is open is not listed.
- (c) The digest line is identical with and without the other-worktree lines.
- (d) Outside git, the dry-run output is unchanged: the existing `solo` area or a new temp root.

The selftest must fail if the other-worktree listing is removed from `cmd_close`.
### Acceptance criteria
- `T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py && d=$(mktemp -d) && git -C "$d" init -q m && python3 $T --root "$d/m/.sdlc" new feature alpha Alpha >/dev/null && python3 $T --root "$d/m/.sdlc" new feature beta Beta >/dev/null && python3 $T --root "$d/m/.sdlc" new feature delta Delta >/dev/null && git -C "$d/m" add -A && git -C "$d/m" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit --no-verify -qm x && git -C "$d/m" worktree add -q ../wt -b wt && python3 $T --root "$d/wt/.sdlc" new feature gamma Gamma >/dev/null && git -C "$d/wt" add -A && git -C "$d/wt" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit --no-verify -qm y && git -C "$d/m" worktree add -q ../wt2 -b wt2 wt && perl -pi -e 's/^status: \w+/status: done/' "$d/m/.sdlc/beta/handoff.md" && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > "$d/m/.sdlc/alpha/filer-L1.md" && out=$(python3 $T --root "$d/m/.sdlc" close alpha --dry-run) && rm -rf "$d" && test "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" -eq 4 && test "$(printf '%s\n' "$out" | sed -n 2p)" = "open T-0003 Delta [delta]" && printf '%s\n' "$out" | sed -n 3p | grep -Eqx 'open T-0004 Gamma \[gamma\] \(worktree wt2?\)' && test "$(printf '%s\n' "$out" | sed -n 4p)" = "expect e3b0c44298fc"`
  - Main has alpha, beta, and delta. Gamma exists only in wt and wt2. Beta is done in main but open in the worktree copies.
  - The check expects exactly 4 lines: gamma listed once with its worktree, delta once without a suffix, beta absent, and the digest unchanged.
- (guard) `T=$(git rev-parse --show-toplevel)/plugins/sdlc-lite/scripts/tickets.py && d=$(mktemp -d) && python3 $T --root "$d/.sdlc" new feature alpha Alpha >/dev/null && python3 $T --root "$d/.sdlc" new feature beta Beta >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > "$d/.sdlc/alpha/filer-L1.md" && out=$(python3 $T --root "$d/.sdlc" close alpha --dry-run) && rm -rf "$d" && test "$out" = "$(printf 'T-0001 dry run: 0 proposed follow-up(s); nothing written\nopen T-0002 Beta [beta]\nexpect e3b0c44298fc')"` (outside git, the output is unchanged)
- `grep -qF '(worktree <name>)' plugins/sdlc-lite/scripts/tickets.py`
- `grep -q "(worktree wt" plugins/sdlc-lite/scripts/tickets.py` (the selftest asserts the other-worktree line)
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- Observable: in a scratch copy of `tickets.py` with the other-worktree lines dropped from the dry-run output, `python3 <copy> selftest` exits 1 and names a worktree dry-run case.

## Step 2: Docs say the dry-run open listing covers other worktrees
level: L1
### Do
State that `close --dry-run` also lists open (proposed, ready, blocked) tickets that exist only in another git worktree's same-relative ticket root, as `open T-NNNN <title> [<slug>] (worktree <name>)` after the local lines, with a local copy deciding any id it holds. Include the literal `(worktree <name>)` text in each place:
- `plugins/sdlc-lite/skills/file/SKILL.md` step 1.1 (line 12), where it describes the `open T-NNNN` lines. Also let step 1.2's likely-duplicate comparison cover these lines. Keep the existing `open T-NNNN` and `likely duplicate` strings that `check.py` requires.
- `plugins/sdlc-lite/skills/ticket/SKILL.md` item 4 (line 12), in the `--dry-run` sentence.
- `CLAUDE.md` Layout, `scripts/tickets.py` bullet, in the `close --dry-run lists ... open T-NNNN <title> [<slug>] line per other proposed, ready, or blocked ticket` clause.
- `.claude/agents/sdlc-lite-author.md` line 17, in the sentence "Keep `close --dry-run`/`--skip`/`--expect`, ... the dry run's `open T-NNNN` listing ...". Add that the listing includes other worktrees' open tickets as `(worktree <name>)`.

Make no code changes. No em dashes.
### Acceptance criteria
- `grep -qF '(worktree <name>)' plugins/sdlc-lite/skills/file/SKILL.md`
- `grep -qF '(worktree <name>)' plugins/sdlc-lite/skills/ticket/SKILL.md`
- `grep -qF '(worktree <name>)' CLAUDE.md`
- `grep -qF '(worktree <name>)' .claude/agents/sdlc-lite-author.md`
- (guard) `grep -qF 'open T-NNNN' plugins/sdlc-lite/skills/file/SKILL.md`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- `! git diff HEAD -- CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md | grep '^+' | grep -q '—'` (no em dashes added)

## Risks
- `git worktree list` order decides which worktree name a duplicated other-worktree id shows. The step 1 probe accepts `wt` or `wt2` for this reason.
- The step 1 probe uses `perl -pi` and `mktemp` in a temp dir outside the repo. If a setup command fails, the temp dir leaks.
- `check.sh` takes about 80 s.
- The worktree name comes from the worktree's toplevel basename. If a builder derives it from the ticket root instead, the probe fails: it would print `.sdlc`, not `wt`.
