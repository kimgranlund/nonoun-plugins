#!/usr/bin/env python3
"""Write the T-0248 placement-proof fixture: two throwaway git repositories, one with the context
registry (arm "registry") and one without it (arm "control").

  build_fixture.py <out-dir>

Writes <out-dir>/registry and <out-dir>/control, each a git repository with one commit. It writes
literal text once. It is not the render machinery of the design (no render_registry, no drift check):
the registry rows, cards and layout tables are written here by a small helper and nothing keeps them in
sync afterwards, which is what "built by hand" means for this proof.

The control arm is the registry arm with these removed and nothing else changed: the registry block of
docs/AGENTS.md and .sdlc/AGENTS.md (replaced by the one plain sentence a pre-registry entry holds), the
card entry files (AGENTS.md and CLAUDE.md) of every home, and the `## Kinds` and `## Decide` sections of
docs/layout.md. `.sdlc/layout.md` exists only in the registry arm (it is new with the registry).
"""
import os
import pathlib
import subprocess
import sys

MARK_START = "<!-- sdlc-lite:managed:start v1 sha256:000000000000 -->"
MARK_END = "<!-- sdlc-lite:managed:end -->"

F = ("id", "kind", "holds", "not", "why", "writer", "form", "life", "entry", "read", "owner")

# ---- docs homes: the nine rows, eleven fields each ----
DOCS = [
    dict(id="`specs/`", kind="specs", holds="what the system is and must do; built or accepted designs",
         **{"not": "unbuilt plans -> `planning/`; dated evidence -> `reports/`"},
         why="one place to trust as current", writer="maintainer, when behavior is built or accepted",
         form="kebab-case; front matter `status`, `date`", life="supersede to `archive/`",
         entry="`specs/AGENTS.md`", read="when changing or using the feature", owner="-"),
    dict(id="`planning/`", kind="planning", holds="proposals and designs under review, not built",
         **{"not": "built behavior -> `specs/`"}, why="plans must not read as fact",
         writer="whoever proposes, before building",
         form="front matter `status`: proposed, accepted, rejected or superseded",
         life="accept then move to `specs/`, or supersede to `archive/`", entry="`planning/AGENTS.md`",
         read="before building new work", owner="-"),
    dict(id="`decisions/`", kind="decisions", holds="one decision with its reason",
         **{"not": "steps -> `guides/`"}, why="keep the why", writer="whoever decides, at decision time",
         form="`NNNN-slug.md`; context, decision, consequences", life="superseded by a new record, not edited",
         entry="`decisions/AGENTS.md`", read="when a choice looks odd", owner="-"),
    dict(id="`references/`", kind="references", holds="lookup facts: APIs, schemas, glossaries, command tables",
         **{"not": "narrative -> `specs/`; steps -> `guides/`"}, why="facts you look up, not read through",
         writer="maintainer, when the fact changes", form="kebab-case; no steps",
         life="edit in place; retire to `archive/`", entry="`references/AGENTS.md`",
         read="when you need a fact", owner="-"),
    dict(id="`guides/`", kind="guides", holds="how-to steps a person follows",
         **{"not": "lookup -> `references/`"}, why="one task, one procedure",
         writer="maintainer, when a task is worth writing down", form="verb-first title; numbered steps",
         life="retire to `archive/` when the task changes", entry="`guides/AGENTS.md`",
         read="when doing the task", owner="-"),
    dict(id="`reports/`", kind="reports", holds="dated evidence: reviews, audits, benchmarks, releases",
         **{"not": "living rules -> `specs/` or `guides/`"}, why="evidence stays as recorded",
         writer="whoever ran it, on the day", form="`YYYY-MM-DD-slug.md`; dated corrections only",
         life="never edited, kept as recorded", entry="`reports/AGENTS.md`", read="when judging a claim",
         owner="-"),
    dict(id="`assets/`", kind="assets", holds="non-Markdown files a doc cites",
         **{"not": "Markdown -> its home"}, why="keep binaries out of text", writer="whoever adds the citing doc",
         form="named for the doc that cites it", life="removed with its last citing doc",
         entry="`assets/AGENTS.md`", read="when a doc embeds one", owner="-"),
    dict(id="`archive/`", kind="archive", holds="superseded or retired material",
         **{"not": "current material -> its home"}, why="history without clutter", writer="whoever retires it",
         form="`git mv`; one line says what replaced it", life="kept; deleted only by a decision",
         entry="`archive/AGENTS.md`", read="only when asked", owner="-"),
    dict(id="`other/`", kind="other", holds="unsorted documents, as a quarantine",
         **{"not": "permanent homes -> the home that fits"}, why="nothing is lost while sorting",
         writer="anyone, when no home fits", form="front matter `owner:` and `review-by:` required",
         life="sort into a home by `review-by`", entry="`other/AGENTS.md`", read="only to sort it",
         owner="the person named in `owner:`"),
]

