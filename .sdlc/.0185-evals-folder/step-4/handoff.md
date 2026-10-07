## Task goal
Model and effort choices are backed by recorded experiments, and a change to the model table cannot land without citing one.

## Step 4: Document evals.py and the table lock where the model table is described
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 to 3. Use no em dashes. Each fact has one authoritative place: the format, the canonical text, and the lock rules live in `.sdlc/evals/AGENTS.md` (step 2) and in evals.py. These edits link there instead of copying them.

`docs/references/sdlc-internals.md`: add an entry headed exactly ``## `scripts/evals.py` ``, after the `scripts/results.py` entry. It covers:
- the purpose: dated eval records, and the lock that ties the model table to one of them
- the CLI: `add`, `list`, `check`, `lock`, `hash`, `selftest`, the global `--root` and `--plugin`, and the exit codes
- the Python API, including `validate_eval` for later callers
- `table-lock.json` and its three keys
- the check.py guard: docstring item 14, skipped when no `.sdlc` sits beside the plugin's repository
- the selftest and its three negative controls
- a link `../../.sdlc/evals/AGENTS.md` for the format and the canonical text

`plugins/sdlc-lite/skills/handoff-format/SKILL.md`: in the layout block, add this line after the `.sdlc/messages/` line, aligned like its neighbours:

```
.sdlc/evals/            the plugin repository's dated model and effort evals (NNNN-<slug>.md) and table-lock.json, written by scripts/evals.py add and lock; check.py fails a model-table change that cites no newer eval; its AGENTS.md documents the format
```

handoff-format is not a preloaded skill (the agents preload only level-rubric), so the Codex TOML does not change.

`plugins/sdlc-lite/AGENTS.md`:
- Extend the Contracts bullet that starts "Claude models and efforts live in `scripts/run.sh`". A change to either table needs a new eval in `.sdlc/evals/` and `scripts/evals.py lock`, else `scripts/check.py` fails; read [the evals entry file](../../.sdlc/evals/AGENTS.md) first.
- Add to the Verification list: `- Evals and the model-table lock: python3 plugins/sdlc-lite/scripts/evals.py check (and selftest).`

`docs/references/codex-role-execution.md`: after "Regenerate the agent files after changes." (line 46), add "A change also needs a new eval in `.sdlc/evals/` and `evals.py lock`, or `check.py` fails; see [the evals entry file](../.sdlc/evals/AGENTS.md)."

Left untouched on purpose:
- `skills/level-rubric/SKILL.md`: the planner and plan-reviewer preload it, so an edit would regenerate the Codex TOML. It is consumer guidance, and the lock is a maintainer gate.
- Root `AGENTS.md`: it routes SDLC changes to `plugins/sdlc-lite/AGENTS.md`, which now carries the rule.
- `docs/lean-sdlc/design.md`: a design record whose line 152 already says each planned folder gets its own entry file when built.

Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`. It must stay green.
### Acceptance criteria
- ``grep -qxF '## `scripts/evals.py`' docs/references/sdlc-internals.md``
- `grep -qF 'table-lock.json' docs/references/sdlc-internals.md`
- `grep -qF '.sdlc/evals/' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'scripts/evals.py' plugins/sdlc-lite/AGENTS.md`
- `grep -qF 'evals.py lock' docs/references/codex-role-execution.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/evals.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/check.py -e docs/references/sdlc-internals.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/AGENTS.md -e docs/references/codex-role-execution.md | { ! grep -q .; }`
