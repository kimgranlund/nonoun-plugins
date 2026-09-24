# Domain: Technical Architecture

> `decompose` domain reference. Method depth in `method.md`. · 2026-06-26

## OUTSIDE-IN axis (structure)

`system → subsystems → modules → units`

- **system** — the bounded thing being built (a package, a service).
- **subsystems** — major internal divisions, ideally along the layering boundaries (e.g. `reactive ← dom ← traits ← controls`).
- **modules** — single-responsibility files/objects within a subsystem.
- **units** — the smallest independently testable function/class/type.

## INSIDE-OUT axis (behavior)

`capabilities → interfaces → data → integration`

- **capabilities** — what the system must do (parse a stream, validate a payload, persist a record).
- **interfaces** — the typed contract each capability is reached through.
- **data** — the structures/schemas the capability owns or moves.
- **integration** — the wiring/seams where a capability meets another module or an external system.

## Stop rule

Stop dividing a module when it is **one responsibility, one interface, one owner** — a buildable unit. A unit that needs two unrelated interfaces is two units; a "module" no one owns is a missing boundary.

## Cross-check (defect quadrant)

- Every capability must map to a module that exposes it → else `UNHOSTED` (a required behavior with no home — the gap that becomes "where does this live?" mid-build).
- Every leaf module must expose a capability **or** carry a `justify` (`adapter`, `shared-util`) → else `UNJUSTIFIED-LEAF` (a speculative layer).
- Honor the dependency direction: a unit hosting a capability must sit in a layer allowed to own it (inward-only).

## Worked pass (the A2UI renderer subsystem)

OUTSIDE-IN: `renderer` → `{stream, surface, tree, binding, action, validate}` (modules).
INSIDE-OUT capabilities: `parse JSONL`, `manage surface state`, `reconstruct tree`, `resolve bindings`, `emit/correlate actions`, `validate payload`.
Map: all host cleanly; `validate` is shared (corpus + runtime) → tag the seam as `integration`. Re-check → clean. (Matches the A2UI project's renderer LLD in its `.claude/docs/llds/` — lifecycle docs live repo-side, not in this bundle.)

```json
{
  "domain": "technical-architecture",
  "nodes": [
    {"id":"stream","label":"stream","leaf":true},
    {"id":"surface","label":"surface","leaf":true},
    {"id":"tree","label":"tree","leaf":true},
    {"id":"binding","label":"binding","leaf":true},
    {"id":"action","label":"action","leaf":true},
    {"id":"validate","label":"validate","leaf":true}
  ],
  "actions": [
    {"id":"parse","label":"parse JSONL"},{"id":"state","label":"manage surface state"},
    {"id":"recon","label":"reconstruct tree"},{"id":"bind","label":"resolve bindings"},
    {"id":"act","label":"emit/correlate actions"},{"id":"val","label":"validate payload"}
  ],
  "hosts": [
    {"action":"parse","node":"stream"},{"action":"state","node":"surface"},
    {"action":"recon","node":"tree"},{"action":"bind","node":"binding"},
    {"action":"act","node":"action"},{"action":"val","node":"validate"}
  ]
}
```