# ---- .sdlc record types: ten rows ----
SDLC = [
    dict(id="`NNNN-slug/`", kind="ticket", holds="a ticket and its work: `handoff.md`, `step-N/`, role results, `runs.jsonl`, `skips.md`",
         **{"not": "reader docs -> `docs/`"}, why="one folder per unit of work",
         writer="roles and scripts, while the ticket runs", form="`handoff.md` front matter; results `<role>-L<n>.md`",
         life="close renames it to `.NNNN-slug/`", entry="-", read="when claiming or continuing it",
         owner="`tickets.py`"),
    dict(id="`<task>/`", kind="task", holds="work folders with no ticket: `verify-*`, `merge-*`, `release-*`",
         **{"not": "tickets -> `NNNN-slug/`"}, why="same shape as a ticket folder", writer="roles, while work runs",
         form="handoff plus results", life="close or delete with the work", entry="-", read="when told to",
         owner="`run.sh`"),
    dict(id="`.NNNN-slug/`", kind="closed ticket", holds="a closed ticket", **{"not": "open work -> `NNNN-slug/`"},
         why="finished work leaves the listing", writer="`tickets.py close`", form="renamed by `tickets.py close`",
         life="kept as history", entry="-", read="only when asked", owner="`tickets.py`"),
    dict(id="`messages/`", kind="mailbox", holds="the git-ignored mailbox",
         **{"not": "anything that must last -> a ticket or `notes.md`"}, why="hand work between harnesses",
         writer="`messages.py`", form="front matter `send_time`, `sender`, `receiver`, `topic`",
         life="expire after its ttl", entry="`messages/AGENTS.md`", read="when mail waits for you",
         owner="`messages.py`"),
    dict(id="`evals/`", kind="evals", holds="dated model and effort experiments",
         **{"not": "the tables themselves -> `plugins/`"}, why="a table change needs evidence",
         writer="whoever ran the experiment", form="`evals.py` file format", life="kept as recorded",
         entry="`evals/AGENTS.md`", read="before changing a model table", owner="`evals.py`"),
    dict(id="`proposals/`", kind="proposals", holds="candidate changes mined from runs",
         **{"not": "decisions -> `docs/decisions/`"}, why="nothing applied without evidence",
         writer="`proposals.py scan`", form="`proposals.py` format", life="accept, reject or promote",
         entry="`proposals/AGENTS.md`", read="when triaging", owner="`proposals.py`"),
    dict(id="`supervisor/`", kind="supervisor", holds="idle-host watcher config and state",
         **{"not": "tickets -> `NNNN-slug/`"}, why="keep watcher state apart", writer="`supervisor.py init`",
         form="`hosts.local.json`", life="rewritten by the watcher", entry="-", read="when waking a host",
         owner="`supervisor.py`"),
    dict(id="`notes.md`", kind="notes", holds="follow-ups not filed as tickets, one block per closed ticket",
         **{"not": "open work -> a ticket"}, why="nothing is dropped at close", writer="`tickets.py close`, or by hand",
         form="`## T-NNNN: title (date)`", life="swept when choosing work", entry="-",
         read="when sweeping open items", owner="`tickets.py`"),
    dict(id="`roadmap.md`", kind="roadmap", holds="the generated queue", **{"not": "edits by hand"},
         why="one ordered view", writer="`tickets.py roadmap`", form="generated", life="regenerated",
         entry="-", read="when choosing next work", owner="`tickets.py`"),
    dict(id="`config`", kind="config", holds="repo-owned `key: value` lines", **{"not": "records"},
         why="tool settings", writer="the repository owner", form="`ticket_folders`, `ticket_root`",
         life="edited by hand", entry="-", read="by tools", owner="`tickets.py`"),
]

ROW_COLS = ("id", "holds", "not", "why", "form", "read")


