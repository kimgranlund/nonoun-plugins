---
name: system-atlas
description: >-
  Draws a whole system as large workflow diagrams from two directions and publishes them as one
  full-width artifact: an inventory of its machinery (skills, agents, commands, rules, hooks,
  checkers, evaluators, verifiers, ontologies, knowledge bases), a machinery map, journey marks,
  an enforcement matrix saying which rules are actually enforced, and findings. Use when asked to
  map, diagram, atlas or explain how a repo, plugin, pipeline or agent system works, when
  onboarding onto an unfamiliar codebase, or when auditing whether the rules a project states are
  enforced anywhere. NOT a file-tree or dependency-graph diagram; NOT prose architecture docs;
  NOT a design-system page (it carries its own visual contract in DESIGN.md).
---

# system-atlas

An atlas draws a system twice and reports where the two drawings disagree.

- Outside-in starts from an actor and a goal: what they touch, wait on, decide, and what can go
  wrong for them.
- Inside-out starts from a component and its state: who owns it, which states exist, what crosses
  which boundary, what is never allowed.
- Cross-check: every outside-in step must land on an inside-out node, and every inside-out
  boundary must surface somewhere an actor can see it. Each mismatch is a finding, not a fix.

Every section's eyebrow names its perspective. `scripts/atlas_check.py` fails a page where one
does not.

## No instructions given

Scan the repo first, so the recommendation is earned, then make ONE `AskUserQuestion` call with
these four questions, recommendation first in each:

1. Subject: Project, Harness, Repo, Whole system. The detected one goes first, marked recommended.
2. Playbook: Overview (recommended), Onboarding, Audit, Trace one flow.
3. Reader: me, a new contributor, a reviewer or stakeholder. This sets how much vocabulary is
   explained.
4. Size: 5, 9 (recommended), 12 diagrams.

Then:

- Trace gets one follow-up question listing the flows found in the inventory.
- A dismissed ask proceeds on the recommended answers, and the scope line says so.
- Any instruction already in the request skips the question it answers. Never ask something the
  user has told you.
- Whole system budgets by detection: harness-heavy is Harness 5, Repo 3, Project 2; a product
  repo with a thin harness is Project 6, Repo 3, Harness 1 to 2. The Repo change journey is
  always included.
- The inventory and the findings run across all subjects whatever the playbook.
- The page opens with a scope line under the header: subject, playbook, reader, size, what was
  skipped. Title is `<Repo name> Atlas`, footer names the sha, and a rerun on the same repo
  updates the same artifact by its URL.

`references/playbooks.md` has the six playbooks, their default diagram lists, the detection
markers and the reader and size rules.

## Procedure

0. Inventory by machinery kind before drawing anything. Walk the detection globs in
   `references/machinery-kinds.md`, one pass per kind, and record every item with its evidence
   path. Then place every stated rule on the enforcement ladder in
   `references/enforcement-ladder.md`. The inventory is what the diagrams are drawn from.
   Reconcile before you place anything low. When a scout reports "none found" for a rule's
   enforcer, that is a claim carried by one evidence path, not a finding. Before the rule goes on
   rung 2 or lower, search the checks inventory (hooks, git hooks, checkers, evaluators,
   verifiers) for the rule's key terms and for the path of the file it governs. Only when the
   checks inventory also shows nothing does "none found" become a finding. On the first real run
   of this skill, the rules scout reported no enforcer for two rules the hooks-and-checks scout
   had evidence for.
1. Harvest as many concepts as the chosen size, 5 to 12, each worth a canvas. Read README, agent and skill files, scripts, hooks,
   config. Each concept needs two independent evidence paths (`references/evidence-rules.md`).
   Fan scouts out per area when the system is large; they return paths and facts, you decide.
2. Split the concepts between the two perspectives and pick a diagram kind per concept from the
   fixed table in `references/diagram-kinds.md`. Lifecycle is a state diagram, handoffs are a
   sequence diagram, gates are a flowchart, one-door adapters are a hub.
3. Draft each diagram under `references/mermaid-rules.md`: verbs on edges, human touchpoints
   shown, failure paths shown, at most 14 nodes per canvas, subgraph means ownership, dashed
   means dispatch, thick means result. Kinds are told apart by shape and a mono prefix, never by
   color.
