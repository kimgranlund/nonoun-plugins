<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add the lean-lane text to the chain skill, the coarse-step rule to the planner contract, and a `steps.py lint` warning that never refuses, plus a check.py guard with a negative control. The goal is that a size-S or M ticket can run in one or two coarse steps, and no text claims a lane that code computes.

## Step 1: steps.py lint warning for non-coarse lean-eligible plans
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets are `plugins/sdlc-lite/scripts/steps.py` (a new function `lean_warnings(plan, task_dir, steps)`, `cmd_lint`, the lint entry of the module docstring, and `selftest`) and `docs/references/sdlc-internals.md` (the `## scripts/steps.py` paragraph, in the sentence ``lint <planner.md | task dir>` runs the same check and writes nothing``).

Settled decisions:
- **Eligibility.** A plan is eligible ("meets the lean plan conditions") only when all of these hold. Each one reuses an existing helper, so the facts stay where they already live.
  - `result_level(plan)` is 1 or 2. Catch `Fail` and treat it as not eligible: a file named `handoff.md` or `base-lint.md` raises today (steps.py:935-939). This keeps `/fix`'s step-handoff lint and the selftest `base-lint.md` case unwarned.
  - `plan_facts(plan)` returns no `unresolved:` item, every level is in 1..3, and no title starts with `Merge `.
  - `len(order.ordered(task_dir, 'planner')) < 2`, which means no replan.
  - `task_dir / 'handoff.md'` has no line equal to `## Plan review`. A missing handoff counts as none.
  - These are the plan-time facts `review_action` uses (steps.py:1213-1242). Ticket size and the AGENTS.md-owner condition are not computable here. T-0197 owns `steps.py lane` and the `review_required()` extraction, so this step does not extract `review_required()` and does not add `lane`.
- **Warnings.** Each warning is one stderr line. Exact formats:
  - more than two steps: `steps lint: warning: <plan>: <k> steps; the coarse-step rule allows at most 2 in a plan that meets the lean plan conditions (agents/planner.md, Coarse steps)`
  - a step whose `### Acceptance criteria` holds exactly one top-level list item (count `criteria_lines(block)` lines matching `^[-*] `): `steps lint: warning: <plan> step <n>: one acceptance criterion; the coarse-step rule merges it into a neighboring step (agents/planner.md, Coarse steps)`
- **Where warnings appear.** `cmd_lint` prints the warnings only after `lint_or_fail` passes. Stdout stays exactly `steps lint: ok` and the exit code stays 0. `split`, `swap`, and `widen` print no warnings: leave `lint_steps` and `lint_or_fail` unchanged, because split, swap, and widen share them.
- **Docstring.** Extend the `lint` entry so `steps.py -h` includes the literal `steps lint: warning:` and the eligibility list.
- **Internals doc.** Add one sentence to the sdlc-internals.md lint description naming `steps lint: warning:` and both triggers.
- **New selftest cases.** Print exactly these labels through `check(...)`:
  - `(lean) lint warns on a lean-eligible plan with 3 steps`: a `planner-L2.md` with three steps at L1 to L3 and two criteria each. Expect rc 0, stdout `steps lint: ok`, and stderr holding `steps lint: warning:` and `3 steps`.
  - `(lean) lint warns on a one-criterion step`: the existing `PLAN` fixture. Expect stderr to name step 1 and step 2.
  - `(lean) no warning for a planner L3 plan, a step at L4, a merge step, a replan, a ## Plan review line, or an unresolved: assumption`: six task dirs, each with err == '' and rc 0. The replan dir holds two planner files; the Plan review dir's `handoff.md` holds a `## Plan review` line.
  - `(lean) no warning for a two-step plan with two criteria per step`
- **Existing check (j).** It asserts `err == ''` for a task dir with two planner files. It stays green because a replan is not eligible. Do not weaken it.

Contract dependents:
- `/fix` lints `step-1/handoff.md`, which `result_level` excludes.
- `check.py`'s merge-block lint is a file target named for the merge block, so it is not eligible.
- No hook or other script reads lint stderr: `git grep -n "steps.py lint"` shows only docs and skills.

Depends on: none. Focused check: `python3 plugins/sdlc-lite/scripts/steps.py selftest`.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lean) lint warns on a lean-eligible plan with 3 steps"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lean) lint warns on a one-criterion step"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lean) no warning for a planner L3 plan, a step at L4, a merge step, a replan, a ## Plan review line, or an unresolved: assumption"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lean) no warning for a two-step plan with two criteria per step"`
- `d=$(mktemp -d) && printf "## Step 1: a\nlevel: L1\n### Acceptance criteria\n- x\n" > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d" 2>&1 >/dev/null | grep -qF "steps lint: warning:"`
- (guard) `d=$(mktemp -d) && printf "## Step 1: a\nlevel: L1\n### Acceptance criteria\n- x\n" > "$d/planner-L2.md" && out=$(python3 plugins/sdlc-lite/scripts/steps.py lint "$d" 2>/dev/null) && test "$out" = "steps lint: ok"`
- `python3 plugins/sdlc-lite/scripts/steps.py -h | grep -qF "steps lint: warning:"`
- `grep -qF "steps lint: warning:" docs/references/sdlc-internals.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/steps.py -e docs/references/sdlc-internals.md | grep -q .`

