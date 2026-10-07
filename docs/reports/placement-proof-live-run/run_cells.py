#!/usr/bin/env python3
"""Run T-0248 placement-proof cells and score them.

  run_cells.py run --type claude|solo|codex|codex-sub --arm registry|control|both [--briefs B01,B02|all]
                   [--pilot] [--jobs N] [--budget-usd X] [--results FILE]
  run_cells.py score --results FILE

One cell = one fresh session on a fresh copy of one fixture arm, given only the line `Path: <start folder>`
and the brief text. Placement is read from the copy with git (against the commit the copy started from):
the paths the session added or renamed to, or, when it added none, the existing files it modified. The
copy is committed afterwards, so the placement is a commit in the throwaway repository.
"""
import argparse
import concurrent.futures
import json
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import time

HERE = pathlib.Path(__file__).resolve().parent
WORK = pathlib.Path("/tmp/placement-proof-0248")
FIXTURES = WORK / "fixtures"
PLUGIN = HERE.parents[2] / "plugins" / "sdlc-lite"
GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="run", GIT_AUTHOR_EMAIL="run@example.invalid",
               GIT_COMMITTER_NAME="run", GIT_COMMITTER_EMAIL="run@example.invalid")
TIMEOUT = 900
lock = threading.Lock()
spent = {"usd": 0.0}


def git(cwd, *args):
    return subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=cwd, env=GIT_ENV,
                          capture_output=True, text=True).stdout


def load():
    briefs = json.loads((HERE / "briefs.json").read_text())
    key = json.loads((HERE / "answer-key.json").read_text())["answers"]
    return briefs, key


def cell_commands(typ, root, start, prompt):
    """Return (argv, env-extra) for the session type."""
    base_claude = ["claude", "-p", "--model", "sonnet", "--effort", "low", "--setting-sources", "project",
                   "--disable-slash-commands", "--strict-mcp-config", "--dangerously-skip-permissions",
                   "--no-session-persistence", "--output-format", "stream-json", "--verbose"]
    if typ == "claude":
        return base_claude + ["--", prompt], {}
    if typ == "solo":
        return (base_claude[:2] + ["--plugin-dir", str(PLUGIN), "--agent", "sdlc-lite:solo"] + base_claude[2:]
                + ["--", prompt]), {"SDLC_ROLE": "solo"}
    codex = ["codex", "exec", "-C", str(start), "-s", "workspace-write", "--add-dir", str(root),
             "-m", "gpt-6.1-sol", "-c", 'model_reasoning_effort="low"', "--ephemeral", "--json"]
    if typ == "codex":
        return codex + [prompt], {}
    if typ == "codex-sub":
        parent = ("Start exactly one subagent. Send it the text between the lines of dashes as its whole task, "
                  "wait for it to finish, then print its final reply verbatim.\n---\n" + prompt + "\n---")
        return codex + [parent], {}
    raise SystemExit("unknown type " + typ)


def parse_claude(out):
    cost = None
    tools = []
    final = ""
    for line in out.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for b in ev.get("message", {}).get("content", []):
                if b.get("type") == "tool_use":
                    inp = b.get("input", {})
                    tools.append(b.get("name", "") + " " + str(inp.get("file_path") or inp.get("command") or inp.get("path") or inp.get("pattern") or "")[:160])
        if ev.get("type") == "result":
            cost = ev.get("total_cost_usd")
            final = ev.get("result", "") or ""
    return cost, None, tools, final


def parse_codex(out):
    usage = None
    tools = []
    final = ""
    for line in out.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        t = ev.get("type", "")
        if t == "turn.completed":
            u = ev.get("usage") or {}
            usage = {k: (usage or {}).get(k, 0) + u.get(k, 0) for k in ("input_tokens", "cached_input_tokens", "output_tokens")}
        item = ev.get("item") or {}
        if t == "item.completed":
            if item.get("type") == "command_execution":
                tools.append("sh " + str(item.get("command", ""))[:160])
            elif item.get("type") in ("agent_message", "assistant_message"):
                final = item.get("text", "") or final
            elif item.get("type") not in ("reasoning",):
                tools.append(str(item.get("type")) + " " + json.dumps(item)[:120])
    return None, usage, tools, final


