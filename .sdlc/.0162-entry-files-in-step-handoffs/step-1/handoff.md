## Task goal
A role working on a plan step reads the entry files that govern the files it changes, on Claude Code and on Codex alike.

## Step 1: steps.py lint refuses a missing `### Read first` path
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first. It is the nearest entry for every file in this step.

In `plugins/sdlc-lite/scripts/steps.py`:
- Add a helper that returns the listed paths of one step block. It reads the lines under a `### Read first` heading, up to the next `## ` or `### ` line, and leaves out fenced lines. It takes each list item that holds a code span, and the path is the text of that span.
- In `lint_steps`, resolve each listed path against the git toplevel of the plan file's folder, using the existing `git_toplevel`. Outside git, resolve it against that folder. A path that does not exist adds this finding: `steps: <plan> step <n>: ### Read first lists a path that does not exist: <path>`.
- `lint_or_fail` then refuses with the usual `plan defect` last line. Because `split` shares `lint_or_fail`, `split` refuses too.
- A step with no subsection stays valid.
- `swap` calls `lint_steps` on a synthetic block that has no subsection, so `swap` is unaffected.
- `split` already copies the subsection verbatim. Do not change that.

Update the module docstring for `lint` and `split`. Name `### Read first`, the one-line item form ``- `<path>` ``, the path base, and the refusal.

Add selftest case (r). It uses a temp git repo so the toplevel base is exercised. Use exactly these check names:
- `(r) lint accepts a ### Read first path that exists`
- `(r) lint refuses a ### Read first path that does not exist`
- `(r) split copies ### Read first into the step handoff`

In `docs/maintenance/sdlc-internals.md`, add the `### Read first` path check to the `scripts/steps.py` entry. That keeps the reference current.
### Acceptance criteria
- ``d=$(mktemp -d) && git -C "$d" init -q && mkdir -p "$d/sub" "$d/.sdlc/t" && touch "$d/sub/AGENTS.md" && printf '## Step 1: x\nlevel: L1\n### Read first\n- `sub/AGENTS.md`\n### Do\nd\n### Acceptance criteria\n- ok\n' > "$d/.sdlc/t/ok.md" && sed "s#sub/AGENTS#gone/AGENTS#" "$d/.sdlc/t/ok.md" > "$d/.sdlc/t/bad.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/.sdlc/t/ok.md" && { python3 plugins/sdlc-lite/scripts/steps.py lint "$d/.sdlc/t/bad.md" > "$d/out" 2>&1; test $? -eq 1; } && grep -qF gone/AGENTS.md "$d/out" && grep -qF "plan defect" "$d/out"``
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -qF 'ok: (r) lint accepts a ### Read first path that exists'`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -qF 'ok: (r) lint refuses a ### Read first path that does not exist'`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -qF 'ok: (r) split copies ### Read first into the step handoff'`
- `grep -qF '### Read first' plugins/sdlc-lite/scripts/steps.py`
- `grep -qF 'Read first' docs/maintenance/sdlc-internals.md`
