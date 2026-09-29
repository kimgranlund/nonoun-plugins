<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest`: pass. Evidence: on the built tree it exits 0 and prints 8 lines of the form `gate <name>: positive ok, negative ok` (layout-parsing, import-detection, create, preserve, idempotence, row-order, malformed-markers, check-mode). At `$SDLC_BASE_SHA` it prints only the 2 Step 1 gates and exits 0, so this is a gate-type criterion. I confirmed it can go red: a copy of onboard.py in /tmp with `preflight=False` made the selftest exit 1.
- `out=$(... selftest) && for g in layout-parsing ... check-mode; do ... grep -qxF "gate $g: positive ok, negative ok" || exit 1; done`: pass. Evidence: rc=0 on the built tree, rc=1 at the base worktree (the 6 new gate lines are missing), and rc=1 on the `preflight=False` mutant.
- `... git init -q && python3 "$s" setup && for f in AGENTS.md CLAUDE.md docs/AGENTS.md docs/CLAUDE.md docs/layout.md; do test -f "$f" || exit 1; done`: pass. Evidence: rc=0; stdout was `created AGENTS.md` through `created docs/layout.md`. At base rc=2 with `onboard.py setup: not implemented`.
- `... setup && python3 "$s" check && test -z "$(python3 "$s" setup --dry-run)"`: pass. Evidence: rc=0; check printed `current AGENTS.md`, `current CLAUDE.md`, `current docs/AGENTS.md`, `current docs/CLAUDE.md`, `present docs/layout.md`. At base rc=2.
- `... setup && grep -qF "Do not spawn another plugin's builder, planner, or reviewer agent in their place." AGENTS.md && grep -qxF "@AGENTS.md" CLAUDE.md && grep -qE "^<!-- sdlc-lite:managed:start v[0-9]+ sha256:[0-9a-f]{12} -->$" AGENTS.md`: pass. Evidence: rc=0; base rc=2. Independent checks:
  - I recomputed each marker hash with `awk` between the markers piped to `shasum -a 256 | cut -c1-12`, a different mechanism from the script's `digest()`. All four matched: AGENTS.md 76eefe83c59e, CLAUDE.md 336cc4fbf19b, docs/AGENTS.md e03afd75d335, docs/CLAUDE.md 336cc4fbf19b.
  - I extracted the five ```markdown blocks from the design's Templates section and compared them with the script constants: all 5 are `==` identical, with the same byte lengths (856, 91, 475, 223, 216).
- `... printf "# Mine\n\nkeep me\n" > AGENTS.md && cp AGENTS.md before.md && python3 "$s" setup && head -c ... AGENTS.md | cmp -s - before.md`: pass. Evidence: rc=0 (`updated AGENTS.md`); base rc=2. I also ran a CRLF probe on `user top\r\n\r\nkeep\r\n`: the prefix stayed byte-identical and the appended block uses CRLF.
- `... setup && printf "# mine\n" > CLAUDE.md && out=$(python3 "$s" check 2>&1); rc=$?; test "$rc" -ne 0 && ... grep -q "unmanaged"`: pass. Evidence: rc=0 on the built tree; base rc=2.
- `... out=$(python3 "$s" setup 2>&1); rc=$?; test "$rc" -eq 1 && ... grep -qF "not a Git work tree" && test -z "$(ls -A)"`: pass. Evidence: rc=0 on the built tree; base rc=1 (it printed "not implemented" instead). `check` outside Git gives the same result: it printed `onboard.py check: not a Git work tree; ...`, rc=1, and wrote 0 files.
- `... mkdir docs && printf "# Layout\n\n## Homes\n- maintenance/\n\n## Frozen paths\n" > docs/layout.md && ... grep -qF "docs/layout.md:4" && test ! -e AGENTS.md`: pass. Evidence: rc=0 on the built tree; base rc=1. `check` and `setup --dry-run` on a layout with a duplicate `## Homes` both printed `docs/layout.md:3: '## Homes' appears twice (first at line 2)`, exited 1, and wrote nothing.
- The Do items beyond the listed commands, checked by observed runs:
  - Gate bite (mutation test): I put each defect into a /tmp copy of onboard.py as the real implementation, and the matching gate printed FAIL.

    | Defect | Gates that failed |
    | --- | --- |
    | Rows 4 and 6 swapped | row-order, idempotence, check-mode |
    | Code-fence rule skipped in `find_block` | preserve, malformed-markers |
    | Unclosed start marker treated as no block | row-order, malformed-markers |
    | Wrap writes outside the markers | create, preserve, malformed-markers |
    | Preflight off | create |
    | No starter text | create |
    | Edited block labelled current | check-mode |
    | `check` always exits 0 | check-mode, malformed-markers |
    | Blank separator before an appended block | preserve |
    | Import detection ignores fences | import-detection |

    One mutant survived: changing `digest()` to hash the wrong input. The gates only check that marker and text agree with each other. The real hash is still correct, confirmed by the `shasum` check under criterion 5.
  - Rich fixture: topics counted through subfolders, README linked first, a single-document topic linked directly, homes listed by folder name, loose documents listed, and a frozen topic and an untracked topic skipped. No empty `docs/reference/` folder was created.
  - Adding a second document to a topic gave `stale docs/AGENTS.md` plus `missing docs/beta/*`, with rc=1. The dry-run diff showed the change, setup applied it, and `check` then exited 0.
  - A hand-edited block produced `edited AGENTS.md` on stderr and was left unchanged. `--force` replaced it, and `check` then exited 0.
  - Running from a subdirectory wrote the files at the Git top level.
  - The dry-run output applies cleanly with `git apply --check`.
  - I ran `check` and `setup --dry-run` against this repository's own tree in a base worktree. `git status` and the AGENTS.md/CLAUDE.md hashes were unchanged, and the size report was `AGENTS.md: 70 lines, over the 60-line target`.
- Neighbor checks: `git diff --check` rc=0; `python3 plugins/sdlc-lite/scripts/check.py` rc=0 (`ok: 18 role levels, 8 agents checked`); `python3 scripts/check-packaging.py` PASS.

## Out of scope changes
None. `git status` shows only `plugins/sdlc-lite/scripts/onboard.py` modified; the untracked files are this run's `.sdlc/.../step-2/` records. The diff against `$SDLC_BASE_SHA` removes only 8 lines: the old usage and docstring text, the argparse help strings, and the `not implemented` stub. The two Step 1 gates are unchanged and still pass.

Steelman of the one candidate finding I dropped:
- The finding: a line that begins `<!-- sdlc-lite:managed:start` but is not an exact marker is treated as malformed, where the design's "whole line" rule would treat it as ordinary text.
- The builder's rebuttal holds. The choice is documented in builder-L4.md. It only refuses to write, so no user bytes are at risk. It matches only at the start of a line, never inside a line or in a fence. No criterion or Do line is violated.

## For the next attempt
None.
