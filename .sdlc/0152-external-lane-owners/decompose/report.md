Manifest: .sdlc/0152-external-lane-owners/decompose/manifest-v1.json (technical-architecture · plan) · coverage_check: clean
Quadrant: load-bearing
Outside-in: two owning files (tickets.py, fanout.py) grouped as non-leaf nodes so a fan-out keeps one writer per file; leaves are the units inside them plus three contract texts (fanout skill, ticket skill, internals doc). No unjustified structure: every leaf hosts an action. Granularity stop: one function or one docstring per leaf.
Inside-out: 23 needs drawn from the ask before reading the tree. Two needs the ask did not name surfaced as actions: idempotent-branch (a second ticket on the same external branch must not re-merge or re-gate) and surface-typo (a registered branch that matches no local ref would guard nothing silently). Both host cleanly. No action names a solution; every leaf carries an accept.
Hand-off: /plan
