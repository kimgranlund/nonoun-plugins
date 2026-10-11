## Task goal
Role prompts can differ by level at generation time, with `overlays/builder.md` carrying `## L1` and `## L5` only; every other generated agent stays byte-identical.

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