def placement(copy, base):
    git(copy, "add", "-A")
    rows = git(copy, "diff", "--cached", "-M", "--name-status", base).splitlines()
    added, modified, deleted = [], [], []
    for r in rows:
        parts = r.split("\t")
        st = parts[0][0]
        if st in "AC":
            added.append(parts[-1])
        elif st == "R":
            added.append(parts[-1])
            deleted.append(parts[1])
        elif st == "M":
            modified.append(parts[-1])
        elif st == "D":
            deleted.append(parts[-1])
    git(copy, "commit", "-q", "--allow-empty", "-m", "placement")
    return added, modified, deleted


def score_one(rec, key):
    k = key.get(rec["brief"])
    if not k:
        return None
    placed = rec["added"] or rec["modified"]
    ok = bool(placed) and all(any(p.startswith(a) for a in k["accepted"]) for p in placed)
    return ok


def run_cell(typ, arm, brief, pilot, results):
    root = WORK / "runs" / (("pilot-" + typ) if pilot else typ) / arm / brief["id"]
    if root.exists():
        shutil.rmtree(root)
    root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FIXTURES / arm, root)
    base = git(root, "rev-parse", "HEAD").strip()
    start = root / brief["start"]
    prompt = f"Path: {start}\n\n{brief['text']}"
    argv, extra = cell_commands(typ, root, start, prompt)
    t0 = time.time()
    try:
        p = subprocess.run(argv, cwd=start, env=dict(os.environ, **extra), capture_output=True, text=True,
                           timeout=TIMEOUT, stdin=subprocess.DEVNULL)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = "timeout", (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "timeout"
    dur = round(time.time() - t0, 1)
    (root.parent / (brief["id"] + ".stream.jsonl")).write_text(out)
    (root.parent / (brief["id"] + ".stderr.txt")).write_text(err or "")
    cost, usage, tools, final = (parse_claude(out) if typ in ("claude", "solo") else parse_codex(out))
    added, modified, deleted = placement(root, base)
    rec = dict(type=typ, arm=arm, brief=brief["id"], pilot=pilot, start=brief["start"], rc=rc, seconds=dur,
               cost_usd=cost, usage=usage, added=added, modified=modified, deleted=deleted,
               tools=tools[:40], final=(final or "")[:700])
    with lock:
        if cost:
            spent["usd"] += cost
        with open(results, "a") as f:
            f.write(json.dumps(rec) + "\n")
    print(f"{typ} {arm} {brief['id']} rc={rc} {dur}s cost={cost} usage={usage} added={added} modified={modified}", flush=True)
    return rec


def cmd_run(a):
    briefs, key = load()
    sel = [briefs["pilot"]] if a.pilot else [b for b in briefs["briefs"] if a.briefs == "all" or b["id"] in a.briefs.split(",")]
    arms = ["registry", "control"] if a.arm == "both" else [a.arm]
    results = pathlib.Path(a.results)
    cells = [(a.type, arm, b) for b in sel for arm in arms]

    def go(c):
        with lock:
            if spent["usd"] >= a.budget_usd:
                print("budget reached, skipping", c[0], c[1], c[2]["id"], flush=True)
                return None
        return run_cell(c[0], c[1], c[2], a.pilot, results)

    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        list(ex.map(go, cells))
    print("claude spend this invocation: $%.2f" % spent["usd"])


def cmd_score(a):
    briefs, key = load()
    rows = [json.loads(l) for l in open(a.results) if l.strip()]
    rows = [r for r in rows if not r["pilot"]]
    table = {}
    for r in rows:
        r["correct"] = score_one(r, key)
        table.setdefault(r["type"], {}).setdefault(r["arm"], {})[r["brief"]] = r
    for typ, arms in table.items():
        print(typ)
        for arm, cells in arms.items():
            n = sum(1 for c in cells.values() if c["correct"])
            print(f"  {arm}: {n}/{len(cells)}  wrong: {[b for b, c in sorted(cells.items()) if not c['correct']]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--type", required=True)
    r.add_argument("--arm", default="both")
    r.add_argument("--briefs", default="all")
    r.add_argument("--pilot", action="store_true")
    r.add_argument("--jobs", type=int, default=3)
    r.add_argument("--budget-usd", type=float, default=100.0)
    r.add_argument("--results", default=str(HERE / "runs.jsonl"))
    s = sub.add_parser("score")
    s.add_argument("--results", default=str(HERE / "runs.jsonl"))
    a = ap.parse_args()
    cmd_run(a) if a.cmd == "run" else cmd_score(a)


if __name__ == "__main__":
    main()
