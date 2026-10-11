<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Write the design doc `docs/specs/sdlc-lite/cascade-guard.md`. It covers a per-ticket agent-run counter that stops and asks after N runs, a single-reviewer route for a plan that is a mechanical copy of a passed plan, and the rule that a verifier never spawns a verifier. Index the doc in the specs folder, and keep docs_check.py, check.py and the no-dash rule green.

## Step 1: Write the cascade guard design and index it
level: L3
### Read first
- `docs/specs/sdlc-lite/AGENTS.md`
### Do
Design only, Markdown only. Nothing is built. Depends on: none. This step is also the plan's gates green step. The ticket is a docs-only change, so the gates are `docs_check.py`, `check.py` and `git diff --check`, per the root `AGENTS.md` validation table. No `check.sh`.

Files this step changes, and no others:
- `docs/specs/sdlc-lite/cascade-guard.md` (new).
- `docs/specs/sdlc-lite/README.md`: add one bullet linking `cascade-guard.md`, in the style of the `Lane lifecycle` bullet.
- `docs/specs/sdlc-lite/AGENTS.md`: add `- [cascade-guard.md](cascade-guard.md)` in alphabetical order inside the `sdlc-lite:managed` block, as `lane-lifecycle.md` was added for T-0422. docs_check does not flag a missing index entry, so the criteria check the entry directly. Evidence: `.sdlc/.0421-bounded-plan-correction-route/verifier-L2.md` line 8.

Shape, copied from the sibling designs `bounded-plan-correction.md` (T-0421) and `verifier-held-criteria.md` (T-0400):
- an H1 title;
- a `Status: ` line on line 3 that names ticket T-0427, says design only and not built, and says the maintainer's go is needed;
- a one-paragraph answer;
- a Sources section.

The doc must contain these H2 headings, each written exactly as `## <name>` or `## <n>. <name>`:
- `Cascade counter`
- `Template-instance plan review`
- `Verifier never spawns a verifier`
- `Relation to T-0421 and the replan cap`
- `Measures`
- `Files a build changes`
- `Build tickets`
- `Rejected alternatives`

What each heading must decide (all from the handoff Intent):

**Cascade counter.**
- The count is agent runs per ticket step, read from the task's `runs.jsonl`.
- It is checked in `dispatch.py prepare`. Read `plugins/sdlc-lite/scripts/dispatch.py` and quote the function where the check would sit.
- Give the exact message it prints. It stops and asks the maintainer and never continues silently.
- The override is explicit and recorded. Name where it is recorded.
- Choose N from measured run counts and state it. The handoff says T-0428 uses 6 until this lands.
  - Get the counts from the maison and agent-ui records: the `runs.jsonl` files under `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc` and `/Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc`, found with `find <repo>/.sdlc -name runs.jsonl`. Use `fleet_collect.py collect <repo>` (its `runs.by_ticket` field) or a read-only python tally.
  - Never pass `--gh`. Both repos are read-only.
  - Cite the counts: the distribution, and the T-0378 count of 11 named in the handoff.

**Template-instance plan review.**
- The proof that a plan is a mechanical copy of a passed plan is a command. Write it as one runnable command in a fenced block or code span. It shows that the diff against the passed plan touches only shas, counts and ids.
- One reviewer looks at the diff only, and the run does not count against the replan cap.
- Name what forces the normal route.
- Include the maintainer's skip rule: a reviewed pass is never re-verified unless a verified file changed since.
- Evidence: the maison T-0378 and T-0379 `plan-reviewer-L1.md` and `plan-reviewer-L1-2.md` paths named in the handoff Context. Read them as data.

**Verifier never spawns a verifier.**
- State what the `block-role-spawn` hook already enforces. Read `plugins/sdlc-lite/adapters/claude/hooks.json` and `plugins/sdlc-lite/scripts/hook-selftest.sh`, and cite them.
- State the gap the maison T-0339 case shows (`.sdlc/tickets/.0339-examples-axe-inherited-nodes/verifier-L3.md` in maison) and the rule that closes it.

**Relation to T-0421 and the replan cap.**
- Read `docs/specs/sdlc-lite/bounded-plan-correction.md` and `plugins/sdlc-lite/scripts/steps.py`: the replan cap `if len(replans) >= 2:` near line 2684, and `review_required` near line 2586.
- Also read `agents/plan-reviewer.md` and `docs/specs/sdlc-lite/verifier-held-criteria.md` (T-0400).
- Say how the template route and the counter fit with the bounded correction and the replan cap of one.
- Separate out T-0428 (the wording) and T-0429 (the docs-only skip). Read their closed folders `.sdlc/.0428-close-first-doctrine` and `.sdlc/.0429-skip-verifier-docs-only`.

**Measures.** K-004-style measures the collector can compute (`plugins/sdlc-lite/scripts/fleet_collect.py`, `runs.by_ticket`). Give each one a before value from the counts above.

