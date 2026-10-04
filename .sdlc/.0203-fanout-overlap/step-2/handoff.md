## Task goal
Add a merge-time file-overlap check to fanout.py.

## Step 2: Dry-run overlap of planned scope allow-lists
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Target: `plugins/sdlc-lite/scripts/fanout.py`, covering a new `planned_scope`, `print_plan`, the docstring's `--dry-run` paragraph and the selftest. Depends on: step 1 (same file).

`steps.py` is not edited, because it is outside the owning files. The parse is composed from the existing public helpers that `fanout.py` already imports through `import steps`: `steps.criteria_indexed`, `steps.list_item`, `steps.line_spans`, `steps.INVERT_GREP_RE`, `steps.widen_forms` and `steps.widen_listed`. These are the forms `steps.py widen` recognizes (F `grep -vxF -e`, E `grep -vxE "..."`, A `grep -vE "^(...)$"`; `steps.py:1526-1538`), and design.md line 68 settles this choice ("parsed with the forms `widen` already recognizes").

`planned_scope(root, slug)` returns the set of allow-listed paths, or `None` when the ticket is not planned:
- It reads every `root/<slug>/step-<n>/handoff.md` whose dir name fully matches `step-\d+` (a `.superseded-<k>` dir never counts).
- For each line from `criteria_indexed` that is a `list_item`, it takes each `line_spans` span containing `git diff --name-only` that matches `INVERT_GREP_RE`.
- For each `widen_forms` match, it takes the entries from `widen_listed`. E and A entries are ERE-unescaped with `re.sub(r'\\(.)', r'\1', e)`.
- It returns the union, or `None` when no step handoff yields an entry.

`print_plan` adds lines after the lane blocks and before the gate lines:
- One line per pair of tickets in different lanes whose scopes intersect, in spec and ticket order: `overlap (planned scope): <laneA> <idA> and <laneB> <idB>: <paths sorted, joined ", ">`. Tickets in the same lane run in sequence and are not compared.
- With no such pair, the line `overlap (planned scope): none`.
- When any ticket is unplanned, or belongs to an external lane (its folder lives on the branch), one line `overlap (planned scope): not planned, checked at merge time: <ids joined ", ">`.

The dry run still creates nothing.

Selftest case 14:
- Repo fixture:
  - `a` T-0001, whose `step-1/handoff.md` has an `### Acceptance criteria` item with the code span `` `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . | grep -vxF -e shared.txt -e a.txt)"` ``;
  - `b` T-0002, whose step-1 span uses the E form `grep -vxE "shared\.txt|b\.txt"`;
  - `c` T-0003 with no step dir;
  - `d` T-0004, whose step-1 span uses `grep -vxF -e b.txt`.
- `--dry-run alpha=T-0001 beta=T-0002,T-0003` prints `overlap (planned scope): alpha T-0001 and beta T-0002: shared.txt` and `overlap (planned scope): not planned, checked at merge time: T-0003`. These literals appear verbatim in the selftest.
- Negative control: `--dry-run alpha=T-0001 beta=T-0004` prints `overlap (planned scope): none` and no pair line.
- Both runs create no branch, worktree or lanes dir.

Existing dry-run asserts use substring checks, so they stay green. Focused check: `python3 plugins/sdlc-lite/scripts/fanout.py selftest`.
### Acceptance criteria
- `grep -qF 'overlap (planned scope): alpha T-0001 and beta T-0002: shared.txt' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF 'overlap (planned scope): none' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF 'overlap (planned scope): not planned, checked at merge time: T-0003' plugins/sdlc-lite/scripts/fanout.py`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/fanout.py)"`
- The verifier observes the negative control: in a temp copy of `plugins/sdlc-lite` outside the repo, `planned_scope` is made to return `None` and that copy's selftest is run. It exits 1 with a miss naming case 14. The real tree is never edited.
