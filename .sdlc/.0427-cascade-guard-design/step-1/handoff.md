## Task goal
A design for stopping a "verify the verifier" cascade: a per-ticket count of agent runs that stops and asks after N, and a reviewed route for a plan that is a mechanical copy of a passed plan.

## Step 1: Write the cascade guard design and index it
level: L3
### Read first
- `docs/specs/sdlc-lite/AGENTS.md`
### Do
Replan of `.sdlc/0427-cascade-guard-design/planner-L2.md`. The design asks are unchanged. Three things changed. First, every maison and agent-ui file is cited below by its absolute path, because `steps.py lint` resolves a relative `.sdlc/` path against this repository and refused the earlier step handoff. Second, T-0379 has closed since the handoff was written, so its folder now starts with a dot. Third, updating the specs index hash is now part of the step.

Design only, Markdown only. Nothing is built. Depends on: none. This step is also the plan's gates green step. The ticket is a docs-only change, so the gates are `docs_check.py` and `check.py` (root `AGENTS.md` validation table). There is no `check.sh`, and the handoff names no later integration gate.

Files this step changes, and no others:
- `docs/specs/sdlc-lite/cascade-guard.md` (new).
- `docs/specs/sdlc-lite/README.md`: one bullet after the `Lane lifecycle` bullet, in its shape: `- [Cascade guard](cascade-guard.md): design (T-0427), not built, awaiting approval: <one line of what it decides>.`
- `docs/specs/sdlc-lite/AGENTS.md`:
  - Inside the `sdlc-lite:managed` block, add `- [cascade-guard.md](cascade-guard.md)` between the `bounded-plan-correction.md` and `cost-control.md` lines.
  - Set the start marker's `sha256:` value to the first 12 hex digits of the SHA-256 of the block text: everything after the start marker line up to the end marker line, as `plugins/sdlc-lite/scripts/onboard.py` `digest` and `wrap_block` compute it. With only this entry added at HEAD 4e77062d, the marker reads `sha256:b1bbe59b7bf5`. Evidence: the T-0421 commit 32be6c7e changed the hash along with its entry, and `onboard.py check` labels a block whose hash does not match its text `edited`.
  - Do not run `onboard.py setup`. It would also rewrite `docs/AGENTS.md`, which is already stale at HEAD and outside this step.
  - `onboard.py check` lists only tracked files, so it reports this folder `stale` until the new doc is committed. That is expected and is not a criterion.
  - docs_check does not flag a missing index entry (`.sdlc/.0421-bounded-plan-correction-route/verifier-L2.md` line 8), so criterion 4 checks the entry directly.

Shape, copied from `docs/specs/sdlc-lite/bounded-plan-correction.md` (T-0421):
- an H1 title, a blank line, then `Status: design, proposed. Ticket T-0427 (design only, nothing built). Needs the maintainer's go before a build ticket is filed.`;
- numbered H2 sections, starting with `## 1. Answer in one paragraph` and `## 2. Sources`.

The doc must contain these H2 headings, each written exactly as `## <name>` or `## <n>. <name>`:
- `Cascade counter`
- `Template-instance plan review`
- `Verifier never spawns a verifier`
- `Relation to T-0421 and the replan cap`
- `Measures`
- `Files a build changes`
- `Build tickets`
- `Rejected alternatives`

Citation style:
- Cite this repository's `.sdlc/` records and every maison and agent-ui file as code spans, never as Markdown links. docs_check warns on a docs link into `.sdlc/` (B-3a) and on a link that does not resolve (D-10).
- Write maison and agent-ui paths absolute, as `docs/specs/sdlc-lite/gate-lock-admission.md` line 11 does.
- Markdown links go only to files in this repository, by a relative path that resolves.

