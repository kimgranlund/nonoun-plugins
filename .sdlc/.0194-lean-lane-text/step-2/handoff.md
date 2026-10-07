## Task goal
Add the lean lane text and the coarse-step rule to the chain skill and the planner contract, plus a steps.py lint warning, so a size-S or M ticket can run in one or two coarse steps.

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
