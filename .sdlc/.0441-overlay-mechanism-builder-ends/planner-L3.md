<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Role prompts can differ by level at generation time through `plugins/sdlc-lite/overlays/<role>.md`. `overlays/builder.md` carries only `## L1` and `## L5`, so only builder-L1, builder-L5 and their two Codex TOMLs change, and every other generated agent stays byte-identical.

## Step 1: Overlay mechanism in both generators, check.py item, and the builder L1 and L5 overlays
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Build the design in `.sdlc/.0440-per-tier-agent-prompts/architect-L1.md` exactly as written. Read all of it (Approach, Interfaces, Constraints and assumptions), and use its `## Carry forward` for the line references. Depends on: none.

1. `plugins/sdlc-lite/scripts/claude_roles.py`:
   - Add `overlay(plugin, role) -> {level: text}`. It reads `<plugin>/overlays/<role>.md` and returns `{}` when there is no file.
     - The file has no frontmatter.
     - Refused: non-blank text before the first `## ` heading, and any `## ` heading other than `## L<n>`.
     - A section's text is the lines between its heading and the next `## L<n>` heading, with leading and trailing blank lines stripped.
   - Refusals. Each one raises `TableError`, so the `generate`, `generate --check` and `selftest` paths exit 2:
     - an overlay file whose stem has no `levels.json` role;
     - a `## L<n>` with no `levels.json` row for that role;
     - any `## ` (H2) line inside a section;
     - any heading line (`#` to `######`) whose text is one of the role's `results.SCHEMA[role]['sections']`. Import `results` from the same scripts dir. A role with no SCHEMA entry skips this refusal;
     - a section over 20 lines after stripping;
     - a denylist word, matched as a whole word with word boundaries that treat `-` and `_` as word characters (so `PR` inside another word passes):
       - `push`, `publish`, `pkill`, `killall` and `run_in_background`, case-insensitive;
       - `PR`, case-sensitive;
       - `/tmp`.
   - Add `insert_overlay(body, level, text)`. It returns the body with this block inserted immediately before the body's `## Output` line:
     - `## At this level`;
     - the fixed line `You run at level L<n>. Where this section seems to differ from the sections above, those win.`;
     - a blank line, the section text, a blank line.
     
     It raises `TableError` when no line of the body is exactly `## Output`.
   - `definitions()` (claude_roles.py:92-106) calls `insert_overlay` for a row whose level has a section. A row with no section keeps today's body byte for byte.
   - `generated_stems` and `problems` stay as they are, so an overlay edited without `generate` fails `generate --check`.
   - Update the module docstring: the "role body verbatim" sentence and the edit-then-generate sentence both name `overlays/<role>.md`.
   - `selftest`:
     - Copy `<plugin>/overlays/` into the temp plugin when it exists.
     - Change the "keeps the role body verbatim" case (claude_roles.py:189): a row with an overlay section equals `insert_overlay(role body, level, section)`, and a row without one stays verbatim.
     - Add at least ten cases whose labels start with `overlay:`, each printed as `ok: overlay: ...` when it passes:
       - builder-L1 and builder-L5 carry the block before `## Output`;
       - builder-L3 is verbatim;
       - with no `overlays/` dir, every definition equals the role body;
       - an overlay edited without generate makes `generate --check` exit 1;
       - `overlays/ghost.md` exits 2;
       - an `## L9` section exits 2;
       - a `## Status` heading, and a `### Status` heading, inside a builder section exit 2;
       - a 21-line section exits 2;
       - the word `push` exits 2;
       - a role body with no `## Output` line exits 2.
     - Each refusal case restores the overlay before the next.
2. `plugins/sdlc-lite/scripts/codex_roles.py`:
   - `instructions(role)` (codex_roles.py:53-62) becomes `instructions(role, level)`. It passes the role body through `claude_roles.insert_overlay` when `claude_roles.overlay(ROOT, role)` has a section for `level`. Import `claude_roles` from the same scripts dir, the way codex_roles already imports `order`.
   - `raw_definitions()` (:134-145) passes the row's level. The alternate copies `data`, so it shares the level.
   - `main()` catches `claude_roles.TableError` and exits 2 with the message on stderr.
   - The prelude and `body()` stay unchanged.
   - Contract dependents of `instructions`: `git grep -n "instructions("` finds only codex_roles.py:142 as a caller. `codex-selftest.py` uses only `definitions()` and `raw_definitions()` (lines 185-190), so it needs no change. It is in this step's scope only in case a case has to be added.
