## Task goal
A dated report with a keep, extend or drop verdict backed by priced runs.

## Step 1: Point the runnable bench tasks at this machine's repos
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
In `plugins/sdlc-lite/bench/tasks/subagent-tool-names.md`, `figma-stale-skip-report.md` and `command-modal-footer.md`, change only the `repo:` line from `/Users/kimba/Projects/nonoun/<name>` to `/Users/kimgranlund/Projects/nonoun/<name>`. The directory name stays the same (`agent-ui`, `ultimate-tokens`). Both repos exist locally and already hold every `base`, `solution` and `tests_from` sha (planner probe: `git -C <repo> cat-file -t <sha>` printed `commit`).

Leave `button-geometry-model.md` and `svelte-icon-component.md` unchanged. Their repos (`gen-ui-system`, `gen-ui-system-svelte`) are not under `/Users/kimgranlund/Projects/nonoun/`, and their base shas are not in `kimgranlund/gen-ui-kit`, `ui-kit` or `ui-kit-svelte` on GitHub (`gh api` returned 422). There is no path to fix them to, so step 2 records them as not run.

Contract dependents: `git grep -n kimba -- . ':(exclude).sdlc' ':(exclude)docs/reports'` finds only these five task files outside the archived `bench/results/`. The archived results are dated evidence and stay as they are. Depends on: none.
### Acceptance criteria
- (red) `for t in subagent-tool-names figma-stale-skip-report command-modal-footer; do f=plugins/sdlc-lite/bench/tasks/$t.md; r=$(sed -n "s/^repo: //p" $f); for k in base solution tests_from; do git -C "$r" cat-file -e "$(sed -n "s/^$k: //p" $f)^{commit}" || exit 1; done; done`
- (red) `for t in subagent-tool-names figma-stale-skip-report command-modal-footer; do grep -qx "repo: /Users/kimgranlund/Projects/nonoun/$(sed -n "s|^repo: .*/||p" plugins/sdlc-lite/bench/tasks/$t.md)" plugins/sdlc-lite/bench/tasks/$t.md || exit 1; done`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/bench/tasks/button-geometry-model.md plugins/sdlc-lite/bench/tasks/svelte-icon-component.md plugins/sdlc-lite/bench/tasks/README.md`
- (guard) `! git diff "$SDLC_BASE_SHA" -- plugins/sdlc-lite/bench/tasks | grep -E "^[-+][^-+]" | grep -qvE "^[-+]repo: "`
- (guard) `python3 -c 'import subprocess,sys,re; a=subprocess.run(["git","diff","--name-only",sys.argv[1],"--",".",":(exclude).sdlc"],capture_output=True,text=True).stdout.split(); b=subprocess.run(["git","ls-files","--others","--exclude-standard","--",".",":(exclude).sdlc"],capture_output=True,text=True).stdout.split(); ok=re.compile(r"plugins/sdlc-lite/bench/tasks/(subagent-tool-names|figma-stale-skip-report|command-modal-footer)\.md"); bad=[p for p in a+b if not ok.fullmatch(p)]; print(bad); sys.exit(1 if bad else 0)' "$SDLC_BASE_SHA"`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/bench/tasks`
