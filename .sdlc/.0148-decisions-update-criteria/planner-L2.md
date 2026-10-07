<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add a script-checked `steps.py widen` route. When the conductor decides to widen a step's scope, the route rewrites the step's scope-guard criterion. Document it in the conductor and /chain contracts so that editing only the prose is no longer the documented way to widen scope.

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

## Step 2: Document the widen route in the conductor, /chain, and role contracts
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Document the route. Each doc names `steps.py widen` literally.

- **`plugins/sdlc-lite/skills/chain/SKILL.md`**:
  - Add item 9, "Scope widening". Trigger: a builder blocked only because a file it needs sits outside the step's scope criterion, when the conductor decides the file serves the task goal. Interactive runs confirm through AskUserQuestion. The decision is never recorded as prose alone.
  - Command: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py widen .sdlc/<task>/step-<n> <path>...`.
  - On exit 0: append `scope widened: step <n>: <its stdout line>` to the task handoff's `## Plan review`. Then run the builder at the blocked builder's level. That run is not a bump and gets no `## Previous attempt`. The widened block does not count toward the rubric's blocked-builder bump.
  - On exit 1: append a `scope decision: step <n>: <paths>` line and the stderr to `## Plan review`, then take the 4.2 replan path.
  - State why: the conductor names only paths and the script rewrites the check, so "never edit the criterion by hand" and "whoever writes the work never sets its check" both hold.
  - Reference item 9 from item 2 (builder blocked) as its one exception.
- **`plugins/sdlc-lite/agents/conductor.md`**: add the same route to the escalation bullet.
- **`plugins/sdlc-lite/skills/handoff-format/SKILL.md`**:
  - Add the `scope widened:` and `scope decision:` entries to `## Plan review`.
  - Add the step handoff's `## Scope widened` section, which `steps.py widen` writes.
- **`plugins/sdlc-lite/skills/level-rubric/SKILL.md`**: in the bump paragraph, a block resolved by `steps.py widen` never counts toward a bump.
- **`plugins/sdlc-lite/agents/planner.md`** rule 9: a `scope decision:` entry in `## Plan review` names paths the conductor allowed for that step. The replan widens that step's scope criterion to hold them. This is replan-time only. Do not change the plan-time scope-guard rules.
- **`plugins/sdlc-lite/scripts/check.py`**: add a `PLAN_DEFECT_DOCS` entry `'steps.py widen': ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md', 'skills/level-rubric/SKILL.md', 'scripts/steps.py')`.
- **Codex agents**: then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to regenerate them. Never hand-edit the TOML files.
### Acceptance criteria
- `grep -qF 'steps.py widen' plugins/sdlc-lite/agents/conductor.md`
- `grep -qF 'steps.py widen' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF 'steps.py widen' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'steps.py widen' plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `grep -qF 'scope decision:' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'scope decision:' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF "'steps.py widen'" plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`

## Step 3: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root. Fix any red that steps 1 and 2 introduced, in the files those steps changed. The shellcheck part of `check.sh` is skipped on this host because shellcheck is not installed. That is not a failure.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check`

## Risks
- `widen` recognizes only three allow-list forms: `grep -vxF -e`, `grep -vxE "..."`, and `grep -vE "^(...)$"`. Past plans also used an exact `test "$(git diff ...)" = "<file>"` and prefix `grep -v '^path$'` forms. Those forms refuse and fall back to the planner L3 replan with a `scope decision:` entry. That path is correct but slower. Changing how planners write scope guards is a non-goal.
- Rebuilding at the blocked builder's level after a widen is a conductor rule. `steps.py next` still prints `replan` for the blocked result until the new builder runs, so the chain and conductor docs must say that the widen route overrides that one `replan`.
- `widen` runs the widened span against the current tree. A blocked builder that already edited files outside even the widened set makes `widen` refuse, which routes to a replan. That is intended, but the conductor may need to name every such path.
- The live conductor behavior (deciding to widen in an unattended lane) is only documented here. A throwaway-project live run is not part of this plan.
