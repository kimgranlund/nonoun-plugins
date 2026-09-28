<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
plugins/sdlc-lite/skills/ticket/templates/feature.md: new template
plugins/sdlc-lite/skills/ticket/templates/chore.md: new template
plugins/sdlc-lite/skills/ticket/templates/bug.md: new template
plugins/sdlc-lite/skills/ticket/templates/spike.md: new template
plugins/sdlc-lite/skills/ticket/templates/idea.md: new template
plugins/sdlc-lite/skills/ticket/SKILL.md: new /ticket skill

## Checks
`ls plugins/sdlc-lite/skills/ticket/templates/` — lists exactly bug.md chore.md feature.md idea.md spike.md: pass
Per-template `grep -c '^id: T-0000$'`, `grep -c '^title: ""$'`, `grep -c '^created: YYYY-MM-DD$'` each print 1, and `grep '^type:'` shows the file's own type: pass, all 5 templates
`grep -n 'gen-ui\|svelte\|Panda' plugins/sdlc-lite/skills/ticket/templates/*.md`: prints nothing (exit 1): pass
SKILL.md contains `name: ticket`, the tickets.py allowed-tools entry, and a "Never hand-edit `.sdlc/roadmap.md`" line: pass
`plugins/sdlc-lite/scripts/check.sh`: exits 0, includes `ok: plugin validate`: pass

## Notes
`scripts/tickets.py` does not exist yet (out of scope for this step; Step 2 per the handoff). The SKILL.md references it as designed, consistent with the handoff's staged plan.
