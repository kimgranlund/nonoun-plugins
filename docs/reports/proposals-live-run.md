# Proposals live run

Recorded: 2026-10-04. Live run for ticket T-0186: `proposals.py scan` mines this repository's own `.sdlc/` run records read-only, files evidence-backed candidates in a temp dir, and refuses to accept one without a valid eval. No model call.

## Environment

- Date: 2026-10-04.
- Host OS: macOS 26.6.2, Darwin 25.6.0.
- `python3 --version`: `Python 3.9.6`.
- Repo commit: `6658615` (`git rev-parse --short HEAD`). The tree includes this ticket's uncommitted changes (step 1's `proposals.py` and `check.sh`, and step 2's entry files and doc edits).
- Temp dir: a `mktemp -d` directory under `/var/folders/.../T/`, outside this repository, removed at the end.

## Commands

Setup, from the repository root:

```sh
R=$(pwd)
T=$(mktemp -d)
P=plugins/sdlc-lite/scripts/proposals.py
src() { find .sdlc \( -name runs.jsonl -o -name notes.md -o -name '*-L[1-5]*.md' \) -type f ! -path '.sdlc/proposals/*' ! -path '.sdlc/messages/*' -print0 | sort -z | xargs -0 shasum -a 256; }
plg() { find plugins -type f -print0 | sort -z | xargs -0 shasum -a 256; }
```

Arm 1, before:

```sh
src >"$T/src.before"; plg >"$T/plg.before"; ls -A .sdlc/proposals
```

Arm 2, scan:

```sh
python3 "$P" --root .sdlc --proposals "$T/proposals" scan
```

Arm 3, candidates and evidence:

```sh
python3 "$P" --root .sdlc --proposals "$T/proposals" list
for id in $(python3 "$P" --root .sdlc --proposals "$T/proposals" list | cut -f1); do python3 "$P" --root .sdlc --proposals "$T/proposals" show $id; done
```

Arm 4, idempotence:

```sh
find "$T/proposals" -type f -exec shasum -a 256 {} + | sort >"$T/h1"
python3 "$P" --root .sdlc --proposals "$T/proposals" scan
find "$T/proposals" -type f -exec shasum -a 256 {} + | sort >"$T/h2"
cmp "$T/h1" "$T/h2"
```

Arm 5, negative control on the transitions:

```sh
f=$(grep -l '^id: P-0001$' "$T"/proposals/*/proposal.md); cp "$f" "$T/p1.before"
python3 "$P" --root .sdlc --proposals "$T/proposals" accept P-0001
python3 "$P" --root .sdlc --proposals "$T/proposals" accept P-0001 --eval docs/reports/evals-live-run.md
cmp "$T/p1.before" "$f"
```

Arm 6, sources and plugins unchanged:

```sh
src >"$T/src.after"; plg >"$T/plg.after"
cmp "$T/src.before" "$T/src.after"; cmp "$T/plg.before" "$T/plg.after"
ls -A .sdlc/proposals
```

Arm 7, negative control on the read-only check. The mutant replaces the `# rule: read-only` line exactly as the selftest's read-only control does: `return <expr>  # rule: read-only` becomes `t = <expr>; Path(path).write_text(t + 'x', encoding='utf-8'); return t` (one line replaced).

```sh
mkdir "$T/copy" && cp -R .sdlc "$T/copy/.sdlc"
mkdir "$T/mutant"   # then write $T/mutant/proposals.py with the replacement above
(cd "$T/copy" && src) >"$T/copy.before"
python3 "$T/mutant/proposals.py" --root "$T/copy/.sdlc" --proposals "$T/copy-proposals" --plugin "$R/plugins/sdlc-lite" scan
(cd "$T/copy" && src) >"$T/copy.after"
cmp "$T/copy.before" "$T/copy.after"
diff "$T/copy.before" "$T/copy.after" | grep -c '^>'
```

Arm 8, cleanup:

```sh
rm -rf "$T"
```

## Evidence

