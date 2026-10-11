<!-- role=planner level=L2 model=opus effort=medium -->
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

## Step 2: Gates green and one live builder L1 dispatch with the overlay
level: L2
guard timeout: 2700
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1. Run every gate below once and fix any red that step 1 introduced, staying inside step 1's file scope. A gate already red at the build-start HEAD is `inherited red`.

Then do the live run, which is the plugin's role-behavior rule (a focused live run in a throwaway project):
1. Run `git worktree add --detach "$SDLC_TMP_WORKTREES/live" HEAD`. Inside that worktree, write a one-step handoff `live-step/handoff.md` with:
   - step title "Add a probe file";
   - Do: create `live-probe.txt` holding the line `overlay probe`;
   - one criterion: `grep -qx 'overlay probe' live-probe.txt`.
2. From that worktree, run this in the foreground with the Bash timeout at 1200000:
   `claude -p --plugin-dir "<lane tree>/plugins/sdlc-lite" --agent sdlc-lite:builder-L1 --dangerously-skip-permissions "Handoff: live-step/handoff.md. Artifacts dir: live-step. Build the step and return your report."`
   - `<lane tree>` is the absolute path of this lane's tree (`git rev-parse --show-toplevel` in the lane), so the session loads the regenerated `agents/builder-L1.md` that carries the overlay.
   - Redirect stdout to `.sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.md` in the lane tree.
   - Write the exact command line you ran to `.sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.cmd`.
3. Leave the throwaway worktree under `$SDLC_TMP_WORKTREES`; the run removes it.

The live run proves that the overlaid definition loads and produces a schema-shaped builder report that does not repeat the `## At this level` heading (the design's literal-L1 risk). It does not prove that the overlay changes builder behavior; that is T-0442's A/B. If the report does repeat `## At this level`, do not change the insertion yourself. Set Status to blocked with a `plan defect:` line naming the design's fallback (insert the block as an H3 under the last section before Output).
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (red) `test -s .sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.md && grep -q '^## Status' .sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.md`
- (red) `test -f .sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.md && ! grep -q '^## At this level' .sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.md`
- (red) `grep -qF -- '--agent sdlc-lite:builder-L1' .sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.cmd && grep -qF -- '--plugin-dir' .sdlc/0441-overlay-mechanism-builder-ends/live-builder-L1.cmd`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/agents/builder-L3.md`
- (guard) `for f in $( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | sort -u ); do case "$f" in plugins/sdlc-lite/overlays/builder.md|plugins/sdlc-lite/scripts/claude_roles.py|plugins/sdlc-lite/scripts/codex_roles.py|plugins/sdlc-lite/scripts/codex-selftest.py|plugins/sdlc-lite/scripts/check.py|plugins/sdlc-lite/agents/builder-L1.md|plugins/sdlc-lite/agents/builder-L5.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml|plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l5.toml|plugins/sdlc-lite/AGENTS.md|docs/references/sdlc-internals.md) ;; *) echo "out of scope: $f"; exit 1 ;; esac; done`

## Assumptions
- Generated Claude definitions are the role body verbatim under a generated frontmatter: verified by reading plugins/sdlc-lite/scripts/claude_roles.py:92-106 and the selftest case at :189.
- Codex instructions are built per role, and codex_roles.py:142 is the only caller of `instructions()`: verified by `git grep -n "instructions("` over plugins and scripts.
- The builder role body has exactly one `## Output` heading, and the Codex prelude has none: verified by `grep -n '^## ' plugins/sdlc-lite/agents/builder.md` (line 33) and `grep -c '## Output' plugins/sdlc-lite/adapters/codex/instructions.md` (0).
- The builder SCHEMA sections are Status, Changes, Checks and Notes: verified at plugins/sdlc-lite/scripts/results.py:32-37.
- check.py's last item is 51, and no file this ticket touches names `overlays` yet: verified by reading the check.py docstring, and `grep -c overlays` returned 0 in check.py, claude_roles.py, codex_roles.py, AGENTS.md and sdlc-internals.md.
- check.sh runs check.py, both `generate --check` commands, `claude_roles.py selftest` and codex-selftest.py: verified at plugins/sdlc-lite/scripts/check.sh:12-18.
- The item 39 negative-control block in check.py copies only `agents/` and `levels.json` into its temp plugin, and the item 44 block copies the whole plugin: verified at check.py:1145-1155 and :1254.
- The design's level-rubric guidance line is dropped for this ticket. The handoff's done-when ("only builder-L1, builder-L5 and their two Codex TOMLs change") outranks the design's guidance list, and agents/planner.md and agents/plan-reviewer.md preload level-rubric into their Codex TOMLs: verified by `grep -ln level-rubric plugins/sdlc-lite/agents/*.md` and the `skills:` list in agents/planner.md:4-5.
- Headless `claude -p --plugin-dir <dir> --agent sdlc-lite:<role>` is the established live-run shape: verified at plugins/sdlc-lite/scripts/run.sh:415-417 and bench.sh:29.
- Every guard is green at base, checked on HEAD 222f817e:
  - check.sh exited 0 in 897 s under fanout load (earlier records: 342 to 382 s), so the guard timeout is 2700.
  - check-packaging, both `generate --check` commands, the builder-L3 diff and the scope loop exited 0.
  - Every `(red)` criterion exited 1 (2 for a missing file), because the overlay work does not exist yet.
  - `steps.py lint` on this plan prints `steps lint: ok`.

## Risks
- The scope guard and the four-file generated-set criterion assume no main sync regenerates other agents during the lane. A resync moves `SDLC_BASE_SHA` past the merge, so they hold unless the merge lands in the middle of a step.
- Another lane may also add check.py item 52. The criterion matches any numbered item that names `overlays/`, so only the docstring text would conflict at merge.
- The live run costs money (one builder L1 session, a few dollars). It also depends on `--plugin-dir` taking precedence over an installed sdlc-lite plugin of the same name; if the installed one wins, the run proves nothing about the overlay. The `.cmd` file shows the verifier which plugin dir was used, but not which definition the host resolved.
- The design's level-rubric one-liner is not written here. T-0443 regenerates more agents anyway, so it is the natural place for it.
- Rule 11: the builder-L3 diff guard was not observed red on a fixture; it relies on `git diff --quiet` exiting 1 on a change. The scope guard was observed red on a fixture path (`plugins/sdlc-lite/agents/builder.md`).
