## Task goal
A recommendation with cited evidence, written back into this file: the rules to keep, the rules to change, and whether apply is worth building.

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
