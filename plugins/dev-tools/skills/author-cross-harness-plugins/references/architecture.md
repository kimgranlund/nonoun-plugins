# Architecture

## Source-of-truth rule

The shared behavioral core owns the workflow. Claude and Codex adapters own
only host metadata or mechanics. A change to workflow behavior lands once.

Recommended plugin tree:

```text
plugin-name/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── skills/<skill-name>/
│   ├── SKILL.md
│   ├── agents/openai.yaml       # Codex skill UI/policy
│   ├── references/
│   ├── scripts/
│   └── assets/
├── agents/
│   ├── openai.yaml              # optional Codex plugin UI metadata
│   └── <agent>.md               # shared body / Codex agent
├── commands/<command>.md        # portable command body
├── scripts/
├── assets/
├── hooks.json                   # Codex hook adapter when hooks exist
├── .mcp.json                    # Codex MCP adapter when MCP exists
├── adapters/claude/
│   ├── skills/<skill-name>/     # only when Claude-only frontmatter is needed
│   ├── commands/<command>.md    # only when Claude metadata is needed
│   ├── hooks.json               # Claude path substitutions
│   └── .mcp.json                # local MCP path substitutions
└── HARNESS-NOTES.md
```

Do not create adapter directories for surfaces the plugin does not ship.

## External toolchains must agree with the adapter tree

