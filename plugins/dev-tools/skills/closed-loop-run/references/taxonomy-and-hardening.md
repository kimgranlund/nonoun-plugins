# Failure taxonomy, evaluator integrity, hardening and anti-patterns

These sections of the closed-loop-run skill are kept here to hold `SKILL.md` under the host's size limit. Text is unchanged; links are relative to `references/`.

## 7. Universal root-cause taxonomy

Start from these categories and extend them when the domain requires more precision: Intent, Context, Knowledge, Planning, Contract, Selection, Generation / Transformation, Implementation, Integration, Runtime / Environment, Interaction / Workflow, Evaluation, Observability, Process. Each is defined in [references/diagnosis.md](diagnosis.md).

Distinguish **discovery failure** from **knowledge failure**, **selection failure**, **contract failure**, and **implementation failure** whenever possible. They require different interventions.

**Evaluation** has two named failure modes worth checking on every unexpected pass or fail:

- **Check narrower than its rule:** the check tests one form of the rule (one output shape, one keyword, one representation) while the rule covers more, so a wrong result in another form passes.
- **Oracle too generic:** the expected outcome admits more than one right answer, or a scripted next step assumes a path the system may legally not take, so a correct result scores as a failure.

**Read the cause-class mix before repairing.** When an AI model or agent is the system under test, give every failure cluster one primary class: (a) exposure, the guidance never reached the model; (b) conflicting or ambiguous guidance; (c) the model ignored clear guidance; (d) a check, oracle, or scenario defect. Class (c) holds only when the guidance was framed in full and a stronger model passed on identical framing (when none is stronger, N samples or a second model family stand in). In a nine-cycle live study, most failures in most cycles were (b) or (d): the guidance or the checks, not the model. Fix (a) and (b) in what the model reads, (d) in the check or scenario, and record (c) as a model note. Field lessons: context-fog-of-war triage (`context:context-fog-of-war` `references/learnings/triage.md`).

## 14. Evaluator integrity

The local solver MUST NOT silently alter acceptance criteria, baselines, or evaluators to pass its own work.

Changes to tests/evaluators are allowed only when evidence shows the evaluator is incorrect or incomplete. Such changes must be reported explicitly and, where practical, independently verified against the original intent.

Prefer separation between **builder** and **verifier** assumptions. This may be implemented using separate agents, contexts, prompts, processes, or simply an explicit evaluation phase that rereads the specification instead of the implementation rationale. Use one independent verifier per change, after it is built, and treat its pass as final: no second verifier re-judges it, and new evidence opens a new episode.

Debate every change to something a model reads (prompts, guidance, skills, repair or error text, tool descriptions, exemplars) before applying it: a reviewer on a different model family challenges the change, the author answers, and unresolved points go to the owner. The debate comes before the change is applied, the verifier after; the debate reviewer is not the verifier. Reviewers from the builder's own family share its blind spots.

## 15. Learning and hardening

After episodes are integrated and H3 verification completes, ask:

> What allowed this causal class of failure to exist, and what is the cheapest durable change that makes recurrence impossible, less likely, or earlier to detect?

Candidate hardening layers, from local to systemic: (1) implementation fix, (2) regression test, (3) stronger invariant/assertion, (4) clearer contract/schema, (5) better metadata/discoverability, (6) improved context/knowledge, (7) improved planning rule or skill, (8) architecture/process change, (9) evaluator/observability improvement.

Do not automatically escalate every failure upward. Choose the lowest-cost layer that addresses the causal class without unnecessary complexity.

Rules for every hardening change:

- **One cause per change.** One ticket or episode per root cause, not per symptom, with a test that fails before the change and passes after it.
- **Every fix shifts a cost somewhere.** Name where it lands (spend, latency, another check, another model's behavior, a new failure shape, an ambiguity the change creates elsewhere) in the change itself, and measure it in the next cycle.
- **Rulings are data.** When the owner settles a contested behavior, record the ruling in a rulings register (one line each: date, behavior, reason, pin test, kept beside the cycle reports) and pin it with a test, so a later fix cannot reverse it silently.
- **Regenerate derived artifacts in the same change.** An index, generated asset, snapshot, baseline, or byte-pinned copy whose source changed is regenerated with its own script, and its freshness check runs before the change lands.

## 20. Anti-patterns

Never default to:

- rerunning the complete suite after every local change;
- "keep trying until it works";
- nested autonomous loops with no parent budget;
- changing multiple unrelated variables per experiment when diagnosis is uncertain;
- rewriting architecture to solve a local symptom;
- declaring success from internal tests alone when an outside-in outcome exists;
- declaring failure without recording what was learned;
- endlessly increasing context with raw logs from every attempt;
- allowing the fixer to redefine success after seeing results;
- starting another full cycle before producing the current cycle report;
- comparing cycles that ran different case sets, settings or sample counts;
- counting a provider error, a credential failure or a runner crash as a result.
