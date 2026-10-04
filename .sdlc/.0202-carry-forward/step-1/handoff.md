## Task goal
Add a `## Carry forward` section to the scout, researcher, architect, and archaeologist results and the reader rule to planner and builder.

## Step 1: Carry forward contracts, result schema, check.py guard, Codex agents
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets:
- `plugins/sdlc-lite/agents/scout.md`, `researcher.md`, `architect.md`, `archaeologist.md`: one new output template section.
- `plugins/sdlc-lite/agents/planner.md`: a reader paragraph.
- `plugins/sdlc-lite/agents/builder.md`: a reader sentence.
- `plugins/sdlc-lite/scripts/results.py`: `SCHEMA` and `selftest()`.
- `plugins/sdlc-lite/scripts/check.py`: a new guard and docstring item 15.
- The regenerated `plugins/sdlc-lite/adapters/codex/agents/*.toml`.

Settled decisions:
- **Producer template.** Use the same text in all four files. Append it after the current last section, with one blank line before it: the heading line `## Carry forward`, then this body line: `The facts and paths later roles must not re-derive: at most 15 lines, one fact per line, each with its path:line or source. For a complete list, such as every caller of a symbol, also name the search that produced it and its scope. "None" if nothing.`
  - Evidence: the handoff Intent ("at most 15 lines: facts and paths later roles must not re-derive") and design.md:119.
  - The "Final message, exactly these sections:" lead-in stays, so the prompt asks for the section, while the schema keeps it optional (see results.py below).
- **Planner paragraph.** Insert this exact paragraph as a new paragraph right after the line `Read the code you plan against. Do not edit anything.` (planner.md:9): `Before searching the code, read the `## Carry forward` section of each scout, researcher, architect, and archaeologist result you read, and search only what it does not answer. A carried-forward list that names a search covering the same scope answers that search, the Contract dependents search included. When a step relies on a carried-forward fact, cite the result path (for example `.sdlc/<task>/scout-L1.md`) in that step's Do instead of copying the section into the plan; the builder reads it there.`
  - Evidence: the handoff Intent ("The planner cites the result path and does not copy it", "search only what it does not answer"), design.md:57 (principle 2) and design.md:131.
  - The Contract dependents clause applies the ticket's rule where planner.md:40 would otherwise repeat the scout's `git grep`. The Contract dependents paragraph itself stays unchanged, so that rule keeps one home.
- **Builder sentence.** Append this exact sentence to builder.md's first paragraph, after "...follow it for the files it governs." (builder.md:5): `When the handoff cites a scout, researcher, architect, or archaeologist result, read that result's `## Carry forward` section before searching the code, and search only what it does not answer.`
- **Inline only in planner.md and builder.md.** There, `## Carry forward` appears only inline in backticks, never as a heading line, so neither role's own output template gains the section.
- **results.py schema.** Append `'Carry forward'` as the last entry of the `sections` tuple of `researcher`, `scout`, `archaeologist`, and `architect` in `SCHEMA` (results.py:42-49).
  - Keys stay `Answer`, `Map`, `Summary`, `Approach`.
  - Only the key section is required (results.py:9-11). A result without the section, including every result written before this ticket, still validates.
  - A `## Carry forward` that is present must follow the other declared sections present. This enforces "ends its result".
  - The planner and builder schemas do not change.
- **results.py selftest.**
  - Append `\n## Carry forward\n- x\n` to the four roles' `bodies` entries.
  - Change the expected value of the `schema prints - for a role with no allowed set` case (results.py:295) to `['scout\tMap\t-\tMap|Entry points|Not found|Carry forward']`.
  - Add a case with the exact label `a scout result without ## Carry forward passes`: `head('scout')` plus `## Map\nm\n\n## Entry points\ne\n\n## Not found\nNone\n`, expecting `None`.
  - Add a case with the exact label `a scout result with ## Carry forward before ## Map fails`: `head('scout')` plus `## Carry forward\n- x\n\n## Map\nm\n`, expecting `## Carry forward comes before ## Map`.
- **check.py guard.** Add a Carry forward guard after the Lean lane text guard (check.py:385-397), using the same pattern: a dict `CARRY_FORWARD` maps each phrase to the files that must hold it.
  - `'## Carry forward'`: agents/scout.md, agents/researcher.md, agents/architect.md, agents/archaeologist.md, agents/planner.md, agents/builder.md.
  - `'at most 15 lines'`: the four producing contracts.
  - `'search only what it does not answer'`: agents/planner.md and agents/builder.md.
  - `'cite the result path'`: agents/planner.md.
  - Error lines, exactly: `<rel>: carry-forward text missing "<phrase>"` when the phrase is absent, and `<rel>: carry-forward negative control not flagged` when `text.replace(phrase, '')` is not flagged.
  - Add docstring item `15. Carry forward:` naming those pairs. State that each pair has a negative control, and that results.SCHEMA declares `Carry forward` last for the four producing roles, so item 13 also requires the heading line there. Label the code comment `(docstring item 15)`.
