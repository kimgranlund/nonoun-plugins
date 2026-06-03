# Changelog — adia-ui-dogfood

## [0.1.0] stable — 2026-06-03

**MINOR** — first cut as a plugin skill. Ported from the framework monorepo's maintainer skill `dogfood-sweep`, renamed and de-repo'd: absolute paths stripped, shared-infra references rewritten to `${CLAUDE_PLUGIN_ROOT}/...`, the component visual probe bundled at `scripts/analyze.mjs` (repo-root resolved from `$ADIA_REPO_ROOT` / cwd, not a path relative to the install), instance data dropped. No procedural changes to the 6 modes.

SKILL.md carries all 6 modes inline (component visual probe / app-shell QA / HTML typo sweep / native-primitive leak / admin-shell composition / component anatomy + card header), with a cold-start triage menu, §Plan-Execute-Verify, §SelfAudit, §Teach, and §FileMap added to match the rollup-family conventions. Modes 2 / 4 / 5 drive **repo-local** audit scripts that ship in the monorepo (`scripts/dev/audit-app-shells.mjs`, `audit-native-primitive-leak.mjs`, `audit-shell-composition.mjs`); modes 3 / 6 use inline shell snippets.

### Reconstructed history (pre-port)

- Added probe #6 (missing component CSS detection) to mode 1 after the swap-to-primitive-but-forget-the-link class slipped past a real PR. The bug class: an agent uses `<button-ui>` markup but forgets the `<link rel="stylesheet">` for the button component CSS; the element registers, the markup looks right, and the control renders unstyled.

- Native-primitive-leak audit (mode 4) intent-marker detection window widened from 80 → 200 chars after a peer agent found that realistic preceding-line comments (indent + comment prefix + reason text + closing `-->` + newline) sat at exactly the 80-char boundary and were not detected.

- Mode 6 (Component Anatomy + Card Header Sweep) added: card-ui `<header><div>` wrapper anti-pattern + missing anatomy sections per the anatomy-sweep gate's expectations.

- Mode 1 (component visual probe via Chromium) was the initial skill. Modes 2–5 were absorbed from the substrate-side `scripts/dev/audit-*.mjs` work over multiple cycles. The skill grew its 6-mode catalog organically.
