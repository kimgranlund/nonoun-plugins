# Best practices — decomposition

> The judgment layer: the non-obvious do/don't beyond the procedure. `method.md` owns the procedure;
> `references/<domain>.md` owns the axis vocabulary; this is what a competent decomposer still gets
> wrong. 2026-06-26.

## Do

- **Derive the two planes independently.** Run INSIDE-OUT *without* reading the node tree — the
  cross-check is worthless if one plane was copied from the other.
- **Make parts MECE** — mutually exclusive (no two nodes own the same responsibility) and collectively
  exhaustive (every part of the whole is covered).
- **Name a node by its responsibility**, not its position ("submit bar," not "bottom row"). The
  cross-check tests what a part *does*, not where it sits.
- **Justify or delete** every action-free leaf — give it a `justify` (`affordance` / `grouping`) or
  remove it. Decoration is gold-plating.
- **Write the manifest and run `scripts/coverage_check.py`** — the gate is deterministic.
- **Stop at one owner** — buildable/assignable without opening another branch.

## Don't

- **Read one plane off the other** — the cardinal sin: it runs one direction twice and passes the
  coverage script *trivially* (the host map is tautological) while finding nothing.
- **Over-decompose** (split past a single owner → coordination cost) or **under-decompose** (a "leaf"
  still hiding two responsibilities is not atomic).
- **Eyeball coverage** — trust `UNHOSTED` / `DANGLING` / `UNJUSTIFIED-LEAF` over your own reading.
- **Decompose into the solution** — name needs and parts, not the implementation you intend; that is the
  downstream author's job.
- **Skip the domain reference** — each domain's axis vocabulary + stop rule keep the planes concrete and
  comparable.

## When to add a domain

If none of the five domains' vocabulary fits, copy `_template.md`, fill both axes + the stop rule + a
worked pass, and add a row to the SKILL.md domain table — don't force a misfit domain onto the problem.

## The validation loop

draft both planes → write the manifest → `coverage_check.py` → fix every defect → re-run → finalize at
**exit 0**. The script is the gate; the prose is the method; `rubric.md` grades the result.

## When the decomposition feeds a parallel build

A cleared decomposition often fans out to concurrent workers. Three rules keep that fan-out honest —
they are the **slicing / verification side** and live here. The dispatch-and-gate EXECUTION model (who
runs which gate, when, and how worktrees fall back) is not carried in this pack — the retired sibling
that owned it is gone; define it in the orchestrator that runs the fan-out, and don't restate slicing
rules there.

### Slice by OWNING FILE — the disjointness test

- **One writer per file.** Cut leaf slices so each FILE (or tightly-coupled file group) has exactly one
  owning slice that applies *every* change that file needs. Slicing by improvement/feature races the
  moment two features touch one file; slicing by owning file makes the fan-out collision-free — and a
  file-disjoint tree then needs NO integration slice at all.
- **Defer every shared/barrel/config edit to ONE serial integration slice.** A barrel re-export, a
  `vitest` `include`, a shared interface, a config array — anything two slices would both write — is
  pulled out and done once, serially, never raced.
- **Run a serial PREP slice first.** Before a wide fan-out, pin the shared interfaces *and* the
  cross-cutting wording (canonical homes, rule phrasing) in one prep pass, so the parallel writers build
  against a fixed base instead of diverging. (The B0 / wave-1-prep pattern.)

### Every new gate or probe ships a negative control — anchor it on a UNIQUE token

- A gate that cannot fail proves nothing. Pair each new gate/probe with a **negative control**: a
  deliberate mutation that MUST make it go red.
- **Anchor the mutation on a UNIQUE code token.** A literal that also appears in a comment (or a
  docstring, or an unrelated string) leaves the *executable* line untouched — the probe stays green and
  you read a false "it didn't bite." Pick a token that occurs only in the line under test (prefer a
  fresh token like `busy`/`badge` over one like `ready` that the surrounding prose also uses).
- **Confirm the mutation actually applied** — `grep` for it in the edited source — before concluding
  anything from the result.
- **An unexpected NC result is "my probe is wrong" FIRST**, not "the gate is vacuous." Rule out a
  mis-anchored or un-applied mutation before you trust a green negative control.

### Every ADR Decision maps to an action before fan-out — and know what `coverage_check` does NOT check

- **Completeness review step.** Before dispatching, walk every ratified *or anticipated* ADR Decision
  and confirm each maps to a decomp action/node. A Decision nobody turned into an action never gets
  built.
- **Scope of `coverage_check.py`.** It verifies the two PLANES cross-check — every action has a node,
  every leaf has an action (node ↔ action). It does NOT verify real-world completeness: an ADR Decision
  that was never written as an action has nothing to leave `UNHOSTED`, so the manifest passes clean
  while the need ships nothing. This stays a JUDGEMENT review step, not a gate — matching prose
  Decisions to actions is semantic, not true/false, so it doesn't belong in the deterministic script.

---

Sources: [Functional decomposition (PSU ME491)](http://web.cecs.pdx.edu/~gerry/class/ME491/notes/functional_decomposition.html) ·
[Work Breakdown Structure principles (PMI)](https://www.pmi.org/learning/library/work-breakdown-structure-basic-principles-4883)