- **Regenerate.** After all agent edits, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. The TOMLs embed each role body (codex_roles.py `instructions()`), so the scout, researcher, architect, archaeologist, planner, and builder TOMLs change.

Contract dependents:
- results.py:295 pins the scout schema line. It is updated in this step.
- check.py item 13 (check.py:416-429) requires every SCHEMA section as a heading line in agents/<role>.md. The four template edits satisfy it.
- `plugins/sdlc-lite/scripts/codex-selftest.py:25` writes a scout result without the section. Leave it untouched, because the section is optional. Run `python3 plugins/sdlc-lite/scripts/codex-selftest.py` as a focused check.
- `run.sh` stays untouched. It validates with `results.py validate` (run.sh:464) and picks the result by `results.py key` (run.sh:440), and no key changes. This answers the ticket's "run.sh required-section handling if affected".
- `steps.py` stays untouched. It reads results through `results.structure_error` and `key_value` only for planner, plan-reviewer, builder, and verifier.
- The seven committed producer results under `.sdlc/` must keep validating (criterion 6).
- Left untouched on purpose:
  - architect.md's read rule: the ticket gives the reader rule to the planner and builder only.
  - `docs/maintenance/sdlc-internals.md`: its results.py entry describes the schema mechanics, which do not change.
  - `docs/lean-sdlc/design.md`: a proposal record.
  - `skills/handoff-format/SKILL.md`: the layout is unchanged.

Negative controls, red before this step and green after:
- Criterion 5: an out-of-order fixture fails validate.
- Criteria 7 and 8: check.py on a plugin copy with the heading or the reader phrase removed prints the FAIL line.

The check.py guard here is this step's own checker, not a repo gate; the whole gates stay on step 2. Write no em dashes.

Depends on: none. Focused checks: `python3 plugins/sdlc-lite/scripts/results.py selftest`, `python3 plugins/sdlc-lite/scripts/check.py`, `python3 plugins/sdlc-lite/scripts/codex-selftest.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`.
### Acceptance criteria
- `for f in scout researcher architect archaeologist; do p=plugins/sdlc-lite/agents/$f.md; test "$(grep "^## " "$p" | tail -n 1)" = "## Carry forward" || exit 1; grep -qF "at most 15 lines" "$p" || exit 1; done`
- `for f in planner builder; do grep -qF "search only what it does not answer" plugins/sdlc-lite/agents/$f.md || exit 1; grep -qF "## Carry forward" plugins/sdlc-lite/agents/$f.md || exit 1; done && grep -qF "cite the result path" plugins/sdlc-lite/agents/planner.md && ! grep -qx "## Carry forward" plugins/sdlc-lite/agents/planner.md plugins/sdlc-lite/agents/builder.md`
- `for r in scout researcher architect archaeologist; do python3 plugins/sdlc-lite/scripts/results.py schema --role $r | grep -q "|Carry forward$" || exit 1; done`
- `out=$(python3 plugins/sdlc-lite/scripts/results.py selftest) && printf "%s\n" "$out" | grep -qF "ok: a scout result without ## Carry forward passes" && printf "%s\n" "$out" | grep -qF "ok: a scout result with ## Carry forward before ## Map fails"`
- `t=$(mktemp) && printf "<!-- role=scout level=L1 model=claude-haiku-4-5 effort=low -->\n## Carry forward\n- a\n\n## Map\n- b\n" > "$t" && python3 plugins/sdlc-lite/scripts/results.py validate "$t" 2>&1 | grep -qF "## Carry forward comes before ## Map"`
- (guard) `fs=$(git ls-files .sdlc | grep -E "/(scout|researcher|architect|archaeologist)-L[0-9][^/]*\.md$") && test -n "$fs" && for f in $fs; do python3 plugins/sdlc-lite/scripts/results.py validate "$f" || exit 1; done`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && python3 -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.write_text(p.read_text().replace(\"## Carry forward\", \"\"))" "$t/p/agents/scout.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/p" | grep -qF "agents/scout.md: result schema: missing ## Carry forward"`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && python3 -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.write_text(p.read_text().replace(\"search only what it does not answer\", \"\"))" "$t/p/agents/builder.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/p" | grep -qF "agents/builder.md: carry-forward text missing"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- `grep -qF "search only what it does not answer" plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml && grep -qF "cite the result path" plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l2.toml && grep -qF "## Carry forward" plugins/sdlc-lite/adapters/codex/agents/sdlc-scout-l1.toml`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/agents/(scout|researcher|architect|archaeologist|planner|builder)\.md|plugins/sdlc-lite/scripts/(results|check)\.py|plugins/sdlc-lite/adapters/codex/agents/sdlc-[a-z0-9-]+\.toml)$" | grep -q .`
- (guard) `! grep -qF "—" plugins/sdlc-lite/agents/scout.md plugins/sdlc-lite/agents/researcher.md plugins/sdlc-lite/agents/architect.md plugins/sdlc-lite/agents/archaeologist.md plugins/sdlc-lite/agents/planner.md plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/scripts/results.py plugins/sdlc-lite/scripts/check.py`
