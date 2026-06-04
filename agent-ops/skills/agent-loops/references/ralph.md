# Ralph / Brute-Force-Until-Done

**One-liner.** Run one prompt in a `while`-true loop where each iteration gets a **fresh context** and only durable on-disk artifacts (spec + plan/ledger + git + progress file) carry state forward — doing **one task per loop** until the work converges. It trades determinism-per-iteration for eventual consistency across many cheap, disposable attempts.

**Where it sits.** Ralph is a **single-agent iteration** topology — the minimal "agentic loop" primitive (model + tools + stop condition) specialized into a brute-force outer loop. In the router it is the second row, just above plan-execute: the cheapest _iterative_ mechanism, selected when the goal is greenfield + a checklist of independent verifiable items + a cheap automated gate + tolerant of brute force. It is the substrate other topologies wrap: an orchestrator-worker can run a Ralph loop per worker; a self-improving loop's inner build step is often a Ralph loop. See `composition.md` for the nesting rules and `control-plane.md` for the cross-cutting termination/context/verification machinery this family instantiates. Score a Ralph plan with `rubrics/rubric-ralph-loop.md` (dimensions R1–R8) plus the cross-cutting `rubrics/rubric-loop-control.md`.

---

## Mechanism — the control flow

The primitive underneath is the generic agentic loop: a model is given tools and a stop condition, and it **acts → observes → acts** until the stop fires. Ralph specializes this into a brute-force **outer** loop.

**Purest form (Huntley).**

```bash
while :; do cat PROMPT.md | <agent>; done
```

An infinite shell loop that re-feeds the same prompt file to a coding agent forever. The load-bearing inversion versus a normal agent session: **context does not accumulate.** Each iteration is a brand-new agent process with an empty context window. The only things that survive an iteration are durable on-disk artifacts — the spec(s) (`@specs/*`), the plan/ledger (`fix_plan.md` / `REFACTOR_PLAN.md` / `todo.md` / `prd.json`), committed code in git, and an append-only learnings/progress file. **Memory is externalized to the filesystem and git, not held in the context window.**

**Per-iteration control flow (the disciplined version — e.g. `snarktank/ralph`).** Each fresh iteration runs this sequence:

1. **Load.** Fresh agent reads spec + plan/ledger + `AGENTS.md` into a clean context. Nothing from the prior iteration's reasoning is replayed.
2. **Select one item.** The agent itself picks the single highest-priority not-yet-passing item. Huntley insists on trusting it to choose: _"Only one thing… you also need to trust Ralph to decide what's the most important thing."_
3. **Search before writing.** Fan out read-only subagents over the codebase to avoid re-implementing existing code — _don't assume not-implemented_. (Guards the duplication failure mode below.)
4. **Implement that one item.** A single, small, reviewable change.
5. **Run the gate.** Typecheck + tests (often extended to build + lint + security scan).
6. **Commit only if green.** The commit is gated on the verification check passing.
7. **Update durable state.** Mark the item done in the plan/ledger; append what was learned to `progress.txt`.
8. **Signal / exit.** Emit a completion signal or exit; the outer loop respawns a fresh instance, returning to step 1.

**Subagent pattern (Huntley).** Fan out up to ~hundreds of **read-only** subagents for codebase search, but **serialize build/tests through one agent** to avoid back-pressure / contention failures. The fan-out accelerates grounding; the serial bottleneck protects correctness.

**Carrier variants.** The loop body is the same; the carrier (how the loop reissues the prompt) determines whether context actually resets — the single most important mechanism property.

| Carrier | Where the loop lives | Context behavior | Notes |
| --- | --- | --- | --- |
| **External `while :;` bash loop** (Huntley purist) | Outside the agent, in the shell | **Fresh per iteration** — new process, empty window each time | The canonical anti-context-rot form; `git reset --hard` is a clean undo |
| **Stop-hook session-internal** (Anthropic `ralph-wiggum` plugin) | Inside one session — a `Stop` hook intercepts the exit attempt and re-injects the same prompt | **Does NOT reset** — state persists via modified files + git history within the session | Simpler to run; trades the anti-rot benefit for single-session convenience. A meaningful divergence from the purist form |
| **Cron / overnight batch** | Scheduler reissues the prompt on a timer | Fresh per scheduled run | "One small refactor every morning"; wall-clock is free |

