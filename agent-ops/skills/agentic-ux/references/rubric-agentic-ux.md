---
date: 2026-05-28
status: draft
version: "0.1.0"
type: rubric
key_question: >
  Does this agentic UX carry the operator through the full workflow lifecycle
  with calibrated trust — explicit role, visible action, bounded risk, a
  closing verify loop, and corrections that compound — or does it optimise the
  generative happy path and leave the operator to babysit, guess, and re-teach?
lens: operator   # the human directing the agent, NOT the engineer building it
council: ux-quality
dimension_critics:
  D1: critic-amelia-w
  D2: critic-geoffrey-l
  D3: critic-sarah-g
  D4: critic-amelia-w
  D5: critic-karri-s
  D6: critic-sarah-g
  D7: critic-geoffrey-l
  D8: critic-karri-s
companion_documents:
  - rubric-agentic-architecture.md               # peer rubric (architecture & utility)
  - council/agentic-ux-council-eval-prompts.md   # the critic council orchestrator
  - workflow-lifecycles.md          # companion reference (taxonomy, to be built)
  - pev-superworkflows.md           # companion reference (loop shapes, to be built)
  - techniques-catalog.md           # companion reference (ralph, subagents, async, to be built)
---

# Agentic UX — Best Practices Rubric

**Agentic UX is not chatbot UX at larger scale.** It is the discipline of how a human _directs, oversees, contains, and improves_ a semi-autonomous agent across the whole lifecycle of working with it — not how the agent is engineered. The unit of evaluation is the **working relationship** (tool + workflow + practice), measured from the **operator's seat**, not the builder's. The same Plan→Execute→Verify vocabulary appears in the builder-side rubrics (agentic coding, prompt control modes); here PEV is scored as something the _operator_ lives inside, not something the _system_ implements.

The central outcome the rubric serves is **calibrated trust**. NN/g's _State of UX 2026_ names trust as the defining design problem for AI experiences, and the most common failure is miscalibration in either direction: the operator who rubber-stamps everything (blind trust, blast radius unbounded) and the operator who reads every diff line-by-line (no trust, no leverage). Calibrated trust is earned mechanically — through **visibility, reversibility, and a closing verify loop** — not asserted. Microsoft Design's formulation is the load-bearing one: **control = visibility + reversibility + choice.** A UX that gives the operator all three can safely grant the agent more autonomy; a UX missing any one of them forces the operator to either over-supervise or get surprised.

The second outcome is **sustainable cognitive load**. The 2026 shift is from _implementer_ to _orchestrator_ (Anthropic Trends Report): the operator's leverage now comes from directing an ensemble, not from typing. A UX where parallelism multiplies supervision cost linearly has not actually scaled the human — it has just moved the bottleneck.

**The operator's arc — and how the dimensions map to it:**

```text
SET UP ───────► WATCH ──────────► BOUND ────────► CLOSE ──────► COMPOUND
D1 autonomy      D3 observability   D5 reversibility D6 PEV loop   D7 feedback
D2 context       D4 steerability    & blast radius   closure       D8 lifecycle
```

**Companion docs:**

- `workflow-lifecycles.md` — the cold-start / orientation / generative / analysis / improving taxonomy (reference-shaped, not scored here)
- `pev-superworkflows.md` — Explore→Plan→Code→Commit, Spec-Driven Development, the agentic loop, and their fit conditions
- `techniques-catalog.md` — ralph loops, subagents, background/async agents, YOLO, self-improving loops, with fit/risk profiles
- The **builder-side** rubrics (agentic coding; prompt control modes) are the mirror — is the _system_ well-engineered, and how does a prompt author choose control modes?

> **Format-fitness note.** The 1–5 matrix fits **bounded evaluation of parallel dimensions** and strains on exploratory/taxonomic material. Agentic UX is a mix. The eight dimensions below are genuinely rubric-shaped — you can score a working relationship against them. The **lifecycle map**, the **P-E-V loop shapes**, and the **technique catalog** (ralph et al.) are taxonomy-shaped and live in the companion references; this rubric _points to_ them (Dimension 8, the anti-patterns, the corpus) rather than trying to score them as a gradient.

