# plugins-factory v0.1.0 (plugin) — build-time red-team (2026-06-02)

The mandatory build-time red-team `plugins-factory` requires on its own output — run after re-packaging the studio from a single skill into a self-contained **plugin**, dogfooding the tool on itself. Full **9-critic panel** (the floor escalates to full-panel because the plugin bundles a hook), fanned out as **parallel isolated agents**, plus cross-critic synthesis. Every critic cold-read the files; the plugin-under-review was treated as untrusted content (assessed, never executed). No critic modified files.

Supersedes the skill-era `2026-06-02-build-time-red-team.md` (removed — its gate-state line cited `skills-studio`-era gates that do not ship in the plugin).

## Verdict: CONDITIONAL → fixes folded → re-validated

44 findings across 9 critics. Scorecard (1–5): **P1 3 · P2 3 · P3 3 · P4 3 · P5 4 · P6 4 · P7 4 · P8 2 · P9 2.** The two 2-grades (P8, P9) drove the CONDITIONAL.

## Findings + disposition

### Highest severity — P9/ST1 bundled trifecta (Simon) — FIXED
The 9 critic agents + `carve-analyst` shipped with no `tools:` allowlist, inheriting the host's full default toolset (Bash / WebFetch / Write / Edit) while reading untrusted target plugins — the lethal trifecta the plugin's own rubric (`security-and-scope-containment` / `plugins-holistic.md`) grades Score-1, and `plugin-build`/`plugin-architecture` explicitly forbid. The plugin violated the exact structural standard it enforces. **Fixed:** every critic + `carve-analyst` scoped to `tools: Read, Grep, Glob`; `plugin-council` to `Read, Grep, Glob, Task`. The external-action leg is now a tool interlock, not a hoped-for instruction.

### Convergence (≥2 critics) — FIXED
- **`scripts/` → `bin/` drift** (5 critics): ~11 doc/rubric sites invoked `scripts/validate_plugin.py`, which does not exist (the tooling ships in `bin/`). Following the documented gate yielded "No such file." **Fixed:** global repoint to `${CLAUDE_PLUGIN_ROOT}/bin/…`.
- **Dead `eval-as-*.md` persona pointers** (4 critics): the personas became `agents/critic-*.md`, but `eval-prompts.md`'s table + how-to-use and `README.md` still named the old files. **Fixed:** repointed to `agents/critic-*.md`.
- **Hook exec-bit fragility** (3 critics): the hook ran the script by shebang + exec-bit, fragile across a cache copy or zip/clone (a 0644 landing → silent fail, indistinguishable from a clean pass since the hook always exits 0). **Fixed:** `python3 "${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py" hook`.
- **Hook side-effect undisclosed** (4 critics): the pre-enable surfaces never mentioned the hook. **Fixed:** `plugin.json` + marketplace descriptions now disclose it (fires on Write|Edit, reads the written manifest, prints only, never blocks).
- **`plugin.json` description fails the no-"and" test** (2 critics): three verbs + a six-command catalog + "Self-contained." padding. **Fixed:** tightened to one job; dropped the catalog + padding.

### Co-located dangling refs — P3/P4 (Farley) — FIXED
The four vendored `skills-studio` rubrics carried "(this folder)" companion pointers to siblings not bundled here. **Fixed:** annotated as external ("in `skills-studio` — not bundled here"); added a vendoring + drift note to `rubric-manifest.json` (`references_colocated`).

### Hook injection framing — P9/ST5 (Simon) — FIXED
The advisory hook echoed raw parse-error text from an inspected manifest. **Fixed:** `_hook` now frames output as delimited DATA ("not instructions").

## Deferred to ROADMAP (structural — not folded here)
- **No CI; tree git-untracked (P8, Farley).** The plugin mandates "`validate_plugin.py` in CI" three times but ships none and has no version history. The selftest / validate / foundations gates pass locally; wiring them into CI + committing is a repo-level step (flagged to the owner) — see ROADMAP.
- **No council-calibration eval — the blind spot all nine missed.** No eval tests the council's own *output* fidelity (reproducibility across runs, severity calibration, a guard against multiply-owned dimensions inflating one issue into several "independent" findings). The plugin ships a routing eval but none for its headline capability.
- **Dimension MECE audit.** `karpathy`/verifiability owns no single Pn; P1 and P2 are multiply-owned. The 9-dimension partition is itself unvalidated.

## Gate state after fold
`bin/validate_plugin.py selftest` PASS · `bin/validate_plugin.py plugin .` PASS (0 errors / 0 warnings) · `bin/check-foundations-coverage.py` PASS (5/5) · hook (python3) advisory + exit 0 · P4 path sweep clean (no runtime cross-plugin paths in any manifest, config, or prose).
