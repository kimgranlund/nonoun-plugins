# Industry standards and alternatives to plan, build, verify, close

Recorded: 2026-10-12, for T-0493 (architect L1, one pass). Question: what are the industry standards and credible alternatives to our plan, build, verify, close system, what does the evidence say about each, and which open tickets should change because of it. No code or ticket was edited; the maintainer files changes.

Method: four researcher L1 sub-agents ran WebSearch in standard mode (12 searches each, two continuations of 5) over the pattern families the ticket names; this pass read their rows against the local reports named below and the open queue. Every claim carries one of four tiers: `published` (a paper, a reproducible leaderboard entry, a third-party measurement, or a production writeup with numbers), `vendor claim` (the vendor's own post or docs, no outside reproduction), `inference` (this report's reading), `unverified` (a number the researcher could not source, or a secondary summary of a primary source that was not opened). A row whose number comes from a secondary summary says so. Dates are publication dates; `arXiv ID` means the month was taken from the identifier.

Local evidence base: `docs/reports/2026-10-11-solo-campaign-baseline.md`, `docs/reports/2026-10-11-solo-fails-and-blocks.md`, `docs/reports/solo-vs-lean-benchmark-2026-10-04.md`, `docs/kpi/005-solo-first-pass-rate.md`, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`, `docs/reports/2026-10-12-fleet-retro-00.md`, `docs/reports/fleet-retro-2026-10-06.md`, `docs/reports/2026-10-07-fleet-retro-05.md`, `docs/specs/sdlc-lite/pillars.md`, `docs/planning/merge-ops-and-queue.md`, `docs/planning/light-merge-lane.md`. Closed `.NNNN-*` folders were not read.

Result in one line: the published record supports execution feedback from reliable tests and an independent judge off the producer's model family; it does not support generator and critic loops without an external signal, role-based multi-agent teams on coding, or spec-first tooling (no outcome data exists); merge-queue gains come from batching under contention at hundreds of engineers and do not transfer to a one-maintainer repo, where the measured cost is hand-resolved generated files. Four queue changes follow, all small; none adds a new pattern.

## 1. The patterns and the evidence

### 1.1 Single agent loop (ReAct, Claude Code and Cursor defaults, plan mode)

| Claim | Number or result | Source | Date | Tier |
|---|---|---|---|---|
| ReAct beats act-only and imitation baselines on ALFWorld and WebShop | ALFWorld 71 vs 45 (act-only) vs 37 (IL); WebShop 40 vs 30.1 vs 29.1 | https://arxiv.org/pdf/2210.03629 | 2022-10-06 | published |
| ReAct trades hallucination for reasoning errors (50 trajectories per method, HotpotQA) | hallucination 56 percent (CoT) vs 0 (ReAct); reasoning errors 16 vs 47 percent | same | 2022-10-06 | published |
| SWE-agent, a single ReAct-style loop with a custom agent-computer interface, on SWE-bench | 12.47 percent of 2,294 (GPT-4 Turbo); interface vs plain shell on Lite 18.00 vs 11.00 percent | https://arxiv.org/abs/2405.15793 | 2024-05 (arXiv ID) | published |
| SWE-agent failure profile | 52.0 percent of unresolved runs are wrong or over-specific patches; 23.4 percent cascading failed edits | https://hyper.ai/papers/2405.15793 (summary) | 2024-05 | published, secondary summary |
| OpenHands CodeAct 2.1 on SWE-bench Lite | 41.67 percent, about $1.33 per instance | https://openhands.dev/blog/openhands-codeact-21-an-open-state-of-the-art-software-development-agent | 2024-11 | vendor claim |
| OpenHands cost spread, same model and dataset, different settings | 30.7 percent at about $0.065 per instance vs 43.3 percent at about $6.20 | https://huggingface.co/datasets/OpenHands/openhands-evaluation-outputs/blob/main/outputs/analysis_report.jsonl | undated | unverified |
| Claude Code plan mode is a read-only permission mode until the user approves a plan | no quantitative claim on the page | https://code.claude.com/docs/en/permission-modes | undated | vendor claim |
| Claude Code sub-agents: own context window, summary returns; limits 20 concurrent, depth 3 | no outcome data | https://code.claude.com/docs/en/sub-agents | undated | vendor claim |
| Cursor plan mode: research, clarifying questions, reviewable plan; 2.2 adds judging of parallel agents | no outcome data; the default agent loop is not documented | https://cursor.com/blog/plan-mode and https://cursor.com/changelog/2-2 | undated | vendor claim |

Reading (inference): the single loop is the baseline every other pattern is measured against, and its measured lever is the tool interface and the test signal, not the loop shape. Our solo lane is this pattern with a brief, a budget and a stop rule.

### 1.2 Plan, then execute, then human review (Devin, Copilot Workspace and coding agent, OpenHands)

| Claim | Number or result | Source | Date | Tier |
|---|---|---|---|---|
| Devin on a random 25 percent of SWE-bench | 13.86 percent (79 of 570) vs 1.96 percent unassisted baseline; harness published | https://cognition.ai/blog/swe-bench-technical-report | 2024-03 | vendor claim (no independent rerun found) |
| Answer.AI hands-on test of Devin, 20 tasks | 3 successes, 14 failures, 3 inconclusive; overcomplicated code, hallucinated features, loops, ignored conventions | https://www.answer.ai/posts/2025-01-08-devin | 2025-01-08 | published (third-party) |
| Devin PRs merged | 67 percent, up from 34 percent | https://cognition.ai/blog/devin-annual-performance-review-2025 | undated | vendor claim |
| Devin public PR merge rate, third-party count | 60.3 percent (38,374 of 63,599) over 8 weeks to 2026-08-16 | https://amplifying.ai/coding-agents/devin | 2026-08-16 | published (third-party) |
| Copilot Workspace sunset; approach carried into the Copilot coding agent | sunset 2025-05-30 | https://githubnext.com/projects/copilot-workspace | 2025-05-30 | vendor claim |
| Agent PR merge rates in the AIDev dataset (33k agent PRs) | Copilot 43.04 percent vs OpenAI Codex 82.59 percent | https://arxiv.org/abs/2601.15195 | 2026-01 (arXiv ID) | published |
| Copilot merge rate on other populations | 77.44 percent (Logicstar tracker); 68.1 percent (secondary summary of arXiv 2607.21832) | https://insights.logicstar.ai | undated | unverified |
| OpenHands paper | 26 percent on SWE-bench for CodeActAgent v1.8 (Claude 3.5 Sonnet); Lite and cost tables not read | https://arxiv.org/abs/2407.16741 | 2024-07-23 | published, secondary summary |

Reading (inference): no controlled comparison of plan-then-execute-then-review against a plain loop was found. The pattern's outcome metric in production is the PR merge rate, which varies by population from 43 to 83 percent and is measured by third parties, not the vendor.

### 1.3 Test-driven and execution-feedback loops (SWE-agent, Aider, Agentless)

| Claim | Number or result | Source | Date | Tier |
|---|---|---|---|---|
| Agentless, a fixed localize-repair-validate pipeline with no agent loop, on SWE-bench Lite | v1 27.33 percent at $0.34 per issue; later 32.00 percent at $0.70; FSE 2025 version 32.67 percent at $0.68 | https://arxiv.org/abs/2407.01489 and https://conf.researchr.org/details/fse-2025/fse-2025-research-papers/85/Demystifying-LLM-based-Software-Engineering-Agents | 2024-07-01; 2025 | published (version split unverified) |
| Agentless ablation: test-based patch selection | 77 fixes (majority vote), 81 (plus regression tests), 96 (plus reproduction tests) | https://arxiv.org/pdf/2407.01489 | 2024-07 | published |
| Aider architect and editor split | 85 percent vs 79.7 percent for o1-preview alone on Aider's benchmark; o1 plus Sonnet no better than o1 alone | https://aider.chat/2024/09/26/architect.html and https://aider.chat/2025/01/24/r1-sonnet.html | 2024-09-26; 2025-01-24 | vendor claim |
| Reflexion with unit-test feedback on HumanEval | 91.0 vs 80.1 percent pass@1 (independent replication 89.4 vs 81.7); on MBPP 77.1, below the 80.1 baseline, blamed on false-positive internal tests | https://arxiv.org/pdf/2303.11366 | 2023-03 | published |
| Generated tests help only when they reproduce the bug (TDFlow) | 93.3 percent with zero bad tests vs 68.0 percent with self-generated tests | https://arxiv.org/pdf/2510.23761 | 2025-10 (arXiv ID) | published |
| Strengthened test suites reject patches the original tests accepted (SWE-ABS) | 19.78 percent of accepted patches rejected; top agent 78.8 falls to 62.2 percent | https://icml.cc/media/icml-2026/Slides/62669.pdf | 2026 | published (slides) |
| Weak tests inflate SWE-bench (SWE-Bench+) | 24.70 percent of successful patches suspicious; SWE-agent plus GPT-4 falls from 12.47 to 4.58 percent | https://yorkspace.library.yorku.ca/items/39fdcdf5-f606-4b77-b59a-27ed480838fa/full | 2024 | published |

Reading (inference): this is the pattern family with the clearest positive evidence, and the clearest caveat: the gain is the test's, not the loop's, and a weak or non-reproducing test turns the signal into noise. Our `(red)` criteria, the red checkpoint and the negative-control rule are the local form of the Agentless reproduction-test ablation.

### 1.4 Generator and critic (Reflexion, Self-Refine, debate, LLM-as-judge, AI code review)

| Claim | Number or result | Source | Date | Tier |
|---|---|---|---|---|
| Self-Refine across 7 tasks | about +20 percent absolute on average; code up to +13 percent; gains diminish after 2 to 3 iterations | https://arxiv.org/abs/2303.17651 | 2023-03 | published |
| Self-correction without external feedback does not help reasoning and sometimes degrades it; debate no better than self-consistency at equal responses | debate 83.0 vs self-consistency 88.2 percent | https://arxiv.org/abs/2310.01798 | 2023-10-03 | published |
| Self-repair gains modest once repair cost is counted; the model's own feedback is the bottleneck; a stronger model's feedback helps | pass rates unverified | https://arxiv.org/abs/2306.09896 | 2023-06 | published |
| Critical survey: no success with feedback from prompted LLMs except on suited tasks; reliable external feedback works | qualitative | https://arxiv.org/abs/2406.01297 | 2024-06 (arXiv ID) | published |
| Simple baselines (retries, temperature, model escalation) match Reflexion, LATS and LDB on HumanEval at up to 50x lower cost; cost is rarely reported | 5 runs each, 164 problems | https://arxiv.org/abs/2407.01502 | 2024-07-01 | published |
| LLM judges prefer their own output; self-recognition correlates with self-preference | summarization, GPT-4, Llama 2, GPT-3.5 | https://arxiv.org/abs/2404.13076 | 2024-04 | published |
| An agentic reviewer with repo access, then revise, raises resolve rate (SWE-Review) | 27.5 to 56.9 percent and 50.9 to 68.8 percent (Qwen3 30B variants) | https://arxiv.org/pdf/2607.06065 | 2026-07 (arXiv ID) | published, secondary summary, numbers unchecked |
| Replacing a selection mechanism with LLM-as-judge got worse results at extra cost (SWE-Replay) | trajectory selection, not code review | https://arxiv.org/pdf/2601.22129 | 2026-01 (arXiv ID) | published |
| Vendor review benchmarks | Qodo F1 60.1 percent on its own benchmark; CodeRabbit F1 about 51 percent, recall 52.5 vs 36.7 percent for Copilot on the Martian benchmark | https://qodo.ai/ai-code-review-benchmark/ and https://coderabbit.ai/blog/coderabbit-tops-martian-code-review-benchmark | undated; 2026-03-03 | vendor claim |
| Google ML-suggested edits resolve reviewer comments | 7.5 percent of comments (earlier about 5 percent); a later system 27.5 and 28.7 percent accepted on a different denominator | https://research.google/pubs/resolving-code-review-comments-with-machine-learning/ and https://arxiv.org/pdf/2507.13499 | 2024; 2025-07 | published |

Reading (inference): a critic that shares the generator's model and has no external signal is the pattern the evidence rejects. A critic with an external signal (tests, repo access) and a different model is the one it supports, and that is the shape of our verifier.

### 1.5 Multi-agent roles (MetaGPT, ChatDev, CrewAI, AutoGen, Anthropic research system)

| Claim | Number or result | Source | Date | Tier |
|---|---|---|---|---|
| MetaGPT pass@1 on HumanEval and MBPP; role ablation | 85.9 and 87.7 percent; engineer only $0.915 and executability 1.0 vs all four roles $1.385 and 4.0 | https://arxiv.org/html/2308.00352v7 | 2023-08-01 (v7 2024-11-01) | published (authors' own benchmark) |
| ChatDev vs GPT-Engineer and MetaGPT on the ChatDev authors' benchmark | executability 0.88 vs 0.358 and 0.4145; tokens 22,949 vs 7,183 and 29,279; time 148 s vs 15.6 s; the authors say multi-agent "needs more tokens and time" and gains "may be overestimated" | https://arxiv.org/html/2307.07924v5 | 2024-06-05 (v1 2023-07-16) | published (authors' own benchmark) |
| MetaGPT and ChatDev each lead on their own benchmark | executability 3.75 vs 2.25 in MetaGPT's paper, the reverse in ChatDev's | both | 2024 | published, conflicting |
| Anthropic multi-agent research system | +90.2 percent over single-agent Opus 4 on an internal eval; agents use about 4x the tokens of chat, multi-agent about 15x; token use explains 80 percent of variance; "most coding tasks involve fewer truly parallelizable tasks than research" | https://www.anthropic.com/engineering/multi-agent-research-system | 2025-06-13 | vendor claim |
| Failure taxonomy of multi-agent systems (MAST) | 14 modes in 3 categories over 1,600 traces, 7 frameworks; the abstract opens with "minimal performance gains" on popular benchmarks | https://arxiv.org/abs/2503.13657 | 2025-03-17 | published |
| Single agent matches or beats multi-agent at equal thinking-token budget (multi-hop QA, not coding) | abstract gives no percentages; one secondary number 0.418 vs 0.327 on MuSiQue | https://arxiv.org/abs/2604.02460 | 2026-04-02 | published; number unverified |
| AutoGen framework paper | abstract gives no quantitative result; results sections not read | https://arxiv.org/abs/2308.08155 | 2023-08-16 | published (no numbers read) |
| CrewAI | qualitative speed claim; no benchmark | https://github.com/crewAIInc/crewAI | undated | vendor claim (no outcome data) |

Reading (inference): no coding benchmark shows a role team beating a single strong agent at equal compute; the cost side is consistent across sources (3x to 15x tokens). Our chain is role-based but sequential, and its measured overhead sits in planning and plan review, not in the role count (section 2).

### 1.6 Spec-driven (Kiro, Spec Kit, Tessl)

| Claim | Number or result | Source | Date | Tier |
|---|---|---|---|---|
| AWS Kiro launch | "implement more complex tasks in fewer shots"; no number | https://www.constellationr.com/insights/news/aws-launches-kiro-ide-powered-ai-agents | 2025-07-14 | vendor claim |
| GitHub Spec Kit launch; GitHub calls it an experiment to test spec-driven development | no outcome data | https://visualstudiomagazine.com/articles/2025/09/03/github-open-sources-kit-for-spec-driven-ai-development.aspx | 2025-09-03 | vendor claim |
| Spec Kit Agents preprint (hooks vs no hooks, not spec vs no spec) | judge score +0.15 on a 1 to 5 scale; SWE-bench Lite +1.7 points to 58.2 percent | https://arxiv.org/abs/2604.05278 | 2026-04-07 | published (preprint) |
| Four-month Spec Kit pilot | no outcome numbers in the abstract | https://arxiv.org/abs/2605.01160 | 2026-05-01 | published (no outcome data) |
| Tessl Spec Registry and Framework | "over 10,000 specs"; no measured effect on task success | https://tessl.io/blog/announcing-tessls-products-to-unlock-the-power-of-agents/ | 2025-09-16 | vendor claim |
| Self-planning code generation (prompting study) | up to +25.4 percent relative pass@1 over direct generation | https://arxiv.org/pdf/2303.06689 | 2023-03 | published |
| "3 to 10x first-pass success" and "25 percent faster" for spec-driven tools | appear only on blogs with no primary source | https://ssojet.com/blog/best-spec-driven-development-tools | undated | unverified |

Reading (inference): spec-first tooling has launch posts and one hooks ablation; it has no published outcome data a year after launch. The only published planning gain is a prompting-level result on function synthesis. Our planner, plan reviewer and `/clarify` are spec-first machinery, and the local data (section 2) is the only outcome data on it we have.

### 1.7 Trunk-based CI with merge queues and trains

| Claim | Number or result | Source | Date | Tier |
|---|---|---|---|---|
| GitHub's own merge queue, 500 engineers | trains before the queue held up to 15 PRs with 8 hour waits; after: 2,500 PRs a month, average wait down 33 percent, batches of 30 plus | https://github.blog/engineering/engineering-principles/how-github-uses-merge-queue-to-ship-hundreds-of-changes-every-day | 2024-03-06 | published (production writeup) |
| Uber SubmitQueue follow-up | CI resources down about 53 percent, CPU down 44 percent, P95 wait down 37 percent (Go monorepo 33.69 to 18.64 min) | https://arxiv.org/html/2501.03440v2 | 2025-05-19 (v2) | published |
| Uber SubmitQueue original (EuroSys 2019) | numbers not extracted | https://www.uber.com/en-US/blog/bypassing-large-diffs-in-submitqueue/ | 2019 | unverified |
| Google continuous testing: few tests ever fail, failures concentrate near the code under test | share-of-tests figure not extracted | https://research.google/pubs/taming-google-scale-continuous-testing/ | 2017 | published |
| Bors "not rocket science rule": main always passes its tests because the merge result is tested, then promoted | no outcome data | https://bors.tech/newsletter/2017/04/30/tmib-04 and https://github.com/graydon/bors | 2017-04-30 | vendor claim (project docs) |
| Zuul dependent pipeline: tests each change as it will merge, speculatively in parallel; a failure ahead retests the rest without it; a window caps speculation | no throughput number | https://docs.openstack.org/infra/zuul/gating.html | undated | vendor claim (project docs) |
| GitLab merge trains, since 12.0 | no throughput number | https://docs.gitlab.com/ci/pipelines/merge_trains/ | 2019 (version line from a mirror, unverified) | vendor claim |
| Meta Sapling and stacked diffs | small individually reviewed commits stacked; no numbers | https://engineering.fb.com/2022/11/15/developer-tools/sapling-source-control-scalable/ | 2022-11-15 | vendor claim |
| Atlassian Jira merge queue | semantic merge failures 7 to 10 percent before, near zero after; build 40 to 35 min | https://www.atlassian.com/blog/bitbucket/merge-queues-how-we-ship-faster-with-fewer-incidents | undated | vendor claim |
| Serial queue ceiling | 30 min CI gives at most 2 PRs an hour; derived arithmetic | https://tianpan.co/blog/2026/07/02/the-merge-queue-is-the-new-bottleneck and https://blog.mergify.com/announcing-speculative-merge-queues | 2026-07-02; undated | vendor claim |
| A merge queue building on the wrong base reverted commits on customers' main | uncorroborated, competitor's post | https://trunk.io/blog/what-happens-if-a-merge-queue-builds-on-the-wrong-commit | undated | unverified |

Reading (inference): every published number here is a batching or speculation gain under contention from hundreds of engineers. The rule that transfers to any size is bors's: test the merge result, then promote by fast-forward. That rule is already ours (`settle` is ff-only after a gate). What is not ours is the forward merge with mechanical resolution, which is what the local data says costs (section 2).

### 1.8 Human code review plus CI

| Claim | Number or result | Source | Date | Tier |
|---|---|---|---|---|
| Review's stated motive is defects; outcomes skew to code improvement and knowledge transfer | percentages not extracted | https://2013.icse-conferences.org/content/expectations-outcomes-and-challenges-modern-code-review.html | 2013 | published |
| Review practices converge across Google, Microsoft and AMD; review raises files a developer knows by 66 to 150 percent | reviewer count not extracted | https://www.microsoft.com/research/publication/convergent-software-peer-review-practices/ | 2013 | published |
| Google: median review latency under 4 hours, 4 reviews per developer per week, 9M changes | | https://research.google/pubs/modern-code-review-a-case-study-at-google/ | 2018 | published |
| Low review coverage and participation link to post-release defects (Qt, VTK, ITK); did not replicate at Sony Mobile | | https://rebels.cs.uwaterloo.ca/confpaper/2014/05/30/the-impact-of-code-review-coverage-and-code-review-participation-on-software-quality.html and https://swag.uwaterloo.ca/publications/a-study-of-the-quality-impacting-practices-of-modern-code-review-at-sony-mobile.html | 2014; 2016 | published |
| DORA 2024: a 25 percent rise in AI adoption goes with throughput down 1.5 percent and stability down 7.2 percent; 39 percent report little trust in AI code | modeled association; the lead researcher says the data cannot say why | https://www.infoq.com/news/2024/11/2024-dora-report/ | 2024-11 | published, secondary coverage (dora.dev not read) |

Reading (inference): human review is justified in the literature by knowledge transfer and coverage, not by defect yield, and its latency floor is hours. For a one-person repo its function is the independent judge, which section 3 covers.

### 1.9 Patterns the ticket's list misses that the evidence shows are now standard

- Speculative or batched queues. The queue gains at GitHub, Uber, Zuul and Mergify all come from speculation and batching; a serial queue is a documented bottleneck (1.7). Inference: a serial queue is only worth it where CI time, not conflict resolution, is the cost.
- PR merge rate in production as the agent outcome metric. The AIDev dataset and the third-party Devin tracker measure merge rate per agent (1.2), where vendors publish benchmark scores. Inference: our K-005 first-pass rate is this metric one stage earlier.
- Auditing the gate itself. SWE-Bench+, SWE-ABS and TDFlow (1.3) each show that test strength changes the score by 10 to 25 points. Inference: a verification gate's own discrimination is a measured quantity, which is what our negative-control rule enforces per check.
- No-agent fixed pipelines. Agentless (1.3) is now a standard baseline: a fixed three-phase pipeline at under a dollar per issue beat agent loops in 2024. Inference: our solo lane with a typed brief is closer to this than to a free agent loop.
- Reviewer-with-repo-access then revise. SWE-Review (1.4, numbers unchecked) is the one published positive reviewer result, and it is a reviewer that runs code, not one that reads a diff.

## 2. Our measured data against the patterns

| Local fact | Value | Source | Pattern it speaks to |
|---|---|---|---|
| Solo against the chain, three tickets | same checked outcome at one seventh the wall time (18 vs 120 min) and one tenth the cost ($2.66 vs $26.83); planner L3 replan plus Fable plan review were about 84 percent of lean spend on the two harder tasks | `docs/reports/solo-vs-lean-benchmark-2026-10-04.md` lines 17 to 30 | 1.1 vs 1.5 and 1.6: a role chain costs where the multi-agent literature says it costs (tokens), and the spend is in planning, the spec-first step |
| Planning plus plan review share of spend | 55.5 percent (agent-ui, $436 of $787); 29 percent (maison), 34 percent (agent-ui, later window); verifiers 7.5 percent | `docs/reports/fleet-retro-2026-10-06.md` line 16; `docs/reports/2026-10-07-fleet-retro-05.md` lines 22 to 23; `docs/specs/sdlc-lite/pillars.md` line 35 | 1.6: spec-first steps are the measured overhead here, and no published number says they buy accuracy |
| Solo first-pass rate | 89 of 123 (72 percent) first-round pass; 107 of 123 (87 percent) ended in pass; 43 of 166 solo tickets had no verifier | `docs/reports/2026-10-11-solo-campaign-baseline.md` lines 5 to 13; `docs/kpi/005-solo-first-pass-rate.md` | 1.2: comparable to the 43 to 83 percent PR merge rates; 1.4: the verifier changes the outcome on 28 percent of first rounds |
| Verifier over-reach | 0 of 34 first-round non-passes; 22 builder gaps, 9 criterion defects | `docs/reports/2026-10-11-solo-fails-and-blocks.md` lines 5, 52 to 57 | 1.4: an independent, different-family judge with repo access did not produce false fails in this sample |
| Cost per solo run | about $3 and 20 minutes (sdlc-lite, 75 priced runs, $222.93); maison estimate about $0.51 and 5 minutes | baseline line 17; `docs/reports/2026-10-12-fleet-retro-00.md` row 11 | 1.3: the same order as Agentless ($0.34 to $0.70 per issue) and OpenHands ($1.33) |
| Wave merge conflicts | 5 of 8 first-parent wave merges hand-resolved, 4 of them on generated files (`roadmap.md`, `.sdlc/AGENTS.md`); cause is two generators of one derived file on two branches | `docs/planning/merge-ops-and-queue.md` lines 16, 18 | 1.7: the local merge cost is conflict resolution, not CI wait; batching does not address it |
| Gate waits | three 1800 s lock waits in waves 42 and 43, each for a cheap gate; no `--priority` passed by `fanout.py` | `docs/planning/merge-ops-and-queue.md` line 18 | 1.7: priority and speculation are where the published queue gains sit |
| Maison wave 7b | verifier spend 303 runs, $216.35, 867 min driven by stale criteria and undeclared holds; one 2.5 h silent agent; 4 plan versions | `docs/reports/2026-10-12-maison-wave-7b-mechanics.md` lines 7, 26 | 1.3: a wrong test criterion costs the way TDFlow's bad tests cost; 1.6: replanning is the spec-first overhead again |
| Lean lane planning refusals | both lean replans followed a planner L2 plan refused at `steps.py split` | benchmark line 37 | 1.6: the plan gate catches plan defects, at $7 to $14 per task |

Inference from the table: our data agrees with the published record on three points (a single loop with tests is the cheap path; roles cost tokens; a different-family judge does not over-reach) and adds one the literature lacks: the cost of the spec-first step in a role chain, measured at 29 to 84 percent of spend. Nothing local tests whether a verified solo pass met intent (the benchmark names this gap at line 38; K-005 at line 22).

## 3. What our system does that no surveyed pattern does

Each item: whether a surveyed pattern does it, then the local evidence for and against keeping it.

### 3.1 Independent verifier on a different model family

Surveyed: partly. Human review plus CI is the industry's independent judge (1.8); SWE-Review is the one published LLM reviewer with repo access that raised resolve rates (1.4, unchecked). No surveyed agent system enforces a different model family for the judge. Published support for the family rule: self-preference bias in LLM judges (https://arxiv.org/abs/2404.13076) and the self-repair finding that a stronger or different model's feedback raises gains where the model's own does not (https://arxiv.org/abs/2306.09896). Published evidence against reviewer loops in general: Kapoor et al. (https://arxiv.org/abs/2407.01502), critic loops at up to 50x cost with no gain on HumanEval, and Huang et al. (https://arxiv.org/abs/2310.01798).

Local for: 0 over-reach in 34 non-passes; the verifier changed the outcome on 28 percent of first rounds; verifiers were 7.5 percent of spend where planning was 55 percent (pillars line 35); `dispatch.py prepare` enforces the family rule mechanically (`plugins/sdlc-lite/agents/solo.md` line 51; `skills/level-rubric/SKILL.md` line 56). Local against: 43 of 166 solo tickets ran with no verifier under the docs-only and L1 defaults, and no local measurement tests whether a verified pass met intent. Verdict (inference): keep; the evidence supports a judge with an external signal and a different family, which is this one, and the pillars rule 2 keeps it. The open question is not whether to keep it but whether the L1 and docs-only skips are safe, which needs a result record to measure (T-0485).

### 3.2 Observed negative controls and the red checkpoint

Surveyed: no. No surveyed pattern requires a check to be observed red before the fix. The mechanism it enforces is the one Agentless (77 to 96 fixes with reproduction tests, https://arxiv.org/pdf/2407.01489), TDFlow (93.3 vs 68.0 percent, https://arxiv.org/pdf/2510.23761) and SWE-ABS (78.8 to 62.2 percent) measured: a test that does not discriminate inflates the pass rate by 10 to 25 points.

Local for: 9 of 34 first-round non-passes were criterion defects (a span that can never pass, a lane-unsatisfiable row), the class the rule exists to catch before a builder runs (`2026-10-11-solo-fails-and-blocks.md` lines 44 to 47); K-004 exists for it with no baseline yet. Local against: the red checkpoint produced a process deviation on every resumed maison attempt (finding 6, `2026-10-12-maison-wave-7b-mechanics.md` line 16), a cost the rule's mechanics, not its principle, caused; T-0473 moved the phase read to the working tree (`plugins/sdlc-lite/scripts/redck.py` docstring). Verdict (inference): keep the rule; the remaining cost is the resume semantics, which T-0486 touches (section 4).

### 3.3 Per-ticket budget stops

Surveyed: no. No surveyed pattern stops a run at a dollar cap and asks; the adjacent evidence is Kapoor et al.'s finding that agent papers rarely report cost at all and that cost-controlled comparisons change the ranking (https://arxiv.org/abs/2407.01502), and the OpenHands cost spread of about 95x for 12.6 points (1.1, unverified).

Local for: solo runs average about $3 against a $10 default cap and about 20 minutes against a 45 minute L2 budget (`agents/solo.md` line 23; `scripts/budget.py` docstring); the stop has never been the cause of a first-round fail in the 34 read. Local against: 113 of 192 baseline runs were unmetered (K-001), so the cap could not fire on them, and no local record shows a budget stop that saved a runaway. Verdict (inference): keep, as the cheapest form of the cost-reporting discipline the literature asks for; its value is unproven only because the runs it would have stopped were unmetered.

## 4. Verdicts on the open queue

Fifteen proposed tickets (`.sdlc/roadmap.md`, 2026-10-12). One verdict each, with the industry line and the local line.

| Ticket | Verdict | Industry line | Local line |
|---|---|---|---|
| T-0443 overlays for other roles and levels (L3) | defer, pending the maintainer's call on T-0458; close as dropped if that call is drop | per-level prompt overlays have no surveyed analogue and no published outcome data | the retest reads `Verdict: drop` and says it never reached the ticket's question (`docs/reports/2026-10-12-builder-overlay-retest.md` lines 5, 13, 53); the handoff itself says drop on a drop |
| T-0463 skill hints and question UI with a parity lint (L3) | keep, beside T-0469 after B as filed | none; a consistency lint is maintenance, not a pattern | quality pillar measure "concepts and tables that must agree" (`pillars.md` line 13); no cost or first-pass number depends on it |
| T-0465 `/plan compaction` (L3) | keep, after T-0467 as filed; reshape: record the before baseline it names before building | no surveyed pattern authors a context-compaction prompt; nothing to compare against | the only ticket in the cluster with an outcome metric (re-asked questions after compaction), currently unmeasured; the measure makes the build judgeable |
| T-0467 plan merge A (L3) | keep | spec-first tooling has no published outcome data (1.6); the merge changes skill count, not the pattern | planning is 29 to 55 percent of spend; the merge does not reduce it by itself, but its replay records lint refusals per plan artifact, the first per-plan measure of planning waste |
| T-0468 plan merge B stubs (L2) | keep, sequenced after A | none | mechanical follow-through of A; one writer on `check.py` at a time |
| T-0469 plan merge C `--summary` cost line (L2) | keep, after B as filed (`depends: [T-0468]`); the cluster's one cost measure | Kapoor et al.: cost is the unreported variable in agent comparisons (1.4) | the `--summary` cost line is the only queued item that puts a dollar figure on a plan before it runs; cost pillar measure "planning share of spend" |
| T-0482 board shows uncovered light merges (L2) | keep, low priority | Zuul and GitLab cancel obsolete pipelines and show what is untested (1.7); visibility of uncovered work is standard | T-0481 is built; the light-merge design's own risk list says an uncovered merge sits in integration undetected until `cover` (`docs/planning/light-merge-lane.md` lines 74 to 75); the saving is maison's, not this repo's |
| T-0485 solo has no validatable result file (L1) | keep, move up to the top of the queue | the production outcome metric for agents is a per-run record (merge rate, 1.2); every benchmark in section 1 depends on one | the benchmark (line 38) and K-005 (line 22) both say solo's quality claim is untested; 43 of 166 solo tickets had no verifier; a `results.py validate --role solo` record is the prerequisite for measuring either |
| T-0486 red checkpoint marked retrospective (L1) | reshape: rerun the T-0316 repro on main first, since T-0473 moved the phase read to the working tree at HEAD; if still red, fold it into the finding 6 resume-semantics ticket the mechanics report ranks second (not yet filed) | test-quality auditing is standard (1.9); a checkpoint that misreads its own phase is a gate auditing itself wrong | `redck.py` docstring (T-0473) and `2026-10-12-maison-wave-7b-mechanics.md` line 16 (finding 6) describe the same mechanism; the ticket's cause line is a guess |
| T-0487 `loaded_context` rollout absent on codex exec (L1) | keep, defer below the Codex-independent tickets | none | the record binds evidence to the context loaded (quality pillar, "claims bound to evidence"); Codex-only, no cost number |
| T-0489 `settle --forward` (L3) | keep, first in the merge cluster | bors rule, test the merge result then promote (1.7), already ours; the published queue gains (33 percent wait, 53 percent CI) are batching under contention and do not transfer | 5 of 8 wave merges hand-resolved, 4 on generated files; the forward merge with regeneration is the only queued change that removes a measured per-wave hand step |
| T-0490 solo worktree default when a lane is open (L2) | defer | none | the design's own finding: the conflicts came from the maintainer's filing commits on main, not from builds in the checkout (`merge-ops-and-queue.md` lines 16, 66); no measured case; 7 closable lanes already pile up |
| T-0491 land gates at `--priority 1`, `ahead` and `blocking` in status (L1) | keep, beside T-0489 | Uber 2025: P95 wait is the queue measure that moves (1.7); priority and speculation are where the gains sit | three 1800 s waits for cheap gates; `fanout.py` passes no `--priority`; cheapest fix in the cluster |
| T-0492 merge ops duty block (L2) | keep, after T-0489 as filed; reshape: the block must name `lanes.py list --stale` as the check that a settle or sweep was skipped | GitHub's writeup: the queue replaced a hand-run train that derailed (1.7); the duty is what makes the scripts run | 7 closable lanes left behind with no script that notices a skipped sweep (`merge-ops-and-queue.md` line 18) |
| T-0493 this spike (L3) | close on this report | | |

## 5. Ranked changes to the queue

At most five. Cost is this repo's measured solo run (about $3 and 20 minutes a run, baseline line 17) scaled by level, so an estimate (inference). Pillar names follow `docs/specs/sdlc-lite/pillars.md`; a worsened measure is named on the line.

1. Move T-0485 to the top and keep its L1 size. Cost: one solo run, about $3 and 20 minutes, plus one verifier round. Pillar: quality (verifier first-pass rate and claims bound to evidence); it is the prerequisite for testing the one claim both local reports leave open, that a verified solo pass met intent. Worsens nothing.
2. Order the merge cluster T-0489, then T-0491 beside it, T-0492 after, and defer T-0490. Cost: T-0489 is L3, about $5 to $15 and an hour on the benchmark's range for a replanned task; T-0491 about $3. Pillar: performance (wall minutes per closed ticket: one hand merge per wave removed) and cost (no 1800 s waits on cheap gates). Worsens resilience's "runs lost" measure only if `settle --forward` regenerates over a real conflict, which its exit 2 control guards.
3. Reshape T-0486 into a 10 minute rerun on main before any build; close if green, else fold into the finding 6 ticket. Cost: under $1. Pillar: cost (an L1 build on a cause that T-0473 may have removed). Worsens nothing.
4. Defer T-0443 to the maintainer's decision on T-0458 and close it as dropped on a drop. Cost: zero now; saves an L3 build (about $10) on an A/B that could not bite. Pillar: cost. Worsens nothing; the pillars rule 4 (cut effort data shows buys nothing) applies.
5. The plan-skill cluster order stands (A, B, then C and T-0463 in parallel, T-0465 after A). The one change: T-0465 records the before baseline its outcome metric names (re-asked questions after a free `/compact`) before it builds, so the build is judgeable. Cost: one replay, under $3. Pillar: cost (planning share of spend becomes visible per plan through T-0469's `--summary` and T-0467's refusal counts; T-0465's measure joins them). Worsens nothing.

Not changed, and why: no new ticket for a generator-critic loop, an LLM diff reviewer, a role team, or spec-first tooling; the published evidence in 1.4 to 1.6 does not support any of them beyond what the independent verifier already is, and the pillars filter requires a named measure they would move.

## 6. Unverified

- Every row marked `unverified` or `secondary summary` in section 1: the Uber 2019 numbers, the Memon test-share figure, the Bacchelli and Bird and Rigby and Bird percentages, the AutoCommenter acceptance numbers, the SWE-Review resolve rates, the Devin 67 percent definition, the DORA sample size (39,000 vs 3,000 by source), the Agentless version split, the OpenHands cost spread, the GitLab 12.0 line, the Trunk incident.
- Zuul, Bors, GitLab merge trains, Sapling, CrewAI, Tessl, Cursor and Claude Code sub-agent rows come from search snippets and docs, not fetched pages; none has outcome data.
- Cursor's default agent loop has no documentation the researcher could find.
- The researchers' reads of ReAct, SWE-agent and Agentless rest on abstracts and summaries, not full tables; the per-component SWE-agent ablation deltas were not extracted.
- Local cost figures are floors (K-001: 113 of 192 baseline runs unmetered). The level-scaled costs in section 5 are estimates.
- Whether the T-0316 codex case of T-0486 still reproduces after T-0473 was not run here.
- No local run tests whether a verified solo pass met the ticket's intent; section 3.1's verdict rests on over-reach and first-pass data only.
- This pass ran one architect, no independent verifier of the research rows; the ticket's one verifier samples them.
