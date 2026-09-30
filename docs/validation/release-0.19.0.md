# Release 0.19.0

Recorded: 2026-09-29. SDLC Lite 0.19.0 and Progressive Context 0.1.2. Previous release: SDLC Lite 0.18.0 (cd6db5c).

## What changed for consumers

| Change | Ticket | Built and verified |
| --- | --- | --- |
| New `onboard` skill and `scripts/onboard.py`: sets up or checks root and `docs/` entry files and `docs/layout.md`, with managed blocks that keep user content byte-identical | T-0160 | /chain, five steps plus loose ends, live run on both hosts |
| Planner writes a `### Read first` subsection for each step whose changed files have a nearest `AGENTS.md` other than the root; builder and verifier read it; `steps.py lint` checks the paths; `/fix` and `/chain` handwritten steps carry it | T-0162 | /chain, six steps, live run on both hosts, all eight arms |
| Codex defaults: `gpt-6-sol` replaced by `gpt-6-astra`; the verifier's alternate model is configured in `models.json` (`verifier_alternates`), and with none configured the verifier shares the builder's model and the run records it | T-0163 | /chain, two steps plus loose ends; live Codex run under T-0162 |
| `/fix` lints the step handoff it wrote, not the task folder | T-0164 | /fix fast lane |
| Conductor: planner, builder, and verifier work runs only through `run.sh`; other plugins' agents are never substitutes | T-0165 | /fix fast lane, live probe recorded |
| `/fix` unattended: never push or open a pull request; report what waits | T-0168 | /fix fast lane |
| `check.py` guards for each rule above, each with a negative control | T-0164, T-0165, T-0168, T-0162 | with the tickets |
| Progressive Context `references/sdlc-lite.md` names the `onboard` skill | T-0160 | with T-0160 |

Every role behavior change above was built by a builder role and checked by an independent verifier role through `scripts/run.sh`.

## Known limits

- `gpt-6-luna` (scout L1 on Codex) is rejected on a ChatGPT account, like `gpt-6-sol` was. It was not part of the T-0163 decision and is still pending a user decision (`docs/codex-role-execution.md`, T-0163 follow-ups in `.sdlc/notes.md`). Codex scout runs fail on such an account until then.
  Correction, 2026-09-30: this limit held on Codex CLI 0.154.0. On CLI 0.159.2 `gpt-6-luna` completes live turns on that account, and the scout is on `gpt-6-luna` again (`docs/validation/codex-account-models-2026-09-30.md`).
- With no `verifier_alternates` configured, Codex verification is not model-independent. The run records it.
- The conductor routing probe did not reproduce the reported bypass with either 0.18.0 or this version (`docs/validation/role-routing-probe.md`). Hook enforcement is T-0166, not in this release.
- A project that installed 0.18.0 Codex agents and then runs `codex_roles.py install` for 0.19.0 keeps the three `sdlc-verifier-lN-alternate.toml` files from 0.18.0 (one pinned to `gpt-6-sol`). They are outside the receipt and the generated `.gitignore`, `install --check` reports the agents current, and the runner never selects them while no alternate is configured. Remove them by hand.
- Open items deferred past this release: the `gpt-6-luna` scout default, T-0161 (reorganization spike), T-0166, T-0167, T-0169, T-0170.

## Checks run for the release

Run on branch `release-0.19.0` on 2026-09-29, from the repository root, all exit 0:

- `bash plugins/sdlc-lite/scripts/check.sh` (shellcheck skipped, not installed)
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `git diff --check main -- . ":(exclude).sdlc"`
- Version parity across each plugin's Claude and Codex manifests

An independent verifier (L3, `.sdlc/release-0.19.0/step-1/`) reran these guards, showed each can fail by injecting a defect in a throwaway worktree, checked every ticket's builder and verifier results, and exercised the `onboard` skill in a temporary repository. Its first pass failed on this record's wording about `gpt-6-luna` and the empty checks section; both are corrected above.
