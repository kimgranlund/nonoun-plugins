## Task goal
Bind each native request to its dispatched profile fingerprint. Reject missing or stale fingerprints in normal responses.

## Step 2: Describe the binding, regenerate profiles, record evidence, gates green
level: L2
guard timeout: 600
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
Depends on: step 1.

Targets: `plugins/sdlc-lite/adapters/codex/instructions.md` (the "Profile handshake" paragraph and the two `codex_exchange.py` paragraphs above it), `docs/references/codex-role-execution.md` (the "Report envelope" section and the native transport paragraph), the generated `plugins/sdlc-lite/adapters/codex/agents/sdlc-*.toml`, and a new report. [creates: docs/reports/2026-10-12-codex-exchange-fingerprint-binding.md]

Settled wording, in both documents:
- Each native request carries `profile_fingerprint`, the binding captured at dispatch. `codex_roles.py handshake --binding` takes that value from the request file.
- `codex_exchange.py` refuses a normal report whose first line is not `profile: <that binding>`: exit 2, no response written, the request stays waiting. The conductor then answers with `--failed` and the refusal message as the reason, and starts a fresh Codex session for a new run. It never edits the report to add the line.
- `--failed` needs no profile line.
- The pre-edit handshake stays a conductor instruction. Include the exact phrase "does not prove the role checked before it edited" for the final-report check, and say the fingerprint is self-reported.
- In `codex-role-execution.md`, name the two new `runs.jsonl` keys and the three new tests as the regression.

`instructions.md` is the prelude of every profile (`codex_roles.py` `instructions()`), so the edit changes all 28 fingerprints: run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` and never hand-edit a TOML.

Left untouched on purpose: `envelope_note` in `codex_roles.py`, `agents/solo.md`, and `skills/sdlc-lite/SKILL.md` tell the role or conductor what to send and stay accurate. `docs/references/sdlc-internals.md` does not mention the exchange (`grep -c codex_exchange` prints 0). `docs/reports/2026-10-12-sdlc-lite-astra-review.md` and its folder are immutable.

The report records the commands run and their results for the missing, stale, current, changed-after-dispatch, and `--failed` cases, the baseline failing output from step 1, and handoff criterion 7 as unverified: a fresh callable named-agent Codex run cannot run on this Claude host without nesting a CLI. No step here proves live Codex behavior.

Run every gate below and fix any red step 1 introduced. A gate already red at the build-start HEAD comes back as `inherited red`. The Progressive Context performance-contract link failure is out of scope. The rest of `check.sh` belongs to the `fanout.py land` gate.
### Acceptance criteria
- `grep -qF profile_fingerprint plugins/sdlc-lite/adapters/codex/instructions.md && grep -qF "does not prove the role checked before it edited" plugins/sdlc-lite/adapters/codex/instructions.md`
- `grep -qF profile_fingerprint docs/references/codex-role-execution.md`
- `grep -qF profile_fingerprint plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`
- `test -f docs/reports/2026-10-12-codex-exchange-fingerprint-binding.md && grep -qi unverified docs/reports/2026-10-12-codex-exchange-fingerprint-binding.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- docs/reports/2026-10-12-sdlc-lite-astra-review docs/reports/2026-10-12-sdlc-lite-astra-review.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/scripts/(codex_exchange\.py|codex-selftest\.py|lifecycle-selftest\.py|run\.sh|solo_run\.py)|plugins/sdlc-lite/adapters/codex/instructions\.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-[a-z0-9-]+\.toml|docs/references/codex-role-execution\.md|docs/reports/2026-10-12-codex-exchange-fingerprint-binding(\.md|/.*))$" | grep -q .`
