<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- docs/reports/ticket-root-router-live-run.md: in the Fresh role section, the `Result:` line now reads `Result: unverified: <two reasons>` instead of `Result: verified`. The "Router read" observation now opens with "not through the `router:` line" instead of "yes".
- docs/README.md: unchanged in this attempt. The previous attempt's list item stays.

## Checks
- `test -f docs/reports/ticket-root-router-live-run.md && grep -qE '^Recorded: [0-9]{4}-[0-9]{2}-[0-9]{2}\.' ...`: exit 0
- `grep -qF '(validation/ticket-root-router-live-run.md)' docs/README.md`: exit 0
- Scripted run grep chain (`## Scripted run`, `- proposed: 1`, `- ready: 1`, `- done: 1`, `ticket_root: tickets`): exit 0
- Fresh role grep chain (`## Fresh role`, `^Result: (verified|unverified: .+)$`, `## Limits`): exit 0
- (guard) changed-file allowlist with SDLC_BASE_SHA=604d7ccb1c2887748ba322c8e4fc53284f21cd52: exit 0
- `git diff --check`: clean. Em dash count in the doc: 0.

## Notes
- No re-run was done, as the verifier directed. The two reasons on the `Result:` line come from the doc's own observations:
  - The router reached the role through nested-memory loading, not through the handoff's `router:` line.
  - The `, claimed by` state was reproduced only by replay.
- I also changed the "Router read: yes." bullet to "Router read: not through the `router:` line." Without that, the bullet contradicted the new `Result:` line. The rest of that bullet is unchanged.