**PROMPT.md is a living document, not a perfect prompt.** Huntley: _"There is no such thing as a perfect prompt."_ You accrete behavioral fixes into it as you watch the loop. The operator's job is to **"sit ON the loop, not IN it"** — engineer the harness, specs, and gates that let the loop succeed, then watch it, intervening with `git reset --hard` when it goes off the rails.

---

## When it fits / when it fails

### When it fits

- **Greenfield / from-scratch** builds with no legacy code to respect. Huntley is explicit: _"There's no way in heck would I use Ralph in an existing code base."_
- The end-state is specifiable as a **checklist of independent, verifiable items** (PRD stories, a refactor against a written standard, a spec with acceptance tests).
- There is a **cheap, automated, trustworthy verification gate** (typecheck, unit tests, build, lint, security scan) — objective back-pressure, not the model's self-assessment.
- Work decomposes into **small chunks each fitting comfortably in one fresh context window** (well under ~100–150k tokens).
- **Overnight / unattended batch** where wall-clock is free and you'd rather throw tokens at the problem than orchestrate carefully — _"just keep throwing tokens at the loop."_
- **Cost-asymmetric** situations: re-running the loop from the same prompt is cheaper than resolving a merge/rebase conflict or hand-debugging — _"Code is cheap — re-run the ralph loop."_
- A **senior engineer is available** to author the spec, build the gates, and supervise. Huntley: _"There is no way this is possible without senior expertise guiding Ralph."_

### When it fails

