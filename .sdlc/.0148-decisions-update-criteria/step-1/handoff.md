## Task goal
A conductor decision that widens a step's scope edits the scope guard the criteria read, so the next builder does not block on the old guard.

## Step 1: Add `steps.py widen` with selftest and internals doc
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add a `widen` subcommand to `plugins/sdlc-lite/scripts/steps.py`: `widen <step dir> <path> [<path> ...] [--timeout SECONDS]`. Model it on `swap` and reuse its helpers: `criteria_indexed`, `list_item`, `line_spans`, `lint_steps`, `git_toplevel`, `base_sha`, `run_guard`, `tree_state`, `tree_changes`, `Fail`.

What it does:
1. **Check the inputs.** `<step dir>/handoff.md` must exist. Each path must be repo-relative and match `^[A-Za-z0-9._/@+-]+$`. A path must not start with `-` or `/`, and must not hold a `..` component.
2. **Find the scope criterion.** Exactly one criterion line (the `criteria_lines` region, a `-` or `*` list item) must have one command span that holds `git diff --name-only` and exactly one recognized allow-list form. There are three recognized forms:
   - (F) `grep -vxF` followed by one or more `-e <word>` args. Append ` -e <path>` after the last `-e` arg.
   - (E) `grep -vxE` followed by one single- or double-quoted pattern. Append `|<path>` inside the quotes, with the path ERE-escaped: backslash before each of `.^$*+?()[]{}|\`.
   - (A) `grep -vE` or `grep -E -v` with a quoted pattern `^(...)$`. Insert `|<escaped path>` before `)$`.

   Zero or several such lines, or an unrecognized form, is a refusal.
3. **Skip paths already listed.** A path is already listed when it is literally an `-e` word (F), or its escaped form is an alternative (E and A). If every path is already listed, print `widen: already applied`, exit 0, and write nothing.
4. **Check the rewritten line.** It must keep its `(guard)` tag and marker and lint clean (`lint_steps`, as swap does).
5. **Run the new span.** Run it under `bash -c` from the git toplevel. Set `SDLC_BASE_SHA` from `<step dir>/base-sha`, else HEAD, exactly as swap does. Refuse on a red span, a timeout, or a span that changed the work tree.
6. **Write.** Replace only the target line. Then append to the step handoff one `## Scope widened` section, created if missing and earlier items kept, with one item per added path: ``- `<path>`: allowed by a conductor scope decision (steps.py widen)``. This gives the builder the decision next to the criterion.
7. **Report.** Print one stdout line: `steps widen: <step dir>: added <paths> to the scope criterion: <new span>`.

Every refusal:
- writes nothing
- prints on stderr
- exits 1
- ends with the last line `plan defect: steps widen refused: <why>; replan this step (/chain 4.2)`

Add a `widen` usage entry to the module docstring, including the literal text `widen <step dir>`, and an argparse subparser. Add selftest cases, each named with the prefix `widen:`:
- (a) the F, E, and A forms apply; afterwards a widened file passes the span and a file outside the set fails it
- (b) rerunning gives `widen: already applied`, writes nothing
- (c) refusals: no scope line, two scope lines, an unrecognized form, a bad path (`../x`, `/x`, `-x`), a red new span. Each writes nothing and ends with the plan-defect line.
- (d) the span sees `SDLC_BASE_SHA` from `base-sha`.

Document the subcommand in the `scripts/steps.py` entry of `docs/references/sdlc-internals.md`, including the text `widen <step dir>`. Change no other file.
### Acceptance criteria
- Widening a `grep -vxF` scope criterion lets the widened file pass, and a file outside the set still fails: `d=$(mktemp -d) && S="$PWD/plugins/sdlc-lite/scripts/steps.py" && cd "$d" && git init -q r && cd r && git -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q --allow-empty -m a && mkdir -p .sdlc/t/step-1 && git rev-parse HEAD > .sdlc/t/step-1/base-sha && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nd\n### Acceptance criteria\n- \x60{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e a.txt | { ! grep -q .; }\x60\n' > .sdlc/t/step-1/handoff.md && touch a.txt && python3 "$S" widen .sdlc/t/step-1 b.txt && touch b.txt && span=$(python3 -c 'import re,sys; print(re.search(chr(96)+"(.+)"+chr(96), [l for l in open(sys.argv[1]) if "git diff --name-only" in l][0]).group(1))' .sdlc/t/step-1/handoff.md) && SDLC_BASE_SHA=$(cat .sdlc/t/step-1/base-sha) bash -c "$span" && touch c.txt && ! SDLC_BASE_SHA=$(cat .sdlc/t/step-1/base-sha) bash -c "$span"`
- Widening a `grep -vxE` criterion escapes the path, so the widened file passes and a lookalike `bxtxt` still fails: `d=$(mktemp -d) && S="$PWD/plugins/sdlc-lite/scripts/steps.py" && cd "$d" && git init -q r && cd r && git -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q --allow-empty -m a && mkdir -p .sdlc/t/step-1 && git rev-parse HEAD > .sdlc/t/step-1/base-sha && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nd\n### Acceptance criteria\n- \x60test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxE "a\\.txt")"\x60\n' > .sdlc/t/step-1/handoff.md && echo x > a.txt && git add a.txt && python3 "$S" widen .sdlc/t/step-1 b.txt && echo x > b.txt && git add b.txt && span=$(python3 -c 'import re,sys; print(re.search(chr(96)+"(.+)"+chr(96), [l for l in open(sys.argv[1]) if "git diff --name-only" in l][0]).group(1))' .sdlc/t/step-1/handoff.md) && SDLC_BASE_SHA=$(cat .sdlc/t/step-1/base-sha) bash -c "$span" && echo x > bxtxt && git add bxtxt && ! SDLC_BASE_SHA=$(cat .sdlc/t/step-1/base-sha) bash -c "$span"`
- A step with no scope criterion refuses with exit 1, a `plan defect:` last line, and an unchanged handoff: `d=$(mktemp -d) && S="$PWD/plugins/sdlc-lite/scripts/steps.py" && cd "$d" && git init -q r && cd r && mkdir -p .sdlc/t/step-1 && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nd\n### Acceptance criteria\n- \x60test -f a.txt\x60\n' > .sdlc/t/step-1/handoff.md && cp .sdlc/t/step-1/handoff.md h.bak && python3 "$S" widen .sdlc/t/step-1 b.txt 2> err.txt; test $? -eq 1 && tail -n 1 err.txt | grep -q '^plan defect:' && cmp -s h.bak .sdlc/t/step-1/handoff.md`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -qF 'ok: widen:'`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `grep -qF 'widen <step dir>' plugins/sdlc-lite/scripts/steps.py`
- `grep -qF 'widen <step dir>' docs/references/sdlc-internals.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/steps.py|docs/references/sdlc-internals.md" | { ! grep -q .; }`
