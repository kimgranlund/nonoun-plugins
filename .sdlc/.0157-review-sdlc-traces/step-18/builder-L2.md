<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/review-traces/SKILL.md` (new): contains the frontmatter, the Codex host line, the `SDLC_ROUTING_REASON` line, and the review task dir setup. It has `## 1. Ingest and detect` and `## 2. Diagnose` with the ```` ```cluster-question ```` template, plus placeholder sections 3 to 5.

## Checks
- `head -1 ... | grep -qx -- '---'`: pass
- `grep -q '^name: review-traces$'`: pass
- `grep -qF '../sdlc-lite/SKILL.md'`: pass
- `grep -qF 'archaeologist L1'` and `grep -qF 'scout L1'`: pass
- `grep -qF 'clusters --max'`, `traces.py ingest`, `traces.py detect`: pass
- awk over the cluster-question fence, then `grep -q '^## Question$'`: pass
- awk over the cluster-question fence, then grep for the "Read only the evidence paths listed above; nothing else." sentence: pass
- `grep -qF 'SDLC_ROUTING_REASON'`: pass
- (guard) scope test against `SDLC_BASE_SHA=7334f49`: pass

All criteria ran in one chained command that printed ALLOK. The guard printed GUARDOK.

## Notes
Sections 3 (Verify), 4 (Propose), and 5 (Report and file) are placeholders. Steps 19 to 21 fill them in.
