# Editing this skill

For agents that change the skill itself. How to use the skill is in SKILL.md; this file does not repeat it.

## Layout

- `SKILL.md`: the entry file the harness loads. Keep it short and link out.
- `references/`: one topic per file (engineering, diagnostics, decision analysis, bundles, hydration, workflows, contract audit, schema, viewer). `viewer.md` holds the shell's UI specification, kept out of SKILL.md.
- `references/learnings/`: runtime-harness field lessons for turning a diagnosis into fixes, one file per step, indexed by `README.md` (its Scope block says what a runtime harness is).
- `scripts/`: Python hydration, detectors, the engineering CLI, the contract audit (`audit.py`) and the library publisher. They never execute trace contents or audited files.
- `assets/`: the reusable offline shell (HTML, CSS, JS) that renders a hydrated report.
- `tests/`: unittest regressions for the scripts; `tests/fixtures/` holds synthetic inputs with no project names.
- `agents/`: host metadata (`openai.yaml`).

## Adding a learning

The existing files hold runtime-harness lessons. A runtime-harness learning goes in the file for its step with the next free number. A CLI-harness learning (a Claude Code or Codex session) goes in a separate file with its own "Applies to: CLI harness" tag, listed in the index. Never mix it into a runtime file. Use the format in `learnings/README.md`: a one-sentence rule, an "Observed in ..." line naming where it was seen, and a "Check:" line saying how a new project confirms it, and an "Applies to:" line (runtime harness, CLI harness, or both). State what was observed and never present it as universal law. Keep it harness-agnostic, with no project paths, agent names or ticket ids. Update the lesson range shown in the index.

## Test

From the skill root: `python3 -B -m unittest discover -s tests`. It must exit 0 after any script change.

## Rules

- No em dashes in any file.
- The skill owns hydration: scripts turn traces into the v2 report, with its evidence, findings and coverage. The shell owns presentation: `assets/` renders the report and never re-derives evidence. Do not move logic across that line.
- A detector abstains when evidence is missing. Do not turn absence into a finding.
- This folder is not a git repo. Copy it somewhere safe before a large edit, and diff against that copy before you report.

## Change log
Record each change set in `updates-log/YYYYMMDD-<slug>/changelog.md` (Added, Changed, Fixed, Open) and add its row at the top of `updates-log/CHANGELOG.md` (newest first).
