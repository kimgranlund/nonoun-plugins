# Triggering evals

`triggers.json` lists prompts with the route they should take: `system` (scripts/system.mjs), `source` (scripts/generate.cjs) or `none` (the skill should not run). They test the SKILL.md frontmatter description and its routing words, not the generators.

Run by hand, with a fresh model session per case so earlier cases can't prime it:

1. Start a new session with this skill installed and no other conversation.
2. Paste one `prompt` verbatim. Don't add context.
3. Record what the model did first: loaded this skill and ran `system.mjs` (system), loaded it and ran `generate.cjs` (source), loaded it and asked the one routing question (note it; it counts as correct only for a case whose `why` says it is ambiguous), or didn't load the skill (none).
4. Compare with `label`. A `none` case that loads the skill is a false trigger; a `system`/`source` case that doesn't is a miss; loading it and picking the other generator is a misroute.

Report per label: correct / total, and list the misses, false triggers and misroutes by `id`. When a case fails, change the description or the routing words in SKILL.md (not the case), and rerun every case: a tighter word for one case can break another. Add a case for each new ambiguity you find, with its `why`.

## Last run (2026-11-11)

One fresh Sonnet 5.5 session per case, given only the prompt and its own skill listing; it named the skill it would load and, for this skill, the generator SKILL.md routes to (nothing was executed).

| Label | Correct | Notes |
|---|---|---|
| system | 7 / 7 | all routed to `system.mjs` |
| source | 5 / 5 | `src-ambiguous-palette` chose source and noted the routing question would also fit |
| none | 5 / 5 | `none-font` loaded a UI-kit skill, `none-chart-code` a dataviz skill — neither loaded this one, which is what the case tests |

17 / 17: no misses, false triggers or misroutes.
