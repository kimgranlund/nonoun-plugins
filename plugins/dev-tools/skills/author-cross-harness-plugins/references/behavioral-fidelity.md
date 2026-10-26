# Behavioral fidelity — what live cross-harness evals actually taught

Every rule here was earned from a live failure in the adia-sdlc eval loop (7 Codex rounds + 1
Claude round, 2026-08-31, converged at round 7, `plugins/adia-sdlc/docs/cross-harness-evals.md`'s Findings log — cited
per rule). Structural validation caught none of them. Apply these at AUTHORING time; the eval
loop exists to catch what slips through, not to substitute for them.

## 1. Invocation policy is a declaration, not an enforcement

`policy.allow_implicit_invocation: false` (Codex) and `disable-model-invocation: true` (Claude)
are NOT reliably enforced as hard routing boundaries by every host runtime. Observed live:
Codex self-invoked `claim` through a lease-write attempt (round 2) and ran `sweep-backlog`'s
discovery scan + `dispatch-build`'s ticket reads (round 3) — all policy-declared human-only.

**Rule: every human-only command ships a body-level backstop as its first paragraph** — "this
procedure begins only when a human explicitly invokes it; a general intent to X is answered by
naming the command; no step below, including read-only ones, runs from an implicit prompt; the
frontmatter/policy declaration is not guaranteed to be enforced — do not rely on it alone."
Explicitly cover read-only first steps: the live failures all began with "harmless" reads.
Proven across claim, make-release, sweep-backlog, dispatch-build (rounds 2-4: every member with
the backstop passed its next round).

## 2. Only the description's first sentence is guaranteed visible at routing time

