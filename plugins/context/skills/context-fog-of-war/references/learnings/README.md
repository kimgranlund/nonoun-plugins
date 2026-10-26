# Learnings

## Scope

Sources: a runtime-harness study and a separate cross-host CLI routing study. Every lesson declares its applicability; observations are not universal requirements.

These are field lessons from a runtime harness: a product-side JS runtime that serves end users. Its producer loop composes persona text, a shared grammar, a retrieved component catalog with skills and exemplars, and tool calls. It validates model output against a UI schema and semantic checks and runs bounded repair rounds before it renders generative UI live.

A CLI harness (a Claude Code or Codex session, which this skill also analyzes) is a different kind. One agent works over a repo with file reads, shell tools and skills, with a human in the loop.

| Runtime study characteristics | CLI study characteristics |
|---|---|
| end users who see every turn | file and shell tools |
| a fixed turn budget | multi-step exploration |
| output validated against a schema | a human reviewer |
| automated repair rounds | long sessions with compaction |
| per-agent persona text over a shared grammar | |
| a live model choice per agent | |
| spend caps on live rounds | |

A lesson tagged "both" relies on nothing in either column (rule out lost context first; an index entry reaches the model as one line). A lesson tagged "runtime harness" depends on something in the left column (repair text is a prompt; show users codes, not internals). Do not apply it to a CLI session without its check. CLI-harness learnings go in their own file here, tagged "Applies to: CLI harness" and listed below.

Lessons for turning a fog analysis into fixes. They were observed in a five-round study of one runtime harness (persona text over a shared grammar, a catalog of primitives and composites, semantic checks feeding a repair round, live rounds on three model sizes). Treat each as a hypothesis for a new project: run its check before relying on it.

Read only the step relevant to the investigation. For the runtime study, the order below describes its triage sequence; CLI routing uses its separate entry.

- [instrument.md](instrument.md): what each trace line must record before any diagnosis (lessons 1 to 5). Applies to: both, except lesson 3.
- [triage.md](triage.md): rule out lost context, then give each failing cluster one cause class (6 to 11). Applies to: both.
- [guidance-authoring.md](guidance-authoring.md): literal small models, one home per rule, per-agent fixes first (12 to 16). Applies to: mixed; 14 and 15 are runtime harness only.
- [validation-and-repair.md](validation-and-repair.md): semantic checks, repair text as a prompt, judging the final turn (17 to 22). Applies to: runtime harness.
- [test-loop.md](test-loop.md): capped live rounds, keyless replays, specific oracles, one cause per ticket (23 to 27). Applies to: mixed; 25 and 27 are both.
- [model-choice.md](model-choice.md): the cheapest passing model per agent (28 to 29). Applies to: runtime harness.
- [contract-audit.md](contract-audit.md): audit guidance and contract surfaces before a live round, and tie each trace finding to its contract (30 to 31). Applies to: both.
- [cli-routing.md](cli-routing.md): task intent, complete delivery, justified reuse, host portability and independent outcome checks (32 to 38). Applies to: CLI harness.
- [applying-this-skill.md](applying-this-skill.md): which fog-of-war output settles each step, and the why-and-fix table a run ends with. Applies to: both.

Cause classes used throughout: (a) exposure, (b) conflicting or ambiguous guidance, (c) model ignored clear guidance, (d) check, oracle or scenario defect.

## Lesson format

Each file opens with an "Applies to:" line. Every lesson is a numbered rule followed by exactly three lines:

```markdown
N. The rule, one sentence, imperative.
   - Observed in <the study>: what was seen, with a count where one exists.
   - Check: how a new project confirms the rule holds there.
   - Applies to: runtime harness | CLI harness | both.
```

A lesson states what was observed, never a universal law. Numbers run across files and are never reused; a new lesson takes the next free number.
