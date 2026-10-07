## Goal
The onboard selftest fails when the marker hash is computed wrongly.

## Context
Found by the filer on T-0160 (`.sdlc/.0160-repo-onboarding-skill/filer-L1-2.md`, Follow-ups): a mutant of the hash function in `plugins/sdlc-lite/scripts/onboard.py` survives, because the gates only compare a marker with the text it was computed from. The design (`docs/specs/repo-onboarding/design.md`, Upsert behavior) defines `<H>` as the first 12 hex characters of the SHA-256 of the block text, with line endings normalized to LF.

## Constraints
Only `plugins/sdlc-lite/scripts/onboard.py` changes. Keep every existing gate.
