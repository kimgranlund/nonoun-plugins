# Release 0.19.0

Recorded: 2026-09-29. SDLC Lite 0.19.0 and Progressive Context 0.1.2. Previous release: SDLC Lite 0.18.0 (cd6db5c).

## What changed for consumers

| Change | Ticket | Built and verified |
| --- | --- | --- |
| New `onboard` skill and `scripts/onboard.py`: sets up or checks root and `docs/` entry files and `docs/layout.md`, with managed blocks that keep user content byte-identical | T-0160 | /chain, five steps plus loose ends, live run on both hosts |
| Planner writes a `### Read first` subsection per step naming the nearest `AGENTS.md` above each changed file; builder and verifier read it; `steps.py lint` checks the paths; `/fix` and `/chain` handwritten steps carry it | T-0162 | /chain, six steps, live run on both hosts, all eight arms |
| Codex defaults: `gpt-6-sol` replaced by `gpt-6-astra`; the verifier's alternate model is configured in `models.json` (`verifier_alternates`), and with none configured the verifier shares the builder's model and the run records it | T-0163 | /chain, two steps; live Codex run under T-0162 |
| `/fix` lints the step handoff it wrote, not the task folder | T-0164 | /fix fast lane |
| Conductor: planner, builder, and verifier work runs only through `run.sh`; other plugins' agents are never substitutes | T-0165 | /fix fast lane, live probe recorded |
| `/fix` unattended: never push or open a pull request; report what waits | T-0168 | /fix fast lane |
| `check.py` guards for each rule above, each with a negative control | T-0164, T-0165, T-0168, T-0162 | with the tickets |
| Progressive Context `references/sdlc-lite.md` names the `onboard` skill | T-0160 | with T-0160 |

Every role behavior change above was built by a builder role and checked by an independent verifier role through `scripts/run.sh`.

## Known limits

- `gpt-6-luna` (scout L1 on Codex) is rejected on a ChatGPT account, like `gpt-6-sol` was. Left as is by the user's decision; see T-0163.
- With no `verifier_alternates` configured, Codex verification is not model-independent. The run records it.
- The conductor routing probe did not reproduce the reported bypass with either 0.18.0 or this version (`docs/validation/role-routing-probe.md`). Hook enforcement is T-0166, not in this release.
- Open tickets deferred past this release: T-0161 (reorganization spike), T-0166, T-0167, T-0169, T-0170.

## Checks run for the release

Filled in at release time; see the release commit.
