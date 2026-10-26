# Verification Ladder

Use the cheapest trustworthy check first, then widen.

| Level | Purpose | Typical examples |
|---|---|---|
| V0 Direct | Did this exact change achieve the local signal? | assertion, probe, focused visual check |
| V1 Local | Is the directly affected artifact correct? | unit test, component test, section validation |
| V2 Neighbor | Did immediate dependencies remain correct? | package/subsystem tests, linked workflow checks |
| V3 Representative Integration | Do selected cross-boundary scenarios work? | smoke/E2E subset, representative cases |
| V4 Full Regression | Did previously valid behavior stay valid? | complete relevant suite |
| V5 Outcome | Does the real-world/user objective hold? | task completion, semantic/visual outcome, production-like run |

A repair window normally stops after sufficient V0–V2 evidence. The outer cycle owns V4–V5.

## Levels in SKILL.md terms

- **V0 Direct:** exact assertion for the changed behavior.
- **V1 Local:** affected unit, component, function, document section, query, or task.
- **V2 Neighbor:** directly dependent or coupled subsystem.
- **V3 Representative integration:** selected cross-boundary scenarios likely to expose regressions.
- **V4 Full regression:** complete relevant verification set.
- **V5 Outcome evaluation:** outside-in verification of the real user/system objective.

H1 repair windows normally operate at V0–V2 and may use V3 when inexpensive. H3 owns V4–V5.

Cache and reuse unchanged evidence where validity can be proven. Invalidate cached evidence when its assumptions or dependencies change.

For a live, nondeterministic system, V4 is a full cycle over the series' fixed comparison set and V5 is the live outcome; a keyless replay of a recorded failure is a V0 or V1 check that costs nothing ([live-evaluation.md](live-evaluation.md)).

## Inside-out and outside-in evaluation

Always distinguish these perspectives when both apply.

### Inside-out

Ask whether the system behaved according to its internal structures and contracts:

- invariants
- schemas/interfaces
- dependencies
- state transitions
- architectural boundaries
- policy/rules
- expected intermediate representations
- resource use

### Outside-in

Ask whether the actual consumer-visible outcome is correct:

- task completion
- observable behavior
- usability/clarity
- rendered or produced result
- real environment behavior
- semantic alignment with intent
- quality thresholds

A run is not fully resolved when only one perspective passes unless the specification explicitly scopes verification to one side.
