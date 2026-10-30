---
date: 2026-10-26
slug: persisted-output-preview
requested_by: user
harness: Codex
verification: 53 skill tests; frozen Claude replay 1/0/1; old-owner negative control
---

## Added

- Regression coverage for explicit persisted-output preview envelopes, string and text-block returns, and negative controls for arguments, examples and incomplete metadata.

## Changed

- Returned-output truncation detection recognizes the anchored persisted-output header only when size, saved-output path and preview metadata are present. It does not open the saved file or infer downstream harm.

## Fixed

- Two explicit previews in preserved Claude tool returns previously produced no truncation signal. Same-trace diagnosis now reports each partial return; the unaffected trace stays clear.

## Open

- Detection does not establish submission, retention, understanding or downstream product harm. Historical product outcomes are unchanged. UI assets were not modified.
