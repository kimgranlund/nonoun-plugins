---
status: proposed
---
# Reorganization plan procedure

Status: built. Steps 1 and 2 write a plan and move nothing (T-0232); step 3 applies an approved plan with `reorg.py` (T-0233). The rules are in [the reorganization rules](reorganization.md).

The work splits in two so each half does what it is good at. A script reads the repository and states facts. A model session reads those facts and proposes a plan. A second script, `reorg.py`, applies only a plan the user approved.

## Step 1: the facts

Run `inventory.py` from the plugin's `scripts/` folder against the repository, read-only:

```
python3 <plugin>/scripts/inventory.py --root <repo> --out <path outside the repo>.json --top 15
```

It lists every tracked document with size, first heading, last commit date, inbound and outbound links, whether its folder has an entry file, and the flags `orphan`, `stale`, `duplicate`, `oversized`, `misplaced`, `broken_links`, plus folders with many documents and no entry file. `.sdlc/`, generated paths, vendored paths, and Git-ignored paths are skipped. The definitions of link, mention, and each flag are in the script's header. The script writes nothing into the repository and makes no model call.

## Step 2: the plan

A solo session (Sonnet at xhigh is enough) reads the text report and the JSON, and reads individual documents only where a proposal needs one. It writes one markdown file, outside the repository or at a docs path the user names. The plan has these sections:

- **Summary:** counts from the inventory, and the three changes that would matter most.
- **Moves:** each is `from`, `to`, the inventory row that backs it (a flag and its evidence), and a risk note.
- **Merges:** documents flagged `duplicate`, with what to keep and what to drop.
- **New entry files:** folders flagged `no_entry_file`, with a one-line scope for each `AGENTS.md`.
- **Links to rewrite:** every link that a move would break, taken from `outbound` and `inbound`, and every `broken_links` row with a proposed fix or "leave".
- **Leave alone:** material the plan will not touch, with the reason (dated evidence, generated files, a folder another process owns).

Rules for the session:

- Every proposal cites an inventory row. A proposal with no row is deleted, not softened.
- Do not propose moving a file out of a folder that holds dated evidence unless the inventory shows the file is misplaced there.
- A flag is a lead, not a verdict. A `duplicate` of templated READMEs is usually intended; say so when the documents are the same kind of file.
- State what was not read.

## Step 3: apply

The plan is never applied by the session that wrote it. The session or the user turns the approved moves into a plan JSON file outside the repository (the format is in `reorg.py`'s header), and the repository needs a `docs/layout.md` that lists its frozen paths. Then, from the user's session:

```
python3 <plugin>/scripts/reorg.py apply <plan>.json --root <repo> --dry-run
python3 <plugin>/scripts/reorg.py apply <plan>.json --root <repo> --approve <digest>
```

The dry run writes nothing. It prints every move, link fix, and rewrite, the links already broken before the first batch, and a digest of the repository and the plan. Passing that digest to `--approve` is the approval. The apply:

1. Refuses unless the digest still matches (an edited document or plan means a new dry run), and refuses every case in [the refusals](reorganization.md#refusals) before any write, printing `reorg.py: refused: <reason>`.
2. Rewrites every citation of a moved file it can, and refuses a citation it cannot rewrite.
3. Makes one Git commit per batch, so `git revert` undoes a batch.
4. Finishes each batch with a link check against the baseline taken before the first move, and restores the start when it fails.

The evidence on this repository is [the apply live run](../../reports/reorg-apply-live-run.md).
