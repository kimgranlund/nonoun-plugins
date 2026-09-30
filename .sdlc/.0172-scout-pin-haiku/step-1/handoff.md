## Task goal
The Claude scout runs on a real Haiku, and the model table, rubric and checks say so.

## Step 1: Pin the scout to claude-haiku-4-5
level: L2

### Do
Observed 2026-09-30 on Claude Code 2.1.285, Max login: `claude -p --model haiku` reported modelUsage `claude-sonnet-5-5`; `--model claude-haiku-4-5` reported `claude-haiku-4-5`; `--model claude-haiku-5-5` failed with `unrecognized_model`. So the alias `haiku` runs Sonnet 5.5 and the scout has not been on a Haiku.

1. In `plugins/sdlc-lite/scripts/run.sh`, change the `scout:L1)` row to `model=claude-haiku-4-5;  effort=low ;;`, keeping the row's layout.
2. In `plugins/sdlc-lite/scripts/check.py`, make the run.sh and rubric comparison accept a pinned id. The run.sh pattern `model=(\w+)` must accept hyphens and digits. Replace `cap(model)` with a function that keeps aliases as now (`sonnet` becomes `Sonnet`) and turns an id of the form `claude-<family>-<major>-<minor>` into `<Family> <major>.<minor>` (so `claude-haiku-4-5` becomes `Haiku 4.5`). Widen the two rubric cell patterns so a cell like `Haiku 4.5 low` parses as model `Haiku 4.5` and effort `low`, without changing how the existing cells parse. Add a guard with a built-in negative control, in the style of the nearby checks, that fails when the scout row in run.sh and the rubric disagree.
3. In `plugins/sdlc-lite/skills/level-rubric/SKILL.md`, change the scout row of the single-level table to `| scout | L1 | Haiku 4.5 low |`. In the Agent-tool seat list, after the line "Mechanical or gather-only work: `haiku`.", add a sentence: "On the maintainer's login (Claude Code 2.1.285) the alias `haiku` resolves to Sonnet 5.5, and the Agent tool takes an alias, so this seat runs Sonnet there; the run.sh scout pins `claude-haiku-4-5`."
4. Check every other place that parses a model name from a result header or table, and widen any pattern that would drop or truncate a hyphenated id: `scripts/traces/sources/results.py`, the detectors under `scripts/traces/`, `scripts/order.py`, and `scripts/steps.py`. Add or extend a selftest case for each pattern you change. Do not change patterns that already accept the id.
5. Add `docs/validation/haiku-alias-2026-09-30.md`, a dated note with: the three probe commands above and their outputs as listed in this step, the CLI version and login type (Max), and a one-line limit: "one machine, one login; other plans may resolve the alias differently". Link it from `docs/README.md` in the style of the neighbouring entries.

### Acceptance criteria
- `grep -qE '^\s+scout:L1\)\s+model=claude-haiku-4-5; +effort=low' plugins/sdlc-lite/scripts/run.sh`
- `grep -qE '^\| scout \| L1 \| Haiku 4.5 low \|' plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `r="$PWD"; d=$(mktemp -d) && mkdir "$d/t" && printf '## Goal\nx\n\n## Question\nx\n' > "$d/t/handoff.md" && cd "$d" && git init -q && git -c user.email=a@b.c -c user.name=a commit -q --allow-empty -m i && SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" scout L1 t/handoff.md | grep -qF -- "--model claude-haiku-4-5"`
- `grep -qF "claude-haiku-4-5" docs/validation/haiku-alias-2026-09-30.md`
- `grep -qF "haiku-alias-2026-09-30.md" docs/README.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