3. `plugins/sdlc-lite/overlays/builder.md`:
   - Exactly two sections, `## L1` and `## L5`, each at most 20 lines, with H3 or lower inside.
   - No builder SCHEMA heading (Status, Changes, Checks, Notes) and no denylist word. Refer to body rules by number, for example "rule 4", and never quote them.
   - No model or effort name in either section, because a level can run on another model (dispatch.py:208-218).
   - `## L1` holds:
     - An ordered procedure that names the body rules in the order they fire: Read first and the handoff, rule 11 red checkpoint, rule 1 scope, rule 6 generators, rule 2 the named checks, rule 8 before calling a gate red, rule 10 stop.
     - These gap defaults:
       - a file the Do names that does not exist: create it;
       - the Do and a criterion disagree on a name: the criterion wins, and say so in Notes;
       - two readings both pass the criteria: take the smaller edit and say which;
       - no convention for a new test or file: copy the nearest existing one in the same folder;
       - read nothing past Read first and the files the Do names.
     - The closing line "Stop only for the gaps rules 3 and 8 route."
   - `## L5` holds:
     - the goal in one line (a closed step);
     - the KPI (the first verifier attempt passes);
     - the budget (the Stop rules ceiling restated, with no new number);
     - these judgment rules:
       - decide instead of enumerating: when two designs both meet the criteria, take the smaller diff and name the other in one line;
       - investigate only what a failing check points at;
       - trace contract dependents only for the contract the diff changes;
       - before the first edit, read every earlier `builder-*.md` and `verifier-*.md` in the step dir and write the root cause in one Notes line.
