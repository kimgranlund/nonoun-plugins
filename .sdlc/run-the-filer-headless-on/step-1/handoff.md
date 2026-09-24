level: L1

## Do
Nothing to build. This step is a spike: the conductor ran the filer headless and recorded results in `.sdlc/run-the-filer-headless-on/evidence.md`. Check that the evidence is true by reproducing it independently.

## Acceptance criteria
1. `.sdlc/run-the-filer-headless-on/fresh-filer-L1.md` is a real filer output (has ## Warnings, ## PR title, ## PR body, ## Changelog entry, ## Follow-ups) and its Follow-ups section is only top-level `- ` bullets, one line each, or exactly `None`.
2. Copy that file as `filer-L1.md` into a temp ticket root next to a ticket-front-matter `handoff.md` with `status: ready` (outside the repo, e.g. mktemp -d), run `python3 plugins/sdlc-lite/scripts/tickets.py --root <tmp> close <slug>`: exits 0 and creates one proposed idea ticket per bullet.
3. Negative control: the same with Follow-ups rewritten as a prose sentence: exits nonzero and writes no ticket.
4. Every `.sdlc/*/filer-L*.md` in the repo passes tickets.py's own `section`/`is_none`/`bullets` check (Follow-ups is None or has at least one bullet); counts match evidence.md.
5. No file under `plugins/` changed (`git status --short plugins/` is empty).

Do not modify anything under the repo; use temp dirs only.