| Arm | Command | Result |
|---|---|---|
| 1 | `src`, `plg` | exit 0 each; 1601 source lines, 378 `plugins/` lines |
| 1 | `ls -A .sdlc/proposals` | exit 0, `AGENTS.md` and `CLAUDE.md` |
| 2 | `proposals.py --root .sdlc --proposals "$T/proposals" scan` | exit 0, `proposals scan: 19 new, 0 updated, 0 unchanged` (18 `replan`, 1 `plan-defect` with 12 evidence lines) |
| 3 | `list`, then `show` for each id | exit 0 for each of the 20 commands; text below |
| 4 | second `scan` | exit 0, `proposals scan: 0 new, 0 updated, 19 unchanged` |
| 4 | `cmp` of the two hash lists | exit 0 |
| 5 | negative control: `accept P-0001` | exit 1, `proposals.py: no eval given: pass --eval <file in .sdlc/evals/>` |
| 5 | negative control: `accept P-0001 --eval docs/reports/evals-live-run.md` | exit 1, `proposals.py: eval docs/reports/evals-live-run.md is not in .sdlc/evals/` |
| 5 | `cmp` of P-0001's file | exit 0, unchanged |
| 6 | `cmp` source manifest | exit 0 |
| 6 | `cmp` `plugins/` manifest | exit 0, the `plugins/` manifest is unchanged |
| 6 | `ls -A .sdlc/proposals` | `AGENTS.md` and `CLAUDE.md` only |
| 7 | negative control: mutant scan of the copy | exit 0, `proposals scan: 19 new, 0 updated, 0 unchanged` (the first pass piped the output and lost the exit code in zsh; arm 7 alone was rerun in a fresh temp dir with the output redirected to a file, and gave the same scan line, `cmp` exit 1, and 1281 differing lines) |
| 7 | `cmp` of the copy's manifests | exit 1, `differ: char 223, line 3`; 1281 of 1601 source lines differ (the files scan reads; planner and other role results matched by the manifest glob are not read) |
| 8 | `rm -rf "$T"` | exit 0; `test -e "$T"` exit 1 |

Arm 3 list output:

