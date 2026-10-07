<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Build a throwaway, read-only reorganization prototype under the T-0161 task folder, run it on this repository with a trial layout, and write a recommendation backed by evidence into `.sdlc/0161-repo-reorganization/handoff.md`: which rules to keep, which to change, and whether apply is worth building.

## Step 1: Trial layout and read-only plan prototype
level: L3
### Do
Everything this step creates goes under `.sdlc/0161-repo-reorganization/spike/`. This is outside the plugin's shipped folders. The step does not create `docs/layout.md` or any other file outside that folder. It creates no ticket, and it moves or rewrites nothing in the repository.

1. Write `.sdlc/0161-repo-reorganization/spike/layout.md` as the trial layout. Use the format in `docs/specs/repo-onboarding/design.md#layout-file`: a `## Homes` section and a `## Frozen paths` section. Follow the "First trial" section of `docs/planning/repo-onboarding/reorganization.md`:
   - Homes: at least `maintenance/`, `reference/`, and `reports/`, plus globs that give destinations to the loose documents where a person would agree with the move.
   - Frozen: `docs/reports/`, `docs/reports/readiness-recovery-validation.md`, `plugins/sdlc-lite/bench/results/`, and `plugins/sdlc-lite/adapters/codex/agents/`.
   - Decide whether `generative-constructs` and `repo-onboarding` stay topics or become homes. Write one sentence of prose in the layout file saying which, and why.
