## Task goal
`/sdlc-lite:report` prints a short executive summary of the current agent thread by default, and the named views (tasks, signals, needs, context, cost, children, identity, evidence, full) on request, from records and the transcript, with no model call in the collector.

## Step 2: report skill, routing, check.py pins, live run, gates green
level: L3
guard timeout: 2700
### Do
Depends on: step 1.

Create the skill folder `plugins/sdlc-lite/skills/report/` [creates: plugins/sdlc-lite/skills/report/SKILL.md]. Copy the three drafts into it:
- `.sdlc/0460-report-skill/draft/SKILL.md` becomes `SKILL.md`.
- `draft/references/views.md` becomes `references/views.md`.
- `draft/references/record-schema.md` becomes `references/record-schema.md`.

Then adjust the copies:
- In the SKILL.md Rules, replace the `docs/specs/doc-standards/core.md` citation with a link to `references/views.md#entry-grammar`, where the verb list already lives. A consumer install has no `docs/`, and plugin AGENTS.md requires a self-contained skill (check.py item 42).
- State in the skill that the Codex transcript mapping is unverified.
- Align `references/record-schema.md` with what step 1 built: the `schema` key, the nine groups, the `health.context` keys, the `unknown` dotted paths, the `report.<key>` config thresholds, and the problem versus likely severity.
- Keep the `**Codex host:**` paragraph. check-packaging.py requires the `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` route in every skill.

Wiring. Each item is a contract dependent found by `git grep -l fleet-status -- . ':(exclude).sdlc' ':(exclude)docs/reports'`, fleet-status being the nearest existing render-never-compose skill:
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: add the routing row `| This thread's state: what finished, what runs, what is next, what needs the user, what is wrong | report |` beside the `board` and `fleet-status` rows.
- `plugins/sdlc-lite/scripts/check.sh`: add `python3 "$root/scripts/report.py" selftest || fail=1` after the `fleet_status.py` line, and name `report.py` in its header comment list.
- `plugins/sdlc-lite/scripts/check.py`: add a docstring item starting `<n>. Report`, where `<n>` is the next free number after the highest present. Other wave-40 lanes may also add items, so take the number at build time. Add a block modeled on item 37 (`FLEET_STATUS_NEEDS`, `fleet_status_bad`):
  - `REPORT_NEEDS` pins these phrases in `skills/report/SKILL.md`: `report.py render`, `Render, never compose`, `Codex host`, `Exit 2 is a refusal`, `references/views.md`, `references/record-schema.md`.
  - It pins these phrases in `scripts/report.py`: `VERBS`, `CollectorError`, `session-status/1`, `def selftest`.
  - It pins `report.py" selftest` in `scripts/check.sh`, and the routing row `| report |` in `skills/sdlc-lite/SKILL.md`.
  - A planted `harness:` reference in the skill is flagged.
  - Errors print with the prefix `check.py: report:`.
  - Negative controls: each phrase removed from each file, a harness reference, and the routing row removed must each be flagged, else check.py fails.
- `plugins/sdlc-lite/AGENTS.md` Verification list: add `- Thread report: \`python3 plugins/sdlc-lite/scripts/report.py selftest\`.`
- `docs/references/sdlc-internals.md`: add one short entry for `report.py` (subcommands, sources, snapshot path, `report.<key>` thresholds). The file has one entry per script.
- `docs/README.md` names fleet-status only inside a dated release line. Leave it unchanged on purpose, because release notes are history.

Live run:
- Run `python3 plugins/sdlc-lite/scripts/report.py render` once on this repo. The default writes one snapshot under the gitignored `.sdlc/runtime/report/`.
- Run it once more with `full`.
- Write `.sdlc/0460-report-skill/notes.md` [creates: .sdlc/0460-report-skill/notes.md] with the date, the command `report.py render`, what it printed, and what was listed under `unknown`.

Gates. This is the gates green step. Run each of these and fix any red that step 1 or this step introduced in the files in scope:
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- `git diff --check "$SDLC_BASE_SHA"`
- `bash plugins/sdlc-lite/scripts/check.sh` (about 900 s on record)

A gate that is already red at the build-start HEAD is reported as `inherited red`. check.sh and check.py are hot files: one writer at a time.
### Acceptance criteria
- (red) `for ph in "report.py render" "Render, never compose" "Codex host" "Exit 2 is a refusal" "references/views.md" "references/record-schema.md"; do grep -qF "$ph" plugins/sdlc-lite/skills/report/SKILL.md || exit 1; done && test -f plugins/sdlc-lite/skills/report/references/views.md && test -f plugins/sdlc-lite/skills/report/references/record-schema.md`
- (red) `test -f plugins/sdlc-lite/skills/report/SKILL.md && ! grep -rqF "docs/" plugins/sdlc-lite/skills/report`
- (red) `grep -qF "| report |" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md && grep -qF "report.py\" selftest" plugins/sdlc-lite/scripts/check.sh && grep -qF "report.py selftest" plugins/sdlc-lite/AGENTS.md && grep -qF "report.py" docs/references/sdlc-internals.md`
- (red) `grep -qE "^[0-9]+\. Report" plugins/sdlc-lite/scripts/check.py && grep -qF "skills/report/SKILL.md" plugins/sdlc-lite/scripts/check.py`
- (red) `t=$(mktemp -d "${SDLC_TMP_WORKTREES:-${TMPDIR:-/tmp}}/rep.XXXX") && cp -R plugins/sdlc-lite "$t/sdlc-lite" && python3 -c "import pathlib, sys; f = pathlib.Path(sys.argv[1]); f.write_text(f.read_text().replace(\"Render, never compose\", \"x\"))" "$t/sdlc-lite/skills/report/SKILL.md" && python3 "$t/sdlc-lite/scripts/check.py" "$t/sdlc-lite" | grep -qF "check.py: report:"`
- (red) `grep -qF "report.py render" .sdlc/0460-report-skill/notes.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vE "^plugins/sdlc-lite/skills/report/" | grep -vxE "plugins/sdlc-lite/scripts/report.py|docs/specs/doc-standards/core.md|docs/references/glossary.md|plugins/sdlc-lite/skills/sdlc-lite/SKILL.md|plugins/sdlc-lite/scripts/check.sh|plugins/sdlc-lite/scripts/check.py|plugins/sdlc-lite/AGENTS.md|docs/references/sdlc-internals.md")" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^plugins/sdlc-lite/skills/report/" | grep -vxE "plugins/sdlc-lite/scripts/report.py|docs/specs/doc-standards/core.md|docs/references/glossary.md")"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- (guard) `git diff --check "$SDLC_BASE_SHA"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