---

## §The Problem

An agentic UX evaluated only on its generative happy path will hide these operator-side failures:

1. **Autonomy mismatch.** The operator's role is never made explicit, so they oscillate between babysitting reversible edits and rubber-stamping irreversible ones. The autonomy ladder (operator → collaborator → consultant → approver → observer) is implicit and un-dial-able.

2. **Opaque execution.** The operator cannot see what the agent did, considered, or rejected until after the fact. Trust degenerates into blind faith or blanket suspicion because there is no middle signal to calibrate against.

3. **Irreversibility surprise.** The agent makes a change whose blast radius the operator did not anticipate and cannot cleanly undo. Recovery becomes manual archaeology.

4. **The loop that never closes.** The operator accepts "done" on the agent's word — green tests, clean compile — with no real verify target named against reality. Verify-theater, operator edition.

5. **Lifecycle tunnel vision.** The UX (and the operator's habits) support only greenfield generation. Cold-start, orientation in unfamiliar code, analysis, and improving the agent are neglected — so context rots, the agent re-discovers the same constraints, and the same mistakes recur.

6. **Evaporating corrections.** Every fix is verbal and per-session. Nothing graduates to durable memory, a skill, or a hook, so the operator re-teaches the agent the same lessons indefinitely.

7. **Technique misapplication.** A powerful pattern is run outside its fit: a ralph-style autonomous loop on a brownfield codebase, YOLO mode without a sandbox, a background agent on an unverifiable task. The technique was sound; the context wasn't.

---

## §First Principles

### 1. The operator's role is the primary design variable

Autonomy is not a single dial from "manual" to "auto." It is a **role assignment** that should be explicit and changeable mid-task. The academic ladder (operator → collaborator → consultant → approver → observer; arXiv 2506.12469) describes who holds the pen at each step. A good agentic UX makes the current role legible and lets the operator move up or down it as confidence and stakes change — approver for a migration, observer for a typo sweep.

### 2. Trust must be calibrated, not assumed — and calibrated by evidence

Trust is the central problem (NN/g 2026). It cannot be designed _in_ by reassurance; it is produced by **visibility + reversibility + choice** (Microsoft Design). The operator should be able to grant trust incrementally because the UX gives them the means to verify it was warranted and to recover when it wasn't. A UX that demands trust without supplying these is asking for faith.

### 3. Match the loop shape to the lifecycle

P-E-V (Plan → Execute → Validate) is the spine, but its instantiation differs by lifecycle. **Explore→Plan→Code→Commit** (Anthropic) fits feature work; **Spec→Plan→Tasks→Implement** (Spec-Driven Development; GitHub Spec-Kit, Kiro, BMAD) fits larger builds; the **think→code→execute→verify→repeat** agentic loop (Willison) fits tight iteration; an unbounded **ralph loop** (Huntley) fits greenfield bootstrapping and almost nothing else. Choosing the wrong loop for the lifecycle is a leading cause of agentic failure.

### 4. Autonomy is earned by reversibility and verifiability

The operator-side mirror of the builder's blast-radius principle: you can safely grant more autonomy exactly where actions are **reversible** and outcomes are **verifiable**. Greenfield + sandbox + strong tests → grant a long leash. Brownfield + production credentials + no verify target → keep the leash short. Huntley's own rule — _"no way in heck would I use Ralph in an existing code base"_ — is this principle stated as a boundary.

### 5. The human owns the verify target, even when the agent runs the check

Willison's three irreducible human pillars are **goal definition, tool preparation, and verification**. The agent can execute the check, but the operator must name what "done against reality" means _before_ execution — npm publish → curl the registry; UI change → render in a browser; API change → integration test against a running server. An operator who has not named the verify target will accept the first green signal as success.

### 6. Corrections must graduate to the right enforcement tier

The relationship compounds only if learning persists. The ladder: **auto-memory** (accrues from corrections) → **declared memory / CLAUDE.md** (durable soft guidance) → **skill** (reusable routine) → **hook / CI gate** (deterministic guarantee). The discipline is matching the tier to the need: prose for soft guidance, mechanism for anything that must not regress. Using a prompt instruction for something that needs a hook is the canonical training mistake.

### 7. Context is a curated instrument, not an accumulator

The agent arrives at zero mileage every session; CLAUDE.md/AGENTS.md is the onboarding guide it reads. But context that only grows becomes the **silent killer of reliability** — stale and bloated context drives a majority of agent failures. Good context is **editable, inspectable, and prunable**, and the UX should support compaction and structured note-taking, not just accumulation.

### 8. The operator scales by orchestration, not by typing

The leverage shift is implementer → orchestrator (Anthropic Trends Report). A mature agentic UX lets one human direct an ensemble — subagents fanning out into isolated context windows, background/async agents returning PRs — while staying **on-the-loop** (reviewing at the PR boundary) rather than **in-the-loop** (approving every step). If overseeing N agents costs N times overseeing one, the UX has not scaled the human.

---

## §The Rubric

### Dimension 1 [review] — Role & autonomy calibration

_primary: Amelia W. (`critic-amelia-w`)_

Is the operator's role explicit, matched to stakes, and changeable mid-task?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | The operator's current role (operator/collaborator/consultant/approver/observer) is legible at all times and dial-able mid-task. Autonomy is matched to reversibility and stakes by default — long leash on reversible/verifiable work, short leash on irreversible/production work. The operator can escalate or relax oversight without restarting. |
| **4 — Good** | Autonomy level is clear and roughly matched to stakes. Changing it mid-task is possible but clunky (e.g., requires a new session). |
| **3 — Adequate** | A single autonomy setting exists (e.g., "ask" vs "auto") but does not vary by action risk. The operator compensates with vigilance. |
| **2 — Poor** | Autonomy is implicit in how the operator phrases requests. Same posture for a typo and a schema migration. |
| **1 — Failing** | No role model. The agent acts at one fixed level regardless of stakes; the operator cannot raise or lower oversight. |

**Test:** mid-task, decide you want tighter oversight for the next risky step and looser oversight afterward. Can you change the agent's leash without losing its progress? If not, autonomy is a fixed dial, not a calibrated role.

---

### Dimension 2 [review] — Context & memory curation

_primary: Geoffrey L. (`critic-geoffrey-l`)_

Can the operator shape, inspect, edit, and prune what the agent knows — and does the UX resist staleness and bloat?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Context (CLAUDE.md/AGENTS.md, memory, rules) is inspectable and editable by the operator. Stale entries are easy to find and remove. The UX supports compaction and structured note-taking for long tasks. Memory is a curated instrument; the operator can answer "what does the agent currently believe about this project?" |
| **4 — Good** | Context is editable and mostly inspectable. Pruning is manual but possible. Bloat is managed by discipline rather than tooling. |
| **3 — Adequate** | Context can be edited but is hard to inspect as a whole; the operator is unsure what's loaded. Staleness creeps in unnoticed. |
| **2 — Poor** | Context is append-mostly. The operator dumps information in and rarely removes it. Bloat accumulates. |
| **1 — Failing** | The operator cannot see or edit what the agent knows. Memory is opaque or absent; every session re-explains the project. |

**Test:** open the agent's persistent context. Can you (a) read everything it currently "knows," (b) point to at least one stale or redundant entry, and (c) remove it in one step? Three yeses = a curated instrument. Any no = an accumulator.

---

### Dimension 3 [gate] — Observability & legibility

_primary: Sarah Gibbons (`critic-sarah-g`)_

Can the operator see what the agent is doing, considered, and changed — at the right altitude?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | The agent's actions are streamed and inspectable: a visible action/tool log, diffs for every file change, and reasoning surfaced at a glanceable altitude (decisions and tradeoffs, not raw token spew). The operator can tell on-track vs off-track in seconds and can drill into any step. |
| **4 — Good** | Actions and diffs are visible. Reasoning is available but either slightly too verbose or too sparse to scan comfortably. |
| **3 — Adequate** | Final changes are visible (a diff) but the path to them is not. The operator sees _what_ changed, not _why_ or _what was rejected_. |
| **2 — Poor** | Visibility is post-hoc and partial. The operator reconstructs what happened from the result. |
| **1 — Failing** | The agent is a black box. The operator sees only "done" and the end state. |

**Test (gate) — mechanical:** for the last task, count how many of these three are present and inspectable: (1) an action/tool log, (2) per-file diffs, (3) the agent's stated reasoning/plan. **PASS = 3/3**; otherwise the gate fails and the score is capped at the count. **Judgment overlay (not scored as the gate):** the altitude check — can the operator judge on-track vs off-track mid-run in under 30 seconds without drowning in output or being starved of signal? Record as a note that can lower a passing gate, never raise a failing one.

---

### Dimension 4 [review] — Steerability & interruption

_primary: Amelia W. (`critic-amelia-w`)_

Can the operator redirect, interrupt, take over, and hand back — without losing work?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | The operator can interrupt mid-execution, inject a correction or new direction, take over manually, and hand back — all while the agent's progress is preserved. A read-only exploration/plan mode is available before committing to edits. Course-correction is cheap and non-destructive. |
| **4 — Good** | Interruption and redirection work and preserve most state. Manual takeover is possible but the handoff back to the agent is awkward. |
| **3 — Adequate** | The operator can stop the agent, but redirecting means restarting the task with a revised prompt; in-flight progress is lost. |
| **2 — Poor** | Interruption is blunt (kill the run). No graceful redirect. The operator waits for completion to correct course. |
| **1 — Failing** | The operator cannot intervene once the agent starts. It runs to completion or failure regardless. |

**Test:** start the agent on a multi-step task, then interrupt at step 2 to change direction. Does it keep steps 0–1 and absorb the new direction, or do you lose progress and restart? Recoverable redirection = real steerability.

---

### Dimension 5 [gate] — Reversibility & blast-radius containment

_primary: Karri S. (`critic-karri-s`)_

When the agent is wrong, can the operator cleanly undo, and is the damage bounded by construction?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every agent action is reversible in one step (checkpoint/undo, or work isolated in a branch/worktree/sandbox surfaced as a reviewable PR). Blast radius is bounded structurally: no network, scoped credentials, budget/step limits for high-autonomy runs. Irreversible/external actions hit a confirmation gate. |
| **4 — Good** | Reversibility exists (e.g., git checkpointing) and most high-risk actions are gated. One or two paths to irreversible action lack a gate. |
| **3 — Adequate** | Recovery is possible but manual (read the diff, revert by hand). Containment depends on the operator remembering to check. |
| **2 — Poor** | Undo is partial or lossy. The agent can take actions with real-world side effects without a sandbox or confirmation. |
| **1 — Failing** | No undo, no isolation, no gates. An agent error can do unbounded, unrecoverable damage (deletes, pushes, production calls). |

**Test (gate) — mechanical:** two checks, both must pass. (1) **One-step reversal** — after an agent action, can it be reverted in a single step (checkpoint/undo, or work isolated in a branch/worktree/PR)? yes/no. (2) **Containment** — for the highest-autonomy mode, name ≥1 structural bound actually in place (sandbox / no-network / scoped creds / budget or step limit). **PASS = one-step reversal present AND ≥1 containment named**; otherwise the blast radius is unbounded and the gate fails. "The agent is instructed to be careful" names no bound and fails check (2).

---

### Dimension 6 `[gate]`/`[review]` — Loop closure: P-E-V from the operator's side

_primary: Sarah Gibbons (`critic-sarah-g`)_

Does the operator define the goal, prepare the tools, and name the verify target — so the Plan→Execute→Validate loop actually closes against reality?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Before execution, the operator (or the UX, prompting them) names the **verify target grounded in reality** for the task type, and the loop closes against it — not against the agent's self-report. Planning precedes execution for any non-trivial change (skipped only when the diff fits one sentence). The three pillars — goal, tools, verification — are visibly the operator's responsibility. |
| **4 — Good** | The loop closes with real verification most of the time. Occasionally the verify target is chosen after execution rather than before, or falls back to tests/lint as the final signal. |
| **3 — Adequate** | Planning and verification happen but verification is internal (tests/compile pass) rather than real-product. The operator treats green CI as done. |
| **2 — Poor** | The loop is Plan→Execute. Validation is the operator eyeballing the summary. No named verify target. |
| **1 — Failing** | No loop. The operator issues a request and accepts "done" with no plan and no verification. |

**Test (gate) — mechanical:** does the workflow specification name a verify target that references **real external state** — not "tests pass," not "the agent reviews its output," not "looks good"? Concrete acceptable targets: `curl registry.npmjs.org → 200`, `browser renders the component`, `integration test against running server passes`. **PASS = a real-state verify target is named**; "tests pass" or no verify target at all = FAIL. This gate caps the score at 3 regardless of other evidence.

**Test (judgment overlay — not the gate):** before your next agent run, state out loud what evidence will prove success _against reality_. Can you name it? If not, you will accept the first green signal as completion — and the loop has not closed. Record as a note that can lower a passing gate, never raise a failing one.

---

### Dimension 7 [review] — Feedback compounding (training & improving)

_primary: Geoffrey L. (`critic-geoffrey-l`)_

Do the operator's corrections persist and graduate to the right enforcement tier, so the same mistake doesn't recur?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Corrections graduate deliberately: auto-memory → declared memory (CLAUDE.md) → skill → hook/CI gate, with the tier matched to the need (prose for soft guidance, mechanism for must-not-regress). A correction given once does not need giving twice. The operator can point to recent corrections now enforced durably. |
| **4 — Good** | Corrections are captured durably (memory/rules updated) and mostly don't recur. Graduation to mechanisms (hooks) happens but inconsistently. |
| **3 — Adequate** | Some corrections persist; others are verbal and evaporate. Recurrence is reduced but not eliminated. No deliberate tier-matching. |
| **2 — Poor** | Corrections are almost all per-session. The operator re-teaches the same lessons regularly. |
| **1 — Failing** | Nothing persists. Every session starts from zero; the agent repeats known mistakes indefinitely. |

**Test:** pick a correction you gave the agent last week. Is it now enforced by memory, a skill, or a hook — or will you have to give it again? And: was the enforcement tier right (a hard rule mechanised, a soft preference left as prose)?

---

### Dimension 8 [review] — Lifecycle coverage

_primary: Karri S. (`critic-karri-s`)_

Does the agentic UX (and the operator's practice) support the full workflow lifecycle, or only the generative happy path?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | All five lifecycles have a deliberate workflow: **cold-start** (onboarding the tool/codebase via CLAUDE.md), **orientation** (read-only plan-mode exploration before edits), **generative** (greenfield build with the right loop), **analysis** (subagent fan-out into isolated context for search/summarisation), and **improving** (the feedback-graduation loop of D7). The operator picks the loop shape that fits the lifecycle. |
| **4 — Good** | Four of five lifecycles have a real workflow. One is ad hoc. |
| **3 — Adequate** | Generative plus one or two others are supported. Orientation or analysis is improvised each time. |
| **2 — Poor** | The operator treats almost everything as a generative build — including analysis and brownfield work where it misfits (e.g., vibe-coding past the point it degrades, ~500 lines of unstated requirements). |
| **1 — Failing** | One workflow for everything. Cold-start, orientation, analysis, and improving are absent or accidental. |

**Test:** list your last 10 agent sessions and tag each by lifecycle (cold-start / orientation / generative / analysis / improving). If you have a repeatable workflow for only one or two tags, the rest are running on luck.

---

## §Anti-patterns

### AP-01 — Rubber-stamp autonomy

**Symptom:** the operator approves every agent action without reading, or runs everything in auto mode regardless of stakes. Blind trust; blast radius unbounded. **Root cause:** approving is lower-friction than reviewing, and the UX offers no risk-tiered default. **Correction:** match autonomy to reversibility (Principle 4). Reserve high autonomy for reversible/verifiable work; gate irreversible/production actions. Make the approver role the default for high-stakes steps.

### AP-02 — Babysitting safe work

**Symptom:** the operator hand-approves every trivial, reversible edit. No leverage; the agent is glorified autocomplete. **Root cause:** under-trust with no mechanism to grant it safely — usually missing reversibility or observability, so the operator compensates with manual oversight. **Correction:** install the means to trust (visibility + reversibility), then relax oversight on the reversible 80%. Move up the autonomy ladder where recovery is cheap.

### AP-03 — Black-box acceptance

**Symptom:** the operator accepts "done" with no visible action log, no diff review, and no named verify target. Verify-theater, operator edition. **Root cause:** the result _looks_ finished and the agent _sounds_ confident. **Correction:** require the three observability artifacts (Dimension 3) and name the real-product verify target before execution (Principle 5).

### AP-04 — Ralph on brownfield

**Symptom:** an unbounded autonomous loop (`while :; do … done`) is pointed at an existing, high-stakes codebase and left to churn. **Root cause:** the technique's greenfield success is generalised past its fit. Ralph is "deterministically bad in a non-deterministic world" — safe only when guarded by signs, specs, and backpressure, on low-stakes greenfield. **Correction:** match the loop to the lifecycle (Principle 3). For brownfield, use bounded Explore→Plan→Code→Commit with tight scope and a human at the plan gate — not an open loop. (See `techniques-catalog.md`.)

### AP-05 — YOLO without a sandbox

**Symptom:** no-per-step-approval mode is enabled with live network access, real credentials, and no budget/test guardrails. **Root cause:** autonomy granted without the structural containment that makes it safe. **Correction:** YOLO requires a sandbox: no/limited network, scoped credentials, budget and step limits, and a strong test suite as backpressure (Willison). Autonomy and containment are granted together or not at all.

### AP-06 — Context hoarding

**Symptom:** everything gets dumped into CLAUDE.md/memory; nothing is ever removed. The agent's context grows monotonically. **Root cause:** adding context feels productive and removal feels risky, so bloat accumulates — the silent killer of reliability. **Correction:** treat context as a curated instrument (Principle 7). Inspect, prune, and compact. Periodically ask "what here is stale?" and delete it.

### AP-07 — Evaporating corrections

**Symptom:** the operator gives the same correction repeatedly across sessions; nothing graduates to a durable tier. **Root cause:** corrections are verbal and per-session; no feedback-graduation discipline. **Correction:** graduate corrections deliberately — memory → skill → hook (Principle 6). After the second time you say it, mechanise it.

### AP-08 — Greenfield-only habits

**Symptom:** every task is treated as a generative build, including analysis and brownfield work. Vibe-coding is pushed past where it degrades (~500 lines of unstated requirements). **Root cause:** one comfortable workflow applied to all five lifecycles. **Correction:** build a deliberate workflow per lifecycle (Dimension 8). Use read-only orientation for unfamiliar code, subagent fan-out for analysis, and spec-driven loops where requirements must be explicit.

---

## §Hard Tests

1. **The takeover test.** Interrupt the agent mid-task and take over. Do you keep its progress and hand back cleanly, or lose state and restart? (Steerability.)

2. **The undo test.** After an agent action you dislike, revert it. One step, or manual archaeology? (Reversibility.)

3. **The altitude test.** Glance at a run mid-flight. Can you judge on-track vs off-track in under 30 seconds — neither drowning in tokens nor starved of signal? (Observability altitude.)

4. **The operator's verify-target test.** Before a run, can _you_ state the evidence that will prove success against reality — not "tests pass"? If not, you'll accept "done" on faith. (Loop closure.)

5. **The lifecycle test.** Tag your last 10 sessions by lifecycle. A repeatable workflow for only one or two tags means the rest run on luck. (Lifecycle coverage.)

6. **The compounding test.** Take a correction from last week. Is it now enforced by memory/skill/hook, or will you repeat it? And is the tier right? (Feedback compounding.)

7. **The technique-fit test.** For the autonomous loop / background agent / YOLO run you used most recently, name the property that made it safe — reversible? verifiable? greenfield? sandboxed? If you can't, you got lucky. (Autonomy earned by reversibility.)

8. **The orchestration test.** Could you run three agent tasks in parallel and stay on-the-loop (review PRs, catch divergence) without thrashing? If supervision cost scales linearly with the number of agents, the UX hasn't scaled you. (Orchestration.)

---

## §Research Corpus and Theoretical Grounding

**Anthropic — Building Effective Agents (2024–2025).** The canonical workflow vocabulary: prompt chaining, routing, parallelization (sectioning/voting), orchestrator-workers, evaluator-optimizer — and the distinction between _workflows_ (predefined paths) and _agents_ (the model directs itself). Source of the "invest in the agent-computer interface (ACI)" argument that underlies the observability and steerability dimensions. (anthropic.com/engineering/building-effective-agents)

**Anthropic — Claude Code Best Practices.** Explore → Plan → Code → Commit; "skip planning only if the diff fits one sentence"; and the highest-leverage practice — _give the agent a way to verify its own work_. Grounds Dimension 6 and Principle 5. (code.claude.com/docs/en/best-practices)

**Anthropic — 2026 Agentic Coding Trends Report.** Documents the **delegation gap** (AI used in ~60% of work, only 0–20% fully delegatable) and the **implementer → orchestrator** shift. The empirical basis for the "operator scales by orchestration" principle and the cognitive-load framing. (resources.anthropic.com/2026-agentic-coding-trends-report)

**Anthropic — Effective Context Engineering for AI Agents.** Compaction, structured note-taking, and sub-agent context isolation as the disciplines that keep context a precision instrument. Grounds Dimension 2 and Principle 7. (anthropic.com/engineering/effective-context-engineering-for-ai-agents)

**Geoffrey Huntley — Ralph / "you are using Claude Code wrong" (2025).** The ralph loop (`while :; do cat PROMPT.md | claude-code; done`) with fresh context per iteration, one task per loop, guarded by _signs, specs, and backpressure_. "Deterministically bad in a non-deterministic world"; "no way in heck would I use Ralph in an existing code base." The proof point (CURSED, a language built over ~3 months) and the explicit fit/anti-fit boundary ground AP-04 and Principle 3. (ghuntley.com/ralph, ghuntley.com/loop)

**Simon Willison — Designing Agentic Loops (2025).** The think→code→execute→verify→repeat loop and the three irreducible human pillars: **goal definition, tool preparation, verification**. Also the canonical YOLO-mode safety analysis (containers without internet, scoped credentials, budget limits, test suites). Grounds Principle 5 and AP-05. (simonwillison.net/2025/Sep/30/designing-agentic-loops/)

**NN/g (Nielsen Norman Group) — State of UX 2026.** Names **trust** as the defining design problem for AI experiences, often shipped "before they are ready." The basis for trust-as-central-outcome rather than trust-as-dimension. (nngroup.com)

**Microsoft Design — AX / control principles.** **Control = visibility + reversibility + choice**; memory should be _editable_; AX optimises an ongoing relationship, not a single session. The load-bearing definition of control used throughout. (via pixelmojo.io/blogs/from-ux-to-ax-design-when-ai-becomes-coworker)

**arXiv 2506.12469 — user-role autonomy taxonomy.** The five-level ladder framed by the _user's_ role: operator → collaborator → consultant → approver → observer. Grounds Dimension 1 and Principle 1. (arxiv.org/pdf/2506.12469)

**Spec-Driven Development — GitHub Spec-Kit, AWS Kiro, BMAD-METHOD.** Specs as executable first-class artifacts; the Spec → Plan → Tasks → Implement loop (Spec-Kit works across 30+ agents); Kiro's spec → design → tasks → implementation. The brownfield-safe alternative to open loops, referenced in Principle 3 and AP-04. (github.com/github/spec-kit, martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)

**Andrej Karpathy — "agentic engineering."** Designing systems, constraints, and feedback loops so AI writes code reliably — the framing under which calibrated trust and verification are engineering problems, not hopes. (machinelearningmastery.com/7-agentic-ai-trends-to-watch-in-2026/)

**Self-improving loops — Reflexion (Princeton/MIT), SICA (ICLR 2025), MemSkill.** Verbal self-reflection in persistent memory (Reflexion), self-editing scaffolding (SICA), and evolving skill sets (MemSkill) — the research frontier behind the "improving" lifecycle and the feedback-graduation ladder. (openreview.net/pdf?id=rShJCyLsOr)
