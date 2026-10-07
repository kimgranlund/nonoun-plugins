---
status: proposed
---
# Reorganization plan procedure

Status: step 1 of the reorganization project. A plan is written; nothing is moved. The apply step is not built (see [the draft rules](reorganization.md) and ticket T-0233).

The work splits in two so each half does what it is good at. A script reads the repository and states facts. A model session reads those facts and proposes a plan. A later script, not built yet, applies only a plan the user approved.

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

## Step 3: the apply gate (not built)

The plan is never applied by the session that wrote it. A later script applies a plan only after the user approves it, and it must:

1. Refuse unless the plan's digest matches the repository now (an edited document means plan again).
2. Do a dry run that prints every move and every link rewrite.
3. Scan for citing files before each move, as `tickets.py close` does for ticket folders, and refuse a move that would orphan a citation it cannot rewrite.
4. Make one Git commit per batch, so `git revert` undoes a batch.
5. Finish with a link check against the baseline taken before the first move, and restore the working tree when it fails.

The remaining requirements are the refusals and validation gates in [the draft rules](reorganization.md).
