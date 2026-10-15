---
id: T-0568
title: "Binary evidence lives in a user-scope cache, not in the repo"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0563]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Images, videos and other heavy run assets go to a user-scope cache outside the repo, so `.sdlc` and the repo hold only text records. Traces are kept, as text, only when they are valuable or the ticket asks for them.

## Intent
- Do:
  1. `wtroot.py evidence <ticket> [--cwd D]` prints, and creates, `<user cache>/sdlc-lite/<repo key>/evidence/<ticket>/`. The user cache is `$XDG_CACHE_HOME`, else `~/Library/Caches` on macOS, else `~/.cache`. `<repo key>` is the one `scratch` already uses. Unlike `$TMPDIR` scratch, it survives a reboot and is never swept.
  2. Roles and skills that write screenshots or other binary evidence (ui-designer, verifier evidence notes, the handoff-format and checks recipes) write them there and cite the path in the Outcome or notes. Traces are kept only when the ticket asks for them or a failure needs them, as text under the records dir.
  3. `tickets.py check` warns, exit 0, for each tracked binary file under `.sdlc/`, with the extension list `png, jpg, jpeg, gif, webp, mp4, mov, webm, zip, pdf`, naming the evidence command.
- Non-goals: moving existing evidence in consumer repos (each repo decides); tracked text traces.
- Done when: the criteria pass.

## Context
Maintainer decision 2026-10-15: "traces should be stored when valuable or the task suggests it. images and heavier assets would be in user scope somewhere in tmp or cache system". agent-ui tracks about 2000 PNGs (about 300 MB) under `.sdlc`. Scratch already lives at `$TMPDIR/sdlc-lite/<repo key>/` (`wtroot.py scratch`); the evidence store sits beside it in the user cache so it outlives a reboot.

## Constraints
No binary is written into the repo by a plugin role. Scratch sweep rules stay as they are.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/wtroot.py selftest` exits 0. Its new cases print `ok:`: the evidence path is under the user cache, honors `XDG_CACHE_HOME`, gives the same path from a lane, and is outside the repo.
2. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new case shows `check` warning on a tracked `.sdlc/x/shot.png` and staying silent on `.md`; the case failed before the change.
3. `grep -rn 'evidence' plugins/sdlc-lite/agents/ui-designer.md plugins/sdlc-lite/skills/handoff-format/SKILL.md` names `wtroot.py evidence`.
4. `bash plugins/sdlc-lite/scripts/run-selftest.sh` and `git diff --check` exit 0.

## Outcome

2026-10-15 · lane: full L2 · verdict: pass · verifier: verifier-L2 (sonnet) · base: ba2daeddeeb4
- Changed: wtroot.py evidence <ticket> gives a user-cache evidence dir; tickets.py check warns on tracked binaries under .sdlc
- Commits: 76cee53 T-0568: wtroot.py evidence puts binary evidence in the user cache; check warns on tracked binaries in .sdlc
- Check: 1 wtroot.py selftest exits 0 with new `ok:` cases: pass
- Check: 2 tickets.py selftest exits 0; new case warns on tracked `.sdlc/x/shot.png`, silent on `.md`; faile...: pass
- Check: 3 grep names `wtroot.py evidence`: pass
- Check: 4 run-selftest.sh and git diff --check exit 0: pass
- Follow-up: note: redck.py deviations printed no process deviation: lines; the... -> notes.md
- Follow-up: note: the 6 em dashes on added lines are all in regenerated... -> notes.md
- Follow-up: note: could not delete scratch under /var/folders/.../0568-verifier-L2 rm... -> notes.md
