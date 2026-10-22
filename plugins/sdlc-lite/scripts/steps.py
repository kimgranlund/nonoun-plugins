#!/usr/bin/env python3
"""Split a planner result into one step handoff per step, so /chain never parses a plan by hand.

Usage: steps.py {split <planner.md | task dir> [--only N ...] [--guard-timeout SECONDS] [--tree PATH] [--override-review REASON] [--supersede] |
                 lint <planner.md | task dir> [--tree PATH] [--approved "<who: why>"] | precheck <task dir> | review <task dir> | lane <task dir> | verifier-level <task dir> |
                 next <step dir> |
                 resume <task dir> |
                 open <task dir> [--explain] |
                 swap <step dir> [--timeout SECONDS] |
                 widen <step dir> <path> [<path> ...] [--timeout SECONDS] [--tree PATH] [--reason WHY] | selftest}
  split     read the plan (a planner-*.md file, or the newest planner-*.md in a task dir,
            by recorded run order in its runs.jsonl, see order.py)
            and the task goal (the ## Goal section of <task dir>/handoff.md, front matter skipped),
            then write <records dir>/step-<n>/handoff.md as "## Task goal", the goal, a blank line,
            and the step block verbatim (## Step <n>: ... up to the next ## heading, trailing
            blank lines trimmed). Prints one line per file written. The records dir is
            order.records_dir(<task dir>): .sdlc/runtime/tasks/<name>/, or the task dir itself for a
            legacy task that already records in place. Every command takes a task, records or step dir
            on either side; handoff.md, ## Plan review and skips.md stay in the task folder, and the
            step paths printed are the records-side ones.
            --tree PATH sets the work tree --only runs its (guard) and (red) spans in, else the git toplevel
            of the plan folder (the lane worktree when the plan lives there).
            --only N (repeatable) writes only those steps; an N not in the plan is an error.
            Refuses a step whose step-<n>/ already holds builder-*.md or verifier-*.md: rename it
            to step-<n>.superseded-<k>/ first (/chain 4.2), or pass --supersede, which renames each
            such chosen step dir to the next free step-<n>.superseded-<k>/ (one stderr line each)
            after every other check passes and before any write. Without --supersede nothing is renamed.
            Refuses a plan whose acceptance criterion commands do not parse (see lint): the
            refusal names each span and ends with "plan defect: replan this step (/chain 3)".
            It also refuses a step whose ### Do runs git stash or --autostash (T-0666).
            It also refuses a criterion span that runs git stash, checkout, reset, restore, or commit in its
            command text (agents/verifier.md rule 3; quoted text does not count; T-0617), a span that joins
            two checks with an unquoted || (see lint),
            one that pins a commit sha fixed at plan time (except the ancestry form
            git merge-base --is-ancestor <sha> HEAD), and one that compares a count over a
            changing set with a fixed number (see lint), and one whose ### Read first lists a
            path that does not exist, and a plan that names in no step a path a verifier or builder
            result beside it flagged on a "plan defect:" line (see lint). An optional ### Read first subsection is copied
            verbatim with the rest of the step block.
            With --only N, split then runs that step's (guard) criteria against the current tree:
            each command-like code span on a criterion line that starts with "(guard)" runs under
            bash -c, from the git toplevel of the task dir (else the task dir), under a per-step
            timeout: an explicit --guard-timeout SECONDS wins; otherwise the step block's own
            "guard timeout: <seconds>" line, else such a line outside every ## Step block (for
            example in ## Goal), else 300; a value of 0 or less counts as no line. Spans run with
            SDLC_BASE_SHA set to git rev-parse HEAD at the toplevel (no build has started, so HEAD
            is the base; unset outside git, never inherited from the caller) and with
            SDLC_TMP_WORKTREES set to a fresh dir under the worktree root tmp prefix that split removes
            after its guard and (red) spans ran (T-0726). A span that references HEAD^1 or holds a
            <placeholder> is skipped, never run. A red guard (nonzero exit) or a timeout refuses:
            one line per red guard with its exit code or timeout and its output tail, then a last
            line "plan defect: step <n> red guard: <span>; replan this step (/chain 3)".
            In a git work tree it also snapshots `git status --porcelain --untracked-files=all`
            (plus each listed path's size and mtime) before the first runnable guard and after
            the last; a path that is new or different afterwards means the guards changed the
            work tree, and split refuses: one line per such path, then one last line
            "plan defect: ... (guard) criteria changed the work tree: <paths>; replan this step
            (/chain 3)" (a red guard, if any, is named on the same line). A tree dirty before
            the guards passes when they leave it as it was. Nothing is undone.
            Then it runs that step's (red) criteria the same way (a criterion line whose leading
            tags, after - or *, hold (red); same timeout, same SDLC_BASE_SHA, spans that reference
            HEAD^1 or hold a <placeholder> skipped): a (red) span is a check of the step's new
            behavior, so it must exit nonzero now. A span that exits 0 (green now, it cannot
            detect the change), a timeout, or a span that changed the work tree refuses, one line
            "steps: <plan> red-first: step <n>: `<span>` is green now; it cannot detect the
            change", then a last line "plan defect: red-first: <k> refusal(s); replan this step
            (/chain 3)". A tree change is undone from a content snapshot taken before the first
            (red) span (red_first, one rule with specgate.py red) and the line says "restored".
            A full split (no --only) and lint never execute a span.
            Refuses a plan the plan review rejected: when the newest plan-reviewer-*.md that counts
            after the chosen plan (order.counts_after) has Verdict replan or blocked, it prints
            "steps: <plan>: the newest plan review <file> says <verdict>; a rejected plan is never
            split" and a last line "plan defect: plan review: <verdict>; run steps.py review
            (/chain 3)", with or without --only, for a file or a dir target.
            --override-review REASON splits a plan whose newest review says replan anyway (the user's
            call: never a conductor's own, never unattended). REASON is one line, required, and is
            whitespace-collapsed. Once every other check passes, split appends the line
            "review override: <review file name>: <reason>" under "## Plan review" in <task dir>/handoff.md
            (the section is created when missing) and prints "steps: review override: <review file> says
            replan; split anyway: <reason>" on stderr. The record makes the override stick: a later split
            of the same plan, and steps.py review, treat that review as overridden, so
            `split --only N` in /chain 4.2 needs no flag. A review that says blocked is never overridden
            (it names missing decisions the user answers), and a newer plan-reviewer result ends the
            override. With no rejecting review the flag does nothing and writes nothing.
            A review whose findings are all criterion-only (T-0582; with any notes-fix items) is not a
            rejection when each amend applies (see review): split writes each new criterion line into its
            step handoff in place of the line holding the old span, so lint and the --only (guard) and (red)
            runs check the new text, folds the notes-fix items, appends "- criterion-only amend: <review
            file>: step <n>: old `<old>` -> new <new>" under ## Plan review in <task dir>/handoff.md (once per
            line; created when missing) for each chosen step it amends, and names each amend on stderr.
            Refuses an invalid result first: when the chosen plan, or the newest plan-reviewer-*.md
            that counts after it, fails results.structure_error (role planner, plan-reviewer), it
            prints "invalid result: <path>: <reason>" before the review check and the goal read.
            Every check runs before any write: a failure prints on stderr, exits 1, and writes nothing
            but the refusal record: a lint refusal, a red guard or a guard tree change, and a red-first
            refusal (split, split --only, and swap) each append one line per finding under ## Plan review
            in <task dir>/handoff.md (T-0543, record_plan_review; written after the guard and (red)
            snapshots): "- <YYYY-MM-DD> plan defect at split: step <n>: <why>", n the finding's first
            "step <n>:" and why the rest of its first line, or with no step "- <date> plan defect at split:
            <the first line after its "steps: <plan>" prefix>". The section is created at the end of the
            file when missing; a line whose text after the date the section holds is skipped; no handoff.md,
            or a read or write failure, writes nothing. Other refusals (a rejected review, an invalid
            result, a missing goal, a step folder that holds role output) record nothing.
  precheck  fail fast (exit 1, naming ## Goal) when <task dir>/handoff.md has no ## Goal section, as split
            would; run.sh calls it before a planner or plan-reviewer on a task handoff. Writes nothing.
  lint      <step dir | step-<n>/handoff.md> (T-0379): check the .sdlc paths (and work_root paths, roots.py) a step handoff cites. Each must exist, and a
            report (builder-L*.md, verifier-L*.md, plan-reviewer-*.md) of the handoff's own step folder that has a
            step-<n>.superseded-<k>/ sibling must name that superseded folder, not the live step-<n>/ (a later report of the
            same name would satisfy it), except under ## Previous attempt. Exit 1, "plan defect: ..." last; dispatch.py
            prepare and run.sh run it before a builder or verifier on a step handoff. A <placeholder>, glob, or
            $VAR path is no citation. Lint writes nothing, refusal or not (the planner lints its own drafts).
            split rewrites the same links in the handoffs it writes: a cited step-<n>/<report> that is absent while a
            step-<n>.superseded-<k>/ sibling holds it becomes the highest-k sibling's path (one stderr line each);
            a path that exists or already names a superseded folder is kept, and no report is touched. (The plan text
            is copied verbatim, so a plan written before the 4.2 rename carries step-<n>/ paths: that is the producer.)
  lint      <planner.md | task dir>: pick the plan the same way split does, then check that every command-like code span
            under a step's ### Acceptance criteria (outside ``` fences) parses under bash -n, with
            each <placeholder> replaced first, and that none holds an unquoted || operator (a
            fallback passes on either side, so the criterion cannot fail); a || inside quotes, one
            whose left operand is exactly `test $# -eq 0`, or one whose right operand is a
            nonzero `exit` (`exit N` with N a nonzero integer literal ending the command, or a
            brace group `{ ...; exit N; }` whose last command is that exit) is allowed, because a
            nonzero exit fails the criterion when the left side fails, so it cannot pass on either
            side; `|| exit 0`, `|| true`, `|| echo ...` stay findings. A for, while, or until span
            ending in done, an if span ending in fi, and a { span ending in } count as commands
            and are linted, also when a trailing redirect or pipe follows the closing keyword
            (`done < f`, `done 2>/dev/null`, `done | cat`); prose starting with those words is not. A span that parses gets
            two more checks on its raw text. It must not pin a commit sha: a span holding the word
            git and a 7 to 40 char lowercase hex run (at least one digit and one of a-f, bounded by
            non-alphanumerics, so also inside <sha>..HEAD, <sha>^, <sha>~2) goes stale on the
            first sync from main; compare against HEAD at build start instead. One form is exempt:
            git merge-base --is-ancestor <sha> HEAD (HEAD as a whole word) is a deliberate ancestry
            check that stays true after a sync; any other hex run in the span still counts. It must not compare
            a count over a changing set with a fixed number: a count tool (wc -l, grep -c,
            grep --count), a set source (a * glob, or ls or find as a word), and a comparison
            (-eq -ne -ge -gt -le -lt = == !=) with a literal integer of 2 or more, all in one span.
            A bare = counts only with whitespace before it, so a bare name=value assignment such as
            n=26 is not a comparison.
            It must not require a clean porcelain status: a span holding git status in a porcelain
            or short form (--porcelain[=v1|v2], --short, -s) with no `-- <pathspec>`, tested for
            emptiness (-z, -eq/=/== with 0 or "", or ! over grep -q), can never pass, because
            builders never commit and the step's own changes keep the status dirty; check
            git diff --quiet HEAD -- <path> plus git ls-files --others --exclude-standard instead.
            A path-scoped status stays allowed.
            It must not require a clean whole-tree diff either: a git diff (never git diff-tree)
            with no `-- <pathspec>`, no commit-to-commit range (A..B, A...B, or two revision
            words), and no --no-index, that uses --quiet or --exit-code without a ! right before
            git, or whose output the span tests for emptiness, can never pass for the same reason;
            a single rev such as HEAD or "$SDLC_BASE_SHA" still diffs against the work tree. Check
            git diff --quiet "$SDLC_BASE_SHA" -- <path> plus git ls-files --others
            --exclude-standard -- <path> instead. The detector reads only span text, so a clean
            check hidden inside a script the span calls stays out of reach.
            It must not read its own step's verifier result (T-0415): a span in step n that holds
            verifier-L followed by a digit and names no step-<m>/ folder with m other than n, or that
            names step-<n>/verifier-L<d> itself, can pass only after that verifier passes; a verifier
            result at an absolute path outside the repository (under none of repo_roots) belongs to another
            repo's ticket and is not counted (T-0613), a relative or in-repo path still is; finding
            "steps: <plan> step <n>: acceptance criterion reads this step's own verifier result, so it
            can pass only after the verifier passes: <span>" and the hint line "move it to a later
            step, or declare it held with a trailing [stage: ..., owner: ...] clause". A criterion line
            that ends with a held clause (CLAUSE_RE, outside any code span) is exempt, and a span that
            names an earlier step's result (step-1/verifier-L2.md from step 2) passes.
            It must not name a path a later step creates (T-0536, order_findings): a non-(guard) criterion span of
            step n whose path token (trim_path_token, NAME= prefix dropped; holding / or a file extension; not
            absolute, $VAR, redirect, glob, URL, or ..) does not exist, that no step k <= n names outside its
            acceptance criteria, and that a later step m declares it creates ([creates:], Outputs:, a ### Do create
            verb) is a finding "steps: <plan> step <n>: acceptance criterion names <path>, which a later step
            creates (step <m>), so it can pass only after step <m>: <span>", one per (n, path), first m. Lint, not
            a plan-reviewer or planner self-check: those are model judgments with no negative control.
            A step may carry a ### Read first subsection: the entry files a role reads before
            the step, one list item per path in the one-line form - `<path>`. Each listed path
            (the text of the item's code span; lines up to the next ## or ### line, ``` fences
            left out) resolves against the git toplevel of the plan file's folder, else that
            folder outside git. A path that does not exist is a finding: "steps: <plan> step <n>:
            ### Read first lists a path that does not exist: <path>", unless an earlier step declares it
            created (declared_future_paths: a [creates: <path>] marker, an Outputs: line, a ### Do create
            verb, a (red) span; T-0533), and lint and split refuse
            with the plan defect last line. A step with no ### Read first stays valid.
            Skill routing (T-0647): a list item or table row of any AGENTS.md under the tree (root included), or a
            prose line of a nested AGENTS.md (T-0676), whose code spans or markdown link targets hold one skill path
            (a SKILL.md file or a folder under skills/) and at least one other path or glob routes those paths to
            that skill; a list item or prose line also needs a routing cue (ROUTE_CUE_RE: ->, read, use, follow)
            just before the skill span, T-0672 (repo_skill_routes; paths in a nested AGENTS.md resolve against its
            folder, a skill path only when it exists there, else against the repo root). A step whose scope allow-list (scope_entries) names a routed path (a trailing / matches the
            folder prefix, else fnmatch) and whose ### Read first does not list the skill is a finding "steps: <plan>
            step <n>: plan defect: edits routed path <p> without its skill under ### Read first: <skill>". A repo
            with no routing lines, or a step with no scope span, gets no such finding.
            It also checks the plan's contract dependents (T-0271): every line that starts
            "plan defect:" (after leading blanks) in a step-*/verifier-*.md or step-*/builder-*.md
            beside the plan, superseded step-<n>.superseded-<k>/ folders included, is split on
            whitespace; a token trimmed of backticks, quotes, brackets, sentence punctuation, and a
            trailing :line, that holds a / or ends in a file extension, is relative with no ..
            part, and names an existing file or folder under the plan folder's git toplevel (else
            that folder) is a path token. A path token that no ## Step block holds as a substring is
            a finding, one per path: "steps: <plan>: no step names <path>, which <result> flagged on
            a plan defect: line", and lint and split refuse with the plan defect last line. A word
            that names nothing on disk (and/or, c1) is no token; a plan with no such results is
            unchanged; swap and widen look beside their step handoff and find none.
            A criterion line whose leading tags hold (parity) (T-0513) names a styling approval: ``- (parity) `<capture
            command>` writes `<real.png>`; against `<mock.png>`: <property>, <property>`` (at most five named properties,
            never "matches"). Lint refuses one that names fewer than two distinct image paths (.png, .jpg, .jpeg, .webp,
            .gif), "(parity) criterion names fewer than two image paths", or no property list (a colon after the last image
            path, then text), "(parity) criterion names no property list"; the plan defect last line follows.
            Never executes a span and needs no handoff.md. Prints "steps lint: ok", or the split
            refusal on stderr and exits 1. Lint writes nothing, clean or refused (T-0543: the planner
            lints its own drafts), except the --approved line below; the same findings under split are
            recorded under ## Plan review (see split).
            Step cap (T-0553): before those checks, lint and split refuse a plan with more steps than the
            ticket's size allows (the task handoff.md front matter size: L1 and L2 3, L3 6, L4 10, L5 15; no
            size, no cap): "steps: <plan>: <k> steps exceed the step cap of <cap> for size <size>" and a last
            line "step cap: split the ticket, or ask the person and rerun steps.py lint <target> --approved
            "<who: why>"" (never a plan defect line: a replan would loop). lint --approved "<who: why>" lets an
            over-cap plan through and appends "step cap approved: <plan file name>: <who: why>" once to the
            task folder's skips.md; that line lets the same plan file through later lint and split runs
            without the flag, and a newer plan file needs its own approval. A plan within its cap ignores
            --approved and writes nothing.
            After a clean lint it also prints coarse-step warnings on stderr (stdout and exit 0
            unchanged; split, swap, and widen print none) when the plan meets the lean plan
            conditions: the plan file name level is L1 or L2 (a name with no level, such as
            handoff.md, is not eligible), no ## Assumptions item starts with "unresolved:",
            every step level is L1 to L3, no step title starts with "Merge ", the task dir
            holds fewer than two planner results (no replan), and handoff.md holds no
            "## Plan review" line. One line per finding:
              steps lint: warning: <plan>: <k> steps; the coarse-step rule allows at most 2 ...
                (more than two steps)
              steps lint: warning: <plan> step <n>: one acceptance criterion; the coarse-step
                rule merges it into a neighboring step ... (exactly one top-level - or * item)
              steps lint: warning: <plan> step <n>: history-shaped criterion: <span> (T-0475; a
                criterion command span that reads git log, git rev-list, or --oneline output)
              steps lint: warning: <plan> step <n>: absolute home path in a criterion: <span>
                (T-0686; a criterion line holding /Users/, /home/, /var/folders/ or /private/tmp/)
  review    review <task dir>: decide whether the task dir's newest planner-*.md (by order.py) needs
            a plan review before split (/chain 3). Reads only; never file times. Stdout: "<action>"
            or "review L1", then "reason: <text>", then one "read: <path>" per result file consulted, each path
            repo-relative when the task is in a git work tree (T-0715: a line pasted into a tracked handoff holds no home path);
            exit 0. Rules, in order:
              no planner-*.md                            -> one "steps review: " line on stderr,
                nothing on stdout, exit 1
              the newest plan fails results.structure_error(plan, 'planner') (empty file, no
                header, header role, section order, no ## Goal) -> invalid result (see below)
              the plan's ## Assumptions section (lines up to the next ## heading) holds a list item
                whose text after "- " or "* " starts with "unresolved:" -> stop (the reason quotes
                the item; the user decides)
              required when: a step block's level: is L4 or L5 (T-0294; planner level, a Merge title,
                a replan, and a "## Plan review" line no longer require it)
              not required                               -> split
              no plan-reviewer-*.md counts after the plan (order.counts_after) -> review L1
              the newest such result fails results.structure_error(r, 'plan-reviewer') -> invalid
                result (a missing or disallowed Verdict is not a structure error; it stays below)
              newest such result's Verdict (first non-blank line under ## Verdict, lowercased):
                pass                                     -> split
                replan whose every ## Findings item is "- step <n>: notes-fix: <text>" -> read as pass
                  (T-0364); split then appends a "### Notes" list of the step's items to that step's handoff
                pass or replan whose every ## Findings item is notes-fix or "- step <n>: criterion-only: old
                  `<span>` -> new <criterion>. Evidence: <...>", with one criterion-only item at least (T-0582)
                  -> amend (split amends each criterion in place and logs it; the replan is not spent), or
                  split when every amend is logged or already in the plan; an item that does not apply (a
                  step the plan lacks, not exactly one criterion line of the step holding the old span, a
                  new text that fails an amend's text checks) makes the review a design replan, below
                replan                                   -> replan, but stop when the task dir holds
                  two or more plan-reviewer results with Verdict replan (the count is per task dir; a
                  criterion-only review whose amends ## Plan review logs is not counted, an unlogged one is);
                  a "review override: <that file name>: <reason>" line under ## Plan review in
                  <task dir>/handoff.md (written by split --override-review) -> split, whatever the count
                blocked                                  -> stop (ask its ## Missing decisions)
                anything else                            -> review L1 (a rerun, never a replan), but
                  two consecutive verdict-less reviews after the plan -> stop
            Red at base (T-0657): when the action is split or review L1, every step's runnable (red) span
            (guard_skipped ones left out) runs once through red_first in a throwaway detached worktree at
            base_sha under the worktree root tmp prefix, removed after. Each span that exits 0 there is
            appended under ## Plan review (record_plan_review) and printed after the read: lines as
            "plan defect: red-at-base: step <n>: `<span>`", and the action becomes replan. No git, no base,
            or no runnable (red) span: nothing runs and review reads only.
            An invalid result prints "invalid result: <path>: <reason>", then "reason: the newest
            result does not match its results.py schema; stop and ask the user", then the read:
            lines; exit 0. next and resume print it the same way.
  verifier-level  verifier-level <task dir>: print the level of a solo ticket's one batched verifier from its
            handoff.md (T-0356): L3 (Fable) for a ticket of size L4 or L5, a title starting "Merge", the word
            security in the title or ## Goal, a line "verifier: L3", or a checkbox criterion under ## Acceptance
            criteria that pins an exact label or string (the words verbatim, exact or literal label/string/text/
            wording/name, or label); else L2 (Sonnet high), L1 and L2 tickets included. Stdout: the level, then
            "reason: <text>" and "read: <handoff.md>"; exit 0; exit 1 when the dir has no handoff.md. Writes nothing.
  lane      lane <task dir>: pick the task's lane, solo, lean, or full, and append it to <task dir>/skips.md.
            Stdout: the lane, then one "reason: <text>" line per reason, then one "read: <path>" line per
            file read (<task dir>/handoff.md when it exists, the newest planner-*.md by order.py when
            there is one, <task dir>/skips.md when it existed before this call); exit 0. For lane solo it also
            records the planner and filer under ## Skipped (one `- skip: <role>; step: all; reason: solo lane...;
            decided: lane` line each, added once), the form the tickets.py skips guard counts, so a conductor can
            close the ticket by reason with no extra step.
            Facts: the size is the handoff.md front matter field size (tickets.parse), the ticket level,
            valid only when it is L1 to L5 (tickets.parse reads the deprecated aliases S, M, L, XL as L1 to
            L4); a handoff with no front matter block has no size. The point is "before
            planning" with no planner result, "after plan review" when there is one and handoff.md has a
            line "## Plan review", else "after planning". The plan is read leniently, like review's
            plan facts: no results.structure_error check, since split, lint, and review refuse a bad plan.
            Rules, reasons collected in this order:
              skips.md has a line starting "- lane: full;" in its ## Lane section -> "skips.md already
                records full, and a lane never returns from full" (a lane never returns from full)
              no valid size -> "handoff.md front matter has no size of L1 to L5"
            Before planning, size alone decides: with either reason above the lane is full and only those
            print; else L1 or L2 -> solo, L3 to L5 -> full, with the one reason "size <v> decides before
            planning (no planner result yet)"; but size L1 or L2 with more than 20 checkbox lines under the
            handoff's ## Acceptance criteria is full, with the one reason "ticket lists <N> criteria (limit
            20 for size L1 or L2); split it into tickets of at most 20". After planning, more reasons follow, in order:
              size L3 to L5 -> "size <v> is above L2, and lean takes only size L1 or L2"
              an unresolved assumption by review_required() (the function review uses) -> "<plan> lists
                an unresolved assumption: "<first item>""
              every reason review_required() returns, verbatim (a step at L4 or L5), then the lean-only
                reasons (a planner L3 plan, a Merge step, a replan, a ## Plan review line: plan review no
                longer needs them, but lean stays strict)
              steps that do not parse -> "<plan> has steps that do not parse (steps.py lint names why)",
                and the step rules below are skipped
              more than 2 steps -> "<k> steps, and lean allows at most 2"
              a step with more than 12 top-level acceptance criteria -> "step <n> has <k> acceptance
                criteria, and lean allows at most 12"
              a step with no scope allow-list (a list-item criterion span with git diff --name-only and a
                grep -v allow-list in a form widen recognizes, F, E, or A) -> "step <n> has no scope
                allow-list in a form steps.py widen recognizes, so its files are unknown"
              an allow-list entry that is not a repo-relative path (widen's path rule; an E or A
                alternative is unescaped, or kept raw when it holds a pattern character) -> "step <n>
                scope entry is not a repo-relative path: <entry>"
              a path in LANE_CONTRACTS (files other roles parse: agents/, skills/, hooks/, the codex
                adapter, run.sh, steps.py, tickets.py, results.py, and the other runner and check
                scripts) -> "step <n> scope names a contract other roles parse: <path>"
              scoped paths whose nearest AGENTS.md dirs (from the path's dir up to the git toplevel, else
                the task dir; none means the root) differ -> "scoped files span <k> AGENTS.md owners:
                <owners>"
            No reason after planning -> lean, with the one reason "every lean condition holds: size <v>,
            planner L<n>, <k> steps at L1 to L3, one AGENTS.md owner (<owner>)"; any reason -> full.
            After planning the lane is never solo.
            skips.md: each call appends one line "- lane: <lane>; point: <point>; reasons: <reasons
            joined by "; ">" to the ## Lane section, after its last non-blank line; with no ## Lane
            section, a new one goes before the first ## line, or at the end; a missing file is written
            as "# Skips", a blank line, "## Lane", and the line. Every other line is kept byte for byte,
            and duplicates are appended too. Lane owns only its ## Lane section.
            A missing task dir prints one "steps lane: no such directory: <task dir>" line on stderr, and
            an OSError writing skips.md one "steps lane: cannot write <path>: <error>" line; either way
            nothing goes to stdout and it exits 1.
  next      print the next escalation action for a step dir (/chain step 4), from its newest
            builder-*.md and verifier-*.md by order.py (ordered, newest, counts_after; never file
            times). Writes nothing. Stdout: "<action>" or "<action> L<n>", then "reason: <text>",
            then one "read: <path>" per result file consulted; exit 0. Rules, in order:
              build level = level of the newest builder result, else the handoff's level: line;
              verifier level: build L1/L2 -> L1, L3 -> L2, L4/L5 -> L3.
              no builder result                          -> build L<handoff level>
              newest builder fails results.structure_error(b, 'builder') (empty file, no header,
                header role, section order)              -> invalid result (printed as review
                prints it); a missing or disallowed Status is not a structure error
              newest builder has no done/blocked Status  -> rebuild L<level of that result>,
                but 2+ consecutive statusless builders (newest first) -> stop
              newest builder Status inherited red: <tests> -> inherited (a gate already red at
                the pre-build HEAD; ask the conductor). Never counted as a fail, a bump, a
                rebuild, or a replan; a bare "inherited red" with no colon is statusless.
              newest builder Status blocked              -> replan, except Notes whose
                first line starts "stale lane:" (missing merged prerequisites, not a plan defect) -> resplit:
                rebase the lane, move the step dir to step-<n>.superseded-<k>, steps.py split --only <n>;
                and Notes whose first line starts "plan defect:" and hold one amend old:/amend new: pair
                (see amend): the step handoff no longer holds the old span and holds the new text ->
                rebuild L<level>; else no other builder result in the dir holds a pair, the step is not
                built, and the task's one replan is unused -> amend L<level> (apply it with steps.py
                amend, then rebuild at that level); else replan, the reason naming why no amend.
                An amend-routed block is never counted for a rebuild or a bump.
              no verifier result counts after the build  -> verify L<verifier level>,
                but done when batch_verified(step dir) names a task-dir verifier result: the
                newest task-dir verifier-*.md (order.py) whose ## Verified section lists
                step-<n>/<newest builder file name> (bare or in a code span) decides, and it
                counts only when it passes results.structure_error and its Verdict is pass (a
                later listing of the same build overrides an earlier one; never file times).
                Never batch-verified: the newest builder Status is not done, the build is L4 or
                L5, the step title starts with "Merge " or holds "gates green" (any case), the
                step is the highest-numbered live step-<n>/ in the task dir, or a sibling
                step-<n>.superseded-<k>/ exists.
              newest verifier fails results.structure_error(v, 'verifier') -> invalid result
                (read: the build and that verifier); a missing or disallowed Verdict is not one
              newest verifier has no pass/fail Verdict   -> reverify L<level of that verifier>,
                but 2+ consecutive no-verdict verifiers after the build -> stop
              newest verifier Verdict inherited red: <tests> -> inherited (a gate already red at
                the pre-build HEAD; ask the conductor). Never counted as a fail or a no-verdict
                run, and it breaks a no-verdict run; a bare "inherited red" with no colon is no verdict.
              newest verifier Verdict pass               -> done, except a Verdict pass beside a Criteria line that
                is unmet-dependency or deferred (fail closed) -> reverify L<level of that verifier>
              fail whose ## For the next attempt starts "unmet-dependency:" or "deferred:" and every held
                Criteria line checks out against the step handoff's bracket clause (T-0408; see open)
                -> wait (no subject met yet), reverify (a declared subject is met now), or deferred (an
                owner stage settles it). Never counted for a rebuild, a bump or a replan; a hold the handoff
                does not declare is an ordinary fail, with "undeclared hold ignored: <ref>" in the reason.
              fail whose ## For the next attempt starts "plan defect:", holds one swap old:/swap new:
                pair (see swap), and no other verifier result in the dir holds a pair -> swap L<build
                level> (apply it with steps.py swap, then rebuild at that level); any other
                plan-defect fail -> replan
              else count non-plan-defect fails whose paired builder (newest before each
              verifier) is at the current build level: 1 -> rebuild L<n>,
              2+ at L1..L4 -> bump L<n+1>, 2+ at L5 -> stop.
              A plan-defect fail, swap-routed or not, is never counted for a rebuild or a bump.
              A verifier with no verdict is never counted as a fail. A builder with no Status is
              never a done or a fail, never adds a bump, and is never a verifier's paired builder.
            Errors (missing dir, no handoff level with no builder result) print one "steps next: "
            line on stderr, nothing on stdout, and exit 1.
  open      open <task dir> [--explain] (T-0408): print one line "<ref>\t<state>\t<subject or owner>" per held
            criterion (unmet-dependency or deferred) the task's handoffs declare with a trailing bracket clause
            `[stage: <word>; owner: <stage word or T-NNNN>; needs: <T-NNNN|file:<path>|cap:<name>, ...>]`. A ref is
            step-<n>#<k> (the k-th bullet under ### Acceptance criteria of that step's handoff) or ticket#<k> (the
            k-th bullet under ## Acceptance criteria of the task handoff). The newest verifier result naming a ref
            decides: pass settles it (a task-dir Verdict pass also settles the refs under its ## Settles). Nothing
            and exit 0 when none; --explain adds the reason a hold is stale (its subject is met now) or an
            ordinary fail (undeclared). tickets.py close refuses while any is open. lint refuses a malformed
            clause; swap keeps a criterion line's clause unchanged.
  resume    pick the step a resumed /chain continues from (/chain step 4). Candidates are the task
            dir's direct children named exactly step-<n> (step-<n>.superseded-<k>/ left out),
            sorted by the integer n (step-2 before step-10). For each in order it runs the next
            rules above; the first whose action is not done, wait or deferred wins (invalid result included);
            a wait or deferred step is skipped, and when only held steps remain the first one is printed
            with "every other step passed" added to its reason. Stdout:
            that step dir as <task dir as given>/step-<n>, then exactly what next prints for it;
            exit 0. When every candidate is done: "done", then "reason: every step-<n>/ passed";
            exit 0. It never picks the newest or highest step dir. Writes nothing and never reads
            file times. A step that next calls done through a batch-verified task-dir verifier
            result (## Verified, above) counts as done.
            A missing task dir, a task dir with no step-<n>/ (run split first), or a next error on
            a candidate prints one "steps resume: " line on stderr, nothing on stdout, and exits 1.
  swap      apply the newest verifier's one criterion swap to <step dir>/handoff.md (/chain 4.2
            light path). A solo task dir (no builder result, a solo-L<n>.md result) works too: the
            newest solo result stands in for the builder result, and the criterion region also
            includes the task handoff's ## Acceptance criteria. The pair lives in that verifier's ## For the next attempt: exactly one
            line starting "swap old:" holding exactly one code span (the old criterion's command,
            verbatim), and exactly one line starting "swap new:" whose stripped rest is the full
            replacement criterion; zero or two or more of either line, or a swap old: line with no
            span or several, is no pair. Preconditions: a newest builder and a newest verifier
            result, the verifier counts after the builder (order.counts_after), its Verdict is
            fail, its note starts "plan defect:", it holds a pair, and no other verifier result in
            the dir holds one (one swap per step). Exactly one criterion line (the criteria_lines
            region, a - or * list item) must hold the old span among its command spans. The new
            text starts with (guard), and carries (red) in its leading tags, exactly when that line
            does, holds at least one command span,
            no span references HEAD^1 or holds a <placeholder>, and it lints clean (the lint rules
            above). Each new span then runs under bash -c from the git toplevel of the step dir
            (else the step dir) under --timeout SECONDS (default 300), with SDLC_BASE_SHA set to
            the first line of <step dir>/base-sha when it names a commit, else HEAD (unset outside
            git, never inherited from the caller): the build is in the tree,
            so a red span or a timeout refuses; in a git work tree a span that changed the work
            tree refuses too, naming the paths (nothing is undone). When no criterion line holds
            the old span but one criterion line's text after its marker equals the new text, it
            prints "swap: already applied", exits 0, and writes nothing. Otherwise it replaces
            only the target line, as <indent><marker> <new text>, and prints one line naming the
            step dir, the old span, and the new text. Every refusal prints on stderr, ends with a
            last line "plan defect: steps swap refused: <why>; replan this step (/chain 4.2)",
            exits 1, and writes nothing.
  amend     amend <step dir> [--timeout SECONDS]: apply the newest blocked builder's one criterion amend to
            <step dir>/handoff.md (/chain 4.10). The pair lives in that builder's ## Notes: the first
            non-blank line starts "plan defect:", then exactly one line starting "amend old:" holding
            exactly one code span (the old criterion's command, verbatim) and exactly one line starting
            "amend new:" whose stripped rest is the full replacement criterion. Refusals: no step
            handoff; the dir is not step-<n>; no builder result; the newest builder's Status is not
            blocked or its Notes do not start "plan defect:"; no pair; the step is already built (a
            builder result with Status done, or any verifier result: a built step's criterion changes
            only through the verifier's swap); another builder result in the dir holds a pair (one
            amend per step); the task already used its one replan (two or more planner-*.md results
            in its records dir, or an "amend applied:" line under the task handoff's ## Plan review);
            then every target and new-text check swap makes. The build is partial, so only a (guard)
            line's new spans run (exit 0, work tree unchanged) and a (red) line's new spans must each
            exit nonzero now (a timeout refuses); a plain criterion is not run. When no criterion line
            holds the old span but one line's text after its marker equals the new text, it prints
            "amend: already applied", exits 0, and writes nothing (checked before the replan cap). On
            success it replaces only the target line, appends "- amend applied: step <n>: old `<old>`
            -> new <new>" under ## Plan review in the task handoff (the section created at the end when
            missing), and prints "steps amend: <step dir>: old `<old>` -> new <new>". Every refusal
            prints on stderr, ends with a last line "plan defect: steps amend refused: <why>; replan
            this step (/chain 4.2)", exits 1, and writes nothing.
  widen     widen <step dir> <path> [<path> ...] [--timeout SECONDS] [--tree PATH] [--reason WHY]: apply a conductor scope
            decision to <step dir>/handoff.md, so the next builder does not block on the old scope
            guard. Each path must be repo-relative, match [A-Za-z0-9._/@+-]+, not start with - or /,
            and hold no .. component. Exactly one criterion line (the criteria_lines region, a - or
            * list item) must hold one command span with git diff --name-only and a grep -v
            allow-list, in exactly one recognized form:
              F  grep -vxF -e <word>...      each path is appended as -e <path> after the last -e arg
              E  grep -vxE "<pattern>"       |<path> is appended inside the quotes
              A  grep -vE "^(...)$" (or grep -E -v)   |<path> is inserted before )$
            In E and A the path is ERE-escaped (a backslash before each of .^$*+?()[]{}|\).
            A deny-path guard is also accepted: a span with git diff --name-only, no grep -v, and
            exactly one run of ':(exclude)<path>' pathspecs; each path is appended as another
            ':(exclude)<path>' after that run, in its quote style (a span with several runs refuses).
            Several such lines refuses. An unrecognized form, or zero such lines, refuses too,
            unless --reason WHY is given: the path list is then the explicit allow-list, recorded
            with the reason as "- `<path>`: allowed by a conductor scope decision (steps.py widen):
            <why>" under ## Scope widened (no span is rewritten or run), and it prints "steps widen:
            <step dir>: no scope criterion; recorded <paths> under ## Scope widened (reason: <why>)".
            With a criterion present --reason is appended to each recorded item. A path already listed
            (an -e word for F, its escaped form an alternative for E and A) is skipped; when every
            path is listed it prints "widen: already applied", exits 0, and writes nothing. The
            rewritten line must keep its marker and (guard) tag and lint clean (the lint rules
            above). The widened span then runs under bash -c from --tree PATH, else the git toplevel
            of the step dir, else the step dir (when the step dir is in a shared or stale checkout and the
            current directory is another work tree of the same repository, that work tree is the default
            and stderr names it; --tree must belong to the step dir's repository) under --timeout SECONDS (default 300), with SDLC_BASE_SHA from
            <step dir>/base-sha, else HEAD, as swap does: a red span, a timeout, or a span that
            changed the work tree refuses. Otherwise it replaces only the target line, appends one
            item per added path, "- `<path>`: allowed by a conductor scope decision (steps.py
            widen)", to a ## Scope widened section (created if missing, earlier items kept), and
            prints "steps widen: <step dir>: added <paths> to the scope criterion: <new span>".
            Every refusal prints on stderr, ends with a last line "plan defect: steps widen
            refused: <why>; replan this step (/chain 4.2)", exits 1, and writes nothing.
  selftest  build fixtures in a temp dir and prove every case and every failure fires
"""
import argparse
import contextlib
import fnmatch
import io
import json
import os
import pathlib
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time

import order
import results
import roots as sdlc_roots  # the state root rule (state_of, record_prefixes); `roots` is a local name here

STEP_RE = re.compile(r'^## Step (\d+): (.+)$')
LEVEL_RE = re.compile(r'^level: L[1-5]\s*$')
GUARD_TIMEOUT_RE = re.compile(r'^guard timeout:\s*(\d+(?:\.\d+)?)\s*$')
DEFAULT_GUARD_TIMEOUT = 300
SPAN_RE = re.compile(r'(`+)(.+?)\1')
ASSIGN_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=')
# A template placeholder is an angle-bracketed run of words (<sha>, <step dir>, <L1|L2|L3>): no =, quote,
# ;, &, (, ), brackets or other operator inside, and no space next to a |, so `i<t ... >=` is not one.
PLACEHOLDER_RE = re.compile(r'<\w[\w.,/:-]*(?:(?: |\|)[\w.,/:-]+)*>')
# The quoted body of a node -e or python -c command: code, never a placeholder inside it.
CODE_BODY_RE = re.compile(r'''(\b(?:node\s+(?:-e|--eval)|python3?\s+-c)\s+)("(?:\\.|[^"\\])*"|'[^']*')''')
TAG_RUN_RE = re.compile(r'^(?:\([\w-]+\)\s*)+')
RED_SNAPSHOT_LIMIT = 8_000_000
BUILTINS = {'cd', 'test', '[', 'echo', 'printf', 'export', 'set', 'true', 'false', 'time', 'type',
            'command', 'eval', 'exec', 'source', '.'}
PLAN_DEFECT = 'plan defect: replan this step (/chain 3)'


class Fail(Exception):
    """A refusal: the message goes to stderr and the command exits 1. Never a traceback."""


def _as_given(given, path):
    """path, in the form given was written in: given itself when both name the same dir, else path (relative to the
    working dir when given was relative)."""
    g = pathlib.Path(given)
    if os.path.abspath(g) == os.path.abspath(path):
        return g
    return pathlib.Path(os.path.relpath(path)) if not g.is_absolute() else pathlib.Path(path)


def task_of(path):
    """The task folder (handoff.md, ## Goal, ## Plan review, skips.md) for a task, records or step dir on either
    side (order.task_dir); a records dir with no task folder is itself."""
    t = order.task_dir(path)
    return pathlib.Path(path) if t is None else _as_given(path, t)


def records_of(path, create=False):
    """The records dir (results, runs.jsonl, step-<n>/ dirs) for a task, records or step dir on either side
    (order.records_dir; a legacy task is its own records dir). create makes a runtime records dir. Without create, an
    existing dir whose records dir does not exist (a hand-written step-<n>/ beside its handoff) is read in place."""
    r = order.records_dir(path, create)
    if not create and not r.is_dir() and pathlib.Path(path).is_dir():
        return pathlib.Path(path)
    return _as_given(path, r)


def step_handoff(d):
    """The handoff.md of a step dir on either side: its own, else its twin's (a hand-written task-side step whose
    records twin dispatch.py prepare created holds its handoff task-side), else d/handoff.md (missing)."""
    d = pathlib.Path(d)
    h = d / 'handoff.md'
    if h.is_file():
        return h
    a = pathlib.Path(os.path.abspath(d))
    t = order.task_dir(a)
    for twin in ((t / a.name) if t is not None else None, order.records_dir(a)):
        if twin is not None and twin != a and (twin / 'handoff.md').is_file():
            return twin / 'handoff.md'
    return h


def step_dirs(task):
    """{n: step-<n> dir} of a task, records or step-holding dir: the records side and the task side united, the
    records-side dir preferred (a hand-written step-<n>/ may exist only beside the task handoff)."""
    out = {}
    for side in (task_of(task), records_of(task)):
        if pathlib.Path(side).is_dir():
            for c in pathlib.Path(side).iterdir():
                if c.is_dir() and re.fullmatch(r'step-\d+', c.name):
                    out[int(c.name[5:])] = c
    return out


def find_plan(target):
    """Return (planner file, task dir) for a planner file, or a task, records or step dir on either side. The plan
    comes through order (the records dir); the task dir is the task folder (task_of)."""
    target = pathlib.Path(target)
    if target.is_dir():
        plan = order.newest(target, 'planner')
        if not plan:
            raise Fail(f'steps: no planner-*.md in {target}')
        return pathlib.Path(plan), task_of(target)
    if target.is_file():
        return target, task_of(target.parent)
    raise Fail(f'steps: no such file or directory: {target}')


def read_goal(task_dir, allow_empty=False):
    handoff = task_dir / 'handoff.md'
    if not handoff.is_file():
        raise Fail(f'steps: no task handoff at {handoff}; the goal comes from its ## Goal section')
    lines = handoff.read_text(encoding='utf-8').splitlines()
    i = 0
    if lines and lines[0].strip() == '---':
        end = next((j for j in range(1, len(lines)) if lines[j].strip() == '---'), None)
        if end is None:
            raise Fail(f'steps: {handoff} opens front matter with --- but never closes it')
        i = end + 1
    start = next((j for j in range(i, len(lines)) if lines[j].rstrip() == '## Goal'), None)
    if start is None:
        near = next((l.strip() for l in lines[i:] if l.startswith('## ') and l.rstrip() != '## Goal'
                     and 'goal' in l.lower()), None)
        hint = f'; found {near} instead, expected ## Goal' if near else ''
        raise Fail(f'steps: {handoff} has no ## Goal section{hint}')
    body = []
    for line in lines[start + 1:]:
        if line.startswith('## '):
            break
        body.append(line)
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    if not body and not allow_empty:
        raise Fail(f'steps: the ## Goal section of {handoff} is empty')
    return '\n'.join(body)


def parse_steps(plan):
    """Return {n: block text} in plan order. A block runs from its ## Step line to the next ## line."""
    steps = {}
    cur = None
    for line in plan.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            cur = None
            m = STEP_RE.match(line)
            if m:
                n = int(m.group(1))
                if n in steps:
                    raise Fail(f'steps: {plan} has step {n} twice')
                steps[n] = cur = [line]
            continue
        if cur is not None:
            cur.append(line)
    if not steps:
        raise Fail(f'steps: {plan} has no "## Step <n>: <title>" blocks')
    out = {}
    for n, block in steps.items():
        while block and not block[-1].strip():
            block.pop()
        if not any(LEVEL_RE.match(line) for line in block):
            raise Fail(f'steps: step {n} in {plan} has no "level: L1".."level: L5" line')
        out[n] = '\n'.join(block)
    return out


def guard_timeout_in(lines):
    """The first "guard timeout: <seconds>" value above 0 (and finite) among lines, else None."""
    for line in lines:
        m = GUARD_TIMEOUT_RE.match(line)
        if m:
            v = float(m.group(1))
            if 0 < v < float('inf'):
                return v
    return None


def plan_guard_timeout(plan):
    """The plan-level guard timeout: a "guard timeout: <seconds>" line outside every ## Step block
    (a block runs from its ## Step line to the next ## line), else None. 0 or less counts as no line."""
    outside, in_step = [], False
    for line in plan.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            in_step = STEP_RE.match(line) is not None
            continue
        if not in_step:
            outside.append(line)
    return guard_timeout_in(outside)


def step_guard_timeout(block):
    """The step-level guard timeout: a "guard timeout: <seconds>" line inside one step block, else
    None. 0 or less counts as no line."""
    return guard_timeout_in(block.splitlines())


def criteria_indexed(lines, heads=('### Acceptance criteria',)):
    """(index, line) for each line under each ### Acceptance criteria of a list of lines, up to the
    next ## or ### line, with ``` fenced lines left out. The one region rule criteria_lines uses.
    heads names the headings that open a region (swap on a solo task dir adds ## Acceptance criteria)."""
    out = []
    inside = fenced = False
    for i, line in enumerate(lines):
        if line.startswith('## ') or line.startswith('### '):
            inside = line.strip() in heads
            fenced = False
            continue
        if not inside:
            continue
        if line.lstrip().startswith('```'):
            fenced = not fenced
            continue
        if not fenced:
            out.append((i, line))
    return out


def criteria_lines(block):
    """Lines under each ### Acceptance criteria of a step block, up to the next ## or ### line,
    with ``` fenced lines left out."""
    return [line for _, line in criteria_indexed(block.splitlines())]


COMPOUND_END = {'for': 'done', 'while': 'done', 'until': 'done', 'if': 'fi', '{': '}'}


def is_command(text):
    """True when a code span reads as a shell command, judged by its head token. A compound
    command counts too: a for, while, or until head with a span ending in done, an if head ending
    in fi, or a { head ending in }. A trailing redirect or pipe after the closing keyword counts
    too (`done < f`, `fi 2>&1`, `} | cat`, never `||`) when a `;`, `&`, or newline comes before
    that keyword. Prose that starts with those words (`for each changed file`, `for each file
    done < f`) does not."""
    tokens = text.split()
    assigns = []
    i = 0
    while i < len(tokens) and (ASSIGN_RE.match(tokens[i]) or tokens[i] == '!'):
        if tokens[i] != '!':
            assigns.append(tokens[i])
        i += 1
    if any('$(' in a for a in assigns):
        return True
    if i == len(tokens):
        return False
    head = tokens[i]
    if head in COMPOUND_END:
        end = re.escape(COMPOUND_END[head])
        if re.search(r'(?:^|[\s;&|])' + end + r'$', text.rstrip()):
            return True
        return re.search(r'[;&\n]\s*' + end + r'\s*(?:\d*(?:<<<|>>|&>|>&?|<)|\|(?!\|))', text) is not None
    return (head in BUILTINS or '/' in head or head.endswith('.py') or head.endswith('.sh')
            or shutil.which(head) is not None)


def line_spans(line):
    """The command-like code spans on one line, in order."""
    spans = []
    for m in SPAN_RE.finditer(line):
        text = m.group(2)
        if text.startswith(' '):
            text = text[1:]
        if text.endswith(' '):
            text = text[:-1]
        if re.search(r'\s', text) and is_command(text):
            spans.append(text)
    return spans


def command_spans(block):
    """The command-like code spans under a step block's acceptance criteria, in order."""
    return [text for line in criteria_lines(block) for text in line_spans(line)]


def is_guard_line(line):
    """True when a criterion line, after its list marker (- or *), starts with (guard)."""
    text = line.lstrip()
    if text.startswith('- ') or text.startswith('* '):
        text = text[2:].lstrip()
    return text.startswith('(guard)')


def guard_spans(block):
    """The command-like code spans on a step block's (guard) criterion lines, in order.
    Same lines (criteria_lines) and same span test (line_spans) as command_spans."""
    return [text for line in criteria_lines(block) if is_guard_line(line) for text in line_spans(line)]


def leading_tags(line):
    """The tags of a criterion line's leading tag run, after its list marker (- or *): ["red"] for
    "- (red) `cmd`", ["guard", "red"] for "- (guard)(red) `cmd`". A tag later in the line is not in the run."""
    text = line.lstrip()
    if text.startswith('- ') or text.startswith('* '):
        text = text[2:].lstrip()
    m = TAG_RUN_RE.match(text)
    return re.findall(r'\(([\w-]+)\)', m.group(0)) if m else []


def is_red_line(line):
    """True when a criterion line's leading tag run, after its list marker, holds (red)."""
    return 'red' in leading_tags(line)


def red_spans(block):
    """The command-like code spans on a step block's (red) criterion lines, in order, a repeated span
    once. Same lines (criteria_lines) and same span test (line_spans) as guard_spans."""
    out = []
    for line in criteria_lines(block):
        if is_red_line(line):
            out += [t for t in line_spans(line) if t not in out]
    return out


def fill_placeholders(text, repl='PLACEHOLDER'):
    """text with each real <placeholder> replaced by repl; a node -e or python -c body is left alone."""
    parts = CODE_BODY_RE.split(text)
    return ''.join(p if i % 3 == 2 else PLACEHOLDER_RE.sub(repl, p) for i, p in enumerate(parts))


def has_placeholder(text):
    return fill_placeholders(text, '\0') != text


def guard_skipped(text):
    """A guard span that cannot run against the current tree: it references HEAD^1 (a merge
    commit not made yet) or holds a <placeholder>."""
    return 'HEAD^1' in text or has_placeholder(text)


def git_toplevel(task_dir):
    """The git toplevel of the task dir, or None outside a git work tree."""
    try:
        r = subprocess.run(['git', '-C', str(task_dir), 'rev-parse', '--show-toplevel'],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    top = r.stdout.strip()
    return top if r.returncode == 0 and top else None


def repo_relative(text, task_dir):
    """text with every absolute path under task_dir's git toplevel (or its main checkout or lanes root) made
    repo-relative (tickets.relative_paths, T-0662), so a line written into a tracked handoff passes a personal-path
    gate (T-0715). Outside git, or on any failure, text comes back unchanged."""
    top = git_toplevel(task_dir)
    if not top or '/' not in text:
        return text
    try:
        import tickets  # local, as lane_action: a copy of steps.py beside only order.py and results.py has no tickets.py
        return tickets.relative_paths(text, pathlib.Path(top))
    except Exception:  # noqa: BLE001 - a path rewrite never breaks the command
        return text


def guard_cwd(task_dir):
    """The git toplevel of the task dir, else the task dir itself."""
    return git_toplevel(task_dir) or str(task_dir)


def git_common_dir(path):
    """The absolute, resolved git common dir of the repo holding path (shared by every linked
    worktree of one repository), or None outside git."""
    try:
        r = subprocess.run(['git', '-C', str(path), 'rev-parse', '--git-common-dir'],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = r.stdout.strip()
    if r.returncode != 0 or not out:
        return None
    return str((pathlib.Path(path) / out).resolve())


def lane_tree(folder, tree=None):
    """The work tree a command evaluates spans in for the handoff folder `folder`. --tree wins (it must be a
    work tree of the same repository as the folder). Else the git toplevel of the folder; but when the
    process cwd is a different work tree of that same repository (a lane worktree, with the shared handoff in
    another checkout), the cwd's toplevel. Raises Fail on a --tree of another repository."""
    top = git_toplevel(folder)
    if tree is not None:
        t = git_toplevel(tree)
        if t is None:
            raise Fail(f'steps: --tree {tree} is not inside a git work tree')
        if top is not None and git_common_dir(t) != git_common_dir(top):
            raise Fail(f'steps: --tree {tree} is a work tree of another repository than {folder}')
        return t
    here = git_toplevel(os.getcwd())
    if top and here and os.path.realpath(here) != os.path.realpath(top) \
            and git_common_dir(here) == git_common_dir(top):
        return here
    return top


def tree_state(top):
    """The work tree's status for side-effect detection: path -> (porcelain XY, size, mtime_ns),
    tracked and untracked (ignored files excluded), or None when git status fails. Read-only:
    --no-optional-locks keeps git from refreshing the index."""
    try:
        r = subprocess.run(['git', '--no-optional-locks', '-C', top, 'status', '--porcelain',
                            '--untracked-files=all', '-z'],
                           capture_output=True, stdin=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    state = {}
    fields = r.stdout.decode('utf-8', errors='surrogateescape').split('\0')
    i = 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if len(entry) < 4:
            continue
        xy, path = entry[:2], entry[3:]
        if 'R' in xy or 'C' in xy:
            i += 1  # a rename or copy is followed by its source path
        try:
            st = os.lstat(os.path.join(top, path))
            stat = (st.st_size, st.st_mtime_ns)
        except OSError:
            stat = None
        state[path] = (xy, stat)
    return state


def tree_changes(before, after):
    """Paths new in after, gone from after, or different between the two states, sorted."""
    return sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))


def rev_commit(top, rev):
    """The full sha of rev as a commit in the repo at top, or None."""
    try:
        r = subprocess.run(['git', '-C', top, 'rev-parse', '--verify', '--quiet', f'{rev}^{{commit}}'],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() or None if r.returncode == 0 else None


def _git_dirs(where):
    """(git dir, common git dir) of the repo at where, as real paths, or None outside git."""
    try:
        r = subprocess.run(['git', '-C', str(where), 'rev-parse', '--git-dir', '--git-common-dir'],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = r.stdout.splitlines()
    if r.returncode != 0 or len(lines) != 2:
        return None
    return tuple(os.path.realpath(os.path.join(str(where), x)) for x in lines)


def exec_toplevel(task_dir):
    """The git toplevel a step's build runs in (T-0381): the task dir's own toplevel, except a task dir in the main
    checkout read from inside an owned linked (lane) worktree of the same repo, where it is that worktree. None
    outside a git work tree."""
    top = git_toplevel(task_dir)
    hd = _git_dirs(task_dir) if top else None
    if not hd or hd[0] != hd[1]:
        return top
    cwd_top = git_toplevel(os.getcwd())
    cd = _git_dirs(cwd_top) if cwd_top else None
    return cwd_top if cd and cd[0] != cd[1] and cd[1] == hd[1] else top


NAMED_BASE_RE = re.compile(r'^[ \t]*(?:-[ \t]+)?[Bb]ase:[ \t]*([0-9a-fA-F]{7,40})[ \t]*(?:#.*)?$', re.M)
NAMED_TESTS_RE = re.compile(r'^[ \t]*(?:-[ \t]+)?tests:[ \t]*(.*?)[ \t]*$', re.M)


def declared_tests(text):
    """(paths, problems) for the `tests:` lines of a handoff or step block (T-0395): a bare line or list item of
    comma-separated repo-relative file paths, each optionally in backticks, e.g. `tests: tests/a.sh, tests/b.sh`.
    A path that is absolute, climbs with .., holds a glob character, or ends in / (a directory) is a problem and
    declares nothing: the declaration is exact files, never a blanket ignore."""
    paths, problems = [], []
    for m in NAMED_TESTS_RE.finditer(text):
        for raw in m.group(1).split(','):
            t = raw.strip().strip('`').strip()
            if not t:
                continue
            if t.startswith('/') or '..' in t.split('/') or t.endswith('/') or any(c in t for c in '*?[]{}'):
                problems.append(t)
            elif t not in paths:
                paths.append(t.removeprefix('./'))
    return paths, problems


def base_sha(top, step_dir=None):
    """SDLC_BASE_SHA for a span (T-0381), in this order: a base the step handoff names (a line `base: <sha>`), else the
    first line of <step dir>/base-sha recorded at the first dispatch, else HEAD at top; None outside git. top is the
    execution tree (exec_toplevel), never the main checkout of a lane. A value that is not a commit that is an
    ancestor of HEAD is skipped, with a stderr line for a named one."""
    if not top:
        return None

    def usable(sha):
        c = rev_commit(top, sha) if sha else None
        if not c:
            return None
        r = subprocess.run(['git', '-C', top, 'merge-base', '--is-ancestor', c, 'HEAD'], capture_output=True,
                           stdin=subprocess.DEVNULL, timeout=30)
        return c if r.returncode == 0 else None
    if step_dir is not None:
        # base-sha lives in the records dir; the handoff is the one in the dir given (a task-level handoff stays in
        # the task folder), else the records-side step handoff
        given, step_dir = pathlib.Path(step_dir), records_of(step_dir)
        named = given / 'handoff.md' if (given / 'handoff.md').is_file() else pathlib.Path(step_dir) / 'handoff.md'
        with contextlib.suppress(OSError, UnicodeDecodeError, subprocess.SubprocessError):
            m = NAMED_BASE_RE.search(named.read_text(encoding='utf-8'))
            if m:
                if usable(m.group(1)):
                    return usable(m.group(1))
                print(f'steps.py: SDLC_BASE_SHA refused: {named} names base '
                      f'{m.group(1)}, which is not a commit that is an ancestor of HEAD in {top}', file=sys.stderr)
        with contextlib.suppress(OSError, UnicodeDecodeError, subprocess.SubprocessError):
            first = ((pathlib.Path(step_dir) / 'base-sha').read_text(encoding='utf-8').splitlines() or [''])[0].strip()
            if usable(first):
                return usable(first)
            # a recorded commit that is not an ancestor of HEAD (a stale tree vs the lane base) stays the base, so
            # the span is red as before instead of silently going green against HEAD (T-0382)
            if rev_commit(top, first):
                return rev_commit(top, first)
    return rev_commit(top, 'HEAD')


def span_env(base, tmp=None):
    """The env a span runs with: SDLC_BASE_SHA set to base, never inherited; unset when base is None.
    SDLC_TMP_WORKTREES is set to tmp when given (T-0726), else left as inherited."""
    env = {k: v for k, v in os.environ.items() if k != 'SDLC_BASE_SHA'}
    if base:
        env['SDLC_BASE_SHA'] = base
    if tmp:
        env['SDLC_TMP_WORKTREES'] = str(tmp)
    return env


@contextlib.contextmanager
def span_tmp(top):
    """A fresh throwaway dir for the spans of one split --only, under the worktree root tmp prefix
    (the system temp dir when there is none), removed on exit (T-0726). Yields its path."""
    import wtroot  # local, as in red_at_base: a copy of steps.py beside only order.py and results.py has no wtroot.py
    root = (wtroot.tmp_root(top) if top else None) or pathlib.Path(tempfile.gettempdir())
    root.mkdir(parents=True, exist_ok=True)
    holder = tempfile.mkdtemp(prefix='split-spans-', dir=root)
    try:
        yield holder
    finally:
        shutil.rmtree(holder, ignore_errors=True)


def run_guard(text, cwd, timeout, base=None, tmp=None):
    """Run one guard span with SDLC_BASE_SHA=base (unset when None) and SDLC_TMP_WORKTREES=tmp (when given).
    Returns (rc or None on timeout, combined output tail lines).
    It runs in its own session so a timeout kills the whole process group, grandchildren too."""
    proc = subprocess.Popen(['bash', '-c', '--', text], cwd=cwd, stdin=subprocess.DEVNULL, env=span_env(base, tmp),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        rc = None
    tail = [line for line in (err + out).decode('utf-8', errors='replace').splitlines() if line.strip()]
    return rc, tail[-5:]


def run_guards(plan, steps, chosen, task_dir, timeouts, tree=None):
    """Run the runnable (guard) spans of each chosen step, each under timeouts[n] seconds; raise
    Fail naming every red one. Called only by split --only; a full split and lint never execute a span.
    tree (--tree) is the work tree the spans run in, else the git toplevel of the task dir."""
    top = git_toplevel(tree or task_dir)
    cwd = top or str(tree or task_dir)
    base = base_sha(top)
    lines, red, before, ran = [], [], None, False
    with span_tmp(top) as tmp:
        for n in chosen:
            for text in guard_spans(steps[n]):
                if guard_skipped(text):
                    continue
                if top and not ran:
                    before = tree_state(top)
                ran = True
                timeout = timeouts[n]
                rc, tail = run_guard(text, cwd, timeout, base, tmp)
                if rc == 0:
                    continue
                why = f'timed out after {timeout:g}s' if rc is None else f'exit {rc}'
                lines.append(f'steps: {plan} step {n}: (guard) criterion is red now ({why}): {text}')
                lines += [f'  {t}' for t in tail]
                red.append(f'step {n} red guard: {text}')
    after = tree_state(top) if before is not None else None
    changed = tree_changes(before, after) if after is not None else []
    if changed:
        which = f'step {chosen[0]}' if len(chosen) == 1 else f'steps {", ".join(map(str, chosen))}'
        lines += [f'steps: {plan} {which}: (guard) criteria changed the work tree: {p}' for p in changed]
        red.append(f'{which} (guard) criteria changed the work tree: {", ".join(changed)}')
    if red:
        record_plan_review(task_dir, plan, [x for x in lines if not x.startswith(' ')])
        raise Fail('\n'.join(lines + [f'plan defect: {"; ".join(red)}; replan this step (/chain 3)']))


def red_snapshot(top, state):
    """The content of every path in a tree_state that exists on disk: path -> ('link', target),
    ('file', bytes, mode, mtime_ns), or None (over RED_SNAPSHOT_LIMIT bytes, or unreadable)."""
    snap = {}
    for p, (_, stat) in state.items():
        if stat is None:
            continue
        fp = os.path.join(top, p)
        try:
            if os.path.islink(fp):
                snap[p] = ('link', os.readlink(fp))
            elif os.path.isfile(fp) and stat[0] <= RED_SNAPSHOT_LIMIT:
                st = os.lstat(fp)
                with open(fp, 'rb') as f:
                    snap[p] = ('file', f.read(), st.st_mode & 0o7777, st.st_mtime_ns)
            else:
                snap[p] = None
        except OSError:
            snap[p] = None
    return snap


def red_remove(top, p):
    """Delete path p under top (a file, link, or directory), then any parent directory left empty."""
    fp = os.path.join(top, p)
    with contextlib.suppress(OSError):
        if os.path.isdir(fp) and not os.path.islink(fp):
            shutil.rmtree(fp)
        else:
            os.remove(fp)
    d = os.path.dirname(fp)
    while d.startswith(top + os.sep):
        try:
            os.rmdir(d)
        except OSError:
            break
        d = os.path.dirname(d)


def red_restore(top, before, after, snap):
    """Undo what the (red) spans did to the work tree: for each path tree_changes(before, after) names,
    a path that was dirty before gets its saved content back, a new untracked path is deleted, and a path
    that was clean is reset to HEAD (an added path that is not in HEAD is unstaged and deleted). Returns the
    paths still different from the before state afterwards, sorted: empty when the tree is restored."""
    def git(*args):
        return subprocess.run(['git', '-C', top, *args], capture_output=True, stdin=subprocess.DEVNULL,
                              timeout=60).returncode

    for p in tree_changes(before, after):
        fp = os.path.join(top, p)
        try:
            if p in before:
                saved = snap.get(p)
                if before[p][1] is None:
                    red_remove(top, p)
                elif saved is not None:
                    if os.path.lexists(fp):
                        red_remove(top, p)
                    os.makedirs(os.path.dirname(fp), exist_ok=True)
                    if saved[0] == 'link':
                        os.symlink(saved[1], fp)
                    else:
                        with open(fp, 'wb') as f:
                            f.write(saved[1])
                        os.chmod(fp, saved[2])
                        os.utime(fp, ns=(saved[3], saved[3]))
            elif after[p][0].strip() == '??':
                red_remove(top, p)
            elif git('cat-file', '-e', f'HEAD:{p}') == 0:
                git('checkout', 'HEAD', '--', p)
            else:
                git('rm', '-f', '-q', '--cached', '--ignore-unmatch', '--', p)
                red_remove(top, p)
        except (OSError, subprocess.SubprocessError):
            pass
    now = tree_state(top)
    return tree_changes(before, now) if now is not None else sorted(tree_changes(before, after))


def red_first(items, top, cwd, base, results=None, tmp=None):
    """Run each (n, span, timeout) of items once, in order, in the current tree and return one message per
    refusal: a span that exits 0 is green now and cannot detect the change; a timeout; and, in a git work
    tree, a tree change, which is undone from a content snapshot taken before the first span (the message
    says whether the tree is restored). n is the step number, or None for a ticket handoff. Empty list: every
    span is red now. The spans run synchronously, so the caller must own the tree while they do. A list passed
    as results gets one (n, span, rc) per span, rc None on a timeout (redck.py records them). tmp, when given, is the SDLC_TMP_WORKTREES the spans run with."""
    out = []
    before = tree_state(top) if top and items else None
    snap = red_snapshot(top, before) if before is not None else {}
    for n, span, timeout in items:
        where = f'step {n}: ' if n is not None else ''
        rc, _ = run_guard(span, cwd, timeout, base, tmp)
        if results is not None:
            results.append((n, span, rc))
        if rc == 0:
            out.append(f'{where}`{span}` is green now; it cannot detect the change')
        elif rc is None:
            out.append(f'{where}`{span}` timed out after {timeout:g}s; a (red) span must exit nonzero quickly')
    after = tree_state(top) if before is not None else None
    changed = tree_changes(before, after) if after is not None else []
    if changed:
        left = red_restore(top, before, after, snap)
        state = f'not restored: {", ".join(left)}' if left else 'restored'
        out.append(f'(red) spans changed the work tree: {", ".join(changed)} ({state})')
    return out


def run_red(plan, steps, chosen, task_dir, timeouts, tree=None):
    """Run the runnable (red) spans of each chosen step, each under timeouts[n] seconds, and raise Fail
    when one is green now, times out, or changes the tree (see red_first). Called only by split --only,
    beside run_guards; a full split and lint never execute a span."""
    top = git_toplevel(tree or task_dir)
    items = [(n, text, timeouts[n]) for n in chosen for text in red_spans(steps[n]) if not guard_skipped(text)]
    with span_tmp(top) as tmp:
        found = red_first(items, top, top or str(tree or task_dir), base_sha(top), tmp=tmp)
    if found:
        record_plan_review(task_dir, plan, [f'steps: {plan} red-first: {m}' for m in found])
        raise Fail('\n'.join([f'steps: {plan} red-first: {m}' for m in found]
                             + [f'plan defect: red-first: {len(found)} refusal(s); replan this step (/chain 3)']))


OR_ALLOWED_LEFT = ['test', '$#', '-eq', '0']
OR_PUNCT = '();<>|&\n'
EXIT_CODE_RE = re.compile(r'\d+')


def skip_dquote(text, i):
    """Index just past the double-quoted string that opens at text[i], honoring a `$(...)` nested
    inside it, whose own quotes start fresh as bash reads them. Raises ValueError when unclosed."""
    i += 1
    while i < len(text):
        c = text[i]
        if c == '\\':
            i += 2
        elif c == '"':
            return i + 1
        elif text.startswith('$(', i):
            i = skip_subst(text, i + 2)
        else:
            i += 1
    raise ValueError('unclosed double quote')


def skip_subst(text, i):
    """Index just past the `)` closing a `$(` whose body starts at text[i]. Raises ValueError when
    unclosed."""
    depth = 1
    while i < len(text):
        c = text[i]
        if c == '\\':
            i += 2
            continue
        if c == "'":
            j = text.find("'", i + 1)
            if j < 0:
                raise ValueError('unclosed single quote')
            i = j + 1
            continue
        if c == '"':
            i = skip_dquote(text, i)
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError('unclosed $(')


def mask_dquotes(text):
    """The span with each top-level double-quoted string replaced by `"x"`. shlex ends a string at
    the first inner `"`, so `"$(node -e "a || b")"` would otherwise leak the quoted || as an
    operator. Single-quoted strings are kept as they are. Raises ValueError when a quote is unclosed."""
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c == '\\':
            out.append(text[i:i + 2])
            i += 2
        elif c == "'":
            j = text.find("'", i + 1)
            if j < 0:
                raise ValueError('unclosed single quote')
            out.append(text[i:j + 1])
            i = j + 1
        elif c == '"':
            i = skip_dquote(text, i)
            out.append('"x"')
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def or_tokens(text):
    """shlex tokens of a span as (token, is_operator) pairs; a newline is its own operator token.
    Double-quoted strings are masked first (mask_dquotes). Raises ValueError on text shlex cannot
    tokenize."""
    lex = shlex.shlex(mask_dquotes(text), posix=True, punctuation_chars=OR_PUNCT)
    lex.commenters = ''
    lex.whitespace = ' \t\r'
    lex.whitespace_split = True
    out = []
    for tok in lex:
        if tok and all(c in OR_PUNCT for c in tok):
            out += [(part, True) for part in re.split(r'(\n)', tok) if part]
        else:
            out.append((tok, False))
    return out


def nonzero_exit_at(toks, i):
    """True when toks[i:] starts with `exit N`, N a nonzero integer literal (mod 256, as the
    shell sees it)."""
    return (i + 1 < len(toks) and toks[i] == ('exit', False) and not toks[i + 1][1]
            and bool(EXIT_CODE_RE.fullmatch(toks[i + 1][0])) and int(toks[i + 1][0]) % 256 != 0)


def ends_command(toks, i):
    """True when a command ends before toks[i]: the end of the span, ;, &&, ||, }, or a newline. A
    lone pipe does not end a command here: `exit N | cat` pipes exit's status into cat, so the
    command's real exit status is cat's, not N's, and is not a fail-fast right operand."""
    if i >= len(toks):
        return True
    tok, op = toks[i]
    return (op and (tok.startswith(';') or tok in ('&&', '||', '\n'))) or (not op and tok == '}')


def fails_fast(toks, i):
    """True when the right operand of a || starting at toks[i] is a nonzero exit: `exit N` ending a
    command, or a brace group `{ ...; exit N; }` whose last command is such an exit."""
    if nonzero_exit_at(toks, i):
        return ends_command(toks, i + 2)
    if toks[i:i + 1] != [('{', False)]:
        return False
    depth = 0
    for j in range(i, len(toks)):
        if toks[j][1]:
            continue
        if toks[j][0] == '{':
            depth += 1
        elif toks[j][0] == '}':
            depth -= 1
            if depth == 0:
                k = j - 3
                return (k > i and toks[j - 1] in ((';', True), ('\n', True)) and nonzero_exit_at(toks, k)
                        and (k == i + 1 or toks[k - 1] in ((';', True), ('\n', True), ('&&', True)))
                        and ends_command(toks, j + 1))
    return False


def or_fallback(text):
    """True when a span holds an unquoted || that is a real fallback, one that lets the criterion
    pass when either side passes. A || is allowed when its left operand is exactly `test $# -eq 0`
    (an empty set short circuit), or when its right operand is a nonzero `exit` (`exit N`, N a
    nonzero integer literal, ending the command, or a brace group `{ ...; exit N; }` whose last
    command is that exit): a nonzero exit fails the criterion when the left side fails, so it
    cannot pass on either side. `|| exit 0`, a bare `|| exit`, `|| true`, `|| return 1`,
    `|| echo ...`, and `|| grep ...` stay findings. So does `|| exit N | cat` (or a brace group
    piped the same way): the pipe hands the exit's status to the next command, so the criterion's
    real exit status is the pipeline's last command, not N, and the left side's failure is masked.
    Pure text: executes nothing.
    Raises ValueError on text shlex cannot tokenize (an unparsable span, already reported)."""
    toks = or_tokens(text)
    left = []
    for i, (tok, op) in enumerate(toks):
        if op:
            if tok == '||' and left != OR_ALLOWED_LEFT and not fails_fast(toks, i + 1):
                return True
            if ';' in tok or '|' in tok or '&&' in tok or tok == '\n':
                left = []
                continue
        left.append(tok)
    return False


GIT_WORD_RE = re.compile(r'(?<![\w.-])git(?![\w-])')
SHA_RE = re.compile(r'(?<![A-Za-z0-9])(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![A-Za-z0-9])')
COUNT_TOOL_RE = re.compile(r'(?<![\w-])wc\s+-[A-Za-z]*l'
                           r'|(?<![\w-])grep\b[^|;&)`]*?\s(?:-[A-Za-z]*c[A-Za-z]*|--count)(?![\w-])')
SET_SOURCE_RE = re.compile(r'\*|(?<![\w./-])(?:ls|find)(?![\w.-])')
COMPARE_RE = re.compile(r'(?:(?<![\w-])-(?:eq|ne|ge|gt|le|lt)|==|!=|(?<=\s)=)\s*["\']?(\d+)(?![\w.])')


ANCESTRY_RE = re.compile(r'(?<![\w.-])git\s+merge-base\s+--is-ancestor\s+'
                         r'(?<![A-Za-z0-9])[0-9a-f]{7,40}\s+HEAD(?![\w~^@:./-])')


def pins_sha(text):
    """True when a span holds the word git and a commit-sha-like hex run fixed at plan time.
    The ancestry form git merge-base --is-ancestor <sha> HEAD is exempt; other hex runs still count."""
    if not GIT_WORD_RE.search(text):
        return False
    return bool(SHA_RE.search(ANCESTRY_RE.sub(' ', text)))


def fixed_set_count(text):
    """True when a span counts over a changing set (a glob, ls, or find) and compares the count
    with a literal integer of 2 or more."""
    return bool(COUNT_TOOL_RE.search(text) and SET_SOURCE_RE.search(text)
                and any(int(m.group(1)) >= 2 for m in COMPARE_RE.finditer(text)))


STATUS_RE = re.compile(r'(?<![\w.-])git\s+status(?![\w-])([^|;&)`]*)')
PORCELAIN_RE = re.compile(r'(?<![\w-])(?:--porcelain(?:=v[12])?|--short|-s)(?![\w-])')
PATHSPEC_RE = re.compile(r'(?<!\S)--(?=\s|$)')
EMPTY_TEST_RE = re.compile(r'(?<![\w-])-z(?![\w-])'
                           r'|(?:(?<![\w-])-eq|==|(?<![=!<>])=(?!=))\s*(?:["\']?0(?![\w.])|""|\'\')'
                           r'|(?<![\w-])!\s[^|;&]*?\|\s*grep\s+(?:-[A-Za-z]*\s+)*-[A-Za-z]*q'
                           r'|(?<![\w-])!\s.*?\bgrep\s+(?:-[A-Za-z]*\s+)*-[A-Za-z]*q')


def requires_clean_status(text):
    """True when a span requires an empty porcelain or short git status with no pathspec: a
    no-commit builder's own changes keep the status dirty, so the criterion can never pass."""
    hit = False
    for m in STATUS_RE.finditer(text):
        args = m.group(1)
        if PORCELAIN_RE.search(args) and not PATHSPEC_RE.search(args):
            hit = True
    return hit and bool(EMPTY_TEST_RE.search(text))


DIFF_RE = re.compile(r'(?<![\w.-])git\s+diff(?![\w-])([^|;&)`]*)')
DIFF_QUIET_RE = re.compile(r'(?<![\w-])(?:--quiet|--exit-code)(?![\w-])')
NEGATED_RE = re.compile(r'(?<!\S)!\s+$')
REDIRECT_RE = re.compile(r'^\d*[<>]')


def requires_clean_diff(text):
    """True when a span requires an empty git diff of the whole work tree: no `--` pathspec, no
    commit-to-commit range, no --no-index, and either an un-negated --quiet/--exit-code or an
    emptiness test on the output. A no-commit builder's own changes keep that diff non-empty."""
    empty_test = bool(EMPTY_TEST_RE.search(text))
    for m in DIFF_RE.finditer(text):
        args = m.group(1)
        if PATHSPEC_RE.search(args):
            continue
        words = [w.strip('"\'') for w in args.split()]
        if '--no-index' in words or any('..' in w for w in words):
            continue
        revs = [w for w in words if w and not w.startswith('-') and not REDIRECT_RE.match(w)]
        if len(revs) >= 2:
            continue
        quiet = bool(DIFF_QUIET_RE.search(args)) and not NEGATED_RE.search(text[:m.start()])
        if quiet or empty_test:
            return True
    return False


GREP_PERL_RE = re.compile(r'(?<![\w-])grep\b(?:\s+(?:-[A-Za-z]*P[A-Za-z]*|--perl-regexp|-[A-Za-z]+|--[a-z-]+(?:=\S+)?))*?'
                          r'\s(?:-[A-Za-z]*P[A-Za-z]*|--perl-regexp)(?![\w-])')


def uses_grep_perl(text):
    """True when a span runs grep -P (or --perl-regexp): BSD grep on macOS has no -P, fails with
    status 2, and a negated pipeline (`! ... | grep -P`) then passes vacuously."""
    return bool(GREP_PERL_RE.search(text))


FORBIDDEN_GIT_RE = re.compile(r'(?<![\w.-])git(?:\s+(?:-[Cc]\s+\S+|--[\w-]+(?:=\S+)?))*\s+'
                              r'(stash|checkout|reset|restore|commit)(?![\w-])')


def unquoted_command_text(text):
    """A span with its quoted text blanked, so a word inside quotes is not read as a command. A $( ... )
    inside double quotes keeps its text: it runs. A backslash hides the next character."""
    out = []
    i, n = 0, len(text)
    quote = None
    depth = 0
    while i < n:
        c = text[i]
        if quote is None:
            if c == '\\':
                out.append('  ')
                i += 2
                continue
            if c in '\'"':
                quote = c
                out.append(' ')
            else:
                out.append(c)
        elif depth:
            out.append(c)
            depth += (c == '(') - (c == ')')
        elif c == '\\' and quote == '"':
            out.append('  ')
            i += 2
            continue
        elif c == quote:
            quote = None
            out.append(' ')
        elif quote == '"' and text.startswith('$(', i):
            out.append('$(')
            depth = 1
            i += 1
        else:
            out.append(' ')
        i += 1
    return ''.join(out)


STASH_RE = re.compile(r'\bgit\s+stash\b|--autostash\b')


def do_stash_lines(block):
    """The lines of a step's ### Do section that run git stash or --autostash (the stash stack is shared across
    sessions; T-0666), stripped."""
    return [x.strip() for x in section_of(block, 'Do').splitlines() if STASH_RE.search(x)]


def forbidden_git(text):
    """The git subcommand (stash, checkout, reset, restore, commit) a span runs that agents/verifier.md
    rule 3 forbids a verifier, else None. Command text only: a word in quotes does not count."""
    m = FORBIDDEN_GIT_RE.search(unquoted_command_text(text))
    return m.group(1) if m else None


def read_first_paths(block):
    """The paths listed under a step block's ### Read first, up to the next ## or ### line, with
    ``` fenced lines left out. Each list item (- or *) that holds a code span gives one path: the
    text of its first code span."""
    out = []
    inside = fenced = False
    for line in block.splitlines():
        if line.startswith('## ') or line.startswith('### '):
            inside = line.strip() == '### Read first'
            fenced = False
            continue
        if not inside:
            continue
        if line.lstrip().startswith('```'):
            fenced = not fenced
            continue
        if fenced:
            continue
        text = line.lstrip()
        if not (text.startswith('- ') or text.startswith('* ')):
            continue
        m = SPAN_RE.search(text)
        if m and m.group(2).strip():
            out.append(m.group(2).strip())
    return out


SKILL_PATH_RE = re.compile(r'(?:^|/)(?:SKILL\.md|skills/[^/]+/?)$')
ROUTE_CUE_RE = re.compile(r'->|\u2192|\b(?:read|reads|use|uses|using|follow|follows)\b', re.I)
SKILL_LINK_RE = re.compile(r'\[[^\]]*\]\(<?([^)\s>]+)>?\)')


def route_path_like(text):
    """True when a code span reads as a path or glob: no whitespace, and a / or * or a file extension."""
    return not re.search(r'\s', text) and ('/' in text or '*' in text or PATH_EXT_RE.search(text) is not None)


def agents_files(top):
    """Every AGENTS.md under top, the root one included: git ls-files (tracked and untracked, ignored left
    out) inside a work tree, else a walk."""
    top = pathlib.Path(top)
    try:
        r = subprocess.run(['git', '-C', str(top), 'ls-files', '-co', '--exclude-standard', '--',
                            'AGENTS.md', '**/AGENTS.md'], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=60)
        if r.returncode == 0:
            return sorted({top / x for x in r.stdout.splitlines() if x.strip()})
    except (OSError, subprocess.TimeoutExpired):
        pass
    return sorted(top.rglob('AGENTS.md'))


def repo_skill_routes(top):
    """[(glob, skill)] from the routing lines of every AGENTS.md under top, root included. A routing line is a
    list item (- or *) or table row (|), or in a nested AGENTS.md also a prose line, whose spans (code spans, and
    markdown link targets that are skill paths, T-0676) hold exactly one skill path (a SKILL.md file or a folder
    under a skills/ directory) and at least one other path or glob (route_path_like); a list item or prose line
    also needs a routing cue (ROUTE_CUE_RE) in the text just before the skill span, so a prose bullet that merely
    mentions a skill is no route. Paths in a nested AGENTS.md resolve against its folder, a skill path only when
    it exists there, else against the repo root; every pair comes back repo-relative in posix form."""
    top = pathlib.Path(top)
    routes = []
    for f in agents_files(top):
        try:
            rel_dir = f.parent.relative_to(top).as_posix()
            text = f.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError, ValueError):
            continue
        prefix = '' if rel_dir == '.' else rel_dir + '/'
        fenced = False
        for line in text.splitlines():
            t = line.lstrip()
            if t.startswith('```'):
                fenced = not fenced
                continue
            if fenced or not (t.startswith('- ') or t.startswith('* ') or t.startswith('|') or prefix):
                continue
            links = [m for m in SKILL_LINK_RE.finditer(t) if SKILL_PATH_RE.search(m.group(1))]
            ms = sorted([m for m in SPAN_RE.finditer(t) if m.group(2).strip()
                         and not any(x.start() <= m.start() < x.end() for x in links)] + links,
                        key=lambda m: m.start())
            spans = [(m.group(1) if m.re is SKILL_LINK_RE else m.group(2)).strip() for m in ms]
            skills = [x for x in spans if route_path_like(x) and SKILL_PATH_RE.search(x)]
            others = [x for x in spans if route_path_like(x) and not SKILL_PATH_RE.search(x)]
            if len(skills) != 1 or not others:
                continue
            if not t.startswith('|'):
                k = next(i for i, x in enumerate(spans) if x == skills[0])
                if not ROUTE_CUE_RE.search(t[ms[k - 1].end() if k else 0:ms[k].start()]):
                    continue
            skill = prefix + skills[0] if (f.parent / skills[0]).exists() else skills[0]
            routes += [(prefix + (g[2:] if g.startswith('./') else g), skill) for g in others]
    return routes


def route_matches(glob, path):
    """True when a repo-relative path falls under a route glob: a trailing / matches the folder prefix,
    otherwise fnmatch."""
    return path.startswith(glob) if glob.endswith('/') else fnmatch.fnmatch(path, glob)


def skill_key(path):
    """A skill path compared by its folder: a trailing / and a final /SKILL.md left out."""
    path = path.rstrip('/')
    return path[:-len('/SKILL.md')] if path.endswith('/SKILL.md') else path


def routed_skills(top, paths, routes=None):
    """The skill paths whose route globs (repo_skill_routes) match any of the repo-relative paths, in route order,
    each once."""
    out = []
    for glob, skill in (repo_skill_routes(top) if routes is None else routes):
        if skill not in out and any(route_matches(glob, p) for p in paths):
            out.append(skill)
    return out


def cmd_routes(paths):
    """routes [<path>...]: with no path, one `<glob> -> <skill>` line per repo_skill_routes pair of the git
    toplevel of the cwd, else `no skill routes`; with paths, one `<path>: <skill>, ...` line per path from
    routed_skills, else `<path>: none`. Writes nothing; exit 0."""
    top = git_toplevel(os.getcwd()) or os.getcwd()
    routes = repo_skill_routes(top)
    if not paths:
        for glob, skill in routes:
            print(f'{glob} -> {skill}')
        if not routes:
            print('no skill routes')
        return 0
    for path in paths:
        print(f'{path}: {", ".join(routed_skills(top, [path], routes)) or "none"}')
    return 0


PLAN_DEFECT_PREFIX = 'plan defect:'
PATH_TRIM = '`\'"()[]{}<>,;:.*'
PATH_LINENO_RE = re.compile(r':\d+(?::\d+)?$')
PATH_EXT_RE = re.compile(r'[A-Za-z0-9_-]\.[A-Za-z0-9]{1,8}$')


def trim_path_token(raw):
    """One whitespace token trimmed of markdown and sentence punctuation (PATH_TRIM), a trailing :line, and any
    leading ./ (the one trim defect_path_tokens and order_path_tokens share)."""
    tok = raw.strip(PATH_TRIM)
    tok = PATH_LINENO_RE.sub('', tok).strip(PATH_TRIM)
    while tok.startswith('./'):
        tok = tok[2:]
    return tok


def defect_path_tokens(text, base):
    """The path tokens in one `plan defect:` line's text: a whitespace-separated token, trimmed of
    markdown and sentence punctuation (and a trailing :line), that holds a / or ends in a file
    extension, is relative with no .. part, and names an existing file or folder under base. A word
    such as and/or, pass/fail, or c1 names nothing on disk and is no token."""
    out = []
    for raw in text.split():
        tok = trim_path_token(raw)
        if not tok or tok.startswith(('/', '~', '-', '$')) or '://' in tok:
            continue
        if '/' not in tok and not PATH_EXT_RE.search(tok):
            continue
        if '..' in tok.split('/') or not (base / tok).exists():
            continue
        if tok not in out:
            out.append(tok)
    return out


def defect_dependents(plan, steps):
    """One finding per path a `plan defect:` line named in a step-*/verifier-*.md or step-*/builder-*.md
    beside the plan (the superseded step-<n>.superseded-<k>/ folders count) that no ## Step block holds,
    read as a substring: a contract dependent a verifier flagged must reach the replan (planner.md).
    The plan's folder is the task dir; paths resolve against its git toplevel, else that folder."""
    folder = pathlib.Path(plan).resolve().parent
    results = sorted(p for kind in ('verifier', 'builder') for p in folder.glob(f'step-*/{kind}-*.md'))
    if not results:
        return []
    base = pathlib.Path(git_toplevel(folder) or folder)
    blocks = list(steps.values())
    seen, findings = set(), []
    for res in results:
        try:
            lines = res.read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line.startswith(PLAN_DEFECT_PREFIX):
                continue
            for tok in defect_path_tokens(line[len(PLAN_DEFECT_PREFIX):], base):
                if tok in seen or any(tok in block for block in blocks):
                    continue
                seen.add(tok)
                findings.append(f'steps: {plan}: no step names {tok}, which {res.relative_to(folder)} flagged '
                                f'on a {PLAN_DEFECT_PREFIX} line\n'
                                '  put it in a step: name it in the Do and the scope criterion, with a criterion '
                                'that runs it, or name it in a Do with the reason it stays untouched')
    return findings


NODE_TEST_RE = re.compile(r'\bnode\s+(?:--?[A-Za-z][\w=-]*\s+)*--test\b((?:\s+[^\s;&|<>]+)*)')
TEST_FILE_EXT_RE = re.compile(r'\.(?:[cm]?[jt]sx?)$')
COUNT_RE = re.compile(r'\b\d+\s+(?:(?:unit |passing |new |failing )?(?:tests?|cases?|checks?|assertions?|files?|specs?)|passed|passing)\b')


def node_test_dir(text):
    """True when a span runs `node --test` on a directory: a positional argument with no script
    extension and no glob character (a bare `node --test` finds no tests in some node versions and
    a dir argument is read as a module path, so the criterion fails or runs nothing)."""
    for m in NODE_TEST_RE.finditer(text):
        for tok in m.group(1).split():
            tok = tok.strip('"\'')
            if tok.startswith('-') or any(c in tok for c in '*?[{$'):
                continue
            if tok.endswith('/') or not TEST_FILE_EXT_RE.search(tok):
                return True
    return False


def count_warnings(plan, steps):
    """One warning per top-level acceptance criterion that cites a numeric count (12 tests) with no
    command code span naming where the count comes from."""
    out = []
    for n, block in steps.items():
        for line in criteria_lines(block):
            if not re.match(r'^[-*] ', line) or not COUNT_RE.search(line) or line_spans(line):
                continue
            out.append(f'steps lint: warning: {plan} step {n}: criterion cites a count without a named '
                       f'source file or command: {line.strip()[:100]}\n'
                       '  name the command or file the count comes from, so a verifier can recompute it')
    return out


HISTORY_RE = re.compile(r'\bgit\s+(?:-\S+\s+)*(?:log|rev-list)\b|--oneline\b')


def history_warnings(plan, steps):
    """One warning per command span in an acceptance criterion that reads commit history (git log,
    git rev-list, --oneline output): the commit count or subject changes with every replan, rebase,
    or squash, so the criterion goes stale before the builder runs it (T-0475). Advisory only."""
    out = []
    for n, block in steps.items():
        for line in criteria_lines(block):
            for span in line_spans(line):
                if HISTORY_RE.search(span):
                    out.append(f'steps lint: warning: {plan} step {n}: history-shaped criterion: '
                               f'{span[:100]}\n  name the state the commit leaves (a file, a test, a diff), '
                               'not its commit count or subject')
    return out


# tickets.ABS_PATH_RE: a personal path in a tracked criterion trips a repo's personal-path gate (T-0686)
ABS_HOME_RE = re.compile(r'/Users/|/home/|/var/folders/|/private/tmp/')


def abs_path_warnings(plan, steps):
    """One warning per acceptance criterion line holding an absolute home or temp path; it names the code span
    that holds the path, else the line. Advisory only (T-0686)."""
    out = []
    for n, block in steps.items():
        for line in criteria_lines(block):
            if not ABS_HOME_RE.search(line):
                continue
            span = next((s for s in line_spans(line) if ABS_HOME_RE.search(s)), line.strip())
            out.append(f'steps lint: warning: {plan} step {n}: absolute home path in a criterion: {span[:100]}\n'
                       '  use a repo-relative path or $TMPDIR, so the tracked record passes a personal-path gate')
    return out


# --- step handoff links (T-0379) ----------------------------------------------
# A replanned step's handoff is split from a plan written while step-<n>/ still held the previous attempt's
# reports; /chain 4.2 then renames that folder to step-<n>.superseded-<k>/, so a path in the plan that names
# step-<n>/builder-L3.md now points at nothing (or, after the rebuild, at the NEW attempt's report). The
# producer is the plan text, which split copies verbatim; the rewrite below and the lint check close it.

_CITE_RES = {}


def cite_re(prefixes=('.sdlc/',)):
    """The citation regex for repo-relative record prefixes (roots.record_prefixes): group 1 is the path, group p
    the prefix it cites."""
    if prefixes not in _CITE_RES:
        alt = '|'.join(re.escape(x) for x in prefixes)
        _CITE_RES[prefixes] = re.compile(
            r"""(?:^|[\s`'"(\[=])((?:[^\s`'"()<>\[\],;|]*/)?(?P<p>""" + alt + r""")[^\s`'"()<>\[\],;|]+)""")
    return _CITE_RES[prefixes]


CITE_RE = cite_re()
REPORT_FILE_RE = re.compile(r'^[a-z][a-z-]*-L[1-5](?:-\d+)?\.md$')
STEP_DIR_RE = re.compile(r'^step-(\d+)$')
SUPERSEDED_RE = re.compile(r'^step-(\d+)\.superseded-(\d+)$')


def sdlc_base(folder):
    """The tree a cited .sdlc/... path resolves against: the nearest ancestor of folder (itself included) that
    holds a .sdlc folder, else the git toplevel of folder, else folder."""
    folder = pathlib.Path(folder).resolve()
    for a in [folder] + list(folder.parents):
        if (a / '.sdlc').is_dir():
            return a
    return pathlib.Path(git_toplevel(folder) or folder)


def record_prefixes(base):
    """roots.record_prefixes of base: ('.sdlc/',) plus '<work_root>/' when base/.sdlc/config sets one; a refused
    config gives ('.sdlc/',)."""
    try:
        return sdlc_roots.record_prefixes(base)
    except sdlc_roots.Fail:
        return ('.sdlc/',)


def cited_sdlc_paths(text, prefixes=('.sdlc/',)):
    """[(start, end, rel, anchor)] for each .sdlc/... path in text (and each <work_root>/... path when prefixes,
    from record_prefixes, names one): rel starts at its prefix, [start, end) is its
    span in text; anchor is the absolute folder the path was written under (so it resolves exactly as written),
    or None for a relative citation, which resolves against sdlc_base. A path whose prefix is exactly / is no citation (T-0474). A path that runs into a placeholder or glob (<n>, *, {a,b}, $VAR, ?) or is only a folder stem is no
    citation; a trailing sentence dot or :line is trimmed."""
    out = []
    for m in cite_re(prefixes).finditer(text):
        raw, at, pre = m.group(1), m.start(1), m.group('p')
        i = raw.index(pre)
        if raw[:i] == '/':
            continue
        rel, start = raw[i:], at + i
        rel = PATH_LINENO_RE.sub('', rel.rstrip('.:')).rstrip('.:')
        end = start + len(rel)
        if any(c in rel for c in '*{}$?') or text[end:end + 1] in ('<', '*', '{', '$', '?') or len(rel) <= len(pre):
            continue
        out.append((start, end, rel, pathlib.Path(raw[:i]) if raw.startswith('/') else None))
    return out


def superseded_holders(base, rel):
    """For rel = .sdlc/.../step-<n>/<report>: the sibling step-<n>.superseded-<k>/ folders that hold that report,
    newest attempt (highest k) first. [] for any other path."""
    p = pathlib.Path(base) / rel
    mm = STEP_DIR_RE.match(p.parent.name)
    if not mm or not REPORT_FILE_RE.match(p.name) or not p.parent.parent.is_dir():
        return []
    found = []
    for d in p.parent.parent.iterdir():
        sm = SUPERSEDED_RE.match(d.name)
        if sm and sm.group(1) == mm.group(1) and (d / p.name).is_file():
            found.append((int(sm.group(2)), d.name))
    return [name for _, name in sorted(found, reverse=True)]


def superseded_rel(rel, holder):
    """rel with its step-<n> folder replaced by the superseded folder name holder."""
    pp = pathlib.PurePosixPath(rel)
    return str(pp.parent.parent / holder / pp.name)


def rewrite_prior_links(text, base):
    """(new text, [(old rel, new rel)]): every cited step-<n>/<report> that no longer exists in the live step
    folder, while a step-<n>.superseded-<k>/ sibling holds that report, now names the newest such sibling. A
    path that exists, one that already names a superseded folder, and any other path stay as written; no report
    file is touched."""
    changes, pieces, last = [], [], 0
    for start, end, rel, anchor in cited_sdlc_paths(text, record_prefixes(base)):
        root = anchor or pathlib.Path(base)
        if (root / rel).exists():
            continue
        holders = superseded_holders(root, rel)
        if not holders:
            continue
        new = superseded_rel(rel, holders[0])
        pieces += [text[last:start], new]
        last = end
        changes.append((rel, new))
    return ''.join(pieces) + text[last:], changes


def previous_attempt_span(text):
    """(start, end) of the ## Previous attempt section of a step handoff, or None. Its citations name the live
    attempt's reports and are never a prior-attempt link."""
    m = re.search(r'^## Previous attempt[ \t]*$', text, re.M)
    if not m:
        return None
    nxt = re.search(r'^## ', text[m.end():], re.M)
    return m.start(), m.end() + (nxt.start() if nxt else len(text) - m.end())


CREATES_MARK_RE = re.compile(r'\[creates:\s*([^\]]+)\]', re.I)
OUTPUTS_LINE_RE = re.compile(r'^[ \t]*(?:[-*][ \t]+)?\**outputs?\**[ \t]*:', re.I | re.M)
CREATE_VERB_RE = re.compile(r'\b(?:creat(?:e|es|ing)|writ(?:e|es|ing)|add(?:s|ing)?|new file|generat(?:e|es|ing))\b', re.I)
FOREIGN_LINE_RE = re.compile(r'^[ \t]*(?:[-*][ \t]+)?\**(?:other|foreign) repos?\**[ \t]*:[ \t]*(.+)$', re.I | re.M)
PREFIX_RE = re.compile(r"""[^\s`'"()<>\[\],;|]*/$""")


def section_of(text, heading):
    """The body of the first `### <heading>` (or `## <heading>`) section of text, or ''."""
    m = re.search(rf'^##+ {re.escape(heading)}[ \t]*$', text, re.M)
    if not m:
        return ''
    nxt = re.search(r'^##+ ', text[m.end():], re.M)
    return text[m.end():m.end() + (nxt.start() if nxt else len(text))]


def declared_future_paths(text, prefixes=('.sdlc/',)):
    """The .sdlc (and work root, per prefixes) paths the handoff says the step itself creates: a [creates: <path>, ...] marker anywhere, a
    path on an `Outputs:` line, a path after a create verb (create, write, add, generate, new file) on a line of
    ### Do, and a path inside a code span of a (red) criterion (it runs only after the build). A declared folder
    covers the paths under it."""
    out = set()
    for m in CREATES_MARK_RE.finditer(text):
        out.update(r for r in (p.strip().strip('`').rstrip('.:') for p in re.split(r'[,\s]+', m.group(1))) if r)
    for m in OUTPUTS_LINE_RE.finditer(text):
        eol = text.find('\n', m.end())
        line = text[m.end():eol if eol >= 0 else len(text)]
        out.update(rel for _, _, rel, _ in cited_sdlc_paths(' ' + line, prefixes))
    for line in section_of(text, 'Do').splitlines():
        v = CREATE_VERB_RE.search(line)
        if v:
            out.update(rel for st, _, rel, _ in cited_sdlc_paths(' ' + line, prefixes) if st - 1 > v.start())
    for span in red_spans(text):
        out.update(rel for _, _, rel, _ in cited_sdlc_paths(' ' + span, prefixes))
    return out


def covered_by(rel, created):
    """True when rel is a declared created path or lies under a declared created folder."""
    return any(rel == f or rel.startswith(f.rstrip('/') + '/') for f in created)


def earlier_created(task_dir, n, prefixes=('.sdlc/',)):
    """The paths the steps before step n declare they create (declared_future_paths, T-0533): from the
    newest plan's ## Step blocks and the live step-<m>/handoff.md files with m < n. A step may cite a path an
    earlier step creates."""
    out = set()
    with contextlib.suppress(Fail, OSError, UnicodeError):
        plan, _ = find_plan(pathlib.Path(task_dir))
        for m, block in parse_steps(plan).items():
            if m < n:
                out |= declared_future_paths(block, prefixes)
    for m, d in step_dirs(task_dir).items():
        h = step_handoff(d)
        if m < n and h.is_file():
            with contextlib.suppress(OSError, UnicodeError):
                out |= declared_future_paths(h.read_text(encoding='utf-8'), prefixes)
    return out


def foreign_repo_names(text):
    """The repo names a handoff line `Other repo: <name>[, <name>]` (or `Foreign repos:`) declares."""
    return {n.strip('` .') for m in FOREIGN_LINE_RE.finditer(text) for n in re.split(r'[,;]\s*', m.group(1)) if n.strip('` .')}


def repo_roots(folder):
    """The resolved trees that are this repository: the git toplevel of folder and the main checkout when folder
    is a linked worktree. [] outside git (no absolute path is then foreign)."""
    top = git_toplevel(folder)
    if not top:
        return []
    roots = [pathlib.Path(top).resolve()]
    try:
        r = subprocess.run(['git', '-C', str(folder), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            roots.append(pathlib.Path(r.stdout.strip()).resolve().parent)
    except (OSError, subprocess.TimeoutExpired):
        pass
    return roots


def is_foreign_citation(text, start, anchor, roots, names):
    """True when the cited path belongs to another repository: an absolute path under none of roots, or a path
    prefixed with a folder named in names (the handoff's `Other repo:` line)."""
    if anchor is not None and roots:
        a = anchor.resolve()
        if not any(a == r or r in a.parents for r in roots):
            return True
    m = PREFIX_RE.search(text[:start])
    return bool(m and names and names & set(pathlib.PurePosixPath(m.group(0)).parts))


def link_findings(handoff):
    """One finding per cited .sdlc path of a step handoff that cannot be trusted before a role is dispatched:
    the path does not exist (the fix is named when a superseded sibling holds the report), or it is a report
    inside the handoff's own step folder that has a step-<n>.superseded-<k>/ sibling (a link meant for the
    previous attempt, which a later report of the same name would satisfy), outside ## Previous attempt. A missing path the step declares it creates, or that is foreign
    (declared_future_paths, is_foreign_citation; T-0457), is not a finding. [] when clean. Runs nothing."""
    handoff = pathlib.Path(handoff)
    text = handoff.read_text(encoding='utf-8')
    base = sdlc_base(handoff.parent)
    prefixes = record_prefixes(base)
    own = handoff.resolve().parent
    prev = previous_attempt_span(text)
    seen, findings = set(), []
    future, names, roots = declared_future_paths(text, prefixes), foreign_repo_names(text), repo_roots(handoff.parent)
    sm = STEP_DIR_RE.match(own.name)
    if sm:
        future |= earlier_created(own.parent, int(sm.group(1)), prefixes)
    for start, _, rel, anchor in cited_sdlc_paths(text, prefixes):
        root = anchor or base
        key = (str(anchor), rel)
        if key in seen:
            continue
        seen.add(key)
        p = root / rel
        if not p.exists() and (is_foreign_citation(text, start, anchor, roots, names)
                               or covered_by(rel, future)):
            continue
        holders = superseded_holders(root, rel)
        shown = f'{anchor}/{rel}' if anchor else rel
        fix = (f'; the previous attempt is {anchor}/{superseded_rel(rel, holders[0])}' if anchor
               else f'; the previous attempt is {superseded_rel(rel, holders[0])}') if holders else ''
        if not p.exists():
            findings.append(f'steps: {handoff}: cited path does not exist: {shown}{fix}')
        elif holders and p.resolve().parent == own and not (prev and prev[0] <= start < prev[1]):
            findings.append(f'steps: {handoff}: {rel} names a report of a prior attempt of this step '
                            f'(a later report of that name would satisfy it){fix}')
    return findings


def tests_findings(plan, steps):
    """One finding per `tests:` entry in a step block that is not an exact repo-relative file path (declared_tests)."""
    return [f'steps: {plan} step {n}: tests: names {t}, which is not an exact repo-relative file path\n'
            '  list files such as tests/a.sh, not a directory, a glob, an absolute path, or a path with ..'
            for n, block in steps.items() for t in declared_tests(block)[1]]


VERIFIER_RESULT_RE = re.compile(r'verifier-L[\d*?\[]')
STEP_FOLDER_RE = re.compile(r'\bstep-(\d+)/')
FINDING_STEP_RE = re.compile(r'\bstep (\d+):')
PLAN_REVIEW_DATED_RE = re.compile(r'^- \d{4}-\d{2}-\d{2} (.*)$')


def reads_own_verifier(text, n, roots=()):
    """True when a criterion span of step n names a verifier result (verifier-L<d>) and names no step-<m>/
    folder with m other than n, or names step-<n>/verifier-L<d> itself: it can pass only after this step's own
    verifier passes. A span that names an earlier step's folder (step-1/verifier-L2.md from step 2) is fine.
    A verifier result at an absolute path under none of roots (T-0613; repo_roots) belongs to another
    repository's ticket and is not this step's own; a relative or in-repo path still counts."""
    own_hits = [t for t in re.split(r'[\s`\'"]+', text) if VERIFIER_RESULT_RE.search(t)
                and not (roots and foreign_absolute(t, roots))]
    if not own_hits:
        return False
    if any(re.search(rf'\bstep-{n}/verifier-L[\d*?\[]', t) for t in own_hits):
        return True
    return all(int(m) == n for m in STEP_FOLDER_RE.findall(text))


def foreign_absolute(token, roots):
    """True when the token (a NAME= prefix dropped) is an absolute path under none of roots: another repository."""
    path = token.split('=', 1)[-1]
    if not path.startswith('/'):
        return False
    a = pathlib.Path(path).resolve()
    return not any(a == r or r in a.parents for r in roots)


def held_line(line):
    """True when a criterion line ends with a bracket clause (CLAUSE_RE) outside any code span: a held criterion."""
    m = CLAUSE_RE.search(line)
    return m is not None and line[:m.start()].count('`') % 2 == 0


def record_plan_review(task_dir, plan, findings):
    """Append one line per split refusal finding under ## Plan review in the task's handoff.md (T-0543), the shape
    fleet_collect's SPLIT_DEFECT_RE counts: `- <YYYY-MM-DD> plan defect at split: step <n>: <why>`, n the first
    "step <n>:" of the finding's first line and why the rest of that line; with no step, `- <date> plan defect at
    split: <that line after its "steps: <plan>" prefix>`. The handoff is order.task_dir's for a records path, else
    task_dir's own; when it is absent nothing is written. The section is created at the end of the file when
    missing. A line whose text after the date the section already holds is skipped. No findings, no write; a read
    or write failure (a read-only tree) is skipped silently, so no caller's exit code or output changes."""
    if not findings:
        return
    try:
        h = task_of(task_dir) / 'handoff.md'
        if not h.is_file():
            return
        with open(h, encoding='utf-8', newline='') as f:
            text = f.read()
        held, inside = set(), False
        for line in text.splitlines():
            if line.startswith('## '):
                inside = line.rstrip() == '## Plan review'
            elif inside and (m := PLAN_REVIEW_DATED_RE.match(line.rstrip())):
                held.add(m.group(1))
        date = time.strftime('%Y-%m-%d', time.gmtime())
        new = text
        for f in findings:
            first = f.split('\n', 1)[0]
            m = FINDING_STEP_RE.search(first)
            if m:
                body = f'plan defect at split: step {m.group(1)}: {first[m.end():].strip()}'
            else:
                rest = first[len(f'steps: {plan}'):] if first.startswith(f'steps: {plan}') else first
                body = f'plan defect at split: {rest.lstrip(": ").strip()}'
            body = repo_relative(body, task_dir)
            if body in held:
                continue
            held.add(body)
            new = section_text(new, '## Plan review', f'- {date} {body}', at_end=True)
        if new != text:
            with open(h, 'w', encoding='utf-8', newline='') as fh:
                fh.write(new)
    except (OSError, UnicodeError):
        pass


def full_gate_commands_for(plan):
    """The `full_gate:` commands of the plan's .sdlc/config when the inner-loop profile governs the task (T-0510): a
    `profile: inner-loop` line there and no `profile: default` line in the task's handoff.md; else []."""
    try:
        import tickets  # local, as lane_action: a copy of steps.py beside only order.py and results.py has no tickets.py
    except ImportError:
        return []
    folder = pathlib.Path(plan).resolve().parent
    root = sdlc_root(folder)
    h = task_of(folder) / 'handoff.md'
    text = h.read_text(encoding='utf-8') if h.is_file() else ''
    return tickets.full_gate_commands(root) if tickets.inner_loop(root, text) else []


IMAGE_PATH_RE = re.compile(r'[\w./@+-]+\.(?:png|jpe?g|webp|gif)\b')


def parity_findings(plan, steps):
    """One finding per (parity) criterion line of a plan step that names fewer than two distinct image
    paths (.png, .jpg, .jpeg, .webp, .gif) or no property list (a colon after the last image path, then text)."""
    out = []
    for n, block in steps.items():
        for line in criteria_lines(block):
            if 'parity' not in leading_tags(line):
                continue
            paths = list(IMAGE_PATH_RE.finditer(line))
            if len({m.group(0) for m in paths}) < 2:
                out.append(f'steps: {plan} step {n}: (parity) criterion names fewer than two image paths: {line.strip()}\n'
                           '  form: - (parity) `<capture command>` writes `<real.png>`; against `<mock.png>`: <property>, <property>')
            elif not re.match(r"[>`'\"]*\s*:\s*\w", line[paths[-1].end():]):
                out.append(f'steps: {plan} step {n}: (parity) criterion names no property list: {line.strip()}\n'
                           '  name at most five properties after the mockup path, after a colon, never "matches"')
    return out


ASSIGN_PREFIX_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=')


def order_path_tokens(text):
    """The path-like tokens of a span or line for the order check (T-0536): a whitespace token trimmed as
    trim_path_token, with a leading NAME= assignment prefix dropped, that holds a / or ends in a file extension;
    skipped when it starts with /, ~, -, $, <, >, or 2>, holds :// or *, or has a .. part. Existence is not checked."""
    out = []
    for raw in text.split():
        bare = raw.lstrip('`\'"(')
        if bare.startswith(('<', '>', '2>')) or '*' in raw:
            continue
        tok = trim_path_token(raw)
        tok = trim_path_token(ASSIGN_PREFIX_RE.sub('', tok))
        if not tok or tok.startswith(('/', '~', '-', '$', '<', '>', '2>')) or '://' in tok or '*' in tok:
            continue
        if '/' not in tok and not PATH_EXT_RE.search(tok):
            continue
        if '..' in tok.split('/'):
            continue
        if tok not in out:
            out.append(tok)
    return out


def declared_future_any(block):
    """The paths of any kind a step block declares it creates (T-0536; the general-path twin of
    declared_future_paths, which reads only .sdlc paths): a [creates: <path>, ...] marker, a path on an Outputs:
    line, and a path after a create verb on a line of its ### Do section."""
    out = set()
    for m in CREATES_MARK_RE.finditer(block):
        out.update(order_path_tokens(m.group(1).replace(',', ' ')))
    for m in OUTPUTS_LINE_RE.finditer(block):
        eol = block.find('\n', m.end())
        out.update(order_path_tokens(block[m.end():eol if eol >= 0 else len(block)]))
    for line in section_of(block, 'Do').splitlines():
        v = CREATE_VERB_RE.search(line)
        if v:
            out.update(order_path_tokens(line[v.end():]))
    return out


def without_criteria(block):
    """A step block with its ### Acceptance criteria section (heading and body, up to the next ## or ### line) cut out."""
    kept, inside = [], False
    for line in block.splitlines():
        if line.startswith('## ') or line.startswith('### '):
            inside = line.strip() == '### Acceptance criteria'
            if inside:
                continue
        if not inside:
            kept.append(line)
    return '\n'.join(kept)


def order_findings(plan, steps, base):
    """One finding per (step n, path) where a non-(guard) criterion span of step n names a path that does not exist
    under base, that no step k <= n names outside its acceptance criteria, and that a later step m > n declares it
    creates (declared_future_any): the criterion can pass only after step m (T-0536). Names the first such m."""
    order = sorted(steps)
    owned = {n: without_criteria(steps[n]) for n in order}
    declared = {n: declared_future_any(steps[n]) for n in order}
    findings = []
    for n in order:
        seen = set()
        for line in criteria_lines(steps[n]):
            if is_guard_line(line):
                continue
            for span in line_spans(line):
                for tok in order_path_tokens(span):
                    if tok in seen or (base / tok).exists():
                        continue
                    if any(tok in owned[k] for k in order if k <= n):
                        continue
                    m = next((m for m in order if m > n and covered_by(tok, declared[m])), None)
                    if m is None:
                        continue
                    seen.add(tok)
                    findings.append(f'steps: {plan} step {n}: acceptance criterion names {tok}, which a later step '
                                    f'creates (step {m}), so it can pass only after step {m}: {span}\n'
                                    f"  move the criterion to step {m}, or name the path in this step's Do when this "
                                    'step creates it')
    return findings


QUANTIFIER_RE = re.compile(r'\b(?:every|all|each)\b', re.I)
ENUMERATION_RE = re.compile(r'\benumerat|\bsampl|\b(?:\d+|[kn]) of (?:\d+|n)\b', re.I)


def quantified_prose(block):
    """The criterion items of a step block (a list item joined with its indented continuation lines) that hold
    no command span (line_spans) yet quantify over a set in prose (the whole word every, all or each) without
    naming an enumeration or sample (enumerate, k of N, sample): a verifier can only pass them by reading. Words
    inside a code span are not prose, and a numeric count (COUNT_RE) is left to count_warnings."""
    items = []
    for line in criteria_lines(block):
        if list_item(line):
            items.append(line.strip())
        elif items and line.startswith((' ', '\t')) and line.strip():
            items[-1] += ' ' + line.strip()
    out = []
    for x in items:
        prose = SPAN_RE.sub(' ', x)
        if (not line_spans(x) and QUANTIFIER_RE.search(prose) and not ENUMERATION_RE.search(prose)
                and not COUNT_RE.search(x)):
            out.append(x)
    return out


def lint_steps(plan, steps, tree=None):
    """Return one finding per command-like criterion span that bash -n cannot parse; for a span that
    parses, one per unquoted || join, one per forbidden git command (forbidden_git), one for a pinned commit sha, one for a count over a changing
    set compared with a fixed number, and one for a span that reads its own step's verifier result on a
    line with no held clause (reads_own_verifier); one per quantified prose criterion with no command
    (quantified_prose); one per ### Read first path that does not exist, resolved against
    the git toplevel of the plan's folder (else that folder); one per skill an AGENTS.md routes a scoped path
    to that ### Read first leaves out (repo_skill_routes); one per path a verifier or builder result
    beside the plan named on a `plan defect:` line that no step names (defect_dependents); [] when
    clean. bash -n parses and never executes."""
    findings = []
    base = None
    full_gates = full_gate_commands_for(plan)
    created = set()
    routes = None
    roots = repo_roots(pathlib.Path(plan).resolve().parent)
    for n, block in steps.items():
        paths = read_first_paths(block)
        if paths and base is None:
            folder = pathlib.Path(plan).resolve().parent
            base = pathlib.Path(lane_tree(folder, tree) or folder)
        for rel in paths:
            if (not (base / rel).exists() and not covered_by(rel, created)
                    and not superseded_holders(sdlc_base(pathlib.Path(plan).resolve().parent), rel)):
                findings.append(f'steps: {plan} step {n}: ### Read first lists a path that does not exist: {rel}')
        scoped = scope_entries(block)
        if scoped:
            if routes is None:
                folder = pathlib.Path(plan).resolve().parent
                try:
                    routes = repo_skill_routes(lane_tree(folder, tree) or folder)
                except Fail:
                    routes = repo_skill_routes(folder)
            listed = {skill_key(p) for p in paths}
            for glob, skill in routes:
                hit = next((p for p in scoped if route_matches(glob, p)), None)
                if hit and skill_key(skill) not in listed:
                    listed.add(skill_key(skill))
                    findings.append(f'steps: {plan} step {n}: plan defect: edits routed path {hit} without its '
                                    f'skill under ### Read first: {skill}')
        created |= declared_future_paths(block)
        for line in do_stash_lines(block):
            findings.append(f'steps: {plan} step {n}: plan defect: ### Do runs git stash or --autostash: {line}\n'
                            '  the stash stack is shared across sessions: snapshot with a WIP commit or a '
                            'git worktree add --detach copy instead')
        for line in quantified_prose(block):
            findings.append(f'steps: {plan} step {n}: plan defect: quantified prose criterion has no command: {line}\n'
                            '  a verifier can only pass it by reading: add a runnable check, or say to enumerate '
                            'the set as k of N with a source pointer per item')
        for line, text in [(x, t) for x in criteria_lines(block) for t in line_spans(x)]:
            if text in full_gates and is_guard_line(line):
                findings.append(f'steps: {plan} step {n}: plan defect: full gate `{text}` owned by the merge gate; '
                                'a (guard) names the local_gate: command instead (inner-loop profile, .sdlc/config)')
                continue
            probe = fill_placeholders(text)
            try:
                r = subprocess.run(['bash', '-n', '-c', '--', probe], capture_output=True, text=True, timeout=5)
                rc, err = r.returncode, r.stderr
            except subprocess.TimeoutExpired:
                rc, err = 1, 'bash -n did not finish within 5 seconds'
            if rc != 0:
                lines = [f'steps: {plan} step {n}: acceptance criterion command does not parse: {text}']
                lines += [f'  {e}' for e in err.splitlines() if e.strip()]
                crit = next((x for x in block.splitlines() if text in x), '')
                if crit.count('`') > 2:
                    lines.append('  hint: a backtick inside a command ends the code span; avoid nested backticks '
                                 'and build the string by concatenation, e.g. node -e "console.log(\'a\' + \'b\')"')
                findings.append('\n'.join(lines))
                continue
            try:
                joined = or_fallback(text)
            except ValueError:
                joined = False
            if joined:
                findings.append(f'steps: {plan} step {n}: acceptance criterion joins two checks with ||: {text}\n'
                                '  the fallback can pass on either side, so the criterion cannot fail: '
                                'split it into separate criteria')
            if pins_sha(text):
                findings.append(f'steps: {plan} step {n}: acceptance criterion pins a commit sha fixed at plan time: '
                                f'{text}\n'
                                '  compare against HEAD at build start (`HEAD`, `HEAD~1`) instead: '
                                'a fixed sha goes stale on the first sync from main '
                                '(only `git merge-base --is-ancestor <sha> HEAD` may name a sha)')
            sub = forbidden_git(text)
            if sub:
                findings.append(f'steps: {plan} step {n}: plan defect: acceptance criterion runs git {sub}, which '
                                f'the verifier may not run (agents/verifier.md rule 3): {text}\n'
                                '  to compare against base, use a git worktree add --detach copy '
                                'or read-only git (log, diff, show, rev-parse, status)')
            if node_test_dir(text):
                findings.append(f'steps: {plan} step {n}: acceptance criterion runs node --test on a directory: '
                                f'{text}\n'
                                '  name the test files or a glob (node --test dir/*.test.js)')
            if fixed_set_count(text):
                findings.append(f'steps: {plan} step {n}: acceptance criterion compares a count over a changing set '
                                f'with a fixed number: {text}\n'
                                '  other lanes change the set: derive the set at run time, '
                                "or check only this step's own items")
            if uses_grep_perl(text):
                findings.append(f'steps: {plan} step {n}: acceptance criterion uses grep -P: {text}\n'
                                '  BSD grep on macOS has no -P, so it errors and a negated pipeline passes '
                                'vacuously: use python3 -c, or grep -E with a literal byte sequence '
                                '(grep -E $(printf "\\xe2\\x80\\x94"))')
            if requires_clean_status(text):
                findings.append(f'steps: {plan} step {n}: acceptance criterion requires a clean porcelain status: '
                                f'{text}\n'
                                "  builders never commit, so the step's own changes keep the status dirty and the "
                                'criterion can never pass: check `git diff --quiet HEAD -- <path>` plus untracked '
                                'files (`git ls-files --others --exclude-standard -- <path>`) instead')
            if requires_clean_diff(text):
                findings.append(f'steps: {plan} step {n}: acceptance criterion requires a clean whole-tree diff: '
                                f'{text}\n'
                                "  builders never commit, so the step's own changes keep the whole-tree diff "
                                'non-empty and the criterion can never pass: check '
                                '`git diff --quiet "$SDLC_BASE_SHA" -- <path>` plus untracked files '
                                '(`git ls-files --others --exclude-standard -- <path>`) instead')
            if reads_own_verifier(text, n, roots) and not held_line(line):
                findings.append(f"steps: {plan} step {n}: acceptance criterion reads this step's own verifier result, "
                                f'so it can pass only after the verifier passes: {text}\n'
                                '  move it to a later step, or declare it held with a trailing '
                                '[stage: ..., owner: ...] clause')
    if base is None:
        folder = pathlib.Path(plan).resolve().parent
        try:
            base = pathlib.Path(lane_tree(folder, tree) or folder)
        except Fail:
            base = folder
    return (findings + tests_findings(plan, steps) + order_findings(plan, steps, base) + defect_dependents(plan, steps)
            + clause_findings(plan, steps) + parity_findings(plan, steps))


def lint_or_fail(plan, steps, tree=None, tool='steps.py lint'):
    """Raise Fail with every lint finding and the plan defect last line. Under split (tool 'steps.py split') each
    finding is first recorded under ## Plan review in the task handoff (record_plan_review); steps.py lint records
    nothing, since the planner lints its own drafts. A clean plan writes nothing."""
    findings = lint_steps(plan, steps, tree)
    if findings:
        if tool == 'steps.py split':
            record_plan_review(pathlib.Path(plan).parent, plan, findings)
        raise Fail('\n'.join(findings + [PLAN_DEFECT]))


STEP_CAPS = {'L1': 3, 'L2': 3, 'L3': 6, 'L4': 10, 'L5': 15}  # T-0553: the most steps a plan may hold per ticket size
APPROVAL_RE = re.compile(r'[^:]*[^\s:][^:]*:\s*\S')  # "<who: why>": a name, a colon, a reason


def step_cap_approved(task_dir, plan):
    """True when the task folder's skips.md holds `step cap approved: <plan file name>: ...`."""
    f = pathlib.Path(task_dir) / 'skips.md'
    head = f'step cap approved: {os.path.basename(plan)}: '
    try:
        return any(x.startswith(head) for x in f.read_text(encoding='utf-8').splitlines())
    except OSError:
        return False


def step_cap_or_fail(plan, task_dir, steps, target, approved=None):
    """Raise Fail when the plan holds more steps than its ticket size allows (STEP_CAPS) and neither approved
    ("<who: why>", the person's call) nor a recorded approval for this plan file lets it through. An approved
    over-cap plan records `step cap approved: <plan file name>: <approved>` once in the task folder's skips.md.
    The last line is never a plan defect: a replan of an oversized ticket is the loop the cap stops."""
    import tickets  # here, not at the top, as lane_action does
    h = pathlib.Path(task_dir) / 'handoff.md'
    try:
        size = (tickets.parse(h.read_text(encoding='utf-8')) or {}).get('size')
    except OSError:
        return
    cap = STEP_CAPS.get(size)
    if cap is None or len(steps) <= cap or step_cap_approved(task_dir, plan):
        return
    if approved:
        with (pathlib.Path(task_dir) / 'skips.md').open('a', encoding='utf-8') as f:
            f.write(f'step cap approved: {os.path.basename(plan)}: {approved}\n')
        print(f'steps: step cap approved: {len(steps)} steps for size {size} (cap {cap}): {approved}', file=sys.stderr)
        return
    raise Fail(f'steps: {plan}: {len(steps)} steps exceed the step cap of {cap} for size {size}\n'
               f'step cap: split the ticket, or ask the person and rerun '
               f'steps.py lint {target} --approved "<who: why>"')


def next_superseded(d):
    """The next free step-<n>.superseded-<k> path beside step dir d (k from 1)."""
    ks = [int(m.group(2)) for c in d.parent.iterdir()
          if (m := SUPERSEDED_RE.match(c.name)) and f'step-{m.group(1)}' == d.name]
    return d.parent / f'{d.name}.superseded-{max(ks, default=0) + 1}'


def split(target, only=None, guard_timeout=None, override_review=None, tree=None, supersede=False):
    """Check everything, then write. Returns the paths written. With only, the chosen steps'
    runnable (guard) spans run before any write, each step under guard_timeout when given, else
    its own guard timeout line, else the plan's, else DEFAULT_GUARD_TIMEOUT. override_review (a reason)
    splits a plan whose newest review says replan, and records the override (record_review_override).
    supersede renames each chosen step dir that holds role output to step-<n>.superseded-<k>/ (next free k)
    after every check passes and before any write; without it such a step dir refuses."""
    plan, task_dir = find_plan(target)
    err = results.structure_error(plan, 'planner')
    if err is not None:
        raise Fail(f'invalid result: {plan}: {err}')
    after = [r for r in order.ordered(task_dir, 'plan-reviewer') if order.counts_after(r, plan)]
    if after:
        err = results.structure_error(after[-1], 'plan-reviewer')
        if err is not None:
            raise Fail(f'invalid result: {after[-1]}: {err}')
    rejected = rejected_by_review(plan, task_dir)
    override = None
    if rejected and override_review is not None and rejected[1] == 'replan':
        override = (os.path.basename(rejected[0]), override_review)
        rejected = None
    if rejected:
        r, v = rejected
        raise Fail(f'steps: {plan}: the newest plan review {os.path.basename(r)} says {v}; '
                   f'a rejected plan is never split\n'
                   f'plan defect: plan review: {v}; run steps.py review (/chain 3)')
    goal = read_goal(task_dir)
    steps = parse_steps(plan)
    step_cap_or_fail(plan, task_dir, steps, target)
    fix = criterion_amends(plan, after[-1], steps) if after else None
    applies = fix is not None and fix[2] is None
    amended = [a for a in fix[1] if not only or a[0] in only] if applies else []
    if applies:
        steps = fix[0]
    lint_or_fail(plan, steps, tree, 'steps.py split')
    folded = review_findings(after[-1])[0] if after and (review_verdict(after[-1]) == 'pass' or applies) else None
    if only:
        missing = sorted(set(n for n in only if n not in steps))
        if missing:
            raise Fail(f'steps: --only {", ".join(map(str, missing))} not in {plan} '
                       f'(steps: {", ".join(map(str, steps))})')
        chosen = [n for n in steps if n in set(only)]
    else:
        chosen = list(steps)
    rec = records_of(task_dir)
    held = []
    for n in chosen:
        d = rec / f'step-{n}'
        done = sorted(p.name for pat in ('builder-*.md', 'verifier-*.md') for p in d.glob(pat)) if d.is_dir() else []
        if done and supersede:
            held.append(d)
        elif done:
            raise Fail(f'steps: {d} already holds role output ({", ".join(done)}). Per /chain 4.2, rename it '
                       f'to step-{n}.superseded-<k>/ (next free k) first, or split again with --supersede. '
                       f'Nothing was written.')
    if only:
        plan_timeout = plan_guard_timeout(plan)
        timeouts = {n: guard_timeout if guard_timeout is not None
                    else step_guard_timeout(steps[n]) or plan_timeout or DEFAULT_GUARD_TIMEOUT
                    for n in chosen}
        run_guards(plan, steps, chosen, task_dir, timeouts, tree)
        run_red(plan, steps, chosen, task_dir, timeouts, tree)
    if override:
        record_review_override(task_dir, *override)
        print(f'steps: review override: {override[0]} says replan; split anyway: {override[1]}', file=sys.stderr)
    if amended:
        record_criterion_amends(task_dir, os.path.basename(after[-1]), amended)
    for d in held:
        dest = next_superseded(d)
        d.rename(dest)
        print(f'steps: superseded {d.name} -> {dest.name}', file=sys.stderr)
    written = []
    rec = records_of(task_dir, create=True)
    for n in chosen:
        d = rec / f'step-{n}'
        d.mkdir(parents=True, exist_ok=True)
        path = d / 'handoff.md'
        body = inherit_widened(f'## Task goal\n{goal}\n\n{steps[n]}\n', earlier_widened(rec, n))
        body, moved = rewrite_prior_links(body, sdlc_base(task_dir))
        for old_rel, new_rel in moved:
            print(f'steps: step {n}: rewrote prior-report link {old_rel} -> {new_rel}', file=sys.stderr)
        if folded and folded.get(n):
            body += '\n### Notes\n' + ''.join(f'- {x}\n' for x in folded[n])
        path.write_text(body, encoding='utf-8')
        written.append(path)
    return written


def earlier_widened(task_dir, n):
    """The paths listed under ## Scope widened in the live step-<m>/handoff.md files with m < n, in
    step order, no duplicates. A superseded or non-numeric step dir is not live."""
    found = []
    for m, d in sorted((m, p) for m, p in step_dirs(task_dir).items() if m < n):
        h = step_handoff(d)
        if not h.is_file():
            continue
        lines = h.read_text(encoding='utf-8').splitlines()
        start = next((i for i, x in enumerate(lines) if x.rstrip() == '## Scope widened'), None)
        if start is None:
            continue
        for x in lines[start + 1:]:
            if x.startswith('## '):
                break
            mm = re.match(r'^- `([^`]+)`', x)
            if mm and repo_path_ok(mm.group(1)) and mm.group(1) not in found:
                found.append(mm.group(1))
    return found


def inherit_widened(text, paths):
    """The step handoff text with paths added to its one scope allow-list and listed under
    ## Scope widened. Unchanged when there are no paths, the step has not exactly one scope span in a
    recognized form, or every path is already allowed. Runs no guard."""
    if not paths:
        return text
    lines = text.splitlines(keepends=True)
    scope = [(i, line, s) for i, line in criteria_indexed([x.rstrip('\r\n') for x in lines])
             if list_item(line) for s in line_spans(line) if is_scope_span(s)]
    if len(scope) != 1:
        return text
    idx, target, old = scope[0]
    forms = widen_forms(old)
    if len(forms) != 1:
        return text
    form, m = forms[0]
    listed = widen_listed(form, m)
    add = [p for p in paths if (p if form == 'F' else ere_escape(p)) not in listed]
    if not add:
        return text
    new_line = replace_span(target, old, widen_span(old, form, m, add))
    if new_line is None:
        return text
    ending = lines[idx][len(lines[idx].rstrip('\r\n')):]
    lines[idx] = new_line + ending
    return add_scope_widened(''.join(lines), add)


def cmd_precheck(task_dir):
    """Fail fast, before any planner or plan-reviewer runs, when split could not read the task goal."""
    try:
        read_goal(task_of(task_dir), allow_empty=True)
    except Fail as e:
        print(f'{e}; steps.py split reads the goal from the ## Goal section of the task handoff '
              f'(a "## Task goal" heading belongs to step handoffs only)', file=sys.stderr)
        return 1
    return 0


def cmd_split(target, only, guard_timeout=None, override_review=None, tree=None, supersede=False):
    try:
        written = split(target, only, guard_timeout, override_review, tree, supersede)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    for p in written:
        print(p)
    return 0


def criteria_count(block):
    """The number of top-level acceptance criteria of a step block: criteria_lines lines that start with
    '- ' or '* '. The one count lean_warnings and lane read."""
    return sum(1 for line in criteria_lines(block) if re.match(r'^[-*] ', line))


def lean_warnings(plan, task_dir, steps):
    """Coarse-step warning lines for a plan that meets the lean plan conditions, else []."""
    try:
        if result_level(plan) not in (1, 2):
            return []
    except Fail:
        return []
    unresolved, why = review_required(plan, task_dir)
    if unresolved or why or lean_only_reasons(plan, task_dir):
        return []
    rule = '(agents/planner.md, Coarse steps)'
    out = []
    if len(steps) > 2:
        out.append(f'steps lint: warning: {plan}: {len(steps)} steps; the coarse-step rule allows at most 2 '
                   f'in a plan that meets the lean plan conditions {rule}')
    for n, block in steps.items():
        if criteria_count(block) == 1:
            out.append(f'steps lint: warning: {plan} step {n}: one acceptance criterion; '
                       f'the coarse-step rule merges it into a neighboring step {rule}')
    return out


def step_handoff_of(target):
    """The handoff.md of target when it is a step folder (step-<n>/) or a handoff.md inside one, else None."""
    t = pathlib.Path(target)
    d = t.parent if t.name == 'handoff.md' else t
    if STEP_DIR_RE.match(os.path.basename(os.path.abspath(d))):  # either side: the twin holding the handoff
        t = step_handoff(d) if t.name == 'handoff.md' or not t.is_file() else t
    if t.is_dir() and STEP_DIR_RE.match(t.resolve().name):
        t = t / 'handoff.md'
    return t if t.is_file() and t.name == 'handoff.md' and STEP_DIR_RE.match(t.resolve().parent.name) else None


def cmd_lint(target, tree=None, approved=None):
    h = step_handoff_of(target)
    if h is not None:
        findings = link_findings(h)
        if findings:
            print('\n'.join(findings + [PLAN_DEFECT]), file=sys.stderr)
            return 1
        print('steps lint: ok')
        return 0
    try:
        plan, task_dir = find_plan(target)
        steps = parse_steps(plan)
        step_cap_or_fail(plan, task_dir, steps, target, approved)
        lint_or_fail(plan, steps, tree)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print('steps lint: ok')
    for w in count_warnings(plan, steps) + history_warnings(plan, steps) + abs_path_warnings(plan, steps) + lean_warnings(plan, task_dir, steps):
        print(w, file=sys.stderr)
    return 0


# --- held criteria (T-0408) ---------------------------------------------------
# A criterion has four states: pass, fail, `unmet-dependency <subject>` and `deferred <owner>`
# (docs/specs/sdlc-lite/verifier-held-criteria.md). The handoff declares which criteria may be held in a trailing
# bracket clause; the verifier may only hold a declared one, and held_items re-derives the claim from the handoff
# and the ticket state instead of trusting the report.

CLAUSE_RE = re.compile(r'\s\[([A-Za-z][\w-]*\s*:[^\[\]]*)\]\s*$')
CLAUSE_KEYS = ('stage', 'owner', 'needs')
WORD_RE = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*')
OWNER_RE = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*|T-\d{4}')
BULLET_RE = re.compile(r'^\s*[-*] ')
HELD_STATES = ('unmet-dependency', 'deferred')
HELD_NOTE_RE = re.compile(r'^(unmet-dependency|deferred):\s*(.*)$')
CLAUSE_HINT = ('use [stage: <word>; owner: <stage word or T-NNNN>; '
               'needs: <T-NNNN | file:<path> | cap:<name>, ...>] at the end of the line, outside any code span')


def parse_clause(line):
    """(meta, error) of a criterion line's trailing bracket clause. meta is {'stage': str, 'owner': str,
    'needs': [subject]} for the keys present, {} when the line has no clause; error is a reason string for a
    malformed clause (unknown or repeated key, empty value, bad owner or subject), else None. The clause is
    outside any code span; the subject grammar is tickets.dep_kind."""
    m = CLAUSE_RE.search(line)
    if not m or line[:m.start()].count('`') % 2:
        return {}, None
    meta = {}
    for part in m.group(1).split(';'):
        key, _, val = part.partition(':')
        key, val = key.strip(), val.strip()
        if key not in CLAUSE_KEYS:
            return {}, f'unknown key "{key}" (the keys are stage, owner, needs)'
        if not val:
            return {}, f'{key} has an empty value'
        if key in meta:
            return {}, f'{key} is given twice'
        if key == 'stage':
            if not WORD_RE.fullmatch(val):
                return {}, f'stage "{val}" is not a lowercase kebab word'
            meta[key] = val
        elif key == 'owner':
            if not OWNER_RE.fullmatch(val):
                return {}, f'owner "{val}" is not a lowercase kebab stage word or T-NNNN'
            meta[key] = val
        else:
            import tickets  # local: tickets.py owns the subject grammar and imports nothing from steps at load
            subjects = [x.strip() for x in val.split(',')]
            for x in subjects:
                if tickets.dep_kind(x) is None:
                    return {}, f'needs "{x}" is not T-NNNN, file:<path> or cap:<name>'
            meta[key] = subjects
    return meta, None


def criteria_meta(line):
    """{'stage', 'owner', 'needs'} of the keys a criterion line's bracket clause declares, else {}."""
    return parse_clause(line)[0]


def clause_findings(plan, steps):
    """One finding per criterion line of a plan step whose trailing bracket clause is malformed."""
    out = []
    for n, block in steps.items():
        for line in criteria_lines(block):
            err = parse_clause(line)[1] if BULLET_RE.match(line) else None
            if err:
                out.append(f'steps: {plan} step {n}: criterion has a bad bracket clause: {err}\n'
                           f'  {line.strip()}\n  {CLAUSE_HINT}')
    return out


def step_criterion_lines(d):
    """{k: line}: the k-th bullet line (1-based) under ### Acceptance criteria of <step dir>/handoff.md."""
    h = step_handoff(d)
    if not h.is_file():
        return {}
    items = [line for _, line in criteria_indexed(h.read_text(encoding='utf-8').splitlines()) if BULLET_RE.match(line)]
    return dict(enumerate(items, 1))


def ticket_criterion_lines(task):
    """{k: line}: the k-th bullet line (1-based) under ## Acceptance criteria of <task dir>/handoff.md, fenced
    lines left out."""
    h = pathlib.Path(task) / 'handoff.md'
    if not h.is_file():
        return {}
    items, inside, fenced = [], False, False
    for line in h.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            inside, fenced = line.rstrip() == '## Acceptance criteria', False
        elif inside and line.lstrip().startswith('```'):
            fenced = not fenced
        elif inside and not fenced and BULLET_RE.match(line):
            items.append(line)
    return dict(enumerate(items, 1))


def live_step_dirs(task):
    """[(name, path)] of the live step-<n>/ dirs of a task dir, by n (they live in its records dir)."""
    return [(c.name, c) for _, c in sorted(step_dirs(task).items())]


def declared_meta(task):
    """{ref: meta} for each criterion of the task dir whose bracket clause declares an owner or needs. A ref is
    step-<n>#<k> or ticket#<k>; the ordinal counts bullet lines only."""
    out = {}
    for name, d in live_step_dirs(task):
        for k, line in step_criterion_lines(d).items():
            meta = criteria_meta(line)
            if meta.get('owner') or meta.get('needs'):
                out[f'{name}#{k}'] = meta
    for k, line in ticket_criterion_lines(task).items():
        meta = criteria_meta(line)
        if meta.get('owner') or meta.get('needs'):
            out[f'ticket#{k}'] = meta
    return out


def ref_key(ref):
    scope, _, k = ref.partition('#')
    return (0, int(scope[5:]), int(k)) if scope.startswith('step-') else (1, 0, int(k))


def sdlc_root(task):
    """The .sdlc root that holds a task dir (roots.state_of its parent: the nearest ancestor named .sdlc, else the
    .sdlc whose config sets a work_root holding the task), else the task dir's parent."""
    t = pathlib.Path(task).resolve()
    return sdlc_roots.state_of(t.parent) or t.parent


def subject_met(subject, root):
    """True when an unmet-dependency subject is met now, by the tickets.py rules: T-NNNN is a done ticket, file:
    is an existing repo path, cap: is provided by a done ticket."""
    import tickets
    kind = tickets.dep_kind(subject)
    if kind == 'file':
        return (tickets.file_base(root) / subject[len('file:'):]).exists()
    try:
        ts = tickets.load(tickets.layout_paths(root).tickets)
    except tickets.Fail:
        return False
    if kind == 'id':
        return any(m.get('id') == subject and m.get('status') == 'done' for _, m in ts)
    if kind == 'cap':
        return subject[len('cap:'):] in {n for _, m in ts if m.get('status') == 'done' for n in tickets.provides_of(m)}
    return False


def hold_item(ref, state, who, meta, root):
    """One held criterion checked against its handoff declaration: {'ref', 'state', 'who', 'status', 'reason'}.
    status is 'held' (declared and still unmet or owned elsewhere), 'stale' (the declared subject is met now, so
    the report needs a re-check) or 'fail' (the handoff declares no such subject or owner: an undeclared hold is
    an ordinary fail)."""
    item = {'ref': ref, 'state': state, 'who': who, 'status': 'held', 'reason': ''}
    if state == 'deferred' and meta.get('owner') != who:
        item.update(status='fail', reason=f'undeclared hold ignored: {ref} (the handoff declares no owner {who})')
    elif state == 'unmet-dependency' and who not in meta.get('needs', []):
        item.update(status='fail', reason=f'undeclared hold ignored: {ref} (the handoff does not declare needs: {who})')
    elif state == 'unmet-dependency' and subject_met(who, root):
        item.update(status='stale', reason=f'stale: {who} is met now; re-check {ref}')
    return item


def result_ts(path):
    name = os.path.basename(str(path))
    for _, rec in order.records(os.path.dirname(str(path))):
        if rec.get('file') == name:
            return str(rec.get('ts') or '')
    return ''


def held_items(task, root=None):
    """The open held criteria of a task dir (a list, sorted by ref; [] when none): for each criterion that the
    handoff declares with owner: or needs:, the newest verifier result (task dir or live step dir) that names its
    ref decides. pass settles it and fail is an ordinary fail; unmet-dependency and deferred are listed through
    hold_item. A step-dir result's bare #k is that step's criterion, a task-dir result's bare #k is ticket#k, and
    a task-dir Verdict pass settles the refs under its ## Settles, and a deferred ref listed under the same result's
    ## Settled by owner by its declared owner is pass (T-0684). Newest is by the run record's ts, then step dir
    before task dir, then order.py; a result with no ts loses to a recorded one. Reads only."""
    task = task_of(task)
    declared = declared_meta(task)
    if not declared:
        return []
    root = pathlib.Path(root) if root is not None else sdlc_root(task)
    events = []
    for default, d, dir_rank in [(n, c, 0) for n, c in live_step_dirs(task)] + [('ticket', task, 1)]:
        for i, w in enumerate(order.ordered(d, 'verifier')):
            states = {}
            for c in results.criteria_states(w):
                if c['k'] is not None:
                    states[f"{c['scope'] or default}#{c['k']}"] = (c['state'], c['who'])
            if results.key_value(w, 'verifier') == 'pass':
                for scope, k in results.settled_refs(w):
                    states.setdefault(f'{scope}#{k}', ('pass', ''))
            for scope, k, owner in results.owner_settled(w):  # T-0684: the declared owner settled its deferred ref
                ref = f'{scope}#{k}'
                if states.get(ref) == ('deferred', owner) and declared.get(ref, {}).get('owner') == owner:
                    states[ref] = ('pass', '')
            events.append(((result_ts(w), dir_rank, i), states))
    latest = {}
    for _, states in sorted(events, key=lambda e: e[0]):
        latest.update(states)
    out = []
    for ref in sorted(declared, key=ref_key):
        got = latest.get(ref)
        if got and got[0] in HELD_STATES:
            out.append(hold_item(ref, got[0], got[1], declared[ref], root))
    return out


def open_items(task, root=None):
    """held_items under the name tickets.py close calls: the open held criteria of a task dir."""
    return held_items(task, root)


def next_note(path):
    """The first non-blank line under ## For the next attempt of a result, stripped, else ''."""
    body = section(path, 'For the next attempt') or []
    return next((line.strip() for line in body if line.strip()), '')


def held_note(path):
    """The subjects or owners a verifier result's first ## For the next attempt line holds (`deferred:
    integration` gives 'integration'), else ''. A display read; it does not check the handoff."""
    m = HELD_NOTE_RE.match(next_note(path))
    return m.group(2).strip() if m else ''


def owner_settled_hold(path):
    """True when the verifier result is a held-only fail (Verdict fail, first next-attempt line `deferred:`, no fail
    or unmet-dependency criterion, at least one deferred one) whose every deferred criterion is listed under its
    ## Settled by owner by that owner (dispatch.py settle-held, T-0684). A ## Criteria bullet line that
    results.criteria_states cannot parse makes it False: a real fail must not land behind a settled hold (T-0696).
    Reads the result alone, no handoff."""
    m = HELD_NOTE_RE.match(next_note(path))
    if results.key_value(path, 'verifier') != 'fail' or not m or m.group(1) != 'deferred':
        return False
    if any(re.match(r'\s*(?:[-*]|\d+\.)\s+\S', line) and not results.CRITERION_RE.match(line)
           for line in section(path, 'Criteria') or []):
        return False
    states = results.criteria_states(path)
    held = [c for c in states if c['state'] == 'deferred']
    settled = results.owner_settled(path)
    return (bool(held) and all(c['state'] in ('pass', 'deferred') for c in states)
            and all(c['k'] is not None and any(k == c['k'] and who == c['who'] and (c['scope'] in (None, scope))
                                               for scope, k, who in settled) for c in held))


def step_holds(d, v):
    """hold_item for each held Criteria line of the step dir's verifier result v, checked against the step
    handoff. A held line with no ref, or a ref of another dir, is an undeclared hold (status fail)."""
    d = pathlib.Path(d).resolve()
    declared = {}
    for k, line in step_criterion_lines(d).items():
        declared[f'{d.name}#{k}'] = criteria_meta(line)
    root = sdlc_root(d.parent)
    out = []
    for c in results.criteria_states(v):
        if c['state'] not in HELD_STATES:
            continue
        ref = f"{c['scope'] or d.name}#{c['k']}" if c['k'] is not None else '#<ref>'
        out.append(hold_item(ref, c['state'], c['who'], declared.get(ref, {}), root))
    return out


def is_verified_hold(d, w):
    """True when the verifier result w holds criteria and every hold checks out against the step handoff."""
    if not HELD_NOTE_RE.match(next_note(w)):
        return False
    items = step_holds(d, w)
    return bool(items) and all(i['status'] != 'fail' for i in items)


def cmd_open(task, explain=False):
    t = task_of(task)
    if not t.is_dir():
        print(f'steps open: no such directory: {t}', file=sys.stderr)
        return 1
    for i in held_items(t):
        line = f"{i['ref']}\t{i['state']}\t{i['who']}"
        print(line + (f"\t{i['reason']}" if explain and i['reason'] else ''))
    return 0


# --- next -------------------------------------------------------------------

HANDOFF_LEVEL_RE = re.compile(r'^level: L([1-5])\s*$')
RESULT_LEVEL_RE = re.compile(r'^[a-z][a-z-]*-L(\d+)')


def verifier_level(build_level):
    """Verifier level from build level: L1 or L2 -> L1, L3 -> L2, L4 or L5 -> L3."""
    return 1 if build_level <= 2 else 2 if build_level == 3 else 3


def result_level(path):
    m = RESULT_LEVEL_RE.match(os.path.basename(path))
    if not m:
        raise Fail(f'steps next: cannot read a level from the name {path}')
    return int(m.group(1))


def section(path, heading):
    """Lines under '## <heading>' up to the next ## line, or None when the heading is absent."""
    lines = pathlib.Path(path).read_text(encoding='utf-8').splitlines()
    for i, line in enumerate(lines):
        if line.rstrip() == f'## {heading}':
            body = []
            for rest in lines[i + 1:]:
                if rest.startswith('## '):
                    break
                body.append(rest)
            return body
    return None


def build_status(path):
    """'done' or 'blocked' from the builder's ## Status (results.py), else Fail."""
    s = build_status_or_none(path)
    if s not in ('done', 'blocked'):
        raise Fail(f'steps next: {path} has no builder status (done/blocked) under ## Status')
    return s


def verdict(path):
    """'pass' or 'fail' from the verifier's ## Verdict (results.py), else Fail."""
    v = verdict_or_none(path)
    if v not in ('pass', 'fail'):
        raise Fail(f'steps next: {path} has no verifier verdict (pass/fail) under ## Verdict')
    return v


def build_status_or_none(path):
    """'done', 'blocked', or 'inherited' (inherited red: <tests>) from the first non-blank line under
    ## Status, read by results.key_value against the builder schema, else None. Ignores the header;
    never raises."""
    return results.key_value(path, 'builder')


def verdict_or_none(path):
    """'pass', 'fail', or 'inherited' (inherited red: <tests>) from the first non-blank line under
    ## Verdict, read by results.key_value against the verifier schema, else None. Ignores the header;
    never raises."""
    return results.key_value(path, 'verifier')


def merge_class(verdict, stale_base, hits, held=''):
    """The merge class of one lane, the one rule `board.py --lanes` and `fanout.py roll` share (T-0374; defined in
    docs/references/sdlc-internals.md, fanout merge class): ('rolling', '') when the lane is independently verified
    (verdict 'pass'), its base is an ancestor of main (stale_base empty) and it touches no declared path (hits
    empty); else ('integration', reason) with the first failing reason in this order: 'hash-bound <path>',
    'stale base <sha7>', 'unverified' (no verdict) or 'verifier <verdict>'. A `fail` verdict whose lane only holds
    criteria (held: the subjects or owners of the result's `deferred:` or `unmet-dependency:` note, T-0408) reads
    'held <who>' in place of 'verifier fail', so a lane waiting on its owner is not read as a defective one."""
    if hits:
        return 'integration', f'hash-bound {sorted(hits)[0]}'
    if stale_base:
        return 'integration', f'stale base {str(stale_base)[:7]}'
    if verdict != 'pass':
        if held and verdict == 'fail':
            return 'integration', f'held {held}'
        return 'integration', f'verifier {verdict}' if verdict and verdict != 'none' else 'unverified'
    return 'rolling', ''


def declared_hits(cwd, globs, *diff, untracked=False):
    """The paths `git diff --name-only <diff...>` in cwd lists that match a declared hash-bound or generated glob
    (tickets.hash_bound_globs; each a git :(glob) pathspec from the repository root), plus, with untracked=True, the
    untracked files that match; sorted. [] when nothing is declared. Raises ValueError when git fails, so an
    unreadable diff never reads as rolling (T-0374)."""
    if not globs:
        return []
    import tickets
    env = {k: v for k, v in os.environ.items() if k not in tickets.GIT_ENV_DROP}
    specs = ['--', *(':(top,glob)' + g for g in globs)]
    cmds = [['diff', '--name-only', *diff, *specs]] + ([['ls-files', '--others', '--exclude-standard', *specs]] if untracked else [])
    out = set()
    for c in cmds:
        p = subprocess.run(['git', '--no-optional-locks', '-C', str(cwd), *c], env=env, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL)
        if p.returncode:
            raise ValueError(p.stderr.strip() or f'git {c[0]} rc={p.returncode}')
        out.update(x for x in p.stdout.splitlines() if x)
    return sorted(out)


def is_plan_defect(path):
    body = section(path, 'For the next attempt') or []
    first = next((line.strip() for line in body if line.strip()), '')
    return first.startswith('plan defect:')


def handoff_level(d):
    h = step_handoff(d)
    if not h.is_file():
        raise Fail(f'steps next: no builder result and no {h} to read a level from')
    for line in h.read_text(encoding='utf-8').splitlines():
        m = HANDOFF_LEVEL_RE.match(line)
        if m:
            return int(m.group(1))
    raise Fail(f'steps next: no builder result and {h} has no "level: L1".."level: L5" line')


BATCH_PATH_RE = re.compile(r'(?<![\w./-])step-\d+/builder-L\d+(?:-\d+)?\.md(?![\w.-])')


def batch_verified(step_dir):
    """Path of the task-dir verifier result that verified this step's newest build in a batch, else
    None. The only copy of the rule (board.py imports it). Reads only; never file times.
    None when: the dir name is not step-<n>; no newest builder, or its Status is not done; the build
    is L4 or L5; the handoff's step title starts with "Merge " or holds "gates green" (any case);
    the step is the highest-numbered live step-<n>/ of the task dir; a step-<n>.superseded-<k>/
    sibling exists. Otherwise the newest task-dir verifier result (order.py) whose ## Verified
    section lists step-<n>/<newest builder name> decides: its path when it is structurally valid
    with Verdict pass, else None."""
    d = pathlib.Path(step_dir)
    if not STEP_DIR_RE.fullmatch(d.name):
        d = d.resolve()
    m = STEP_DIR_RE.fullmatch(d.name)
    if not m:
        return None
    d = records_of(d)
    n, task_dir = int(m.group(1)), d.parent
    b = order.newest(d, 'builder')
    if b is None or build_status_or_none(b) != 'done' or result_level(b) >= 4:
        return None
    title = ''
    h = step_handoff(d)
    if h.is_file():
        for line in h.read_text(encoding='utf-8').splitlines():
            t = STEP_RE.match(line)
            if t:
                title = t.group(2).strip()
                break
    if title.startswith('Merge ') or 'gates green' in title.lower():
        return None
    live = [int(x.group(1)) for c in task_dir.iterdir()
            if c.is_dir() and (x := STEP_DIR_RE.fullmatch(c.name))]
    if n >= max(live, default=n):
        return None
    if any(c.is_dir() and re.fullmatch(rf'step-{n}\.superseded-\d+', c.name) for c in task_dir.iterdir()):
        return None
    want = f'step-{n}/{os.path.basename(b)}'
    for w in reversed(order.ordered(task_dir, 'verifier')):
        listed = {p for line in (section(w, 'Verified') or []) for p in BATCH_PATH_RE.findall(line)}
        if want not in listed:
            continue
        if (results.structure_error(w, 'verifier') is None and verdict_or_none(w) == 'pass'
                and all(c['state'] == 'pass' for c in results.criteria_states(w))):
            return w
        return None
    return None


def next_action(step_dir):
    """Return (action, level or None, reason, [result paths read]). Reads only; never file times.
    Ordering comes from order.py alone (ordered, newest, counts_after). A step dir on the task side reads its
    records-side twin (records_of)."""
    d = records_of(step_dir)
    if not d.is_dir():
        raise Fail(f'steps next: no such directory: {step_dir}')
    builders = order.ordered(d, 'builder')
    b = order.newest(d, 'builder')
    if b is None:
        n = handoff_level(d)
        return 'build', n, f'no builder result; handoff level L{n}', []
    err = results.structure_error(b, 'builder')
    if err is not None:
        return 'invalid result', None, f'{b}: {err}', [b]
    level = result_level(b)
    read = [b]
    if build_status_or_none(b) is None:
        runs = 0
        for x in reversed(builders):
            if build_status_or_none(x) is not None:
                break
            runs += 1
        name = os.path.basename(b)
        if runs <= 1:
            return ('rebuild', level,
                    f'{name} has no done/blocked under ## Status; not counted as a fail, rerun the builder at the same level',
                    read)
        return ('stop', None,
                f'{runs} consecutive builder results with no Status (newest {name}); ask the user', read)
    if build_status_or_none(b) == 'inherited':
        return ('inherited', None,
                f'{os.path.basename(b)} reports inherited red (gate already red at the pre-build HEAD); '
                'ask the conductor, not a fail, rebuild, bump, or replan', read)
    builders = [x for x in builders if build_status_or_none(x) in ('done', 'blocked')]
    if build_status(b) == 'blocked':
        notes = section(b, 'Notes') or []
        first = next((line.strip() for line in notes if line.strip()), '')
        if first.startswith('stale lane:'):
            n = re.sub(r'^step-(\d+)$', r'\1', d.name)
            return ('resplit', None,
                    f'newest builder {os.path.basename(b)} is blocked by a stale lane, not a plan defect ({first}); '
                    f'rebase the lane onto the merged prerequisites, move {d.name} to {d.name}.superseded-<k> '
                    f'(next free k), then steps.py split --only {n} <task dir>; never a replan', read)
        name = os.path.basename(b)
        pair = amend_pair(b) if first.startswith('plan defect:') else None
        if pair is not None and amend_applied(d, pair):
            return ('rebuild', level, f'{name} proposed a criterion amend that is applied; rebuild at L{level}', read)
        why = ''
        if pair is not None:
            if earlier_amend(d, b):
                why = ' (its amend is not offered: the step already had one)'
            elif step_built(d):
                why = ' (its amend is not offered: the step is already built; only the verifier\'s swap changes it)'
            elif used := replan_used(d):
                why = f' (its amend is not offered: the task already used its one replan: {used})'
            else:
                return ('amend', level,
                        f'{name} is blocked with a plan defect and proposes one criterion amend; '
                        f'apply it with steps.py amend, then rebuild at L{level}', read)
        elif any(section_lines_start(b, p, 'Notes') for p in ('amend old:', 'amend new:')):
            why = (' (its amend lines are not a plan defect: note with exactly one amend old: holding one code '
                   'span and one amend new:)')
        return 'replan', None, f'newest builder {name} is blocked (a blocked build replans){why}', read
    v = order.newest(d, 'verifier')
    if v is None or not order.counts_after(v, b):
        batch = batch_verified(d)
        if batch is not None:
            want = f'{d.resolve().name}/{os.path.basename(b)}'
            return ('done', None,
                    f'batch verifier {os.path.basename(batch)} lists {want} with Verdict pass', read + [batch])
        why ='no verifier result' if v is None else f'verifier {os.path.basename(v)} is older than the build'
        return ('verify', verifier_level(level),
                f'{why}; build L{level} -> verifier L{verifier_level(level)}', read)
    read.append(v)
    err = results.structure_error(v, 'verifier')
    if err is not None:
        return 'invalid result', None, f'{v}: {err}', read
    if verdict_or_none(v) is None:
        runs = 0
        for w in reversed(order.ordered(d, 'verifier')):
            if not order.counts_after(w, b):
                continue
            if verdict_or_none(w) is not None:
                break
            runs += 1
        name = os.path.basename(v)
        if runs <= 1:
            return ('reverify', result_level(v),
                    f'{name} has no verdict (pass/fail) under ## Verdict; rerun the verifier at the same level',
                    read)
        return ('stop', None,
                f'{runs} consecutive verifier results with no verdict at build L{level} (newest {name}); ask the user',
                read)
    if verdict_or_none(v) == 'inherited':
        return ('inherited', None,
                f'{os.path.basename(v)} reports inherited red (gate already red at the pre-build HEAD); '
                'ask the conductor, not a fail, rebuild, bump, or replan', read)
    if verdict(v) == 'pass':
        beside = next((c for c in results.criteria_states(v) if c['state'] in HELD_STATES), None)
        if beside is not None:
            ref = f"#{beside['scope'] + '#' if beside['scope'] else ''}{beside['k']}" if beside['k'] is not None else 'a criterion'
            return ('reverify', result_level(v),
                    f'{os.path.basename(v)} has Verdict pass but {ref} is {beside["state"]} {beside["who"]}; '
                    'read as fail, rerun the verifier at the same level', read)
        return 'done', None, f'newest verifier {os.path.basename(v)} passed', read
    ignored = ''
    if HELD_NOTE_RE.match(next_note(v)):
        name, items = d.resolve().name, step_holds(d, v)
        bad = [i for i in items if i['status'] == 'fail']
        if items and not bad:
            refs = ', '.join(i['ref'] for i in items)
            stale = [i for i in items if i['status'] == 'stale']
            if stale:
                return ('reverify', result_level(v),
                        f"{name}: subject now met; re-check {', '.join(i['ref'] for i in stale)}", read)
            unmet = sorted({i['who'] for i in items if i['state'] == 'unmet-dependency'})
            if unmet:
                return ('wait', None,
                        f"{name} waits on {', '.join(unmet)}; not a defect, no rebuild, bump or replan", read)
            owners = sorted({i['who'] for i in items})
            return ('deferred', None,
                    f"{name} built; {refs} owned by {', '.join(owners)}; the owner stage settles them", read)
        ignored = ('undeclared hold ignored: ' + ', '.join(i['ref'] for i in bad) if bad
                   else 'undeclared hold ignored: the note holds a criterion no Criteria line names') + '; '
    if is_plan_defect(v):
        name = os.path.basename(v)
        if swap_pair(v) is not None and not earlier_swap(d, v):
            return ('swap', level,
                    f'{name} failed with a plan defect and proposes one criterion swap; '
                    f'apply it with steps.py swap, then rebuild at L{level}', read)
        why = ''
        if swap_pair(v) is not None:
            why = ' (its swap is refused: the step already had one)'
        elif any(section_lines_start(v, p) for p in ('swap old:', 'swap new:')):
            why = ' (its swap lines are not exactly one swap old: with one code span and one swap new:)'
        return 'replan', None, f'newest verifier {name} failed with a plan defect{why}', read
    count = 0
    for w in order.ordered(d, 'verifier'):
        paired = [x for x in builders if order.counts_after(w, x)]
        if not paired or result_level(paired[-1]) != level:
            continue
        if w not in read:
            read.append(w)
        if verdict_or_none(w) == 'fail' and not is_plan_defect(w) and not is_verified_hold(d, w):
            count += 1
    if count <= 1:
        return 'rebuild', level, f'{ignored}first counted fail at build L{level}', read
    if level < 5:
        return 'bump', level + 1, f'{ignored}{count} counted fails at build L{level}', read
    return 'stop', None, f'{ignored}{count} counted fails at build L5; there is no L6, ask the user', read


INVALID_REASON = 'the newest result does not match its results.py schema; stop and ask the user'


def print_action(action, level, reason, read, rel_to=None):
    """The stdout of next, resume (after its step dir line), and review. An invalid result prints
    "invalid result: <path>: <why>", then the fixed reason line, then the read: lines."""
    if action == 'invalid result':
        print(f'invalid result: {reason}')
        print(f'reason: {INVALID_REASON}')
    else:
        print(action if level is None else f'{action} L{level}')
        print(f'reason: {repo_relative(reason, rel_to) if rel_to is not None else reason}')
    for p in read:
        print(f'read: {repo_relative(str(p), rel_to) if rel_to is not None else p}')


def cmd_next(step_dir):
    try:
        action, level, reason, read = next_action(step_dir)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print_action(action, level, reason, read)
    return 0


# --- resume -----------------------------------------------------------------

STEP_DIR_RE = re.compile(r'step-(\d+)')


def resume_action(task):
    """Return (step dir or None, action, level or None, reason, [result paths read]) for a task dir:
    the lowest-numbered step-<n>/ (by integer n; step-<n>.superseded-<k>/ left out) whose next_action
    is not done, wait or deferred, else the first wait or deferred step (a held step is never printed done),
    else (None, 'done', None, reason, []). Reads only; never file times."""
    t = pathlib.Path(task)
    if not t.is_dir():
        raise Fail(f'steps resume: no such directory: {t}')
    dirs = step_dirs(t)
    nums = sorted(dirs)
    if not nums:
        raise Fail(f'steps resume: {t} has no step-<n>/ dirs; run steps.py split {t} first')
    held = None
    for n in nums:
        d = dirs[n]
        try:
            action, level, reason, read = next_action(d)
        except Fail as e:
            msg = ' '.join(str(e).split('\n'))
            if msg.startswith('steps next: '):
                msg = msg[len('steps next: '):]
            raise Fail(f'steps resume: {d}: {msg}')
        if action in ('wait', 'deferred'):  # the held step's own build is complete: go on to the next one
            held = held or (d, action, level, reason, read)
        elif action != 'done':
            return d, action, level, reason, read
    if held is not None:
        d, action, level, reason, read = held
        return d, action, level, f'{reason}; every other step passed', read
    return None, 'done', None, 'every step-<n>/ passed', []


def cmd_resume(task):
    try:
        d, action, level, reason, read = resume_action(task)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    if d is not None:
        print(d)
    print_action(action, level, reason, read)
    return 0


# --- review -----------------------------------------------------------------

NOTES_FIX_RE = re.compile(r'^[-*] step (\d+): notes-fix: (\S.*)$')
CRITERION_ONLY_RE = re.compile(r'^[-*] step (\d+): criterion-only: old `([^`]+)` -> new (\S.*?)\. Evidence: \S')


def review_findings(path):
    """({step number: [one-line fix text]} of the `- step <n>: notes-fix: <text>` items under ## Findings of a
    plan-reviewer result (T-0364), [(step number, old span, new criterion text)] of its `- step <n>: criterion-only:
    old `<span>` -> new <text>. Evidence: <...>` items (T-0582), count of the other items). Read leniently; never
    raises."""
    try:
        lines = pathlib.Path(path).read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeDecodeError):
        return {}, [], 0
    notes, amends, other, inside = {}, [], 0, False
    for line in lines:
        if line.startswith('## '):
            inside = line.rstrip() == '## Findings'
            continue
        if not inside or not line.strip():
            continue
        m = NOTES_FIX_RE.match(line.strip())
        a = CRITERION_ONLY_RE.match(line.strip())
        if m:
            notes.setdefault(int(m.group(1)), []).append(' '.join(m.group(2).split()))
        elif a:
            old = a.group(2)[1:] if a.group(2).startswith(' ') else a.group(2)
            amends.append((int(a.group(1)), old[:-1] if old.endswith(' ') else old, a.group(3).strip()))
        else:
            other += 1
    return notes, amends, other


def review_notes(path):
    """The notes-fix items of a plan-reviewer result when every item under ## Findings is one, else None.
    A `- plan:` item, an unmarked step item, a criterion-only item, and a file with no items are not notes-level."""
    notes, amends, other = review_findings(path)
    return notes if notes and not amends and not other else None


def criterion_amends(plan, review, steps=None):
    """(steps, todo, why) for a plan-reviewer result whose findings are all criterion-only or notes-fix items, with
    at least one criterion-only item (T-0582), else None. steps is {n: block} of the plan (parse_steps, or the steps
    given) with each todo amend applied in place: the one criterion line of step n whose command spans hold the old
    span is replaced by the new text, after every text check an amend makes (check_new_text). todo lists the
    (n, old, new) amends applied; a pair whose new text step n already holds, with no line holding the old span,
    needs none. why is None when every pair applies, else the reason the review is a design replan (a step the plan
    lacks, no or several lines holding the old span, a new text that fails a check); steps and todo are then empty."""
    _, amends, other = review_findings(review)
    if not amends or other:
        return None

    def refuse(why, detail=()):
        raise Fail(why)

    plan = pathlib.Path(plan)
    try:
        out = dict(parse_steps(plan) if steps is None else steps)
        todo = []
        for n, old, new in amends:
            if n not in out:
                refuse(f'step {n} is not in {os.path.basename(plan)}')
            lines = out[n].split('\n')
            items, targets = criterion_targets(lines, ('### Acceptance criteria',), old)
            if not targets and new_applied(items, new):
                continue
            idx, target = one_target(targets, old, refuse)
            check_new_text(plan, target, new, refuse)
            indent, marker, _ = list_item(target)
            lines[idx] = f'{indent}{marker} {new}'
            out[n] = '\n'.join(lines)
            todo.append((n, old, new))
    except Fail as e:
        return {}, [], f'its criterion-only finding does not apply: {str(e).splitlines()[0]}'
    return out, todo, None


CRITERION_LOG_RE = re.compile(r'^[-*] criterion-only amend: (\S+): step \d+: ')


def criterion_log(review_name, n, old, new):
    """The ## Plan review line split writes for one applied criterion-only amend."""
    return f'- criterion-only amend: {review_name}: step {n}: old `{old}` -> new {new}'


def plan_review_lines(task_dir):
    """The stripped lines under ## Plan review in <task dir>/handoff.md. Read leniently: a missing handoff holds none."""
    found, inside = [], False
    try:
        lines = (pathlib.Path(task_dir) / 'handoff.md').read_text(encoding='utf-8').splitlines()
    except OSError:
        return found
    for line in lines:
        if line.startswith('## '):
            inside = line.rstrip() == '## Plan review'
        elif inside:
            found.append(line.strip())
    return found


def amended_reviews(task_dir):
    """Names of the plan-reviewer results whose criterion-only amends split logged under ## Plan review."""
    return {m.group(1) for line in plan_review_lines(task_dir) if (m := CRITERION_LOG_RE.match(line))}


def design_replan(path, amended):
    """True when a plan-reviewer result counts toward the replan cap: Verdict replan (review_verdict), unless every
    finding is criterion-only or notes-fix and split logged its amends (its name in amended). An unlogged
    criterion-only review counts: it did not apply, or it was never split."""
    if review_verdict(path) != 'replan':
        return False
    _, amends, other = review_findings(path)
    return not (amends and not other and os.path.basename(path) in amended)


def review_verdict(path):
    """'pass', 'replan', or 'blocked' from the first non-blank line under ## Verdict, read by
    results.key_value against the plan-reviewer schema, else None. Ignores the header; never raises.
    A `replan` whose findings are all Notes-level fixes (review_notes) reads as 'pass': the findings are
    folded into the step Notes by split, never a replan (T-0364). A real defect keeps `replan`."""
    v = results.key_value(path, 'plan-reviewer')
    if v == 'replan' and review_notes(path):
        return 'pass'
    return v


def plan_facts(plan):
    """(unresolved assumption items, step levels, step titles) of a plan, read leniently: a malformed
    plan is split's and lint's to refuse, never review's."""
    unresolved, levels, titles = [], [], []
    in_assume = in_step = False
    for line in pathlib.Path(plan).read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            in_assume = line.rstrip() == '## Assumptions'
            m = STEP_RE.match(line)
            in_step = bool(m)
            if m:
                titles.append(m.group(2).strip())
            continue
        if in_assume:
            m = re.match(r'^\s*[-*] (.*)$', line)
            if m and m.group(1).lstrip().startswith('unresolved:'):
                unresolved.append(m.group(1).strip())
        if in_step:
            m = HANDOFF_LEVEL_RE.match(line)
            if m:
                levels.append(int(m.group(1)))
    return unresolved, levels, titles


def review_required(plan, task_dir):
    """(unresolved assumption items, reasons a plan review is required) for plan in task_dir. The one
    rule that review, lane, and lint's lean warnings read. result_level's Fail propagates."""
    unresolved, levels, titles = plan_facts(plan)
    why = []
    if any(n in (4, 5) for n in levels):
        why.append('a step is at builder L4 or L5')
    return unresolved, why


REVIEW_OVERRIDE_RE = re.compile(r'^(?:[-*] )?review override: (\S+): (\S.*)$')


def review_overrides(task_dir):
    """{plan-reviewer result file name: reason} from the `review override: <file>: <reason>` lines under
    ## Plan review in <task dir>/handoff.md. Read leniently: a missing handoff holds none."""
    return {m.group(1): m.group(2) for line in plan_review_lines(task_dir) if (m := REVIEW_OVERRIDE_RE.match(line))}


def record_review_override(task_dir, review_name, reason):
    """Append `review override: <review file name>: <reason>` to ## Plan review in <task dir>/handoff.md
    (created when missing). An OSError is a Fail naming the path."""
    p = pathlib.Path(task_dir) / 'handoff.md'
    try:
        with open(p, encoding='utf-8', newline='') as f:
            old = f.read()
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(section_text(old, '## Plan review',
                                 repo_relative(f'review override: {review_name}: {reason}', task_dir), at_end=True))
    except OSError as e:
        raise Fail(f'steps split: cannot write {p}: {e}')


def record_criterion_amends(task_dir, review_name, amended):
    """Append one criterion_log line per applied criterion-only amend to ## Plan review in <task dir>/handoff.md
    (created when missing), skipping a line already there, and name each on stderr. An OSError is a Fail naming
    the path."""
    p = pathlib.Path(task_dir) / 'handoff.md'
    have = set(plan_review_lines(task_dir))
    try:
        with open(p, encoding='utf-8', newline='') as f:
            text = f.read()
        for n, old, new in amended:
            print(f'steps: step {n}: criterion-only amend: old `{old}` -> new {new}', file=sys.stderr)
            line = repo_relative(criterion_log(review_name, n, old, new), task_dir)
            if line not in have:
                text = section_text(text, '## Plan review', line, at_end=True)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
    except OSError as e:
        raise Fail(f'steps split: cannot write {p}: {e}')


def rejected_by_review(plan, task_dir):
    """(plan-reviewer result, verdict) when the newest plan-reviewer result that counts after plan
    says replan or blocked, else None. A replan review that a `review override:` line names is not
    a rejection; a blocked one never is overridden. A review whose criterion-only amends all apply
    (criterion_amends) is not a rejection, whatever its verdict; one whose amends do not apply is a replan."""
    after = [r for r in order.ordered(task_dir, 'plan-reviewer') if order.counts_after(r, plan)]
    if not after:
        return None
    v = review_verdict(after[-1])
    fix = criterion_amends(plan, after[-1]) if v in ('pass', 'replan') else None
    if fix is not None:
        v = 'pass' if fix[2] is None else 'replan'
    if v == 'replan' and os.path.basename(after[-1]) in review_overrides(task_dir):
        return None
    return (after[-1], v) if v in ('replan', 'blocked') else None


def review_action(task):
    """Return (action, level or None, reason, [result paths read]) for a task dir's newest plan:
    split, review L1, replan, or stop. Reads only; never file times. Ordering comes from order.py
    alone (ordered, newest, counts_after)."""
    t = task_of(task)
    if not t.is_dir():
        raise Fail(f'steps review: no such directory: {t}')
    plans = order.ordered(t, 'planner')
    if not plans:
        raise Fail(f'steps review: no planner-*.md in {t}; run the planner first (/chain 3)')
    plan = plans[-1]
    err = results.structure_error(plan, 'planner')
    if err is not None:
        return 'invalid result', None, f'{plan}: {err}', [plan]
    pname = os.path.basename(plan)
    read = [plan]
    unresolved, why = review_required(plan, t)
    if unresolved:
        return ('stop', None, f'{pname} lists an unresolved assumption: "{unresolved[0]}"; the user decides',
                read)
    if not why:
        return 'split', None, f'{pname} is a routine plan; no plan review is required', read
    need = '; '.join(why)
    reviews = order.ordered(t, 'plan-reviewer')
    after = [r for r in reviews if order.counts_after(r, plan)]
    if not after:
        return 'review', 1, f'a plan review is required ({need}) and none counts after {pname}', read
    r = after[-1]
    rname = os.path.basename(r)
    read.append(r)
    err = results.structure_error(r, 'plan-reviewer')
    if err is not None:
        return 'invalid result', None, f'{r}: {err}', read
    v = review_verdict(r)
    fix = criterion_amends(plan, r) if v in ('pass', 'replan') else None
    why_fix = ''
    if fix is not None and fix[2] is None:
        if not fix[1] or rname in amended_reviews(t):
            return ('split', None, f'the criterion-only amends of the newest plan review {rname} are applied; '
                    'split', read)
        return ('amend', None,
                f'every finding of the newest plan review {rname} is criterion-only (or notes-fix): run steps.py '
                f'split, which amends {len(fix[1])} criterion line(s) in the step handoffs in place and logs each '
                'under ## Plan review; the replan is not spent', read)
    if fix is not None:
        v, why_fix = 'replan', f' ({fix[2]})'
    if v == 'pass':
        return 'split', None, f'the newest plan review {rname} passed {pname}', read
    if v == 'replan':
        why_override = review_overrides(t).get(rname)
        if why_override:
            return 'split', None, f'the newest plan review {rname} says replan; overridden: {why_override}', read
        amended = amended_reviews(t)
        replans = [x for x in reviews if x == r or design_replan(x, amended)]
        if len(replans) >= 2:
            read += [x for x in replans if x not in read]
            return ('stop', None,
                    f'{len(replans)} plan reviews in {t} say replan (newest {rname}{why_fix}); '
                    'the second replan review asks the user', read)
        return 'replan', None, f'the newest plan review {rname} says replan{why_fix}; replan at planner L3', read
    if v == 'blocked':
        return ('stop', None,
                f'the newest plan review {rname} says blocked; ask the user its ## Missing decisions', read)
    runs = 0
    for x in reversed(after):
        if review_verdict(x) is not None:
            break
        runs += 1
        if x not in read:
            read.append(x)
    if runs <= 1:
        return ('review', 1,
                f'{rname} has no verdict (pass/replan/blocked) under ## Verdict; rerun the plan-reviewer, '
                'never a replan', read)
    return ('stop', None,
            f'{runs} consecutive plan reviews with no verdict after {pname} (newest {rname}); ask the user', read)


def red_at_base(plan, task_dir):
    """The runnable (red) spans of every step of plan that exit 0 at the base sha, as (n, span) in order (T-0657).
    They run once, through red_first, in a throwaway detached worktree at base_sha under the worktree root tmp prefix
    (wtroot.tmp_root), removed after, so the main and lane trees are never touched. No git, no base, no plan steps or
    no runnable span: an empty list and no worktree."""
    top = git_toplevel(task_dir)
    base = base_sha(top)
    if not base:
        return []
    try:
        steps = parse_steps(pathlib.Path(plan))
    except (Fail, OSError, UnicodeDecodeError):
        return []
    plan_timeout = plan_guard_timeout(pathlib.Path(plan))
    items = [(n, text, step_guard_timeout(steps[n]) or plan_timeout or DEFAULT_GUARD_TIMEOUT)
             for n in steps for text in red_spans(steps[n]) if not guard_skipped(text)]
    if not items:
        return []
    import wtroot  # local, as tickets is: a copy of steps.py beside only order.py and results.py has no wtroot.py
    tmp_root = wtroot.tmp_root(top) or pathlib.Path(tempfile.gettempdir())
    tmp_root.mkdir(parents=True, exist_ok=True)
    holder = pathlib.Path(tempfile.mkdtemp(prefix='review-red-', dir=tmp_root))
    tree = holder / 'tree'
    ran = []
    try:
        r = subprocess.run(['git', '-C', top, 'worktree', 'add', '-q', '--detach', str(tree), base],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=120)
        if r.returncode != 0:
            print(f'steps review: red-at-base skipped: git worktree add failed: {r.stderr.strip()}', file=sys.stderr)
            return []
        red_first(items, str(tree), str(tree), base, ran)
    finally:
        subprocess.run(['git', '-C', top, 'worktree', 'remove', '--force', str(tree)], capture_output=True,
                       stdin=subprocess.DEVNULL, timeout=120)
        shutil.rmtree(holder, ignore_errors=True)
        subprocess.run(['git', '-C', top, 'worktree', 'prune'], capture_output=True, stdin=subprocess.DEVNULL,
                       timeout=120)
    return [(n, span) for n, span, rc in ran if rc == 0]


def cmd_review(task):
    try:
        action, level, reason, read = review_action(task)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    defects = []
    if action in ('split', 'review'):
        plan = read[0]
        green = red_at_base(plan, task_of(task))
        defects = [f'plan defect: red-at-base: step {n}: `{span}`' for n, span in green]
        if defects:
            record_plan_review(task_of(task), plan, [f'steps: {plan} step {n}: red-at-base: `{span}` is green at '
                                                     'base; it cannot detect the change' for n, span in green])
            action, level = 'replan', None
            reason = (f'{len(defects)} (red) span(s) of {os.path.basename(plan)} already pass at the base commit '
                      '(red-at-base); replan at planner L3')
    print_action(action, level, reason, read, rel_to=task_of(task))
    for line in defects:
        print(line)
    return 0


# --- lane -------------------------------------------------------------------

LANE_MAX_STEPS = 2
LANE_MAX_CRITERIA = 12
LANE_MAX_TICKET_CRITERIA = 20
LANE_CONTRACTS = (
    'plugins/sdlc-lite/agents/',
    'plugins/sdlc-lite/skills/',
    'plugins/sdlc-lite/hooks/',
    'plugins/sdlc-lite/adapters/codex/',
    'plugins/sdlc-lite/scripts/run.sh',
    'plugins/sdlc-lite/scripts/run_lifecycle.py',
    'plugins/sdlc-lite/scripts/readiness.py',
    'plugins/sdlc-lite/scripts/codex_roles.py',
    'plugins/sdlc-lite/scripts/steps.py',
    'plugins/sdlc-lite/scripts/tickets.py',
    'plugins/sdlc-lite/scripts/results.py',
    'plugins/sdlc-lite/scripts/order.py',
    'plugins/sdlc-lite/scripts/check.py',
    'plugins/sdlc-lite/scripts/check.sh',
    'scripts/check-packaging.py',
)
LANE_STICKY = 'skips.md already records full, and a lane never returns from full'
LANE_NO_SIZE = 'handoff.md front matter has no size of L1 to L5'
LANE_SOLO_SIZES = ('L1', 'L2')  # the ticket levels the solo lane takes before planning, and lean after it
LANE_INNER_LOOP_SIZE = 'L3'  # T-0512: size the inner-loop profile also sends to solo before planning (no merge, no security word)
LANE_MERGE_TITLE_RE = re.compile(r'\bmerge\b', re.I)
ERE_PATTERN_CHARS = set('^$*+?()[]{}')


def is_lane_contract(p):
    """True when path p is in LANE_CONTRACTS: by prefix for an entry ending in /, else exactly."""
    return any(p.startswith(c) if c.endswith('/') else p == c for c in LANE_CONTRACTS)


def scope_entry(alt):
    """One E or A alternative as a path: backslash escapes removed, or the alternative kept raw when it
    is a pattern (a ^$*+?()[]{} left after deleting each backslash pair). An unescaped . is a dot."""
    if set(re.sub(r'\\.', '', alt)) & ERE_PATTERN_CHARS:
        return alt
    return re.sub(r'\\(.)', r'\1', alt)


def scope_entries(block):
    """Every allow-list entry of a step block's scope spans (list-item criterion lines, a span with
    git diff --name-only and a grep -v allow-list in a form widen recognizes), or None when there is
    no such span. F words come quotes stripped; E and A alternatives come through scope_entry."""
    spans = [s for line in criteria_lines(block) if list_item(line)
             for s in line_spans(line) if is_scope_span(s) and widen_forms(s)]
    if not spans:
        return None
    out = []
    for s in spans:
        for form, m in widen_forms(s):
            listed = widen_listed(form, m)
            out += listed if form == 'F' else [scope_entry(a) for a in listed]
    return out


def agents_owner(root, p):
    """The label of the nearest dir from (root/p).parent up to root holding AGENTS.md, relative to
    root in posix form ('.' for root); root when none holds one."""
    cur = (root / p).parent
    while True:
        if (cur / 'AGENTS.md').is_file():
            return cur.relative_to(root).as_posix()
        if cur == root or root not in cur.parents:
            return '.'
        cur = cur.parent


def lane_sticky(skips):
    """True when skips.md, inside a ## Lane section, has a line starting '- lane: full;'."""
    if not skips.is_file():
        return False
    inside = False
    for line in skips.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            inside = line.rstrip() == '## Lane'
        elif inside and line.startswith('- lane: full;'):
            return True
    return False


def ticket_criteria(text):
    """The number of checkbox lines ('- [ ]', '- [x]') under '## Acceptance criteria' of a handoff."""
    inside, n = False, 0
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.rstrip() == '## Acceptance criteria'
        elif inside and re.match(r'^\s*[-*] \[[ xX]\]', line):
            n += 1
    return n


def lean_only_reasons(plan, task_dir):
    """Reasons the lean lane refuses a plan that needs no plan review (T-0294 narrowed review to L4 and
    L5): a planner L3 plan, a Merge step, a replan, a ## Plan review line. Lean is a stricter lane."""
    _, _, titles = plan_facts(plan)
    why = []
    if result_level(plan) == 3:
        why.append(f'{os.path.basename(plan)} is a planner L3 plan')
    if any(x.startswith('Merge ') for x in titles):
        why.append('the plan has a merge step')
    n = len(order.ordered(task_dir, 'planner'))
    if n >= 2:
        why.append(f'{n} planner results (a replan)')
    h = pathlib.Path(task_dir) / 'handoff.md'
    if h.is_file() and any(x.rstrip() == '## Plan review' for x in h.read_text(encoding='utf-8').splitlines()):
        why.append('handoff.md holds ## Plan review')
    return why


def lane_action(task):
    """Return (lane, point, reasons, [files read]) for a task dir: solo, lean, or full. Writes nothing.
    The plan is read leniently, like plan_facts: split, lint, and review refuse a bad plan."""
    # Imported here, not at the top: results.py's selftest copies steps.py beside only order.py and
    # results.py and runs steps.py next, so a top-level import would fail there.
    import tickets
    t = task_of(task)
    if not t.is_dir():
        raise Fail(f'steps lane: no such directory: {t}')
    h, skips = t / 'handoff.md', t / 'skips.md'
    read = []
    size, review_line, ticket_k = None, False, 0
    if h.is_file():
        read.append(str(h))
        text = h.read_text(encoding='utf-8')
        size = (tickets.parse(text) or {}).get('size')
        review_line = any(line.rstrip() == '## Plan review' for line in text.splitlines())
        ticket_k = ticket_criteria(text)
    if size not in tickets.ENUMS['size']:
        size = None
    plan = order.newest(t, 'planner')
    if plan:
        read.append(plan)
    if skips.is_file():
        read.append(str(skips))
    point = ('before planning' if not plan else 'after plan review' if review_line else 'after planning')
    reasons = []
    if lane_sticky(skips):
        reasons.append(LANE_STICKY)
    if size is None:
        reasons.append(LANE_NO_SIZE)
    if not plan:
        if reasons:
            return 'full', point, reasons, read
        if size == LANE_INNER_LOOP_SIZE and tickets.inner_loop(sdlc_root(t), text):
            title = str((tickets.parse(text) or {}).get('title', ''))
            if LANE_MERGE_TITLE_RE.search(title):
                return 'full', point, ['size L3 stays full: the title names a merge'], read
            if VERIFIER_SECURITY_RE.search(text):
                return 'full', point, ['size L3 stays full: the handoff names security'], read
            return 'solo', point, ['size L3 goes to solo-L3 under profile: inner-loop '
                                   '(no merge in the title, no security word in the handoff; the one batched verifier stays)'], read
        if size in LANE_SOLO_SIZES and ticket_k > LANE_MAX_TICKET_CRITERIA:
            return 'full', point, [f'ticket lists {ticket_k} criteria (limit {LANE_MAX_TICKET_CRITERIA} for size L1 or L2); '
                                   f'split it into tickets of at most {LANE_MAX_TICKET_CRITERIA}'], read
        lane = 'solo' if size in LANE_SOLO_SIZES else 'full'
        return lane, point, [f'size {size} decides before planning (no planner result yet)'], read

    pname = os.path.basename(plan)
    if size not in LANE_SOLO_SIZES:
        reasons.append(f'size {size} is above L2, and lean takes only size L1 or L2')
    unresolved, why = review_required(plan, t)
    if unresolved:
        reasons.append(f'{pname} lists an unresolved assumption: "{unresolved[0]}"')
    reasons += why
    reasons += lean_only_reasons(plan, t)
    try:
        steps = parse_steps(pathlib.Path(plan))
    except Fail:
        reasons.append(f'{pname} has steps that do not parse (steps.py lint names why)')
        return 'full', point, reasons, read
    if len(steps) > LANE_MAX_STEPS:
        reasons.append(f'{len(steps)} steps, and lean allows at most {LANE_MAX_STEPS}')
    for n, block in steps.items():
        k = criteria_count(block)
        if k > LANE_MAX_CRITERIA:
            reasons.append(f'step {n} has {k} acceptance criteria, and lean allows at most {LANE_MAX_CRITERIA}')
    entries = {n: scope_entries(block) for n, block in steps.items()}
    for n, got in entries.items():
        if got is None:
            reasons.append(f'step {n} has no scope allow-list in a form steps.py widen recognizes, '
                           'so its files are unknown')
    for n, got in entries.items():
        for e in dict.fromkeys(got or []):
            if not repo_path_ok(e):
                reasons.append(f'step {n} scope entry is not a repo-relative path: {e}')
    paths = {n: [e for e in dict.fromkeys(got or []) if repo_path_ok(e)] for n, got in entries.items()}
    for n, got in paths.items():
        for p in got:
            if is_lane_contract(p):
                reasons.append(f'step {n} scope names a contract other roles parse: {p}')
    root = pathlib.Path(guard_cwd(t))
    owners = sorted({agents_owner(root, p) for got in paths.values() for p in got})
    if len(owners) > 1:
        reasons.append(f'scoped files span {len(owners)} AGENTS.md owners: {", ".join(owners)}')
    if reasons:
        return 'full', point, reasons, read
    level = result_level(plan)
    owner = owners[0] if owners else '.'
    return ('lean', point, [f'every lean condition holds: size {size}, planner L{level}, {len(steps)} steps '
                            f'at L1 to L3, one AGENTS.md owner ({owner})'], read)


def lane_record(lane, point, reasons):
    """The one skips.md line a lane call appends."""
    return f'- lane: {lane}; point: {point}; reasons: {"; ".join(reasons)}'


def lane_text(old, record):
    """skips.md text with record appended to its ## Lane section: after that section's last non-blank
    line; else a new ## Lane section before the first ## line, or at the end. old None is a missing
    file. Every other line is kept byte for byte."""
    if old is None:
        return f'# Skips\n\n## Lane\n{record}\n'
    return section_text(old, '## Lane', record)


def section_text(old, heading, record, at_end=False):
    """old with record appended to its heading section: after that section's last non-blank line; else
    a new section before the first ## line, or at the end (always at the end with at_end, for a file
    whose ## sections come first). Every other line is kept byte for byte."""
    lines = old.splitlines(keepends=True)
    if lines and not lines[-1].endswith(('\n', '\r')):
        lines[-1] += '\n'
    bare = [x.rstrip('\r\n') for x in lines]
    start = next((i for i, x in enumerate(bare) if x.rstrip() == heading), None)
    if start is not None:
        end = next((j for j in range(start + 1, len(bare)) if bare[j].startswith('## ')), len(bare))
        last = end
        while last > start + 1 and not bare[last - 1].strip():
            last -= 1
        return ''.join(lines[:last] + [record + '\n'] + lines[last:])
    first = next((i for i, x in enumerate(bare) if x.startswith('## ')), None)
    if first is None or at_end:
        sep = '' if not bare or not bare[-1].strip() else '\n'
        return ''.join(lines) + f'{sep}{heading}\n{record}\n'
    return ''.join(lines[:first] + [heading + '\n', record + '\n', '\n'] + lines[first:])


def solo_skips_text(text, size=None):
    """skips.md text with the planner and filer a solo lane skips recorded under ## Skipped, in the form the
    tickets.py skips guard counts (`- skip: <role>; step: all; reason: ...; decided: lane`), or None when
    nothing is to be added: the last `- lane:` line is not solo, or both entries already exist (idempotent).
    Every other line is kept byte for byte."""
    lanes = re.findall(r'(?m)^- lane: ([^;\r\n]*)', text)
    if not lanes or lanes[-1].strip() != 'solo':
        return None
    why = f'solo lane: size {size} runs end to end in one session' if size else 'solo lane: runs end to end in one session'
    nl = '\r\n' if '\r\n' in text else '\n'
    add = ''.join(f'- skip: {role}; step: all; reason: {why}; decided: lane{nl}' for role in ('planner', 'filer')
                  if not re.search(rf'(?m)^- skip: {role};', text))
    if not add:
        return None
    if re.search(r'(?m)^## Skipped[ \t]*\r?$', text):
        return re.sub(r'(?m)^(## Skipped[ \t]*\r?\n)', lambda m: m.group(1) + add, text, count=1)
    if text and not text.endswith(('\n', '\r')):
        text += nl
    return text + nl + '## Skipped' + nl + add


def write_solo_skips(task, size=None):
    """Record a solo lane's skipped planner and filer in <task>/skips.md (solo_skips_text). Returns True when
    it wrote. The one writer for every caller: record_lane runs it after a solo lane record, and fanout.py calls
    it too. SDLC_SELFTEST_NO_SKIPPED=1 turns it off (a selftest's negative control). An OSError is a Fail."""
    if os.environ.get('SDLC_SELFTEST_NO_SKIPPED') == '1':
        return False
    p = pathlib.Path(task) / 'skips.md'
    try:
        if not p.is_file():
            return False
        with open(p, encoding='utf-8', newline='') as f:
            old = f.read()
        new = solo_skips_text(old, size)
        if new is None:
            return False
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(new)
        return True
    except OSError as e:
        raise Fail(f'steps lane: cannot write {p}: {e}')


def record_lane(task, lane, point, reasons):
    """Append the lane record to <task>/skips.md; for lane solo also the planner and filer ## Skipped
    entries (write_solo_skips), so any caller can close the ticket by reason. An OSError is a Fail naming the path."""
    p = pathlib.Path(task) / 'skips.md'
    try:
        old = None
        if p.is_file():
            with open(p, encoding='utf-8', newline='') as f:
                old = f.read()
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(lane_text(old, lane_record(lane, point, reasons)))
    except OSError as e:
        raise Fail(f'steps lane: cannot write {p}: {e}')
    if lane == 'solo':
        write_solo_skips(task)


def cmd_lane(task, check=False):
    try:
        lane, point, reasons, read = lane_action(task)
        if not check:
            record_lane(task_of(task), lane, point, reasons)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print(lane)
    for r in reasons:
        print(f'reason: {r}')
    for p in read:
        print(f'read: {p}')
    return 0


# --- verifier level of a ticket (T-0356) -------------------------------------

VERIFIER_FABLE_SIZES = ('L4', 'L5')
VERIFIER_MARK_RE = re.compile(r'^verifier: L3\s*$', re.M)
VERIFIER_MERGE_RE = re.compile(r'^Merge\b')
VERIFIER_SECURITY_RE = re.compile(r'\bsecurity\b', re.I)
# A criterion that pins an exact label or string says so in words; one that does not carries the mark line.
VERIFIER_PIN_RE = re.compile(r'\bverbatim\b|\b(?:exact|exactly|literal)\s+(?:label|string|text|wording|name)s?\b|\blabels?\b', re.I)


def ticket_verifier(text):
    """(level, reason) of the one batched verifier of a solo ticket, from its handoff text. L3 (Fable) only for a
    ticket of size L4 or L5, a Merge ticket, a security ticket, a ticket whose acceptance criteria pin an exact
    label or string (the words verbatim, exact label, literal string, or label), or one with a `verifier: L3`
    line; every other ticket, any L1 or L2 ticket included, gets L2 (Sonnet high). The replay in
    docs/reports/2026-10-07-verifier-l2-replay.md found L2 missed a literal label match and nothing else."""
    import tickets
    meta = tickets.parse(text) or {}
    size, title = str(meta.get('size', '')), str(meta.get('title', ''))
    goal, criteria, inside = [], [], None
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.rstrip()[3:]
        elif inside == 'Goal':
            goal.append(line)
        elif inside == 'Acceptance criteria' and re.match(r'^\s*[-*] \[[ xX]\]', line):
            criteria.append(line)
    if size in VERIFIER_FABLE_SIZES:
        return 'L3', f'size {size}'
    if VERIFIER_MERGE_RE.match(title):
        return 'L3', 'a merge ticket'
    if VERIFIER_SECURITY_RE.search(title) or VERIFIER_SECURITY_RE.search(' '.join(goal)):
        return 'L3', 'a security ticket'
    if VERIFIER_MARK_RE.search(text):
        return 'L3', 'the handoff carries a verifier: L3 line'
    if any(VERIFIER_PIN_RE.search(c) for c in criteria):
        return 'L3', 'a criterion pins an exact label or string'
    return 'L2', f'size {size or "unset"}: no L4 or L5 size, merge, security, or exact label or string criterion'


def cmd_verifier_level(task):
    h = task_of(task) / 'handoff.md'
    if not h.is_file():
        print(f'steps verifier-level: no handoff.md in {task}', file=sys.stderr)
        return 1
    level, reason = ticket_verifier(h.read_text(encoding='utf-8'))
    print(level)
    print(f'reason: {reason}')
    print(f'read: {h}')
    return 0


# --- swap -------------------------------------------------------------------

SWAP_DEFECT = '; replan this step (/chain 4.2)'


def section_lines_start(path, prefix, heading='For the next attempt'):
    """The stripped lines under ## <heading> (default For the next attempt) that start with prefix."""
    try:
        body = section(path, heading) or []
    except Exception:
        return []
    return [line.strip() for line in body if line.strip().startswith(prefix)]


def section_pair(path, heading, prefix):
    """(old span, new text) from a result's ## <heading>, or None. A pair is exactly one line starting
    '<prefix> old:' holding exactly one code span (stripped of one edge space, like line_spans) and exactly
    one line starting '<prefix> new:' with a non-empty value."""
    po, pn = f'{prefix} old:', f'{prefix} new:'
    olds = section_lines_start(path, po, heading)
    news = section_lines_start(path, pn, heading)
    if len(olds) != 1 or len(news) != 1:
        return None
    spans = []
    for m in SPAN_RE.finditer(olds[0][len(po):]):
        text = m.group(2)
        if text.startswith(' '):
            text = text[1:]
        if text.endswith(' '):
            text = text[:-1]
        spans.append(text)
    new = news[0][len(pn):].strip()
    if len(spans) != 1 or not spans[0].strip() or not new:
        return None
    return spans[0], new


def swap_pair(path):
    """(old span, new text) from a verifier result's ## For the next attempt 'swap old:'/'swap new:' lines,
    or None (section_pair)."""
    return section_pair(path, 'For the next attempt', 'swap')


def earlier_swap(d, v):
    """True when a verifier result in d other than v proposes a swap: one swap per step."""
    return any(w != v and swap_pair(w) is not None for w in order.ordered(d, 'verifier'))


def list_item(line):
    """(indent, marker, text after the marker) for a '-' or '*' list item line, else None."""
    m = re.match(r'^(\s*)([-*]) (.*)$', line)
    return (m.group(1), m.group(2), m.group(3)) if m else None


def criterion_targets(lines, heads, old):
    """(items, targets) of a handoff's lines (keepends): items are the (index, line) list items of the criteria
    region under heads, targets the items holding old among their command spans."""
    items = [(i, line) for i, line in criteria_indexed([x.rstrip('\r\n') for x in lines], heads)
             if list_item(line)]
    return items, [(i, line) for i, line in items if old in line_spans(line)]


def new_applied(items, new):
    """True when one criterion item's text after its marker equals new: the swap or amend is already applied."""
    return any(list_item(line)[2].strip() == new for _, line in items)


def one_target(targets, old, refuse):
    """The one (index, line) target, else refuse: no line or several lines hold the old span."""
    if not targets:
        refuse(f'no criterion line holds the old span: {old}')
    if len(targets) > 1:
        refuse(f'{len(targets)} criterion lines hold the old span: {old}')
    return targets[0]


def check_new_text(h, target, new, refuse):
    """The new criterion's command spans after every text check a swap or amend makes, else refuse: it keeps the
    target's (guard) tag, (red) tag and bracket clause, holds a command span, has no HEAD^1 or <placeholder> span,
    and lints clean (lint_steps against handoff h)."""
    if new.startswith('(guard)') != is_guard_line(target):
        refuse('the new text must start with (guard) exactly when the old criterion line does: '
               f'old {"is" if is_guard_line(target) else "is not"} a (guard) line')
    if is_red_line(new) != is_red_line(target):
        refuse('the new text must carry (red) in its leading tags exactly when the old criterion line does: '
               f'old {"is" if is_red_line(target) else "is not"} a (red) line')
    if parse_clause(target)[0] != parse_clause(f'- {new}')[0]:
        refuse('the new text must keep the old criterion line\'s bracket clause unchanged: '
               f'old {target.strip()}')
    spans = line_spans(f'- {new}')
    if not spans:
        refuse(f'the new criterion holds no runnable command span: {new}')
    skipped = [s for s in spans if guard_skipped(s)]
    if skipped:
        refuse(f'a new span references HEAD^1 or holds a <placeholder>, so it cannot run now: {skipped[0]}')
    findings = lint_steps(h, {1: f'## Step 1: swap\nlevel: L1\n### Acceptance criteria\n- {new}'})
    if findings:
        refuse(f'the new criterion does not lint: {new}', findings)
    return spans


def swap(step_dir, timeout=300):
    """Apply the newest verifier's criterion swap to <step dir>/handoff.md after every check passes.
    Returns the one stdout line. Raises Fail (last line 'plan defect: ...; replan this step (/chain 4.2)')
    and writes nothing on any refusal. A task-side step dir means its records-side twin (records_of)."""
    d = records_of(step_dir)

    def refuse(why, detail=()):
        raise Fail('\n'.join(list(detail) + [f'plan defect: steps swap refused: {why}{SWAP_DEFECT}']))

    if not d.is_dir():
        refuse(f'no such directory: {d}')
    h = step_handoff(d)
    if not h.is_file():
        refuse(f'no step handoff at {h}')
    b = order.newest(d, 'builder')
    solo = b is None and order.newest(d, 'solo') is not None
    if solo:
        b = order.newest(d, 'solo')
    v = order.newest(d, 'verifier')
    if b is None or v is None:
        refuse('the step dir needs a builder (or, in a solo task dir, a solo) result and a verifier result')
    vname = os.path.basename(v)
    if not order.counts_after(v, b):
        refuse(f'verifier {vname} is older than the newest build {os.path.basename(b)}')
    if verdict_or_none(v) != 'fail':
        refuse(f'newest verifier {vname} has no fail verdict')
    if not is_plan_defect(v):
        refuse(f'newest verifier {vname} does not start ## For the next attempt with "plan defect:"')
    pair = swap_pair(v)
    if pair is None:
        refuse(f'newest verifier {vname} has no single swap old: (one code span) and swap new: pair')
    if earlier_swap(d, v):
        refuse(f'another verifier result in {d} already proposed a swap; one swap per step')
    old, new = pair

    text = h.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)
    heads = ('### Acceptance criteria', '## Acceptance criteria') if solo else ('### Acceptance criteria',)
    items, targets = criterion_targets(lines, heads, old)
    if not targets and new_applied(items, new):
        return 'swap: already applied'
    idx, target = one_target(targets, old, refuse)
    spans = check_new_text(h, target, new, refuse)

    top = git_toplevel(d)
    cwd = top or str(d)
    base = base_sha(exec_toplevel(d), d)
    before = tree_state(top) if top else None
    detail, red = [], []
    for s in spans:
        rc, tail = run_guard(s, cwd, timeout, base)
        if rc == 0:
            continue
        why = f'timed out after {timeout:g}s' if rc is None else f'exit {rc}'
        detail.append(f'steps swap: {d}: new criterion span is red now ({why}): {s}')
        detail += [f'  {t}' for t in tail]
        red.append(f'red now: {s}')
    after = tree_state(top) if before is not None else None
    changed = tree_changes(before, after) if after is not None else []
    if changed:
        detail += [f'steps swap: {d}: new criterion span changed the work tree: {p}' for p in changed]
        red.append(f'the new criterion changed the work tree: {", ".join(changed)}')
    if red:
        refuse('; '.join(red), detail)

    indent, marker, _ = list_item(target)
    ending = lines[idx][len(lines[idx].rstrip('\r\n')):]
    lines[idx] = f'{indent}{marker} {new}{ending}'
    h.write_text(''.join(lines), encoding='utf-8')
    return f'steps swap: {d}: old `{old}` -> new {new}'


def cmd_swap(step_dir, timeout=300):
    try:
        line = swap(step_dir, timeout)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print(line)
    return 0


# --- amend ------------------------------------------------------------------
# A builder blocked by one defective criterion of an unbuilt step proposes one amend in its ## Notes (under the
# "plan defect:" line); steps.py amend applies it after the swap checks. It is the task's one replan: the script
# records "amend applied:" under ## Plan review in the task handoff, so the cap never depends on the conductor.

AMEND_STEP_RE = re.compile(r'^step-(\d+)$')


def amend_pair(path):
    """(old span, new text) from a builder result's ## Notes 'amend old:'/'amend new:' lines, or None
    (section_pair)."""
    return section_pair(path, 'Notes', 'amend')


def earlier_amend(d, b):
    """True when a builder result in d other than b proposes an amend: one amend per step."""
    return any(x != b and amend_pair(x) is not None for x in order.ordered(d, 'builder'))


def notes_first(path):
    """The first non-blank stripped line under ## Notes, else ''."""
    return next((line.strip() for line in (section(path, 'Notes') or []) if line.strip()), '')


def step_built(d):
    """True when the step is already built: a builder result in d with Status done, or any verifier result."""
    return (any(build_status_or_none(x) == 'done' for x in order.ordered(d, 'builder'))
            or bool(order.ordered(d, 'verifier')))


def replan_used(d):
    """Why the task of step dir d already used its one replan, else None: its records dir holds two or more
    planner-*.md results (order.ordered, as lean_only_reasons counts them), or the task handoff's ## Plan review
    holds an "amend applied:" line."""
    task = task_of(d)
    n = len(order.ordered(records_of(task), 'planner'))
    if n >= 2:
        return f'{n} planner results (a replan)'
    h = task / 'handoff.md'
    if h.is_file():
        inside = False
        for line in h.read_text(encoding='utf-8').splitlines():
            if line.startswith('## '):
                inside = line.rstrip() == '## Plan review'
            elif inside and 'amend applied:' in line:
                return f'the task handoff ## Plan review holds an amend: {line.strip()}'
    return None


def amend_applied(d, pair):
    """True when the step handoff no longer holds the old span in a criterion line and one criterion line's
    text equals the new text."""
    h = step_handoff(d)
    if not h.is_file():
        return False
    items, targets = criterion_targets(h.read_text(encoding='utf-8').splitlines(keepends=True),
                                       ('### Acceptance criteria',), pair[0])
    return not targets and new_applied(items, pair[1])


def amend(step_dir, timeout=300):
    """Apply the newest blocked builder's one criterion amend to <step dir>/handoff.md after every check passes,
    and record it under ## Plan review in the task handoff. Returns the one stdout line. Raises Fail (last line
    'plan defect: steps amend refused: ...; replan this step (/chain 4.2)') and writes nothing on any refusal.
    Unlike swap, the build is partial: only a (guard) line's spans run (exit 0, work tree unchanged), and a (red)
    line's spans must each exit nonzero now; a plain criterion is not run."""
    d = records_of(step_dir)

    def refuse(why, detail=()):
        raise Fail('\n'.join(list(detail) + [f'plan defect: steps amend refused: {why}{SWAP_DEFECT}']))

    if not d.is_dir():
        refuse(f'no such directory: {d}')
    h = step_handoff(d)
    if not h.is_file():
        refuse(f'no step handoff at {h}')
    m = AMEND_STEP_RE.match(d.name)
    if not m:
        refuse(f'{d} is not a step-<n> dir of a task')
    b = order.newest(d, 'builder')
    if b is None:
        refuse('the step dir holds no builder result')
    bname = os.path.basename(b)
    if build_status_or_none(b) != 'blocked':
        refuse(f'newest builder {bname} is not blocked')
    if not notes_first(b).startswith('plan defect:'):
        refuse(f'newest builder {bname} does not start ## Notes with "plan defect:"')
    pair = amend_pair(b)
    if pair is None:
        refuse(f'newest builder {bname} has no single amend old: (one code span) and amend new: pair')
    old, new = pair
    lines = h.read_text(encoding='utf-8').splitlines(keepends=True)
    items, targets = criterion_targets(lines, ('### Acceptance criteria',), old)
    if not targets and new_applied(items, new):
        return 'amend: already applied'
    if step_built(d):
        refuse('the step is already built (a builder result with Status done, or a verifier result); '
               'a built step\'s criterion changes only through the verifier\'s steps.py swap')
    if earlier_amend(d, b):
        refuse(f'another builder result in {d} already proposed an amend; one amend per step')
    used = replan_used(d)
    if used:
        refuse(f'the task already used its one replan: {used}')
    idx, target = one_target(targets, old, refuse)
    spans = check_new_text(h, target, new, refuse)

    guard, red_line = is_guard_line(target), is_red_line(target)
    if guard or red_line:
        top = git_toplevel(d)
        cwd = top or str(d)
        base = base_sha(exec_toplevel(d), d)
        before = tree_state(top) if top and guard else None
        detail, bad = [], []
        for s in spans:
            rc, tail = run_guard(s, cwd, timeout, base)
            if guard and rc != 0:
                why = f'timed out after {timeout:g}s' if rc is None else f'exit {rc}'
                detail.append(f'steps amend: {d}: new (guard) span is red now ({why}): {s}')
                detail += [f'  {t}' for t in tail]
                bad.append(f'(guard) red now: {s}')
            elif red_line and not guard and (rc is None or rc == 0):
                why = f'timed out after {timeout:g}s' if rc is None else 'exit 0'
                detail.append(f'steps amend: {d}: new (red) span is not red before the build ({why}): {s}')
                bad.append(f'(red) green now: {s}')
        after = tree_state(top) if before is not None else None
        changed = tree_changes(before, after) if after is not None else []
        if changed:
            detail += [f'steps amend: {d}: new criterion span changed the work tree: {p}' for p in changed]
            bad.append(f'the new criterion changed the work tree: {", ".join(changed)}')
        if bad:
            refuse('; '.join(bad), detail)

    indent, marker, _ = list_item(target)
    ending = lines[idx][len(lines[idx].rstrip('\r\n')):]
    lines[idx] = f'{indent}{marker} {new}{ending}'
    task_h = task_of(d) / 'handoff.md'
    record = repo_relative(f'- amend applied: step {m.group(1)}: old `{old}` -> new {new}', d)
    old_task = task_h.read_text(encoding='utf-8') if task_h.is_file() else ''
    h.write_text(''.join(lines), encoding='utf-8')
    task_h.write_text(section_text(old_task, '## Plan review', record, at_end=True), encoding='utf-8')
    return f'steps amend: {d}: old `{old}` -> new {new}'


def cmd_amend(step_dir, timeout=300):
    try:
        line = amend(step_dir, timeout)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print(line)
    return 0


# --- widen ------------------------------------------------------------------

WIDEN_PATH_RE = re.compile(r'^[A-Za-z0-9._/@+-]+$')
ERE_SPECIAL = set('.^$*+?()[]{}|\\')
INVERT_GREP_RE = re.compile(r'(?<![\w-])grep(?:\s+-[A-Za-z]+)*\s+(?:-[A-Za-z]*v|--invert-match(?![\w-]))')
WIDEN_F_RE = re.compile(r'(?<![\w-])grep\s+-vxF((?:\s+-e\s+(?:"[^"]*"|\'[^\']*\'|[^\s|;&)\'"]+))+)')
WIDEN_F_WORD_RE = re.compile(r'-e\s+("[^"]*"|\'[^\']*\'|[^\s|;&)\'"]+)')
WIDEN_E_RE = re.compile(r'(?<![\w-])grep\s+-vxE\s+(?:"((?:\\.|[^"\\])*)"|\'([^\']*)\')')
WIDEN_A_RE = re.compile(r'(?<![\w-])grep\s+(?:-vE|-E\s+-v)\s+'
                        r'(?:"\^\(((?:\\.|[^"\\])*)\)\$"|\'\^\(([^\']*)\)\$\')')


def is_scope_span(span):
    """True when a code span is a scope check: git diff --name-only with a grep -v allow-list."""
    return 'git diff --name-only' in span and INVERT_GREP_RE.search(span) is not None


DENY_EXCL_RE = re.compile(r"""(['"]):\(exclude\)([^'"\s]+)\1""")


def is_deny_span(span):
    """True when a code span is a deny-path scope guard: git diff --name-only with an :(exclude)
    pathspec and no grep -v allow-list (that one is is_scope_span)."""
    return ('git diff --name-only' in span and not is_scope_span(span)
            and DENY_EXCL_RE.search(span) is not None)


def deny_runs(span):
    """The :(exclude) pathspec tokens of a span, grouped into runs of tokens separated only by
    whitespace: [[match, ...], ...]."""
    runs, last = [], None
    for m in DENY_EXCL_RE.finditer(span):
        if last is not None and not span[last.end():m.start()].strip():
            runs[-1].append(m)
        else:
            runs.append([m])
        last = m
    return runs


def widen_deny(span, paths):
    """(new span, paths added, why-not) for a deny-path guard: an :(exclude)<path> pathspec per new path
    appended after the one run of exclude pathspecs, in that run's quote style. why-not is a refusal
    reason (new is None) when the span has not exactly one run or one git diff --name-only."""
    runs = deny_runs(span)
    if len(runs) != 1:
        return None, [], f'the deny-path scope criterion has {len(runs)} :(exclude) pathspec runs; need exactly one'
    if span.count('git diff --name-only') != 1:
        return None, [], 'the deny-path scope criterion has several git diff --name-only commands; need exactly one'
    listed = {m.group(2) for m in runs[0]}
    add = [p for p in paths if p not in listed]
    q = runs[0][-1].group(1)
    at = runs[0][-1].end()
    return span[:at] + ''.join(f' {q}:(exclude){p}{q}' for p in add) + span[at:], add, None


def repo_path_ok(p):
    """True when p is a repo-relative path of [A-Za-z0-9._/@+-] with no leading - or / and no ..
    component: the path rule widen and lane share."""
    return (WIDEN_PATH_RE.match(p) is not None and not p.startswith('-') and not p.startswith('/')
            and '..' not in p.split('/'))


def ere_escape(path):
    """The path with a backslash before each ERE special character."""
    return ''.join('\\' + c if c in ERE_SPECIAL else c for c in path)


def ere_alternatives(pattern):
    """The top-level alternatives of an ERE pattern, split on each | not escaped by a backslash."""
    return re.split(r'(?<!\\)\|', pattern)


def widen_forms(span):
    """[(form, match)] for each recognized allow-list form in a span: F (grep -vxF -e ...),
    E (grep -vxE "<pattern>"), A (grep -vE or grep -E -v "^(...)$")."""
    return [(form, m) for form, rx in (('F', WIDEN_F_RE), ('E', WIDEN_E_RE), ('A', WIDEN_A_RE))
            for m in rx.finditer(span)]


def widen_listed(form, m):
    """The entries a form already allows: the -e words (quotes stripped) for F, the alternatives for E and A."""
    if form == 'F':
        return [w[1:-1] if w[:1] in '"\'' and w[-1:] == w[:1] and len(w) > 1 else w
                for w in WIDEN_F_WORD_RE.findall(m.group(1))]
    return ere_alternatives(m.group(1) if m.group(1) is not None else m.group(2))


def widen_span(span, form, m, paths):
    """The span with paths added to its allow-list form."""
    if form == 'F':
        at, add = m.end(), ''.join(f' -e {p}' for p in paths)
    else:
        at = m.end() - (1 if form == 'E' else 3)
        add = ''.join(f'|{ere_escape(p)}' for p in paths)
    return span[:at] + add + span[at:]


def replace_span(line, old, new):
    """The line with its code span whose text (one edge space stripped, like line_spans) is old
    replaced by new, the backtick fence and edge spaces kept."""
    for m in SPAN_RE.finditer(line):
        text = m.group(2)
        lead = ' ' if text.startswith(' ') else ''
        trail = ' ' if text.endswith(' ') and len(text) > 1 else ''
        if text[len(lead):len(text) - len(trail)] == old:
            return line[:m.start(2)] + lead + new + trail + line[m.end(2):]
    return None


def add_scope_widened(text, paths, reason=None):
    """The handoff text with one '## Scope widened' item per path: appended to the existing section,
    after its last non-blank line, or in a new section at the end. A reason is appended to each item."""
    tail = f': {reason}' if reason else ''
    items = [f'- `{p}`: allowed by a conductor scope decision (steps.py widen){tail}' for p in paths]
    lines = text.splitlines()
    start = next((i for i, x in enumerate(lines) if x.rstrip() == '## Scope widened'), None)
    if start is None:
        body = text.rstrip('\n')
        return f'{body}\n\n## Scope widened\n' + '\n'.join(items) + '\n'
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith('## ')), len(lines))
    last = end
    while last > start + 1 and not lines[last - 1].strip():
        last -= 1
    out = lines[:last] + items + lines[last:]
    return '\n'.join(out) + '\n'


def widen(step_dir, paths, timeout=300, reason=None, tree=None):
    """Add paths to the one scope criterion of <step dir>/handoff.md after every check passes, and
    record them under ## Scope widened. A step with no scope criterion at all and a reason: record the
    explicit path list and the reason under ## Scope widened, rewrite nothing else. Returns the one
    stdout line. Raises Fail (last line
    'plan defect: steps widen refused: ...; replan this step (/chain 4.2)') and writes nothing on any
    refusal."""
    d = records_of(step_dir)

    def refuse(why, detail=()):
        raise Fail('\n'.join(list(detail) + [f'plan defect: steps widen refused: {why}{SWAP_DEFECT}']))

    h = step_handoff(d)
    if not h.is_file():
        refuse(f'no step handoff at {h}')
    if not paths:
        refuse('no path given')
    for p in paths:
        if not repo_path_ok(p):
            refuse(f'not a repo-relative path of [A-Za-z0-9._/@+-] with no leading - or / and no .. '
                   f'component: {p}')
    paths = list(dict.fromkeys(paths))
    if reason is not None:
        reason = ' '.join(reason.split())
        if not reason:
            refuse('--reason is empty')

    text = h.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)
    items = [(i, line) for i, line in criteria_indexed([x.rstrip('\r\n') for x in lines]) if list_item(line)]
    scope = [(i, line, s) for i, line in items for s in line_spans(line)
             if is_scope_span(s) or is_deny_span(s)]
    rows = sorted(set(i for i, _, _ in scope))
    if not rows:
        if reason is not None:
            return widen_recorded(h, text, paths, reason)
        refuse('no criterion line has a command span with git diff --name-only and a grep -v allow-list '
               '(accepted forms: grep -vxF -e <word>..., grep -vxE "<pattern>", or grep -vE "^(...)$"; '
               "or a deny-path guard with one run of ':(exclude)<path>' pathspecs); "
               'pass --reason "<why>" to record an explicit file list instead')
    if len(rows) > 1:
        refuse(f'{len(rows)} criterion lines have a git diff --name-only span with a grep -v allow-list '
               'or an :(exclude) deny-path; need exactly one')
    if len(scope) > 1:
        refuse('the scope criterion line has several git diff --name-only spans with a grep -v allow-list '
               'or an :(exclude) deny-path')
    idx, target, old = scope[0]
    if is_deny_span(old):
        new, add, why = widen_deny(old, paths)
        if why:
            refuse(f'{why}: {old}')
    else:
        forms = widen_forms(old)
        if not forms:
            if reason is not None:
                return widen_recorded(h, text, paths, reason)
            refuse('the scope criterion has an unrecognized allow-list form (want grep -vxF -e <word>..., '
                   f'grep -vxE "<pattern>", or grep -vE "^(...)$"): {old}')
        if len(forms) > 1:
            refuse(f'the scope criterion has {len(forms)} allow-list forms; need exactly one: {old}')
        form, m = forms[0]
        listed = widen_listed(form, m)
        add = [p for p in paths if (p if form == 'F' else ere_escape(p)) not in listed]
        if not add:
            return 'widen: already applied'
        new = widen_span(old, form, m, add)
    if not add:
        return 'widen: already applied'
    new_line = replace_span(target, old, new)
    if new_line is None or list_item(new_line) is None:
        refuse(f'cannot rewrite the scope criterion line: {target}')
    if list_item(new_line)[:2] != list_item(target)[:2] or is_guard_line(new_line) != is_guard_line(target):
        refuse('the rewritten line lost its list marker or its (guard) tag')
    if new not in line_spans(new_line):
        refuse(f'the rewritten span is not a command span: {new}')
    findings = lint_steps(h, {1: f'## Step 1: widen\nlevel: L1\n### Acceptance criteria\n{new_line}'})
    if findings:
        refuse(f'the widened criterion does not lint: {new}', findings)

    try:
        top = lane_tree(d, tree)
    except Fail as e:
        refuse(str(e).removeprefix('steps: '))
    cwd = top or str(d)
    if top and os.path.realpath(top) != os.path.realpath(git_toplevel(d) or top):
        print(f'steps widen: {d}: evaluating the scope span in the work tree {top}', file=sys.stderr)
    base = base_sha(top, d)
    before = tree_state(top) if top else None
    detail, red = [], []
    rc, tail = run_guard(new, cwd, timeout, base)
    if rc != 0:
        why = f'timed out after {timeout:g}s' if rc is None else f'exit {rc}'
        detail.append(f'steps widen: {d}: widened scope span is red now ({why}): {new}')
        detail += [f'  {t}' for t in tail]
        red.append(f'red now: {new}')
    after = tree_state(top) if before is not None else None
    changed = tree_changes(before, after) if after is not None else []
    if changed:
        detail += [f'steps widen: {d}: widened scope span changed the work tree: {p}' for p in changed]
        red.append(f'the widened span changed the work tree: {", ".join(changed)}')
    if red:
        refuse('; '.join(red), detail)

    ending = lines[idx][len(lines[idx].rstrip('\r\n')):]
    lines[idx] = new_line + ending
    h.write_text(add_scope_widened(''.join(lines), add, reason), encoding='utf-8')
    return f'steps widen: {d}: added {", ".join(add)} to the scope criterion: {new}'


def widen_recorded(h, text, paths, reason):
    """The no-criterion path of widen: the plan holds no scope allow-list to extend, so the conductor's
    explicit file list and reason are the allow-list, recorded under ## Scope widened. Returns the one
    stdout line; writes nothing when every path is already listed."""
    lines = text.splitlines()
    start = next((i for i, x in enumerate(lines) if x.rstrip() == '## Scope widened'), None)
    listed = set()
    if start is not None:
        for x in lines[start + 1:]:
            if x.startswith('## '):
                break
            mm = re.match(r'^- `([^`]+)`', x)
            if mm:
                listed.add(mm.group(1))
    add = [p for p in paths if p not in listed]
    if not add:
        return 'widen: already applied'
    h.write_text(add_scope_widened(text, add, reason), encoding='utf-8')
    return (f'steps widen: {h.parent}: no scope criterion; recorded {", ".join(add)} under '
            f'## Scope widened (reason: {reason})')


def cmd_widen(step_dir, paths, timeout=300, reason=None, tree=None):
    try:
        line = widen(step_dir, paths, timeout, reason, tree)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print(line)
    return 0


# --- selftest ---------------------------------------------------------------

HANDOFF = """---
id: T-0001
title: "x"
---

## Goal

Ship the widget.
Second goal line.

## Intent
- not part of the goal
"""

GOAL = 'Ship the widget.\nSecond goal line.'

STEP1 = """## Step 1: First thing
level: L2
### Do
Do one.

### Acceptance criteria
- one works"""

STEP2 = """## Step 2: Second thing
level: L1
### Do
Do two.
### Acceptance criteria
- two works"""

PLAN = f"""# Plan
## Goal
plan goal, not the task goal

{STEP1}


{STEP2}

## Risks
- RISKTEXT must not leak
"""

BROKEN_CRITERION = "- `grep -c 'foo' bar'`"

BROKEN_PLAN = PLAN.replace('- one works', BROKEN_CRITERION)


def snapshot(root):
    """Every file under root: relative path -> (mtime_ns, bytes). A handoff.md is held by content alone, without
    the ## Plan review growth a split refusal appends by design (T-0543): its `- <date> plan defect at split: `
    lines, and the section heading when that growth created it."""
    snap = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            p = pathlib.Path(dirpath) / f
            if f == 'handoff.md':
                text = p.read_bytes()
                kept = re.sub(rb'(?m)^- \d{4}-\d{2}-\d{2} plan defect at split: .*\n', b'', text)
                if kept != text:
                    kept = re.sub(rb'\n?## Plan review\n\Z', b'', kept)
                snap[str(p.relative_to(root))] = (None, kept)
                continue
            snap[str(p.relative_to(root))] = (p.stat().st_mtime_ns, p.read_bytes())
    return snap


HDR_NAME_RE = re.compile(r'^([a-z][a-z-]*)-L([1-5])')


def hdr(name, text):
    """A role-result fixture as run.sh writes it: the header line, role and level parsed from the file
    name, then text. Text that already starts with <!-- is returned as is."""
    if text.startswith('<!--'):
        return text
    m = HDR_NAME_RE.match(os.path.basename(str(name)))
    return f'<!-- role={m.group(1)} level=L{m.group(2)} model=opus effort=low -->\n{text}'


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


def selftest():
    misses = []

    def check(name, cond):
        if cond:
            print(f'ok: {name}')
        else:
            misses.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        count = [0]

        def task(plan=PLAN, handoff=HANDOFF, plan_name='planner-L2.md'):
            count[0] += 1
            d = tmp / f'task{count[0]}'
            d.mkdir()
            if handoff is not None:
                (d / 'handoff.md').write_text(handoff, encoding='utf-8')
            if plan is not None:
                (d / plan_name).write_text(hdr(plan_name, plan), encoding='utf-8')
            return d

        def refused(name, argv, root, needle=None, needles=()):
            before = snapshot(root)
            rc, out, err = run_main(argv)
            check(name, rc != 0 and err.strip() != '' and out == '' and snapshot(root) == before
                  and (needle is None or needle in err) and all(x in err for x in needles))

        want1 = f'## Task goal\n{GOAL}\n\n{STEP1}\n'
        want2 = f'## Task goal\n{GOAL}\n\n{STEP2}\n'

        # (precheck) T-0261: a task handoff with no ## Goal (a ## Task goal heading) is refused before any
        # planner runs; one with ## Goal passes
        d = task(plan=None, handoff='## Task goal\nx\n')
        refused('(precheck) a handoff with only ## Task goal is refused naming ## Goal', ['precheck', str(d)], d,
                '## Goal')
        refused('(precheck) the refusal names the ## Task goal heading it found', ['precheck', str(d)], d,
                needles=('found ## Task goal', 'expected ## Goal'))
        d = task(plan=None, handoff='## Notes\nx\n')
        refused('(precheck) no near heading keeps the plain message', ['precheck', str(d)], d)
        rc, _, err = run_main(['precheck', str(d)])
        check('(precheck) no near heading adds no found hint', 'found' not in err)
        d = task(handoff='## Task goal\nx\n')
        refused('(split) a handoff with only ## Task goal names it as found', ['split', str(d)], d,
                needles=('found ## Task goal', 'expected ## Goal'))
        d = task(plan=None, handoff=HANDOFF)
        rc, out, err = run_main(['precheck', str(d)])
        check('(precheck) a handoff with ## Goal passes silently', rc == 0 and out == '' and err == '')
        # (a) normal plan followed by ## Risks
        d = task()
        rc, out, _ = run_main(['split', str(d / 'planner-L2.md')])
        h1, h2 = d / 'step-1' / 'handoff.md', d / 'step-2' / 'handoff.md'
        got1 = h1.read_text(encoding='utf-8') if h1.is_file() else None
        got2 = h2.read_text(encoding='utf-8') if h2.is_file() else None
        check('(a) 2-step plan writes both handoffs exactly, Risks stays out',
              rc == 0 and got1 == want1 and got2 == want2 and got2 is not None and 'RISKTEXT' not in got2
              and out.split() == [str(h1), str(h2)])

        # (b) --only 2 writes only step-2; --only 9 fails and writes nothing
        d = task()
        rc, out, _ = run_main(['split', str(d), '--only', '2'])
        h2 = d / 'step-2' / 'handoff.md'
        check('(b) --only 2 writes only step-2',
              rc == 0 and not (d / 'step-1').exists() and h2.is_file()
              and h2.read_text(encoding='utf-8') == want2)
        d = task()
        refused('(b) --only 9 fails and writes nothing', ['split', str(d), '--only', '9'], d)

        # (c) task dir input picks the newest planner-*.md by recorded run order, never by file time
        def c_case(times, runs):
            d = task(plan=PLAN.replace('Do one.', 'L3 PLAN'), plan_name='planner-L3.md')
            (d / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN.replace('Do one.', 'L2 PLAN')),
                                             encoding='utf-8')
            for name, t in times.items():
                os.utime(d / name, (t, t))
            if runs is not None:
                (d / 'runs.jsonl').write_text(''.join(
                    f'{{"role": "planner", "level": "{n[8:10]}", "file": "{n}"}}\n' for n in runs), encoding='utf-8')
            rc, _, _ = run_main(['split', str(d)])
            h1 = d / 'step-1' / 'handoff.md'
            return rc, h1.read_text(encoding='utf-8') if h1.is_file() else ''

        def uses(res, want, other):
            rc, got = res
            return rc == 0 and f'{want} PLAN' in got and f'{other} PLAN' not in got

        recorded = ['planner-L3.md', 'planner-L2.md']
        check('(c) equal mtimes: runs.jsonl decides, the lower-named file recorded last is used',
              uses(c_case({'planner-L2.md': 1_000_000, 'planner-L3.md': 1_000_000}, recorded), 'L2', 'L3'))
        check('(c) inverse mtimes: runs.jsonl still decides, same result',
              uses(c_case({'planner-L2.md': 1_000_000, 'planner-L3.md': 2_000_000}, recorded), 'L2', 'L3'))
        check('(c) no runs.jsonl: level then k order, planner-L3.md beats a newer planner-L2.md',
              uses(c_case({'planner-L3.md': 1_000_000, 'planner-L2.md': 2_000_000}, None), 'L3', 'L2'))

        # (d) a step with no level line
        d = task(plan=PLAN.replace('level: L1\n', 'Level is L1\n'))
        refused('(d) missing level: fails and writes nothing', ['split', str(d)], d)

        # (e) duplicate step number
        d = task(plan=PLAN.replace('## Step 2:', '## Step 1:'))
        refused('(e) duplicate step number fails and writes nothing', ['split', str(d)], d)

        # (f) no steps
        d = task(plan='# Plan\n## Goal\nnothing\n## Risks\n- none\n')
        refused('(f) no steps fails and writes nothing', ['split', str(d)], d)

        # (g) step-1 holds builder output: refuse, step-1 and step-2 untouched
        d = task()
        (d / 'step-1').mkdir()
        (d / 'step-1' / 'handoff.md').write_text('old step 1\n', encoding='utf-8')
        (d / 'step-1' / 'builder-L2.md').write_text(hdr('builder-L2.md', '## Status\ndone\n'), encoding='utf-8')
        (d / 'step-2').mkdir()
        (d / 'step-2' / 'handoff.md').write_text('old step 2\n', encoding='utf-8')
        refused('(g) step-1 with builder-L2.md refuses, names superseded, changes nothing',
                ['split', str(d)], d, needle='superseded')
        d = task()
        (d / 'step-2').mkdir()
        (d / 'step-2' / 'verifier-L1.md').write_text(hdr('verifier-L1.md', 'pass\n'), encoding='utf-8')
        refused('(g) verifier-*.md output also refuses', ['split', str(d)], d, needle='superseded')
        # (g) --supersede: step-2 holding builder-L2.md moves to the next free step-2.superseded-<k>/, then
        # a new step-2 is written; the negative control (no flag) is the refusal just above
        d = task()
        (d / 'step-2').mkdir()
        (d / 'step-2' / 'handoff.md').write_text('old step 2\n', encoding='utf-8')
        (d / 'step-2' / 'builder-L2.md').write_text(hdr('builder-L2.md', '## Status\ndone\n'), encoding='utf-8')
        refused('(g) --supersede negative control: without the flag step-2 with builder-L2.md refuses, '
                'writes nothing', ['split', str(d), '--only', '2'], d, needle='--supersede')
        rc, out, err = run_main(['split', str(d), '--only', '2', '--supersede'])
        sup = d / 'step-2.superseded-1'
        check('(g) --supersede: step-2 moves to step-2.superseded-1 with its output, a new step-2 is written',
              rc == 0 and (sup / 'builder-L2.md').is_file()
              and (sup / 'handoff.md').read_text(encoding='utf-8') == 'old step 2\n'
              and (d / 'step-2' / 'handoff.md').read_text(encoding='utf-8') == want2
              and not (d / 'step-2' / 'builder-L2.md').exists() and 'step-2.superseded-1' in err)
        (d / 'step-2' / 'verifier-L1.md').write_text(hdr('verifier-L1.md', 'pass\n'), encoding='utf-8')
        rc, _, _ = run_main(['split', str(d), '--only', '2', '--supersede'])
        check('(g) --supersede: a second supersede takes the next free k (step-2.superseded-2)',
              rc == 0 and (d / 'step-2.superseded-2' / 'verifier-L1.md').is_file() and sup.is_dir()
              and (d / 'step-2' / 'handoff.md').read_text(encoding='utf-8') == want2)
        d = task()
        (d / 'step-2').mkdir()
        (d / 'step-2' / 'builder-L2.md').write_text(hdr('builder-L2.md', '## Status\ndone\n'), encoding='utf-8')
        refused('(g) --supersede renames nothing when another check refuses (--only 9)',
                ['split', str(d), '--only', '9', '--supersede'], d)

        # (h) handoff with no Goal section, and no handoff at all
        d = task(handoff='---\nid: T-0001\n---\n\n## Intent\n- x\n')
        refused('(h) handoff with no ## Goal fails and writes nothing', ['split', str(d)], d)
        d2 = task(handoff=None)
        refused('(h) missing handoff.md fails and writes nothing', ['split', str(d2)], d2)

        # re-split over a plain handoff.md with no role output overwrites it
        d = task()
        (d / 'step-1').mkdir()
        (d / 'step-1' / 'handoff.md').write_text('stale\n', encoding='utf-8')
        rc, _, _ = run_main(['split', str(d)])
        check('re-split overwrites a plain step-1/handoff.md with no role output',
              rc == 0 and (d / 'step-1' / 'handoff.md').read_text(encoding='utf-8') == want1)

        # (i) a dot-prefixed closed ticket folder (.NNNN-slug) splits like any task dir
        d = tmp / '.0003-x'
        d.mkdir()
        (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
        (d / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN), encoding='utf-8')
        rc, _, _ = run_main(['split', str(d)])
        h1 = d / 'step-1' / 'handoff.md'
        check('(i) split on .0003-x writes .0003-x/step-1/handoff.md',
              rc == 0 and h1.is_file() and h1.read_text(encoding='utf-8') == want1)

        # (j) a criterion command that does not parse: split and lint refuse as a plan defect
        d = task(plan=BROKEN_PLAN)
        refused('(j) split refuses a broken criterion command as a plan defect, writes nothing',
                ['split', str(d)], d, needles=('plan defect', 'step 1', 'does not parse'))
        d2 = task(plan=PLAN.replace('- one works', "- `node -e \"console.log(`x`)\"`"))
        refused('(j) a nested-backtick criterion gets the hint line, first line kept',
                ['lint', str(d2 / 'planner-L2.md')], d2, needles=('does not parse', 'hint: a backtick', 'concatenation'))
        refused('(j) lint on the plan file exits 1 with plan defect, writes nothing',
                ['lint', str(d / 'planner-L2.md')], d, needle='plan defect')

        def j_dir(broken_name, clean_name):
            d = task(plan=None)
            (d / broken_name).write_text(hdr(broken_name, BROKEN_PLAN), encoding='utf-8')
            (d / clean_name).write_text(hdr(clean_name, PLAN), encoding='utf-8')
            (d / 'runs.jsonl').write_text(''.join(
                f'{{"role": "planner", "level": "{n[8:10]}", "file": "{n}"}}\n'
                for n in ('planner-L3.md', 'planner-L2.md')), encoding='utf-8')
            return d

        d = j_dir('planner-L2.md', 'planner-L3.md')
        refused('(j) lint on a task dir lints the plan runs.jsonl names newest (broken planner-L2.md)',
                ['lint', str(d)], d, needle='plan defect')
        d = j_dir('planner-L3.md', 'planner-L2.md')
        rc, out, err = run_main(['lint', str(d)])
        rc2, _, _ = run_main(['split', str(d)])
        check('(j) lint on a task dir skips an older broken planner-L3.md, like split',
              rc == 0 and out.strip() == 'steps lint: ok' and err == '' and rc2 == 0)

        # (order) T-0536: a criterion naming a path a later step creates can pass only after that step
        order_plan = ('# Plan\n\n## Step 1: Use the tool\nlevel: L2\n### Do\nCall the tool.\n'
                      '### Acceptance criteria\n- `test -f tools/new-tool.sh`\n\n'
                      '## Step 2: Make the tool\nlevel: L2\n### Do\nCreate `tools/new-tool.sh`.\n'
                      '### Acceptance criteria\n- `test -x tools/new-tool.sh`\n')
        d = task(plan=order_plan)
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(order) refuses a criterion naming a path a later step creates',
              rc == 1 and 'which a later step creates (step 2)' in err and 'step 1:' in err)
        d = task(plan=order_plan.replace('Call the tool.', 'Create `tools/new-tool.sh` and call it.'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check("(order) negative: the step's own Do creates the path", rc == 0 and 'a later step creates' not in err)
        d = task(plan=order_plan)
        (d / 'tools').mkdir()
        (d / 'tools' / 'new-tool.sh').write_text('#!/bin/sh\n', encoding='utf-8')
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(order) negative: the path exists in the tree', rc == 0 and 'a later step creates' not in err)
        d = task(plan=order_plan.replace('- `test -f tools/', '- (guard) `test -f tools/'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(order) negative: a (guard) line names the path', rc == 0 and 'a later step creates' not in err)

        # (step cap) T-0553: a plan with more steps than its ticket size allows stops for the person, never a replan
        def cap_plan(k):
            return '# Plan\n## Goal\nx\n\n' + '\n'.join(f'## Step {i}: Part {i}\nlevel: L2\n### Do\nd\n### Acceptance criteria\n'
                                            f'- `test -f part{i}`\n- `test -s part{i}`\n' for i in range(1, k + 1))

        def cap_handoff(size):
            return HANDOFF.replace('title: "x"\n', f'title: "x"\nsize: {size}\n')

        d = task(plan=cap_plan(7), handoff=cap_handoff('L3'))
        refused('(step cap) lint refuses a 7-step L3 plan and writes nothing', ['lint', str(d)], d,
                needles=('7 steps exceed the step cap of 6 for size L3', '--approved'))
        rc, _, err = run_main(['lint', str(d)])
        check('(step cap) the refusal ends with a step cap line, never a plan defect line',
              err.strip().splitlines()[-1].startswith('step cap: split the ticket') and 'plan defect' not in err)
        refused('(step cap) split refuses the same plan and writes nothing', ['split', str(d)], d,
                needle='7 steps exceed the step cap of 6')
        d = task(plan=cap_plan(6), handoff=cap_handoff('L3'))
        rc, out, err = run_main(['lint', str(d)])
        check('(step cap) a 6-step L3 plan passes lint', rc == 0 and out.strip() == 'steps lint: ok' and 'step cap' not in err)
        d = task(plan=cap_plan(4), handoff=cap_handoff('L2'))
        refused('(step cap) a 4-step L2 plan is over the cap of 3', ['lint', str(d)], d, needle='cap of 3 for size L2')
        d = task(plan=cap_plan(7))
        rc, _, err = run_main(['lint', str(d)])
        check('(step cap) negative: a handoff with no size has no cap', rc == 0 and 'step cap' not in err)
        d = task(plan=cap_plan(7), handoff=cap_handoff('L3'))
        refused('(step cap) --approved needs "<who: why>"', ['lint', str(d), '--approved', 'yes'], d, needle='<who: why>')
        rc, out, err = run_main(['lint', str(d), '--approved', 'maintainer: one ticket on purpose'])
        skips = (d / 'skips.md').read_text(encoding='utf-8') if (d / 'skips.md').is_file() else ''
        check('(step cap) --approved lets a 7-step L3 plan through and records it in skips.md',
              rc == 0 and out.strip() == 'steps lint: ok'
              and skips == 'step cap approved: planner-L2.md: maintainer: one ticket on purpose\n')
        rc, out, err = run_main(['split', str(d)])
        check('(step cap) the recorded approval lets split write all 7 steps without the flag',
              rc == 0 and len(out.split()) == 7 and 'step cap' not in err)
        (d / 'planner-L3.md').write_text(hdr('planner-L3.md', cap_plan(7)), encoding='utf-8')
        refused('(step cap) a newer plan file needs its own approval', ['lint', str(d / 'planner-L3.md')], d,
                needle='step cap of 6')
        d = task(plan=cap_plan(6), handoff=cap_handoff('L3'))
        run_main(['lint', str(d), '--approved', 'maintainer: not needed'])
        check('(step cap) a plan within its cap ignores --approved and writes nothing', not (d / 'skips.md').exists())

        # (lean) coarse-step warnings after a clean lint
        def lean_plan(levels, n_crit=2, title='Thing', assume=''):
            blocks = [f'## Step {i}: {title} {i}\nlevel: L{lv}\n### Do\nd\n### Acceptance criteria\n'
                      + '\n'.join(f'- c{j}' for j in range(n_crit)) for i, lv in enumerate(levels, 1)]
            return f'# Plan\n{assume}' + '\n\n'.join(blocks) + '\n'

        d = task(plan=lean_plan([1, 2, 3]))
        rc, out, err = run_main(['lint', str(d)])
        check('(lean) lint warns on a lean-eligible plan with 3 steps',
              rc == 0 and out == 'steps lint: ok\n' and 'steps lint: warning:' in err and '3 steps' in err)
        d = task()
        rc, out, err = run_main(['lint', str(d)])
        check('(lean) lint warns on a one-criterion step',
              rc == 0 and out == 'steps lint: ok\n' and ' step 1: one acceptance criterion' in err
              and ' step 2: one acceptance criterion' in err)
        three = lean_plan([1, 2, 3], n_crit=1)
        quiet = [task(plan=three, plan_name='planner-L3.md'),
                 task(plan=lean_plan([1, 4, 2], n_crit=1)),
                 task(plan=lean_plan([1, 2], n_crit=1) + '\n## Step 3: Merge lane\nlevel: L2\n'
                      '### Acceptance criteria\n- m\n'),
                 task(plan=three, plan_name='planner-L1.md'),
                 task(plan=three, handoff=HANDOFF + '\n## Plan review\nrequired\n'),
                 task(plan=lean_plan([1, 2, 3], n_crit=1,
                                     assume='## Assumptions\n- unresolved: which db\n\n'))]
        (quiet[3] / 'planner-L2.md').write_text(three, encoding='utf-8')
        res = [run_main(['lint', str(q)]) for q in quiet]
        check('(lean) no warning for a planner L3 plan, a step at L4, a merge step, a replan, '
              'a ## Plan review line, or an unresolved: assumption',
              all(r[0] == 0 and r[2] == '' for r in res))
        d = task(plan=lean_plan([2, 3]))
        rc, out, err = run_main(['lint', str(d)])
        check('(lean) no warning for a two-step plan with two criteria per step',
              rc == 0 and out == 'steps lint: ok\n' and err == '')

        # (t0347) node --test on a directory fails lint; a bare count warns; a count with a command passes
        d = task(plan=PLAN.replace('- one works', '- `node --test tests`'))
        refused('(t0347) lint refuses node --test on a directory',
                ['lint', str(d / 'planner-L2.md')], d, needles=('plan defect', 'node --test on a directory'))
        d = task(plan=PLAN.replace('- one works', '- `node --test tests/*.test.js` and `node --test tests/a.test.js`'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(t0347) node --test on a glob or a file passes lint', rc == 0 and 'directory' not in err)
        d = task(plan=PLAN.replace('- one works', '- all 12 tests pass'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(t0347) a bare count warns and exits 0',
              rc == 0 and 'cites a count without a named' in err and 'step 1' in err)
        d = task(plan=PLAN.replace('- one works', '- `python3 scripts/steps.py selftest` runs 12 cases'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(t0347) a count with a named command does not warn', rc == 0 and 'cites a count' not in err)

        # (t0475) a criterion span that counts or greps commit subjects warns and exits 0
        d = task(plan=PLAN.replace('- one works', "- `git log --oneline $SDLC_BASE_SHA..HEAD | grep -c 'feat: x' | grep -qx 3`"))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(t0475) a git log commit-subject criterion warns history-shaped criterion and exits 0',
              rc == 0 and out == 'steps lint: ok\n' and 'history-shaped criterion' in err and 'step 1' in err)
        d = task(plan=PLAN.replace('- one works', '- `git rev-list --count $SDLC_BASE_SHA..HEAD | grep -qx 3`'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(t0475) a git rev-list --count criterion warns', rc == 0 and 'history-shaped criterion' in err)
        d = task(plan=PLAN.replace('- one works', '- `git diff --quiet HEAD -- scripts/steps.py` and `grep -c "x" scripts/steps.py`'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(t0475) a state-form criterion does not warn', rc == 0 and 'history-shaped' not in err)

        # (t0686) a criterion holding an absolute home path warns and exits 0; a repo-relative one does not
        d = task(plan=PLAN.replace('- one works', '- `grep -q x /Users/someone/repo/scripts/steps.py`'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(t0686) an absolute home path in a criterion warns and exits 0',
              rc == 0 and out == 'steps lint: ok\n' and 'step 1: absolute home path in a criterion: grep -q x /Users/someone/' in err)
        d = task(plan=PLAN.replace('- one works', '- `grep -q x scripts/steps.py`'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(t0686) a repo-relative criterion does not warn', rc == 0 and 'absolute home path' not in err)

        # (k) command spans that parse, and non-command spans, pass
        k_spans = ['grep -c "x" scripts/steps.py', 'scripts/steps.py',
                   'python3 scripts/board.py --root <tmp>', 'SDLC_DRY_RUN=1 scripts/run.sh builder L3 x.md',
                   'd=$(mktemp -d) && ls "$d"', '--sort recent', 'duplicate of T-0002 (beta)']
        k_plan = PLAN.replace('- one works', '\n'.join(f'- `{s}`' for s in k_spans))
        d = task(plan=k_plan)
        rc, _, _ = run_main(['split', str(d)])
        rc2, out2, _ = run_main(['lint', str(d / 'planner-L2.md')])
        kept = command_spans(parse_steps(d / 'planner-L2.md')[1])
        check('(k) parsing command spans, a path, a flag, and prose pass: split writes both, lint ok',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and (d / 'step-2' / 'handoff.md').is_file()
              and rc2 == 0 and out2.strip() == 'steps lint: ok'
              and kept == [k_spans[0], k_spans[2], k_spans[3], k_spans[4]])

        # (k2) a || fallback between checks: lint and split refuse; quoted ||, the
        # `test $# -eq 0 ||` short circuit, and && pass
        d = task(plan=PLAN.replace('- one works', '- `grep -q a x || grep -q b x`'))
        refused('(k2) split refuses a || fallback criterion as a plan defect, writes nothing',
                ['split', str(d)], d, needles=('plan defect', 'step 1', 'joins two checks with ||'))
        refused('(k2) lint refuses a || fallback criterion with plan defect',
                ['lint', str(d / 'planner-L2.md')], d, needle='plan defect')
        ok_spans = ['grep -qE "a||b" x', "grep -q 'a||b' x",
                    'set -- $(ls); test $# -eq 0 || grep -q x "$@"', 'grep -q a x && grep -q b x',
                    'test -f a || exit 1', 'for f in a b; do test -f "$f" || exit 1; done',
                    'for id in P1 P2; do grep -qE "x" "$f" || { echo "missing $id"; exit 1; }; done',
                    'test "$(node -e "process.stdout.write(String(a || b))")" = 1']
        d = task(plan=PLAN.replace('- one works', '\n'.join(f'- `{s}`' for s in ok_spans)))
        rc, _, _ = run_main(['split', str(d)])
        rc2, out2, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k2) quoted ||, the test $# -eq 0 || short circuit, &&, and a fail-fast || nonzero exit '
              '(plain, in a loop, in a brace group) pass: split and lint ok',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and rc2 == 0
              and out2.strip() == 'steps lint: ok')
        check('(k2) the for loops are linted as command spans',
              command_spans(parse_steps(d / 'planner-L2.md')[1])[-2:] == ok_spans[-2:])
        for form in ('test -f a || exit 0', 'test -f a || true', 'test -f a || exit',
                     'test -f a || { exit 1; echo x; }',
                     'test -f a || exit 1 | cat',
                     'test "$(node -e "x")" = 1 || true',
                     'test -f a || { echo x; exit 1; } | cat',
                     'for p in a b; do test -f "$p" || echo MISSING "$p"; done',
                     'for p in a b; do grep -q a "$p" || grep -q b "$p"; done'):
            d = task(plan=PLAN.replace('- one works', f'- `{form}`'))
            refused(f'(k2) lint refuses a || fallback ({form}) with plan defect',
                    ['lint', str(d / 'planner-L2.md')], d, needles=('plan defect', 'joins two checks with ||'))
        for form in ('while read x; do test -f x || echo m; done < f',
                     'for p in a b; do grep -q a "$p" || grep -q b "$p"; done | cat'):
            d = task(plan=PLAN.replace('- one works', f'- `{form}`'))
            refused(f'(k2) lint refuses a || fallback in a compound with a trailing redirect or pipe ({form})',
                    ['lint', str(d / 'planner-L2.md')], d, needles=('plan defect', 'joins two checks with ||'))
        # (k2b) grep -P is vacuous on macOS: refused; portable forms pass
        for form in ("! cat x | grep -P '\\x{2014}'", "! grep -qP 'a' x", "! grep --perl-regexp a x"):
            d = task(plan=PLAN.replace('- one works', f'- `{form}`'))
            refused(f'(k2b) lint refuses grep -P ({form})', ['lint', str(d / 'planner-L2.md')], d,
                    needles=('plan defect', 'uses grep -P', 'python3 -c'))
        d = task(plan=PLAN.replace('- one works', '- `! cat x | grep -E "a|b"`\n- `! python3 -c "import sys; sys.exit(0)"`\n- `grep -c P x`'))
        rc, out, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k2b) portable guard forms lint ok', rc == 0 and out.strip() == 'steps lint: ok')
        # (k2q) T-0660: a quantified prose criterion with no command is refused; one with a command span or one
        # naming an enumeration passes
        d = task(plan=PLAN.replace('- one works', '- meta.ts lists every public prop'))
        refused('(k2q) lint refuses a quantified prose criterion with no command', ['lint', str(d / 'planner-L2.md')],
                d, needles=('plan defect', 'quantified prose criterion has no command', 'every public prop'))
        for form in ('- every prop is listed: `node check.mjs`',
                     '- enumerate every public prop as k of N with a source line'):
            d = task(plan=PLAN.replace('- one works', form))
            rc, out, _ = run_main(['lint', str(d / 'planner-L2.md')])
            check(f'(k2q) lint passes a quantified criterion with a command or an enumeration ({form})',
                  rc == 0 and out.strip() == 'steps lint: ok')
        # (k2d) T-0617: a git command agents/verifier.md rule 3 forbids is refused in command text; quoted
        # text, read-only git, and git worktree add --detach pass
        for form in ('s=$(git stash create); test -n "$s"', 'git -C x checkout main', 'git reset --hard HEAD',
                     'git restore a', 'git commit -m x', 'test -n "$(git stash list)"'):
            d = task(plan=PLAN.replace('- one works', f'- `{form}`'))
            refused(f'(k2d) lint refuses a forbidden git command ({form})', ['lint', str(d / 'planner-L2.md')], d,
                    needles=('plan defect', 'agents/verifier.md rule 3'))
        d = task(plan=PLAN.replace('- one works', '- `s=$(git stash create); test -n "$s"`'))
        refused('(k2d) the refusal names git stash', ['lint', str(d / 'planner-L2.md')], d,
                needles=('plan defect', 'git stash', 'agents/verifier.md rule 3'))
        # (k2s) T-0666: git stash or --autostash in a step's ### Do is refused; a clean Do passes
        for form in ('run git merge --autostash main', 'git stash push'):
            d = task(plan=PLAN.replace('Do one.', form))
            refused(f'(k2s) lint refuses a stash in ### Do ({form})', ['lint', str(d / 'planner-L2.md')], d,
                    needles=('plan defect', '### Do runs git stash or --autostash', form))
        d = task(plan=PLAN.replace('Do one.', 'run git merge main, then git status'))
        rc, out, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k2s) a clean Do lints ok', rc == 0 and out.strip() == 'steps lint: ok')
        ok_git = ['git diff --check', "grep -qF 'git stash list' x", 'grep -qF "git checkout" x',
                  'git worktree add --detach "$t" HEAD', 'git log -1 && git show HEAD && git rev-parse HEAD',
                  'git status --porcelain -- x', 'git restore-x']
        d = task(plan=PLAN.replace('- one works', '\n'.join(f'- `{x}`' for x in ok_git)))
        rc, out, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k2d) read-only git, git worktree add --detach, and quoted git words lint ok',
              rc == 0 and out.strip() == 'steps lint: ok')
        # (k2c) a tests: line names exact repo-relative files (T-0395); a directory, glob, absolute path, or .. is refused
        for form in ('tests/', 'tests/*.sh', '/abs/a.sh', '../a.sh'):
            d = task(plan=PLAN.replace('- one works', f'- one works\ntests: tests/ok.sh, {form}'))
            refused(f'(k2c) lint refuses a tests: entry ({form})', ['lint', str(d / 'planner-L2.md')], d,
                    needles=('plan defect', 'not an exact repo-relative file path'))
        d = task(plan=PLAN.replace('- one works', '- one works\n- tests: `tests/a.sh`, tests/b.sh'))
        rc, out, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k2c) exact test files lint ok and parse as declared',
              rc == 0 and out.strip() == 'steps lint: ok'
              and declared_tests('- tests: `tests/a.sh`, ./tests/b.sh\n') == (['tests/a.sh', 'tests/b.sh'], []))
        form = 'while read x; do test -f x || exit 1; done < f'
        d = task(plan=PLAN.replace('- one works', f'- `{form}`'))
        rc, out, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k2) a fail-fast loop with a trailing redirect is a command span and lints ok',
              rc == 0 and out.strip() == 'steps lint: ok'
              and command_spans(parse_steps(d / 'planner-L2.md')[1]) == [form])
        check('(k2) prose `for each file done < f` with a trailing redirect stays a non-command',
              not is_command('for each file done < f'))
        d = task(plan=PLAN.replace('- one works', '- `for each changed file`'))
        rc, out, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k2) prose `for each changed file` stays a non-command span: lint ok',
              rc == 0 and out.strip() == 'steps lint: ok'
              and command_spans(parse_steps(d / 'planner-L2.md')[1]) == [])

        # (k3) a criterion that pins a commit sha (bare, and in a <sha>..HEAD range): lint and split refuse
        sha = '3f9c' + '2ab'
        for form in (f'git diff --quiet {sha} -- src', f'git diff --quiet {sha}..HEAD -- src'):
            d = task(plan=PLAN.replace('- one works', f'- `{form}`'))
            refused(f'(k3) split refuses a criterion that pins a commit sha ({form}), writes nothing',
                    ['split', str(d)], d, needles=('plan defect', 'step 1', 'pins a commit sha fixed at plan time'))
            refused(f'(k3) lint refuses a criterion that pins a commit sha ({form}) with plan defect',
                    ['lint', str(d / 'planner-L2.md')], d, needles=('plan defect', 'pins a commit sha'))

        # (k3) the ancestry form is exempt; a second pinned sha beside it is still refused
        d = task(plan=PLAN.replace('- one works', f'- `git merge-base --is-ancestor {sha} HEAD`'))
        rc, out, _ = run_main(['lint', str(d / 'planner-L2.md')])
        rc2, _, _ = run_main(['split', str(d)])
        check('(k3) is-ancestor <sha> HEAD pass: lint ok and split writes the step',
              rc == 0 and out.strip() == 'steps lint: ok' and rc2 == 0
              and (d / 'step-1' / 'handoff.md').is_file())
        sha2 = 'e81d' + '04c'
        d = task(plan=PLAN.replace('- one works',
                                   f'- `git merge-base --is-ancestor {sha} HEAD && git diff --quiet {sha2} -- src`'))
        refused('(k3) is-ancestor plus a second pinned sha: refuse with plan defect',
                ['lint', str(d / 'planner-L2.md')], d, needles=('plan defect', 'pins a commit sha'))

        # (k4) a glob count compared with a fixed number: lint and split refuse
        d = task(plan=PLAN.replace('- one works', '- `test "$(ls .sdlc/*/handoff.md | wc -l)" -eq 26`'))
        refused('(k4) split refuses a glob count compared with a fixed number, writes nothing',
                ['split', str(d)], d,
                needles=('plan defect', 'step 1', 'compares a count over a changing set with a fixed number'))
        refused('(k4) lint refuses a glob count compared with a fixed number with plan defect',
                ['lint', str(d / 'planner-L2.md')], d, needles=('plan defect', 'fixed number'))

        # (k5) HEAD-relative git, %H, a single-file count, a glob count -eq 0, and the merge-step
        # two-parent criterion pass
        ok_spans = ['git diff --quiet HEAD -- src', 'git log -1 --format=%H HEAD~1',
                    'test "$(grep -c foo x.txt)" -eq 2', 'test "$(ls .sdlc/*/handoff.md | wc -l)" -eq 0',
                    'test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3']
        d = task(plan=PLAN.replace('- one works', '\n'.join(f'- `{s}`' for s in ok_spans)))
        rc, _, _ = run_main(['split', str(d)])
        rc2, out2, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k5) HEAD, %H, single-file count, glob count -eq 0, and two-parent check pass: '
              'no pins a commit sha, no fixed number finding',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and rc2 == 0
              and out2.strip() == 'steps lint: ok')

        # (k6) a criterion that requires a clean porcelain status: lint and split refuse
        st = 'git ' + 'status'
        for form in (f'test -z "$({st} --porcelain)"', f'test -z "$({st} -s)"',
                     f'test "$({st} --porcelain | wc -l)" -eq 0'):
            d = task(plan=PLAN.replace('- one works', f'- `{form}`'))
            refused(f'(k6) split refuses a criterion that requires a clean porcelain status ({form}), writes nothing',
                    ['split', str(d)], d, needles=('plan defect', 'step 1', 'clean porcelain status'))
            refused(f'(k6) lint refuses a criterion that requires a clean porcelain status ({form}) with plan defect',
                    ['lint', str(d / 'planner-L2.md')], d, needles=('plan defect', 'clean porcelain status'))
        ok_spans = ['git diff --quiet HEAD -- src', 'test -z "$(git ls-files --others --exclude-standard -- src)"',
                    f'test -z "$({st} --porcelain -- src)"', '! git rev-parse -q --verify MERGE_HEAD']
        d = task(plan=PLAN.replace('- one works', '\n'.join(f'- `{s}`' for s in ok_spans)))
        rc2, out2, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k6) diff HEAD, untracked ls-files, path-scoped status, and no MERGE_HEAD pass lint',
              rc2 == 0 and out2.strip() == 'steps lint: ok')

        # (k8) a criterion that requires a clean whole-tree diff: lint and split refuse; a pathspec, a
        # commit-to-commit range, a negated --quiet, a plain listing, and diff-tree pass
        df = 'git ' + 'diff'
        for form in (f'{df} --quiet', f'{df} --exit-code HEAD', f'{df} --quiet "$SDLC_BASE_SHA"',
                     f'test -z "$({df} --name-only HEAD)"'):
            d = task(plan=PLAN.replace('- one works', f'- `{form}`'))
            refused(f'(k8) split refuses a criterion that requires a clean whole-tree diff ({form}), writes nothing',
                    ['split', str(d)], d, needles=('plan defect', 'step 1', 'clean whole-tree diff'))
            refused(f'(k8) lint refuses a criterion that requires a clean whole-tree diff ({form}) with plan defect',
                    ['lint', str(d / 'planner-L2.md')], d, needles=('plan defect', 'clean whole-tree diff'))
        ok_spans = [f'{df} --quiet HEAD -- src', f'{df} --quiet HEAD~1 HEAD', f'{df} --exit-code main...HEAD',
                    f'! {df} --quiet', f'{df} --name-only HEAD', f'{df}-tree --cc HEAD']
        d = task(plan=PLAN.replace('- one works', '\n'.join(f'- `{s}`' for s in ok_spans)))
        rc2, out2, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k8) a pathspec, a two-commit range, a negated --quiet, a listing, and diff-tree pass lint',
              rc2 == 0 and out2.strip() == 'steps lint: ok')

        # (k7) a bare name=value assignment is not a comparison; = == != comparisons still refuse
        ok_spans = ['n=26; ls .sdlc/*/handoff.md | wc -l', 'export N=26; find . -name "*.md" | grep -c md']
        d = task(plan=PLAN.replace('- one works', '\n'.join(f'- `{s}`' for s in ok_spans)))
        rc, _, _ = run_main(['split', str(d)])
        rc2, out2, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k7) a bare n=26 assignment beside a glob count passes: split and lint ok',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and rc2 == 0
              and out2.strip() == 'steps lint: ok'
              and command_spans(parse_steps(d / 'planner-L2.md')[1]) == ok_spans)
        for form in ('[ "$(ls x* | wc -l)" = 26 ]', '[ "$(ls x* | wc -l)" == 26 ]',
                     '[ "$(ls x* | wc -l)" != 26 ]', 'n=26; ls x* | wc -l | grep -q x; [ "$n" == 26 ]'):
            d = task(plan=PLAN.replace('- one works', f'- `{form}`'))
            refused(f'(k7) lint refuses a glob count compared with a fixed number ({form})',
                    ['lint', str(d / 'planner-L2.md')], d,
                    needles=('plan defect', 'compares a count over a changing set with a fixed number'))

        # (l) a broken command under ### Do is not a criterion
        d = task(plan=PLAN.replace('Do one.', BROKEN_CRITERION))
        rc, _, _ = run_main(['split', str(d)])
        check('(l) a broken command under ### Do is ignored: split writes normally',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and (d / 'step-2' / 'handoff.md').is_file())

        # (m) a broken command inside a ``` fence under the criteria is skipped
        d = task(plan=PLAN.replace('- one works', f'- one works\n```\n{BROKEN_CRITERION}\n```'))
        rc, _, _ = run_main(['split', str(d)])
        check('(m) a broken command inside a ``` fence is skipped: split writes normally',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and (d / 'step-2' / 'handoff.md').is_file())

        # (n) split --only runs the step's (guard) criteria; full split and lint never do.
        # Every guard uses absolute tmp paths, so none touches the repo.
        def guard_plan(*criteria):
            return ('## Goal\ng\n\n## Step 1: x\nlevel: L1\n### Do\nd\n### Acceptance criteria\n'
                    + ''.join(f'- {c}\n' for c in criteria))

        red_span = f'test -e {tmp}/nonexistent-sdlc-guard'
        d = task(plan=guard_plan('not a guard', f'(guard) `{red_span}`'))
        before = snapshot(d)
        rc, out, err = run_main(['split', str(d), '--only', '1'])
        last = err.strip().splitlines()[-1] if err.strip() else ''
        check('(n) --only with a red guard refuses, writes nothing, last line is plan defect with the span',
              rc == 1 and out == '' and snapshot(d) == before and not (d / 'step-1').exists()
              and last.startswith('plan defect:') and red_span in last and '(exit 1)' in err)

        green = tmp / 'n-green-ran'
        d = task(plan=guard_plan(f'(guard) `touch {green} && test -f handoff.md`'))
        rc, out, err = run_main(['split', str(d), '--only', '1'])
        check('(n) --only with a green guard runs it (from the task dir outside git) and writes the handoff',
              rc == 0 and err == '' and green.exists() and (d / 'step-1' / 'handoff.md').is_file())

        # (T-0726) split --only exports a fresh SDLC_TMP_WORKTREES to guard and red spans and removes it after
        saved_tmpwt = os.environ.pop('SDLC_TMP_WORKTREES', None)
        try:
            seen = tmp / 'n-tmpwt-guard'
            d = task(plan=guard_plan(f'(guard) `x=$(mktemp -d "$SDLC_TMP_WORKTREES/x.XXXXXX") && printf %s "$SDLC_TMP_WORKTREES" > {seen}`'))
            rc, _, err = run_main(['split', str(d), '--only', '1'])
            used = seen.read_text() if seen.is_file() else ''
            check('(T-0726) --only exports SDLC_TMP_WORKTREES to a guard, a fresh dir removed afterwards',
                  rc == 0 and err == '' and used != '' and not pathlib.Path(used).exists())
            seen = tmp / 'n-tmpwt-red'
            d = task(plan=guard_plan(f'(red) `printf %s "$SDLC_TMP_WORKTREES" > {seen}; test ! -d "$SDLC_TMP_WORKTREES"`'))
            rc, _, err = run_main(['split', str(d), '--only', '1'])
            used = seen.read_text() if seen.is_file() else ''
            check('(T-0726) --only exports SDLC_TMP_WORKTREES to a (red) span, a fresh dir removed afterwards',
                  rc == 0 and err == '' and used != '' and not pathlib.Path(used).exists())
        finally:
            if saved_tmpwt is not None:
                os.environ['SDLC_TMP_WORKTREES'] = saved_tmpwt

        # (T-0377) the plan folder lacks the file the guard greps; the lane tree has it
        lane_tree = tmp / 'n-lane-tree'
        lane_tree.mkdir()
        (lane_tree / 'lane-only.txt').write_text('x\n')
        d = task(plan=guard_plan('(guard) `test -f lane-only.txt`'))
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(n) --only without --tree runs the guard in the plan folder (red: file is in the lane tree only)',
              rc == 1 and 'plan defect:' in err and not (d / 'step-1').exists())
        rc, out, err = run_main(['split', str(d), '--only', '1', '--tree', str(lane_tree)])
        check('(n) --only --tree runs the guard in the lane tree and writes the handoff',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())

        d = task(plan=guard_plan(f'(guard) `git diff --quiet HEAD^1 HEAD && test -e {tmp}/nope`'))
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(n) a HEAD^1 guard is skipped (it would be red if run)',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())

        d = task(plan=guard_plan('(guard) `test -e <tmp>/nope`'))
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(n) a <placeholder> guard is skipped (it would be red if run)',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())

        # T-0404: an operator span (i<t ... >=, =>) is a command, not a <placeholder>
        check('(n) a node -e body with i<t and => is not skipped',
              not guard_skipped('node -e "for(let i=0;i<t;i++){}; const f=(x)=>x"'))
        check('(n) a node -e body with i<t || n >= 1 is not skipped',
              not guard_skipped('node -e "if (i<t || n >= 1) process.exit(0)"'))
        check('(n) a python -c body with a<b and c>d is not skipped',
              not guard_skipped("python3 -c 'a=1; b=2; assert a<b or b>a'"))
        check('(n) an unquoted i<t ... >= is not skipped', not guard_skipped('test $i<t && test $n >= 1'))
        check('(n) <sha> and <step dir> are still skipped',
              guard_skipped('git cat-file -e <sha>') and guard_skipped('test -d <step dir>/x')
              and guard_skipped('test -e <L1|L2|L3>') and guard_skipped('node -e "1" <sha>'))
        check('(n) lint fills a real placeholder but leaves a node -e body alone',
              fill_placeholders('node -e "i<t; f=(x)=>x" <sha>') == 'node -e "i<t; f=(x)=>x" PLACEHOLDER')

        d = task(plan=guard_plan('(guard) `sleep 30`'))
        before = snapshot(d)
        t0 = time.monotonic()
        rc, out, err = run_main(['split', str(d), '--only', '1', '--guard-timeout', '1'])
        took = time.monotonic() - t0
        last = err.strip().splitlines()[-1] if err.strip() else ''
        check('(n) a guard past --guard-timeout refuses fast, writes nothing, plan defect last line',
              rc == 1 and out == '' and snapshot(d) == before and took < 15
              and 'timed out after 1s' in err and last.startswith('plan defect:') and 'sleep 30' in last)

        # (guard timeout) a "guard timeout: <seconds>" line sets the split --only default; a step line
        # beats the plan line, an explicit --guard-timeout beats both, and 0 counts as no line.
        def gt_plan(plan_line, step_line, span):
            return (f'## Goal\ng\n{plan_line}\n\n## Step 1: x\nlevel: L1\n{step_line}\n### Do\nd\n'
                    f'### Acceptance criteria\n- (guard) `{span}`\n\n## Risks\nguard timeout: 99\n')

        def gt_refused(plan_text, argv_extra=()):
            d = task(plan=plan_text)
            before = snapshot(d)
            t0 = time.monotonic()
            rc, out, err = run_main(['split', str(d), '--only', '1', *argv_extra])
            took = time.monotonic() - t0
            return rc, out, err, took, snapshot(d) == before and not (d / 'step-1').exists()

        rc, out, err, took, untouched = gt_refused(gt_plan('guard timeout: 1', '', 'sleep 3'))
        rc2, _, err2, took2, untouched2 = gt_refused(gt_plan('guard timeout: 1', 'guard timeout: 0', 'sleep 3'))
        check('(guard timeout) a plan guard timeout line sets the split --only default',
              rc == 1 and out == '' and untouched and took < 15 and 'timed out after 1s' in err
              and rc2 == 1 and untouched2 and took2 < 15 and 'timed out after 1s' in err2
              and plan_guard_timeout(task(plan=gt_plan('guard timeout: 1', 'guard timeout: 7', 'x y')) / 'planner-L2.md') == 1
              and plan_guard_timeout(task(plan=gt_plan('guard timeout: 0', 'guard timeout: 7', 'x y')) / 'planner-L2.md') == 99)

        rc, out, err, took, untouched = gt_refused(gt_plan('guard timeout: 10', 'guard timeout: 1', 'sleep 3'))
        check('(guard timeout) a step guard timeout line overrides the plan line',
              rc == 1 and out == '' and untouched and took < 15 and 'timed out after 1s' in err
              and step_guard_timeout('## Step 1: x\nlevel: L1\nguard timeout: 2.5') == 2.5
              and step_guard_timeout('## Step 1: x\nlevel: L1\nguard timeout: 0') is None)

        d = task(plan=gt_plan('guard timeout: 1', 'guard timeout: 1', 'sleep 2'))
        rc, _, err = run_main(['split', str(d), '--only', '1', '--guard-timeout', '10'])
        rc2, out2, err2, _, untouched2 = gt_refused(gt_plan('guard timeout: 10', 'guard timeout: 10', 'sleep 3'),
                                                    ('--guard-timeout', '1'))
        check('(guard timeout) --guard-timeout overrides both lines',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file()
              and rc2 == 1 and out2 == '' and untouched2 and 'timed out after 1s' in err2)

        marker = tmp / 'n-full-ran'
        d = task(plan=guard_plan(f'(guard) `touch {marker}`', f'(guard) `{red_span}`'))
        rc, _, _ = run_main(['split', str(d)])
        rc2, out2, _ = run_main(['lint', str(d)])
        check('(n) full split and lint execute no guard: marker absent, a red guard does not refuse',
              rc == 0 and rc2 == 0 and out2.strip() == 'steps lint: ok'
              and (d / 'step-1' / 'handoff.md').is_file() and not marker.exists())

        check('(n) guard_spans keeps only (guard) lines and the same spans command_spans sees',
              guard_spans('## Step 1: x\nlevel: L1\n### Do\n- (guard) `ls -e /`\n### Acceptance criteria\n'
                          '- `ls -a /`\n* (guard) `ls -b /` and `ls -c /`\n  - (guard) `ls -f /`\n'
                          '- (guard) prose\n- x (guard) `ls -d /`\n```\n- (guard) `ls -g /`\n```\n')
              == ['ls -b /', 'ls -c /', 'ls -f /'])

        # (o) split --only in a git work tree refuses when the guards changed the tree
        # (tracked or untracked); a tree already dirty before passes when the guards leave it as is.
        # Each case builds its own throwaway repo under tmp; guards run from its toplevel.
        def o_repo(*criteria, commit=None, dirty=None):
            count[0] += 1
            r = tmp / f'o-repo{count[0]}'
            r.mkdir()
            subprocess.run(['git', 'init', '-q', str(r)], check=True, capture_output=True)
            if commit:
                (r / commit).write_text('a\n', encoding='utf-8')
                subprocess.run(['git', '-C', str(r), 'add', commit], check=True, capture_output=True)
                subprocess.run(['git', '-C', str(r), '-c', 'user.name=t', '-c', 'user.email=t@t',
                                'commit', '-qm', 'i'], check=True, capture_output=True)
            if dirty:
                (r / dirty).write_text('pre\n', encoding='utf-8')
            d = r / '.sdlc' / 'x'
            d.mkdir(parents=True)
            (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
            (d / 'planner-L2.md').write_text(hdr('planner-L2.md', guard_plan(*criteria)), encoding='utf-8')
            return d

        def o_refused(name, d, path):
            rc, out, err = run_main(['split', str(d), '--only', '1'])
            last = err.strip().splitlines()[-1] if err.strip() else ''
            check(name, rc == 1 and out == '' and not (d / 'step-1').exists()
                  and last.startswith('plan defect:') and 'changed the work tree' in last
                  and path in last and last.endswith('; replan this step (/chain 3)')
                  and f'(guard) criteria changed the work tree: {path}' in err)

        o_refused('(o) a guard that creates an untracked file refuses, writes nothing, plan defect names the path',
                  o_repo('(guard) `touch o-made && test -f o-made`'), 'o-made')
        o_refused('(o) a guard that modifies a committed tracked file refuses, writes nothing, names the path',
                  o_repo('(guard) `echo b >> tracked.txt`', commit='tracked.txt'), 'tracked.txt')
        d = o_repo('(guard) `test -d .sdlc`', commit='tracked.txt')
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(o) a guard that changes nothing passes and writes the handoff',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())
        d = o_repo('(guard) `test -f already-dirty && grep -q a tracked.txt`', commit='tracked.txt',
                   dirty='already-dirty')
        (d.parents[1] / 'tracked.txt').write_text('a\nedited before\n', encoding='utf-8')
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(o) a tree dirty before (untracked and modified), guards changing nothing, passes',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())
        d = o_repo('(guard) `echo more >> already-dirty`', dirty='already-dirty')
        o_refused('(o) a guard that changes an already-dirty file refuses', d, 'already-dirty')
        d = o_repo('(guard) `touch o-both`', f'(guard) `{red_span}`')
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        lines = err.strip().splitlines()
        check('(o) a red guard and a changed tree are both reported, one plan defect last line',
              rc == 1 and not (d / 'step-1').exists() and red_span in lines[-1] and 'o-both' in lines[-1]
              and sum(x.startswith('plan defect:') for x in lines) == 1)
        d = o_repo('(guard) `touch o-full`')
        rc, _, _ = run_main(['split', str(d)])
        check('(o) full split in a git repo runs no guard and does not refuse',
              rc == 0 and not (d.parents[1] / 'o-full').exists() and (d / 'step-1' / 'handoff.md').is_file())

        # (red) split --only runs the step's (red) criteria after its guards: a span must exit nonzero now.
        def red_refused(name, d, *needles):
            before = snapshot(d)
            rc, out, err = run_main(['split', str(d), '--only', '1'])
            last = err.strip().splitlines()[-1] if err.strip() else ''
            check(name, rc == 1 and out == '' and snapshot(d) == before and not (d / 'step-1').exists()
                  and last.startswith('plan defect: red-first:') and last.endswith('; replan this step (/chain 3)')
                  and all(x in err for x in needles))

        def porcelain(d):
            return subprocess.run(['git', '-C', str(d.parents[1]), 'status', '--porcelain', '--untracked-files=all'],
                                  capture_output=True, text=True).stdout

        d = o_repo('(red) `test -f red-made`', '(guard) `test -d .sdlc`', commit='tracked.txt')
        rc, out, err = run_main(['split', str(d), '--only', '1'])
        check('(red) a (red) span that is red now passes: split --only writes the handoff',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())
        d = o_repo('(red) `test -d .sdlc`', commit='tracked.txt')
        red_refused('(red) a (red) span that is green now is refused with its name and writes nothing', d,
                    'red-first: step 1: `test -d .sdlc` is green now; it cannot detect the change')
        d = o_repo('(red) `sleep 30`')
        rc, out, err = run_main(['split', str(d), '--only', '1', '--guard-timeout', '1'])
        check('(red) a (red) span that times out is refused under the step timeout',
              rc == 1 and not (d / 'step-1').exists() and 'timed out after 1s' in err
              and 'red-first: step 1:' in err)
        d = o_repo('(red) `touch red-made; false`', commit='tracked.txt')
        red_refused('(red) a (red) span that changes the tree is refused, naming the path', d,
                    'changed the work tree: red-made (restored)')
        check('(red) the refused span left the tree as it found it (the snapshot restored it)',
              not (d.parents[1] / 'red-made').exists())
        d = o_repo('(red) `echo b >> tracked.txt; false`', commit='tracked.txt', dirty='already-dirty')
        (d.parents[1] / 'already-dirty').write_text('pre-edit\n', encoding='utf-8')
        red_refused('(red) a tracked-file edit is refused too', d, 'changed the work tree: tracked.txt (restored)')
        check('(red) tracked and already-dirty files are byte-identical after the refusal',
              (d.parents[1] / 'tracked.txt').read_text(encoding='utf-8') == 'a\n'
              and (d.parents[1] / 'already-dirty').read_text(encoding='utf-8') == 'pre-edit\n')
        d = o_repo('(red) `echo mine > already-dirty; false`', dirty='already-dirty')
        (d.parents[1] / 'already-dirty').write_text('builder work\n', encoding='utf-8')
        red_refused('(red) a span that rewrites an already-dirty file is refused', d, 'already-dirty (restored)')
        check('(red) the already-dirty file holds its content from before the span',
              (d.parents[1] / 'already-dirty').read_text(encoding='utf-8') == 'builder work\n')
        d = o_repo('(red) `touch s1; git add s1; false`', commit='tracked.txt')
        red_refused('(red) a span that stages a new file is refused', d, 's1 (restored)')
        check('(red) the staged new file is unstaged and gone',
              's1' not in porcelain(d) and not (d.parents[1] / 's1').exists())
        d = o_repo('(red) `git rm -q tracked.txt; false`', commit='tracked.txt')
        red_refused('(red) a span that deletes a tracked file is refused', d, 'tracked.txt (restored)')
        check('(red) the deleted tracked file is back and clean',
              (d.parents[1] / 'tracked.txt').read_text(encoding='utf-8') == 'a\n'
              and 'tracked.txt' not in porcelain(d))
        # control: with the restore disabled the same span leaves its file behind, so the checks above can fail
        d = o_repo('(red) `touch red-kept; false`')
        kept = globals()['red_restore']
        globals()['red_restore'] = lambda *a: []
        try:
            rc, _, err = run_main(['split', str(d), '--only', '1'])
        finally:
            globals()['red_restore'] = kept
        check('(red) control: with red_restore disabled the changed file stays behind (the restore check bites)',
              rc == 1 and (d.parents[1] / 'red-kept').exists())
        d = o_repo('(red) `test -d .sdlc`', '(guard) `test -d .sdlc`')
        rc, _, err = run_main(['split', str(d)])
        check('(red) a full split runs no (red) span: a green one does not refuse',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file())
        check('(red) red_spans keeps only (red) lines, a repeat once, and the spans line_spans sees',
              red_spans('## Step 1: x\nlevel: L1\n### Do\n- (red) `cat -e x`\n### Acceptance criteria\n'
                        '- `cat -a x`\n* (red) `cat -b x` and `cat -c x`\n  - (red) `cat -f x`\n'
                        '- (red) `cat -b x`\n- (guard) `cat -h x`\n- (guard)(red) `cat -i x`\n'
                        '- (red) prose\n- x (red) `cat -d x`\n```\n- (red) `cat -g x`\n```\n')
              == ['cat -b x', 'cat -c x', 'cat -f x', 'cat -i x'])

        # (r) ### Read first: each listed path must exist under the git toplevel of the plan's folder
        r = tmp / 'r-repo'
        (r / 'sub').mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', str(r)], check=True, capture_output=True)
        (r / 'sub' / 'AGENTS.md').write_text('x\n', encoding='utf-8')
        rf_ok = STEP1.replace('### Do', '### Read first\n- `sub/AGENTS.md`\n### Do')
        d = r / '.sdlc' / 'r-ok'
        d.mkdir(parents=True)
        (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
        (d / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN.replace(STEP1, rf_ok)), encoding='utf-8')
        rc, out, err = run_main(['lint', str(d)])
        check('(r) lint accepts a ### Read first path that exists', rc == 0 and 'steps lint: ok' in out)
        rc, out, _ = run_main(['split', str(d)])
        h = d / 'step-1' / 'handoff.md'
        check('(r) split copies ### Read first into the step handoff',
              rc == 0 and h.is_file() and h.read_text(encoding='utf-8') == f'## Task goal\n{GOAL}\n\n{rf_ok}\n')
        d = r / '.sdlc' / 'r-bad'
        d.mkdir(parents=True)
        (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
        (d / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN.replace(STEP1, rf_ok.replace('sub/AGENTS',
                                                                                                'gone/AGENTS'))),
                                          encoding='utf-8')
        rc, out, err = run_main(['lint', str(d)])
        rc2, out2, err2 = run_main(['split', str(d)])
        check('(r) lint refuses a ### Read first path that does not exist',
              rc == 1 and out == '' and 'does not exist: gone/AGENTS.md' in err
              and err.strip().splitlines()[-1].startswith('plan defect')
              and rc2 == 1 and 'gone/AGENTS.md' in err2 and not (d / 'step-1').exists())
        # T-0533: a path an earlier step marks [creates: <path>] is no plan defect in a later step; with no
        # marker the same path is refused as before (the negative control)
        for tag, mark in (('c-ok', ' [creates: sub/new.md, .sdlc/c-ok/notes.md]'), ('c-bad', '')):
            d = r / '.sdlc' / tag
            d.mkdir(parents=True)
            (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
            s2 = STEP2.replace('### Do', '### Read first\n- `sub/new.md`\n### Do').replace(
                'Do two.', f'Do two. Read .sdlc/{tag}/notes.md first.')
            (d / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN.replace('Do one.', 'Do one.' + mark)
                                                 .replace(STEP2, s2)), encoding='utf-8')
            rc, out, err = run_main(['lint', str(d)])
            rc2, _, err2 = run_main(['split', str(d), '--only', '2'])
            (d / 'step-2').mkdir(exist_ok=True)
            (d / 'step-2' / 'handoff.md').write_text(f'## Task goal\ng\n\n{s2}\n', encoding='utf-8')
            rc3, out3, err3 = run_main(['lint', str(d / 'step-2')])
            if mark:
                check('(r) T-0533: a path an earlier step marks [creates:] passes lint, split --only, and step lint',
                      rc == 0 and rc2 == 0 and rc3 == 0 and 'steps lint: ok' in out3 and err3 == '')
            else:
                check('(r) T-0533 control: with no create marker lint, split --only, and step lint still refuse',
                      rc == 1 and 'does not exist: sub/new.md' in err and rc2 == 1 and 'sub/new.md' in err2
                      and rc3 == 1 and f'.sdlc/{tag}/notes.md' in err3)

        # (rt) T-0647: a step whose scope names a path an AGENTS.md routes to a repo skill lists that skill under
        # ### Read first, else lint refuses; a repo with no routing lines lints as before (the control)
        rt = tmp / 'rt-repo'
        (rt / '.agents' / 'skills' / 'recipe').mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', str(rt)], check=True, capture_output=True)
        (rt / '.agents' / 'skills' / 'recipe' / 'SKILL.md').write_text('x\n', encoding='utf-8')
        RT_SCOPE = ('- `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; '
                    'git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } '
                    '| grep -vxF -e src/styles/a.css | { ! grep -q .; }`')
        rt_step = STEP1.replace('- one works', RT_SCOPE)
        rt_read = rt_step.replace('### Do', '### Read first\n- `.agents/skills/recipe/SKILL.md`\n### Do')
        RT_MSG = 'without its skill under ### Read first: .agents/skills/recipe/SKILL.md'

        def rt_lint(tag, agents, step):
            (rt / 'AGENTS.md').write_text(agents, encoding='utf-8')
            d = rt / '.sdlc' / tag
            d.mkdir(parents=True)
            (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
            (d / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN.replace(STEP1, step)), encoding='utf-8')
            return run_main(['lint', str(d)])

        RT_ROUTE = '# Repo\n\n- `src/styles/` uses `.agents/skills/recipe/SKILL.md`\n'
        check('(rt) repo_skill_routes reads the root routing line; routed_skills matches a path under it',
              repo_skill_routes(rt) == [] and (rt / 'AGENTS.md').write_text(RT_ROUTE, encoding='utf-8') > 0
              and repo_skill_routes(rt) == [('src/styles/', '.agents/skills/recipe/SKILL.md')]
              and routed_skills(rt, ['src/styles/a.css']) == ['.agents/skills/recipe/SKILL.md']
              and routed_skills(rt, ['src/other.css']) == [])
        # (rt) T-0672: a prose bullet that names a skill beside paths without a routing cue before it is no route
        RT_PROSE = ('# Repo\n\n- Models live in `src/a.json` (the `src/run.sh` rows mirror it), with the consumer '
                    'explanation in `.agents/skills/recipe/SKILL.md`. `src/check.py` checks them.\n')
        (rt / 'AGENTS.md').write_text(RT_PROSE, encoding='utf-8')
        check('(rt) T-0672: a prose bullet that mentions a skill beside paths yields no route',
              repo_skill_routes(rt) == [])
        # (rt) T-0676: a markdown link to a SKILL.md is a skill span, and a nested AGENTS.md prose line with a cue
        # routes; a root-relative skill cited from the nested file resolves to the root skill
        (rt / 'AGENTS.md').write_text('# Repo\n\n- `src/styles/` follows [recipe](.agents/skills/recipe/SKILL.md)\n',
                                      encoding='utf-8')
        check('(rt) T-0676: a root bullet that links the skill as markdown yields its route',
              repo_skill_routes(rt) == [('src/styles/', '.agents/skills/recipe/SKILL.md')])
        (rt / 'AGENTS.md').write_text('# Repo\n', encoding='utf-8')
        (rt / 'src').mkdir(exist_ok=True)
        (rt / 'src' / 'AGENTS.md').write_text(
            '# Src\n\nBefore editing `styles/`, read `.agents/skills/recipe/SKILL.md`.\n', encoding='utf-8')
        check('(rt) T-0676: a nested AGENTS.md prose line with a cue routes to the root skill',
              repo_skill_routes(rt) == [('src/styles/', '.agents/skills/recipe/SKILL.md')])
        (rt / 'src' / 'AGENTS.md').unlink()
        # (rt) T-0677: `routes` prints the resolved routes of the cwd repo, or says there are none
        cwd = os.getcwd()
        try:
            os.chdir(rt)
            (rt / 'AGENTS.md').write_text(RT_ROUTE, encoding='utf-8')
            r1 = run_main(['routes'])
            r2 = run_main(['routes', 'src/styles/a.css', 'src/other.css'])
            (rt / 'AGENTS.md').write_text('# Repo\n', encoding='utf-8')
            r3 = run_main(['routes'])
            r4 = run_main(['routes', 'src/styles/a.css'])
        finally:
            os.chdir(cwd)
        check('(rt) T-0677: routes prints one <glob> -> <skill> line, and the skill per routed path',
              r1 == (0, 'src/styles/ -> .agents/skills/recipe/SKILL.md\n', '')
              and r2 == (0, 'src/styles/a.css: .agents/skills/recipe/SKILL.md\nsrc/other.css: none\n', ''))
        check('(rt) T-0677: routes in a repo with no route prints no skill routes and none per path',
              r3 == (0, 'no skill routes\n', '') and r4 == (0, 'src/styles/a.css: none\n', ''))
        (rt / 'AGENTS.md').write_text(RT_ROUTE, encoding='utf-8')
        rc, out, err = rt_lint('rt-bad', RT_ROUTE, rt_step)
        check('(rt) lint refuses a step that edits a routed path without its skill under ### Read first',
              rc == 1 and 'plan defect: edits routed path src/styles/a.css ' + RT_MSG in err)
        rc, out, err = rt_lint('rt-ok', RT_ROUTE, rt_read)
        check('(rt) lint accepts the same step listing the routed skill', rc == 0 and 'steps lint: ok' in out)
        rc, out, err = rt_lint('rt-none', '# Repo\n\n- `src/styles/` holds styles.\n', rt_step)
        check('(rt) control: a repo with no routing lines lints the same step clean',
              rc == 0 and 'steps lint: ok' in out)

        # (s) T-0271: a path a verifier or builder result named on a `plan defect:` line must appear in
        # a ## Step block of the plan, else lint and split refuse (the contract dependents rule)
        (r / 'sub' / 'dependencies.json').write_text('{}\n', encoding='utf-8')
        DEP = 'sub/dependencies.json'
        s_names = PLAN.replace('Do two.', f'Do two. Also update `{DEP}`.')

        def s_task(plan, files):
            count[0] += 1
            d = r / '.sdlc' / f's{count[0]}'
            d.mkdir(parents=True)
            (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
            (d / 'planner-L2.md').write_text(hdr('planner-L2.md', plan), encoding='utf-8')
            for name, text in files:
                (d / name).parent.mkdir(exist_ok=True)
                (d / name).write_text(hdr(pathlib.Path(name).name, text), encoding='utf-8')
            return d

        def s_defect(line, kind='verifier'):
            if kind == 'verifier':
                return f'## Verdict\nfail\n\n## For the next attempt\n\n{line}\nwiden the step\n'
            return f'## Status\nblocked\n\n## Notes\n{line}\n'

        V_OLD = 'step-1.superseded-1/verifier-L1.md'
        for what, line in (('a bare path', f'plan defect: step 3 failed on {DEP}'),
                           ('a backticked path with a period and :line', f'plan defect: `{DEP}:12`.'),
                           ('a path in a longer line', f'plan defect: c1 and/or c2 and pass/fail; {DEP}, gone/x.json')):
            d = s_task(PLAN, [(V_OLD, s_defect(line))])
            rc, out, err = run_main(['lint', str(d)])
            lines = err.strip().splitlines()
            check(f'(s) lint refuses a plan that omits {what} a verifier named on a plan defect: line',
                  rc == 1 and out == '' and f'no step names {DEP}, which {V_OLD} flagged' in err
                  and err.count('no step names') == 1 and 'and/or' not in err and 'gone/x.json' not in err
                  and lines[-1].startswith('plan defect'))
            refused(f'(s) split refuses it too and writes nothing ({what})', ['split', str(d)], d, DEP)
        d = s_task(PLAN, [(V_OLD, s_defect(f'plan defect: {DEP}'))])
        rc, out, err = run_main(['lint', str(d)])
        check('(s) the finding is advice for the planner: put the path in a step',
              'name it in the Do and the scope criterion' in err)
        d = s_task(PLAN, [('step-2.superseded-1/builder-L2.md', s_defect(f'plan defect: {DEP} is stale', 'builder'))])
        rc, out, err = run_main(['lint', str(d)])
        check('(s) lint reads builder-*.md as well as verifier-*.md',
              rc == 1 and f'no step names {DEP}, which step-2.superseded-1/builder-L2.md flagged' in err)
        d = s_task(PLAN, [('step-1/verifier-L1.md', s_defect(f'plan defect: {DEP}'))])
        rc, out, err = run_main(['lint', str(d)])
        check('(s) lint reads a live step-<n>/ result, not only a superseded one',
              rc == 1 and f'no step names {DEP}, which step-1/verifier-L1.md flagged' in err)
        d = s_task(PLAN, [(V_OLD, s_defect(f'plan defect: {DEP}')),
                          ('step-2.superseded-1/builder-L2.md', s_defect(f'plan defect: {DEP}', 'builder'))])
        rc, out, err = run_main(['lint', str(d)])
        check('(s) one finding per path across results', rc == 1 and err.count('no step names') == 1)

        # the positive controls: naming the path in a step, or holding no token, passes and splits
        d = s_task(s_names, [(V_OLD, s_defect(f'plan defect: {DEP}'))])
        rc, out, err = run_main(['lint', str(d)])
        check('(s) lint accepts a plan whose step names the flagged path', rc == 0 and 'steps lint: ok' in out)
        rc, out, _ = run_main(['split', str(d)])
        check('(s) split writes the steps for a plan that names the flagged path',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and (d / 'step-2' / 'handoff.md').is_file())
        for what, line in (('no token', 'plan defect: c2 contradicts c1'),
                           ('a word that names nothing on disk', 'plan defect: and/or pass/fail gone/x.json'),
                           ('a path outside the repo', 'plan defect: ../outside.json /etc/hosts'),
                           ('a url', 'plan defect: https://example.com/a.json')):
            d = s_task(PLAN, [(V_OLD, s_defect(line))])
            rc, out, err = run_main(['lint', str(d)])
            check(f'(s) a plan defect: line with {what} adds no finding', rc == 0 and 'steps lint: ok' in out)
        d = s_task(PLAN, [(V_OLD, f'## Verdict\nfail\n\n## For the next attempt\n\nfix it, see {DEP}\n'
                                  f'not a plan defect: {DEP}\n')])
        rc, out, err = run_main(['lint', str(d)])
        check('(s) only a line that starts with plan defect: counts', rc == 0 and 'steps lint: ok' in out)

        # the negative control: the path named outside every ## Step block (## Risks) is still a finding
        d = s_task(PLAN.replace('RISKTEXT must not leak', f'RISKTEXT {DEP}'),
                   [(V_OLD, s_defect(f'plan defect: {DEP}'))])
        rc, out, err = run_main(['lint', str(d)])
        check('(s) a path named only outside the ## Step blocks is still a finding',
              rc == 1 and f'no step names {DEP}' in err)

        # next: the /chain step 4 action from the newest results, by recorded run order
        DONE, BLOCKED = '## Status\ndone\n', '## Status\nblocked\n\n## Notes\nplan defect: c1 bad\n'
        PASS = '## Verdict\npass\n\n## For the next attempt\nNone\n'
        FAIL = '## Verdict\nfail\n\n## For the next attempt\nfix x\n'
        DEFECT = '## Verdict\nfail\n\n## For the next attempt\n\nplan defect: c2 contradicts c1\n'

        def step(level, files=(), handoff=True):
            """files: (name, text) in run order; each is recorded in runs.jsonl with a file field."""
            count[0] += 1
            d = tmp / f'step{count[0]}'
            d.mkdir()
            if handoff:
                (d / 'handoff.md').write_text(f'## Task goal\ng\n\n## Step 1: x\nlevel: L{level}\n',
                                              encoding='utf-8')
            for name, text in files:
                (d / name).write_text(hdr(name, text), encoding='utf-8')
            if files:
                (d / 'runs.jsonl').write_text(''.join(f'{{"file": "{n}"}}\n' for n, _ in files),
                                              encoding='utf-8')
            return d

        def nxt(d, want):
            rc, out, err = run_main(['next', str(d)])
            lines = out.splitlines()
            return (rc == 0 and err == '' and lines[:1] == [want] and len(lines) >= 2
                    and lines[1].startswith('reason: ') and all(x.startswith('read: ') for x in lines[2:]))

        check('next build: no results -> build at the handoff level',
              nxt(step(2), 'build L2'))
        check('next verify: build L2 done, no verifier -> verify L1',
              nxt(step(2, [('builder-L2.md', DONE)]), 'verify L1'))
        check('next verify: build L4 done, no verifier -> verify L3',
              nxt(step(4, [('builder-L4.md', DONE)]), 'verify L3'))
        check('next verify: build L3 done, no verifier -> verify L2',
              nxt(step(3, [('builder-L3.md', DONE)]), 'verify L2'))
        check('next replan: a blocked builder with no amend pair replans',
              nxt(step(2, [('builder-L2.md', BLOCKED)]), 'replan'))
        STALE = '## Status\nblocked\n\n## Notes\nstale lane: T-0042 is not merged into this lane\n'
        rc, out, err = run_main(['next', str(step(2, [('builder-L2.md', STALE)]))])
        check('next resplit: a blocked builder whose Notes start "stale lane:" routes to resplit, not replan, '
              'naming .superseded and split --only',
              rc == 0 and out.splitlines()[:1] == ['resplit'] and '.superseded-' in out and 'split --only' in out)
        check('next replan: a fail whose next-attempt note starts "plan defect:" replans',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', DEFECT)]), 'replan'))
        check('next done: the newest verifier passed',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', PASS)]), 'done'))
        check('next rebuild: one counted fail -> rebuild at the same level',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL)]), 'rebuild L2'))
        check('next bump: two counted fails at L2 -> bump L3',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', FAIL)]), 'bump L3'))
        check('next rebuild after a bump: fails at L2 do not count at L3 -> rebuild L3',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', FAIL),
                           ('builder-L3.md', DONE), ('verifier-L2.md', FAIL)]), 'rebuild L3'))
        check('next plan-defect fails are not counted: defect then fail at L2 -> rebuild L2',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', DEFECT),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', FAIL)]), 'rebuild L2'))
        check('next stop: two counted fails at L5 -> stop',
              nxt(step(5, [('builder-L5.md', DONE), ('verifier-L3.md', FAIL),
                           ('builder-L5-2.md', DONE), ('verifier-L3-2.md', FAIL)]), 'stop'))
        check('next verify: a stale verifier older than the rebuild -> verify L1',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', DONE)]), 'verify L1'))
        NOVERDICT = 'Nothing to do until the test gate reports.\n'
        check('next reverify: a verifier with no verdict -> reverify at its level',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', NOVERDICT)]), 'reverify L1'))
        check('next stop: two consecutive no-verdict verifiers after the build -> stop',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', NOVERDICT),
                           ('verifier-L1-2.md', '## Notes\nhm\n')]), 'stop'))
        check('next rebuild: no verdict then a real fail at L2 -> rebuild L2 (no-verdict not counted)',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', NOVERDICT),
                           ('verifier-L1-2.md', FAIL)]), 'rebuild L2'))
        check('next done: no verdict then a pass -> done',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', NOVERDICT),
                           ('verifier-L1-2.md', PASS)]), 'done'))
        check('next reverify: fail, rebuild, fail, then no verdict at L2 -> reverify L1, not bump',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', FAIL),
                           ('verifier-L1-3.md', NOVERDICT)]), 'reverify L1'))
        check('next rebuild: a builder with no done/blocked Status -> rebuild L2, not an error',
              nxt(step(2, [('builder-L2.md', '## Status\nmaybe\n')]), 'rebuild L2'))
        check('next stop: two consecutive builders with no Status -> stop',
              nxt(step(2, [('builder-L2.md', 'Waiting.\n'), ('builder-L2-2.md', 'Waiting.\n')]), 'stop'))
        check('next verify: a statusless builder then a done builder -> verify L1',
              nxt(step(2, [('builder-L2.md', 'Waiting.\n'), ('builder-L2-2.md', DONE)]), 'verify L1'))
        INHERITED = '## Status\ninherited red: test_a\n'
        check('next inherited: newest builder reports inherited red -> inherited',
              nxt(step(2, [('builder-L2.md', INHERITED)]), 'inherited'))
        check('next inherited: an inherited builder then a done builder -> verify L1',
              nxt(step(2, [('builder-L2.md', INHERITED), ('builder-L2-2.md', DONE)]), 'verify L1'))
        check('next inherited: done, fail, then inherited -> inherited, not rebuild or bump',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', INHERITED)]), 'inherited'))
        check('next inherited: "inherited red" with no colon is statusless -> rebuild L2',
              nxt(step(2, [('builder-L2.md', '## Status\ninherited red\n')]), 'rebuild L2'))
        V_INHERITED = '## Verdict\ninherited red: test_a\n'
        check('next inherited: done builder, then verifier inherited red: <tests> -> inherited',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', V_INHERITED)]), 'inherited'))
        check('next reverify: verifier "inherited red" with no colon is no verdict -> reverify L1',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', '## Verdict\ninherited red\n')]),
                  'reverify L1'))
        check('next inherited: done, fail, rebuild, then an inherited verifier -> inherited, not bump',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', V_INHERITED)]), 'inherited'))
        check('next rebuild: an inherited verifier, rebuild, then a fail at L2 -> rebuild L2 (inherited not a fail)',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', V_INHERITED),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', FAIL)]), 'rebuild L2'))
        check('next rebuild: a fail verifier still -> rebuild L2',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL)]), 'rebuild L2'))
        # order comes from runs.jsonl, never from file times: times set inverse to the run order
        d = step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL), ('builder-L2-2.md', DONE)])
        for i, name in enumerate(('builder-L2-2.md', 'verifier-L1.md', 'builder-L2.md')):
            t = 1_700_000_000 + i * 100
            os.utime(d / name, (t, t))
        check('next verify: file times are ignored, runs.jsonl decides', nxt(d, 'verify L1'))

        def next_refused(name, d):
            root = d if d.is_dir() else tmp
            before = snapshot(root)
            rc, out, err = run_main(['next', str(d)])
            check(name, rc == 1 and out == '' and err.startswith('steps next: ')
                  and len(err.strip().splitlines()) == 1 and snapshot(root) == before)

        next_refused('next error: a dir that does not exist', tmp / 'no-such-step')
        next_refused('next error: no handoff.md and no builder result', step(2, handoff=False))
        d = step(2)
        (d / 'handoff.md').write_text('## Task goal\ng\n\n## Step 1: x\n', encoding='utf-8')
        next_refused('next error: a handoff with no level line and no builder result', d)

        # SDLC_BASE_SHA: split --only sets it to HEAD at the toplevel, never inherited from the caller
        d = o_repo('(guard) `test "$SDLC_BASE_SHA" = "$(git rev-parse HEAD)"`', commit='o-base')
        saved = os.environ.get('SDLC_BASE_SHA')
        os.environ['SDLC_BASE_SHA'] = 'inherited-bogus'
        try:
            rc, _, err = run_main(['split', str(d), '--only', '1'])
        finally:
            if saved is None:
                os.environ.pop('SDLC_BASE_SHA', None)
            else:
                os.environ['SDLC_BASE_SHA'] = saved
        check('(o) split --only runs a guard with SDLC_BASE_SHA = HEAD, overriding the caller env',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file())
        p = tmp / 'base-lint.md'
        p.write_text(guard_plan('`git diff --name-only "$SDLC_BASE_SHA"`'), encoding='utf-8')
        rc, out, _ = run_main(['lint', str(p)])
        check('lint does not flag git diff --name-only "$SDLC_BASE_SHA" as pinning a sha',
              rc == 0 and out.strip() == 'steps lint: ok')

        d = step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL)])
        before = snapshot(d)
        rc, _, _ = run_main(['next', str(d)])
        check('next writes nothing: the step dir snapshot is equal before and after',
              rc == 0 and snapshot(d) == before)

        # resume: the lowest-numbered non-superseded step whose next action is not done
        def r_task(steps_files):
            """steps_files: {dir name: [(name, text)] in run order}; each dir gets an L2 handoff."""
            count[0] += 1
            t = tmp / f'resume{count[0]}'
            t.mkdir()
            for name, files in steps_files.items():
                d = t / name
                d.mkdir()
                (d / 'handoff.md').write_text('## Task goal\ng\n\n## Step 1: x\nlevel: L2\n', encoding='utf-8')
                for fname, text in files:
                    (d / fname).write_text(hdr(fname, text), encoding='utf-8')
                if files:
                    (d / 'runs.jsonl').write_text(''.join(f'{{"file": "{n}"}}\n' for n, _ in files),
                                                  encoding='utf-8')
            return t

        def rsm(t):
            before = snapshot(t)
            rc, out, err = run_main(['resume', str(t)])
            return rc, out.splitlines(), err, snapshot(t) == before

        PASSED = [('builder-L2.md', DONE), ('verifier-L1.md', PASS)]
        t = r_task({'step-1': PASSED, 'step-2': [('builder-L2.md', BLOCKED)],
                    'step-3': [('builder-L2.md', DONE)]})
        rc, lines, err, same = rsm(t)
        check('resume: a blocked step-2 is chosen over a later step-3 with a done builder',
              rc == 0 and err == '' and same and lines[:2] == [str(t / 'step-2'), 'replan']
              and len(lines) >= 3 and lines[2].startswith('reason: ')
              and lines[3:] == [f'read: {t / "step-2" / "builder-L2.md"}'])
        t = r_task({'step-1': PASSED, 'step-2': PASSED})
        rc, lines, err, same = rsm(t)
        check('resume: every step passed prints done',
              rc == 0 and err == '' and same and lines == ['done', 'reason: every step-<n>/ passed'])
        t = r_task({'step-1': PASSED, 'step-2': [], 'step-10': [],
                    'step-2.superseded-1': [('builder-L2.md', BLOCKED)]})
        rc, lines, err, same = rsm(t)
        check('resume: a superseded dir is ignored and step-2 comes before step-10',
              rc == 0 and err == '' and same and lines[:2] == [str(t / 'step-2'), 'build L2'])
        t = r_task({'step-1': PASSED, 'step-10': [('builder-L2.md', BLOCKED)], 'step-2.superseded-1': []})
        rc, lines, err, same = rsm(t)
        check('resume: step-10 is reached after step-1 when only a superseded step-2 exists',
              rc == 0 and same and lines[:2] == [str(t / 'step-10'), 'replan'])
        t = r_task({})
        rc, lines, err, same = rsm(t)
        check('resume error: no step dirs exits 1 with "steps resume:" on stderr',
              rc == 1 and lines == [] and err.startswith('steps resume: ') and 'split' in err
              and len(err.strip().splitlines()) == 1 and same)
        rc, out, err = run_main(['resume', str(tmp / 'no-such-task')])
        check('resume error: a missing task dir exits 1 with "steps resume:" on stderr',
              rc == 1 and out == '' and err.startswith('steps resume: ') and len(err.strip().splitlines()) == 1)
        t = r_task({'step-1': PASSED, 'step-2': []})
        (t / 'step-2' / 'handoff.md').write_text('## Task goal\ng\n\n## Step 2: x\n', encoding='utf-8')
        rc, lines, err, same = rsm(t)
        check('resume error: a next error on a candidate exits 1 with one "steps resume:" line',
              rc == 1 and lines == [] and err.startswith('steps resume: ') and 'step-2' in err
              and len(err.strip().splitlines()) == 1 and same)

        # next batch: a task-dir verifier result whose ## Verified section lists a step's newest build
        def b_task(steps=None, task_files=(), superseded=()):
            """steps: {dir name: (title, [(name, text)] in run order)}; task_files: task-dir results in
            run order, recorded in the task dir's runs.jsonl."""
            count[0] += 1
            t = tmp / f'batch{count[0]}'
            t.mkdir()
            if steps is None:
                steps = {'step-1': ('a', [('builder-L2.md', DONE)]),
                         'step-2': ('b', [('builder-L2.md', DONE)]),
                         'step-3': ('c', [('builder-L2.md', DONE), ('verifier-L1.md', PASS)])}
            for name, (title, files) in steps.items():
                d = t / name
                d.mkdir()
                n = name.split('-')[1]
                (d / 'handoff.md').write_text(f'## Task goal\ng\n\n## Step {n}: {title}\nlevel: L2\n',
                                              encoding='utf-8')
                for fname, text in files:
                    (d / fname).write_text(hdr(fname, text), encoding='utf-8')
                if files:
                    (d / 'runs.jsonl').write_text(''.join(f'{{"file": "{f}"}}\n' for f, _ in files),
                                                  encoding='utf-8')
            for name in superseded:
                (t / name).mkdir()
            for fname, text in task_files:
                (t / fname).write_text(hdr(fname, text), encoding='utf-8')
            if task_files:
                (t / 'runs.jsonl').write_text(''.join(f'{{"file": "{f}"}}\n' for f, _ in task_files),
                                              encoding='utf-8')
            return t

        def listing(paths, verdict='pass'):
            items = ''.join(f'- `{p}`\n' if i % 2 else f'- {p}\n' for i, p in enumerate(paths))
            return f'## Verdict\n{verdict}\n\n## For the next attempt\nNone\n\n## Verified\n{items}'

        BOTH = listing(['step-1/builder-L2.md', 'step-2/builder-L2.md'])
        t = b_task(task_files=[('verifier-L3.md', BOTH)])
        rc, out, err = run_main(['next', str(t / 'step-2')])
        lines = out.splitlines()
        rc2, lines2, err2, same = rsm(t)
        check('next batch: a listed unchanged step is done, and resume prints done',
              rc == 0 and err == '' and lines[:1] == ['done']
              and lines[1:2] == ['reason: batch verifier verifier-L3.md lists step-2/builder-L2.md with Verdict pass']
              and lines[2:] == [f'read: {t / "step-2" / "builder-L2.md"}', f'read: {t / "verifier-L3.md"}']
              and nxt(t / 'step-1', 'done') and rc2 == 0 and same
              and lines2 == ['done', 'reason: every step-<n>/ passed'])
        newer = [('builder-L2-2.md', DONE), ('builder-L2.md', DONE)]
        t = b_task({'step-1': ('a', [('builder-L2.md', DONE)]), 'step-2': ('b', newer), 'step-3': ('c', [])},
                   [('verifier-L3.md', listing(['step-2/builder-L2-2.md']))])
        check('next batch: a listing of an older build (order.py, not the -2 name) -> verify',
              nxt(t / 'step-2', 'verify L1'))
        t = b_task({'step-1': ('a', [('builder-L2.md', DONE)]), 'step-2': ('b', newer), 'step-3': ('c', [])},
                   [('verifier-L3.md', listing(['step-2/builder-L2.md']))])
        check('next batch: a listing of the newest build by order.py -> done',
              nxt(t / 'step-2', 'done'))
        t = b_task(task_files=[('verifier-L3.md', listing(['step-1/builder-L2.md']))])
        check('next batch: an unlisted step -> verify', nxt(t / 'step-2', 'verify L1')
              and nxt(t / 'step-1', 'done'))
        for lv in (4, 5):
            t = b_task({'step-1': ('a', []), 'step-2': ('b', [(f'builder-L{lv}.md', DONE)]), 'step-3': ('c', [])},
                       [('verifier-L3.md', listing([f'step-2/builder-L{lv}.md']))])
            check(f'next batch: an L{lv} build is never batch-verified -> verify L3',
                  nxt(t / 'step-2', 'verify L3'))
        for title in ('Merge lane-a', 'Docs and Gates Green'):
            t = b_task({'step-1': ('a', []), 'step-2': (title, [('builder-L2.md', DONE)]), 'step-3': ('c', [])},
                       [('verifier-L3.md', BOTH)])
            check(f'next batch: a step titled "{title}" -> verify', nxt(t / 'step-2', 'verify L1'))
        t = b_task({'step-1': ('a', [('builder-L2.md', DONE)]), 'step-2': ('b', [('builder-L2.md', DONE)])},
                   [('verifier-L3.md', BOTH)])
        check('next batch: the highest-numbered live step -> verify', nxt(t / 'step-2', 'verify L1')
              and nxt(t / 'step-1', 'done'))
        t = b_task(task_files=[('verifier-L3.md', BOTH)], superseded=['step-2.superseded-1'])
        check('next batch: a step with a superseded sibling -> verify', nxt(t / 'step-2', 'verify L1')
              and nxt(t / 'step-1', 'done'))
        t = b_task(task_files=[('verifier-L3.md', listing(['step-2/builder-L2.md'], 'fail'))])
        check('next batch: a listing with Verdict fail -> verify', nxt(t / 'step-2', 'verify L1'))
        FAIL_LIST = listing(['step-2/builder-L2.md'], 'fail')
        t = b_task(task_files=[('verifier-L3-2.md', BOTH), ('verifier-L3.md', FAIL_LIST)])
        check('next batch: a newer fail listing (order.py) overrides an older pass listing -> verify',
              nxt(t / 'step-2', 'verify L1') and nxt(t / 'step-1', 'done'))
        t = b_task(task_files=[('verifier-L3-2.md', FAIL_LIST), ('verifier-L3.md', BOTH)])
        check('next batch: a newer pass listing overrides an older fail listing -> done',
              nxt(t / 'step-2', 'done'))
        t = b_task(task_files=[('verifier-L3.md', listing(['step-1/builder-L2.md'])),
                               ('verifier-L3-2.md', listing(['step-2/builder-L2.md']))])
        check('next batch: two batches over disjoint steps both count', nxt(t / 'step-1', 'done')
              and nxt(t / 'step-2', 'done'))
        bad = '<!-- role=builder level=L3 model=opus effort=low -->\n' + BOTH
        t = b_task(task_files=[('verifier-L3.md', bad)])
        check('next batch: a structurally invalid task verifier result -> verify',
              nxt(t / 'step-2', 'verify L1'))
        t = b_task({'step-1': ('a', []), 'step-2': ('b', [('builder-L2.md', DONE), ('verifier-L1.md', FAIL)]),
                    'step-3': ('c', [])}, [('verifier-L3.md', BOTH)])
        check('next batch: a per-step fail counting after the build wins over a pass listing -> rebuild',
              nxt(t / 'step-2', 'rebuild L2'))

        # amend: a blocked builder's plan-defect note proposes one criterion amend for an unbuilt step;
        # steps.py amend applies it and records it as the task's one replan, next routes to it.
        A_OLD = 'test -f zzz-amend-old'
        A_HANDOFF = ('## Task goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nd\n### Acceptance criteria\n'
                     '- (guard) `test -d .`\n- `' + A_OLD + '` (old check)\n- prose line\n')
        A_NEW = '`test -f zzz-amend-new` (new check)'

        def amend_b(old=A_OLD, new=A_NEW):
            return (f'## Status\nblocked\n\n## Notes\nplan defect: c2 names the wrong file\n'
                    f'amend old: `{old}`\namend new: {new}\n')

        def a_task(files, task_files=(), task_handoff='## Goal\ng\n', n=1):
            """A task dir with handoff.md, step-<n>/handoff.md and files in run order; task_files are
            task-dir results in run order."""
            count[0] += 1
            t = tmp / f'amend{count[0]}'
            d = t / f'step-{n}'
            d.mkdir(parents=True)
            (t / 'handoff.md').write_text(task_handoff, encoding='utf-8')
            (d / 'handoff.md').write_text(A_HANDOFF, encoding='utf-8')
            for where, fs in ((d, files), (t, task_files)):
                for name, text in fs:
                    (where / name).write_text(hdr(name, text), encoding='utf-8')
                if fs:
                    (where / 'runs.jsonl').write_text(''.join(f'{{"file": "{x}"}}\n' for x, _ in fs),
                                                      encoding='utf-8')
            return t, d

        def amend_refused(t, d, needle):
            before_h, before_t = ((x / 'handoff.md').read_text(encoding='utf-8') for x in (d, t))
            rc, out, err = run_main(['amend', str(d)])
            last = err.strip().splitlines()[-1] if err.strip() else ''
            return (rc == 1 and out == '' and needle in err
                    and last.startswith('plan defect: steps amend refused:')
                    and last.endswith('; replan this step (/chain 4.2)')
                    and (d / 'handoff.md').read_text(encoding='utf-8') == before_h
                    and (t / 'handoff.md').read_text(encoding='utf-8') == before_t)

        t, d = a_task([('builder-L2.md', amend_b())])
        rc, out, err = run_main(['amend', str(d)])
        want = A_HANDOFF.replace(f'- `{A_OLD}` (old check)', f'- {A_NEW}')
        task_text = (t / 'handoff.md').read_text(encoding='utf-8')
        first_ok = (rc == 0 and err == '' and (d / 'handoff.md').read_text(encoding='utf-8') == want
                    and out.strip() == f'steps amend: {d}: old `{A_OLD}` -> new {A_NEW}'
                    and task_text == f'## Goal\ng\n\n## Plan review\n- amend applied: step 1: old `{A_OLD}` -> new {A_NEW}\n')
        before = snapshot(t)
        rc, out, err = run_main(['amend', str(d)])
        check('(amend) applies one criterion',
              first_ok and rc == 0 and out.strip() == 'amend: already applied' and snapshot(t) == before)
        # a (red) line: a new span green now refuses; a (guard) line: a new span red now refuses
        R_A = A_HANDOFF.replace('- `' + A_OLD + '`', '- (red) `' + A_OLD + '`')
        t, d = a_task([('builder-L2.md', amend_b(new='(red) `test -f handoff.md` (new check)'))])
        (d / 'handoff.md').write_text(R_A, encoding='utf-8')
        red_green = amend_refused(t, d, '(red) green now')
        t, d = a_task([('builder-L2.md', amend_b('test -d .', '(guard) `test -f zzz-none`'))])
        guard_red = amend_refused(t, d, '(guard) red now')
        t, d = a_task([('builder-L2.md', amend_b(new='(red) `test -f zzz-amend-new` (new check)'))])
        (d / 'handoff.md').write_text(R_A, encoding='utf-8')
        rc, _, _ = run_main(['amend', str(d)])
        check('(amend) a (red) line runs its new spans red-first, a (guard) line green, a plain line not at all',
              red_green and guard_red and rc == 0 and first_ok)
        check('(amend) refuses: the step is already built',
              amend_refused(*a_task([('builder-L2.md', DONE), ('builder-L2-2.md', amend_b())]), 'already built')
              and amend_refused(*a_task([('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                                         ('builder-L2-2.md', amend_b())]), 'already built')
              and amend_refused(*a_task([('verifier-L1.md', FAIL), ('builder-L2.md', amend_b())]),
                                'already built'))
        A_PLAN = '## Steps\n## Step 1: x\nlevel: L2\n'
        other = '## Goal\ng\n\n## Plan review\n- amend applied: step 2: old `x` -> new `y`\n'
        check('(amend) refuses: the task already used its one replan',
              amend_refused(*a_task([('builder-L2.md', amend_b())],
                                    [('planner-L2.md', A_PLAN), ('planner-L3.md', A_PLAN)]),
                            'already used its one replan')
              and amend_refused(*a_task([('builder-L2.md', amend_b())], task_handoff=other),
                                'already used its one replan'))
        check('(amend) refuses: one amend per step, a note with no pair, a note that is not a plan defect',
              amend_refused(*a_task([('builder-L2.md', amend_b()), ('builder-L2-2.md', amend_b())]),
                            'one amend per step')
              and amend_refused(*a_task([('builder-L2.md', BLOCKED)]), 'no single amend old:')
              and amend_refused(*a_task([('builder-L2.md', amend_b().replace('plan defect:', 'other:'))]),
                                'plan defect:'))

        def a_next(d, want):
            rc, out, err = run_main(['next', str(d)])
            return rc == 0 and out.splitlines()[:1] == [want]
        t, d = a_task([('builder-L2.md', amend_b())])
        routes = a_next(d, 'amend L2')
        run_main(['amend', str(d)])
        routes = routes and a_next(d, 'rebuild L2')
        t, d = a_task([('builder-L2.md', amend_b())], [('planner-L2.md', A_PLAN), ('planner-L3.md', A_PLAN)])
        routes = routes and a_next(d, 'replan')
        t, d = a_task([('builder-L2.md', amend_b())], task_handoff=other)
        routes = routes and a_next(d, 'replan')
        t, d = a_task([('builder-L2.md', amend_b()), ('builder-L2-2.md', amend_b())])
        routes = routes and a_next(d, 'replan')
        t, d = a_task([('builder-L2.md', DONE), ('builder-L2-2.md', amend_b())])
        check('(amend) next routes', routes and a_next(d, 'replan'))

        # swap: a verifier's plan-defect fail proposes one criterion swap; steps.py swap applies it
        # after every check, next routes to it. Spans run from the step dir (tmp is outside git).
        S_OLD = 'test -f zzz-old'
        S_HANDOFF = ('## Task goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nd\n### Acceptance criteria\n'
                     '- (guard) `test -d .`\n  * `' + S_OLD + '` (old check)\n- prose line\n')

        def swap_v(old=S_OLD, new='`test -f handoff.md` (new check)', extra='', tag='plan defect: c bad\n'):
            return (f'## Verdict\nfail\n\n## For the next attempt\n{tag}swap old: `{old}`\n'
                    f'swap new: {new}\n{extra}')

        def s_step(files, handoff=S_HANDOFF, where=None):
            d = step(2, files) if where is None else where
            (d / 'handoff.md').write_text(handoff, encoding='utf-8')
            return d

        def swap_refused(name, d, needle=None):
            before = snapshot(d)
            rc, out, err = run_main(['swap', str(d)])
            last = err.strip().splitlines()[-1] if err.strip() else ''
            check(f'swap: {name}', rc == 1 and out == '' and snapshot(d) == before
                  and last.startswith('plan defect:') and last.endswith('; replan this step (/chain 4.2)')
                  and (needle is None or needle in err))

        # (a) a pair applies: only the target line changes, its indent and marker are kept
        d = s_step([('builder-L2.md', DONE), ('verifier-L1.md', swap_v())])
        rc, out, err = run_main(['swap', str(d)])
        want = S_HANDOFF.replace(f'  * `{S_OLD}` (old check)', '  * `test -f handoff.md` (new check)')
        check('swap: (a) a pair applies: only the target line changes, marker, indent, and the (guard) '
              'sibling kept, stdout names old and new',
              rc == 0 and err == '' and (d / 'handoff.md').read_text(encoding='utf-8') == want
              and S_OLD in out and 'test -f handoff.md' in out and len(out.splitlines()) == 1)
        # solo task dir: solo-L2.md stands in for the builder; the ticket's ## Acceptance criteria is the region
        solo_h = ('---\nid: T-0001\n---\n\n## Goal\ng\n\n## Acceptance criteria\n- `' + S_OLD
                  + '` (old check)\n- prose line\n\n## Context\n- `' + S_OLD + '` named here is not a criterion\n')
        count[0] += 1
        sd = tmp / f'solo{count[0]}'
        sd.mkdir()
        (sd / 'handoff.md').write_text(solo_h, encoding='utf-8')
        for name, text in (('solo-L2.md', '## Status\ndone\n'), ('verifier-L2.md', swap_v())):
            (sd / name).write_text(hdr(name, text), encoding='utf-8')
        (sd / 'runs.jsonl').write_text('{"file": "solo-L2.md"}\n{"file": "verifier-L2.md"}\n', encoding='utf-8')
        rc, out, err = run_main(['swap', str(sd)])
        check('swap: a solo task dir with solo-L2.md and a plan-defect verifier fail applies the swap '
              'to its ## Acceptance criteria line only',
              rc == 0 and (sd / 'handoff.md').read_text(encoding='utf-8')
              == solo_h.replace(f'- `{S_OLD}` (old check)', '- `test -f handoff.md` (new check)'))
        (sd / 'solo-L2.md').unlink()
        (sd / 'handoff.md').write_text(solo_h, encoding='utf-8')
        swap_refused('a task dir with neither a builder nor a solo result refuses', sd, needle='solo')
        # (b) already applied: rerun on the swapped handoff exits 0 and writes nothing
        before = snapshot(d)
        rc, out, err = run_main(['swap', str(d)])
        check('swap: (b) already applied: exit 0, prints swap: already applied, writes nothing',
              rc == 0 and out.strip() == 'swap: already applied' and snapshot(d) == before)
        # a guard line swapped for a guard line applies
        g = S_HANDOFF.replace('(guard) `test -d .`', '(guard) `test -d zzz-nodir`')
        d = s_step([('builder-L2.md', DONE),
                    ('verifier-L1.md', swap_v('test -d zzz-nodir', '(guard) `test -f handoff.md`'))], g)
        rc, _, _ = run_main(['swap', str(d)])
        check('swap: (a) a (guard) line swapped for a (guard) line applies',
              rc == 0 and (d / 'handoff.md').read_text(encoding='utf-8')
              == g.replace('(guard) `test -d zzz-nodir`', '(guard) `test -f handoff.md`'))

        # (c) refusals: each writes nothing and ends with a plan defect line
        pair = [('builder-L2.md', DONE)]
        swap_refused('(c) old span in no criterion line',
                     s_step(pair + [('verifier-L1.md', swap_v('test -f zzz-missing'))]), 'no criterion line')
        swap_refused('(c) old span in two criterion lines',
                     s_step(pair + [('verifier-L1.md', swap_v())], S_HANDOFF + f'- again `{S_OLD}`\n'),
                     '2 criterion lines')
        swap_refused('(c) tag mismatch: a plain line swapped for a (guard) text',
                     s_step(pair + [('verifier-L1.md', swap_v(new='(guard) `test -f handoff.md`'))]), '(guard)')
        swap_refused('(c) tag mismatch: a (guard) line swapped for a plain text',
                     s_step(pair + [('verifier-L1.md', swap_v('test -d .', '`test -f handoff.md`'))]), '(guard)')
        R_HANDOFF = S_HANDOFF.replace('  * `' + S_OLD + '`', '  * (red) `' + S_OLD + '`')
        swap_refused('(c) tag mismatch: a (red) line swapped for a plain text drops the (red) tag',
                     s_step(pair + [('verifier-L1.md', swap_v(new='`test -f handoff.md`'))], handoff=R_HANDOFF),
                     '(red)')
        swap_refused('(c) tag mismatch: a plain line swapped for a (red) text adds a (red) tag',
                     s_step(pair + [('verifier-L1.md', swap_v(new='(red) `test -f handoff.md`'))]), '(red)')
        d = s_step(pair + [('verifier-L1.md', swap_v(new='(red) `test -f handoff.md` (new check)'))],
                   handoff=R_HANDOFF)
        rc, out, err = run_main(['swap', str(d)])
        check('swap: (a) a (red) line swapped for a (red) text applies and keeps the tag',
              rc == 0 and err == ''
              and '  * (red) `test -f handoff.md` (new check)' in (d / 'handoff.md').read_text(encoding='utf-8'))
        swap_refused('(c) new text with no command span',
                     s_step(pair + [('verifier-L1.md', swap_v(new='the file exists'))]), 'no runnable')
        swap_refused('(c) new span with an unquoted || join',
                     s_step(pair + [('verifier-L1.md', swap_v(new='`test -f a || test -f handoff.md`'))]),
                     'joins two checks with ||')
        swap_refused('(c) new span with a <placeholder>',
                     s_step(pair + [('verifier-L1.md', swap_v(new='`test -f <tmp>/handoff.md`'))]),
                     '<placeholder>')
        swap_refused('(c) new span red now',
                     s_step(pair + [('verifier-L1.md', swap_v(new='`test -f zzz-new`'))]), 'red now (exit 1)')
        r = tmp / 'swap-repo'
        r.mkdir()
        subprocess.run(['git', 'init', '-q', str(r)], check=True, capture_output=True)
        (r / 'sdlc').mkdir()
        d = s_step([], where=r / 'sdlc')
        for name, text in pair + [('verifier-L1.md', swap_v(new='`touch s-made && test -f s-made`'))]:
            (d / name).write_text(hdr(name, text), encoding='utf-8')
        swap_refused('(c) new span that changes the work tree (a throwaway git repo)', d,
                     'changed the work tree: s-made')
        # a swap span sees SDLC_BASE_SHA from <step dir>/base-sha, not HEAD
        r = tmp / 'swap-base-repo'
        r.mkdir()
        g = ['git', '-C', str(r), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']
        subprocess.run(['git', 'init', '-q', str(r)], check=True, capture_output=True)
        subprocess.run(g + ['commit', '-q', '--allow-empty', '-m', 'a'], check=True, capture_output=True)
        first = subprocess.run(['git', '-C', str(r), 'rev-parse', 'HEAD'], check=True, capture_output=True,
                               text=True).stdout.strip()
        subprocess.run(g + ['commit', '-q', '--allow-empty', '-m', 'b'], check=True, capture_output=True)
        (r / 'sdlc').mkdir()
        d = s_step([], where=r / 'sdlc')
        (d / 'base-sha').write_text(first + '\n', encoding='utf-8')
        new = '`test "$SDLC_BASE_SHA" = "$(head -n 1 sdlc/base-sha)" && test "$SDLC_BASE_SHA" != "$(git rev-parse HEAD)"`'
        for name, text in pair + [('verifier-L1.md', swap_v(new=new))]:
            (d / name).write_text(hdr(name, text), encoding='utf-8')
        rc, out, err = run_main(['swap', str(d)])
        check('swap: a new span sees SDLC_BASE_SHA from the stored base-sha, not HEAD',
              rc == 0 and 'base-sha' in (d / 'handoff.md').read_text(encoding='utf-8'))
        # T-0381: a step dir in the MAIN checkout, the owned lane worktree as the cwd: the span base comes from the lane.
        # Order: a base the handoff names, else the base-sha recorded at the first dispatch, else the lane HEAD; never
        # the main checkout's HEAD.
        main_r = tmp / 'shared-base-repo'
        main_r.mkdir()
        gm = ['git', '-C', str(main_r), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']

        def rev(where, what='HEAD'):
            return subprocess.run(['git', '-C', str(where), 'rev-parse', what], check=True, capture_output=True,
                                  text=True).stdout.strip()
        subprocess.run(['git', 'init', '-q', str(main_r)], check=True, capture_output=True)
        subprocess.run(gm + ['commit', '-q', '--allow-empty', '-m', 'a'], check=True, capture_output=True)
        sb_a = rev(main_r)
        subprocess.run(gm + ['commit', '-q', '--allow-empty', '-m', 'b'], check=True, capture_output=True)
        sb_main = rev(main_r)
        lane_r = tmp / 'shared-base-lane'
        subprocess.run(gm + ['worktree', 'add', '-q', '-b', 'sb-lane', str(lane_r), 'HEAD'], check=True, capture_output=True)
        gl = ['git', '-C', str(lane_r), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']
        subprocess.run(gl + ['commit', '-q', '--allow-empty', '-m', 'l1'], check=True, capture_output=True)
        sb_l1 = rev(lane_r)
        subprocess.run(gl + ['commit', '-q', '--allow-empty', '-m', 'l2'], check=True, capture_output=True)
        sb_l2 = rev(lane_r)
        sb_orphan = subprocess.run(gm + ['commit-tree', rev(main_r, 'HEAD^{tree}'), '-m', 'orphan'], check=True,
                                   capture_output=True, text=True).stdout.strip()
        (main_r / 'sdlc').mkdir()
        sd = s_step([], where=main_r / 'sdlc')
        sd_hand = (sd / 'handoff.md').read_text(encoding='utf-8')

        def shared_base(at):
            here = os.getcwd()
            os.chdir(at)
            try:
                return base_sha(exec_toplevel(sd), sd)
            finally:
                os.chdir(here)
        (sd / 'base-sha').unlink(missing_ok=True)
        check('shared step dir (T-0381): nothing recorded gives the lane HEAD, not the main checkout HEAD',
              shared_base(lane_r) == sb_l2 != sb_main)
        (sd / 'base-sha').write_text(sb_l1 + '\n', encoding='utf-8')
        check('shared step dir (T-0381): a rework keeps the base recorded at the first dispatch (a lane commit)',
              shared_base(lane_r) == sb_l1)
        (sd / 'handoff.md').write_text(sd_hand + f'\nbase: {sb_a}\n', encoding='utf-8')
        check('shared step dir (T-0381): a base the handoff names wins over the recorded one',
              shared_base(lane_r) == sb_a)
        (sd / 'handoff.md').write_text(sd_hand + f'\nbase: {sb_orphan}\n', encoding='utf-8')
        err_buf = io.StringIO()
        with contextlib.redirect_stderr(err_buf):
            got = shared_base(lane_r)
        check('shared step dir (T-0381): a named base that is no ancestor of HEAD is refused loudly and the recorded one kept',
              got == sb_l1 and 'SDLC_BASE_SHA refused' in err_buf.getvalue())
        (sd / 'handoff.md').write_text(sd_hand, encoding='utf-8')
        (sd / 'base-sha').unlink()
        check('shared step dir (T-0381) negative control: from the main checkout the base is the main checkout HEAD',
              shared_base(main_r) == sb_main)
        swap_refused('(c) verifier older than the newest builder',
                     s_step(pair + [('verifier-L1.md', swap_v()), ('builder-L2-2.md', DONE)]), 'older')
        swap_refused('(c) newest verifier a pass', s_step(pair + [('verifier-L1.md', PASS)]), 'no fail verdict')
        swap_refused('(c) a fail with no plan defect',
                     s_step(pair + [('verifier-L1.md', swap_v(tag='fix x\n'))]), 'plan defect:"')
        swap_refused('(c) a plan defect with no pair', s_step(pair + [('verifier-L1.md', DEFECT)]), 'no single')
        two_new = swap_v(extra='swap new: `test -d .`\n')
        swap_refused('(c) two swap new: lines', s_step(pair + [('verifier-L1.md', two_new)]), 'no single')
        swap_refused('(c) a second swap on the step',
                     s_step(pair + [('verifier-L1.md', swap_v()), ('builder-L2-2.md', DONE),
                                    ('verifier-L1-2.md', swap_v())]), 'one swap per step')

        # (d) next routes a plan-defect fail with one pair to swap, else replan
        check('next swap: a plan-defect fail with one pair -> swap L2, reason names steps.py swap',
              nxt(s_step(pair + [('verifier-L1.md', swap_v())]), 'swap L2')
              and 'steps.py swap' in run_main(['next', str(s_step(pair + [('verifier-L1.md', swap_v())]))])[1])
        check('next swap: two swap new: lines -> replan',
              nxt(s_step(pair + [('verifier-L1.md', two_new)]), 'replan'))
        check('next swap: a second swap on the step -> replan',
              nxt(s_step(pair + [('verifier-L1.md', swap_v()), ('builder-L2-2.md', DONE),
                                 ('verifier-L1-2.md', swap_v())]), 'replan'))
        check('next swap: the DEFECT fixture (no pair) still -> replan',
              nxt(s_step(pair + [('verifier-L1.md', DEFECT)]), 'replan'))
        check('next swap: a swap-routed fail is not counted: swap fail then a fail at L2 -> rebuild L2',
              nxt(s_step(pair + [('verifier-L1.md', swap_v()), ('builder-L2-2.md', DONE),
                                 ('verifier-L1-2.md', FAIL)]), 'rebuild L2'))

        # widen: a conductor scope decision adds paths to the one scope criterion. Each case builds a
        # throwaway repo with one empty commit; the step dir is <repo>/sdlc, recorded base-sha = HEAD.
        W_LIST = '{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude)sdlc"; ' \
                 'git ls-files --others --exclude-standard -- . ":(exclude)sdlc"; }'
        W_FORMS = {'F': f'{W_LIST} | grep -vxF -e a.txt | {{ ! grep -q .; }}',
                   'E': f'{W_LIST} | grep -vxE "a\\.txt" | {{ ! grep -q .; }}',
                   'A': f"{W_LIST} | grep -vE '^(a\\.txt)$' | {{ ! grep -q .; }}"}

        def w_handoff(*criteria):
            return ('## Task goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nd\n### Acceptance criteria\n'
                    + ''.join(f'- {c}\n' for c in criteria))

        def w_repo(handoff, base=True):
            count[0] += 1
            r = tmp / f'w-repo{count[0]}'
            r.mkdir()
            g = ['git', '-C', str(r), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']
            subprocess.run(['git', 'init', '-q', str(r)], check=True, capture_output=True)
            subprocess.run(g + ['commit', '-q', '--allow-empty', '-m', 'a'], check=True, capture_output=True)
            d = r / 'sdlc'
            d.mkdir()
            (d / 'handoff.md').write_text(handoff, encoding='utf-8')
            if base:
                head = subprocess.run(['git', '-C', str(r), 'rev-parse', 'HEAD'], check=True,
                                      capture_output=True, text=True).stdout.strip()
                (d / 'base-sha').write_text(head + '\n', encoding='utf-8')
            (r / 'a.txt').write_text('x\n', encoding='utf-8')
            return r, d

        def w_span(d):
            spans = [s for line in criteria_lines((d / 'handoff.md').read_text(encoding='utf-8'))
                     for s in line_spans(line) if 'git diff --name-only' in s]
            return spans[0] if len(spans) == 1 else None

        def w_green(r, d):
            span = w_span(d)
            return span is not None and run_guard(span, str(r), 30, base_sha(str(r), d))[0] == 0

        def widen_refused(name, d, argv_paths, needle=None):
            before = snapshot(d)
            rc, out, err = run_main(['widen', str(d)] + argv_paths)
            last = err.strip().splitlines()[-1] if err.strip() else ''
            check(f'widen: {name}', rc == 1 and out == '' and snapshot(d) == before
                  and last.startswith('plan defect: steps widen refused:')
                  and last.endswith('; replan this step (/chain 4.2)') and (needle is None or needle in err))

        for form, span in W_FORMS.items():
            r, d = w_repo(w_handoff(f'(guard) `{span}`', '`test -d .`'))
            rc, out, err = run_main(['widen', str(d), 'b.txt', 'dir/c+d.txt'])
            text = (d / 'handoff.md').read_text(encoding='utf-8')
            (r / 'b.txt').write_text('x\n', encoding='utf-8')
            (r / 'dir').mkdir()
            (r / 'dir' / 'c+d.txt').write_text('x\n', encoding='utf-8')
            widened = w_green(r, d)
            (r / 'bxtxt').write_text('x\n', encoding='utf-8')
            outside = not w_green(r, d)
            want_add = {'F': '-e a.txt -e b.txt -e dir/c+d.txt', 'E': 'a\\.txt|b\\.txt|dir/c\\+d\\.txt',
                        'A': '^(a\\.txt|b\\.txt|dir/c\\+d\\.txt)$'}[form]
            check(f'widen: (a) the {form} form applies: the widened files pass the span, a lookalike outside '
                  'the set fails it, (guard) kept, ## Scope widened lists each path, one stdout line',
                  rc == 0 and err == '' and len(out.splitlines()) == 1
                  and out.startswith(f'steps widen: {d}: added b.txt, dir/c+d.txt to the scope criterion: ')
                  and want_add in text and '- (guard) `' in text and widened and outside
                  and '## Scope widened\n- `b.txt`: allowed by a conductor scope decision (steps.py widen)\n'
                      '- `dir/c+d.txt`: allowed by a conductor scope decision (steps.py widen)\n' in text)
            # (b) rerun: every path already listed
            before = snapshot(d)
            rc, out, err = run_main(['widen', str(d), 'b.txt', 'dir/c+d.txt'])
            check(f'widen: (b) the {form} form rerun prints widen: already applied, exit 0, writes nothing',
                  rc == 0 and out.strip() == 'widen: already applied' and snapshot(d) == before)

        # a second widen keeps the earlier ## Scope widened items and adds only the new path
        r, d = w_repo(w_handoff(f'`{W_FORMS["F"]}`'))
        rc1, _, _ = run_main(['widen', str(d), 'b.txt'])
        rc2, out, _ = run_main(['widen', str(d), 'b.txt', 'e.txt'])
        text = (d / 'handoff.md').read_text(encoding='utf-8')
        check('widen: a second widen adds only the unlisted path and keeps the earlier Scope widened item',
              rc1 == 0 and rc2 == 0 and 'added e.txt to' in out and '-e a.txt -e b.txt -e e.txt' in text
              and text.count('## Scope widened') == 1 and text.count('`b.txt`: allowed') == 1
              and text.endswith('- `b.txt`: allowed by a conductor scope decision (steps.py widen)\n'
                                '- `e.txt`: allowed by a conductor scope decision (steps.py widen)\n'))

        # deny-path guard: git diff --name-only <base> -- . ':(exclude)<path>' | { ! grep -q .; }
        D_SPAN = 'git diff --name-only "$SDLC_BASE_SHA" -- . \':(exclude)sdlc\' \':(exclude)a.txt\' | { ! grep -q .; }'
        r, d = w_repo(w_handoff(f'(guard) `{D_SPAN}`', '`test -d .`'))
        git_add = lambda *a: subprocess.run(['git', '-C', str(r), 'add', '-N'] + list(a), check=True,
                                            capture_output=True)
        (r / 'dir').mkdir()
        for f in ('a.txt', 'b.txt', 'dir/c.txt'):
            (r / f).write_text('x\n', encoding='utf-8')
        git_add('a.txt', 'b.txt', 'dir/c.txt')
        red_before = not w_green(r, d)
        rc, out, err = run_main(['widen', str(d), 'b.txt', 'dir/c.txt'])
        text = (d / 'handoff.md').read_text(encoding='utf-8')
        green_after = w_green(r, d)
        (r / 'bxtxt').write_text('x\n', encoding='utf-8')
        git_add('bxtxt')
        outside = not w_green(r, d)
        check('widen: (d) a deny-path guard gets an :(exclude) pathspec per path: red before, green after, a '
              'lookalike outside the set still fails, (guard) kept, ## Scope widened lists each path',
              red_before and rc == 0 and err == '' and len(out.splitlines()) == 1
              and out.startswith(f'steps widen: {d}: added b.txt, dir/c.txt to the scope criterion: ')
              and "':(exclude)a.txt' ':(exclude)b.txt' ':(exclude)dir/c.txt' | { ! grep -q .; }" in text
              and '- (guard) `' in text and green_after and outside
              and '## Scope widened\n- `b.txt`: allowed by a conductor scope decision (steps.py widen)\n'
                  '- `dir/c.txt`: allowed by a conductor scope decision (steps.py widen)\n' in text)
        before = snapshot(d)
        rc, out, err = run_main(['widen', str(d), 'b.txt', 'a.txt'])
        check('widen: (d) a deny-path guard rerun with listed paths prints widen: already applied, writes nothing',
              rc == 0 and out.strip() == 'widen: already applied' and snapshot(d) == before)
        # forms the deny rewrite cannot handle stay refused
        r, d = w_repo(w_handoff('`git diff --name-only "$SDLC_BASE_SHA" | wc -l | grep -qx 0`'))
        widen_refused('(d) a git diff --name-only span with neither allow-list nor exclude is still refused', d,
                      ['b.txt'], 'no criterion line has a command span with git diff --name-only and a grep -v allow-list')
        r, d = w_repo(w_handoff('`git diff --name-only "$SDLC_BASE_SHA" -- . \':(exclude)x\' | cat; '
                                'git diff --name-only -- \':(exclude)y\' | { ! grep -q .; }`'))
        widen_refused('(d) a deny-path span with two exclude runs is refused', d, ['b.txt'], 'pathspec runs')

        # split inherits earlier widenings: step 1 widened by P, then split --only 2 puts P in step 2's
        # scope allow-list and its ## Scope widened section; a plan with no earlier widening is unchanged
        i_span = f'`{W_LIST} | grep -vxF -e a.txt | {{ ! grep -q .; }}`'
        i_plan = PLAN.replace('- two works', f'- two works\n- {i_span}')
        d = task(plan=i_plan)
        (d / 'step-1').mkdir()
        (d / 'step-1' / 'handoff.md').write_text(
            w_handoff(i_span) + '\n## Scope widened\n- `p/inherit.txt`: allowed by a conductor scope decision '
            '(steps.py widen)\n', encoding='utf-8')
        rc, _, _ = run_main(['split', str(d), '--only', '2'])
        text = (d / 'step-2' / 'handoff.md').read_text(encoding='utf-8')
        check('split: step 2 inherits the path step 1 widened, in its allow-list and its Scope widened section',
              rc == 0 and '-e a.txt -e p/inherit.txt' in text
              and '## Scope widened\n- `p/inherit.txt`: allowed by a conductor scope decision (steps.py widen)\n' in text)
        d = task(plan=i_plan)
        rc, _, _ = run_main(['split', str(d), '--only', '2'])
        text = (d / 'step-2' / 'handoff.md').read_text(encoding='utf-8')
        check('split: a step 2 with no earlier widening is unchanged',
              rc == 0 and '## Scope widened' not in text and '-e a.txt | ' in text)

        # (c) refusals: each writes nothing and ends with the plan-defect line
        r, d = w_repo(w_handoff('`test -d .`'))
        widen_refused('(c) no scope criterion line', d, ['b.txt'], 'no criterion line')
        widen_refused('(c) no scope criterion line names the accepted forms', d, ['b.txt'],
                      'grep -vxF -e <word>..., grep -vxE "<pattern>", or grep -vE "^(...)$"')
        widen_refused('(c) no scope criterion and no --reason still refuses, naming --reason', d, ['b.txt'],
                      '--reason')
        # (e) an explicit file list with a reason is the allow-list when the step has no scope criterion
        before = (d / 'handoff.md').read_text(encoding='utf-8')
        rc, out, err = run_main(['widen', str(d), 'b.txt', 'dir/c.txt', '--reason', 'citation-only   edits'])
        text = (d / 'handoff.md').read_text(encoding='utf-8')
        check('widen: (e) no scope criterion plus --reason records the list and the reason, rewrites no criterion',
              rc == 0 and err == '' and len(out.splitlines()) == 1
              and 'no scope criterion; recorded b.txt, dir/c.txt' in out and '(reason: citation-only edits)' in out
              and text.startswith(before.rstrip('\n')) and '`test -d .`' in text
              and text.endswith('## Scope widened\n'
                                '- `b.txt`: allowed by a conductor scope decision (steps.py widen): citation-only edits\n'
                                '- `dir/c.txt`: allowed by a conductor scope decision (steps.py widen): citation-only edits\n'))
        before = snapshot(d)
        rc, out, err = run_main(['widen', str(d), 'b.txt', '--reason', 'again'])
        check('widen: (e) the same list and a reason again prints widen: already applied, exit 0, writes nothing',
              rc == 0 and out.strip() == 'widen: already applied' and snapshot(d) == before)
        rc, out, err = run_main(['widen', str(d), 'e.txt', '--reason', 'more'])
        text = (d / 'handoff.md').read_text(encoding='utf-8')
        check('widen: (e) a later list adds only the new path and keeps the earlier items',
              rc == 0 and text.count('## Scope widened') == 1 and text.count('`b.txt`') == 1
              and text.endswith('- `e.txt`: allowed by a conductor scope decision (steps.py widen): more\n'))
        r, d = w_repo(w_handoff('`test -d .`'))
        widen_refused('(e) an empty --reason refuses', d, ['b.txt', '--reason', '  '], '--reason is empty')
        widen_refused('(e) a bad path still refuses with --reason', d, ['../x', '--reason', 'why'],
                      'not a repo-relative path')
        r, d = w_repo(w_handoff(f'`{W_FORMS["F"]}`'))
        rc, out, err = run_main(['widen', str(d), 'b.txt', '--reason', 'needed for the doc'])
        check('widen: (e) with a criterion present --reason widens the criterion and is recorded on the item',
              rc == 0 and '-e a.txt -e b.txt' in (d / 'handoff.md').read_text(encoding='utf-8')
              and (d / 'handoff.md').read_text(encoding='utf-8').endswith(
                  '(steps.py widen): needed for the doc\n'))
        r, d = w_repo(w_handoff(f'`{W_FORMS["F"]}`', f'`{W_FORMS["E"]}`'))
        widen_refused('(e) two scope criterion lines still refuse with --reason', d, ['b.txt', '--reason', 'why'],
                      '2 criterion lines')
        r, d = w_repo(w_handoff(f'`{W_FORMS["F"]}`', f'`{W_FORMS["E"]}`'))
        widen_refused('(c) two scope criterion lines', d, ['b.txt'], '2 criterion lines')
        r, d = w_repo(w_handoff(f'`{W_LIST} | grep -v -e a.txt | {{ ! grep -q .; }}`'))
        widen_refused('(c) an unrecognized allow-list form (grep -v -e)', d, ['b.txt'], 'unrecognized')
        rc, out, err = run_main(['widen', str(d), 'b.txt', '--reason', 'conductor decision'])
        check('widen: (e) an unrecognized allow-list form plus --reason records the list under Scope widened',
              rc == 0 and 'recorded b.txt under' in out and '(reason: conductor decision)' in out
              and (d / 'handoff.md').read_text(encoding='utf-8').endswith(
                  '- `b.txt`: allowed by a conductor scope decision (steps.py widen): conductor decision\n'))
        r, d = w_repo(w_handoff(f'`{W_FORMS["F"]}`'))
        for bad in ('../x', '/x', '-x', 'a b', 'x/../y'):
            widen_refused(f'(c) a bad path {bad!r}', d, ['b.txt', bad], 'not a repo-relative path')
        widen_refused('(c) no path given', d, [], 'no path given')
        (r / 'z.txt').write_text('x\n', encoding='utf-8')
        widen_refused('(c) a red new span (an unlisted file already changed)', d, ['b.txt'], 'red now (exit 1)')
        r, d = w_repo(w_handoff(f'`{W_LIST} | grep -vxF -e a.txt | {{ ! grep -q .; }} && touch w-made`'))
        widen_refused('(c) a new span that changes the work tree', d, ['b.txt'], 'changed the work tree: w-made')
        d = tmp / 'w-nohandoff'
        d.mkdir()
        widen_refused('(c) no step handoff', d, ['b.txt'], 'no step handoff')

        # (d) the span sees SDLC_BASE_SHA from <step dir>/base-sha, not HEAD: without base-sha it is red
        d_span = f'test "$SDLC_BASE_SHA" != "$(git rev-parse HEAD)" && {W_FORMS["F"]}'
        for with_base in (True, False):
            r, d = w_repo(w_handoff(f'`{d_span}`'))
            g = ['git', '-C', str(r), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']
            subprocess.run(g + ['commit', '-q', '--allow-empty', '-m', 'b'], check=True, capture_output=True)
            if not with_base:
                (d / 'base-sha').unlink()
                widen_refused('(d) with no base-sha the span sees HEAD and is red', d, ['b.txt'], 'red now')
                continue
            rc, _, err = run_main(['widen', str(d), 'b.txt'])
            check('widen: (d) the span sees SDLC_BASE_SHA from base-sha, not HEAD',
                  rc == 0 and err == '' and '-e a.txt -e b.txt' in (d / 'handoff.md').read_text(encoding='utf-8'))

        # (T-0382) a shared handoff in the primary checkout (stale at A), the lane worktree at B holds the
        # prerequisite commit and base-sha names B: widen must evaluate the lane, not the stale root
        def lane_repo(extra_lane_file=None):
            r, d = w_repo(w_handoff(f'`{W_FORMS["F"]}`'))
            g = ['git', '-C', str(r), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']
            lane = tmp / f'{r.name}-lane'
            subprocess.run(g + ['worktree', 'add', '-q', '--detach', str(lane)], check=True, capture_output=True)
            (lane / 'prerequisite.txt').write_text('p\n', encoding='utf-8')
            gl = ['git', '-C', str(lane), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']
            subprocess.run(gl + ['add', 'prerequisite.txt'], check=True, capture_output=True)
            subprocess.run(gl + ['commit', '-q', '-m', 'prerequisite'], check=True, capture_output=True)
            head = subprocess.run(['git', '-C', str(lane), 'rev-parse', 'HEAD'], check=True,
                                  capture_output=True, text=True).stdout.strip()
            (d / 'base-sha').write_text(head + '\n', encoding='utf-8')
            if extra_lane_file:
                (lane / extra_lane_file).write_text('u\n', encoding='utf-8')
            return r, d, lane

        def run_in(cwd, argv):
            old = os.getcwd()
            os.chdir(cwd)
            try:
                return run_main(argv)
            finally:
                os.chdir(old)

        r, d, lane = lane_repo()
        before = snapshot(d)
        rc, out, err = run_in(r, ['widen', str(d), 'b.txt'])
        check('widen: (T-0382) the primary checkout alone (no lane) stays red as before: stale root vs lane base',
              rc == 1 and out == '' and snapshot(d) == before and 'red now (exit 1)' in err
              and 'evaluating' not in err)
        rc, out, err = run_in(r, ['widen', str(d), 'b.txt', '--tree', str(lane)])
        check('widen: (T-0382) --tree the lane accepts the prerequisite from a shared handoff',
              rc == 0 and '-e a.txt -e b.txt' in (d / 'handoff.md').read_text(encoding='utf-8'))
        r, d, lane = lane_repo()
        rc, out, err = run_in(lane, ['widen', str(d), 'b.txt'])
        check('widen: (T-0382) with no --tree the lane cwd is the default tree, and stderr names it',
              rc == 0 and '-e a.txt -e b.txt' in (d / 'handoff.md').read_text(encoding='utf-8')
              and 'evaluating the scope span in the work tree' in err)
        r, d, lane = lane_repo('unrelated.txt')
        before = snapshot(d)
        rc, out, err = run_in(lane, ['widen', str(d), 'b.txt'])
        check('widen: (T-0382) negative control: an unrelated changed file in the lane still refuses, writes nothing',
              rc == 1 and out == '' and snapshot(d) == before and 'red now (exit 1)' in err
              and err.strip().splitlines()[-1].startswith('plan defect: steps widen refused:'))
        r2, d2 = w_repo(w_handoff(f'`{W_FORMS["F"]}`'))
        before = snapshot(d2)
        rc, out, err = run_in(r2, ['widen', str(d2), 'b.txt', '--tree', str(lane)])
        check('widen: (T-0382) a --tree of another repository refuses, writes nothing',
              rc == 1 and out == '' and snapshot(d2) == before and 'another repository' in err
              and err.strip().splitlines()[-1].startswith('plan defect: steps widen refused:'))
        rc, out, err = run_in(r2, ['widen', str(d2), 'b.txt', '--tree', str(tmp / 'no-such-dir')])
        check('widen: (T-0382) a --tree that is not a directory refuses', rc == 1 and 'not a directory' in err)
        rc, out, err = run_in(r2, ['widen', str(d2), 'b.txt'])
        check('widen: (T-0382) the ordinary single-checkout case is unchanged: no tree note, widened',
              rc == 0 and 'evaluating' not in err and '-e a.txt -e b.txt' in (d2 / 'handoff.md').read_text(encoding='utf-8'))

        # (r) review: whether a plan needs a plan review, and the verdict routing; each rule with its
        # negative form. Plan files hold STEP-shaped blocks; runs.jsonl orders results when given.
        def r_plan(level='L1', title='a', tail=''):
            return (f'## Goal\ng\n\n## Step 1: {title}\nlevel: {level}\n### Do\nx\n### Acceptance criteria\n'
                    f'- one works\n{tail}')

        def r_review(v):
            return f'## Verdict\n{v}\n\n## Findings\n- step 1: x\n\n## Missing decisions\nNone\n'

        def r_task(files, runs=None, handoff='## Goal\ng\n'):
            count[0] += 1
            d = tmp / f'review{count[0]}'
            d.mkdir()
            if handoff is not None:
                (d / 'handoff.md').write_text(handoff, encoding='utf-8')
            for name, text in files.items():
                (d / name).write_text(hdr(name, text), encoding='utf-8')
            if runs is not None:
                (d / 'runs.jsonl').write_text(''.join(json.dumps(
                    {'role': n.rsplit('-L', 1)[0], 'level': 'L' + n.rsplit('-L', 1)[1][0], 'file': n}) + '\n'
                    for n in runs), encoding='utf-8')
            return d

        def r_first(d):
            before = snapshot(d)
            rc, out, err = run_main(['review', str(d)])
            lines = out.splitlines()
            return (lines[0] if rc == 0 and len(lines) >= 2 and lines[1].startswith('reason: ')
                    and snapshot(d) == before else f'rc={rc} err={err.strip()}')

        d = r_task({})
        before = snapshot(d)
        rc, out, err = run_main(['review', str(d)])
        d2 = r_task({'planner-L2.md': r_plan()})
        check('(r) no planner-*.md: one steps review: line on stderr, nothing on stdout, exit 1; '
              'a planner result exits 0',
              rc == 1 and out == '' and err.startswith('steps review: ') and len(err.strip().splitlines()) == 1
              and snapshot(d) == before and run_main(['review', str(d2)])[0] == 0)
        rc, out, _ = run_main(['review', str(d2)])
        check('(r) output: the action, then reason:, then read: <plan path>',
              rc == 0 and out.splitlines()[0] == 'split' and out.splitlines()[1].startswith('reason: ')
              and out.splitlines()[2] == f'read: {d2 / "planner-L2.md"}')

        # (T-0657) review runs each (red) span once at the base sha in a throwaway worktree; one green there
        # turns split into replan with a red-at-base plan defect, and the worktree is gone after.
        def worktree_list(d):
            return subprocess.run(['git', '-C', str(d.parents[1]), 'worktree', 'list', '--porcelain'],
                                  capture_output=True, text=True).stdout

        d = o_repo('(red) `test -f README.md`', commit='README.md')
        wt_before, tree_before = worktree_list(d), porcelain(d)
        rc, out, err = run_main(['review', str(d)])
        lines = out.splitlines()
        check('(r) red-at-base: a (red) span green at base prints replan and the plan defect, logs it, and '
              'leaves no worktree and an unchanged tree',
              rc == 0 and lines[0] == 'replan' and 'plan defect: red-at-base: step 1: `test -f README.md`' in lines
              and 'step 1: red-at-base: `test -f README.md`' in (d / 'handoff.md').read_text(encoding='utf-8')
              and worktree_list(d) == wt_before and porcelain(d) == tree_before
              and not list(d.parents[2].glob('*.worktrees/tmp/review-red-*')))
        d = o_repo('(red) `test -f absent.txt`', commit='README.md')
        wt_before = worktree_list(d)
        rc, out, err = run_main(['review', str(d)])
        check('(r) red-at-base negative: a (red) span red at base reviews as before (split, no defect line)',
              rc == 0 and out.splitlines()[0] == 'split' and 'red-at-base' not in out
              and worktree_list(d) == wt_before)
        # (T-0715) a line meant for a tracked handoff holds no absolute home path: review prints repo-relative read:
        # paths, and the ## Plan review appends strip the repo prefix from a quoted path.
        d = o_repo('(red) `test -f absent.txt`', commit='README.md')
        rc, out, err = run_main(['review', str(d)])
        reads = [x for x in out.splitlines() if x.startswith('read: ')]
        check('(r) review prints the read: path repo-relative, never an absolute home or temp path',
              rc == 0 and reads == ['read: .sdlc/x/planner-L2.md'] and str(tmp) not in out)
        plan = str(d / 'planner-L2.md')
        record_plan_review(d, plan, [f'steps: {plan} step 1: plan-reviewer found {d}/planner-L2.md wrong'])
        record_review_override(d, 'plan-reviewer-L1.md', f'accepted per {d}/planner-L2.md')
        held = (d / 'handoff.md').read_text(encoding='utf-8').split('## Plan review', 1)[-1]
        check('(r) the ## Plan review appends hold the repo-relative path and no absolute path',
              '.sdlc/x/planner-L2.md wrong' in held and 'accepted per .sdlc/x/planner-L2.md' in held
              and str(tmp) not in held and not ABS_HOME_RE.search(held))
        check('(r) an unresolved: item under ## Assumptions stops, for - and * items, and the reason quotes it',
              r_first(r_task({'planner-L2.md': r_plan(tail='\n## Assumptions\n- unresolved: flag or positional\n')}))
              == 'stop'
              and r_first(r_task({'planner-L2.md': r_plan(tail='\n## Assumptions\n* unresolved: which one\n')}))
              == 'stop'
              and 'unresolved: flag or positional' in run_main(['review', str(r_task(
                  {'planner-L2.md': r_plan(tail='\n## Assumptions\n- unresolved: flag or positional\n')}))])[1])
        check('(r) negative: a settled assumption, an unresolved: item outside ## Assumptions, or one not at the '
              'item start does not stop',
              r_first(r_task({'planner-L2.md': r_plan(tail='\n## Assumptions\n- settled: flag\n')})) == 'split'
              and r_first(r_task({'planner-L2.md': r_plan(tail='\n## Risks\n- unresolved: x\n')})) == 'split'
              and r_first(r_task({'planner-L2.md': r_plan(tail='\n## Assumptions\n- was unresolved: x\n')}))
              == 'split')
        check('(r) a routine plan (planner L2, steps at L1..L3, no merge, one plan, no ## Plan review) -> split',
              r_first(r_task({'planner-L2.md': r_plan('L3')})) == 'split')
        check('(r) a step at L4 or L5 -> review L1; negative: a step at L3 -> split',
              r_first(r_task({'planner-L2.md': r_plan('L4')})) == 'review L1'
              and r_first(r_task({'planner-L2.md': r_plan('L5')})) == 'review L1'
              and r_first(r_task({'planner-L2.md': r_plan('L3')})) == 'split')
        check('(r) plan review only for L4 or L5: an all-L1-to-L3 plan (planner L3, a replan, a ## Plan review '
              'handoff line, a Merge title) -> split; an L4 and an L5 step -> review L1',
              r_first(r_task({'planner-L3.md': r_plan()})) == 'split'
              and r_first(r_task({'planner-L2.md': r_plan('L3'), 'planner-L2-2.md': r_plan('L3')})) == 'split'
              and r_first(r_task({'planner-L2.md': r_plan()},
                                 handoff='## Goal\ng\n\n## Plan review\nplan defect: x\n')) == 'split'
              and r_first(r_task({'planner-L2.md': r_plan(title='Merge lane/x')})) == 'split'
              and r_first(r_task({'planner-L3.md': r_plan('L4')})) == 'review L1'
              and r_first(r_task({'planner-L3.md': r_plan('L5')})) == 'review L1')
        d = r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('pass')})
        rc, out, _ = run_main(['review', str(d)])
        check('(r) a pass review after the plan -> split, reading the plan and the review',
              rc == 0 and out.splitlines()[0] == 'split'
              and f'read: {d / "plan-reviewer-L1.md"}' in out.splitlines())
        check('(r) negative: a pass review before a newer plan does not count -> review L1',
              r_first(r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('pass'),
                              'planner-L3-2.md': r_plan('L4')},
                             ['planner-L3.md', 'plan-reviewer-L1.md', 'planner-L3-2.md'])) == 'review L1')
        check('(r) one replan review -> replan; a PASS verdict is read lowercased -> split',
              r_first(r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('replan')})) == 'replan'
              and r_first(r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('PASS')})) == 'split')
        check('(r) a second replan review in the task dir -> stop; negative: a replan then a pass -> split',
              r_first(r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('replan'),
                              'planner-L3-2.md': r_plan('L4'), 'plan-reviewer-L1-2.md': r_review('replan')},
                             ['planner-L3.md', 'plan-reviewer-L1.md', 'planner-L3-2.md', 'plan-reviewer-L1-2.md']))
              == 'stop'
              and r_first(r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('replan'),
                                  'planner-L3-2.md': r_plan('L4'), 'plan-reviewer-L1-2.md': r_review('pass')},
                                 ['planner-L3.md', 'plan-reviewer-L1.md', 'planner-L3-2.md',
                                  'plan-reviewer-L1-2.md'])) == 'split')
        check('(r) a blocked review -> stop; negative: the same review with pass -> split',
              r_first(r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('blocked')})) == 'stop'
              and r_first(r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('pass')})) == 'split')
        check('(r) one verdict-less review -> review L1 (a rerun, never a replan); two consecutive -> stop',
              r_first(r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('maybe')})) == 'review L1'
              and r_first(r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('maybe'),
                                  'plan-reviewer-L1-2.md': '## Findings\nNone\n'},
                                 ['planner-L3.md', 'plan-reviewer-L1.md', 'plan-reviewer-L1-2.md'])) == 'stop')
        check('(r) negative: a verdict-less review before the plan does not count toward two -> review L1',
              r_first(r_task({'plan-reviewer-L1.md': r_review('maybe'), 'planner-L3.md': r_plan('L4'),
                              'plan-reviewer-L1-2.md': r_review('maybe')},
                             ['plan-reviewer-L1.md', 'planner-L3.md', 'plan-reviewer-L1-2.md'])) == 'review L1')

        d = r_task({'planner-L3.md': r_plan('L4'), 'planner-L3-2.md': r_plan('L4', 'Merge x')},
                   runs=['planner-L3.md', 'planner-L3-2.md'], handoff='## Goal\ng\n\n## Plan review\nx\n')
        rr_why = ['a step is at builder L4 or L5']
        rr_out = run_main(['review', str(d)])[1].splitlines()
        d2 = r_task({'planner-L2.md': r_plan(tail='\n## Assumptions\n- unresolved: which db\n')})
        check('(r) review_required returns the unresolved items and every reason review prints, in order',
              review_required(d / 'planner-L3-2.md', d) == ([], rr_why)
              and len(rr_out) >= 2
              and rr_out[1] == 'reason: a plan review is required (a step is at builder L4 or L5) and none counts '
              'after planner-L3-2.md'
              and review_required(d2 / 'planner-L2.md', d2) == (['unresolved: which db'], []))

        # (r) split refuses a plan whose newest counting review says replan or blocked, before any write
        for v in ('replan', 'blocked'):
            for how, argv in (('a dir target', lambda d: ['split', str(d)]),
                              ('--only 1', lambda d: ['split', str(d), '--only', '1']),
                              ('a file target', lambda d: ['split', str(d / 'planner-L3.md')])):
                d = r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review(v)})
                before = snapshot(d)
                rc, out, err = run_main(argv(d))
                last = err.strip().splitlines()[-1] if err.strip() else ''
                check(f'(r) split refuses a plan whose newest review says {v} ({how}), writes nothing',
                      rc == 1 and out == '' and snapshot(d) == before and not (d / 'step-1').exists()
                      and f'the newest plan review plan-reviewer-L1.md says {v}; a rejected plan is never split'
                      in err and last == f'plan defect: plan review: {v}; run steps.py review (/chain 3)')
        d = r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('pass')})
        rc, _, _ = run_main(['split', str(d)])
        check('(r) negative: split writes a plan whose newest review says pass',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file())
        d = r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('replan'),
                    'planner-L3-2.md': r_plan()}, ['planner-L3.md', 'plan-reviewer-L1.md', 'planner-L3-2.md'])
        rc, _, _ = run_main(['split', str(d)])
        check('(r) negative: split writes a replan whose rejecting review ran before it',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file())
        # (r) --override-review: a replan verdict only, after every other check, recorded, sticky
        OV = '\n## Plan review\nreview override: plan-reviewer-L1.md: the user accepts it\n'
        for how, extra in (('a dir target', []), ('--only 1', ['--only', '1'])):
            d = r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('replan')})
            rc, out, err = run_main(['split', str(d), *extra, '--override-review', '  the user   accepts it '])
            h = (d / 'handoff.md').read_text(encoding='utf-8')
            rc2, _, err2 = run_main(['split', str(d), '--only', '1'])
            rc3, rout, _ = run_main(['review', str(d)])
            check(f'(r) --override-review splits a replan review ({how}), records one collapsed line under '
                  '## Plan review, and sticks for a later split and for review',
                  rc == 0 and (d / 'step-1' / 'handoff.md').is_file()
                  and h == '## Goal\ng\n' + OV
                  and 'steps: review override: plan-reviewer-L1.md says replan; split anyway: the user accepts it'
                  in err
                  and rc2 == 0 and err2 == '' and (d / 'handoff.md').read_text(encoding='utf-8') == h
                  and rc3 == 0 and rout.splitlines()[0] == 'split'
                  and 'says replan; overridden: the user accepts it' in rout)
        d = r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('replan')},
                   handoff='## Goal\ng\n\n## Plan review\nplan review: replan: x\n\n## Other\ny\n')
        rc, _, _ = run_main(['split', str(d), '--override-review', 'ok'])
        check('(r) --override-review appends after the last ## Plan review line and keeps every other line',
              rc == 0 and (d / 'handoff.md').read_text(encoding='utf-8')
              == '## Goal\ng\n\n## Plan review\nplan review: replan: x\nreview override: plan-reviewer-L1.md: ok\n'
                 '\n## Other\ny\n')
        d = r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('replan')})
        before = snapshot(d)
        rc, out, err = run_main(['split', str(d), '--override-review', ' \t '])
        check('(r) negative: an empty --override-review reason refuses and writes nothing',
              rc == 1 and out == '' and 'steps: --override-review needs a reason' in err and snapshot(d) == before)
        d = r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('blocked')})
        before = snapshot(d)
        rc, out, err = run_main(['split', str(d), '--override-review', 'ok'])
        check('(r) negative: --override-review never overrides a blocked review',
              rc == 1 and out == '' and snapshot(d) == before and not (d / 'step-1').exists()
              and err.strip().splitlines()[-1] == 'plan defect: plan review: blocked; run steps.py review (/chain 3)')
        d = r_task({'planner-L3.md': r_plan(tail='- `echo "x`\n'), 'plan-reviewer-L1.md': r_review('replan')})
        before = snapshot(d)
        rc, out, err = run_main(['split', str(d), '--override-review', 'ok'])
        check('(r) negative: --override-review runs after every other check: a plan the lint refuses records nothing',
              rc == 1 and out == '' and snapshot(d) == before and 'plan defect' in err
              and 'review override' not in (d / 'handoff.md').read_text(encoding='utf-8'))
        d = r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_review('replan'),
                    'plan-reviewer-L1-2.md': r_review('replan')},
                   ['planner-L3.md', 'plan-reviewer-L1.md', 'plan-reviewer-L1-2.md'],
                   handoff='## Goal\ng\n' + OV)
        before = snapshot(d)
        rc, out, err = run_main(['split', str(d)])
        check('(r) negative: an override names one review file, so a newer replan review is not overridden',
              rc == 1 and out == '' and snapshot(d) == before
              and 'the newest plan review plan-reviewer-L1-2.md says replan; a rejected plan is never split' in err
              and r_first(d) == 'stop')
        d = r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('pass')})
        rc, _, err = run_main(['split', str(d), '--override-review', 'ok'])
        check('(r) --override-review with no rejecting review does nothing: it splits and writes no record',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and err == ''
              and (d / 'handoff.md').read_text(encoding='utf-8') == '## Goal\ng\n')
        # (r) T-0364: Notes-level findings pass and fold into the step Notes; a real defect still replans
        def r_notes(v, items):
            return f'## Verdict\n{v}\n\n## Findings\n{items}\n\n## Missing decisions\nNone\n'

        NF = '- step 1: notes-fix: guard line contradicts the Do; use the Do.\n- step 1: notes-fix: add tests/x.py to scope.'
        for v in ('replan', 'pass'):
            d = r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_notes(v, NF)})
            rc, out, _ = run_main(['review', str(d)])
            rc2, _, _ = run_main(['split', str(d)])
            h = (d / 'step-1' / 'handoff.md').read_text(encoding='utf-8') if rc2 == 0 else ''
            check(f'(r) a {v} review whose findings are all notes-fix passes: review says split, split appends '
                  'them to the step Notes',
                  rc == 0 and out.splitlines()[0] == 'split' and rc2 == 0
                  and h.endswith('\n### Notes\n- guard line contradicts the Do; use the Do.\n'
                                 '- add tests/x.py to scope.\n'))
        d = r_task({'planner-L3.md': r_plan('L4'),
                    'plan-reviewer-L1.md': r_notes('replan', NF + '\n- step 1: criteria: c2 cannot go red.')})
        before = snapshot(d)
        rc, out, err = run_main(['split', str(d)])
        check('(r) negative: one real defect among notes-fix findings still replans and split refuses',
              r_first(d) == 'replan' and rc == 1 and out == '' and snapshot(d) == before)
        for bad in ('- plan: notes-fix: x', '- step 1: x', 'None'):
            d = r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_notes('replan', bad)})
            check(f'(r) negative: a replan review whose finding is "{bad}" is not notes-level and replans',
                  r_first(d) == 'replan')
        d = r_task({'planner-L3.md': r_plan('L4'), 'plan-reviewer-L1.md': r_notes('replan', NF),
                    'plan-reviewer-L1-2.md': r_notes('replan', NF)},
                   ['planner-L3.md', 'plan-reviewer-L1.md', 'plan-reviewer-L1-2.md'])
        check('(r) notes-fix reviews never count toward the one-replan cap', r_first(d) == 'split')
        # (r) T-0582: a criterion-only finding (a fact mismatch on main) is amended in place and never spends the
        # replan; a design finding after the replan still asks the user
        CP = r_plan('L4', tail='- `test -f old.md` exits 0\n')
        CO = ('- step 1: criterion-only: old `test -f old.md` -> new `test -f new.md` exits 0. '
              'Evidence: `test -f old.md` exits 1 on main; `test -f new.md` exits 0.')
        CO_LOG = ('- criterion-only amend: plan-reviewer-L1-2.md: step 1: old `test -f old.md` -> '
                  'new `test -f new.md` exits 0')
        AFTER = ['planner-L3.md', 'plan-reviewer-L1.md', 'planner-L3-2.md', 'plan-reviewer-L1-2.md']
        d = r_task({'planner-L3.md': CP, 'plan-reviewer-L1.md': r_review('replan'), 'planner-L3-2.md': CP,
                    'plan-reviewer-L1-2.md': r_notes('replan', CO)}, AFTER)
        check('(r) a criterion-only finding after the replan routes to amend, not to the user', r_first(d) == 'amend')
        d2 = r_task({'planner-L3.md': CP, 'plan-reviewer-L1.md': r_review('replan'), 'planner-L3-2.md': CP,
                     'plan-reviewer-L1-2.md': r_review('replan')}, AFTER)
        check('(r) negative: a design finding after the replan still routes to the user (stop)', r_first(d2) == 'stop')
        rc, _, err = run_main(['split', str(d)])
        sh = (d / 'step-1' / 'handoff.md').read_text(encoding='utf-8') if rc == 0 else ''
        th = (d / 'handoff.md').read_text(encoding='utf-8')
        rc2, _, _ = run_main(['split', str(d)])
        check('(r) split applies a criterion-only amend to the step handoff, logs it once under ## Plan review, '
              'and review then says split',
              rc == 0 and '- `test -f new.md` exits 0\n' in sh and 'old.md' not in sh
              and th == '## Goal\ng\n\n## Plan review\n' + CO_LOG + '\n'
              and 'steps: step 1: criterion-only amend: old `test -f old.md` -> new `test -f new.md` exits 0' in err
              and r_first(d) == 'split' and rc2 == 0
              and (d / 'handoff.md').read_text(encoding='utf-8') == th)
        for v in ('replan', 'pass'):
            d = r_task({'planner-L3.md': CP, 'plan-reviewer-L1.md': r_notes(v, CO)})
            check(f'(r) a first {v} review whose findings are all criterion-only routes to amend', r_first(d) == 'amend')
        rc, _, _ = run_main(['split', str(d)])
        check('(r) a logged criterion-only amend does not spend the replan a builder amend needs',
              rc == 0 and 'criterion-only amend:' in (d / 'handoff.md').read_text(encoding='utf-8')
              and replan_used(d / 'step-1') is None)
        files = {'planner-L3.md': CP, 'plan-reviewer-L1.md': r_notes('replan', CO), 'planner-L3-2.md': CP,
                 'plan-reviewer-L1-2.md': r_review('replan')}
        logged = '## Goal\ng\n\n## Plan review\n' + CO_LOG.replace('L1-2.md', 'L1.md') + '\n'
        check('(r) an applied (logged) criterion-only review is not counted: a later design review replans; '
              'negative: unlogged, it counts and the design review stops',
              r_first(r_task(files, AFTER, handoff=logged)) == 'replan' and r_first(r_task(files, AFTER)) == 'stop')
        for bad, why in ((CO.replace('old `test -f old.md`', 'old `test -f gone.md`'), 'an old span no criterion holds'),
                         (CO.replace('step 1:', 'step 2:', 1), 'a step the plan does not have'),
                         (CO.split('. Evidence:')[0], 'no Evidence'),
                         (CO + '\n- step 1: interfaces: Do names a missing symbol.', 'a design finding beside it')):
            d = r_task({'planner-L3.md': CP, 'plan-reviewer-L1.md': r_notes('replan', bad)})
            before = snapshot(d)
            rc, out, _ = run_main(['split', str(d)])
            check(f'(r) negative: a criterion-only review with {why} is a design replan and split refuses',
                  r_first(d) == 'replan' and rc == 1 and out == '' and snapshot(d) == before)
        d = r_task({'planner-L3.md': CP, 'plan-reviewer-L1.md': r_notes('replan', CO + '\n' + NF)})
        rc, _, _ = run_main(['split', str(d)])
        sh = (d / 'step-1' / 'handoff.md').read_text(encoding='utf-8') if rc == 0 else ''
        check('(r) criterion-only beside notes-fix findings: review says amend; split amends and folds the Notes',
              r_first(r_task({'planner-L3.md': CP, 'plan-reviewer-L1.md': r_notes('replan', CO + '\n' + NF)}))
              == 'amend' and rc == 0 and '- `test -f new.md` exits 0\n' in sh
              and sh.endswith('\n### Notes\n- guard line contradicts the Do; use the Do.\n- add tests/x.py to scope.\n'))
        # (lane) the lane of a ticket, and its record in skips.md
        def l_handoff(size='L2', tail=''):
            front = f'---\nid: T-0001\ntitle: "x"\nsize: {size}\n---\n\n' if size is not None else ''
            return f'{front}## Goal\ng\n{tail}'

        def l_scope(form):
            return f'- (guard) `git diff --name-only "$SDLC_BASE_SHA" | {form} | grep -q . && exit 1 || exit 0`'

        L_F1 = 'grep -vxF -e docs/a.md -e docs/b.md'
        L_F2 = 'grep -vxF -e docs/c.md'

        def l_step(n, level, crit=2, scope=None):
            items = [f'- c{n}.{j} holds' for j in range(crit - (1 if scope else 0))]
            if scope:
                items.append(l_scope(scope))
            return f'## Step {n}: Thing {n}\nlevel: L{level}\n### Do\nd\n### Acceptance criteria\n' + '\n'.join(items)

        def l_plan(levels=(2, 3), crits=(12, 2), scopes=(L_F1, L_F2), title1='Thing 1', assume='- a'):
            blocks = [l_step(i, lv, c, sc) for i, (lv, c, sc) in enumerate(zip(levels, crits, scopes), 1)]
            blocks[0] = blocks[0].replace('## Step 1: Thing 1', f'## Step 1: {title1}', 1)
            return '## Goal\ng\n\n' + '\n\n'.join(blocks) + f'\n\n## Assumptions\n{assume}\n\n## Risks\n- r\n'

        def l_task(handoff, plans=None, files=None):
            count[0] += 1
            r = tmp / f'lane{count[0]}'
            subprocess.run(['git', 'init', '-q', str(r)], check=True, capture_output=True)
            d = r / '.sdlc' / '0001-x'
            d.mkdir(parents=True)
            if handoff is not None:
                (d / 'handoff.md').write_text(handoff, encoding='utf-8')
            for name, text in (plans or {}).items():
                (d / name).write_text(hdr(name, text), encoding='utf-8')
            for name, text in (files or {}).items():
                (r / name).parent.mkdir(parents=True, exist_ok=True)
                (r / name).write_text(text, encoding='utf-8')
            return d

        def l_run(d):
            rc, out, err = run_main(['lane', str(d)])
            lines = out.splitlines()
            reasons = [x[len('reason: '):] for x in lines if x.startswith('reason: ')]
            reads = [x[len('read: '):] for x in lines if x.startswith('read: ')]
            skips = d / 'skips.md'
            recs = [x for x in skips.read_text(encoding='utf-8').splitlines() if x.startswith('- lane: ')] \
                if skips.is_file() else []
            return (lines[0] if rc == 0 and lines and err == '' else f'rc={rc} err={err.strip()}'), reasons, reads, recs

        lean_ok = 'every lean condition holds: size L2, planner L2, 2 steps at L1 to L3, one AGENTS.md owner (.)'
        ok = True
        # the levels, then the deprecated aliases (read as L1 to L4): the same lanes, the reason names the level
        for size, want, level in (('L1', 'solo', 'L1'), ('L2', 'solo', 'L2'), ('L3', 'full', 'L3'), ('L4', 'full', 'L4'),
                                  ('L5', 'full', 'L5'), ('S', 'solo', 'L1'), ('M', 'solo', 'L2'), ('L', 'full', 'L3'),
                                  ('XL', 'full', 'L4')):
            lane, reasons, _, recs = l_run(l_task(l_handoff(size)))
            why = f'size {level} decides before planning (no planner result yet)'
            ok = ok and lane == want and reasons == [why] \
                and recs == [f'- lane: {want}; point: before planning; reasons: {why}']
        for k, want in ((20, 'solo'), (21, 'full')):
            crit = '\n## Acceptance criteria\n' + ''.join(f'- [ ] c{i}\n' for i in range(k))
            lane, reasons, _, _ = l_run(l_task(l_handoff('L2', crit)))
            why = 'size L2 decides before planning (no planner result yet)' if k == 20 else \
                'ticket lists 21 criteria (limit 20 for size L1 or L2); split it into tickets of at most 20'
            ok = ok and lane == want and reasons == [why]
        lane, reasons, _, recs = l_run(l_task(l_handoff(None)))
        check('(lane) before planning, size alone decides: L1 and L2 (aliases S, M) solo, L3 to L5 (aliases L, XL) full, no size full',
              ok and lane == 'full' and reasons == [LANE_NO_SIZE]
              and recs == [f'- lane: full; point: before planning; reasons: {LANE_NO_SIZE}'])

        # (lane) T-0512: under `profile: inner-loop` a size L3 ticket with no merge title and no security word goes solo
        def il_lane(size, config, title='x', tail=''):
            d = l_task(l_handoff(size, tail).replace('title: "x"', f'title: "{title}"'))
            if config is not None:
                (d.parent / 'config').write_text(config, encoding='utf-8')
            lane, reasons, _, _ = l_run(d)
            return lane, reasons
        ilp = 'profile: inner-loop\n'
        on_lane, on_why = il_lane('L3', ilp)
        check('(lane) inner-loop profile: size L3 with no merge title and no security word prints solo, and says why',
              on_lane == 'solo' and len(on_why) == 1 and 'profile: inner-loop' in on_why[0])
        check('(lane) control: size L3 without the profile line is full (as before)', il_lane('L3', None)[0] == 'full'
              and il_lane('L3', '# profile: inner-loop\n')[0] == 'full')
        check('(lane) control: size L3 with profile: default in the handoff is full',
              il_lane('L3', ilp, tail='profile: default\n')[0] == 'full')
        check('(lane) negative control: an L3 titled merge ... stays full under the profile',
              il_lane('L3', ilp, title='merge the lanes')[0] == 'full')
        check('(lane) negative control: an L3 handoff naming security stays full under the profile',
              il_lane('L3', ilp, tail='Fix a security hole.\n')[0] == 'full')
        check('(lane) negative control: L4 and L5 stay full under the profile',
              il_lane('L4', ilp)[0] == 'full' and il_lane('L5', ilp)[0] == 'full')
        check('(lane) the profile leaves L1 and L2 solo', il_lane('L1', ilp)[0] == 'solo' and il_lane('L2', ilp)[0] == 'solo')

        ok = True
        for form in (L_F2, 'grep -vxE "docs/c\\.md"', 'grep -vE "^(docs/c\\.md)$"'):
            d = l_task(l_handoff(), {'planner-L2.md': l_plan(scopes=(L_F1, form))})
            lane, reasons, reads, recs = l_run(d)
            ok = ok and lane == 'lean' and reasons == [lean_ok] \
                and recs == [f'- lane: lean; point: after planning; reasons: {lean_ok}'] \
                and reads == [str(d / 'handoff.md'), str(d / 'planner-L2.md')]
        check('(lane) a two-step size L2 plan at L1 to L3 inside one AGENTS.md owner is lean, for scope forms F, E, '
              'and A', ok)

        lane, reasons, _, _ = l_run(l_task(l_handoff(), {'planner-L2.md': l_plan(title1='Merge lane/x')}))
        check('(lane) lean stays strict: a Merge step keeps a ticket full though plan review no longer needs it',
              lane == 'full' and reasons == ['the plan has a merge step'])

        lane, reasons, _, _ = l_run(l_task(l_handoff(), {'planner-L2.md': l_plan(levels=(2, 4))}))
        check('(lane) negative: the same two-step plan with one step at L4 is full',
              lane == 'full' and reasons == ['a step is at builder L4 or L5'])

        d = l_task(l_handoff(), {'planner-L3.md': l_plan(), 'planner-L3-2.md': l_plan()})
        with open(d / 'handoff.md', 'a', encoding='utf-8') as f:
            f.write('\n## Plan review\nrequired\n')
        lane, reasons, _, _ = l_run(d)
        check('(lane) lean stays strict: planner L3, a replan, and a ## Plan review line each keep a ticket full '
              'though plan review no longer requires them',
              lane == 'full' and 'handoff.md holds ## Plan review' in reasons
              and any('planner L3 plan' in r for r in reasons) and any('(a replan)' in r for r in reasons))

        rr_cases = [
            l_task(l_handoff(), {'planner-L2.md': l_plan(levels=(4, 3))}),
            l_task(l_handoff(), {'planner-L2.md': l_plan(levels=(2, 5))}),
            l_task(l_handoff(), {'planner-L2.md': l_plan(assume='- unresolved: which db')}),
        ]
        ok = True
        for d in rr_cases:
            plan = order.newest(d, 'planner')
            unresolved, why = review_required(plan, d)
            rc, out, _ = run_main(['review', str(d)])
            lane, reasons, _, _ = l_run(d)
            want = [f'{os.path.basename(plan)} lists an unresolved assumption: "{x}"' for x in unresolved[:1]] + why
            ok = ok and rc == 0 and out.splitlines()[0] in ('review L1', 'stop') and lane == 'full' \
                and (unresolved or why) and all(w in reasons for w in want)
        unresolved_reasons = l_run(rr_cases[-1])[1]
        check('(lane) every plan steps.py review requires a review or a stop for is full, with each review_required '
              'reason',
              ok and 'planner-L2.md lists an unresolved assumption: "unresolved: which db"' in unresolved_reasons)

        full_cases = [
            (l_task(l_handoff('L3'), {'planner-L2.md': l_plan()}), 'size L3 is above L2, and lean takes only size L1 or L2'),
            (l_task(l_handoff('L'), {'planner-L2.md': l_plan()}), 'size L3 is above L2, and lean takes only size L1 or L2'),
            (l_task(l_handoff(), {'planner-L2.md': l_plan(levels=(2, 3, 1), crits=(12, 2, 2),
                                                          scopes=(L_F1, L_F2, 'grep -vxF -e docs/d.md'))}),
             '3 steps, and lean allows at most 2'),
            (l_task(l_handoff(), {'planner-L2.md': l_plan(crits=(13, 2))}),
             'step 1 has 13 acceptance criteria, and lean allows at most 12'),
            (l_task(l_handoff(), {'planner-L2.md': l_plan(scopes=(L_F1, None))}),
             'step 2 has no scope allow-list in a form steps.py widen recognizes, so its files are unknown'),
            (l_task(l_handoff(), {'planner-L2.md': l_plan(scopes=(L_F1, 'grep -vxE "docs/.*"'))}),
             'step 2 scope entry is not a repo-relative path: docs/.*'),
            (l_task(l_handoff(), {'planner-L2.md': l_plan(
                scopes=(L_F1, 'grep -vxF -e plugins/sdlc-lite/scripts/steps.py'))}),
             'step 2 scope names a contract other roles parse: plugins/sdlc-lite/scripts/steps.py'),
            (l_task(l_handoff(), {'planner-L2.md': l_plan(scopes=(L_F1, 'grep -vE "^(docs/a\\.md|pkg/x\\.py)$"'))},
                    {'pkg/AGENTS.md': '# pkg\n'}),
             'scoped files span 2 AGENTS.md owners: ., pkg'),
        ]
        res = [(l_run(d), want) for d, want in full_cases]
        check('(lane) full after planning: size L3, three steps, a 13-criterion step, no recognized scope allow-list, '
              'a non-path scope entry, a contract path, or two AGENTS.md owners',
              all(r[0] == 'full' and r[1] == [want] for r, want in res))

        rec_m = '- lane: solo; point: before planning; reasons: size L2 decides before planning (no planner result yet)'
        why_s = 'solo lane: runs end to end in one session'
        sk = f'- skip: planner; step: all; reason: {why_s}; decided: lane\n- skip: filer; step: all; reason: {why_s}; decided: lane\n'
        d = l_task(l_handoff())
        _, _, reads1, _ = l_run(d)
        made = (d / 'skips.md').read_text(encoding='utf-8')
        _, _, reads2, _ = l_run(d)
        twice = (d / 'skips.md').read_text(encoding='utf-8')
        d2 = l_task(l_handoff())
        (d2 / 'skips.md').write_text('# Skips\n\n## Lane\n- lane: lean; point: x; reasons: old\n\n## Skipped\n- x\n',
                                     encoding='utf-8')
        _, _, reads3, _ = l_run(d2)
        d3 = l_task(l_handoff())
        (d3 / 'skips.md').write_text('## Skipped\n- x\n', encoding='utf-8')
        _, _, reads4, _ = l_run(d3)
        d4 = l_task(l_handoff())
        (d4 / 'skips.md').write_text('note\n', encoding='utf-8')
        l_run(d4)
        check('(lane) skips.md: each call appends one - lane: line to ## Lane, a solo lane adds the planner and filer ## Skipped entries once, and every other line is kept',
              made == f'# Skips\n\n## Lane\n{rec_m}\n\n## Skipped\n{sk}'
              and twice == f'# Skips\n\n## Lane\n{rec_m}\n{rec_m}\n\n## Skipped\n{sk}'
              and str(d / 'skips.md') not in reads1 and str(d / 'skips.md') in reads2
              and (d2 / 'skips.md').read_text(encoding='utf-8')
              == f'# Skips\n\n## Lane\n- lane: lean; point: x; reasons: old\n{rec_m}\n\n## Skipped\n{sk}- x\n'
              and str(d2 / 'skips.md') in reads3
              and (d3 / 'skips.md').read_text(encoding='utf-8') == f'## Lane\n{rec_m}\n\n## Skipped\n{sk}- x\n'
              and str(d3 / 'skips.md') in reads4
              and (d4 / 'skips.md').read_text(encoding='utf-8') == f'note\n\n## Lane\n{rec_m}\n\n## Skipped\n{sk}')

        d = l_task(l_handoff(), {'planner-L2.md': l_plan()},
                   {'.sdlc/0001-x/skips.md': '# Skips\n\n## Lane\n- lane: full; point: before planning; reasons: x\n'})
        lane, reasons, _, recs = l_run(d)
        d2 = l_task(l_handoff(), {'planner-L2.md': l_plan()},
                    {'.sdlc/0001-x/skips.md': '# Skips\n\n## Other\n- lane: full; point: x; reasons: x\n'})
        check('(lane) a recorded full stays full when the facts give lean',
              lane == 'full' and reasons[:1] == [LANE_STICKY] and len(recs) == 2
              and recs[1].startswith(f'- lane: full; point: after planning; reasons: {LANE_STICKY}')
              and l_run(d2)[0] == 'lean')

        before = snapshot(tmp)
        missing = tmp / 'lane-missing'
        rc, out, err = run_main(['lane', str(missing)])
        check('(lane) a missing dir: one steps lane: line on stderr, nothing on stdout, exit 1, nothing written',
              rc == 1 and out == '' and err.startswith('steps lane: ') and len(err.strip().splitlines()) == 1
              and not missing.exists() and snapshot(tmp) == before)

        # (lane solo close) a conductor-style flow, no fanout: steps lane, then tickets.py close --reason, with
        # the T-0219 skips guard live. Negative control: with the Skipped write off, a plain close is refused (close
        # --reason writes the missing entries itself since T-0581, so it cannot show the guard).
        def solo_flow(name, disable):
            r = tmp / f'solo-{name}'
            subprocess.run(['git', 'init', '-q', str(r)], check=True, capture_output=True)
            tk = [sys.executable, str(pathlib.Path(__file__).resolve().parent / 'tickets.py'), '--root', '.sdlc']
            env_ = dict(os.environ, SDLC_SELFTEST_NO_SKIPPED='1') if disable else {
                k: v for k, v in os.environ.items() if k != 'SDLC_SELFTEST_NO_SKIPPED'}
            made = subprocess.run([*tk, 'new', 'feature', 'solo-a', 'Solo A'], cwd=str(r), env=env_,
                                  capture_output=True, text=True)
            d = r / '.sdlc' / 'solo-a'
            hp = d / 'handoff.md'
            hp.write_text(re.sub(r'(?m)^size:.*$', 'size: L2', hp.read_text(encoding='utf-8')), encoding='utf-8')
            lane_run_ = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'lane', str(d)],
                                       cwd=str(r), env=env_, capture_output=True, text=True)
            first = (d / 'skips.md').read_text(encoding='utf-8') if (d / 'skips.md').is_file() else ''
            subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'lane', str(d)], cwd=str(r),
                           env=env_, capture_output=True, text=True)
            second = (d / 'skips.md').read_text(encoding='utf-8')
            closed = subprocess.run([*tk, 'close', 'solo-a', *([] if disable else ['--reason', 'delivered by solo'])],
                                    cwd=str(r), env=env_, capture_output=True, text=True)
            return made, lane_run_, first, second, closed

        made, lr, first, second, closed = solo_flow('on', False)
        check('(lane solo close) lane solo writes the planner and filer ## Skipped entries and the close by reason passes '
              f'with the guard live (rc={closed.returncode} {closed.stderr.strip()[:160]!r})',
              made.returncode == 0 and lr.stdout.splitlines()[:1] == ['solo'] and closed.returncode == 0
              and '- skip: planner; step: all;' in second and '- skip: filer; step: all;' in second
              and 'decided: lane' in second)
        check('(lane solo close) running lane twice adds no duplicate entries: one planner and one filer entry',
              second.count('- skip: planner;') == 1 and second.count('- skip: filer;') == 1
              and first.count('- skip:') == 2 and second.count('- lane: solo') == 2)
        made0, lr0, first0, second0, closed0 = solo_flow('off', True)
        check('(lane solo close) negative control: with the Skipped write off a plain close is refused '
              f'(rc={closed0.returncode} {closed0.stderr.strip()[:160]!r})',
              closed0.returncode == 1 and 'no ## Skipped entry' in closed0.stderr and '- skip:' not in second0)
        full_ = tmp / 'solo-full'
        subprocess.run(['git', 'init', '-q', str(full_)], check=True, capture_output=True)
        fd = full_ / '.sdlc' / 'big'
        fd.mkdir(parents=True)
        (fd / 'handoff.md').write_text(l_handoff('L3'), encoding='utf-8')
        subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'lane', str(fd)], cwd=str(full_),
                       capture_output=True, text=True)
        check('(lane solo close) only lane solo writes Skipped entries: a size L3 ticket (lane full) gets none',
              '- skip:' not in (fd / 'skips.md').read_text(encoding='utf-8'))

    # (v) The verifier level of a solo ticket (T-0356): L2 by default, L3 only on the named conditions.
    def v_text(size='L2', title='x', goal='g', criteria=(), tail=''):
        front = f'---\nid: T-0001\ntitle: "{title}"\nsize: {size}\n---\n\n' if size is not None else ''
        crit = ''.join(f'- [ ] {c}\n' for c in criteria)
        return f'{front}## Goal\n{goal}\n\n## Acceptance criteria\n{crit}\n## Context\n{tail}\n'

    def v_level(text):
        return ticket_verifier(text)[0]

    check('(v) negative control: an L1 or L2 ticket with plain criteria gets verifier L2',
          v_level(v_text('L1', criteria=['`true` exits 0'])) == 'L2' and v_level(v_text('L2', criteria=['`true` exits 0'])) == 'L2')
    check('(v) negative control: an unsized ticket and a size L3 ticket get verifier L2',
          v_level(v_text(None)) == 'L2' and v_level(v_text('L3')) == 'L2')
    check('(v) negative control: exactly one, security, or label outside the Goal, title, and criteria, and verifier: L3 inside a sentence, do not raise it',
          v_level(v_text(criteria=['exactly one file changes'], tail='a label, a security note, verifier: L3 in prose')) == 'L2')
    check('(v) positive control: a line that is only verifier: L3 raises it, wherever it sits',
          v_level(v_text(tail='verifier: L3')) == 'L3')
    check('(v) positive control: size L4 and size L5 get verifier L3',
          v_level(v_text('L4')) == 'L3' and v_level(v_text('L5')) == 'L3')
    check('(v) positive control: a title starting Merge gets verifier L3; one that only contains merge does not',
          v_level(v_text(title='Merge lane x')) == 'L3' and v_level(v_text(title='Do not merge lane x')) == 'L2')
    check('(v) positive control: the word security in the title or the Goal gets verifier L3',
          v_level(v_text(title='Security review of hooks')) == 'L3' and v_level(v_text(goal='close a security hole')) == 'L3')
    check('(v) positive control: a criterion that pins an exact label or string gets verifier L3',
          v_level(v_text(criteria=['the exact label reads `cost`'])) == 'L3'
          and v_level(v_text(criteria=['the text matches verbatim'])) == 'L3'
          and v_level(v_text(criteria=['the cost_basis label is `x`'])) == 'L3')
    check('(v) a label word in a plain bullet outside the criteria checkboxes does not raise it',
          v_level(v_text(tail='- the label is shown')) == 'L2')
    with tempfile.TemporaryDirectory() as vtmp:
        vd = pathlib.Path(vtmp)
        (vd / 'handoff.md').write_text(v_text('L2', criteria=['`true` exits 0']), encoding='utf-8')
        rc, out, err = run_main(['verifier-level', str(vd)])
        rc2, _, err2 = run_main(['verifier-level', str(vd / 'nope')])
        check('(v) verifier-level prints the level, a reason, and the handoff read; writes no file; a dir with no handoff.md exits 1',
              rc == 0 and err == '' and out.splitlines()[0] == 'L2' and out.splitlines()[1].startswith('reason: ')
              and out.splitlines()[2] == f'read: {vd / "handoff.md"}' and sorted(x.name for x in vd.iterdir()) == ['handoff.md']
              and rc2 == 1 and 'no handoff.md' in err2)

    # (L) T-0379: a step handoff cites prior-attempt reports of a superseded step; lint refuses a stale or
    # absent path, and split rewrites the new handoff's citations into the immutable superseded folder
    with tempfile.TemporaryDirectory() as ltmp:
        lroot = pathlib.Path(ltmp)
        counter = [0]

        def l_task(superseded, live=(), cites=None):
            """A fixture ticket under <root>/.sdlc: planner-L3.md whose steps 3, 4 and 9 cite the previous
            attempt's reports as step-<n>/<report>, the superseded folders holding the reports, and any
            reports already in the live step folders."""
            counter[0] += 1
            top = lroot / f'r{counter[0]}'
            td = top / '.sdlc' / '0001-x'
            td.mkdir(parents=True)
            (td / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
            cites = cites or {3: 'builder-L3.md', 4: 'builder-L3.md', 9: 'verifier-L3.md'}
            blocks = ''.join(
                f'## Step {n}: s{n}\nlevel: L1\n\n### Read first\n- `.sdlc/0001-x/step-{n}/{rep}`\n\n### Acceptance criteria\n'
                f'- `true`\n\nPrior attempt: see .sdlc/0001-x/step-{n}/{rep} for the findings.\n\n'
                for n, rep in cites.items())
            (td / 'planner-L3.md').write_text(hdr('planner-L3.md', f'# Plan\n## Goal\ng\n\n{blocks}'), encoding='utf-8')
            for name, files in superseded.items():
                (td / name).mkdir()
                for f in files:
                    (td / name / f).write_text(hdr(f, '## Status\ndone\n'), encoding='utf-8')
            for name, files in dict(live).items():
                (td / name).mkdir(exist_ok=True)
                for f in files:
                    (td / name / f).write_text(hdr(f, '## Status\ndone\n'), encoding='utf-8')
            return td

        ln = lambda td, n: (td / f'step-{n}' / 'handoff.md')
        rd = lambda td, n: ln(td, n).read_text(encoding='utf-8') if ln(td, n).is_file() else ''
        rep = {'step-3.superseded-1': ['builder-L3.md'], 'step-4.superseded-1': ['builder-L3.md'],
               'step-9.superseded-1': ['verifier-L3.md']}
        td = l_task(rep)
        rc, out, err = run_main(['split', str(td)])
        h3, h4, h9 = (rd(td, n) for n in (3, 4, 9))
        check('(L) split rewrites steps 3, 4 and 9 citations into the superseded folder, one per step',
              rc == 0 and '.sdlc/0001-x/step-3.superseded-1/builder-L3.md' in h3
              and '.sdlc/0001-x/step-4.superseded-1/builder-L3.md' in h4
              and '.sdlc/0001-x/step-9.superseded-1/verifier-L3.md' in h9
              and '/step-3/builder-L3.md' not in h3 and '/step-4/builder-L3.md' not in h4 and '/step-9/verifier-L3.md' not in h9)
        check('(L) the rewrite covers the prose citation as well as the ### Read first one',
              h3.count('step-3.superseded-1/builder-L3.md') == 2)
        check('(L) split names each rewrite on stderr', err.count('rewrote prior-report link') == 6)
        check('(L) the rewritten handoffs pass lint with the live step dir still empty',
              all(run_main(['lint', str(ln(td, n))])[0] == 0 for n in (3, 4, 9)))
        check('(L) split never touches a finished report',
              (td / 'step-3.superseded-1' / 'builder-L3.md').read_text(encoding='utf-8') == hdr('builder-L3.md', '## Status\ndone\n'))
        # the newest superseded attempt holding the report is the previous one
        td = l_task({'step-3.superseded-1': ['builder-L3.md'], 'step-3.superseded-2': ['builder-L3.md']},
                    cites={3: 'builder-L3.md'})
        run_main(['split', str(td)])
        h3 = rd(td, 3)
        check('(L) with two superseded attempts the citation keeps the previous (highest k) attempt',
              'step-3.superseded-2/builder-L3.md' in h3 and 'superseded-1' not in h3)
        # an explicit superseded citation keeps its attempt identity
        td = l_task({'step-3.superseded-1': ['builder-L3.md'], 'step-3.superseded-2': ['builder-L3.md']}, cites={3: 'builder-L3.md'})
        pl = td / 'planner-L3.md'
        pl.write_text(pl.read_text(encoding='utf-8').replace('step-3/builder-L3.md', 'step-3.superseded-1/builder-L3.md'), encoding='utf-8')
        rc, _, err = run_main(['split', str(td)])
        h3 = rd(td, 3)
        check('(L) an explicit step-3.superseded-1 citation is kept, not moved to the newest attempt',
              rc == 0 and 'step-3.superseded-1/builder-L3.md' in h3 and 'superseded-2' not in h3 and 'rewrote' not in err)
        # lint refusals
        td = l_task(rep)
        run_main(['split', str(td)])
        h3p = ln(td, 3)
        good = h3p.read_text(encoding='utf-8') if h3p.is_file() else ''
        rc, out, err = run_main(['lint', str(h3p)])
        check('(L) lint passes a step handoff whose citations all exist', rc == 0 and out.startswith('steps lint: ok'))
        h3p.write_text(good + '\nAlso read .sdlc/0001-x/step-3.superseded-1/builder-L9.md.\n', encoding='utf-8')
        rc, _, err = run_main(['lint', str(h3p)])
        check('(L) lint refuses an absent cited .sdlc path and names it',
              rc == 1 and 'builder-L9.md' in err and 'does not exist' in err)
        h3p.write_text(good.replace('step-3.superseded-1/builder-L3.md', 'step-3/builder-L3.md'), encoding='utf-8')
        rc, _, err = run_main(['lint', str(h3p)])
        check('(L) lint refuses a current-step report path that has a superseded sibling and names the fix',
              rc == 1 and 'step-3.superseded-1/builder-L3.md' in err and 'does not exist' in err)
        (td / 'step-3' / 'builder-L3.md').write_text(hdr('builder-L3.md', '## Status\ndone\n'), encoding='utf-8')
        rc, _, err = run_main(['lint', str(h3p)])
        check('(L) path reuse: a later new builder-L3.md in step-3/ does not satisfy a link meant for the previous build',
              rc == 1 and 'prior attempt' in err and 'step-3.superseded-1/builder-L3.md' in err)
        # a step with no superseded sibling may cite another live step's report
        td = l_task({}, live={'step-1': ['builder-L2.md']}, cites={3: 'builder-L3.md'})
        h = ln(td, 3)
        h.parent.mkdir()
        h.write_text('## Task goal\ng\n\n## Step 3: s\nlevel: L1\nRead .sdlc/0001-x/step-1/builder-L2.md first.\n', encoding='utf-8')
        check('(L) a citation of another live step\'s existing report passes lint',
              run_main(['lint', str(h)])[0] == 0 and run_main(['lint', str(h.parent)])[0] == 0)
        # an uncited-placeholder or glob path is not a citation
        h.write_text('## Task goal\ng\n\nWrite .sdlc/<task>/step-<n>/builder-L3.md and see .sdlc/0001-x/step-*/x.md.\n', encoding='utf-8')
        check('(L) placeholder and glob paths are not checked', run_main(['lint', str(h)])[0] == 0)
        # under work_root: docs/work a step handoff's citations of the work root are checked too (T-0622)
        wtop = lroot / 'wr'
        (wtop / '.sdlc').mkdir(parents=True)
        (wtop / '.sdlc' / 'config').write_text('work_root: docs/work\n', encoding='utf-8')
        (wtop / 'docs' / 'work' / '0001-x').mkdir(parents=True)
        (wtop / 'docs' / 'work' / '0001-x' / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
        wh = wtop / '.sdlc' / 'runtime' / 'tasks' / '0001-x' / 'step-1' / 'handoff.md'
        wh.parent.mkdir(parents=True)
        wh.write_text('## Task goal\ng\n\n## Step 1: s\nlevel: L1\nRead docs/work/0001-x/handoff.md first.\n', encoding='utf-8')
        rc_ok = run_main(['lint', str(wh)])[0]
        wh.write_text('## Task goal\ng\n\n## Step 1: s\nlevel: L1\nRead `docs/work/0001-x/gone.md` first.\n', encoding='utf-8')
        rc, _, err = run_main(['lint', str(wh)])
        check('(L) work_root: lint checks a cited docs/work path and names an absent one',
              rc_ok == 0 and rc == 1 and 'docs/work/0001-x/gone.md' in err and 'does not exist' in err)
        check('(L) work_root: sdlc_root of a docs/work task is the .sdlc state root',
              sdlc_root(wtop / 'docs' / 'work' / '0001-x') == wtop.resolve() / '.sdlc')
        # a plan defect is not raised for a Read first path split will rewrite; a truly absent one still is
        td = l_task({'step-3.superseded-1': ['builder-L3.md']}, cites={3: 'builder-L3.md'})
        check('(L) plan lint accepts a Read first path that split will rewrite', run_main(['lint', str(td)])[0] == 0)
        td = l_task({'step-3.superseded-1': ['verifier-L3.md']}, cites={3: 'builder-L3.md'})
        rc, _, err = run_main(['lint', str(td)])
        check('(L) plan lint still refuses a Read first path no superseded folder holds',
              rc == 1 and 'does not exist' in err)
        # absolute citations resolve exactly as written (T-0393)
        td = l_task({}, cites={3: 'builder-L3.md'})
        own = ln(td, 3)
        own.parent.mkdir(parents=True, exist_ok=True)
        sh = lroot / f'shared{counter[0]}' / '.sdlc' / 'tickets' / '0001-evidence'
        sh.mkdir(parents=True)
        (sh / 'verifier.md').write_text('x\n', encoding='utf-8')
        ab = f'{sh}/verifier.md'
        own.write_text(f'## Task goal\ng\n\nRead {ab}:12 first.\n', encoding='utf-8')
        check('(L) an existing absolute target outside the owned tree passes with no local mirror',
              run_main(['lint', str(own)])[0] == 0)
        (sh / 'verifier.md').unlink()
        mir = td.parent / '.sdlc' / 'tickets' / '0001-evidence'
        mir.mkdir(parents=True)
        (mir / 'verifier.md').write_text('y\n', encoding='utf-8')
        rc, _, err = run_main(['lint', str(own)])
        check('(L) a nonexistent absolute target fails even with a local same-suffix file, naming the original',
              rc == 1 and 'does not exist' in err and ab in err)
        own.write_text('## Task goal\ng\n\nRead .sdlc/tickets/0001-evidence/verifier.md and '
                       '../.sdlc/tickets/0001-evidence/verifier.md.\n', encoding='utf-8')
        check('(L) relative and repository-root citations still resolve against the owned base',
              run_main(['lint', str(own)])[0] == 0)
        sup = sh / 'step-1.superseded-1'
        sup.mkdir()
        (sup / 'builder-L3.md').write_text('z\n', encoding='utf-8')
        own.write_text(f'## Task goal\ng\n\nRead {sh}/step-1/builder-L3.md:5.\n', encoding='utf-8')
        rc, _, err = run_main(['lint', str(own)])
        check('(L) superseded-report guidance names the original absolute target',
              rc == 1 and f'{sh}/step-1/builder-L3.md' in err and f'{sh}/step-1.superseded-1/builder-L3.md' in err)
        # T-0457: a path the step creates and a path from another repo are not citations to refuse
        def f_lint(body, sub=''):
            td = l_task({}, cites={3: 'builder-L3.md'})
            h = ln(td, 3)
            h.parent.mkdir(parents=True, exist_ok=True)
            h.write_text('## Task goal\ng\n\n## Step 3: s\nlevel: L1\n' + body, encoding='utf-8')
            return run_main(['lint', str(h)])
        miss = '.sdlc/0001-x/sample.py'
        rc, _, err = f_lint(f'### Do\nRead {miss} first.\n')
        check('(L) T-0457 control: a missing cited repo file is still refused', rc == 1 and miss in err)
        rc, _, err = f_lint(f'### Do\nCreate {miss} with the sample.\n')
        check('(L) T-0457: a path a ### Do line creates passes lint', rc == 0 and err == '')
        rc, _, err = f_lint(f'### Do\nBuild it.\nOutputs: `{miss}`\n')
        check('(L) T-0457: a path on an Outputs line passes lint', rc == 0 and err == '')
        rc, _, err = f_lint(f'### Do\nBuild it. [creates: {miss}]\n### Acceptance criteria\n- `python3 {miss}` runs\n')
        check('(L) T-0457: a [creates: <path>] marker passes lint', rc == 0 and err == '')
        rc, _, err = f_lint(f'### Do\nBuild it.\n### Acceptance criteria\n- (red) `python3 {miss}`\n')
        check('(L) T-0457: a path inside a (red) criterion span passes lint', rc == 0 and err == '')
        rc, _, err = f_lint(f'### Do\nBuild it.\n### Acceptance criteria\n- `python3 {miss}`\n')
        check('(L) T-0457 control: the same path in a plain criterion span is still refused', rc == 1 and miss in err)
        rc, _, err = f_lint(f'### Do\nCreate {miss}.\nRead .sdlc/0001-x/typo.md.\n')
        check('(L) T-0457 control: a create target does not exempt another missing path',
              rc == 1 and 'typo.md' in err and 'sample.py' not in err)
        rc, _, err = f_lint('### Do\nOther repo: ui-kit-maison\nRead ui-kit-maison/.sdlc/tickets/0001-x/handoff.md.\n')
        check('(L) T-0457: a path prefixed with a declared other repo name passes lint', rc == 0 and err == '')
        rc, _, err = f_lint('### Do\nRead ui-kit-maison/.sdlc/tickets/0001-x/handoff.md.\n')
        check('(L) T-0457 control: the same prefix with no Other repo line is still refused',
              rc == 1 and 'tickets/0001-x/handoff.md' in err)
        rc, _, err = f_lint("### Do\nBuild it.\n### Acceptance criteria\n- `python3 -c \"open(P + '/.sdlc/out/x.json')\"` exits 0\n")
        check('(L) T-0474: a citation whose prefix is exactly / is no citation', rc == 0 and err == '')
        rc, _, err = f_lint("### Do\nBuild it.\n### Acceptance criteria\n- `python3 -c \"open(P + '.sdlc/out/x.json')\"` exits 0\n")
        check('(L) T-0474 control: the same path with no leading / is still refused', rc == 1 and '.sdlc/out/x.json' in err)
        gr = lroot / f'gitrepo{counter[0]}'
        subprocess.run(['git', 'init', '-q', str(gr)], check=True, capture_output=True)
        gh = gr / '.sdlc' / '0001-x' / 'step-1' / 'handoff.md'
        gh.parent.mkdir(parents=True)
        far = lroot / f'elsewhere{counter[0]}' / '.sdlc' / 'tickets' / '0001-x' / 'verifier.md'
        gh.write_text(f'## Task goal\ng\n\n## Step 1: s\nlevel: L1\n### Do\nRead {far}.\n', encoding='utf-8')
        rc, _, err = run_main(['lint', str(gh)])
        check('(L) T-0457: an absolute path outside the repository passes lint', rc == 0 and err == '')
        near = gr / '.sdlc' / 'tickets' / '0001-x' / 'verifier.md'
        gh.write_text(f'## Task goal\ng\n\n## Step 1: s\nlevel: L1\n### Do\nRead {near}.\n', encoding='utf-8')
        rc, _, err = run_main(['lint', str(gh)])
        check('(L) T-0457 control: a missing absolute path inside the repository is still refused',
              rc == 1 and str(near) in err)

        # no input hashing change: dispatch.py owns that; here only prove split output is stable when nothing is stale
        td = l_task(rep)
        run_main(['split', str(td)])
        before = {n: rd(td, n) for n in (3, 4, 9)}
        run_main(['split', str(td)])
        check('(L) a second split gives byte-identical handoffs',
              before == {n: rd(td, n) for n in (3, 4, 9)} and all(before.values()))

        # T-0408 held criteria: unmet-dependency and deferred are not defects; open lists them; swap keeps the clause
        T_FM = ('---\nid: T-0307\ntitle: "schema"\ntype: chore\nstatus: {st}\nsize: L1\npriority: P2\ndepends: []\n'
                'created: 2026-10-09\n---\n\n## Goal\nx\n')
        H_STEP = ('## Task goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nd\n### Acceptance criteria\n'
                  '- `test -f a` [needs: T-0307]\n- `test -f b` [owner: integration]\n- `test -f c`\n')
        H_UNMET = ('## Verdict\nfail\n\n## Criteria\n- #1 `test -f a`: unmet-dependency T-0307. Evidence: no a\n\n'
                   '## For the next attempt\nunmet-dependency: T-0307\n- #1 unmet-dependency\n')
        H_DEFER = ('## Verdict\nfail\n\n## Criteria\n- #2 `test -f b`: deferred integration. Evidence: no b\n\n'
                   '## For the next attempt\ndeferred: integration\n- #2 deferred\n')
        H_PASSHELD = ('## Verdict\npass\n\n## Criteria\n- #2 `test -f b`: deferred integration. Evidence: no b\n\n'
                      '## For the next attempt\nNone\n')
        H_UNDECL = ('## Verdict\nfail\n\n## Criteria\n- #3 `test -f c`: deferred integration. Evidence: no c\n\n'
                    '## For the next attempt\ndeferred: integration\n- #3 deferred\n')
        SETTLE = ('## Verdict\npass\n\n## Criteria\n- #step-1#2 `test -f b`: pass. Evidence: b exists\n\n'
                  '## For the next attempt\nNone\n\n## Settles\n- step-1#2\n')

        def held_task(step_files, t_status='ready', step_handoff=H_STEP, task_files=(), ticket_ac=None):
            """<root>/.sdlc/{0307-schema, task/{handoff.md, step-1, step-2}}: returns the task dir."""
            count[0] += 1
            root = tmp / f'held{count[0]}' / '.sdlc'
            (root / '0307-schema').mkdir(parents=True)
            (root / '0307-schema' / 'handoff.md').write_text(T_FM.format(st=t_status), encoding='utf-8')
            t = root / 'task'
            s1 = t / 'step-1'
            s1.mkdir(parents=True)
            (t / 'handoff.md').write_text('## Goal\ng\n' + (ticket_ac or ''), encoding='utf-8')
            (s1 / 'handoff.md').write_text(step_handoff, encoding='utf-8')
            for d, files in ((s1, step_files), (t, task_files)):
                for name, text in files:
                    (d / name).write_text(hdr(name, text), encoding='utf-8')
                if files:
                    (d / 'runs.jsonl').write_text(''.join(f'{{"file": "{n}"}}\n' for n, _ in files), encoding='utf-8')
            return t

        B = ('builder-L2.md', DONE)
        t = held_task([B, ('verifier-L1.md', H_UNMET)])
        check('held: unmet-dependency with T-0307 still ready -> wait, not a replan or rebuild',
              nxt(t / 'step-1', 'wait'))
        t = held_task([B, ('verifier-L1.md', H_UNMET)], t_status='done')
        check('held: control, T-0307 done -> reverify the recheck, not wait', nxt(t / 'step-1', 'reverify L1'))
        t = held_task([B, ('verifier-L1.md', H_DEFER)])
        check('held: deferred with a declared owner -> deferred', nxt(t / 'step-1', 'deferred'))
        t = held_task([B, ('verifier-L1.md', H_DEFER)], step_handoff=H_STEP.replace(' [owner: integration]', ''))
        check('held: control, the same result with no owner clause -> counted rebuild, not deferred',
              nxt(t / 'step-1', 'rebuild L2'))
        t = held_task([B, ('verifier-L1.md', H_UNDECL)])
        check('held: a hold on a criterion with no clause -> rebuild', nxt(t / 'step-1', 'rebuild L2'))
        t = held_task([B, ('verifier-L1.md', H_DEFER), ('verifier-L1-2.md', H_DEFER), ('verifier-L1-3.md', H_DEFER)])
        check('held: repeated held results are not counted fails -> still deferred, never bump',
              nxt(t / 'step-1', 'deferred'))
        t = held_task([B, ('verifier-L1.md', H_PASSHELD)])
        check('held: Verdict pass beside a deferred line is never done -> reverify', nxt(t / 'step-1', 'reverify L1'))
        saved_states = results.criteria_states
        results.criteria_states = lambda path: []
        try:
            got = next_action(t / 'step-1')[0]
        finally:
            results.criteria_states = saved_states
        check(f'held: control, with the criteria reader stubbed empty the same result is done ({got})', got == 'done')
        t = held_task([B, ('verifier-L1.md', H_DEFER)])
        rc, out, err = run_main(['open', str(t)])
        check('held: open lists the deferred criterion', rc == 0 and out == 'step-1#2\tdeferred\tintegration\n' and err == '')
        t = held_task([B, ('verifier-L1.md', H_DEFER)], task_files=[('verifier-L2.md', SETTLE)])
        rc, out, err = run_main(['open', str(t)])
        check('held: a task-dir result that settles the ref empties open', rc == 0 and out == '' and err == '')
        t = held_task([B, ('verifier-L1.md', H_DEFER)], task_files=[('verifier-L2.md', SETTLE.replace('pass\n\n## Crit', 'fail\n\n## Crit', 1).replace(': pass.', ': fail.'))])
        rc, out, err = run_main(['open', str(t)])
        check('held: control, a settling result that fails the ref leaves it out of open as an ordinary fail',
              rc == 0 and out == '')
        t = held_task([B, ('verifier-L1.md', H_UNMET)], t_status='done')
        rc, out, err = run_main(['open', '--explain', str(t)])
        check('held: open --explain names a stale unmet-dependency',
              rc == 0 and out.startswith('step-1#1\tunmet-dependency\tT-0307') and 'stale' in out)
        t = held_task([], ticket_ac='\n## Acceptance criteria\n- [ ] ships it [owner: integration]\n',
                      task_files=[('verifier-L2.md', '## Verdict\nfail\n\n## Criteria\n- #1 ships it: deferred integration. '
                                   'Evidence: not yet\n\n## For the next attempt\ndeferred: integration\n')])
        rc, out, err = run_main(['open', str(t)])
        check('held: a bare #k in a task-dir result is ticket#k', rc == 0 and out == 'ticket#1\tdeferred\tintegration\n')
        # T-0684: a deferred ref listed under ## Settled by owner by its declared owner is pass; another owner is not
        H_OWNED = ('## Verdict\nfail\n\n## Criteria\n- #1 the review passes: deferred conductor. Evidence: owner stage\n\n'
                   '## For the next attempt\ndeferred: conductor\n\n## Settled by owner\n'
                   '- ticket#1 {who}: docs/review.md at abc1234\n')
        for who, want in (('conductor', ''), ('integration', 'ticket#1\tdeferred\tconductor\n')):
            t = held_task([], ticket_ac='\n## Acceptance criteria\n- [ ] the review passes [owner: conductor]\n',
                          task_files=[('verifier-L2.md', H_OWNED.format(who=who))])
            rc, out, err = run_main(['open', str(t)])
            check(f'held: T-0684 a ref settled by {who} ' + ('empties open' if not want else 'stays open (control)'),
                  rc == 0 and out == want)
        # T-0696: a Criteria line criteria_states cannot parse keeps a settled hold from reading as pass
        for extra, want in (('', True), ('- #2 y FAILED no evidence\n', False)):
            t = held_task([], ticket_ac='\n## Acceptance criteria\n- [ ] the review passes [owner: conductor]\n',
                          task_files=[('verifier-L2.md', H_OWNED.format(who='conductor').replace(
                              'owner stage\n\n', 'owner stage\n' + extra + '\n', 1))])
            check('held: T-0696 owner_settled_hold ' + ('is True for a fully parsed result' if want
                  else 'is False beside an unparsed Criteria line'), owner_settled_hold(t / 'verifier-L2.md') is want)
        t = held_task([B, ('verifier-L1.md', H_DEFER)])
        (t / 'step-2').mkdir()
        (t / 'step-2' / 'handoff.md').write_text('## Task goal\ng\n\n## Step 2: y\nlevel: L1\n', encoding='utf-8')
        rc, out, err = run_main(['resume', str(t)])
        check('held: resume skips a deferred step for the next unfinished one',
              rc == 0 and out.splitlines()[:2] == [str(t / 'step-2'), 'build L1'])
        os.remove(t / 'step-2' / 'handoff.md')
        (t / 'step-2' / 'handoff.md').write_text('## Task goal\ng\n\n## Step 2: y\nlevel: L1\n', encoding='utf-8')
        (t / 'step-2' / 'builder-L1.md').write_text(hdr('builder-L1.md', DONE), encoding='utf-8')
        (t / 'step-2' / 'verifier-L1.md').write_text(hdr('verifier-L1.md', PASS), encoding='utf-8')
        rc, out, err = run_main(['resume', str(t)])
        check('held: resume with only held steps left prints the held action, never done',
              rc == 0 and out.splitlines()[:2] == [str(t / 'step-1'), 'deferred'] and 'every other step passed' in out)
        check('held: merge_class names the owner of a held lane',
              merge_class('fail', '', [], 'integration') == ('integration', 'held integration')
              and merge_class('fail', '', []) == ('integration', 'verifier fail'))
        # lint refuses a malformed bracket clause; a good one passes
        for bad in ('[bogus: x]', '[owner: ]', '[owner: Bad Owner]', '[needs: nowhere]', '[owner: a; owner: b]'):
            d = task(plan=PLAN.replace('- one works', f'- `test -f a` {bad}'))
            rc, _, err = run_main(['lint', str(d)])
            check(f'held: lint refuses the clause {bad}', rc == 1 and 'bracket clause' in err
                  and err.strip().splitlines()[-1].startswith('plan defect:'))
        d = task(plan=PLAN.replace('- one works', '- `test -f a` [stage: integration; owner: integration]\n- `test -f b` [needs: T-0307, file:a/b, cap:x]'))
        rc, out, err = run_main(['lint', str(d)])
        check('held: lint accepts stage, owner and needs clauses', rc == 0 and out.startswith('steps lint: ok'))

        # (circ) T-0415: lint refuses a criterion that reads its own step's verifier result (it can pass only after
        # that verifier passes) unless its line is held. T-0543: steps.py lint records nothing; a split refusal appends
        # one line per finding under ## Plan review in the task handoff, once per text; a clean run writes nothing
        def review_lines(d):
            h = d / 'handoff.md'
            return [x for x in h.read_text(encoding='utf-8').splitlines() if ' plan defect at split: ' in x] if h.is_file() else []

        def no_refusals(root):
            return not any(pathlib.Path(root).rglob('refusals.jsonl'))

        own = 'grep -q pass .sdlc/x/step-2/verifier-L2.md'
        circ_msg = "acceptance criterion reads this step's own verifier result, so it can pass only after the verifier passes"
        circ_hint = '  move it to a later step, or declare it held with a trailing [stage: ..., owner: ...] clause'
        d = task(plan=PLAN.replace('- two works', f'- `{own}`'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        d2 = task(plan=PLAN.replace('- one works', '- `test -s verifier-L1.md`'))
        rc2, _, err2 = run_main(['lint', str(d2 / 'planner-L2.md')])
        d3 = task(plan=PLAN.replace('- two works', '- `grep -q pass step-1/verifier-L1.md step-2/verifier-L1.md`'))
        rc3, _, err3 = run_main(['lint', str(d3 / 'planner-L2.md')])
        check('(circ) lint refuses a criterion that reads its own step verifier result',
              rc == 1 and out == '' and f'step 2: {circ_msg}: {own}\n{circ_hint}\n' in err
              and err.strip().splitlines()[-1] == PLAN_DEFECT
              and rc2 == 1 and f'step 1: {circ_msg}: test -s verifier-L1.md' in err2
              and rc3 == 1 and f'step 2: {circ_msg}: grep -q pass step-1' in err3)
        d = task(plan=PLAN.replace('- two works', f'- `{own}` [stage: integration; owner: integration]'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(circ) negative control: the same criterion with a held clause passes lint',
              rc == 0 and out.startswith('steps lint: ok') and circ_msg not in err and review_lines(d) == [])
        gl = 'grep -q pass .sdlc/x/step-2/verifier-L*.md'
        d = task(plan=PLAN.replace('- two works', f'- `{gl}`'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        d2 = task(plan=PLAN.replace('- two works', f'- `{gl}` [stage: integration; owner: integration]'))
        rc2, out2, err2 = run_main(['lint', str(d2 / 'planner-L2.md')])
        check('(circ) the glob form verifier-L* is refused like the digit form, and a held clause exempts it',
              rc == 1 and f'step 2: {circ_msg}: {gl}' in err and err.strip().splitlines()[-1] == PLAN_DEFECT
              and rc2 == 0 and out2.startswith('steps lint: ok') and circ_msg not in err2)
        d = task(plan=PLAN.replace('- two works', '- `grep -q pass .sdlc/x/step-1/verifier-L2.md`'))
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        check('(circ) negative control: a criterion that reads an earlier step verifier result passes lint',
              rc == 0 and out.startswith('steps lint: ok') and circ_msg not in err and review_lines(d) == [])
        # T-0613: a verifier result at an absolute path outside the repository belongs to another repo's ticket
        foreign = tmp / 'circ-foreign-repo' / '.sdlc' / 'runtime' / 'tasks' / '0247-x' / 'verifier-L1.md'
        d = o_repo(f'`test -s {foreign}`')
        rc, out, err = run_main(['lint', str(d / 'planner-L2.md')])
        d2 = o_repo(f'`test -s {foreign.with_name("verifier-L1.attempt.json")}`')
        rc2, out2, err2 = run_main(['lint', str(d2 / 'planner-L2.md')])
        check('(circ) T-0613: a verifier result at an absolute path outside the repository passes lint',
              rc == 0 and out.startswith('steps lint: ok') and circ_msg not in err
              and rc2 == 0 and out2.startswith('steps lint: ok') and circ_msg not in err2)
        d = o_repo('`test -s verifier-L1.md`')
        rc, _, err = run_main(['lint', str(d / 'planner-L2.md')])
        d2 = o_repo(f'`test -s {tmp / f"o-repo{count[0] + 1}" / ".sdlc" / "x" / "verifier-L1.md"}`')
        rc2, _, err2 = run_main(['lint', str(d2 / 'planner-L2.md')])
        check('(circ) T-0613 control: a relative or in-repo absolute verifier result is still refused',
              rc == 1 and circ_msg in err and rc2 == 1 and circ_msg in err2)

        d = o_repo('`test -s .sdlc/x/step-1/verifier-L1.md`')
        (d / 'step-3').mkdir()
        (d / 'step-3' / 'handoff.md').write_text('## Task goal\ng\n\n## Step 3: y\nlevel: L1\n### Do\n'
                                                 'read .sdlc/x/missing-report.md\n', encoding='utf-8')
        before = snapshot(d.parent.parent)
        rc, _, err = run_main(['lint', str(d)])
        rc_h, _, err_h = run_main(['lint', str(d / 'step-3')])
        check('(T-0543) a lint refusal writes nothing',
              rc == 1 and circ_msg in err and rc_h == 1 and 'missing-report.md' in err_h
              and snapshot(d.parent.parent) == before and review_lines(d) == [] and no_refusals(d.parent.parent))
        old_h = (d / 'handoff.md').read_text(encoding='utf-8')
        rc_b, _, err_b = run_main(['split', str(d), '--only', '1'])
        rows = review_lines(d)
        rc_c, _, err_c = run_main(['split', str(d)])
        new_h = (d / 'handoff.md').read_text(encoding='utf-8')
        today = time.strftime('%Y-%m-%d', time.gmtime())
        check('(T-0543) a split refusal appends one ## Plan review line',
              rc_b == 1 and circ_msg in err_b and rc_c == 1 and len(rows) == 1
              and rows[0] == f'- {today} plan defect at split: step 1: {circ_msg}: test -s .sdlc/x/step-1/verifier-L1.md'
              and review_lines(d) == rows and new_h == old_h + f'\n## Plan review\n{rows[0]}\n'
              and no_refusals(d.parent.parent))

        d = o_repo('(guard) `test -f circ-missing`')
        rc, _, _ = run_main(['split', str(d), '--only', '1'])
        g = review_lines(d)
        d = o_repo('(red) `test -d .sdlc`')
        rc_r, _, _ = run_main(['split', str(d), '--only', '1'])
        r = review_lines(d)
        check('(circ) split records a red guard and a red-first refusal under ## Plan review',
              rc == 1 and len(g) == 1 and g[0].endswith(': (guard) criterion is red now (exit 1): test -f circ-missing')
              and ' plan defect at split: step 1: ' in g[0]
              and rc_r == 1 and len(r) == 1 and ' plan defect at split: step 1: `test -d .sdlc` is green now' in r[0])
        d = o_repo('`test -s .sdlc/x/step-1/verifier-L1.md`')
        os.chmod(d / 'handoff.md', 0o444)
        try:
            rc, out, err = run_main(['split', str(d)])
        finally:
            os.chmod(d / 'handoff.md', 0o644)
        check('(circ) a read-only handoff records nothing and the refusal is unchanged',
              rc == 1 and out == '' and circ_msg in err and 'Traceback' not in err and review_lines(d) == [])
        # swap keeps the bracket clause
        S_HELD = S_HANDOFF.replace('(old check)', '[owner: integration]')
        d = s_step([('builder-L2.md', DONE), ('verifier-L1.md', swap_v(new='`test -f handoff.md`'))], handoff=S_HELD)
        swap_refused('a swap that drops the bracket clause', d, 'bracket clause')
        d = s_step([('builder-L2.md', DONE), ('verifier-L1.md', swap_v(new='`test -f handoff.md` [owner: other]'))], handoff=S_HELD)
        swap_refused('a swap that changes the bracket clause', d, 'bracket clause')
        d = s_step([('builder-L2.md', DONE), ('verifier-L1.md', swap_v(new='`test -f handoff.md` [owner: integration]'))], handoff=S_HELD)
        rc, out, err = run_main(['swap', str(d)])
        check('held: control, a swap that keeps the clause applies', rc == 0 and '[owner: integration]' in (d / 'handoff.md').read_text(encoding='utf-8'))

        # (profile) T-0510: under `profile: inner-loop` a (guard) equal to a `full_gate:` command is a plan defect
        def il_plan(name, config, handoff=HANDOFF):
            d = tmp / name / '.sdlc' / 't1'
            d.mkdir(parents=True)
            (d.parent / 'config').write_text(config, encoding='utf-8')
            (d / 'handoff.md').write_text(handoff, encoding='utf-8')
            (d / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN.replace('- one works', '- (guard) `python3 suite.py`')),
                                             encoding='utf-8')
            return d / 'planner-L2.md'
        IL = 'profile: inner-loop\nlocal_gate: python3 check.py\nfull_gate: python3 suite.py\n'
        rc, out, err = run_main(['lint', str(il_plan('il-on', IL))])
        check('(profile) a (guard) on the full gate lints with the plan defect',
              rc == 1 and 'plan defect: full gate `python3 suite.py` owned by the merge gate' in err)
        rc, out, err = run_main(['lint', str(il_plan('il-off', IL.replace('profile: inner-loop\n', '')))])
        check('(profile) control: the same plan without the profile line lints clean', rc == 0 and 'plan defect' not in err)
        rc, out, err = run_main(['lint', str(il_plan('il-default', IL, HANDOFF.replace('## Goal', 'profile: default\n\n## Goal')))])
        check('(profile) control: a handoff with profile: default lints clean', rc == 0 and 'plan defect' not in err)
        rc, out, err = run_main(['lint', str(il_plan('il-other', IL.replace('python3 suite.py\n', 'python3 other.py\n')))])
        check('(profile) control: a (guard) that is not the full gate lints clean', rc == 0 and 'plan defect' not in err)

        # (parity) T-0513: a (parity) criterion names two image paths and a property list
        def parity_plan(name, criterion):
            d = tmp / name
            d.mkdir(parents=True)
            (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
            (d / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN.replace('- one works', criterion)), encoding='utf-8')
            return d / 'planner-L2.md'
        rc, out, err = run_main(['lint', str(parity_plan('par-ok', '- (parity) `python3 shot.py out/real.png` writes `out/real.png`; against `mock/card.png`: column count, gutter, filled primary button'))])
        check('(parity) a capture command, two image paths and a property list lint clean', rc == 0 and 'parity' not in err)
        rc, out, err = run_main(['lint', str(parity_plan('par-one', '- (parity) `python3 shot.py out/real.png` writes `out/real.png`: column count, gutter'))])
        check('(parity) a line with one image path is refused', rc == 1 and 'names fewer than two image paths' in err and 'plan defect' in err)
        rc, out, err = run_main(['lint', str(parity_plan('par-noprops', '- (parity) `python3 shot.py out/real.png` writes `out/real.png`; against `mock/card.png`'))])
        check('(parity) a line with no property list is refused', rc == 1 and 'names no property list' in err and 'plan defect' in err)
        rc, out, err = run_main(['lint', str(parity_plan('par-tag', '- (guard) `python3 shot.py out/real.png` writes `out/real.png`'))])
        check('(parity) control: a line without the (parity) tag is not checked', rc == 0 and 'parity' not in err)

        # (records dir) T-0540: step dirs live in the records dir (order.records_dir); handoff.md and skips.md stay
        # in the task folder. Legacy control: a task folder that already records in place keeps its step dirs there.
        sd = tmp / 'rd' / '.sdlc'
        rt = sd / 'runtime' / 'tasks'
        tf, rf = sd / '0001-r', rt / '0001-r'
        tf.mkdir(parents=True)
        rf.mkdir(parents=True)
        (tf / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
        (rf / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN), encoding='utf-8')
        rc, out, err = run_main(['split', str(tf)])
        rc2, out2, _ = run_main(['resume', str(tf)])
        rc3, out3, _ = run_main(['next', str(tf / 'step-1')])
        check('(records dir) split writes step dirs in the records dir',
              rc == 0 and out.split() == [str(rf / 'step-1' / 'handoff.md'), str(rf / 'step-2' / 'handoff.md')]
              and (rf / 'step-1' / 'handoff.md').read_text(encoding='utf-8') == want1
              and sorted(p.name for p in tf.iterdir()) == ['handoff.md']
              and (sd / 'runtime' / '.gitignore').read_text(encoding='utf-8') == '*\n'
              and rc2 == 0 and out2.splitlines()[0] == str(rf / 'step-1')
              and rc3 == 0 and out3.splitlines()[0] == 'build L2')
        lt = sd / '0002-s'
        lt.mkdir()
        (lt / 'handoff.md').write_text(HANDOFF.replace('title: "x"\n', 'title: "x"\nsize: L3\n'), encoding='utf-8')
        rc, out, _ = run_main(['lane', str(rt / '0002-s')])
        skips = lt / 'skips.md'
        check('(records dir) lane keeps skips.md in the task folder',
              rc == 0 and out.splitlines()[0] == 'full' and skips.is_file()
              and '- lane: full; point: before planning;' in skips.read_text(encoding='utf-8')
              and not (rt / '0002-s').exists() and sorted(p.name for p in lt.iterdir()) == ['handoff.md', 'skips.md'])
        lg = sd / '0003-l'
        lg.mkdir()
        (lg / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
        (lg / 'planner-L2.md').write_text(hdr('planner-L2.md', PLAN), encoding='utf-8')
        (lg / 'runs.jsonl').write_text('{"file": "planner-L2.md"}\n', encoding='utf-8')
        rc, out, _ = run_main(['split', str(lg)])
        check('(records dir) legacy control: a task folder holding runs.jsonl keeps its step dirs in place',
              rc == 0 and (lg / 'step-1' / 'handoff.md').read_text(encoding='utf-8') == want1
              and (lg / 'step-2' / 'handoff.md').is_file() and not (rt / '0003-l').exists())
        # a hand-written task-side step handoff whose records twin dispatch.py prepare created (empty of handoffs)
        hw = sd / '0004-h'
        (hw / 'step-1').mkdir(parents=True)
        (hw / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
        (hw / 'step-1' / 'handoff.md').write_text('## Task goal\ng\n\n## Step 1: x\nlevel: L2\n', encoding='utf-8')
        (rt / '0004-h' / 'step-1').mkdir(parents=True)
        rc, out, err = run_main(['lint', str(hw / 'step-1')])
        rc2, out2, err2 = run_main(['next', str(hw / 'step-1')])
        rc3, out3, err3 = run_main(['resume', str(hw)])
        check('(records dir) a task-side step handoff with an empty records twin: lint, next and resume read it',
              rc == 0 and 'steps lint: ok' in out and rc2 == 0 and out2.splitlines()[0] == 'build L2'
              and rc3 == 0 and out3.splitlines()[:2] == [str(rt / '0004-h' / 'step-1'), 'build L2'])
        # a hand-written task-side step-1/ with a records dir that holds no step-1 twin: step_dirs lists the task side
        ts = sd / '0005-t'
        (ts / 'step-1').mkdir(parents=True)
        (ts / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
        (rt / '0005-t').mkdir(parents=True)
        got = step_dirs(ts).get(1)
        check('(records dir) step_dirs lists a task-side step dir',
              got is not None and os.path.realpath(got) == os.path.realpath(ts / 'step-1'))

    if misses:
        print('steps selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('steps selftest: PASS')
    return 0


def main(argv):
    ap = argparse.ArgumentParser(
        prog='steps.py', description=__doc__.split('\n')[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='lint: after a clean lint, a plan that meets the lean plan conditions (planner L1 or L2,\n'
               'no unresolved: assumption, steps at L1 to L3, no Merge step, no replan, no ## Plan review\n'
               'line in handoff.md) gets one stderr line per finding, "steps lint: warning: ...", for more\n'
               'than two steps or a step with one acceptance criterion; stdout and exit 0 stay unchanged.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('split', help='write step-<n>/handoff.md for each step of a plan')
    p.add_argument('target', help='a planner-*.md file, or a task dir (its newest planner-*.md by recorded run order)')
    p.add_argument('--only', type=int, action='append', metavar='N',
                   help='write only step N (repeatable); runs its (guard) criteria first, with SDLC_BASE_SHA=HEAD')
    p.add_argument('--guard-timeout', type=float, default=None, metavar='SECONDS',
                   help='per-guard timeout for --only; it overrides any "guard timeout: <seconds>" line '
                        '(default: the step block\'s line, else the plan\'s line outside every step, else 300); '
                        'a timeout is a red guard')
    p.add_argument('--tree', default=None, metavar='PATH',
                   help='the work tree --only runs its (guard) and (red) spans in (default: the git toplevel '
                        'of the plan folder); use the lane worktree when the plan folder is in another checkout')
    p.add_argument('--override-review', default=None, metavar='REASON',
                   help='split a plan whose newest plan review says replan anyway (the user\'s call); records '
                        '"review override: <review file>: <reason>" under ## Plan review in handoff.md; '
                        'a blocked review is never overridden')
    p.add_argument('--supersede', action='store_true',
                   help='rename a chosen step-<n>/ that holds builder or verifier output to the next free '
                        'step-<n>.superseded-<k>/ after every check passes, then split')
    p = sub.add_parser('lint', help='check that criterion commands parse under bash -n; writes nothing')
    p.add_argument('target', help='a planner-*.md file, or a task dir (its newest planner-*.md by recorded run order)')
    p.add_argument('--tree', default=None, metavar='PATH',
                   help='the work tree the ### Read first paths resolve against (default: the git toplevel of the '
                        'plan folder, or the current work tree when that is another worktree of the same repository)')
    p.add_argument('--approved', default=None, metavar='"WHO: WHY"',
                   help='the person\'s approval of a plan over the step cap for its ticket size (T-0553); recorded as '
                        '"step cap approved: <plan file>: <who: why>" in the task folder\'s skips.md')
    p = sub.add_parser('precheck', help='fail fast when a task dir handoff has no ## Goal section; writes nothing')
    p.add_argument('task', help='a task dir holding handoff.md')
    p = sub.add_parser('next', help='print the next escalation action for a step dir; writes nothing')
    p.add_argument('step_dir', help='a step dir (step-<n>/) holding handoff.md and builder/verifier results')
    p = sub.add_parser('resume', help='print the step dir a resumed /chain continues from, and its next action')
    p.add_argument('task', help='a task dir holding step-<n>/ dirs')
    p = sub.add_parser('review', help='print whether a task dir\'s newest plan needs a plan review, and the next action')
    p.add_argument('task', help='a task dir holding planner-*.md and any plan-reviewer-*.md results')
    p = sub.add_parser('lane', help='print a task dir\'s lane (solo, lean, or full) and append it to its skips.md')
    p.add_argument('task', help='a task dir holding handoff.md and any planner-*.md results')
    p.add_argument('--check', action='store_true', help='print the lane only; write nothing (run.sh lane gate)')
    p = sub.add_parser('verifier-level', help='print the level (L2 or L3) of the one batched verifier of a solo ticket; writes nothing')
    p.add_argument('task', help='a task dir holding the ticket handoff.md')
    p = sub.add_parser('routes', help='print the skill routes the AGENTS.md files of the current repo resolve; writes nothing')
    p.add_argument('paths', nargs='*', metavar='path', help='repo-relative paths: print the skills routed to each instead')
    p = sub.add_parser('open', help='list the held criteria (unmet-dependency, deferred) of a task dir; writes nothing')
    p.add_argument('task', help='a task dir holding handoff.md and any step-<n>/ dirs')
    p.add_argument('--explain', action='store_true', help='add the reason a hold was read as stale or an ordinary fail')
    p = sub.add_parser('swap', help="apply the newest verifier's one criterion swap to a step handoff")
    p.add_argument('step_dir', help='a step dir (step-<n>/) holding handoff.md and builder/verifier results')
    p.add_argument('--timeout', type=float, default=300, metavar='SECONDS',
                   help='per-span timeout for the new criterion (default 300); a timeout refuses. Spans run with '
                        'SDLC_BASE_SHA from the handoff\'s `base:` line, else <step dir>/base-sha, else HEAD of the execution tree')
    p = sub.add_parser('amend', help="apply the newest blocked builder's one criterion amend to a step handoff")
    p.add_argument('step_dir', help='a step dir (step-<n>/) holding handoff.md and builder results')
    p.add_argument('--timeout', type=float, default=300, metavar='SECONDS',
                   help='per-span timeout for a new (guard) or (red) criterion (default 300); a timeout refuses')
    p = sub.add_parser('widen', help='add paths to the one scope criterion of a step handoff')
    p.add_argument('step_dir', help='a step dir (step-<n>/) holding handoff.md')
    p.add_argument('paths', nargs='*', metavar='path', help='repo-relative paths to allow (one or more)')
    p.add_argument('--timeout', type=float, default=300, metavar='SECONDS',
                   help='timeout for the widened span (default 300); a timeout refuses. It runs with '
                        'SDLC_BASE_SHA from the handoff\'s `base:` line, else <step dir>/base-sha, else HEAD of the execution tree')
    p.add_argument('--tree', default=None, metavar='PATH',
                   help='the work tree the widened span runs in (default: the git toplevel of the step dir, or the '
                        'current work tree when that is another worktree of the same repository); it must belong '
                        'to the same repository as the step dir')
    p.add_argument('--reason', metavar='WHY',
                   help='why the files are in scope; recorded on each ## Scope widened item. With no scope '
                        'criterion in the step it makes the path list the recorded allow-list')
    sub.add_parser('selftest', help='prove every case and every refusal fires')
    a, extra = ap.parse_known_args(argv)
    if extra and a.cmd != 'widen':
        ap.error(f'unrecognized arguments: {" ".join(extra)}')
    if a.cmd == 'widen':
        # a path such as -x reaches here as an unknown option; widen refuses it as a bad path
        if not 0 < a.timeout < float('inf'):
            print('steps: --timeout must be a finite number of seconds greater than 0', file=sys.stderr)
            return 1
        if a.tree is not None and not os.path.isdir(a.tree):
            print(f'steps: --tree {a.tree} is not a directory', file=sys.stderr)
            return 1
        return cmd_widen(a.step_dir, a.paths + extra, a.timeout, a.reason, a.tree)
    if a.cmd == 'selftest':
        return selftest()
    if a.cmd == 'precheck':
        return cmd_precheck(a.task)
    if a.cmd == 'next':
        return cmd_next(a.step_dir)
    if a.cmd == 'resume':
        return cmd_resume(a.task)
    if a.cmd == 'review':
        return cmd_review(a.task)
    if a.cmd == 'lane':
        return cmd_lane(a.task, a.check)
    if a.cmd == 'verifier-level':
        return cmd_verifier_level(a.task)
    if a.cmd == 'routes':
        return cmd_routes(a.paths)
    if a.cmd == 'open':
        return cmd_open(a.task, a.explain)
    if a.cmd == 'swap':
        if not 0 < a.timeout < float('inf'):
            print('steps: --timeout must be a finite number of seconds greater than 0', file=sys.stderr)
            return 1
        return cmd_swap(a.step_dir, a.timeout)
    if a.cmd == 'amend':
        if not 0 < a.timeout < float('inf'):
            print('steps: --timeout must be a finite number of seconds greater than 0', file=sys.stderr)
            return 1
        return cmd_amend(a.step_dir, a.timeout)
    if a.cmd == 'lint':
        if a.tree is not None and not os.path.isdir(a.tree):
            print(f'steps: --tree {a.tree} is not a directory', file=sys.stderr)
            return 1
        approved = None if a.approved is None else ' '.join(a.approved.split())
        if approved is not None and not APPROVAL_RE.match(approved):
            print('steps: --approved takes "<who: why>": who approved, a colon, and why', file=sys.stderr)
            return 1
        return cmd_lint(a.target, a.tree, approved)
    if a.guard_timeout is not None and not 0 < a.guard_timeout < float('inf'):
        print('steps: --guard-timeout must be a finite number of seconds greater than 0', file=sys.stderr)
        return 1
    reason = None
    if a.override_review is not None:
        reason = ' '.join(a.override_review.split())
        if not reason:
            print('steps: --override-review needs a reason', file=sys.stderr)
            return 1
    if a.tree is not None and not os.path.isdir(a.tree):
        print(f'steps: --tree {a.tree} is not a directory', file=sys.stderr)
        return 1
    return cmd_split(a.target, a.only, a.guard_timeout, reason, a.tree, a.supersede)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