```
P-0001	candidate	2	replan-021d88f1	Repeated planner runs in .sdlc/0016-ticket-numbered-folders
P-0002	candidate	2	replan-f58f6d42	Repeated planner runs in .sdlc/0060-unpassable-plan-criteria
P-0003	candidate	2	replan-154e845f	Repeated planner runs in .sdlc/0065-fanout-py-s-default-lane
P-0004	candidate	2	replan-a6b926a3	Repeated planner runs in .sdlc/0081-add-a-steps-py-selftest
P-0005	candidate	2	replan-10e4c6f9	Repeated planner runs in .sdlc/0092-run-a-live-probe-to
P-0006	candidate	2	replan-eeffbb3b	Repeated planner runs in .sdlc/0109-make-the-fixed-count-lint
P-0007	candidate	2	replan-63a2e256	Repeated planner runs in .sdlc/0113-close-rename-breaks-refs
P-0008	candidate	2	replan-e59d59cc	Repeated planner runs in .sdlc/0121-pattern-kill-hook-does-not
P-0009	candidate	2	replan-125b7e2b	Repeated planner runs in .sdlc/0132-planner-batch-probes
P-0010	candidate	2	replan-8e8ca0b3	Repeated planner runs in .sdlc/0135-extend-the-clean-status-lint
P-0011	candidate	2	replan-14482663	Repeated planner runs in .sdlc/0157-review-sdlc-traces
P-0012	candidate	2	replan-ce5dc26a	Repeated planner runs in .sdlc/0162-entry-files-in-step-handoffs
P-0013	candidate	2	replan-63e9323d	Repeated planner runs in .sdlc/0166-agent-spawn-hook
P-0014	candidate	2	replan-d7c5dae9	Repeated planner runs in .sdlc/0177-mailbox-core
P-0015	candidate	2	replan-5c2cb329	Repeated planner runs in .sdlc/0178-messenger-agent
P-0016	candidate	2	replan-e2cd2d91	Repeated planner runs in .sdlc/0179-messages-entry-files
P-0017	candidate	3	replan-c45f7c00	Repeated planner runs in .sdlc/0181-messages-wait
P-0018	candidate	2	replan-19db4531	Repeated planner runs in .sdlc/0184-role-result-schema
P-0019	candidate	12	plan-defect-efbe35d7	Repeated plan defect verdicts

Arm 3 `show` output, every proposal:

```
---
id: P-0001
title: Repeated planner runs in .sdlc/0016-ticket-numbered-folders
status: candidate
pattern: replan .sdlc/0016-ticket-numbered-folders
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0016-ticket-numbered-folders/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0016-ticket-numbered-folders/runs.jsonl):1 (run) "role=planner level=L1"
- [.sdlc/.0016-ticket-numbered-folders/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0016-ticket-numbered-folders/runs.jsonl):2 (run) "role=planner level=L3"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0002
title: Repeated planner runs in .sdlc/0060-unpassable-plan-criteria
status: candidate
pattern: replan .sdlc/0060-unpassable-plan-criteria
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0060-unpassable-plan-criteria/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0060-unpassable-plan-criteria/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0060-unpassable-plan-criteria/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0060-unpassable-plan-criteria/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0003
title: Repeated planner runs in .sdlc/0065-fanout-py-s-default-lane
status: candidate
pattern: replan .sdlc/0065-fanout-py-s-default-lane
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0065-fanout-py-s-default-lane/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0065-fanout-py-s-default-lane/runs.jsonl):1 (run) "role=planner level=L1 file=planner-L1.md"
- [.sdlc/.0065-fanout-py-s-default-lane/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0065-fanout-py-s-default-lane/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0004
title: Repeated planner runs in .sdlc/0081-add-a-steps-py-selftest
status: candidate
pattern: replan .sdlc/0081-add-a-steps-py-selftest
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0081-add-a-steps-py-selftest/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0081-add-a-steps-py-selftest/runs.jsonl):1 (run) "role=planner level=L1 file=planner-L1.md"
- [.sdlc/.0081-add-a-steps-py-selftest/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0081-add-a-steps-py-selftest/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0005
title: Repeated planner runs in .sdlc/0092-run-a-live-probe-to
status: candidate
pattern: replan .sdlc/0092-run-a-live-probe-to
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0092-run-a-live-probe-to/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0092-run-a-live-probe-to/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0092-run-a-live-probe-to/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0092-run-a-live-probe-to/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0006
title: Repeated planner runs in .sdlc/0109-make-the-fixed-count-lint
status: candidate
pattern: replan .sdlc/0109-make-the-fixed-count-lint
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0109-make-the-fixed-count-lint/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0109-make-the-fixed-count-lint/runs.jsonl):1 (run) "role=planner level=L1 file=planner-L1.md"
- [.sdlc/.0109-make-the-fixed-count-lint/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0109-make-the-fixed-count-lint/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0007
title: Repeated planner runs in .sdlc/0113-close-rename-breaks-refs
status: candidate
pattern: replan .sdlc/0113-close-rename-breaks-refs
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0113-close-rename-breaks-refs/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0113-close-rename-breaks-refs/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0113-close-rename-breaks-refs/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0113-close-rename-breaks-refs/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0008
title: Repeated planner runs in .sdlc/0121-pattern-kill-hook-does-not
status: candidate
pattern: replan .sdlc/0121-pattern-kill-hook-does-not
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0121-pattern-kill-hook-does-not/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0121-pattern-kill-hook-does-not/runs.jsonl):1 (run) "role=planner level=L1 file=planner-L1.md"
- [.sdlc/.0121-pattern-kill-hook-does-not/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0121-pattern-kill-hook-does-not/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0009
title: Repeated planner runs in .sdlc/0132-planner-batch-probes
status: candidate
pattern: replan .sdlc/0132-planner-batch-probes
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0132-planner-batch-probes/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0132-planner-batch-probes/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0132-planner-batch-probes/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0132-planner-batch-probes/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0010
title: Repeated planner runs in .sdlc/0135-extend-the-clean-status-lint
status: candidate
pattern: replan .sdlc/0135-extend-the-clean-status-lint
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0135-extend-the-clean-status-lint/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0135-extend-the-clean-status-lint/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0135-extend-the-clean-status-lint/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0135-extend-the-clean-status-lint/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0011
title: Repeated planner runs in .sdlc/0157-review-sdlc-traces
status: candidate
pattern: replan .sdlc/0157-review-sdlc-traces
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0157-review-sdlc-traces/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0157-review-sdlc-traces/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"
- [.sdlc/.0157-review-sdlc-traces/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0157-review-sdlc-traces/runs.jsonl):3 (run) "role=planner level=L3 file=planner-L3-2.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0012
title: Repeated planner runs in .sdlc/0162-entry-files-in-step-handoffs
status: candidate
pattern: replan .sdlc/0162-entry-files-in-step-handoffs
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0162-entry-files-in-step-handoffs/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0162-entry-files-in-step-handoffs/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0162-entry-files-in-step-handoffs/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0162-entry-files-in-step-handoffs/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0013
title: Repeated planner runs in .sdlc/0166-agent-spawn-hook
status: candidate
pattern: replan .sdlc/0166-agent-spawn-hook
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0166-agent-spawn-hook/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0166-agent-spawn-hook/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0166-agent-spawn-hook/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0166-agent-spawn-hook/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0014
title: Repeated planner runs in .sdlc/0177-mailbox-core
status: candidate
pattern: replan .sdlc/0177-mailbox-core
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0177-mailbox-core/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0177-mailbox-core/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0177-mailbox-core/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0177-mailbox-core/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0015
title: Repeated planner runs in .sdlc/0178-messenger-agent
status: candidate
pattern: replan .sdlc/0178-messenger-agent
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0178-messenger-agent/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0178-messenger-agent/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0178-messenger-agent/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0178-messenger-agent/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0016
title: Repeated planner runs in .sdlc/0179-messages-entry-files
status: candidate
pattern: replan .sdlc/0179-messages-entry-files
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0179-messages-entry-files/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0179-messages-entry-files/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0179-messages-entry-files/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0179-messages-entry-files/runs.jsonl):3 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0017
title: Repeated planner runs in .sdlc/0181-messages-wait
status: candidate
pattern: replan .sdlc/0181-messages-wait
occurrences: 3
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0181-messages-wait/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0181-messages-wait/runs.jsonl):1 (run) "role=planner level=L2 file=planner-L2.md"
- [.sdlc/.0181-messages-wait/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0181-messages-wait/runs.jsonl):2 (run) "role=planner level=L3 file=planner-L3.md"
- [.sdlc/.0181-messages-wait/runs.jsonl](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0181-messages-wait/runs.jsonl):4 (run) "role=planner level=L3 file=planner-L3-2.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0018
title: Repeated planner runs in .sdlc/0184-role-result-schema
status: candidate
pattern: replan .sdlc/0184-role-result-schema
occurrences: 2
created: 2026-10-04
eval:
---

