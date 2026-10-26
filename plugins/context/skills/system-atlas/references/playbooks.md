# Playbooks

Six playbooks. Subjects are Project, Harness, Repo, or Whole system. Lenses are Overview,
Onboarding, Audit, Trace. Playbooks 1 to 3 are the Overview lens on one subject; 4 to 6 are
lenses applied to whichever subject was chosen.

| # | Playbook | Answers | Lean |
|---|---|---|---|
| 1 | The Project | what does the product do | balanced |
| 2 | The Harness | what machinery surrounds the work | inside-out |
| 3 | The Repo | how does a change travel | outside-in |
| 4 | The Onboarding | what does my first hour look like | outside-in, heavy |
| 5 | The Audit | are the stated rules enforced | inside-out, findings first |
| 6 | The Trace | what happens when X | one scenario end to end |

## Default diagram lists

1. The Project: actors and entry points; runtime topology; entity lifecycle; data and contract
   flow; one-door boundaries; failure and recovery.
2. The Harness: machinery map with kinds as lanes; who dispatches whom; the enforcement ladder;
   the check gates; vocabulary and records.
3. The Repo: contributor journey; branch to review to CI to release; where records get written;
   what blocks a merge.
4. The Onboarding: install to first success; what I touch and what I wait on; where I get stuck
   and who unblocks me; the five terms I must know.
5. The Audit: the enforcement matrix as the hero; one diagram per unenforced rule; verifier
   independence; checks that cannot fail.
6. The Trace: a single flow drawn outside-in, then the same flow inside-out, with every
   machinery kind that fires marked on it.

Folded in, never their own playbook: Data lives inside The Project, Release lives inside The
Repo or is a Trace of a release. A candidate seventh, Before and After (today against a
proposal), is not built.

## Subject detection

- Harness markers: `.claude/`, `CLAUDE.md`, `AGENTS.md`, `skills/`, `agents/`, `hooks/`,
  `plugins/`, `.mcp.json`.
- Project markers: source dirs with a runtime, a package or build manifest, data stores, servers,
  entry points.
- Repo markers are assumed: any git repo has a change journey.

Weigh by volume and by what the README spends its words on. The detected subject is the one
recommended in the ask.

## Whole system budget

| Detection | Project | Harness | Repo |
|---|---|---|---|
| Harness-heavy repo | 2 | 5 | 3 |
| Product repo with a thin harness | 6 | 1 to 2 | 3 |

The Repo change journey is always included, whatever the split. The inventory and the findings
run across all subjects whatever the playbook is.

## Reader and size

Reader sets how much vocabulary is explained: me (terse, no glossing), a new contributor (every
term expanded on first use, the five-terms diagram earns its place), a reviewer or stakeholder
(terms glossed once, findings and the enforcement matrix up front).

Size is 5, 9 or 12 diagrams. Under a smaller size, cut whole concepts from the bottom of the
playbook's list; never shrink a concept below the perspective it was chosen for.

## Scope line

The page opens with one: subject, playbook, reader, size, what was skipped. Title is
`<Repo name> Atlas`, the footer names the sha, and a rerun on the same repo updates the same
artifact by its URL.
