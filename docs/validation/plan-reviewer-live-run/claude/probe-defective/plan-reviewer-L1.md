<!-- role=plan-reviewer level=L1 model=opus effort=high -->
## Verdict
replan

## Findings
- step 1: goal coverage: the handoff's Goal requires `hello world` when no argument is given. No step's Do or acceptance criteria mentions the no-argument case, and the plan's own `## Goal` rewrites the handoff Goal without it. Evidence: handoff.md Goal ("and `hello world` with no argument") vs planner-L3.md:3 and planner-L3.md:8-10.
- step 1: builder readiness: the Do leaves a design decision to the builder: "pick the argument convention (positional or `--name`) as you see fit". The handoff already settles this as positional (`bash greet.sh Ada`), so the plan should state it, not delegate it. If the builder picks `--name`, `bash greet.sh Ada` breaks the Goal. Evidence: planner-L3.md:8; handoff.md Goal.
- step 1: acceptance criteria: `bash greet.sh Ada | grep -q Ada` does not pin the exact output `hello Ada`. It passes on `Ada`, `goodbye Ada`, or `hello Ada Ada`, and does not check the separator or the `hello` prefix. No criterion covers the no-arg `hello world` output, so the step's required behavior is only partly checked. The criterion does go red on today's code (`bash greet.sh Ada` prints `hello`), but it bites only on "Ada absent". Evidence: planner-L3.md:10; command `bash greet.sh Ada` output `hello`; greet.sh:2.
- step 1: builder readiness: `level: L4` does not fit the level-rubric builder table. L4 is for work that crosses modules or involves concurrency or state. This is a one-file, fully specified edit to a two-line script, which fits L1 or L2. Evidence: planner-L3.md:6; greet.sh:1-2; handoff.md Constraints ("one file").
- step 1: scope: the step has no scope criterion naming the files it may touch. The builder has nothing to check against the handoff's "one file" constraint. Evidence: planner-L3.md:5-10 (only Do and Acceptance criteria sections); handoff.md Constraints.

## Missing decisions
None