A generated-overlay pipeline (an emitter that writes `.codex-plugin/`, per-skill `openai.yaml`,
prompts) and this skill's adapter-tree convention are two answers to the same problem — when both
exist in an estate, every reader in the pipeline must source Claude-only frontmatter from the
adapter tree, not the shared root. Live case (2026-08-31, kimgranlund/claude-plugins#1010/#1011):
an emitter reading `disable-model-invocation` off the shared root silently regenerated every
command-shaped skill as model-routable (dropping its Codex `policy:` block), and the release
gate's lint flagged all 25 shared roots for deliberately-absent fields. Before adopting the
adapter tree in an estate with shipping tooling, verify (or fix) that the emitter, linter, and
release gate are adapter-tree aware — a stale cached copy of a fixed tool reintroduces the bug
(also observed live: a pre-fix cached emitter stripped freshly regenerated policy blocks).

## Three portability classes

### Shared

The same file preserves semantics in both harnesses. Typical examples:

- `skills/<name>/SKILL.md` using the Agent Skills core fields, when Claude's
  default invocation behavior is sufficient;
- `references/`, `assets/`, and self-contained scripts;
- plain command bodies that do not use host expansion tokens;
- remote MCP configuration with identical authentication semantics.

### Adapted

The behavior is shared but host metadata or execution syntax differs. Typical
examples:

- a generated Claude skill tree when Claude-only frontmatter is required;
- Claude agent frontmatter prepended directly on the root Codex agent body
  (co-located, not a separate adapter file — Claude Code has no manifest field
  for relocating agents, verified against CLI 2.1.250; see `claude-code.md`'s
  Agent adapter section);
- Claude `disable-model-invocation` paired with Codex
  `policy.allow_implicit_invocation` in their respective adapter files;
- hook or local-MCP commands that need `${CLAUDE_PLUGIN_ROOT}` in Claude but a
  different executable resolution strategy in Codex;
- two manifest locations with synchronized identity fields.

### Host-only

The other harness has no equivalent. Keep it optional, move essential behavior
into a shared skill, and record the degradation. Examples can include a native
background/fork mode, monitor, output style, app connector, or UI-only asset.
Never claim host-only enhancement as cross-harness behavior.

## Canonical behavior rules

- Names are stable public APIs. Skill `name` matches its directory.
- Descriptions say what the surface does and when it applies; trigger language
  is front-loaded.
- Shared `SKILL.md` frontmatter contains only the Agent Skills portable core.
  Claude-only fields live in a generated Claude skill adapter.
- Shared bodies do not contain `${CLAUDE_*}`, `$ARGUMENTS`, dynamic `!command`
  injection, or assumptions about one harness's current working directory.
- File references are relative Markdown links. Instructions locate executable
  helpers relative to the loaded skill or plugin root.
- Delegation is capability-conditional: use native delegation when available;
  otherwise execute the same phases serially.
- Permissions and dependencies are not conflated. Declaring an MCP dependency
  does not grant permission to call it.
- Side effects retain the same approval point in both harnesses.

## Adapter fidelity

For skills, agents, or commands that require two files, the adapter body after
its YAML frontmatter matches the shared body exactly. Skill resources referenced
by relative path are copied mechanically into the adapter tree and checked for
byte-for-byte drift. Metadata may differ; workflow text may not.

When exact equivalence is impossible, `HARNESS-NOTES.md` uses this shape:

```markdown
| Surface | Harness | Missing semantic | Fallback | Verification |
|---|---|---|---|---|
| `deploy` skill | Codex | model-only visibility | Explicit invocation remains visible | Manual routing test pending |
```

## Rebase integrity in a version-slot merge queue

Observed live (adia-harness PR #81, 2026-09-01): a rebase's auto-merge reported success with
no conflicts yet silently dropped independently-added blocks — an entire new skill directory
(root + adapter), its naming-manifest exemption, a plugin.json displayName key, and an
authz-log line. Cause is git's own content merge on near-identical anchor context around two
independently-added blocks, not anything specific to the change being rebased; structural
gates all passed against the corrupted tree because they cannot know what SHOULD exist.

Standing rule for any rebase inside a parallel-build version queue: after the rebase, run
`git diff origin/main HEAD --diff-filter=D --name-only` and justify every deletion by name
(a legitimately-deleted generated file, e.g. a command-only prompt file for a skill that is
no longer command-only) before pushing. The marshal's independent verify repeats the same
sweep. A deletion nobody can explain is a stop-and-restore, never merged.

Second live finding (same PR, minutes later): the reviewer, running in the SHARED worktree,
caught live `<<<<<<<` conflict markers and 3 release_gate failures — later forensics
(`git show <sha>:<path>` on every tracked file) proved the committed blobs carried no
markers; the reviewer had read the working tree mid-rebase, while git had conflict markers
materialized on disk. Three additions to the standing rule: a reviewer verifies
`git rev-parse HEAD` matches the dispatched SHA before AND after its gate runs (a moved
HEAD invalidates the pass); the marshal's verify includes a conflict-marker grep and the
release gate, not only the fixture gate; and a builder never pushes to a branch whose
review is live — the marshal sequences every push once review has been dispatched.

Root cause of the same PR's double-push: the first rebase ran against a STALE local
`origin/main` ref — it reported success and every downstream check passed because the tree
was internally consistent, just not actually caught up. Mandatory first step after any
rebase: `git fetch origin main && git merge-base --is-ancestor origin/main HEAD` — ancestry
against the freshly-fetched remote tip, before gates, before the deletion sweep.

## Composing with an adopter repo's own harness (repo-adapter-wins)

Earned from the first real adoption (adiav2, 2026-09-01, tickets #88/#95/#100-#103). A governed
repo often already carries its own repo-local harness — hooks, a workflow.json contract, even
same-named repo-local skills. The plugin composes; it never competes:

- **Repo-local wins, structurally.** Every lifecycle procedure opens with a Step 0 defer-check:
  a same-named repo-local skill exists → invoke it by name and stop; the plugin's own steps
  never run. Absent → byte-identical default behavior.
- **workflow.json is the override surface.** pr.transport (e.g. github-rest-api via `gh api`,
  never the high-level PR CLI when declared), branch.pattern, linear.* statuses — declared keys
  win; an unsatisfiable declaration is a named FAIL, never a silent fallback.
- **Intentional collisions need an acknowledgment mechanism.** A permanent repo-local override
  otherwise WARNs forever and makes "no collisions" acceptance criteria unmeetable. Pattern:
  an acknowledgedCollisions list in workflow.json — acknowledged+real reads INFO (uncounted),
  acknowledged+stale is itself a WARN, unacknowledged keeps the WARN.
- **Verify-capability probes beat static config checks.** The adopter's own doctor pattern
  (adopted into team-init): prove the PR writer is USABLE with a bounded side-effect-free call
  (empty POST → expected HTTP 422 proves auth+scope without creating anything); disclose that
  the check makes one real network call.
- **Review the adoption PR from both sides.** The adopter's review found upstream defects
  (silent config misreads, missing status transitions) that unit tests never could — a live
  adoption run is the only test of composition. Budget for a fix wave immediately after the
  first adopter's review.

Upstream PRs into a SHARED toolchain repo (nonoun/plugins, 2026-09-01, plugins-c4 incident):
never switch that repo's primary checkout to a feature branch — peers commit there assuming
`main` (a peer's ops commit landed on my PR branch and needed a cherry-pick recovery). Do
upstream work in a worktree or scratch clone; the primary stays on `main`, always. Corollary for
the toolchain-agreement rule: "use the repo-main emitter" means main WITH the fix merged, and
until the upstream PR merges the fix is used from a worktree path, not by moving the primary.

Bash default cwd is NOT stable across calls in a multi-worktree session (2026-09-02, seats v14
and reviewer-v13): a fresh Bash call's cwd can land in the primary checkout OR any sibling
worktree — one build edited the primary by mistake, one reviewer ran gates against the wrong
worktree, one build saw its cwd silently become another seat's tree. Hard rule for every seat
prompt: absolute paths (or `git -C <worktree>`) on every command, and a `git rev-parse
--show-toplevel` sanity print before any gate run whose result will be reported.

Marshal verification must never mutate a seat's worktree (2026-09-02): a `git reset --hard
origin/<branch>` run in a builder's worktree to pin the reported SHA silently discarded that
builder's uncommitted rebump. Verify from a scratch export instead — `git -C <repo> fetch` then
`git archive <sha> | tar -x -C <scratch>` (or a throwaway `git worktree add --detach`) — and
compare `git rev-parse origin/<branch>` to the reported SHA without touching the seat's tree.

Adapter-tree sync is TWO fields, not one (2026-09-02, seats v20 #131/#132): the emitter reads
bodies FROM the root skills/ tree and never writes the Claude adapter copies back — so every
root SKILL.md body edit must be synced into adapters/claude/skills/<name>/SKILL.md by hand (the
tree Claude Code actually loads), AND the adapter's own frontmatter `description` must be
re-synced whenever the root description changes — validate_cross_harness reports description
drift as a separate error from body drift. A scripted root-vs-adapter diff over description
AND body (frontmatter otherwise excluded) belongs in every build seat's pre-PR checklist.

## Version-slot merge queue, second night (adia-harness 2026-09-02, PRs #158 to #181)

Fourteen PRs through one marshal, one reviewer, ten build seats. Rules earned, each from a live
incident:

- **A blocker jumping the queue costs every PR behind it a rebump.** G14 (version strictly above
  origin/main) means a 0.6.16 blocker landing ahead of 0.6.10/0.6.14 forced both to rebump; assign
  slots at dispatch, reassign explicitly on every queue reorder, and tell each seat its slot in the
  rebase message. Two seats independently picked the same slot (0.6.16, 0.6.18) when left to guess.
- **Squash merges make every sibling CONFLICTING the moment one lands** (ledger and manifest
  version lines). Rebase strictly one at a time, in landing order; pre-review substance on the
  un-rebased SHA so the reviewer's final pass is ancestry + gates only.
- **A branch built on top of another open PR's branch gets flattened, never rebased**: after the
  base PR squash-merges, `git checkout -b flat origin/main` + apply the branch's OWN commits' diff
  (not the whole-tree diff against main, which silently reverts everything that landed in between;
  a seat caught exactly that before applying). Merge commits in a seat branch are the signal.
- **Docs-only commits behind main are acceptable ancestry** when the file-list intersection with
  the PR is empty (`comm -12` on the two diff lists) and GitHub reports MERGEABLE; the reviewer
  verifies the intersection, never assumes it.
- **Regeneration replaces only its fenced span**: a conflict on the marker line itself leaves an
  orphaned `<<<<<<< HEAD` above the block that the generator never sees, and a count-only freshness
  check passes a banner whose version is stale. Freshness checks must compare the banner version to
  the manifest and fail on any conflict marker in a generated file (adia-harness #174, #175).
- **Two release_gate copies disagree**: the harness cache copy flagged a G3 lint FAIL that the
  repo-main copy did not; name which copy a verdict came from, and let the ship gate (repo-main)
  be the authority.
- **PR-body gates are literal**: check_merge accepts only `**Status** - done`; check_handoff accepts
  `**Field** - text` and `**Field**: text` but not `**Field:** text` (#169). State the accepted
  shape in the seat brief; a builder should not reverse-engineer a regex.
- **A seat that pushes outside its signal is a queue hazard, not initiative**: one seat rebumped
  and pushed on a version correction while frozen; harmless that time, but the marshal's "no push
  until the go" line goes in every rebase brief verbatim.
- **Design records ride the same queue rules but merge fast-forward, owner-ratified**, no version
  bump; the seat drafts on a branch, the owner rules on the stop-and-asks in one batched round,
  the seat finalizes (status flip + ratification line), the marshal fast-forwards main.

## One release per merge, and the overnight board clear (adia-harness 2026-09-02, PRs #190 to #224)

Twenty merges, twenty releases (0.6.24 to 0.6.56), one marshal, one reviewer, up to four build seats.

- **Release per merge without a bump commit**: package the artifact from a detached worktree at
  the PR head (G14 passes there: head > main), squash-merge, then `gh release create --target
  <merge sha>` with that artifact. Main never carries a "Ship" commit; the PR's own version IS the
  release. Patch numbers climb freely; the owner ruled "0.6.93 would be totally fine".
- **Version order beats readiness order** when three PRs sit on adjacent slots: merging the
  highest first forces the other two to rebump. Reorder the review queue by version (lowest
  first) and each lands with a ledger-only rebase.
- **`git reset --soft origin/main` to flatten is a revert trap**: it stages the branch's whole tree
  over main, silently undoing every file main changed since the fork. Two seats caught it; the
  safe flatten re-applies only the branch's OWN authored files (or cherry-picks its non-merge
  commits) onto a fresh branch off main, then diffs against main to prove additive-only.
- **A regenerated-but-uncommitted inventory is the classic "passed on my dirty tree" report**:
  the builder ran `make_inventory.py check` against the working tree, pushed a commit without the
  regenerated files, and main's new banner-version rule caught it. Verify from git objects, never
  from a seat's working tree.
- **Reviewer methodology that found real bugs**: a ThreadPoolExecutor(10) against any store
  writer (found assign_slot's slot duplication and the unlocked sibling stores); two minted
  identities against a shared store (found the session-identity clobber); a poison-pill run_fn
  that raises on any call (proves "absent config performs zero calls"); sabotage the fix and
  expect RED (proves a control bites). Put these four in every reviewer brief.
- **Pre-read then final**: review substance on the un-rebased SHA while the queue moves, then a
  final ancestry+gates pass on the rebased SHA; a marshal can skip the final for a ledger-only
  rebase when the reviewer already approved and the packaging gate re-proves G14/G15.
- **A stale cached gate copy misreports for a whole night**: the reviewer cited a 3.17.6 cache
  (no G15, a spurious G3 FAIL) until asked which copy it ran; name the canonical gate path in the
  reviewer brief, and treat a FAIL that main itself shows as a copy-drift question first.
- **Per-seat cwd + shared stash**: a linked worktree shares the primary's stash store; a seat's
  `git stash pop` popped the owner's uncommitted work (caught). Rule: no `git stash` in a linked
  worktree; scratch commits or a temp branch instead (guard hook tracked).

## Board clear 2 (adia-harness 2026-09-02, PRs #231 to #241): small addenda

- **Assign version slots at dispatch AND tell the seat "if main passed it, take the next free
  patch"**: three seats still landed on one slot (0.6.51, 0.6.61) because they read main at
  different moments. Landing lowest-first and rebumping the rest costs one ledger rebase each;
  it is the cheapest correct outcome, do not fight it.
- **A worktree's staleness is the reviewer's, not the builder's, to tolerate**: give the
  reviewer the pushed SHA and let it build a detached scratch worktree when the seat's tree has
  diverged; never rebase a seat's worktree while a review is mid-run on it (moved HEAD aborts
  the pass).
- **Body-only adapter sync**: copying root SKILL.md over the adapter clobbers adapter-only
  frontmatter (disable-model-invocation, user-invocable, argument-hint). Sync the body under the
  frontmatter, never the file; validate_cross_harness reports description drift and body drift
  separately, so a byte-identical body with intact frontmatter is the target.
- **A lint phantom is fixed by naming**: release_gate's G8 flagged `milestone-close` in prose as
  a missing skill; the namespaced citation form (`adapter_ci:milestone-close`) is what the gate
  exempts. Fix the citation, do not allowlist.
- **Close-by-keyword is literal**: three tickets stayed open after their PRs merged because the
  body said "Fix #N" in prose but carried no `Closes #N` line. The merge step closes the ticket
  by id regardless, and the brief demands the `Closes` line.

## Surfaces of record (adia-harness SPEC v1.8.0, 2026-09-02): what a plugin repo keeps where

Owner ruling after living with mirrors: "move away from managing mirrored files". One job per
surface, verified by gates:
- **Root README** is the only hand-maintained operator doc (install both harnesses, getting
  started, filing, the generated inventory block). The standalone INVENTORY.md copy retires; the
  freshness gate covers one output and fails on a leftover copy.
- **Plugin README** shrinks to identity + one pointer up + compendium reading order + a release
  POINTER. The release ledger lives in GitHub Releases (one release per merge already produces
  it); the harness gate's ledger/mention checks read Releases or the newest tag and the ROOT
  README's inventory fence (kimgranlund/claude-plugins#1019), so retiring ledger prose cannot
  regress the docs check. Retiring prose that incidentally mentioned every script DID regress it
  (45 G10 warns) until the gate learned the root fence; padding the plugin README back is the
  wrong fix.
- **Wiki** = generated pages that exist as no repo file (Plan from the board, Releases, Skills by
  phase, Roles, Home with LINKS to the compendium), never a mirror of a file; a page byte-equal to
  a repo file is a team-init WARN.
- **Projects + Milestones** hold plan and roadmap state; the plan/roadmap doc retires to git
  history and a gate fails uncited dated future items in docs.
- Tags carry the plugin prefix (`adia-sdlc-v0.6.78`): any ledger reader must extract
  `v?X.Y.Z` after an optional prefix and be fixture-tested with a real prefixed tag; a bare-`v`
  strip passed every mock and failed live.
- A live smoke that "closes" what it created is not cleanup: delete, then assert by a fresh
  read that the throwaway is gone.

## PR CI shape (adia-harness #268, 2026-09-02)

- **One PR workflow, family workflows off pull_request.** Seven runs per PR were six copies of the
  same selftests plus a review; now `pr.yml` (paths-filtered) runs the reusable `gates.yml` via
  `uses:` plus the Claude review, with `concurrency: pr-<n>` cancel-in-progress. Keep the
  reusable workflow governed repos pin by tag; drop only its own `pull_request` trigger. A
  `workflow_shape.py` gate holds the invariant (byte-identical .github twins, only `pr.yml` on
  pull_request) with a planted-trigger negative control.
- **Review skip on generated-only diffs**: classify the changed set in a first job; manifests,
  plugin.yaml, HARNESS-NOTES, plugin README only = skip the model review; any other path = review.
  A root README change counts as "review" (false negative toward more review).
- **The harness release gate is a local ship-time gate, not CI**: CI never had the harness plugin
  installed; do not wire an installer for it into the org's PR gate.
- **Tool resolution reads the cache, the marshal reads repo-main**: `resolve-tool` picks the newest
  CACHED harness, so seats lag an unshipped harness fix until it ships; the marshal's own gate path
  is the repo-main checkout. Either ship the harness promptly or declare `toolchain.<tool>` per
  repo; never let the two verdicts disagree silently.
- **Relay SHAs by copy, never by ear**: a builder mistyped its own long SHA in a report; verify
  every SHA against `gh pr view --json headRefOid` before briefing a reviewer.
- **A locked record contradicted by a change gets a dated append-only note in the same PR**
  (LLD "gates.yml runs on pull_request"), never a silent edit and never left stale.

## Learnings, 2026-09-03 sweep (#267, #270)

- A version-slot assigner that reads only `main` collides when two PRs are open at once: #272
  took 0.6.82 while #271 already held it. Consult open PR heads (or the queue's assigned slots)
  before minting; until then the marshal rebumps the later-landing PR (adia-harness #273).
- An append-only queue with first-match `done` strands the fresh entry after a force-push; every
  queue that stores a SHA needs an in-place `update` op (merge_queue has one since #270,
  review_queue tracked as #274).
- A ruleset that blocks force-push on `*` makes every feature-branch re-push a logged bypass;
  scope force-push protection to the default branch only.
- A reviewer whose scratch worktree is pruned mid-review must re-pin against the final head and
  diff PR-owned files old-vs-new before reusing any evidence.
- Slot order is landing order: when a higher-slot PR is reviewed first, hold it; each landing
  costs the next PR one rebase whose conflicts are only generated/version-stamp files, resolved by
  regenerating, never hand-merging. Reviewer diffs PR-owned files old-vs-new head and re-pins
  before the final verdict; content review can start before the rebase.
- A reviewer's scratch worktree under /tmp still registers in the primary's worktree list; prune
  after each merge.
- Pin the merge to the approved head: `gh pr merge --squash --match-head-commit <sha>`. A builder
  amend between the head check and the merge landed a different tree once (adia-harness #290);
  the authz record must name the sha that actually merged (append a superseding record, never
  edit).
- Tell a seat FREEZE means no further pushes: an em-dash fix pushed after the PR was handed to
  review is a new head and a new review.
- A subagent calling EnterWorktree rebinds the parent session's cwd and every sibling seat with it
  (seen as "primary edits" and "refusing to run it" from other seats). Dispatch briefs must say:
  never EnterWorktree/ExitWorktree; `git worktree add` + `git -C` + absolute paths only. If it
  happens, the marshal runs ExitWorktree(keep) and the seats resume.
- Head-to-head diffs after a rebase include everything main gained in between; compare PR-owned
  paths only (or three-dot against the fork point) before calling a rebase content-identical.
- W14 shape that worked: SPEC amendment by a design seat, fast-forwarded to main; tickets chained
  by Blocked-by; one release per PR; the marshal merges with --match-head-commit; every ticket
  label is small|big (spec-lock's set), never medium.
- A repo-wide prose sweep is a script with a matching check (one scope filter for both), an explicit
  skipped list (locked records, generated files, syntax-bearing assets, counted fixtures), and a
  reviewer re-derivation (re-run the rule over the old tree and diff against the commit).
