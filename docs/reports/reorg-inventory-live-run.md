# Reorganization inventory live run

Recorded: 2026-10-05. Live run for ticket T-0232: `inventory.py` ran read-only on two repositories, and one model session wrote a reorganization plan from one of the inventories. Nothing was moved. Evidence is in [`reorg-inventory-live-run/`](reorg-inventory-live-run/); the claims below name the file that shows each one.

## What ran

- `inventory.py` at the T-0232 branch, run from this worktree: `python3 plugins/sdlc-lite/scripts/inventory.py --root <repo> --out <path outside the repo> --top 12` (selftest result: [`selftest.txt`](reorg-inventory-live-run/selftest.txt), `PASS`).
- Repositories: `/Users/kimgranlund/Projects/maison/ui-kit-maison` at HEAD `01951d4e`, and this repository at `d5b689e`.
- Plan session: `claude -p --model sonnet --effort xhigh --allowedTools "Read Grep Glob"` with read access to the repository and the inventory files, `--output-format json` (the flags are in the command as I ran it; the effort is not recorded in the result). Prompt: [`plan-prompt.txt`](reorg-inventory-live-run/plan-prompt.txt). Result: [`plan-session-full.json`](reorg-inventory-live-run/plan-session-full.json) (`success`, 34 turns, `total_cost_usd` 2.5008968, 364376 ms; a six-field excerpt is in [`plan-session.json`](reorg-inventory-live-run/plan-session.json)). Its `modelUsage` lists two models: `claude-sonnet-5-5` ($0.924) and `claude-fable-5-1` ($1.577). The result's `usage.iterations` tags the second model's usage as one `advisor_message` iteration (the same 103373 in and 10857 out as its `modelUsage` entry); I did not trace what it contributed. The result also lists one denied `Bash` call (`permission_denials`), made by the session and refused because only Read, Grep, and Glob were allowed. The session had no write tool; the plan is its printed answer ([`maison-plan.md`](reorg-inventory-live-run/maison-plan.md), 122 lines).
- Claude Code version: [`claude-version.txt`](reorg-inventory-live-run/claude-version.txt).

## Inventory results

| Repository | Documents | Skipped | Orphan | Duplicate | Misplaced | Broken links | Oversized | Stale | Folders with no entry file |
|---|---|---|---|---|---|---|---|---|---|
| maison | 230 | 10 | 2 | 42 | 10 | 5 | 0 | 0 | 2 |
| this repository | 498 | 1958 | 170 | 275 | 6 | 3 | 1 | 0 | 13 |

Source: [`maison-summary.json`](reorg-inventory-live-run/maison-summary.json), [`sdlc-summary.json`](reorg-inventory-live-run/sdlc-summary.json); the top rows per flag are in [`maison-inventory.txt`](reorg-inventory-live-run/maison-inventory.txt) and [`sdlc-inventory.txt`](reorg-inventory-live-run/sdlc-inventory.txt). The full JSON reports are not committed (maison 176 KB, this repository 1.2 MB). "Skipped" for this repository is almost entirely `.sdlc/` records, which are skipped by default.

What the numbers say, from the text reports:

- On maison, of the 12 duplicate rows shown in `maison-inventory.txt`, 10 are `README.md` files under `src/components/` and the other two are two `SKILL.md` files; the 10 misplaced rows in `maison-inventory.txt` are six `README.md` files under `src/components/`, two `SKILL.md` files, the spec `docs/reference/gen-ui-system/specs/gen-ui-recipes.md`, and `examples/application-patterns/component.md`. The plan session read some of these and judged them leads, not defects (see the plan below); the inventory itself does not.
- On this repository the flags are dominated by `docs/reports/` evidence (the `orphan` and `duplicate` rows in `sdlc-inventory.txt` are mostly small `.txt` and `.md` files inside live-run folders, with the same boilerplate in several of them). The inventory has no notion of dated or frozen evidence, so it reports it. The draft rules freeze that material by listing it in `docs/layout.md`; the inventory does not read that file yet.

## The plan and a spot check

[`maison-plan.md`](reorg-inventory-live-run/maison-plan.md) proposes no move and no merge. It proposes three small changes: rewriting five ticket links in four specs to the dot-prefixed closed-ticket folders, adding two `AGENTS.md` entry files, and linking two orphan documents from their parents. For each flagged group it states why the flag is a lead. It ends with a "Not read" section that lists what it did not open.

I checked six claims in the plan by hand, read-only, against maison. The commands and what they showed are in [`spot-check.txt`](reorg-inventory-live-run/spot-check.txt). All six held:

1. The rewrite target `.sdlc/tickets/.0059-theme-context-provider/theme-context-contract.md` exists and the undotted folder does not.
2. `docs/layout.md` lists `docs/reports/` under Frozen paths.
3. `docs/reference` has no entry file directly in it, and `specs/` has 11 documents and none.
4. `examples/fourth-wave-domain/README.md` has 3 lines and nothing cites `fourth-wave-domain/component.md`.
5. `src/components/button/component.md` line 46 holds `<a href="…">` inside prose, which is why the link check flagged it.
6. The two sampled READMEs both open with "Author semantic intent in [contract.json](contract.json)". The plan quotes that sentence without the link markup, so my first exact-string search missed it; the claim is true.

The plan makes more claims than six and I did not count them. The spot check does not judge whether the plan is the right plan.

## Limits

- One run each on two repositories, and one plan, written once. Plan quality is not judged beyond the six checks.
- The inventory flags are heuristics with fixed thresholds (stale 180 days against the newest commit, oversized 500 lines, duplicate 0.6 overlap of sampled word groups, misplaced 60 percent of at least three links). No other values were tried.
- The inventory does not read `docs/layout.md`, so it cannot freeze evidence folders, and the plan session had to explain the flags it saw as noise. A frozen or evidence classification is the next input to settle.
- A broken link whose target is `…` inside example markup is reported as broken (maison `src/components/button/component.md`); the inventory does not understand example prose.
- The plan's links-to-rewrite item says it did not check whether a gate reads two hash files that cite the specs; that remains unchecked.
- The rules in [the draft](../planning/repo-onboarding/reorganization.md) are not implemented. There is no apply step (T-0233), no digest, and no refusal logic.
- Spend: the plan session cost 2.5008968 dollars by its own result, of which $1.577 is listed under a second model (see above); the inventory runs cost nothing.
- Maison's working tree had three modified files before this work and the same three after it.
- Verification: the first L3 pass ([`reorg-inventory-live-run/verify-0232-verifier-L3.md`](reorg-inventory-live-run/verify-0232-verifier-L3.md)) passed five of six criteria and failed one on a misplaced-rows sentence and an unbacked model claim; both were fixed. A narrow L3 pass ([`reorg-inventory-live-run/verify-0232-narrow-verifier-L3.md`](reorg-inventory-live-run/verify-0232-narrow-verifier-L3.md)) passed two of three criteria and failed one on the second-model sentence above; I applied its suggested wording and confirmed it by checking the numbers against `plan-session-full.json` with a short script. No third verifier ran, so no verifier result says `pass` overall for the final text.
