---
name: decompose
description: Break a scoped problem into parts along two independent planes, outside-in (whole to parts, the structure) and inside-out (actions to surfaces, the behavior), then prove they cover each other with scripts/coverage_check.py. Use when breaking down a technical or UX architecture, a goal, or a system; when a breakdown has structure with no behavior; or when acceptance criteria map to no task. NOT for greenfield decisions still unmade (/grill first); NOT for a concrete screen layout.
argument-hint: <handoff.md | what to decompose> [--plan] [--strict]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/skills/decompose/scripts/coverage_check.py:*)
---
Arguments: `$ARGUMENTS`

A one-direction breakdown hides the other direction's failure. Run both planes independently and let the script find the gap. Depth: `references/method.md`, `references/foundations.md`, `references/best-practices.md`; grade with `references/rubric.md`.

## The crossing

| | has a node (outside-in) | no node |
|---|---|---|
| has an action (inside-out) | load-bearing | UNHOSTED: a need with nowhere to live |
| no action | UNJUSTIFIED: decoration, unless it carries a `justify` | n/a |

## Modes
- default: both planes, manifest, gate.
- `--plan`: the manifest feeds /plan, so every leaf needs an `accept` predicate (gate code NO-ACCEPT). Use this inside /chain.
- `--strict`: advisories (UNJUSTIFIED-LEAF, EDGE-UNJUSTIFIED) block too.

## Steps
1. Read the task handoff and any `design.md`. Pick the domain reference for each plane's vocabulary and stop rule: `references/{layout,components,technical-architecture,ux-architecture,goals}.md`; none fits → copy `references/_template.md`.
2. Outside-in: a node tree. Mark leaves. Give every pure-structure node a `justify` (`affordance`, `grouping`).
3. Inside-out, without looking at the tree: the action set (verbs, needs, capabilities). Reading one plane off the other passes the gate trivially and finds nothing.
4. Map each action to the node(s) hosting it. Add `edges` only for a real build-order dependency; the default is parallel.
5. Write `.sdlc/<slug>/decompose/manifest-v1.json` (schema below) and run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/decompose/scripts/coverage_check.py <manifest>` (add `--strict` in strict mode). Never eyeball coverage.
6. Fix every UNHOSTED, DANGLING, EDGE-DANGLING, EDGE-CYCLE, and (plan mode) NO-ACCEPT; resolve each advisory by hosting an action, adding a `justify`, or deleting. Rerun until exit 0.
7. Every ratified decision in `design.md` must map to an action. The script cannot see a decision nobody wrote as an action; this is a judgment step.
8. A manifest handed to /plan is versioned: a replan writes `manifest-v<n+1>.json` with the diff and reason, never an in-place edit.

If the work will fan out to parallel builders: one writer per file, shared or barrel edits in one serial integration slice, a serial prep slice before a wide fan-out (`references/best-practices.md`).

## Manifest schema

```jsonc
{
  "domain": "technical-architecture",
  "plan": true,
  "nodes":   [{ "id": "n1", "label": "submit bar", "leaf": true, "justify": null,
                "accept": "`pnpm test submit-bar` exits 0" }],
  "actions": [{ "id": "a1", "label": "submit the form" }],
  "hosts":   [{ "action": "a1", "node": "n1" }],
  "edges":   [{ "from": "n2", "to": "n1", "why": "n1 renders the schema n2 pins" }]
}
```

## Report
Write `.sdlc/<slug>/decompose/report.md`, add `Decomposition: decompose/report.md` under the handoff's Context, and reply with the first two lines:

```
Manifest: <path> (<domain> · <mode>) · coverage_check: <clean | codes>
Quadrant: <load-bearing | unhosted actions | unjustified structure | both broken>
Outside-in: <findings: MECE gaps, granularity, unjustified structure>
Inside-out: <findings: unhosted needs, actions that name solutions, missing accepts>
Hand-off: /plan
```

Done when: the checker exits 0 in the chosen mode, the planes were derived independently, and the report names the quadrant. Not done: coverage eyeballed, one plane read off the other, or a handed-off manifest edited in place.