## Step 2: Lean chain text, coarse-step rule, check.py guard, regenerate, gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets:
- `plugins/sdlc-lite/agents/planner.md`: a new `## Coarse steps` section.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: a new `## Lean chain` section.
- `plugins/sdlc-lite/scripts/check.py`: a new guard and docstring item 13.
- The regenerated `plugins/sdlc-lite/adapters/codex/agents/*.toml`.

Settled decisions, from `docs/lean-sdlc/design.md` section "1. Lean chain" and resolved decision 2:
- **planner.md.** Insert `## Coarse steps` between the paragraph starting "Each step must be buildable" and `## Criteria that can pass`. It is the one authoritative home of the coarse-step rule and states:
  - one step per independently verifiable outcome, never one per file or concern (use the exact phrase `independently verifiable outcome`);
  - at most 12 criteria per step, guards included;
  - two steps with a sequential dependency, the same builder level, and no gate between them merge into one;
  - whole-suite gates stay on the final `gates green` step (rule 14), so a lean plan is one or two steps with the gates inside the last;
  - `steps.py lint` prints a `steps lint: warning:` line and never refuses when a plan that meets the lean plan conditions has more than two steps or a step with one criterion. Name the conditions exactly as Step 1 implements them: planner L1 or L2, every step at L1 to L3, no merge step, no replan, no `## Plan review` line, no `unresolved:` assumption.
- **chain SKILL.md.** Insert an unnumbered `## Lean chain` section after the paragraph starting "Every role runs through" and before `## 1. Brief`. It is the one authoritative home of the lane conditions and states:
  - **Lean conditions (all hold):** a size S or M ticket; planner L1 or L2; at most two steps, each at builder L1 to L3; no merge step; no replan; the change stays within one nearest `AGENTS.md` owner, or one script and its tests, with no change to a contract other roles parse (role output sections, `run.sh` tables, `steps.py`, `tickets.py` invariants, hooks).
  - **Full chain is mandatory when any of these holds:** planner L3; any step at L4 or L5; any merge step; any replan; a `## Plan review` line in the task handoff; an `unresolved:` assumption; the ticket changes role behavior, a runner invariant, a hook, or a check (its focused live run is still required); or a step touches shared generated state (roadmap, router, generated Codex agents) alongside other tickets in flight. A lean task that meets any of these is on the full chain from that point. Work already done stays valid.
  - **What lean means:** the planner's `Coarse steps` rule (link to agents/planner.md, do not restate it). Plan review still follows `steps.py review` (a lean plan is a routine plan). There is one verifier per step, and lean never skips a role that `steps.py review` or `steps.py next` asks for.
  - **Close-out:** the lean lane always runs the filer (sections 5 and 6 unchanged, no new `close` gate). Use the exact phrase `always runs the filer`.
  - **What the code computes today:** no script computes the lane yet. The conductor reads these conditions, and `steps.py lint` only warns on step and criterion counts. This sentence satisfies the ticket's "text must not claim a lane the code cannot compute".
  - No em dashes.
- **check.py.** Add a `Lean lane text` guard after the Read-first guard, with a dict mapping each phrase to the files that must hold it:
  - `'## Lean chain'`: `skills/chain/SKILL.md`
  - `'always runs the filer'`: `skills/chain/SKILL.md`
  - `'independently verifiable outcome'`: `agents/planner.md`
  - `'steps lint: warning:'`: `agents/planner.md` and `scripts/steps.py`

  Each pair is checked with the read-first pattern (check.py:358-366): append an error when the phrase is missing, and when present, append `<rel>: lean-lane negative control not flagged` if the missing-function does not flag `text.replace(phrase, '')`. Add docstring item `13. Lean lane text: ...` listing those pairs.