2. Write `.sdlc/0161-repo-reorganization/spike/reorg_plan.py`. It must be Python 3.9 compatible (the host's `python3` is 3.9), standard library only, and read-only. It imports `parse_layout`, `frozen_match`/`_frozen`, and `list_documents` from `plugins/sdlc-lite/scripts/onboard.py` by adding that folder to `sys.path`, and it copies none of that code. CLI: `--layout <path>` (required) and `--json` (print one JSON object; without it, print human-readable tables). It follows the rules in `reorganization.md` (Inventory, Frozen material, Plan):
   - Inventory every tracked Markdown file and build the link graph from it.
   - Classify each candidate under `docs/` as placed, misplaced (with its destination), or unplaced.
   - Compute moves with the matching rule, and the link rewrites those moves imply, both in the citing files and inside each moved file.
   - Find frozen candidates, using the `YYYY-MM-DD` name rule or a `Recorded:` line in the first ten lines.
   - Find the links that are broken before any move.
3. JSON keys:
   - `placed`, `moves` (`{from,to,rule}`), `rewrites` (`{file,line,old,new}`), `unplaced`, `frozen_candidates` (`{path,reason}`), and `baseline_broken` (`{file,line,target}`).
   - `cite_forms`: for the documents that move, integer counts of cites by form, with at least the keys `markdown_link`, `backtick_path`, and `other`. This is the N5 evidence. Count reference-style links, autolinks, HTML links, anchors, and links inside code fences under their own keys when they occur.
   - `ambiguities`: a list of `{kind, paths}` for the three N2 cases, with `kind` one of `multi_home`, `name_collision`, `into_frozen`. The list is empty when none occur.
   - Output order must be deterministic (sorted).
4. Never move or rewrite a frozen path, and never propose to. Files under `.sdlc/` and git-ignored paths are always frozen.
5. Run it and save the output:
   - JSON to `.sdlc/0161-repo-reorganization/spike/plan.json`, as the exact stdout of `python3 .sdlc/0161-repo-reorganization/spike/reorg_plan.py --layout .sdlc/0161-repo-reorganization/spike/layout.md --json`.
   - The human tables to `.sdlc/0161-repo-reorganization/spike/plan.txt`.
6. Write `.sdlc/0161-repo-reorganization/spike/review.md`. Give one line per proposed move and per unplaced file: `ok` or `wrong`, a one-clause reason, and the verdict a person would give.
### Acceptance criteria
- `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import onboard as o; l=o.parse_layout(sys.argv[1]); assert all(o._frozen(l.frozen,p) for p in sys.argv[2:])" .sdlc/0161-repo-reorganization/spike/layout.md docs/reports/x.md docs/reports/readiness-recovery-validation.md plugins/sdlc-lite/bench/results/x.md plugins/sdlc-lite/adapters/codex/agents/x.toml`
- `python3 .sdlc/0161-repo-reorganization/spike/reorg_plan.py --layout .sdlc/0161-repo-reorganization/spike/layout.md --json | python3 -c "import json,sys; d=json.load(sys.stdin); assert {'placed','moves','rewrites','unplaced','frozen_candidates','baseline_broken','cite_forms','ambiguities'} <= set(d)"`
- `bash -c 'diff <(python3 .sdlc/0161-repo-reorganization/spike/reorg_plan.py --layout .sdlc/0161-repo-reorganization/spike/layout.md --json) .sdlc/0161-repo-reorganization/spike/plan.json'`
- `python3 -c "import json; d=json.load(open('.sdlc/0161-repo-reorganization/spike/plan.json')); files={b['file'] for b in d['baseline_broken']}; assert {'docs/specs/generative-constructs/README.md','docs/specs/generative-constructs/progressive-context-plugin.md'} <= files, files"`
- `python3 -c "import json; d=json.load(open('.sdlc/0161-repo-reorganization/spike/plan.json')); t=[m['from'] for m in d['moves']]+[r['file'] for r in d['rewrites']]; bad=[p for p in t if p.startswith(('docs/reports/','.sdlc/','plugins/sdlc-lite/bench/results/','plugins/sdlc-lite/adapters/codex/agents/')) or p=='docs/reports/readiness-recovery-validation.md']; assert not bad, bad"`
- `python3 -c "import json; d=json.load(open('.sdlc/0161-repo-reorganization/spike/plan.json')); seen={m['from'] for m in d['moves']}|set(d['unplaced']); want={'docs/other/claude-handoff.md','docs/other/claude-response.md','docs/references/codex-role-execution.md','docs/references/plugin-compatibility.md'}; assert want <= seen, want-seen"`
- `python3 -c "import json; d=json.load(open('.sdlc/0161-repo-reorganization/spike/plan.json')); c=d['cite_forms']; assert all(isinstance(c[k],int) for k in ('markdown_link','backtick_path','other')); assert all(a['kind'] in ('multi_home','name_collision','into_frozen') for a in d['ambiguities'])"`
- `test -s .sdlc/0161-repo-reorganization/spike/plan.txt`
- `python3 -c "import json; d=json.load(open('.sdlc/0161-repo-reorganization/spike/plan.json')); r=open('.sdlc/0161-repo-reorganization/spike/review.md').read(); miss=[p for p in [m['from'] for m in d['moves']]+d['unplaced'] if p not in r]; assert not miss, miss"`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc')"`
- (guard) `test -z "$(git ls-files --others --exclude-standard -- . ':(exclude).sdlc/0161-repo-reorganization')"`

## Step 2: Recommendation in the handoff, gates green
level: L3
### Do
Add a `## Recommendation` section at the end of `.sdlc/0161-repo-reorganization/handoff.md`. Leave the front matter and the existing sections unchanged, and do not change `status:`, because the conductor closes the ticket. Base every claim on `spike/plan.json`, `spike/plan.txt`, or `spike/review.md`, and cite the file (and the key or line) it came from. The section contains:
- A line in exactly the form `Counts: placed P, misplaced M, unplaced U`, with the integers taken from `len(placed)`, `len(moves)`, and `len(unplaced)` in `plan.json`. Follow it with the share of moves that `review.md` judged `ok`.
- One labelled paragraph per open finding, starting `N1:`, `N2:`, `N3:`, `N5:`, `N9:`, `N15:`. Each paragraph says whether the finding occurred in practice, with evidence:
  - N5: the `cite_forms` counts.
  - N2: the `ambiguities` entries.
  - N3: whether a topic needed a glob.
  - N1, N9, and N15: what should hold the plan (a ticket or a file outside `.sdlc/`), with the reason.
- `### Rules to keep` and `### Rules to change`: bullet lists that name the rule in `docs/planning/repo-onboarding/reorganization.md` each item refers to.
- One line in exactly the form `Apply verdict: build`, `Apply verdict: defer`, or `Apply verdict: drop`, followed by a short justification. Say whether a reviewed plan carried out by hand is enough.

Do not edit `docs/planning/repo-onboarding/reorganization.md`. Changing the design is follow-up work after the spike.

This is the gates green step. Run every gate below and fix any red that step 1 introduced.
### Acceptance criteria
- `awk '/^## Recommendation/,0' .sdlc/0161-repo-reorganization/handoff.md | grep -qE '^Apply verdict: (build|defer|drop)$'`
- `for n in N1 N2 N3 N5 N9 N15; do awk '/^## Recommendation/,0' .sdlc/0161-repo-reorganization/handoff.md | grep -q "^$n:" || exit 1; done`
- `for h in '### Rules to keep' '### Rules to change'; do awk '/^## Recommendation/,0' .sdlc/0161-repo-reorganization/handoff.md | grep -qxF "$h" || exit 1; done`
- `python3 -c "import json,re; d=json.load(open('.sdlc/0161-repo-reorganization/spike/plan.json')); t=open('.sdlc/0161-repo-reorganization/handoff.md').read().split('## Recommendation',1)[1]; m=re.search(r'^Counts: placed (\d+), misplaced (\d+), unplaced (\d+)', t, re.M); assert m and tuple(map(int,m.groups()))==(len(d['placed']),len(d['moves']),len(d['unplaced'])), m and m.groups()"`
- `awk '/^## Recommendation/,0' .sdlc/0161-repo-reorganization/handoff.md | grep -qF 'plan.json'`
- (guard) `python3 -c "import subprocess,sys; a=subprocess.run(['git','show',sys.argv[1]+':'+sys.argv[2]],capture_output=True,text=True,check=True).stdout; b=open(sys.argv[3]).read(); f=lambda t:t.split('\n---\n',1)[0]; assert f(a)==f(b)" "$SDLC_BASE_SHA" .sdlc/0161-repo-reorganization/handoff.md .sdlc/0161-repo-reorganization/handoff.md`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc')"`
- (guard) `test -z "$(git ls-files --others --exclude-standard -- . ':(exclude).sdlc/0161-repo-reorganization')"`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- .sdlc/0161-repo-reorganization`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check`
- (guard) `python3 scripts/check-packaging.py`

## Risks
- The trial layout comes from `.sdlc/0161-repo-reorganization/spike/layout.md` through `--layout`, not from `docs/layout.md`. This follows the "nothing in this repository is moved or rewritten" rule, but it means the prototype never tests the real file location or setup creating `docs/layout.md`.
- `onboard.py`'s `_frozen` is a private helper. If T-0160 renames it, step 1's first criterion and the prototype's import break.
- Deciding whether a move "looks right to a person" is the builder's judgement in `review.md`. No criterion can check that judgement, only that every move and unplaced file is reviewed. The conductor should read `review.md` before accepting the verdict.
- Counting cite forms (N5) depends on the prototype's own heuristics for backticked paths. False positives or misses there skew the N5 answer. The recommendation should state the heuristic it used.
- Other lanes sync into main while this runs. If a sync adds tracked Markdown files under `docs/`, `plan.json` goes stale against a fresh run, and step 1's diff criterion goes red until `plan.json` is regenerated.