**Files a build changes.** Repo-relative paths.

**Build tickets.** One entry per build ticket, each with a size L1 to L4 and its own negative control: the defect the gate must reject.

**Rejected alternatives.** Each one with the reason it was rejected.

Validation scope: run the criteria below. Also open every relative link in the new doc and confirm its target exists. No em or en dashes anywhere in the changed files.
### Acceptance criteria
- (red) `test -f docs/specs/sdlc-lite/cascade-guard.md`
- `grep -qE "^Status: " docs/specs/sdlc-lite/cascade-guard.md`
- `python3 -c "import sys;t=open('docs/specs/sdlc-lite/cascade-guard.md',encoding='utf-8').read();sys.exit(1 if (chr(0x2014) in t or chr(0x2013) in t) else 0)"`
- `python3 -c "import sys,re;L=open('docs/specs/sdlc-lite/cascade-guard.md',encoding='utf-8').read().splitlines();need=['Cascade counter','Template-instance plan review','Verifier never spawns a verifier','Relation to T-0421 and the replan cap','Measures','Files a build changes','Build tickets','Rejected alternatives'];miss=[n for n in need if not any(re.fullmatch('## ([0-9]+[.] )?'+re.escape(n)+' *',l) for l in L)];print(miss);sys.exit(1 if miss else 0)"`
- `grep -qF "(cascade-guard.md)" docs/specs/sdlc-lite/README.md`
- `grep -qF "[cascade-guard.md](cascade-guard.md)" docs/specs/sdlc-lite/AGENTS.md`
- The Cascade counter section states N as one integer and cites the maison and agent-ui run counts it was chosen from, with their source paths. The check runs in `dispatch.py prepare`, prints a stop-and-ask message, and its override is explicit and recorded (observed by reading the doc).
- The Template-instance plan review section gives the mechanical-copy proof as one runnable command. It states one reviewer on the diff only, that the run does not count against the replan cap, what forces the normal route, and that a pass is not re-verified unless a verified file changed since (observed by reading the doc).
- The Build tickets section lists each ticket with a size from L1 to L4 and its own negative control. The Verifier never spawns a verifier section states what `block-role-spawn` enforces today, citing `plugins/sdlc-lite/adapters/claude/hooks.json` (observed by reading the doc).
- `test -z "$({ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "docs/specs/sdlc-lite/(cascade-guard|README|AGENTS)\.md")"`
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/docs_check.py) && printf "%s\n" "$out" | grep -qE "^docs_check: 0 errors"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`

## Assumptions
- docs_check.py and check.py are green at HEAD 4e77062d: verified by running them. docs_check printed `docs_check: 0 errors, 25 warnings`. check.py printed `ok: 19 role levels, 9 agents, 22 generated definitions checked` and took about 4 seconds, so neither guard needs a `guard timeout:` line.
- The guard's grep shape can go red: verified by running the same pipeline with the error count pattern `^docs_check: [1-9][0-9]* errors`, which exited 1 on the green tree. That shows the output line is parsed as written.
- The heading check and the dash check discriminate: verified on fixtures under the tmp prefix. The heading check exited 0 with all headings present and 1 with `Measures` removed. The dash check exited 1 on a file holding U+2014.
- The scope check passes at base and rejects a stray path: verified. It exited 0 on the current tree with `.sdlc` excluded, and the grep part printed a non-allowed path from a fixture list. `.worktrees/tmp` is gitignored (`git check-ignore`).
- docs_check does not flag a missing AGENTS.md index entry, so the AGENTS.md entry gets its own grep criterion: verified by `.sdlc/.0421-bounded-plan-correction-route/verifier-L2.md` line 8.
- The source facts the builder relies on exist:
  - the replan cap is at `steps.py:2684`;
  - `fleet_collect.py` exposes `by_ticket`, at lines 14 and 547;
  - `block-role-spawn` is wired in `adapters/claude/hooks.json`;
  - the maison T-0378 plan-reviewer files exist;
  - maison and agent-ui keep per-task `runs.jsonl` files under `.sdlc/<task>/`, not one top-level file.

  All verified by grep, ls and find.
- Choosing N and the proof command is the design deliverable the ticket asks for, not an unsettled plan decision. The Do fixes the evidence N must come from and the form the proof must take.

## Risks
- The maison and agent-ui records may be thin or uneven, so N rests on few data points. The Do requires the doc to cite the counts, so a weak basis shows up in review rather than hiding.
- Content criteria 7 to 9 are judgment checks for the verifier. They hold the doc to the handoff's six decisions but cannot prove the decisions are good. The maintainer's go, stated in the Status line, remains the real gate.
- docs_check may add a D-11 warning (over 400 lines) if the doc runs long. A warning is not an error, and the criterion accepts 0 errors only.