## Evidence

- .sdlc/0184-role-result-schema/runs.jsonl:1 (run) "role=planner level=L2 file=planner-L2.md"
- .sdlc/0184-role-result-schema/runs.jsonl:3 (run) "role=planner level=L3 file=planner-L3.md"

## Proposed change

Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.
```

```
---
id: P-0019
title: Repeated plan defect verdicts
status: candidate
pattern: plan-defect
occurrences: 12
created: 2026-10-04
eval:
---

## Evidence

- [.sdlc/.0081-add-a-steps-py-selftest/step-1.superseded-1/verifier-L1.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0081-add-a-steps-py-selftest/step-1.superseded-1/verifier-L1.md):16 (## For the next attempt) "plan defect: the mutant criterion says to copy `plugins/sdlc-lite/scripts/steps.py` alone to a temp dir, but steps.py does `import order` (line 76), so the c..."
- [.sdlc/.0081-add-a-steps-py-selftest/step-1.superseded-1/verifier-L1.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0081-add-a-steps-py-selftest/step-1.superseded-1/verifier-L1.md):17 (## For the next attempt) "plan defect: the (guard) says `git diff --name-only` lists no other file, but the task handoff `.sdlc/0081-add-a-steps-py-selftest/handoff.md` was modified b..."
- [.sdlc/.0092-run-a-live-probe-to/step-2.superseded-1/builder-L1.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0092-run-a-live-probe-to/step-2.superseded-1/builder-L1.md):8 (## Notes (first line required format)) "plan defect: `git diff --quiet HEAD -- plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts/hook-live-probe.sh` fails at the pre-step-2 state itself, because no..."
- [.sdlc/.0092-run-a-live-probe-to/step-2.superseded-1/builder-L1.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0092-run-a-live-probe-to/step-2.superseded-1/builder-L1.md):39 (## Notes) "plan defect: `git diff --quiet HEAD -- plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts/hook-live-probe.sh` fails at the pre-step-2 tree state, because non-..."
- [.sdlc/.0113-close-rename-breaks-refs/step-2.superseded-1/builder-L2.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0113-close-rename-breaks-refs/step-2.superseded-1/builder-L2.md):19 (## Notes) "plan defect: `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/tickets.py` cannot pass. Only merge steps commit, so step 1's tickets.py change is still unc..."
- [.sdlc/.0134-mirror-the-extended-planner-rules/step-1/verifier-L1.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0134-mirror-the-extended-planner-rules/step-1/verifier-L1.md):28 (## For the next attempt) "plan defect: criterion 4 (`git diff --stat HEAD | awk '{print $1}'` plus an empty `git ls-files --others --exclude-standard`) can never pass inside a /chain..."
- [.sdlc/.0135-extend-the-clean-status-lint/step-1.superseded-1/builder-L3.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0135-extend-the-clean-status-lint/step-1.superseded-1/builder-L3.md):23 (## Notes) "plan defect: criterion 5 (the `steps.py split "$d/t"` criterion) writes `printf 'h\n' >"$d/t/handoff.md"`, a handoff with no `## Goal` section. `split` reads..."
- [.sdlc/.0157-review-sdlc-traces/step-2.superseded-1/builder-L2.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0157-review-sdlc-traces/step-2.superseded-1/builder-L2.md):23 (## Notes) "plan defect: (guard) scope. Its regex `^(plugins/sdlc-lite/scripts/traces/.*)$` does not allow `plugins/sdlc-lite/scripts/traces.py` (the entry script, with..."
- [.sdlc/.0162-entry-files-in-step-handoffs/step-5.superseded-1/builder-L3.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0162-entry-files-in-step-handoffs/step-5.superseded-1/builder-L3.md):23 (## Notes) "plan defect: the Codex levels "builder L4, verifier L3. These levels map to `gpt-6-astra`" are wrong for the verifier. `codex_roles.resolve` switches the ver..."
- [.sdlc/.0178-messenger-agent/step-2.superseded-1/builder-L2.md](https://github.com/kimgranlund/sdlc-lite/blob/51cbf1bacc20ff563669f244978f73ff2c9d78a4/.sdlc/.0178-messenger-agent/step-2.superseded-1/builder-L2.md):26 (## Notes) "plan defect: criterion `for a in ... conductor-l1; do grep -qF messenger .../sdlc-conductor-l1.toml` assumes the conductor agent preloads level-rubric, but i..."
- .sdlc/codex-scout-luna/step-1/verifier-L1.md:17 (## For the next attempt) "plan defect: the step changed a shared contract (the scout L1 model in `adapters/codex/models.json`) but did not include its dependent doc table. `docs/codex..."
- .sdlc/verify-ticket-stages/step-1/verifier-L3.md:62 (## For the next attempt) "plan defect: criterion 10 (the em dash count guard) counts added lines, and two regenerated single-line TOML fields carry em dashes that already exist on mai..."

## Proposed change

Examine the planner rules behind these criteria and whether steps.py lint could refuse them.
```

The rehearsal with a prototype found 18 `replan` candidates and one `plan-defect` with 12 evidence lines; the real script found the same counts. No `verifier-fail`, `builder-bump`, `next-attempt`, or `follow-up` pattern reached two occurrences in this repository's records.

## Limits

- One machine, one run.
- `promote` ran only in the selftest; no ticket was filed here.
- The manifest covers the sources scan reads and `plugins/`, not logs, `.running` files, or other `.sdlc` files.
- Quotes are cut at 160 characters, so the plan-defect evidence above shows each defect's start only.
- No candidate was committed: they lived in the temp dir, and `.sdlc/proposals/` holds only its entry files.