- **Regenerate.** Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. The planner TOMLs embed planner.md (check: `grep -l "gates green" adapters/codex/agents` lists `sdlc-planner-l{1,2,3}.toml`).
- **Left untouched on purpose:**
  - `agents/conductor.md` and the Codex host skill: T-0199 and T-0197 own those.
  - `skills/handoff-format`: the step template is unchanged.
- **Gates green.** Run every gate below and fix any red that Step 1 or this step introduced.

Depends on: step 1, which provides the `steps lint: warning:` text that the guard and the planner text name. This step is kept separate from step 1 because the merged step would exceed the 12-criterion limit.
### Acceptance criteria
- `grep -qF "## Lean chain" plugins/sdlc-lite/skills/chain/SKILL.md && grep -qF "always runs the filer" plugins/sdlc-lite/skills/chain/SKILL.md && grep -qF "Coarse steps" plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF "## Coarse steps" plugins/sdlc-lite/agents/planner.md && grep -qF "independently verifiable outcome" plugins/sdlc-lite/agents/planner.md && grep -qF "steps lint: warning:" plugins/sdlc-lite/agents/planner.md`
- `grep -qF "independently verifiable outcome" plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l2.toml`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && python3 -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.write_text(p.read_text().replace(\"independently verifiable outcome\", \"\"))" "$t/p/agents/planner.md" && ! python3 plugins/sdlc-lite/scripts/check.py "$t/p"`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && python3 -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.write_text(p.read_text().replace(\"## Lean chain\", \"\"))" "$t/p/skills/chain/SKILL.md" && ! python3 plugins/sdlc-lite/scripts/check.py "$t/p"`
- (guard) `! grep -qF "—" plugins/sdlc-lite/agents/planner.md plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite/scripts/steps.py docs/references/sdlc-internals.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/agents/planner\.md|plugins/sdlc-lite/skills/chain/SKILL\.md|plugins/sdlc-lite/scripts/check\.py|plugins/sdlc-lite/scripts/steps\.py|docs/maintenance/sdlc-internals\.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-[a-z0-9-]+\.toml)$" | grep -q .`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`

## Assumptions
- `steps.py lint` today prints only `steps lint: ok` on stdout and nothing on stderr for a clean plan: verified by steps.py:913-921 and by probe C6, which exits 0 with stdout `steps lint: ok`.
- `result_level` raises `Fail` on a name with no level, so lint on `handoff.md` or `base-lint.md` must catch it: verified by steps.py:935-939 and the selftest `base-lint.md` case near line 2276.
- Selftest (j)'s `err == ''` lint case uses a task dir with two planner files, so it is not eligible and stays green: verified by `j_dir` at steps.py:1811-1827.
- The other selftest lint calls check only stdout or rc, so warnings on stderr leave them green: verified by `grep -n "run_main(\['lint'" steps.py` and reading each assertion.
- `review_action`'s plan-time reasons (planner L3, L4/L5 step, a `Merge` title, two or more planner results, a `## Plan review` line, an `unresolved:` item) match the design's mandatory list: verified by steps.py:1213-1242 and design.md:83-87.
- check.py accepts a plugin root argument, and an unmodified copy passes: verified by probe D8b (rc 0, `ok: 19 role levels, 9 agents checked`).
- The planner TOMLs embed planner.md, so generate changes them: verified by `grep -l "gates green" plugins/sdlc-lite/adapters/codex/agents` listing `sdlc-planner-l1/l2/l3.toml`.
- All gates are green at HEAD 99d29b8: verified by probes G1 to G5 (check.sh, check-packaging, generate --check, tickets check, diff --check all rc 0).
- No touched file holds an em dash today: verified by `grep -c "—"`, which returns 0 for all five files.

## Risks
- T-0197 (`steps.py lane`, `review_required()`) must replace Step 1's inline eligibility facts with the extracted function, so the plan facts live in one place. Until then, `lean_warnings` repeats `review_action`'s plan-time reasons. That repetition is acceptable only because the warning is advisory.
- `check.sh` includes `claude plugin validate` and the hook live-probe selftest. A host without the `claude` CLI would turn the gates green guard red for reasons unrelated to this change. It is green on this host.
- The D8-style negative controls copy the whole plugin into a temp dir, so check.py runs against a copy. Their red state was observed at HEAD (rc 1). They only pass once the new guard flags the missing phrase.
