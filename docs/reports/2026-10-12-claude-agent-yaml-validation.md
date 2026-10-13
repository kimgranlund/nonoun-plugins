# Claude agent YAML validation (T-0503)

Date: 2026-10-12. Fixes finding F1 of the [Astra review](2026-10-12-sdlc-lite-astra-review.md).

## Change

- `claude_roles.py` decodes the source description once and serializes the complete value (role text plus level suffix) as one double-quoted YAML scalar.
- `agents/conductor.md` description is now a quoted scalar.
- `check.py` parses every `agents/*.md` frontmatter with PyYAML, requires non-empty `name` and `description`, and carries a rejecting fixture (text after the closing quote, unquoted colon-space) plus a passing quoted fixture.

## Observed

| Check | Result |
|---|---|
| Baseline `builder-L2.md` and `conductor.md` (from HEAD) through `yaml.safe_load` | both rejected |
| `probes.py` after the change | agents count 34, invalid 0; skills count 38, invalid 0 |
| `claude_roles.py selftest`, both `generate --check`, `check.py`, `check-packaging.py` | pass |

## Unverified

Acceptance criterion 5 (a fresh Claude session discovers the generated agents and completes one prepared scout dispatch in a throwaway project) was not run: the lane is unattended and has no live host session. Only the YAML format is established; agent-loading impact stays unverified.
