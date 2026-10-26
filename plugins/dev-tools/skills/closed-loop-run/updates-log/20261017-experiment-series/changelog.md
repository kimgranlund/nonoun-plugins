---
date: 2026-10-17
slug: experiment-series
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: conductor
    agent: sdlc-lite conductor (main session)
    model: claude-opus-5-5
    did: wrote the handoff (task folder closed-loop-run-series) and the lesson outline from nine live cycles, dispatched the solo
  - role: solo
    agent: sdlc-lite:solo-L3 (clr-solo-L3)
    model: claude-opus-5-5
    did: SKILL.md restructure and additions, references/experiment-series.md, references/live-evaluation.md, references/diagnosis.md, references/records.md, additions to references/control-model.md and references/verification-ladder.md, templates/cycle-report.yaml series block, README.md, this updates-log
  - role: verifier
    agent: sdlc-lite:verifier-L3
    model: fable
    did: independent verification, verdict pass; five fix-now items and twelve notes, applied by the solo after the verdict
project: nine live closed-loop cycles on a generative UI runtime (a private repo), three model sizes, capped spend
verification: pass (verifier fable L3, 2026-10-17), fix-now items applied after
backup: /private/tmp/claude-501/scratch/clr-backup-1792235237
---

# 2026-10-17: running a series of live, paid cycles; SKILL.md restructure

SKILL.md went from 490 lines to 253. No sentence was dropped: a sentence-level coverage check compared every backup SKILL.md sentence against the new SKILL.md plus `references/**/*.md` after normalizing punctuation (365 sentences: 364 present, 1 renamed heading listed). Every em dash in the skill was replaced; section 2 invariants are verbatim.

## Added
- `references/experiment-series.md`: the series loop; a fixed comparison set rerun unchanged (compare only identical runs); alternating targeted and full cycles; regression accounting by transition (pass to fail churn beside the pass rate); one mechanism metric per fix with the verdicts fixed live, partly, not exercised, regressed; an approval gate before each paid cycle; fixing tooling gaps under test before the next cycle; when a series stops.
- `references/live-evaluation.md`: single-sample noise and when to sample N; cheapest first under a hard cap; a dry run before spend; credential and quota preflight; quarantine of provider errors and runner crashes; freezing failures as keyless replays before fixing; recorded versus authored repair rounds (mechanism, not compliance); keeping every cycle's evidence.
- `references/diagnosis.md`: the diagnosis sequence and the root-cause taxonomy (moved), plus rule out lost context first, uniform errors point at your own pipeline, the two Evaluation failure modes (check narrower than its rule, oracle too generic), cause classes (a) to (d) for model-driven systems, and any/only cluster counts.
- `references/records.md`: the episode, attempt, learning record and cycle report YAML shapes (moved verbatim), a `series` block for cycle reports, and the output behavior list (moved).
- SKILL.md section 17 "Running a series", linking both new references.
- `updates-log/` with `AGENTS.md`, `CHANGELOG.md` and this entry.

## Changed
- `SKILL.md` section 6: two root-cause steps first (lost context, uniform errors). Section 7: categories as one line with definitions in `references/diagnosis.md`, the two Evaluation failure modes, and the cause-class mix. Section 13: any/only counts and the uniform-errors link. Section 14: one independent verifier; adversarial review on a different model family for changes to anything a model reads. Section 15: hardening layers as one line, plus one cause per change, every fix shifts a cost, rulings register with pin tests, regenerate derived artifacts in the same change. Sections 16 to 20 renumbered; anti-patterns gain two series items. Description adds the series use.
- `references/control-model.md`: run protocol, checkpoints, concurrency, cost-aware strategy and universal adaptation moved in; an H4 series note.
- `references/verification-ladder.md`: ladder levels in SKILL.md terms and the inside-out and outside-in checklists moved in; a note on V4 and V0 for live systems.
- `templates/cycle-report.yaml`: `series` block (comparison set, kind, compared_to, transitions, mechanism metrics, quarantined provider errors, spend vs cap and stop, frozen replays, tooling gaps).
- `README.md`: lists the references and the updates-log.

## Fixed
- None. No behavior of an earlier rule changed; the README line that named only two references was stale and now lists all six.
- After verification (solo, from the verifier's fix-now items and notes): the owner is defined once in SKILL.md section 1 (the person or governing caller who holds the budget, approves paid cycles, settles rulings) and names the approver of every paid cycle; section 3 says a report's `next_cycle.required` is never that approval; lost context left cause class (a); a cell not run is partial, and zero usable samples after N attempts is failed; "end the episode" became "end the scenario" and "actor" became "system under test" or "model"; rulings register shape and home; the two dropped output-behavior rules restored in SKILL.md section 16; debate before the change, verifier after, and why a pass is final; "useful failure" defined; `regressions` points at `series.transitions.pass_to_fail`; list prices stated as an upper bound; first-cycle spend estimate; the pass to fail row notes sample-1 noise; a class (c) stand-in when no stronger model exists; a second, non-booking oracle example.

## Open
- `examples/generative-ui.md` has no series example; add one when the skill next runs a series end to end.
- Field-test the series references on a fresh series with an agent that has not seen this change.
