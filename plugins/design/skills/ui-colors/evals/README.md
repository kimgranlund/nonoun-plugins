# Triggering evals

`triggers.json` lists prompts with the route they should take: `system` (scripts/system.mjs), `source` (scripts/generate.cjs) or `none` (the skill should not run). They test the SKILL.md frontmatter description and its routing words, not the generators.

Run by hand, with a fresh model session per case so earlier cases can't prime it:

1. Start a new session with this skill installed and no other conversation.
2. Paste one `prompt` verbatim. Don't add context.
3. Record what the model did first: loaded this skill and ran `system.mjs` (system), loaded it and ran `generate.cjs` (source), loaded it and asked the one routing question (note it; it counts as correct only for a case whose `why` says it is ambiguous), or didn't load the skill (none).
4. Compare with `label`. A `none` case that loads the skill is a false trigger; a `system`/`source` case that doesn't is a miss; loading it and picking the other generator is a misroute.

Report per label: correct / total, and list the misses, false triggers and misroutes by `id`. When a case fails, change the description or the routing words in SKILL.md (not the case), and rerun every case: a tighter word for one case can break another. Add a case for each new ambiguity you find, with its `why`.

## Last run (2026-11-12)

Batched, not per-case: one fresh Sonnet session judged all 20 prompts at once, each as its own first message, given only a listing of the installed skills' descriptions (the `dataviz` line was written by hand, not copied from the host). It named the skill it would load and, for this skill, the generator; nothing was executed.

| Label | Correct | Notes |
|---|---|---|
| system | 7 / 7 | all routed to `system.mjs`; `sys-chart` notes `dataviz` as the alternative |
| source | 5 / 5 | `src-ambiguous-palette` would ask the routing question, which its `why` allows |
| none | 8 / 8 | the three sibling cases (added 2026-11-12) went to `ui-materials`, `ui-geometry` and `ui-showcase-bento`; `none-chart-code` loaded `dataviz`, not this skill |

20 / 20. Two earlier runs the same day each missed one case: `sys-wcag-audit` asked the routing question (fixed by naming the per-mode failing-pairs report in the description), then `sys-chart` went to `dataviz` (fixed by naming chart data series). The 2026-11-11 run (17 / 17, one fresh session per case) used the earlier description.

## Run after the family audit (2026-11-12)

Batched, not per-case. One fresh Sonnet session per run read a listing of twelve installed skills' descriptions (copied from their SKILL.md files; the `dataviz` line from the host's listing) and these 21 prompts mixed with ui-showcase-bento's 12, shuffled and without labels. It named the skill it would load and, for this skill, the generator, with "ask" offered as an answer; nothing was executed. Three runs: the descriptions as they were before the audit's edits, then the edited descriptions twice.

| Label | Correct | Notes |
|---|---|---|
| system | 7 / 8 | `sys-wcag-audit` picked this skill and would ask the routing question, in all three runs, the one before the edits included |
| source | 5 / 5 | `src-ambiguous-palette` went to `generate.cjs` without asking |
| none | 8 / 8 | as in the last run |

20 / 21 in each run. `sys-showcase-only`, added in this audit, went to `system.mjs` in all three runs, so these runs do not separate the old description from the new one. `sys-wcag-audit` is an open miss under this protocol: the description was not changed for it.
