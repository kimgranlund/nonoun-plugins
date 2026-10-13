## Task goal
A new pipeline role, `ui-designer`, that plans, reviews and generates correct, semantic DOM structure and excellent CSS, aware of the design system and sibling styling around the code it touches.

## Step 2: Live run of the three modes, release note, gates green
level: L2
guard timeout: 3960
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
Depends on: step 1, which is built and verified (pass) and sits uncommitted in this tree. `$SDLC_BASE_SHA` is the commit before step 1, so the scope list below holds step 1's paths too.

Names used below: `<tree>` is this repository's work tree, `<project>` is the throwaway project's root, `<mode>` is one of `plan`, `review`, `generate`, and `<level>` is the level that mode runs at.

Path rule, the defect that refused try 1 of this step: `steps.py lint` reads every literal path under a `.sdlc` folder in a step handoff as a path of this repository that must exist (`cited_sdlc_paths` and `link_findings` in `plugins/sdlc-lite/scripts/steps.py`). The throwaway project's handoffs and results are files of another git repository, so this step names them only with the `<mode>` placeholder, which lint does not read as a path. Use the same form in your result file.

1. Throwaway project. Under the tmp prefix your brief names, `git init` a folder named `ui-designer-live`. Its one commit holds a `.gitignore`, three project files, and three handoffs.
   - `.gitignore`: one line, `.worktrees/`. `run.sh` gives each role a scratch folder under the project's `.worktrees/tmp` (`plugins/sdlc-lite/scripts/run.sh:510`), and that folder must not show in the status files.
   - `index.html`: a product list built from generic `div` elements with no landmarks and one clickable `div`.
   - `tokens.css`: custom properties for color, space, and radius.
   - `styles.css`: a layer order, one card component that uses the tokens, and one rule with a hardcoded color.
   - One handoff per mode at `.sdlc/<mode>/handoff.md` under `<project>`. Each holds a `## Goal` and exactly one mode line (`mode: plan`, `mode: review`, `mode: generate`), and names project files only. Plan: an order summary section for the page. Review: `index.html` and `styles.css`. Generate: add the order summary to `index.html` and `styles.css`.
   - Never delete the project; the run cleans the prefix.
2. Runs. From `<project>`, run `SDLC_CLAUDE_EXEC=1 bash <tree>/plugins/sdlc-lite/scripts/run.sh ui-designer <level> .sdlc/<mode>/handoff.md` three times, in this order: plan at `L2`, review at `L1`, generate at `L1`.
   - Run each in the foreground with the Bash timeout at 600000 or more; `plugins/sdlc-lite/hooks/block-background.sh` refuses a background run in this session.
   - This is the legacy Claude branch of `run.sh` (`plugins/sdlc-lite/AGENTS.md`, Contracts and routing): a running session cannot load the lane's new `ui-designer-L<n>` definitions, so `dispatch.py prepare` is not usable here.
   - Each run starts from a clean project. When `git status --porcelain -- . ":(exclude).sdlc"` prints anything before a run, run that mode in a fresh `git clone` of `<project>` instead (a sibling folder under the same prefix). Nothing is deleted or reset.
   - After each run, save the output of that same status command as `<mode>.status.txt`.
3. Evidence. Copy each run's result unchanged to `docs/reports/2026-10-13-ui-designer-live-run/<mode>.txt`, and the three status files beside them. `run.sh` writes the result beside the handoff as `ui-designer-<level>.md`; a second run in the same folder gets a `-2` suffix, so copy the newest.
4. Rerun rule. If a result fails `results.py validate`, or the plan or review run changed a project file, fix `plugins/sdlc-lite/agents/ui-designer.md`, regenerate both hosts (`claude_roles.py generate`, `codex_roles.py generate`), and rerun that mode. At most two reruns per mode, then Status blocked. If the host refuses to start `claude -p`, Status is blocked with the exact refusal; never substitute a fixture for a run.
5. `docs/reports/2026-10-13-ui-designer-live-run.md` (create), linked from `docs/README.md` if `docs_check.py` asks.
   - Header facts: `Recorded:` date, `claude --version`, and the base commit with a note that step 1's changes are uncommitted on top of it.
   - Per run: the command, exit code, model and effort and cost from the `runs.jsonl` beside that handoff, the `results.py validate` outcome, and a link to its `.txt` and status file.
   - `## Not proven`: the Codex host, and the sub-agent dispatch path with the generated definitions.
   - `## Release note`: one line for the next patch (no release-notes file exists before a release is cut, so the filer copies this line into its Changelog entry).
6. Gates. Run every gate below and fix any red step 1 or this step introduced. A gate already red at the build-start HEAD is Status `inherited red`. When `SDLC_BASE_SHA` is empty in your shell, export it from the first line of the `base-sha` file beside this handoff.
### Acceptance criteria
- (red) The three retained results are valid: `for m in plan review generate; do python3 plugins/sdlc-lite/scripts/results.py validate docs/reports/2026-10-13-ui-designer-live-run/$m.txt --role ui-designer || exit 1; done`
- (red) Each result states the mode it ran: `python3 -c "import sys;sys.path.insert(0,'plugins/sdlc-lite/scripts');import results;sys.exit(any(results.key_value('docs/reports/2026-10-13-ui-designer-live-run/%s.txt'%m,'ui-designer')!=m for m in ('plan','review','generate')))"`
- (red) Plan and review left the project unchanged and generate changed it: `d=docs/reports/2026-10-13-ui-designer-live-run; test -f $d/plan.status.txt && test ! -s $d/plan.status.txt && test -f $d/review.status.txt && test ! -s $d/review.status.txt && test -s $d/generate.status.txt`
- (red) The report links the three results: `for m in plan review generate; do grep -qF "2026-10-13-ui-designer-live-run/$m.txt" docs/reports/2026-10-13-ui-designer-live-run.md || exit 1; done`
- (red) The report carries the release-note line: `grep -qx '## Release note' docs/reports/2026-10-13-ui-designer-live-run.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) Scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE '^(plugins/sdlc-lite/(agents|adapters|hooks|scripts|skills/level-rubric|skills/agent)/|docs/references/|docs/README\.md$|docs/reports/2026-10-13-ui-designer-(role|live-run)(\.md$|/))')"`