def row_table(rows):
    out = ["| id | holds | not | why | form | read |", "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        out.append("| " + " | ".join(r[c] for c in ROW_COLS) + " |")
    return "\n".join(out)


def kinds_table(rows):
    out = ["| " + " | ".join(F) + " |", "| " + " | ".join("---" for _ in F) + " |"]
    for r in rows:
        out.append("| " + " | ".join(r[c] for c in F) + " |")
    return "\n".join(out)


def card(r):
    lines = ["## Registry row"] + [f"- {f}: {r[f]}" for f in F] + ["", "## Local rules", "(none yet)"]
    return "\n".join(lines) + "\n"


DOCS_DECIDE = """1. Is it not Markdown? yes -> `assets/`
2. Is it retired or replaced? yes -> `archive/`
3. Is it a dated record of something that happened (a run, review, audit, benchmark, release)? yes -> `reports/`
4. Is it one decision with its reason? yes -> `decisions/`
5. Is it steps a person follows to do a task? yes -> `guides/`
6. Is it lookup material (a table, API, glossary)? yes -> `references/`
7. Does it describe something not built yet? yes -> `planning/`
8. Does it describe what the system is or must do? yes -> `specs/`
9. otherwise -> `other/`, with `owner:` and `review-by:`"""

SDLC_DECIDE = """1. Does a script or role write it while work runs? yes -> its record type row above
2. Is it a deliverable a reader returns to? yes -> `docs/`, then the docs `## Decide` list
3. Must a result outlive its ticket? yes -> promote a copy to `docs/reports/` with `source:`, and the `.sdlc` copy stays
4. Is it a design that outlived its ticket? yes -> promote a copy to `docs/planning/` or `docs/specs/`
5. otherwise -> `its ticket folder`"""

DOCS_CHECKLIST = """1. Pick the home with the `## Decide` list; do not create a new folder.
2. Name the file by the home's `form` column and add the front matter it requires.
3. Put the file in that home, then link it from the document it supports.
4. Never copy a fact; link to its one authoritative home.
5. A work record or runtime state is not a doc: it belongs in `.sdlc/`."""

SDLC_CHECKLIST = """1. Pick the record type with the `## Decide` list.
2. Put a role or script result in the ticket folder it belongs to; never in `docs/`.
3. Put a follow-up that is not a ticket in `notes.md`.
4. A reader deliverable is not a work record: it belongs in `docs/`.
5. Never edit `roadmap.md` by hand."""

DOCS_ENTRY_REGISTRY = f"""# Documentation

{MARK_START}
`docs/` holds durable knowledge written for readers; work records and runtime state live in `.sdlc/`. Placement effect unproven; see docs-schema design.

How to use it: read the registry below, pick one home with `## Decide`, read that home's one file.

{row_table(DOCS)}

## Decide

{DOCS_DECIDE}

## Add a document

{DOCS_CHECKLIST}
{MARK_END}

Keep one authoritative copy of each fact and link to it.
"""

DOCS_ENTRY_CONTROL = """# Documentation

Pick the folder for the task; read one file, not the folder. The folder names are listed in `layout.md`.

Keep one authoritative copy of each fact and link to it.
"""

SDLC_ENTRY_REGISTRY = f"""# Work records

{MARK_START}
`.sdlc/` holds work records and runtime state written by scripts and roles while work runs; reader docs live in `docs/`. Placement effect unproven; see docs-schema design.

How to use it: read the registry below, pick one record type with `## Decide`, read that type's one file.

{row_table(SDLC)}

## Decide

{SDLC_DECIDE}

## Add a record

{SDLC_CHECKLIST}
{MARK_END}

Closed `.NNNN-*` folders are history: open one only when asked.
"""

SDLC_ENTRY_CONTROL = """# Work records

This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md` and `config`.

Closed `.NNNN-*` folders are history: open one only when asked.
"""

HOMES = [r["id"] for r in DOCS]

LAYOUT_BASE = """# Docs layout

## Homes

""" + "\n".join(f"- {h}" for h in HOMES) + """

## Frozen paths

- none
"""

LAYOUT_DOCS_REGISTRY = LAYOUT_BASE + f"""
## Kinds

{kinds_table(DOCS)}

## Decide

{DOCS_DECIDE}
"""

LAYOUT_SDLC_REGISTRY = f"""# Work records layout

## Kinds

{kinds_table(SDLC)}

## Decide

{SDLC_DECIDE}
"""

# ---- existing documents: one per docs home, and the existing .sdlc records ----
EXISTING = {
    "docs/specs/board-columns.md": """---
status: accepted
date: 2026-09-12
---
# Board columns

The board shows four columns: Task, Step, Status and Percent. Status is one of the stage words the ticket
tool writes. The board is rendered from the ticket folders and never written by hand.
""",
    "docs/planning/dispatcher-queue-proposal.md": """---
status: proposed
date: 2026-09-20
---
# Dispatcher queue proposal

Proposal: let the dispatcher hold a queue of ready tickets and start the next one when a lane frees.
Nothing is built. The open question is how a stalled lane releases its slot.
""",
    "docs/decisions/0001-use-markdown-tickets.md": """# 0001: Tickets are Markdown files

Status: accepted, 2026-08-30

Context: tickets must be readable by people and by every agent without a server.
Decision: one `handoff.md` per ticket folder, with front matter.
Consequences: no query language; the roadmap is generated by a script.
""",
    "docs/references/cli-flags.md": """# CLI flags

| Command | Flag | Meaning |
| --- | --- | --- |
| `tickets.py` | `--root` | the work-records folder |
| `steps.py` | `lane` | print the lane for a ticket |
""",
    "docs/guides/resume-a-stopped-run.md": """# Resume a stopped run

1. Open the ticket folder and read `runs.jsonl` for the last attempt.
2. Delete the attempt's lock file.
3. Start the same role again with the same handoff.
4. Check that the new attempt wrote its result file.
""",
    "docs/reports/2026-09-30-link-audit.md": """# Link audit, 2026-09-30

Ran the link check over every Markdown file. 212 links checked, 3 broken, all fixed the same day.
""",
    "docs/assets/lane-flow.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40"><rect width="120" height="40" fill="none" stroke="black"/><text x="8" y="24">lane flow</text></svg>
""",
    "docs/archive/legacy-lane-names.md": """# Legacy lane names

Retired 2026-08-15. Replaced by the lane names in [board columns](../specs/board-columns.md).
The old names were `quick`, `normal` and `deep`.
""",
    "docs/other/unsorted-notes-2026-09.md": """---
owner: kim
review-by: 2026-11-01
---
# Unsorted notes, September

Loose notes from the planning call. Not yet sorted into a home.
""",
    ".sdlc/config": "ticket_folders: numbered\n",
    ".sdlc/roadmap.md": """# Roadmap

- T-0007 Retry rule for stopped runs (0007-retry-rule), status ready
""",
    ".sdlc/notes.md": """# Notes

## T-0003: Board colors (2026-09-20)
- note: revisit the color palette after the next release.
""",
    ".sdlc/0007-retry-rule/handoff.md": """---
id: T-0007
title: "Retry rule for stopped runs"
type: feature
status: ready
size: S
---

## Goal
A stopped run retries once with the same handoff before it reports blocked.
""",
    ".sdlc/0007-retry-rule/builder-L2.md": """# Builder result

Changed `runner.py` to retry once. Checks: unit tests green.
""",
    ".sdlc/.0003-board-colors/handoff.md": """---
id: T-0003
title: "Board colors"
type: chore
status: done
size: S
---

## Goal
Color the board's status column.
""",
    ".sdlc/messages/done/codex/20261001-0900-review-ready.md": """---
send_time: 2026-10-01T09:00:00Z
sender: claude
receiver: codex
topic: review ready
---
The retry change is ready for review.
""",
    ".sdlc/evals/2026-09-28-model-table.md": """# Model table experiment, 2026-09-28

Compared two effort rows on 10 tasks; the lower row passed 9 of 10 at lower cost.
""",
    ".sdlc/proposals/p-0001-cache-board.md": """# Proposal p-0001: cache the board

Mined from three runs that re-rendered an unchanged board. Status: open.
""",
}

SDLC_CARD_HOMES = {"mailbox": "messages", "evals": "evals", "proposals": "proposals"}


def write(base, rel, text):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def build(base, arm):
    base.mkdir(parents=True)
    for rel, text in EXISTING.items():
        write(base, rel, text)
    if arm == "registry":
        write(base, "docs/layout.md", LAYOUT_DOCS_REGISTRY)
        write(base, "docs/AGENTS.md", DOCS_ENTRY_REGISTRY)
        write(base, ".sdlc/layout.md", LAYOUT_SDLC_REGISTRY)
        write(base, ".sdlc/AGENTS.md", SDLC_ENTRY_REGISTRY)
        for r in DOCS:
            home = r["kind"]
            write(base, f"docs/{home}/AGENTS.md", card(r))
            write(base, f"docs/{home}/CLAUDE.md", "@AGENTS.md\n")
        for r in SDLC:
            if r["kind"] in SDLC_CARD_HOMES:
                d = SDLC_CARD_HOMES[r["kind"]]
                write(base, f".sdlc/{d}/AGENTS.md", card(r))
                write(base, f".sdlc/{d}/CLAUDE.md", "@AGENTS.md\n")
    else:
        write(base, "docs/layout.md", LAYOUT_BASE)
        write(base, "docs/AGENTS.md", DOCS_ENTRY_CONTROL)
        write(base, ".sdlc/AGENTS.md", SDLC_ENTRY_CONTROL)
    write(base, "docs/CLAUDE.md", "@AGENTS.md\n")
    write(base, ".sdlc/CLAUDE.md", "@AGENTS.md\n")
    env = dict(os.environ, GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
    for cmd in (["git", "init", "-q", "-b", "main"], ["git", "add", "-A"],
                ["git", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "fixture " + arm]):
        subprocess.run(cmd, cwd=base, check=True, env=env)


def main():
    out = pathlib.Path(sys.argv[1]).resolve()
    for arm in ("registry", "control"):
        build(out / arm, arm)
        print("built", out / arm)


if __name__ == "__main__":
    main()