4. Regenerate with `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. Never hand-edit a generated file.
   - Only `agents/builder-L1.md`, `agents/builder-L5.md`, `adapters/codex/agents/sdlc-builder-l1.toml` and `sdlc-builder-l5.toml` may change.
   - The Codex fingerprints of the other agents do not move, because their instructions do not change and the plugin version is not bumped.
5. `plugins/sdlc-lite/scripts/check.py`:
   - Add one new numbered docstring item after the last one, plus its code. The last item is 51 at HEAD; take the next free number at build time, because other lanes add items.
   - The item checks two things: every `overlays/*.md` stem has `levels.json` rows, and no `.md` file sits in a subdirectory of `agents/` (an overlay placed in `agents/overlays/`).
   - Negative controls, in check.py's own style (a pure function, then `errors.append('check.py: ... negative control not flagged')` when a planted case is not flagged): a planted `overlays/ghost.md` stem and a planted `agents/overlays/x.md` path are each flagged.
   - The item's first docstring line (the `<n>. ` line) names `overlays/`. The literal `overlays/ghost.md` appears in the item text or the code.
   - Items 39 and 44 keep their text.
   - Contract dependent: the item 39 negative-control block (check.py:1145-1155) builds its temp plugin from `agents/` and `levels.json` only. Add `shutil.copytree(root/'overlays', _tp/'overlays')` when `root/'overlays'` exists. Without it, that block's baseline `generate --check` already differs on builder-L1, and the hand-edit control stops testing anything.
   - Left untouched on purpose:
     - The item 44 copy (check.py:1254) copies the whole plugin, so it needs no change.
     - dispatch.py uses only `claude_roles.source` (dispatch.py:662), so it needs no change.
     - Both were found by `git grep -n "copytree\|TemporaryDirectory\|claude_roles\." plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite/scripts/dispatch.py`.
6. Guidance, in the same change:
   - In `plugins/sdlc-lite/AGENTS.md`, the generated-agents bullet (line 18) becomes "After changing a role file, its skills list, `levels.json`, or `overlays/<role>.md`, run ... generate".
   - The `## scripts/claude_roles.py` entry of `docs/references/sdlc-internals.md` (line 21) gets one sentence on `overlays/<role>.md` and the `## At this level` block.
   - `skills/level-rubric/SKILL.md` is left untouched on purpose. The Codex planner and plan-reviewer agents preload it (the `skills:` lists in agents/planner.md and agents/plan-reviewer.md; sdlc-internals.md:21 says editing it regenerates Codex files). Editing it would therefore change TOMLs that the ticket's done-when keeps byte-identical. It is named for T-0443 in Risks.

Validation scope: `claude_roles.py selftest`, both `generate --check` commands, `python3 plugins/sdlc-lite/scripts/codex-selftest.py`, and `python3 plugins/sdlc-lite/scripts/check.py`. Run check.py once to see the new item green; the whole-suite gate belongs to step 2.
### Acceptance criteria
- (red) `python3 -c "import re, sys; t = open('plugins/sdlc-lite/overlays/builder.md').read(); sys.exit(0 if re.findall(r'^## .*$', t, re.M) == ['## L1', '## L5'] else 1)"`
- (red) `python3 -c "import sys; from pathlib import Path; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import codex_roles; P = Path('plugins/sdlc-lite'); H = '## At this level\nYou run at level %s. Where this section seems to differ from the sections above, those win.\n'; ts = [(lv, (P/'agents'/('builder-'+lv+'.md')).read_text()) for lv in ('L1', 'L5')] + [(lv, codex_roles.loads(P/'adapters/codex/agents'/('sdlc-builder-'+lv.lower()+'.toml'))['developer_instructions']) for lv in ('L1', 'L5')]; bad = [lv for lv, t in ts if not (t.find(H % lv) >= 0 and t.find('\n## Output\n', t.find(H % lv)) > 0 and '\n## ' not in t[t.find(H % lv):t.find('\n## Output\n', t.find(H % lv))])]; print(bad); sys.exit(1 if bad else 0)"`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/agents/builder-L3.md`
- (red) `ch=$( { git diff --name-only "$SDLC_BASE_SHA" -- plugins/sdlc-lite/agents plugins/sdlc-lite/adapters/codex/agents; git ls-files --others --exclude-standard -- plugins/sdlc-lite/agents plugins/sdlc-lite/adapters/codex/agents; } | sort -u | tr '\n' ' ' ); test "$ch" = "plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l5.toml plugins/sdlc-lite/agents/builder-L1.md plugins/sdlc-lite/agents/builder-L5.md "`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/claude_roles.py selftest) && test "$(printf '%s\n' "$out" | grep -c '^ok: overlay:')" -ge 10`
- (red) `python3 -c "import inspect, sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import codex_roles; sys.exit(0 if list(inspect.signature(codex_roles.instructions).parameters) == ['role', 'level'] else 1)"`
- (guard) `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (red) `grep -qE '^[0-9]+\. .*overlays/' plugins/sdlc-lite/scripts/check.py && grep -qF 'overlays/ghost.md' plugins/sdlc-lite/scripts/check.py`
- (red) `grep -qF 'overlays/<role>.md' plugins/sdlc-lite/AGENTS.md && grep -qF 'overlays/' docs/references/sdlc-internals.md`
- (red) `test -f plugins/sdlc-lite/overlays/builder.md && ! grep -qE '[[:space:]]$' plugins/sdlc-lite/overlays/builder.md`
- (guard) `for f in $( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | sort -u ); do case "$f" in plugins/sdlc-lite/overlays/builder.md|plugins/sdlc-lite/scripts/claude_roles.py|plugins/sdlc-lite/scripts/codex_roles.py|plugins/sdlc-lite/scripts/codex-selftest.py|plugins/sdlc-lite/scripts/check.py|plugins/sdlc-lite/agents/builder-L1.md|plugins/sdlc-lite/agents/builder-L5.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml|plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l5.toml|plugins/sdlc-lite/AGENTS.md|docs/references/sdlc-internals.md) ;; *) echo "out of scope: $f"; exit 1 ;; esac; done`

## Step 2: Gates green, the Codex regenerate line, and one live builder L1 run with the overlay
level: L2
guard timeout: 2700
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Depends on: step 1, which passed verification. This step replaces the earlier step 2, which `dispatch.py prepare` refused: `steps.py lint` reads every `.sdlc/` path in a step handoff as a cited input that must already exist, and that step named its output files that way. Its outputs now go into this step's own Artifacts dir under plain file names, and no text of this step names a dot-sdlc file the step creates. Keep it that way in anything you add.

1. Guidance line. In `plugins/sdlc-lite/AGENTS.md`, the Codex regenerate bullet (line 17, the one that starts "After changing shared role bodies") becomes "After changing shared role bodies, preloaded skill bodies, Codex mappings, `overlays/<role>.md`, or the Codex prelude, run ...", with the rest of the line unchanged. Why it belongs here: step 1 made `codex_roles.py instructions(role, level)` read the overlay, so an overlay edit regenerates Codex TOMLs too, and step 1's builder flagged this line as stale in its Notes because step 1's Do limited the edit to line 18.
2. Gates. Run every gate criterion below once and fix any red that step 1 introduced, staying inside the scope criterion's file list. A gate already red at the build-start HEAD is `inherited red`. `check.sh` took 897 s under fanout load at base, so give its Bash call a timeout of at least 2700000 ms.
3. Live run, the plugin's rule that a role behavior change gets a focused live run in a throwaway project. Below, `<art>` is the absolute path on the `Artifacts dir:` line of your dispatch prompt (this step's folder), `<lane>` the absolute path on its `Tree:` line with no trailing slash, and `<tmp>` the throwaway folder it names.
   1. Make the throwaway project with `mkdir -p "<tmp>/live"` and `git -C "<tmp>/live" init -q`. Do not use `git worktree add`: under this headless conductor `SDLC_ROLE` is set and `SDLC_TMP_WORKTREES` is not, so `hooks/block-stray-worktree.sh` refuses it (seen at plan time). In `<tmp>/live` write `live-step/handoff.md` in the step handoff layout this step's own handoff uses, one line each, in this order:
      - `## Task goal`, then the line `Add a probe file to the throwaway project.`;
      - `## Step 1: Add a probe file`, then `level: L1`;
      - `### Do`, then `Create live-probe.txt holding the line overlay probe.`;
      - `### Acceptance criteria`, then the one criterion `` - `grep -qx 'overlay probe' live-probe.txt` ``.
   2. In one foreground Bash call with the timeout at 1200000, from `<tmp>/live`, run:
      `claude -p --plugin-dir "<lane>/plugins/sdlc-lite" --agent sdlc-lite:builder-L1 --dangerously-skip-permissions --output-format stream-json --verbose "Handoff: live-step/handoff.md. Artifacts dir: live-step. Build the step and return your report." > "<art>/live-run.jsonl"`
   3. Write that exact command line, with `<lane>` and `<art>` expanded, as one line to `<art>/live-run.cmd`.
   4. Extract the session's final report with `python3 -c "import json, sys; ev = [json.loads(l) for l in open(sys.argv[1]) if l.startswith('{')]; print([e for e in ev if e.get('type') == 'result'][-1]['result'])" "<art>/live-run.jsonl" > "<art>/live-run.md"`.
   5. Leave `<tmp>/live` where it is. It sits under the git-ignored `.worktrees/`, and a headless run cannot answer a delete prompt.

The file names are deliberate: a name such as `live-builder-L1.md` matches the role-report pattern (`REPORT_FILE_RE` in `steps.py`, `<role>-L*.md` in `order.py`) and could be read as a role result in the step folder.

What the live run proves: the stream-json `init` event lists one `sdlc-lite` plugin, at `<lane>/plugins/sdlc-lite` (a plan-time probe showed an inline `--plugin-dir` plugin replaces the installed `sdlc-lite@sdlc-lite`), so the session ran the regenerated `agents/builder-L1.md` that carries the overlay; and its report keeps the builder schema without repeating `## At this level` (the design's literal-L1 risk). It does not prove that the overlay changes builder behavior; that is T-0442's A/B. If the report does repeat `## At this level`, do not change the insertion yourself: set Status to blocked with a `plan defect:` line naming the design's fallback (insert the block as an H3 under the last section before Output).

Validation scope: the gates below (`check.sh` runs check.py, both `generate --check` commands, `claude_roles.py selftest` and codex-selftest.py), packaging, `git diff --check`, and the live-run files.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
- (red) `grep -qE '^- After changing shared role bodies.*overlays/<role>\.md' plugins/sdlc-lite/AGENTS.md`
- (red) `cd .sdlc/0441-overlay-mechanism-builder-ends/step-2 && test -s live-run.md && grep -q '^## Status' live-run.md`
- (red) `cd .sdlc/0441-overlay-mechanism-builder-ends/step-2 && test -s live-run.md && ! grep -q '^## At this level' live-run.md`
- (red) `cd .sdlc/0441-overlay-mechanism-builder-ends/step-2 && test -f live-run.cmd && grep -qF -- '--agent sdlc-lite:builder-L1' live-run.cmd && grep -qF -- '--plugin-dir' live-run.cmd`
- (red) `cd .sdlc/0441-overlay-mechanism-builder-ends/step-2 && test -s live-run.jsonl && python3 -c "import json, os, subprocess, sys; top = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip(); ev = [json.loads(l) for l in open('live-run.jsonl') if l.startswith('{')]; init = [e for e in ev if e.get('type') == 'system' and e.get('subtype') == 'init']; ps = [os.path.realpath(p.get('path', '')) for p in (init[0].get('plugins', []) if init else []) if p.get('name') == 'sdlc-lite']; print(ps); sys.exit(0 if ps == [os.path.realpath(top + '/plugins/sdlc-lite')] else 1)"`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/agents/builder-L3.md`
- (guard) `for f in $( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | sort -u ); do case "$f" in plugins/sdlc-lite/overlays/builder.md|plugins/sdlc-lite/scripts/claude_roles.py|plugins/sdlc-lite/scripts/codex_roles.py|plugins/sdlc-lite/scripts/codex-selftest.py|plugins/sdlc-lite/scripts/check.py|plugins/sdlc-lite/agents/builder-L1.md|plugins/sdlc-lite/agents/builder-L5.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml|plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l5.toml|plugins/sdlc-lite/AGENTS.md|docs/references/sdlc-internals.md) ;; *) echo "out of scope: $f"; exit 1 ;; esac; done`

## Assumptions
- Step 1 passed and keeps its number and text from `.sdlc/0441-overlay-mechanism-builder-ends/planner-L2.md`: verified by `.sdlc/0441-overlay-mechanism-builder-ends/step-1/verifier-L2.md` (Verdict pass, 12 of 12 criteria) and a byte comparison of the Step 1 block.
- `steps.py lint` on a step handoff (`link_findings`, plugins/sdlc-lite/scripts/steps.py:1491-1516) treats every `.sdlc/` path in the text as a cited input that must exist, skipping only a path that runs into a placeholder or glob (`cited_sdlc_paths`, :1422-1437): verified by reading the code and the two lines in `.sdlc/0441-overlay-mechanism-builder-ends/refusals.jsonl`. The new step 2 names only the existing step-2 folder: verified by `steps.py lint` on a draft step-2 handoff in a scratch copy (`steps lint: ok`).
- `steps.py split --only 2` reuses `step-2/`, because it holds no role output (steps.py:1721 refuses only a folder with role output): verified by `ls` (handoff.md only).
- A nested `claude -p` runs from a sub-agent of this headless conductor, and an inline `--plugin-dir` sdlc-lite replaces the installed `sdlc-lite@sdlc-lite` (enabled in ~/.claude/settings.json): verified by a plan-time haiku probe whose stream-json `init` event listed one `sdlc-lite` plugin, path the lane's `plugins/sdlc-lite`, source `sdlc-lite@inline`, with `sdlc-lite:builder-L1` among the agents (cost $0.12).
- `git worktree add` is refused here: `SDLC_ROLE=conductor` is set and `SDLC_TMP_WORKTREES` is unset in this session, and block-stray-worktree.sh (lines 42-46) uses the `.worktrees/tmp` fallback only when `SDLC_ROLE` is unset: verified by two refused attempts at plan time and `echo $SDLC_ROLE`.
- `.worktrees/` is git-ignored, so the throwaway project never reaches the scope guard: verified by `git check-ignore -v` (.gitignore:10).
- `plugins/sdlc-lite/AGENTS.md` line 17 does not name overlays: verified by `sed -n 17p` and step 1's builder Notes.
- Plan-time probes on the current tree with `SDLC_BASE_SHA=222f817e` (step 1's recorded base, still HEAD):
  - every `(red)` criterion exited 1;
  - check-packaging, `git diff --check`, the builder-L3 diff, the scope loop and both `generate --check` commands exited 0;
  - each guard shape was seen red: `git diff --check` on a trailing-whitespace fixture, the builder-L3 diff form on builder-L1.md, the scope loop with a one-path list, the heading negation on builder-L1.md, and the plugin-path check on a fixture holding the installed plugin's path (green on a fixture holding the lane path);
  - check.sh exited 0 at base in 897 s (planner-L2 record; earlier records 342 to 382 s), so the guard timeout stays 2700. It was not re-run on step 1's tree.

## Risks
- check.sh on step 1's tree is unverified at plan time. Step 2's Do fixes any red it introduced inside the scope list.
- The live run costs one builder L1 session. It proves that the overlaid definition loads and keeps the report shape, not that the overlay changes behavior.
- The nested session inherits `SDLC_ROLE=conductor` and `SDLC_HEADLESS=1`, so its hooks treat it as the conductor rather than a builder. This does not touch what the criteria check.
- The hook gap itself (a sub-agent of a headless conductor cannot create any throwaway worktree) is a plugin defect outside this ticket and a candidate follow-up.
- The scope guard assumes no main sync regenerates other agents during the lane. A resync moves `SDLC_BASE_SHA` past the merge, so it holds unless the merge lands in the middle of the step.
- The design's level-rubric one-liner is not written here; T-0443 regenerates more agents anyway.
- Plan-time scratch files (fixtures and a scratch git repo, no registered worktree) stay under `.worktrees/tmp/0441-planner-L3/`, because rule 15 forbids the delete the brief asks for. The folder is git-ignored.
- If step 2 fails and its folder is superseded, the live-run files move with the old attempt and the rebuild writes fresh ones.
