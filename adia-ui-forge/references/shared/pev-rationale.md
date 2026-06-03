# Plan-Execute-Verify Rationale

## Statement

Every rollup-family skill follows the **Plan → Execute → Verify** loop on every invocation. The loop is the load-bearing centerpiece of the skill ecosystem. Every other discipline (§Teach, §SelfAudit, audit-roster scripts, check-\* gates) exists to make the loop reliable.

## The three phases

**Plan** — Classify the intent. Pick the right mode from the cold-start menu. **Name the verify target up front.** If you cannot name how you'll know the work succeeded, you don't have a plan — you have a vibe.

**Execute** — Run the mode procedure. Capture artifacts the verify step will read (build output, render screenshots, eval logs, registry response). Avoid premature claims of "done": execute is the middle step, not the last one.

**Verify** — **Run the result against the real product or substrate**, not against the skill's own self-checks. The skill is not done until the external signal (curl, render, eval, audit script) confirms the work matches intent.

## What "verify against reality" looks like, per skill class

| Skill class | Real-product verify target |
| --- | --- |
| Release skill | `curl https://registry.npmjs.org/<pkg>/<version>` returns 200; `curl https://<production-host>/` returns 200 with the new build hash |
| Authoring skill (in-repo source) | Build verify passes (zero drift) + the affected primitive's demo page renders correctly |
| Composition / UI-kit skill | The composed HTML renders correctly in a real demo / app; Playwright snapshot or visual sweep against intent |
| Pipeline / generation skill | Eval thresholds hold (cov, avg, MRR, F1); MCP smoke; tool round-trip |
| Substrate-ops skill | Production endpoint returns the desired response; audit script re-run shows 0 findings |
| Audit / dogfood skill | Re-running the audit on the touched surface shows the original critical finding is absent |
| Migration skill | Sweep-verification audit reports 0 hits in legacy-pattern set; build gate green |

## Source citation

> _"A good plan is really important to avoid issues down the line. Once there is a good plan, it will one-shot the implementation almost every time."_
>
> _"Give Claude a way to verify its work. If Claude has that feedback loop, it will 2-3x the quality."_
>
> — Boris Cherny, Head of Claude Code (Pragmatic Engineer interview, howborisusesclaudecode.com)

This was identified in a senior-engineering review as **the most-cited Boris principle and the ecosystem's biggest initial gap.** The skill family had §SelfAudit (audit-the-skill drift detection) but no equivalent discipline for verifying _the output_ of a skill invocation. Boris's verify-the-output (browser, test suite, simulator) is what 2-3x's quality — and it had no analog.

A PEV elevation sweep made PEV the load-bearing centerpiece across the senior skill ecosystem. Every senior skill now carries a top-band `## §Plan-Execute-Verify` H2 in SKILL.md with a per-mode verify-target table naming the **real-product** verify target for each mode.

## PEV vs §SelfAudit — two disciplines, both required

`§SelfAudit` (the `audit-<skill>-roster.mjs` pattern) checks the **skill's own** invariants — catalogs, gate rosters, sibling-file parity, capability-menu vs section-content consistency. It is a different discipline from verify-the-output.

| Discipline | What it checks | What happens without it |
| --- | --- | --- |
| **Verify-the-output (PEV)** | Did the invocation produce the right artifact in reality? | The skill ships broken outputs; users hit defects the skill could have caught |
| **§SelfAudit** | Is the skill itself drift-free against its own claims? | The skill rots over time; menu items point to nothing; instructions name files that don't exist |

A skill with only §SelfAudit is well-maintained but may ship broken output. A skill with only verify-the-output is correct today but rots over time. **A first-class senior skill has both.**

## How this binds into the harness (5-point PEV-binding check)

Every senior skill MUST satisfy these 5 points:

1. **A top-band `## §Plan-Execute-Verify` H2** in SKILL.md (above the §LoadingProtocol or §FileMap; visible from cold-start triage).
2. **A per-mode verify-target table** in §PEV naming the _real-product_ verify for each mode (not internal self-checks).
3. **A cross-reference from §Teach** pointing back to §PEV (so §Teach landings inherit the loop).
4. **A cold-start triage mention** of PEV (so agents pick a mode knowing the loop is mandatory).
5. **The `skill.json` description** mentions verification or the verify target by name (so routing favors skills that close the loop).

A `scripts/skills/check-pev.mjs` substrate-side gate enforces these 5 points; all senior skills pass `--strict` at the time of elevation.

## Source

The verify-the-output discipline distilled here was vendored from the framework monorepo's senior-engineering review notes and extensibility vision. **Skills citing PEV should reference THIS file (`${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md`), not the monorepo-only source docs** — those substrate paths don't resolve in consumer repos where many of these skills are invoked.