4. Source-truth check BEFORE drawing the page. Take every node and edge label and name the file
   it came from. A label with no file is cut, or kept and marked intended rather than observed.
   The first atlas ever drawn was partly drawn from memory; that is the failure this step exists
   to stop.
5. Assemble and publish. Write one `atlas.json` beside the work, then run
   `python3 scripts/atlas_build.py atlas.json page.html`. Never hand-assemble the page: the
   assembler drops the example section, builds the nav, escapes every diagram, emits the three
   table sections, fills every placeholder, and runs `atlas_check.py` for you, exiting with its
   code. Generated pages embed the pinned Mermaid renderer and work offline, including `file://`.
   Before publishing, open the result in a browser and confirm every diagram becomes SVG and
   the viewer opens and restores it. The structural checker cannot prove browser execution.
   Do not rely on an artifact host to render Mermaid. `assets/atlas.example.json` is the input shape;
   `assets/section-block.html` and `assets/table-section.html` are what it emits, and are read
   only when the contract itself needs changing. The assembler refuses, before writing anything,
   a perspective that is not Outside-in or Inside-out, a section without exactly 3 rules, and a
   sections count that disagrees with `scope.size`. Fix every failure it names, then publish with
   the Artifact tool. On a rerun, find the prior artifact with the Artifact tool's list action,
   matched by title, and publish to that URL instead of making a second one. Obey `DESIGN.md` for
   every visual decision and `references/mermaid-class-map.md` for the diagram theming.
6. Staleness. The atlas is stale the moment any source path it cites changes past the footer sha.
   Say so in the handoff and put the sha where a later reader will find it.

## Outputs

Five, all of them, in the page or in the handoff beside it:

1. Inventory: count per kind, every item with its evidence path.
2. Machinery map: one inside-out diagram, kinds as lanes, who invokes whom, who writes which
   record.
3. Journey marks: on each outside-in step, which kinds fire.
4. Enforcement matrix: every rule against its rung, its enforcer, and for a judged check its
   independence and whether its control can fail.
5. Findings: the list in `references/enforcement-ladder.md`, starting with a rule nothing
   enforces and a check whose control cannot fail.

## Stop rules

- Stop and ask when the system has no discernible actor: an atlas without an outside-in
  perspective is half a deliverable, and the owner may want a different artifact.
- Stop drawing a canvas at 14 nodes. Split the concept instead of shrinking the type.
- Do not publish a page `atlas_check.py` fails. The failures are contract breaches, not style
  notes.
- Do not report a claim carried by one evidence path. Mark it intended and move on.
- Do not invent an enforcer. A rule with no hook, checker, evaluator or verifier behind it is a
  rung 2 rule and a finding.

## Reference files

Read each when its step comes up, not before.

| File | Read it |
|---|---|
| `DESIGN.md` | Before writing or editing any page CSS. The visual contract, D1 to D12. |
| `references/playbooks.md` | Before the ask, to pick the recommendation, and again when filling the diagram list. |
| `references/machinery-kinds.md` | At step 0, the inventory pass. Globs, fields, shapes, prefixes. |
| `references/enforcement-ladder.md` | At step 0 and again at the enforcement matrix and findings. |
| `references/perspective-questions.md` | At step 2, to decide which perspective a concept belongs to. |
| `references/diagram-kinds.md` | At step 2, picking the diagram type and the shape per kind. |
| `references/mermaid-rules.md` | At step 3, while drafting every diagram. |
| `references/mermaid-class-map.md` | When a diagram kind paints wrong, or when adding a new kind. |
| `references/evidence-rules.md` | At steps 1 and 4, and before writing any finding. |
| `references/anti-patterns.md` | At step 3 and again before publishing. |
| `assets/atlas.example.json` | At step 5, to see the input shape `atlas_build.py` takes. |
| `assets/page-template.html` | Only to change the visual contract. `atlas_build.py` fills it. |
| `assets/section-block.html` | The concept section the assembler emits. Read it to change that shape. |
| `assets/table-section.html` | The three table sections (inventory, matrix, findings) and their fixed header rows. |
| `assets/viewer.js` | Only if the inlined viewer in the template needs repair. |
