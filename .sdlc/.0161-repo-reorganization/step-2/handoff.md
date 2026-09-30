## Task goal
A recommendation with cited evidence, written back into this file: the rules to keep, the rules to change, and whether apply is worth building.

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
- `### Rules to keep` and `### Rules to change`: bullet lists that name the rule in `docs/repo-onboarding/reorganization.md` each item refers to.
- One line in exactly the form `Apply verdict: build`, `Apply verdict: defer`, or `Apply verdict: drop`, followed by a short justification. Say whether a reviewed plan carried out by hand is enough.

Do not edit `docs/repo-onboarding/reorganization.md`. Changing the design is follow-up work after the spike.

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
