#!/usr/bin/env python3
"""Split a planner result into one step handoff per step, so /chain never parses a plan by hand.

Usage: steps.py {split <planner.md | task dir> [--only N ...] [--guard-timeout SECONDS] |
                 lint <planner.md | task dir> | review <task dir> | lane <task dir> | next <step dir> |
                 resume <task dir> |
                 swap <step dir> [--timeout SECONDS] |
                 widen <step dir> <path> [<path> ...] [--timeout SECONDS] | selftest}
  split     read the plan (a planner-*.md file, or the newest planner-*.md in a task dir,
            by recorded run order in its runs.jsonl, see order.py)
            and the task goal (the ## Goal section of <task dir>/handoff.md, front matter skipped),
            then write <task dir>/step-<n>/handoff.md as "## Task goal", the goal, a blank line,
            and the step block verbatim (## Step <n>: ... up to the next ## heading, trailing
            blank lines trimmed). Prints one line per file written.
            --only N (repeatable) writes only those steps; an N not in the plan is an error.
            Refuses a step whose step-<n>/ already holds builder-*.md or verifier-*.md: rename it
            to step-<n>.superseded-<k>/ first (/chain 4.2). This script never renames anything.
            Refuses a plan whose acceptance criterion commands do not parse (see lint): the
            refusal names each span and ends with "plan defect: replan this step (/chain 3)".
            It also refuses a criterion span that joins two checks with an unquoted || (see lint),
            one that pins a commit sha fixed at plan time (except the ancestry form
            git merge-base --is-ancestor <sha> HEAD), and one that compares a count over a
            changing set with a fixed number (see lint), and one whose ### Read first lists a
            path that does not exist (see lint). An optional ### Read first subsection is copied
            verbatim with the rest of the step block.
            With --only N, split then runs that step's (guard) criteria against the current tree:
            each command-like code span on a criterion line that starts with "(guard)" runs under
            bash -c, from the git toplevel of the task dir (else the task dir), under a per-step
            timeout: an explicit --guard-timeout SECONDS wins; otherwise the step block's own
            "guard timeout: <seconds>" line, else such a line outside every ## Step block (for
            example in ## Goal), else 300; a value of 0 or less counts as no line. Spans run with
            SDLC_BASE_SHA set to git rev-parse HEAD at the toplevel (no build has started, so HEAD
            is the base; unset outside git, never inherited from the caller). A span that references HEAD^1 or holds a
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
            A full split (no --only) and lint never execute a span.
            Refuses a plan the plan review rejected: when the newest plan-reviewer-*.md that counts
            after the chosen plan (order.counts_after) has Verdict replan or blocked, it prints
            "steps: <plan>: the newest plan review <file> says <verdict>; a rejected plan is never
            split" and a last line "plan defect: plan review: <verdict>; run steps.py review
            (/chain 3)", with or without --only, for a file or a dir target.
            Refuses an invalid result first: when the chosen plan, or the newest plan-reviewer-*.md
            that counts after it, fails results.structure_error (role planner, plan-reviewer), it
            prints "invalid result: <path>: <reason>" before the review check and the goal read.
            Every check runs before any write: a failure prints on stderr, exits 1, writes nothing.
  lint      pick the plan the same way split does, then check that every command-like code span
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
            A step may carry a ### Read first subsection: the entry files a role reads before
            the step, one list item per path in the one-line form - `<path>`. Each listed path
            (the text of the item's code span; lines up to the next ## or ### line, ``` fences
            left out) resolves against the git toplevel of the plan file's folder, else that
            folder outside git. A path that does not exist is a finding: "steps: <plan> step <n>:
            ### Read first lists a path that does not exist: <path>", and lint and split refuse
            with the plan defect last line. A step with no ### Read first stays valid.
            Never executes a span, writes nothing, and needs no
            handoff.md. Prints "steps lint: ok", or the split refusal on stderr and exits 1.
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
  review    review <task dir>: decide whether the task dir's newest planner-*.md (by order.py) needs
            a plan review before split (/chain 3). Reads only; never file times. Stdout: "<action>"
            or "review L1", then "reason: <text>", then one "read: <path>" per result file consulted;
            exit 0. Rules, in order:
              no planner-*.md                            -> one "steps review: " line on stderr,
                nothing on stdout, exit 1
              the newest plan fails results.structure_error(plan, 'planner') (empty file, no
                header, header role, section order, no ## Goal) -> invalid result (see below)
              the plan's ## Assumptions section (lines up to the next ## heading) holds a list item
                whose text after "- " or "* " starts with "unresolved:" -> stop (the reason quotes
                the item; the user decides)
              required when: the plan's file name level is L3, or a step block's level: is L4 or L5,
                or a step title starts with "Merge ", or the task dir holds two or more planner
                results (a replan), or handoff.md holds a line "## Plan review"
              not required                               -> split
              no plan-reviewer-*.md counts after the plan (order.counts_after) -> review L1
              the newest such result fails results.structure_error(r, 'plan-reviewer') -> invalid
                result (a missing or disallowed Verdict is not a structure error; it stays below)
              newest such result's Verdict (first non-blank line under ## Verdict, lowercased):
                pass                                     -> split
                replan                                   -> replan, but stop when the task dir holds
                  two or more plan-reviewer results with Verdict replan (the count is per task dir)
                blocked                                  -> stop (ask its ## Missing decisions)
                anything else                            -> review L1 (a rerun, never a replan), but
                  two consecutive verdict-less reviews after the plan -> stop
            An invalid result prints "invalid result: <path>: <reason>", then "reason: the newest
            result does not match its results.py schema; stop and ask the user", then the read:
            lines; exit 0. next and resume print it the same way.
  lane      lane <task dir>: pick the task's lane, solo, lean, or full, and append it to <task dir>/skips.md.
            Stdout: the lane, then one "reason: <text>" line per reason, then one "read: <path>" line per
            file read (<task dir>/handoff.md when it exists, the newest planner-*.md by order.py when
            there is one, <task dir>/skips.md when it existed before this call); exit 0. For lane solo it also
            records the planner and filer under ## Skipped (one `- skip: <role>; step: all; reason: solo lane...;
            decided: lane` line each, added once), the form the tickets.py skips guard counts, so a conductor can
            close the ticket by reason with no extra step.
            Facts: the size is the handoff.md front matter field size (tickets.parse), valid only when it
            is S, M, L, or XL; a handoff with no front matter block has no size. The point is "before
            planning" with no planner result, "after plan review" when there is one and handoff.md has a
            line "## Plan review", else "after planning". The plan is read leniently, like review's
            plan facts: no results.structure_error check, since split, lint, and review refuse a bad plan.
            Rules, reasons collected in this order:
              skips.md has a line starting "- lane: full;" in its ## Lane section -> "skips.md already
                records full, and a lane never returns from full" (a lane never returns from full)
              no valid size -> "handoff.md front matter has no size of S, M, L, or XL"
            Before planning, size alone decides: with either reason above the lane is full and only those
            print; else S or M -> solo, L or XL -> full, with the one reason "size <v> decides before
            planning (no planner result yet)". After planning, more reasons follow, in order:
              size L or XL -> "size <v> is above M, and lean takes only size S or M"
              an unresolved assumption by review_required() (the function review uses) -> "<plan> lists
                an unresolved assumption: "<first item>""
              every reason review_required() returns, verbatim (planner L3, a step at L4 or L5, a merge
                step, a replan, a ## Plan review line)
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
              newest builder Status blocked              -> replan (whatever its Notes say)
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
              newest verifier Verdict pass               -> done
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
  resume    pick the step a resumed /chain continues from (/chain step 4). Candidates are the task
            dir's direct children named exactly step-<n> (step-<n>.superseded-<k>/ left out),
            sorted by the integer n (step-2 before step-10). For each in order it runs the next
            rules above; the first whose action is not done wins (invalid result included). Stdout:
            that step dir as <task dir as given>/step-<n>, then exactly what next prints for it;
            exit 0. When every candidate is done: "done", then "reason: every step-<n>/ passed";
            exit 0. It never picks the newest or highest step dir. Writes nothing and never reads
            file times. A step that next calls done through a batch-verified task-dir verifier
            result (## Verified, above) counts as done.
            A missing task dir, a task dir with no step-<n>/ (run split first), or a next error on
            a candidate prints one "steps resume: " line on stderr, nothing on stdout, and exits 1.
  swap      apply the newest verifier's one criterion swap to <step dir>/handoff.md (/chain 4.2
            light path). The pair lives in that verifier's ## For the next attempt: exactly one
            line starting "swap old:" holding exactly one code span (the old criterion's command,
            verbatim), and exactly one line starting "swap new:" whose stripped rest is the full
            replacement criterion; zero or two or more of either line, or a swap old: line with no
            span or several, is no pair. Preconditions: a newest builder and a newest verifier
            result, the verifier counts after the builder (order.counts_after), its Verdict is
            fail, its note starts "plan defect:", it holds a pair, and no other verifier result in
            the dir holds one (one swap per step). Exactly one criterion line (the criteria_lines
            region, a - or * list item) must hold the old span among its command spans. The new
            text starts with (guard) exactly when that line does, holds at least one command span,
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
  widen     widen <step dir> <path> [<path> ...] [--timeout SECONDS]: apply a conductor scope
            decision to <step dir>/handoff.md, so the next builder does not block on the old scope
            guard. Each path must be repo-relative, match [A-Za-z0-9._/@+-]+, not start with - or /,
            and hold no .. component. Exactly one criterion line (the criteria_lines region, a - or
            * list item) must hold one command span with git diff --name-only and a grep -v
            allow-list, in exactly one recognized form:
              F  grep -vxF -e <word>...      each path is appended as -e <path> after the last -e arg
              E  grep -vxE "<pattern>"       |<path> is appended inside the quotes
              A  grep -vE "^(...)$" (or grep -E -v)   |<path> is inserted before )$
            In E and A the path is ERE-escaped (a backslash before each of .^$*+?()[]{}|\).
            Zero or several such lines, or an unrecognized form, refuses. A path already listed
            (an -e word for F, its escaped form an alternative for E and A) is skipped; when every
            path is listed it prints "widen: already applied", exits 0, and writes nothing. The
            rewritten line must keep its marker and (guard) tag and lint clean (the lint rules
            above). The widened span then runs under bash -c from the git toplevel of the step dir
            (else the step dir) under --timeout SECONDS (default 300), with SDLC_BASE_SHA from
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

STEP_RE = re.compile(r'^## Step (\d+): (.+)$')
LEVEL_RE = re.compile(r'^level: L[1-5]\s*$')
GUARD_TIMEOUT_RE = re.compile(r'^guard timeout:\s*(\d+(?:\.\d+)?)\s*$')
DEFAULT_GUARD_TIMEOUT = 300
SPAN_RE = re.compile(r'(`+)(.+?)\1')
ASSIGN_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=')
PLACEHOLDER_RE = re.compile(r'<[^<>\s][^<>]*>')
BUILTINS = {'cd', 'test', '[', 'echo', 'printf', 'export', 'set', 'true', 'false', 'time', 'type',
            'command', 'eval', 'exec', 'source', '.'}
PLAN_DEFECT = 'plan defect: replan this step (/chain 3)'


class Fail(Exception):
    """A refusal: the message goes to stderr and the command exits 1. Never a traceback."""


def find_plan(target):
    """Return (planner file, task dir) for a planner file or a task dir."""
    target = pathlib.Path(target)
    if target.is_dir():
        plan = order.newest(target, 'planner')
        if not plan:
            raise Fail(f'steps: no planner-*.md in {target}')
        return pathlib.Path(plan), target
    if target.is_file():
        return target, target.parent
    raise Fail(f'steps: no such file or directory: {target}')


def read_goal(task_dir):
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
        raise Fail(f'steps: {handoff} has no ## Goal section')
    body = []
    for line in lines[start + 1:]:
        if line.startswith('## '):
            break
        body.append(line)
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    if not body:
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


def criteria_indexed(lines):
    """(index, line) for each line under each ### Acceptance criteria of a list of lines, up to the
    next ## or ### line, with ``` fenced lines left out. The one region rule criteria_lines uses."""
    out = []
    inside = fenced = False
    for i, line in enumerate(lines):
        if line.startswith('## ') or line.startswith('### '):
            inside = line.strip() == '### Acceptance criteria'
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