Codex's discovery menu surfaces `short_description` = the description's FIRST sentence. A NOT
clause later in the description is invisible when the router picks. Observed live: `research`'s
declarative-statement exclusion (added mid-description, round 3) failed in round 4; moving it
into the first sentence fixed routing pressure, and a body-level gate check ("if the triggering
message states a claim rather than requesting X, say so in one line and stop — loading this
skill is not a commitment to run it") converts any residual mis-route into a one-line stop.

**Rule: an exclusion that must gate ROUTING lives in sentence one; everything late in the
description is Claude-menu-only. Pair it with a body gate check as the second layer.**

## 3. Near-miss lookalikes must be excluded by name

Generic questions and declarative statements that share vocabulary with a skill WILL route to it
unless the description names them out. Observed live: "how do I structure a good git branch
name" routed to check-branch (round 2); "research says X" routed to research (rounds 3-4).

**Rule: for every skill, ask "what is the nearest message that should NOT route here?" and write
that exclusion into the description** ("Use when checking a CONCRETE branch name…; NOT generic
branch-naming advice"; "only on an explicit REQUEST to investigate — a statement that merely
mentions research requests nothing"). Ship a no-trigger eval case for each named near miss.

## 4. Prohibitions lose to generative bias — write construction rules

"Never guess a missing field" failed in two consecutive rounds (file-defect invented Repro,
Classification, Severity from a bare failure condition). What worked: flipping the prohibition
into a mechanical construction rule — "pass `--field` ONLY for content quotable from the
reporter's own words; OMIT everything else so the render tool's own gap placeholder fills it",
plus gating derived side effects (a label) on a valid enum value ("a gap-valued Severity gets NO
severity label"). Round 4 also showed a second-order failure: the gap PLACEHOLDER text leaked
into a label (`severity:(gap: …)`) because the label step was unconditional.

**Rule: where the model must not invent content, don't forbid inventing — specify the only legal
construction, make omission the default path, and gate every downstream use of a possibly-gap
value on a validity check.** And make the quotability test per-FIELD, not per-report (round 5):
words that exist in the source but answer a DIFFERENT field's question are not quotable for this
one — state each field's own question ("Repro takes only a stated reproduction ACTION; a failure
condition answers Expected-vs-actual and leaves Repro as a gap"). A construction rule without
field semantics still leaks content sideways.

## 5. Verifier skills: the verdict comes from running the tool, and the tool's path is spelled out

Two distinct live failures: implicit routing to check-branch answered from grammar reasoning
without running the checker (round 2 Codex; also the gap Claude Code was warned against), and a
completion-condition session concluded the checker "was missing" because a depth-limited find
missed `skills/<name>/scripts/` (round 3).

**Rule: a verifier's body states (a) "the verdict always comes from running the script and
reading its exit code — never reason about conformance by inspection", and (b) the script's
exact installed path relative to the plugin root, with a "if a relative invocation misses,
resolve the plugin root first rather than concluding the script is absent" line.**

## 6. Guarded commands leak through their siblings

An implicit "ship a release" request routed through broadly-invocable siblings (release-rules,
check-release) and executed real preflight — RDD/evidence inspection, an attempted gate run —
before the guarded command's own body (and its backstop) ever loaded (round 2).

**Rule: when a command is human-only, its SIBLINGS' descriptions each carry a NOT-the-door
fence**: "NOT the door for a '<intent phrase>' request — that intent is answered by naming
/<command> for the human, never by starting <sibling's own act> here."

## 7. Dispatch is not completion

A parent that dispatches a sub-agent must await the child and relay its verdict verbatim;
"Dispatched X" as a final answer is a live-observed failure (round 1) and nondeterministic even
when usually correct. **Rule: the agent body carries a note addressed to its dispatcher** —
"await the return and relay the verdict before ending your turn; reporting only that dispatch
occurred is not completion."

## 8. New members inherit none of this automatically

Round 3's four new-surface defects were ALL recurrences of classes already fixed on older
members — Wave-6 commands shipped without the backstop and near-miss fences their siblings had
already earned. **Rule: patterns 1-7 are authoring conventions for every NEW member, applied at
write time — a new command-shaped skill that ships without its backstop + named near-miss
exclusion + eval cases is incomplete, not merely untested.**

## 9. Eval-loop methodology (what made the loop converge)

- **Exclude the answer key**: if the eval doc ships inside the plugin, a tested session can read
  its own expected column from the installed cache (observed live). Delete it from the tested
  working copy AND cache; confirm absence post-run.
- **One fresh top-level host process per row**. For Codex, a suitable CLI trial uses
  `codex exec --ephemeral --model <chosen-model> -c
  'model_reasoning_effort="<chosen-effort>"'` with an isolated `CODEX_HOME`; add
  `--skip-git-repo-check` only when its trust-check bypass is appropriate for the
  disposable fixture. Select an available model and effort deliberately. Use the
  corresponding ordinary top-level Claude process for Claude. A child-agent task
  does not substitute for a top-level routing/loading trial. Use disposable fixtures
  for anything mutating.
- **Freeze identity before launch**: hash the exact candidate, adapters, readable resources
  and effective configuration for every row. Recheck after the run. Rows that mix a live
  main-checkout adapter with worktree canonical files do not establish the tested revision.
- **Retain raw host events and verbatim output**. Self-reported tool calls and fluent answers
  do not prove advertisement, selection or loading. Record requested and observed model
  identity separately when the host exposes both.
- **Grade stages independently**: packaged, installed/enabled, advertised, selected,
  body/resources loaded, executed, observable completion and cleanup. Use `unverified`
  instead of promoting output quality or artifact presence into an earlier-stage pass.
- **Every fix lands with a regression eval case** (the `n99` convention) in the skill's own
  suite, both the shared and adapter copies.
- **Confirmation rounds re-run only the failed rows**; full re-runs only after structural change.
- **Separate environment limits from plugin defects** and stop re-fixing them: Codex's sandbox
  keeps `.git/refs` read-only even under approval flags — an expected-fail row, not a defect.
- **Convergence pattern observed**: prose fix → partial; front-loaded/mechanical fix → held.
  Budget two rounds per defect class: one advisory attempt is acceptable, the second fix must be
  structural (position, construction rule, or gate).
- **Audit the eval's own expectations before fixing the skill** (round 6): a mismatch row where
  the skill followed its stated contract and the EXPECTATION contradicts it is an eval-spec bug —
  correct the row, don't "fix" correct behavior (live case: an eval demanded Classification stay
  a gap when the reporter had literally named the failing file, which the skill's contract
  rightly treats as quotable). Judge each late-round finding against the contract first.
- **Logical inversion is construction, not quoting** (round 6): "X crashes" does not license
  "expected: X should not crash" — an unstated expected half is a gap. Paired-field templates
  (expected/actual) need the per-half rule stated.

### Evidence calibration for subagents and worktrees

A worktree changes the child working directory and isolates persisted writes; it is not a
filesystem sandbox and does not prove where a host resolved its advertised skills. A child
that reports loading an adapter from the main checkout while reading canonical files from its
worktree supports a discovery-contamination hypothesis only. Verify the rule in a separate
frozen top-level process with retained events before documenting it as host behavior.

An independently inspected diff proves the resulting artifact and its file identity. It does
not prove which reads, tool calls, validations or routing decisions produced that diff. Keep
those claims at `reported` unless their raw host events or command receipts were retained.
Literal `/skill-name` text handled by a child proves that child's interpretation; it does not
establish the interactive host's slash-command dispatch semantics.

## Design-time commands never block on missing context

Codex 0.3.0 smoke test (probes 4/5): given an abstract target with no repo present,
decompose-problem and plan-goal-run each returned a question list instead of their artifact —
graded PARTIAL even though routing and mutation-safety were perfect. The intake family's rule
generalizes to every artifact-producing design command: insufficient context forks to a
PROVISIONAL artifact with named gaps (assumption-tagged units, a draft charter with gap-marked
end-state), never a blocking clarify round. Eval the abstract-target case explicitly: expected
output is the provisional artifact, and a question-list response is the failure.

## Command-only is invisible by design — say so wherever install docs live

Live adopter confusion (Codex, 2026-09-01, v0.4.6): a model verified the plugin was installed,
saw a command-only skill absent from its available-skills catalog, and concluded the task had a
stale catalog — conflating "not visible to the model" with "not shipped." Two rules earned:
(1) every install/upgrade doc that says "start a fresh task if skills don't appear" MUST scope
that advice to model-invocable skills and state that command-only members are intentionally
absent from the model catalog (`disable-model-invocation: true`; Codex ships them as
`prompts/<name>.md`), invoked explicitly by name; (2) call them "command-only prompts," not
"skills," in that sentence — the word "skill" is what made the fresh-task advice misapply.
The inventory's per-member invocation dial ("command-only" vs "model + user invocable") is the
reader's authority; cite it.

## Declared config is recognized or WARNed — never silently defaulted

Live defect class (adiav2 adoption, tickets #100/#102): a repo DECLARED its conventions —
branch.pattern in prose naming Linear's branchName, the backend ruling in AGENTS.md instead of
CLAUDE.md — and the plugin silently fell back to defaults because the declaration didn't match
the one literal shape it looked for. Rule: config-reading code recognizes INTENT (a sentinel OR
a recognizable declaration of the same convention), and a declared-but-unrecognized value
produces a named WARN telling the author the sentinel — the silent-default branch exists only
for genuinely absent config. Discovery orders honor the repo's own canon: an explicit
structured block (workflow.json linear.*) > the harness entry file > the repo's declared
canonical file (AGENTS.md) > a file the entry file defers to by name. Negative controls for
every branch, including the "declared elsewhere than you expected" case.