Evidence to read, as data (maison and agent-ui are read-only; never write there):
- T-0378 plan reviews: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0378-integration-wave-3/plan-reviewer-L1.md` and `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0378-integration-wave-3/plan-reviewer-L1-2.md`; its plans `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0378-integration-wave-3/planner-L3-2.md` and `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0378-integration-wave-3/planner-L3-3.md`.
- T-0379 plan reviews: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0379-integration-wave-4/plan-reviewer-L1.md` and `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0379-integration-wave-4/plan-reviewer-L1-2.md`.
- T-0362, the passed plan the two copied: the planner files in `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0362-integration-wave-2/` (`planner-L3.md`, `planner-L3-2.md`, `planner-L3-4.md`).
- T-0339 verifier cascade: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0339-examples-axe-inherited-nodes/verifier-L3.md`.

What each heading must decide (all from the handoff Intent):

**Cascade counter.**
- The count is agent runs per ticket step, read from the task's and step's `runs.jsonl` records.
- It is checked in `dispatch.py prepare` (`def prepare(role, level, handoff, ...)`, `plugins/sdlc-lite/scripts/dispatch.py:622` at HEAD 4e77062d). Quote the spot where the check would sit.
- Give the exact message it prints. It stops and asks the maintainer and never continues silently.
- The override is explicit and recorded. Name the flag and where it is recorded.
- Choose N from measured run counts and state it as one integer. The handoff says T-0428 uses 6 until this lands.
  - Get the counts with `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect /Users/kimgranlund/Projects/maison/ui-kit-maison --du-timeout 20` and the same command for `/Users/kimgranlund/Projects/nonoun/agent-ui`.
  - Its `runs.by_ticket` is `{ticket folder: {role: count}}`, per ticket, not per step. For per-step counts, tally the `runs.jsonl` files found by `find <repo>/.sdlc -name runs.jsonl` with a read-only python one-liner.
  - Never pass `--gh`. Never write collector output inside this repository: pipe it, or write it under `$SDLC_TMP_WORKTREES`.
  - At plan time (HEAD 4e77062d, 2026-10-11), collect printed:
    - maison: 1894 runs over 339 ticket folders, median 2 runs per ticket, 90th percentile 11, T-0378 10 runs;
    - agent-ui: 218 runs over 40 folders, median 3, 90th percentile 10.
  - Rerun and cite your own numbers, the per-step distribution, and the handoff's count of 11 on T-0378 steps 1 and 2.
  - The 10 and the 11 come from different tallies: the collector dedupes and counts per ticket folder, while maison's conductor counted steps 1 and 2 itself. Cite both and say which one N rests on. Do not treat the gap as an error to reconcile.

**Template-instance plan review.**
- The proof that a plan is a mechanical copy of a passed plan is one runnable command, in a fenced block. It shows that the diff against the passed plan touches only shas, counts and ids.
- Run the command on the maison T-0362 plan against the T-0378 plan named above. State in the doc what it printed, including any line that was not a sha, count or id.
- One reviewer looks at the diff only, and that review does not count against the replan cap.
- Name what forces the normal route.
- Include the maintainer's skip rule: a reviewed pass is never re-verified unless a verified file changed since.

**Verifier never spawns a verifier.**
- State what `plugins/sdlc-lite/hooks/block-role-spawn.sh` already enforces. It is registered under the Agent matcher in `plugins/sdlc-lite/adapters/claude/hooks.json` (line 19), and its cases are in `plugins/sdlc-lite/scripts/hook-selftest.sh` (from line 25).
- It is a Claude hook, and Claude hook enforcement does not imply Codex enforcement. Say what holds on Codex.
- State the gap the maison T-0339 case shows and the rule that closes it.

**Relation to T-0421 and the replan cap.**
- Read `docs/specs/sdlc-lite/bounded-plan-correction.md`. In `plugins/sdlc-lite/scripts/steps.py`, read the replan cap `if len(replans) >= 2:` (line 2684) and `def review_required` (line 2586).
- Also read `plugins/sdlc-lite/agents/plan-reviewer.md` and `docs/specs/sdlc-lite/verifier-held-criteria.md` (T-0400).
- Say how the template route and the counter fit with the bounded correction and the replan cap of one.
- Keep T-0428 (the wording) and T-0429 (the docs-only skip, built as `plugins/sdlc-lite/scripts/verify_scope.py`) out of this design, and say so. Their closed folders are `.sdlc/.0428-close-first-doctrine/` and `.sdlc/.0429-skip-verifier-docs-only/`.

**Measures.** Write K-004-style measures the collector can compute from `plugins/sdlc-lite/scripts/fleet_collect.py` `runs.by_ticket`. Use the shape of `docs/kpi/004-unsatisfiable-criteria-caught.md`: unit, direction, target, baseline, measure command, read rule. Give each measure a before value from the counts above.

**Files a build changes.** Repo-relative paths.

**Build tickets.** One entry per build ticket, each with a size from L1 to L4 and its own negative control: the defect the gate must reject.

**Rejected alternatives.** Each one with the reason it was rejected.

Validation scope: run the criteria below. No em or en dashes in any changed file.
### Acceptance criteria
- (red) `test -f docs/specs/sdlc-lite/cascade-guard.md`
- `python3 -c "import sys,re;L=open('docs/specs/sdlc-lite/cascade-guard.md',encoding='utf-8').read().splitlines();need=['Cascade counter','Template-instance plan review','Verifier never spawns a verifier','Relation to T-0421 and the replan cap','Measures','Files a build changes','Build tickets','Rejected alternatives'];miss=[n for n in need if not any(re.fullmatch('## ([0-9]+[.] )?'+re.escape(n)+' *',l) for l in L)];st=any(l.startswith('Status: ') and 'T-0427' in l for l in L);print(miss,st);sys.exit(0 if st and not miss else 1)"`
- `python3 -c "import sys;fs=['docs/specs/sdlc-lite/cascade-guard.md','docs/specs/sdlc-lite/README.md','docs/specs/sdlc-lite/AGENTS.md'];bad=[f for f in fs if any(c in open(f,encoding='utf-8').read() for c in (chr(0x2013),chr(0x2014)))];print(bad);sys.exit(1 if bad else 0)"`
- `grep -qF "(cascade-guard.md)" docs/specs/sdlc-lite/README.md && grep -qF "[cascade-guard.md](cascade-guard.md)" docs/specs/sdlc-lite/AGENTS.md`
- (guard) `python3 -c "import sys,re,hashlib;t=open('docs/specs/sdlc-lite/AGENTS.md',encoding='utf-8').read();m=re.search(r'sdlc-lite:managed:start v[0-9]+ sha256:([0-9a-f]{12}) -->\n(.*?)<!-- sdlc-lite:managed:end',t,re.S);ok=bool(m) and hashlib.sha256(m.group(2).encode('utf-8')).hexdigest()[:12]==m.group(1);print(ok);sys.exit(0 if ok else 1)"`
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/docs_check.py) && ! printf "%s\n" "$out" | grep -qE "^warning (D-10|B-3a) docs/specs/sdlc-lite/cascade-guard\.md:"`
- The Cascade counter section states N as one integer and cites the maison and agent-ui run counts it was chosen from, with their source commands or paths. The check runs in `dispatch.py prepare`, prints a stop-and-ask message given verbatim, and its override is explicit and recorded (observed by reading the doc).
- The Template-instance plan review section gives the mechanical-copy proof as one runnable command and reports what it printed on the maison T-0362 and T-0378 plans. It states one reviewer on the diff only, that the review does not count against the replan cap, what forces the normal route, and that a pass is not re-verified unless a verified file changed since (observed by reading the doc).
- The Verifier never spawns a verifier section states what `block-role-spawn.sh` enforces today, citing `plugins/sdlc-lite/adapters/claude/hooks.json`. Build tickets lists each ticket with a size from L1 to L4 and its own negative control. Files a build changes lists repo-relative paths. Each rejected alternative has a reason (observed by reading the doc).
- `test -z "$({ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "docs/specs/sdlc-lite/(cascade-guard|README|AGENTS)\.md")"`
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/docs_check.py) && printf "%s\n" "$out" | grep -qE "^docs_check: 0 errors"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