def guard_skipped(text):
    """A guard span that cannot run against the current tree: it references HEAD^1 (a merge
    commit not made yet) or holds a <placeholder>."""
    return 'HEAD^1' in text or PLACEHOLDER_RE.search(text) is not None


def git_toplevel(task_dir):
    """The git toplevel of the task dir, or None outside a git work tree."""
    try:
        r = subprocess.run(['git', '-C', str(task_dir), 'rev-parse', '--show-toplevel'],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    top = r.stdout.strip()
    return top if r.returncode == 0 and top else None


def guard_cwd(task_dir):
    """The git toplevel of the task dir, else the task dir itself."""
    return git_toplevel(task_dir) or str(task_dir)


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


def base_sha(top, step_dir=None):
    """SDLC_BASE_SHA for a span: the first line of <step dir>/base-sha when it names a commit,
    else HEAD at top; None outside git."""
    if not top:
        return None
    if step_dir is not None:
        f = pathlib.Path(step_dir) / 'base-sha'
        with contextlib.suppress(OSError, UnicodeDecodeError):
            first = (f.read_text(encoding='utf-8').splitlines() or [''])[0].strip()
            sha = rev_commit(top, first) if first else None
            if sha:
                return sha
    return rev_commit(top, 'HEAD')


def span_env(base):
    """The env a span runs with: SDLC_BASE_SHA set to base, never inherited; unset when base is None."""
    env = {k: v for k, v in os.environ.items() if k != 'SDLC_BASE_SHA'}
    if base:
        env['SDLC_BASE_SHA'] = base
    return env


def run_guard(text, cwd, timeout, base=None):
    """Run one guard span with SDLC_BASE_SHA=base (unset when None).
    Returns (rc or None on timeout, combined output tail lines).
    It runs in its own session so a timeout kills the whole process group, grandchildren too."""
    proc = subprocess.Popen(['bash', '-c', '--', text], cwd=cwd, stdin=subprocess.DEVNULL, env=span_env(base),
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


def run_guards(plan, steps, chosen, task_dir, timeouts):
    """Run the runnable (guard) spans of each chosen step, each under timeouts[n] seconds; raise
    Fail naming every red one. Called only by split --only; a full split and lint never execute a span."""
    top = git_toplevel(task_dir)
    cwd = top or str(task_dir)
    base = base_sha(top)
    lines, red, before, ran = [], [], None, False
    for n in chosen:
        for text in guard_spans(steps[n]):
            if guard_skipped(text):
                continue
            if top and not ran:
                before = tree_state(top)
            ran = True
            timeout = timeouts[n]
            rc, tail = run_guard(text, cwd, timeout, base)
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
        raise Fail('\n'.join(lines + [f'plan defect: {"; ".join(red)}; replan this step (/chain 3)']))


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


def lint_steps(plan, steps):
    """Return one finding per command-like criterion span that bash -n cannot parse; for a span that
    parses, one per unquoted || join, one for a pinned commit sha, and one for a count over a changing
    set compared with a fixed number; one per ### Read first path that does not exist, resolved against
    the git toplevel of the plan's folder (else that folder); [] when clean. bash -n parses and never
    executes."""
    findings = []
    base = None
    for n, block in steps.items():
        paths = read_first_paths(block)
        if paths and base is None:
            folder = pathlib.Path(plan).resolve().parent
            base = pathlib.Path(git_toplevel(folder) or folder)
        for rel in paths:
            if not (base / rel).exists():
                findings.append(f'steps: {plan} step {n}: ### Read first lists a path that does not exist: {rel}')
        for text in command_spans(block):
            probe = PLACEHOLDER_RE.sub('PLACEHOLDER', text)
            try:
                r = subprocess.run(['bash', '-n', '-c', '--', probe], capture_output=True, text=True, timeout=5)
                rc, err = r.returncode, r.stderr
            except subprocess.TimeoutExpired:
                rc, err = 1, 'bash -n did not finish within 5 seconds'
            if rc != 0:
                lines = [f'steps: {plan} step {n}: acceptance criterion command does not parse: {text}']
                lines += [f'  {e}' for e in err.splitlines() if e.strip()]
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
            if fixed_set_count(text):
                findings.append(f'steps: {plan} step {n}: acceptance criterion compares a count over a changing set '
                                f'with a fixed number: {text}\n'
                                '  other lanes change the set: derive the set at run time, '
                                "or check only this step's own items")
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
    return findings


def lint_or_fail(plan, steps):
    findings = lint_steps(plan, steps)
    if findings:
        raise Fail('\n'.join(findings + [PLAN_DEFECT]))


def split(target, only=None, guard_timeout=None):
    """Check everything, then write. Returns the paths written. With only, the chosen steps'
    runnable (guard) spans run before any write, each step under guard_timeout when given, else
    its own guard timeout line, else the plan's, else DEFAULT_GUARD_TIMEOUT."""
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
    if rejected:
        r, v = rejected
        raise Fail(f'steps: {plan}: the newest plan review {os.path.basename(r)} says {v}; '
                   f'a rejected plan is never split\n'
                   f'plan defect: plan review: {v}; run steps.py review (/chain 3)')
    goal = read_goal(task_dir)
    steps = parse_steps(plan)
    lint_or_fail(plan, steps)
    if only:
        missing = sorted(set(n for n in only if n not in steps))
        if missing:
            raise Fail(f'steps: --only {", ".join(map(str, missing))} not in {plan} '
                       f'(steps: {", ".join(map(str, steps))})')
        chosen = [n for n in steps if n in set(only)]
    else:
        chosen = list(steps)
    for n in chosen:
        d = task_dir / f'step-{n}'
        done = sorted(p.name for pat in ('builder-*.md', 'verifier-*.md') for p in d.glob(pat)) if d.is_dir() else []
        if done:
            raise Fail(f'steps: {d} already holds role output ({", ".join(done)}). Per /chain 4.2, rename it '
                       f'to step-{n}.superseded-<k>/ (next free k) first, then split again. Nothing was written.')
    if only:
        plan_timeout = plan_guard_timeout(plan)
        timeouts = {n: guard_timeout if guard_timeout is not None
                    else step_guard_timeout(steps[n]) or plan_timeout or DEFAULT_GUARD_TIMEOUT
                    for n in chosen}
        run_guards(plan, steps, chosen, task_dir, timeouts)
    written = []
    for n in chosen:
        d = task_dir / f'step-{n}'
        d.mkdir(parents=True, exist_ok=True)
        path = d / 'handoff.md'
        path.write_text(f'## Task goal\n{goal}\n\n{steps[n]}\n', encoding='utf-8')
        written.append(path)
    return written


def cmd_split(target, only, guard_timeout=None):
    try:
        written = split(target, only, guard_timeout)
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
    if unresolved or why:
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


def cmd_lint(target):
    try:
        plan, task_dir = find_plan(target)
        steps = parse_steps(plan)
        lint_or_fail(plan, steps)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print('steps lint: ok')
    for w in lean_warnings(plan, task_dir, steps):
        print(w, file=sys.stderr)
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


def is_plan_defect(path):
    body = section(path, 'For the next attempt') or []
    first = next((line.strip() for line in body if line.strip()), '')
    return first.startswith('plan defect:')


def handoff_level(d):
    h = d / 'handoff.md'
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
    n, task_dir = int(m.group(1)), d.parent
    b = order.newest(d, 'builder')
    if b is None or build_status_or_none(b) != 'done' or result_level(b) >= 4:
        return None
    title = ''
    h = d / 'handoff.md'
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
        if results.structure_error(w, 'verifier') is None and verdict_or_none(w) == 'pass':
            return w
        return None
    return None


def next_action(step_dir):
    """Return (action, level or None, reason, [result paths read]). Reads only; never file times.
    Ordering comes from order.py alone (ordered, newest, counts_after)."""
    d = pathlib.Path(step_dir)
    if not d.is_dir():
        raise Fail(f'steps next: no such directory: {d}')
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
        return 'replan', None, f'newest builder {os.path.basename(b)} is blocked (a blocked build replans)', read
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
        return 'done', None, f'newest verifier {os.path.basename(v)} passed', read
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
        if verdict_or_none(w) == 'fail' and not is_plan_defect(w):
            count += 1
    if count <= 1:
        return 'rebuild', level, f'first counted fail at build L{level}', read
    if level < 5:
        return 'bump', level + 1, f'{count} counted fails at build L{level}', read
    return 'stop', None, f'{count} counted fails at build L5; there is no L6, ask the user', read


INVALID_REASON = 'the newest result does not match its results.py schema; stop and ask the user'


def print_action(action, level, reason, read):
    """The stdout of next, resume (after its step dir line), and review. An invalid result prints
    "invalid result: <path>: <why>", then the fixed reason line, then the read: lines."""
    if action == 'invalid result':
        print(f'invalid result: {reason}')
        print(f'reason: {INVALID_REASON}')
    else:
        print(action if level is None else f'{action} L{level}')
        print(f'reason: {reason}')
    for p in read:
        print(f'read: {p}')


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
    is not done, else (None, 'done', None, reason, []). Reads only; never file times."""
    t = pathlib.Path(task)
    if not t.is_dir():
        raise Fail(f'steps resume: no such directory: {t}')
    nums = sorted(int(m.group(1)) for c in t.iterdir()
                  if c.is_dir() and (m := STEP_DIR_RE.fullmatch(c.name)))
    if not nums:
        raise Fail(f'steps resume: {t} has no step-<n>/ dirs; run steps.py split {t} first')
    for n in nums:
        d = pathlib.Path(task) / f'step-{n}'
        try:
            action, level, reason, read = next_action(d)
        except Fail as e:
            msg = ' '.join(str(e).split('\n'))
            if msg.startswith('steps next: '):
                msg = msg[len('steps next: '):]
            raise Fail(f'steps resume: {d}: {msg}')
        if action != 'done':
            return d, action, level, reason, read
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

def review_verdict(path):
    """'pass', 'replan', or 'blocked' from the first non-blank line under ## Verdict, read by
    results.key_value against the plan-reviewer schema, else None. Ignores the header; never raises."""
    return results.key_value(path, 'plan-reviewer')


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
    pname = os.path.basename(plan)
    why = []
    if result_level(plan) == 3:
        why.append(f'{pname} is a planner L3 plan')
    if any(n in (4, 5) for n in levels):
        why.append('a step is at builder L4 or L5')
    if any(x.startswith('Merge ') for x in titles):
        why.append('the plan has a merge step')
    n = len(order.ordered(task_dir, 'planner'))
    if n >= 2:
        why.append(f'{n} planner results (a replan)')
    h = pathlib.Path(task_dir) / 'handoff.md'
    if h.is_file() and any(line.rstrip() == '## Plan review'
                           for line in h.read_text(encoding='utf-8').splitlines()):
        why.append('handoff.md holds ## Plan review')
    return unresolved, why


def rejected_by_review(plan, task_dir):
    """(plan-reviewer result, verdict) when the newest plan-reviewer result that counts after plan
    says replan or blocked, else None."""
    after = [r for r in order.ordered(task_dir, 'plan-reviewer') if order.counts_after(r, plan)]
    if not after:
        return None
    v = review_verdict(after[-1])
    return (after[-1], v) if v in ('replan', 'blocked') else None


def review_action(task):
    """Return (action, level or None, reason, [result paths read]) for a task dir's newest plan:
    split, review L1, replan, or stop. Reads only; never file times. Ordering comes from order.py
    alone (ordered, newest, counts_after)."""
    t = pathlib.Path(task)
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
    if v == 'pass':
        return 'split', None, f'the newest plan review {rname} passed {pname}', read
    if v == 'replan':
        replans = [x for x in reviews if review_verdict(x) == 'replan']
        if len(replans) >= 2:
            read += [x for x in replans if x not in read]
            return ('stop', None,
                    f'{len(replans)} plan reviews in {t} say replan (newest {rname}); '
                    'the second replan review asks the user', read)
        return 'replan', None, f'the newest plan review {rname} says replan; replan at planner L3', read
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


def cmd_review(task):
    try:
        action, level, reason, read = review_action(task)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print_action(action, level, reason, read)
    return 0


# --- lane -------------------------------------------------------------------

LANE_MAX_STEPS = 2
LANE_MAX_CRITERIA = 12
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
LANE_NO_SIZE = 'handoff.md front matter has no size of S, M, L, or XL'
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


def lane_action(task):
    """Return (lane, point, reasons, [files read]) for a task dir: solo, lean, or full. Writes nothing.
    The plan is read leniently, like plan_facts: split, lint, and review refuse a bad plan."""
    # Imported here, not at the top: results.py's selftest copies steps.py beside only order.py and
    # results.py and runs steps.py next, so a top-level import would fail there.
    import tickets
    t = pathlib.Path(task)
    if not t.is_dir():
        raise Fail(f'steps lane: no such directory: {t}')
    h, skips = t / 'handoff.md', t / 'skips.md'
    read = []
    size, review_line = None, False
    if h.is_file():
        read.append(str(h))
        text = h.read_text(encoding='utf-8')
        size = (tickets.parse(text) or {}).get('size')
        review_line = any(line.rstrip() == '## Plan review' for line in text.splitlines())
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
        lane = {'S': 'solo', 'M': 'solo'}.get(size, 'full')
        return lane, point, [f'size {size} decides before planning (no planner result yet)'], read

    pname = os.path.basename(plan)
    if size in ('L', 'XL'):
        reasons.append(f'size {size} is above M, and lean takes only size S or M')
    unresolved, why = review_required(plan, t)
    if unresolved:
        reasons.append(f'{pname} lists an unresolved assumption: "{unresolved[0]}"')
    reasons += why
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
    lines = old.splitlines(keepends=True)
    if lines and not lines[-1].endswith(('\n', '\r')):
        lines[-1] += '\n'
    bare = [x.rstrip('\r\n') for x in lines]
    start = next((i for i, x in enumerate(bare) if x.rstrip() == '## Lane'), None)
    if start is not None:
        end = next((j for j in range(start + 1, len(bare)) if bare[j].startswith('## ')), len(bare))
        last = end
        while last > start + 1 and not bare[last - 1].strip():
            last -= 1
        return ''.join(lines[:last] + [record + '\n'] + lines[last:])
    first = next((i for i, x in enumerate(bare) if x.startswith('## ')), None)
    if first is None:
        return ''.join(lines) + f'\n## Lane\n{record}\n'
    return ''.join(lines[:first] + ['## Lane\n', record + '\n', '\n'] + lines[first:])


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


def cmd_lane(task):
    try:
        lane, point, reasons, read = lane_action(task)
        record_lane(task, lane, point, reasons)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print(lane)
    for r in reasons:
        print(f'reason: {r}')
    for p in read:
        print(f'read: {p}')
    return 0


# --- swap -------------------------------------------------------------------

SWAP_DEFECT = '; replan this step (/chain 4.2)'


def section_lines_start(path, prefix):
    """The stripped lines under ## For the next attempt that start with prefix."""
    try:
        body = section(path, 'For the next attempt') or []
    except Exception:
        return []
    return [line.strip() for line in body if line.strip().startswith(prefix)]


def swap_pair(path):
    """(old span, new text) from a verifier result's ## For the next attempt, or None.
    A pair is exactly one line starting 'swap old:' holding exactly one code span (stripped of one
    edge space, like line_spans) and exactly one line starting 'swap new:' with a non-empty value."""
    olds = section_lines_start(path, 'swap old:')
    news = section_lines_start(path, 'swap new:')
    if len(olds) != 1 or len(news) != 1:
        return None
    spans = []
    for m in SPAN_RE.finditer(olds[0][len('swap old:'):]):
        text = m.group(2)
        if text.startswith(' '):
            text = text[1:]
        if text.endswith(' '):
            text = text[:-1]
        spans.append(text)
    new = news[0][len('swap new:'):].strip()
    if len(spans) != 1 or not spans[0].strip() or not new:
        return None
    return spans[0], new


def earlier_swap(d, v):
    """True when a verifier result in d other than v proposes a swap: one swap per step."""
    return any(w != v and swap_pair(w) is not None for w in order.ordered(d, 'verifier'))


def list_item(line):
    """(indent, marker, text after the marker) for a '-' or '*' list item line, else None."""
    m = re.match(r'^(\s*)([-*]) (.*)$', line)
    return (m.group(1), m.group(2), m.group(3)) if m else None


def swap(step_dir, timeout=300):
    """Apply the newest verifier's criterion swap to <step dir>/handoff.md after every check passes.
    Returns the one stdout line. Raises Fail (last line 'plan defect: ...; replan this step (/chain 4.2)')
    and writes nothing on any refusal."""
    d = pathlib.Path(step_dir)

    def refuse(why, detail=()):
        raise Fail('\n'.join(list(detail) + [f'plan defect: steps swap refused: {why}{SWAP_DEFECT}']))

    if not d.is_dir():
        refuse(f'no such directory: {d}')
    h = d / 'handoff.md'
    if not h.is_file():
        refuse(f'no step handoff at {h}')
    b = order.newest(d, 'builder')
    v = order.newest(d, 'verifier')
    if b is None or v is None:
        refuse('the step dir needs a builder result and a verifier result')
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
    items = [(i, line) for i, line in criteria_indexed([x.rstrip('\r\n') for x in lines])
             if list_item(line)]
    targets = [(i, line) for i, line in items if old in line_spans(line)]
    if not targets:
        if any(list_item(line)[2].strip() == new for _, line in items):
            return 'swap: already applied'
        refuse(f'no criterion line holds the old span: {old}')
    if len(targets) > 1:
        refuse(f'{len(targets)} criterion lines hold the old span: {old}')
    idx, target = targets[0]

    if new.startswith('(guard)') != is_guard_line(target):
        refuse('the new text must start with (guard) exactly when the old criterion line does: '
               f'old {"is" if is_guard_line(target) else "is not"} a (guard) line')
    spans = line_spans(f'- {new}')
    if not spans:
        refuse(f'the new criterion holds no runnable command span: {new}')
    skipped = [s for s in spans if guard_skipped(s)]
    if skipped:
        refuse(f'a new span references HEAD^1 or holds a <placeholder>, so it cannot run now: {skipped[0]}')
    findings = lint_steps(h, {1: f'## Step 1: swap\nlevel: L1\n### Acceptance criteria\n- {new}'})
    if findings:
        refuse(f'the new criterion does not lint: {new}', findings)

    top = git_toplevel(d)
    cwd = top or str(d)
    base = base_sha(top, d)
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


def add_scope_widened(text, paths):
    """The handoff text with one '## Scope widened' item per path: appended to the existing section,
    after its last non-blank line, or in a new section at the end."""
    items = [f'- `{p}`: allowed by a conductor scope decision (steps.py widen)' for p in paths]
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


def widen(step_dir, paths, timeout=300):
    """Add paths to the one scope criterion of <step dir>/handoff.md after every check passes, and
    record them under ## Scope widened. Returns the one stdout line. Raises Fail (last line
    'plan defect: steps widen refused: ...; replan this step (/chain 4.2)') and writes nothing on any
    refusal."""
    d = pathlib.Path(step_dir)

    def refuse(why, detail=()):
        raise Fail('\n'.join(list(detail) + [f'plan defect: steps widen refused: {why}{SWAP_DEFECT}']))

    h = d / 'handoff.md'
    if not h.is_file():
        refuse(f'no step handoff at {h}')
    if not paths:
        refuse('no path given')
    for p in paths:
        if not repo_path_ok(p):
            refuse(f'not a repo-relative path of [A-Za-z0-9._/@+-] with no leading - or / and no .. '
                   f'component: {p}')
    paths = list(dict.fromkeys(paths))

    text = h.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)
    items = [(i, line) for i, line in criteria_indexed([x.rstrip('\r\n') for x in lines]) if list_item(line)]
    scope = [(i, line, s) for i, line in items for s in line_spans(line)
             if is_scope_span(s)]
    rows = sorted(set(i for i, _, _ in scope))
    if not rows:
        refuse('no criterion line has a command span with git diff --name-only and a grep -v allow-list')
    if len(rows) > 1:
        refuse(f'{len(rows)} criterion lines have a git diff --name-only span with a grep -v allow-list; '
               'need exactly one')
    if len(scope) > 1:
        refuse('the scope criterion line has several git diff --name-only spans with a grep -v allow-list')
    idx, target, old = scope[0]
    forms = widen_forms(old)
    if not forms:
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

    top = git_toplevel(d)
    cwd = top or str(d)
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
    h.write_text(add_scope_widened(''.join(lines), add), encoding='utf-8')
    return f'steps widen: {d}: added {", ".join(add)} to the scope criterion: {new}'


def cmd_widen(step_dir, paths, timeout=300):
    try:
        line = widen(step_dir, paths, timeout)
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
    """Every file under root: relative path -> (mtime_ns, bytes)."""
    snap = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            p = pathlib.Path(dirpath) / f
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

        d = task(plan=guard_plan(f'(guard) `git diff --quiet HEAD^1 HEAD && test -e {tmp}/nope`'))
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(n) a HEAD^1 guard is skipped (it would be red if run)',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())

        d = task(plan=guard_plan('(guard) `test -e <tmp>/nope`'))
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(n) a <placeholder> guard is skipped (it would be red if run)',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())

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
        check('next replan: a blocked builder replans, whatever its Notes say',
              nxt(step(2, [('builder-L2.md', BLOCKED)]), 'replan'))
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

        # (c) refusals: each writes nothing and ends with the plan-defect line
        r, d = w_repo(w_handoff('`test -d .`'))
        widen_refused('(c) no scope criterion line', d, ['b.txt'], 'no criterion line')
        r, d = w_repo(w_handoff(f'`{W_FORMS["F"]}`', f'`{W_FORMS["E"]}`'))
        widen_refused('(c) two scope criterion lines', d, ['b.txt'], '2 criterion lines')
        r, d = w_repo(w_handoff(f'`{W_LIST} | grep -v -e a.txt | {{ ! grep -q .; }}`'))
        widen_refused('(c) an unrecognized allow-list form (grep -v -e)', d, ['b.txt'], 'unrecognized')
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
        check('(r) a planner L3 plan -> review L1; negative: planner L2 -> split',
              r_first(r_task({'planner-L3.md': r_plan()})) == 'review L1'
              and r_first(r_task({'planner-L2.md': r_plan()})) == 'split')
        check('(r) a step at L4 or L5 -> review L1; negative: a step at L3 -> split',
              r_first(r_task({'planner-L2.md': r_plan('L4')})) == 'review L1'
              and r_first(r_task({'planner-L2.md': r_plan('L5')})) == 'review L1'
              and r_first(r_task({'planner-L2.md': r_plan('L3')})) == 'split')
        check('(r) a step titled Merge <branch> -> review L1; negative: a title Merger or merge -> split',
              r_first(r_task({'planner-L2.md': r_plan(title='Merge lane/x')})) == 'review L1'
              and r_first(r_task({'planner-L2.md': r_plan(title='Merger of x')})) == 'split'
              and r_first(r_task({'planner-L2.md': r_plan(title='merge lane/x')})) == 'split')
        check('(r) two planner results (a replan) -> review L1; negative: one -> split',
              r_first(r_task({'planner-L2.md': r_plan(), 'planner-L2-2.md': r_plan()})) == 'review L1'
              and r_first(r_task({'planner-L2.md': r_plan()})) == 'split')
        check('(r) handoff.md with a ## Plan review line -> review L1; negative: ### Plan review -> split',
              r_first(r_task({'planner-L2.md': r_plan()}, handoff='## Goal\ng\n\n## Plan review\nplan defect: x\n'))
              == 'review L1'
              and r_first(r_task({'planner-L2.md': r_plan()}, handoff='## Goal\ng\n\n### Plan review\nx\n'))
              == 'split')
        d = r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('pass')})
        rc, out, _ = run_main(['review', str(d)])
        check('(r) a pass review after the plan -> split, reading the plan and the review',
              rc == 0 and out.splitlines()[0] == 'split'
              and f'read: {d / "plan-reviewer-L1.md"}' in out.splitlines())
        check('(r) negative: a pass review before a newer plan does not count -> review L1',
              r_first(r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('pass'),
                              'planner-L3-2.md': r_plan()},
                             ['planner-L3.md', 'plan-reviewer-L1.md', 'planner-L3-2.md'])) == 'review L1')
        check('(r) one replan review -> replan; a PASS verdict is read lowercased -> split',
              r_first(r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('replan')})) == 'replan'
              and r_first(r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('PASS')})) == 'split')
        check('(r) a second replan review in the task dir -> stop; negative: a replan then a pass -> split',
              r_first(r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('replan'),
                              'planner-L3-2.md': r_plan(), 'plan-reviewer-L1-2.md': r_review('replan')},
                             ['planner-L3.md', 'plan-reviewer-L1.md', 'planner-L3-2.md', 'plan-reviewer-L1-2.md']))
              == 'stop'
              and r_first(r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('replan'),
                                  'planner-L3-2.md': r_plan(), 'plan-reviewer-L1-2.md': r_review('pass')},
                                 ['planner-L3.md', 'plan-reviewer-L1.md', 'planner-L3-2.md',
                                  'plan-reviewer-L1-2.md'])) == 'split')
        check('(r) a blocked review -> stop; negative: the same review with pass -> split',
              r_first(r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('blocked')})) == 'stop'
              and r_first(r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('pass')})) == 'split')
        check('(r) one verdict-less review -> review L1 (a rerun, never a replan); two consecutive -> stop',
              r_first(r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('maybe')})) == 'review L1'
              and r_first(r_task({'planner-L3.md': r_plan(), 'plan-reviewer-L1.md': r_review('maybe'),
                                  'plan-reviewer-L1-2.md': '## Findings\nNone\n'},
                                 ['planner-L3.md', 'plan-reviewer-L1.md', 'plan-reviewer-L1-2.md'])) == 'stop')
        check('(r) negative: a verdict-less review before the plan does not count toward two -> review L1',
              r_first(r_task({'plan-reviewer-L1.md': r_review('maybe'), 'planner-L3.md': r_plan(),
                              'plan-reviewer-L1-2.md': r_review('maybe')},
                             ['plan-reviewer-L1.md', 'planner-L3.md', 'plan-reviewer-L1-2.md'])) == 'review L1')

        d = r_task({'planner-L3.md': r_plan(), 'planner-L3-2.md': r_plan('L4', 'Merge x')},
                   runs=['planner-L3.md', 'planner-L3-2.md'], handoff='## Goal\ng\n\n## Plan review\nx\n')
        rr_why = ['planner-L3-2.md is a planner L3 plan', 'a step is at builder L4 or L5',
                  'the plan has a merge step', '2 planner results (a replan)', 'handoff.md holds ## Plan review']
        rr_out = run_main(['review', str(d)])[1].splitlines()
        d2 = r_task({'planner-L2.md': r_plan(tail='\n## Assumptions\n- unresolved: which db\n')})
        check('(r) review_required returns the unresolved items and every reason review prints, in order',
              review_required(d / 'planner-L3-2.md', d) == ([], rr_why)
              and len(rr_out) >= 2
              and rr_out[1] == 'reason: a plan review is required (planner-L3-2.md is a planner L3 plan; a step is '
              'at builder L4 or L5; the plan has a merge step; 2 planner results (a replan); handoff.md holds '
              '## Plan review) and none counts after planner-L3-2.md'
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
        # (lane) the lane of a ticket, and its record in skips.md
        def l_handoff(size='M', tail=''):
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

        lean_ok = 'every lean condition holds: size M, planner L2, 2 steps at L1 to L3, one AGENTS.md owner (.)'
        ok = True
        for size, want in (('S', 'solo'), ('M', 'solo'), ('L', 'full'), ('XL', 'full')):
            lane, reasons, _, recs = l_run(l_task(l_handoff(size)))
            why = f'size {size} decides before planning (no planner result yet)'
            ok = ok and lane == want and reasons == [why] \
                and recs == [f'- lane: {want}; point: before planning; reasons: {why}']
        lane, reasons, _, recs = l_run(l_task(l_handoff(None)))
        check('(lane) before planning, size alone decides: S and M solo, L and XL full, no size full',
              ok and lane == 'full' and reasons == [LANE_NO_SIZE]
              and recs == [f'- lane: full; point: before planning; reasons: {LANE_NO_SIZE}'])

        ok = True
        for form in (L_F2, 'grep -vxE "docs/c\\.md"', 'grep -vE "^(docs/c\\.md)$"'):
            d = l_task(l_handoff(), {'planner-L2.md': l_plan(scopes=(L_F1, form))})
            lane, reasons, reads, recs = l_run(d)
            ok = ok and lane == 'lean' and reasons == [lean_ok] \
                and recs == [f'- lane: lean; point: after planning; reasons: {lean_ok}'] \
                and reads == [str(d / 'handoff.md'), str(d / 'planner-L2.md')]
        check('(lane) a two-step size M plan at L1 to L3 inside one AGENTS.md owner is lean, for scope forms F, E, '
              'and A', ok)

        lane, reasons, _, _ = l_run(l_task(l_handoff(), {'planner-L2.md': l_plan(levels=(2, 4))}))
        check('(lane) negative: the same two-step plan with one step at L4 is full',
              lane == 'full' and reasons == ['a step is at builder L4 or L5'])

        d = l_task(l_handoff(), {'planner-L2.md': l_plan()})
        first = l_run(d)[0]
        with open(d / 'handoff.md', 'a', encoding='utf-8') as f:
            f.write('\n## Plan review\nrequired\n')
        lane, reasons, _, recs = l_run(d)
        check('(lane) negative: a lean ticket whose handoff gains a ## Plan review line is full on the next call',
              first == 'lean' and lane == 'full' and reasons == ['handoff.md holds ## Plan review']
              and len(recs) == 2 and recs[1].startswith('- lane: full; point: after plan review; '))

        rr_cases = [
            l_task(l_handoff(), {'planner-L3.md': l_plan()}),
            l_task(l_handoff(), {'planner-L2.md': l_plan(levels=(4, 3))}),
            l_task(l_handoff(), {'planner-L2.md': l_plan(levels=(2, 5))}),
            l_task(l_handoff(), {'planner-L2.md': l_plan(title1='Merge x')}),
            l_task(l_handoff(), {'planner-L2.md': l_plan(), 'planner-L2-2.md': l_plan()}),
            l_task(l_handoff(tail='\n## Plan review\nrequired\n'), {'planner-L2.md': l_plan()}),
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
            (l_task(l_handoff('L'), {'planner-L2.md': l_plan()}), 'size L is above M, and lean takes only size S or M'),
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
        check('(lane) full after planning: size L, three steps, a 13-criterion step, no recognized scope allow-list, '
              'a non-path scope entry, a contract path, or two AGENTS.md owners',
              all(r[0] == 'full' and r[1] == [want] for r, want in res))

        rec_m = '- lane: solo; point: before planning; reasons: size M decides before planning (no planner result yet)'
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
        # the T-0219 skips guard live. Negative control: with the Skipped write off, the close is refused.
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
            hp.write_text(re.sub(r'(?m)^size:.*$', 'size: M', hp.read_text(encoding='utf-8')), encoding='utf-8')
            lane_run_ = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'lane', str(d)],
                                       cwd=str(r), env=env_, capture_output=True, text=True)
            first = (d / 'skips.md').read_text(encoding='utf-8') if (d / 'skips.md').is_file() else ''
            subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'lane', str(d)], cwd=str(r),
                           env=env_, capture_output=True, text=True)
            second = (d / 'skips.md').read_text(encoding='utf-8')
            closed = subprocess.run([*tk, 'close', 'solo-a', '--reason', 'delivered by solo'], cwd=str(r), env=env_,
                                    capture_output=True, text=True)
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
        check('(lane solo close) negative control: with the Skipped write off the close by reason is refused '
              f'(rc={closed0.returncode} {closed0.stderr.strip()[:160]!r})',
              closed0.returncode == 1 and 'no ## Skipped entry' in closed0.stderr and '- skip:' not in second0)
        full_ = tmp / 'solo-full'
        subprocess.run(['git', 'init', '-q', str(full_)], check=True, capture_output=True)
        fd = full_ / '.sdlc' / 'big'
        fd.mkdir(parents=True)
        (fd / 'handoff.md').write_text(l_handoff('L'), encoding='utf-8')
        subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'lane', str(fd)], cwd=str(full_),
                       capture_output=True, text=True)
        check('(lane solo close) only lane solo writes Skipped entries: a size L ticket (lane full) gets none',
              '- skip:' not in (fd / 'skips.md').read_text(encoding='utf-8'))

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
    p = sub.add_parser('lint', help='check that criterion commands parse under bash -n; writes nothing')
    p.add_argument('target', help='a planner-*.md file, or a task dir (its newest planner-*.md by recorded run order)')
    p = sub.add_parser('next', help='print the next escalation action for a step dir; writes nothing')
    p.add_argument('step_dir', help='a step dir (step-<n>/) holding handoff.md and builder/verifier results')
    p = sub.add_parser('resume', help='print the step dir a resumed /chain continues from, and its next action')
    p.add_argument('task', help='a task dir holding step-<n>/ dirs')
    p = sub.add_parser('review', help='print whether a task dir\'s newest plan needs a plan review, and the next action')
    p.add_argument('task', help='a task dir holding planner-*.md and any plan-reviewer-*.md results')
    p = sub.add_parser('lane', help='print a task dir\'s lane (solo, lean, or full) and append it to its skips.md')
    p.add_argument('task', help='a task dir holding handoff.md and any planner-*.md results')
    p = sub.add_parser('swap', help="apply the newest verifier's one criterion swap to a step handoff")
    p.add_argument('step_dir', help='a step dir (step-<n>/) holding handoff.md and builder/verifier results')
    p.add_argument('--timeout', type=float, default=300, metavar='SECONDS',
                   help='per-span timeout for the new criterion (default 300); a timeout refuses. Spans run with '
                        'SDLC_BASE_SHA from <step dir>/base-sha, else HEAD')
    p = sub.add_parser('widen', help='add paths to the one scope criterion of a step handoff')
    p.add_argument('step_dir', help='a step dir (step-<n>/) holding handoff.md')
    p.add_argument('paths', nargs='*', metavar='path', help='repo-relative paths to allow (one or more)')
    p.add_argument('--timeout', type=float, default=300, metavar='SECONDS',
                   help='timeout for the widened span (default 300); a timeout refuses. It runs with '
                        'SDLC_BASE_SHA from <step dir>/base-sha, else HEAD')
    sub.add_parser('selftest', help='prove every case and every refusal fires')
    a, extra = ap.parse_known_args(argv)
    if extra and a.cmd != 'widen':
        ap.error(f'unrecognized arguments: {" ".join(extra)}')
    if a.cmd == 'widen':
        # a path such as -x reaches here as an unknown option; widen refuses it as a bad path
        if not 0 < a.timeout < float('inf'):
            print('steps: --timeout must be a finite number of seconds greater than 0', file=sys.stderr)
            return 1
        return cmd_widen(a.step_dir, a.paths + extra, a.timeout)
    if a.cmd == 'selftest':
        return selftest()
    if a.cmd == 'next':
        return cmd_next(a.step_dir)
    if a.cmd == 'resume':
        return cmd_resume(a.task)
    if a.cmd == 'review':
        return cmd_review(a.task)
    if a.cmd == 'lane':
        return cmd_lane(a.task)
    if a.cmd == 'swap':
        if not 0 < a.timeout < float('inf'):
            print('steps: --timeout must be a finite number of seconds greater than 0', file=sys.stderr)
            return 1
        return cmd_swap(a.step_dir, a.timeout)
    if a.cmd == 'lint':
        return cmd_lint(a.target)
    if a.guard_timeout is not None and not 0 < a.guard_timeout < float('inf'):
        print('steps: --guard-timeout must be a finite number of seconds greater than 0', file=sys.stderr)
        return 1
    return cmd_split(a.target, a.only, a.guard_timeout)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