- **Legacy / brownfield** codebases — the loop has no way to respect existing invariants and will trample them. (Route to a brownfield per-file loop with an inner evaluator-optimizer instead; see `examples/example-a-react-to-hooks.md`.)
- **Vague or absent specs** — _"if the specs are bad, the results will be meh."_ Garbage spec in, AI slop out. The failure is **upstream** of the loop.
- **No automated verification gate** — without objective back-pressure the model chases the reward signal (green build) and ships placeholder/stub implementations that "pass" but don't do the work.
- Tasks needing **human judgment, design decisions, or one-shot/irreversible operations** (production debugging, schema migrations) — the loop's "just try again" premise breaks.
- **Running indefinitely without checkpoints** — _overbaking_: the loop eventually goes off-track (_"It's Ralph Wiggum, after all"_) and invents bizarre out-of-scope work (Huntley's example: unprompted post-quantum cryptography support).
- **Unbounded subagent fan-out** — recursive spawning can explode token spend ~10× within minutes without a spawn-budget cap.
- **Non-deterministic multi-agent orchestration on top of Ralph** — Huntley warns it becomes _"what microservices would look like if the microservices themselves are non-deterministic — a red hot mess."_
- **Letting context accumulate** (the failure the technique exists to prevent) — _"The more you use the context window, the worse the outcomes."_ Quality degrades past ~147k tokens even on a 200k window.

---

## Key parameters — the knobs a builder sets

The highest-value section. Each knob gets a sensible default; deviations need a stated reason. Defaults assume the disciplined greenfield case; the autonomy/permissions row tightens for unattended runs.

| Parameter | What it controls | Default | Rationale |
| --- | --- | --- | --- |
| **Loop carrier / harness** | External `while :;` bash loop vs Stop-hook session-internal vs cron batch | **External `while :;` bash loop** (fresh context per iteration) | The purist form is the only one that actually resets context, which is the whole point. Use Stop-hook only when single-session convenience outweighs anti-rot; use cron only for trickle/overnight cadence. |
| **Spec / source-of-truth artifact(s)** | The durable contract surviving every reset: `PROMPT.md` + `@specs/*` | **Declarative end-state spec** ("match this standard / these acceptance tests"), not a one-shot imperative | This is where ~all human leverage lives; the loop is only as good as this artifact. Declarative survives reset and resists drift; imperative does not. |
| **Plan / progress file + completion ledger** | Externalizes "what's left" and "what's done" for a memoryless instance: `fix_plan.md` / `todo.md` / `prd.json` with `passes: true\|false` | **A per-item ledger with an explicit pass flag** + an append-only `progress.txt` | The emptiness / all-pass state of this file is typically the real stop condition. A fresh instance reconstructs state from it alone. |
| **Verification gate definition** | The typecheck / test / build / lint / security command that gates a commit | **Typecheck + unit tests, commit-only-if-green** (extend to build + lint + security as the project warrants) | The back-pressure that turns brute force into convergence rather than slop. Without it the loop optimizes the proxy (green build) over the goal. |
| **One-task-per-loop scope discipline** | Constrains each iteration to a single item; trusts the agent to pick it | **Exactly one item per iteration**, agent-selected | Keeps each change inside a fresh window, small, reviewable, and revertible — prevents context overflow and merge-conflict debt. |
| **Stop / iteration bounds** | `--max-iterations N` + optional exact completion sentinel + "plan file empty" | **`--max-iterations N` as the PRIMARY backstop** + ledger-empty as the semantic stop | Semantic completion signals are unreliable on impossible tasks; the hard cap is the real safety net against infinite spend and overbaking. |
| **Subagent fan-out + spawn budget** | Read-only search subagents (wide) + a recursion/spawn cap; build/test serialized | **Wide read-only fan-out for search; a hard spawn-budget cap; build/test through ONE agent** | Search fan-out accelerates grounding, but unbounded recursive spawning burns tokens ~10×; serializing build/test avoids contention failures. |
| **Permissions / file allowlist + autonomy flag** | `--yolo` / `--dangerously-skip-permissions` for unattended; a write allowlist; git-per-iteration | **Confine writes to an allowlist** (e.g. `src/**`, `@specs/**`) + commit per iteration; enable the autonomy flag **only** once the allowlist + gate are trusted | The allowlist + git-per-iteration bound the blast radius of a bad loop and make `git reset --hard` a clean undo. Autonomy without containment is how a bad loop corrupts the repo. |

---

## Termination / context strategy / verification gate (this family)

These instantiate the cross-cutting substrate in `control-plane.md`; the points below are how Ralph **specifically** sets them, not a re-derivation.

**Termination (layered — see control-plane §termination).** Stack, do not rely on any single layer:

- **Goal-gate:** plan/PRD ledger fully satisfied — every item `passes: true` / `todo.md` has no open tasks. This is the canonical "done" signal in disciplined implementations.
- **Completion sentinel (self-reported, weak):** the agent emits an exact string the harness matches (e.g. `<promise>COMPLETE</promise>`). Exact-match only — it **cannot distinguish DONE from BLOCKED**, so a stuck loop looks like a running one. Never the sole stop.
- **Hard cap (PRIMARY):** `--max-iterations N`. Recommended as the real safety backstop precisely because semantic signals are unreliable on impossible tasks.
- **Operator intervention:** Ctrl+C / `/cancel-ralph`, or judging it off-track and issuing `git reset --hard` to restart from a known-good commit.
- **(Implicit, dangerous):** no condition at all — pure `while :;` runs forever. This is what produces overbaking and is exactly why practitioners add explicit bounds.

**Context strategy (fresh end of the fresh↔accumulating axis — see control-plane §context).** Fresh-context-per-iteration is **the defining strategy** of the purist form: every loop spawns a new process with an empty window; nothing from the prior iteration's reasoning is replayed. Continuity comes entirely from **external durable state** — specs, the plan/todo/PRD ledger, committed code in git, an append-only progress/learnings file, and `AGENTS.md` for discoveries to share forward. Rationale: the context window is the LLM's "RAM" and quality measurably degrades past ~100–150k tokens (context rot), so each iteration deliberately re-loads **only** spec + current task into a clean window and discards everything else. _Divergence:_ the Stop-hook plugin variant does **not** reset — state persists in-session via modified files + git history — trading the anti-rot benefit for single-session simplicity. Some practitioners force rotation to fresh context at ~60–80% window capacity rather than strictly per-task.

**Verification gate (see control-plane §verification — executable-oracle tier).** An **automated, on-disk** gate run inside each iteration **before commit** — typically typecheck + unit tests, often extended to build, lint, security scan, and standards-conformance. Huntley frames it as mandatory (_"unit test after each change"_); practitioners call it _"back-pressure engineering."_ When a check fails, the failure is fed back to the agent (same or next iteration) which fixes it — **no human hand-fixing in the loop.** Commit-only-if-green means git history is a chain of verified states, so `git reset --hard` always lands on something that passed. **Critical caveat:** the gate must test **real behavior** — models chase the proxy reward (green build) and will emit placeholder/stub code that passes a weak gate. Gate rigor is the single biggest determinant of convergence-to-working-code vs convergence-to-slop. The completion sentinel is self-reported and explicitly **not** trustworthy on its own; `--max-iterations` is the real safety backstop. _(Confidence: gate-rigor → convergence is empirically-supported across the practitioner cases; the exact token thresholds for context rot are practitioner-folklore approximations.)_

---

## Failure modes — each with its guard

| Failure mode | What happens | Guard |
| --- | --- | --- |
| **AI slop / placeholder implementations** | Model satisfies the proxy (compiles, build green) with stubs rather than real functionality — the **dominant** failure when the gate is weak or absent | Make the gate test **real behavior** (assert outputs/side-effects, not just compilation); raise the verifier to ≥ the generator; add acceptance/behavioral tests to the ledger |
| **Overbaking** | Left unbounded, the loop diverges and invents out-of-scope work (Huntley: unprompted post-quantum crypto) — _"eventually it goes completely off track"_ | `--max-iterations N` as the primary cap; scope discipline (one ledger item per loop); operator watching with `git reset --hard` on drift |
| **False-negative search → duplication** | Codebase search misses an existing implementation; the agent concludes "not implemented" and rebuilds it, corrupting the codebase | Mandate the search-before-write step (3) with read-only subagents; _"don't assume not-implemented"_; prefer broad search over narrow ripgrep |
| **Context rot** (non-fresh variants) | Accumulating error logs and history past ~147k tokens degrade reasoning — the exact failure fresh-context exists to prevent | Use the **external `while :;`** carrier (true reset); or force rotation at ~60–80% window capacity |
| **Subagent spawn explosion** | Recursive spawning without a budget cap burns tokens ~10× in minutes | Hard spawn-budget / recursion-depth cap; serialize build/test through one agent |
| **Spec-quality collapse** | Vague/incomplete spec yields "meh" output deterministically — failure is upstream, in the human's spec | Invest in a declarative end-state spec with acceptance criteria **before** running; this is the #1 leverage point (rubric R1) |
| **Cost runaway** | Unbounded `while :;` with no `--max-iterations` keeps spending on impossible or already-done tasks | `--max-iterations` + a token/cost ceiling circuit-breaker; ledger-empty semantic stop |
| **Eventual unrecoverable breakage** | The agent corrupts the codebase badly enough that only operator intervention recovers — the loop cannot always self-heal | Commit-per-iteration + write allowlist so every state is revertible; `git reset --hard` to last green; operator on the loop |
| **Completion-signal ambiguity** | Exact-string sentinel can't distinguish DONE from BLOCKED, so a stuck loop looks like a running one until max-iterations | Never trust the sentinel alone — pair with the ledger goal-gate and the `--max-iterations` backstop; add a no-progress detector (K flat rounds) per control-plane |
| **Fragile harness state** | Deleting plugin/state files mid-run, or a missing autonomy flag, breaks the loop with cryptic errors (observed in early Anthropic plugin) | Treat harness/state files as immutable mid-run; verify the autonomy/permissions flag before launching unattended |

---

## Composition — how Ralph nests and wraps other layers

Ralph is the **minimal iterative substrate**, so it most often appears _as the inner body_ of a larger topology, or _with a sub-step wrapped around its gate_. See `composition.md` for the full layer-nesting rules.

- **As a worker body inside orchestrator-workers.** An orchestrator decomposes a build into independent ledger items and runs one Ralph loop per worker. The orchestrator owns dispatch + the global ledger; each worker owns its fresh-context loop. (The independence requirement is strict — workers must not write shared state, or the conflicting-implicit-decisions failure appears.)
- **As the inner build step of a self-improving loop.** The outer loop curates a skill/learnings library across runs; the inner per-run build is a Ralph loop whose `progress.txt` / `AGENTS.md` feeds the outer curation. Keep the held-out utility measurement (the self-improving gate) separate from Ralph's per-iteration commit gate.
- **Wrapping an evaluator-optimizer around the per-item step.** When a single ledger item itself needs iterative refinement against a judge (e.g. a brownfield-adjacent file that must match a standard), the item's implement-step becomes a generate-critique-revise cycle, while Ralph remains the outer item-by-item driver. This is the brownfield-leaning composition in `examples/example-a-react-to-hooks.md`.
- **Cron-scheduled Ralph as an async/background loop.** A trickle carrier ("one small refactor every morning") makes Ralph a scheduled async agent; hand the _operator-oversight UX_ of that unattended run to the sibling `agentic-ux` skill — this skill designs the mechanism, not the human's trust/steer/interrupt experience.
- **Do not stack non-deterministic multi-agent orchestration on top of Ralph.** Huntley's explicit warning (_"a red hot mess"_); if you need parallelism, fan out **read-only** search, keep build/test single-threaded, and keep the ledger the single source of truth.

---

## Primary sources

- **Ralph Wiggum as a "software engineer"** — Geoffrey Huntley. <https://ghuntley.com/ralph/> — the primary, original source by the creator: the `while :; do cat PROMPT.md | <agent>; done` loop, one-thing-per-loop, subagent fan-out, "no perfect prompt," "sit on the loop not in it," greenfield-only, and explicit failure modes (overbaking, ripgrep false negatives, placeholder code).
- **everything is a ralph loop** — Geoffrey Huntley. <https://ghuntley.com/loop/> — the loop as universal primitive (model + tools + stop condition), "one task per loop," the monolithic single-process stance, and the warning against non-deterministic multi-agent orchestration.
- **Anthropic `ralph-wiggum` plugin README** (claude-code). <https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md> — the official productized variant: the Stop-hook session-internal loop (vs external bash), `--max-iterations`, `--completion-promise` exact-string matching, `/cancel-ralph`, the explicit guidance that `--max-iterations` is the PRIMARY safety mechanism, and the not-good-for list.
- **snarktank/ralph** — autonomous PRD-driven loop. <https://github.com/snarktank/ralph> — the best mechanism template for a builder: fresh instance per iteration; memory via git + `progress.txt` + `prd.json` (`passes: true|false`); pick highest-priority failing story → implement → typecheck/test → commit-if-green → mark passed → append learnings → repeat until all pass or max-iterations; emits `<promise>COMPLETE</promise>`.
- **A Brief History of Ralph** — HumanLayer Blog. <https://www.humanlayer.dev/blog/brief-history-of-ralph> — traces the practitioner-added guardrails: declarative specs over imperative prompts, research/plan/implement decomposition across context windows, overnight cron batching, the overbaking phenomenon, and the conditional-convergence model. Separates empirical cases from folklore.
- **The Ralph Wiggum Loop: autonomous code generation with a fresh context** — codecentric. <https://www.codecentric.de/en/knowledge-hub/blog/the-ralph-wiggum-loop-autonomous-code-generation-with-a-fresh-context> — the clearest articulation of the fresh-context mechanism and durable-state substitution (context = LLM "RAM"; only spec+task enter each window), the attended→unattended graduation path, "back-pressure engineering" as the gate, and a quantified case (~16 phases, ~4h, ~€70).

---

_Scoring: this topology is scored by `rubrics/rubric-ralph-loop.md` (R1 spec-quality · R2 gate-rigor · R3 context-reset · R4 stop-safety · R5 scope-per-iteration · R6 durable-memory · R7 blast-radius · R8 economics) in union with the cross-cutting `rubrics/rubric-loop-control.md`._
