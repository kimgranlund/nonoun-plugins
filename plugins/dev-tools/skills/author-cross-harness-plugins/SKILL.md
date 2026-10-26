---
name: author-cross-harness-plugins
description: >-
  Creates or migrates one-source plugins that load in both Claude Code and
  Codex, preserving skills, agents, commands, hooks, MCP wiring, scripts, and
  package metadata through shared cores and thin host adapters. Use when the
  user asks to build, port, package, audit, or repair a plugin for both
  harnesses. NOT for a plugin intentionally targeting only one harness.
---

# Cross-Harness Plugin Authoring

Build one behavioral source of truth with two package adapters. A surface is
portable only when both harnesses preserve its invocation, inputs, tools,
side effects, and output—not merely when both load a file with the same name.

## Operating contract

1. Inspect the target repository, its local instructions, and every existing
   plugin surface before choosing a layout. Apply the
   [repository-entry contract](references/repository-entry.md) when the target
   uses `CLAUDE.md`, `AGENTS.md`, or repository-local skill adapters.
2. Classify each surface as shared, adapted, or host-only. Never silently drop
   a host-specific field or pretend that a partial translation is equivalent.
3. Keep essential behavior in shared skills, command bodies, scripts, and
   references. Host adapters contain metadata, path substitution, or native UX
   only; they do not own the workflow.
4. Create both manifests in the same plugin directory and keep identity fields
   synchronized.
5. Record every unavailable semantic in `HARNESS-NOTES.md` with the affected
   surface, the target harness, and the fallback.
6. Run the bundled validator. Match live checks to the changed surface: use
   fresh sessions in both harnesses when changing cross-host routing or behavior.

## Authoring route

- Read [architecture.md](references/architecture.md) before choosing or
  changing the plugin tree.
- Read [surface-matrix.md](references/surface-matrix.md) for every surface the
  requested plugin ships. It defines the portable subset and the adapter rule.
- Read [claude-code.md](references/claude-code.md) when writing the Claude
  manifest or adapter files.
- Read [codex.md](references/codex.md) when writing the Codex manifest,
  `openai.yaml`, or marketplace entry.
- Read [readme-schema.md](references/readme-schema.md) when writing or auditing a plugin's
  README — the required section order (install both harnesses, getting-started with operator
  examples, filing instructions, the marker-fenced generated inventory, release ledger) and the
  everything-in-one-file rule.
- Read [behavioral-fidelity.md](references/behavioral-fidelity.md) BEFORE authoring any
  command-shaped, verifier, or intake surface — the live-eval-earned rules (body backstops for
  human-only timing, first-sentence routing exclusions, construction-rules-over-prohibitions,
  dispatch-await, eval-loop method). Structural validation catches none of these.
- Read [evidence-contract.md](references/evidence-contract.md) before claiming
  cross-host verification. It defines staged evidence, first-session preflight,
  retained-event requirements, and revision isolation.
- Read [repository-entry.md](references/repository-entry.md) when adding or
  reviewing repository instructions. Keep one shared authority, use thin host
  entry files, preserve existing precedence, and verify the committed clone view.

For an existing plugin, preserve its public names and behavior unless the user
explicitly authorizes a migration. Move duplicated workflow instructions into
the shared core, then reduce each adapter to its real host delta.

## Verification

Run:

```bash
python3 <this-skill-dir>/scripts/validate_cross_harness.py <plugin-root>
```

Errors block completion. Warnings require either a correction or an explicit
entry in `HARNESS-NOTES.md`. A clean structural result is not behavioral proof.
For changed routing or execution, freeze the exact candidate and configuration
identity, then exercise a should-trigger prompt, near miss, explicit invocation,
and observable completion condition in fresh top-level processes for each affected
host. Run the full dual-host matrix when claiming cross-host behavior or changing
shared behavior; a documentation-only edit needs local link and consistency checks.
New mechanical gates need a negative control. A child agent or worktree can isolate
writes and prove resulting artifacts; it does not by itself prove top-level
discovery, advertisement, selection or loading. Choose an available model and
reasoning effort deliberately for live trials and record both with the result.

Retain raw host events and exact output. Grade packaging, activation,
advertisement, selection, body/resource loading, execution, completion and cleanup
as separate stages. Record requested and observed model identity independently,
and use `unverified` where the host exposes no decisive event. Agent self-report
and answer quality are supplementary evidence only. Apply
[behavioral-fidelity.md](references/behavioral-fidelity.md) §9's complete eval-loop
method, including answer-key exclusion, verbatim mismatch output and a regression
case per demonstrated defect.

## Result

Report:

- shared source surfaces;
- Claude adapters created or changed;
- Codex adapters created or changed;
- validation and behavioral checks run, with exact candidate/config identities;
- per-stage evidence outcomes and retained raw-event locations;
- documented degradations, unverified stages or missing live-harness verification.

Done means both manifests load the intended surfaces and essential behavior has
an equivalent path in each harness. A package that only loads without preserving
behavior is not done.
