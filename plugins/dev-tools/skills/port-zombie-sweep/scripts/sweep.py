#!/usr/bin/env python3
"""List dev servers holding TCP LISTEN ports and rank likely zombies. Read-only, kills nothing.

Usage: sweep.py [--all] [--each] [--min-port N]
  --kill-list  print only the suggested PIDs, space separated
  --each       one row per process instead of groups
  --all        include non-dev processes (system daemons, apps)
  --min-port   ignore ports below N (default 1024)
"""
import argparse, os, re, subprocess
from collections import defaultdict

DEV = re.compile(r"\b(node|bun|deno|vite|next|webpack|esbuild|astro|nuxt|remix|storybook|"
                 r"python\d*(\.\d+)?|uvicorn|gunicorn|flask|ruby|rails|puma|php|java|hugo|"
                 r"jekyll|wrangler|http-server|serve)\b", re.I)

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout

def days(etime):  # [[dd-]hh:]mm:ss -> float days
    d, _, rest = etime.rpartition("-")
    parts = [int(x) for x in rest.split(":")]
    while len(parts) < 3: parts.insert(0, 0)
    h, m, s = parts
    return int(d or 0) + (h * 3600 + m * 60 + s) / 86400

ap = argparse.ArgumentParser()
ap.add_argument("--all", action="store_true")
ap.add_argument("--kill-list", action="store_true")
ap.add_argument("--each", action="store_true")
ap.add_argument("--min-port", type=int, default=1024)
a = ap.parse_args()

ports, pid = defaultdict(set), None
for line in run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN", "-Fpn"]).splitlines():
    if line[0] == "p": pid = line[1:]
    elif line[0] == "n":
        p = int(line.rsplit(":", 1)[1])
        if p >= a.min_port: ports[pid].add(p)
if not ports:
    raise SystemExit("no listening ports")

info = {}
for line in run(["ps", "-o", "pid=,ppid=,etime=,args=", "-p", ",".join(ports)]).splitlines():
    f = line.split(None, 3)
    if len(f) == 4: info[f[0]] = f[1:]

cwd, pid = {}, None
for line in run(["lsof", "-a", "-d", "cwd", "-Fn", "-p", ",".join(ports)]).splitlines():
    if line[0] == "p": pid = line[1:]
    elif line[0] == "n": cwd[pid] = line[1:]

rows = []
for pid, ps in ports.items():
    if pid not in info: continue
    ppid, etime, args = info[pid]
    exe = os.path.basename(args.split()[0])
    dev = bool(DEV.search(exe) or DEV.search(args[:200]))
    if not dev and not a.all: continue
    d, wd, why = days(etime), cwd.get(pid, "?"), []
    if dev:
        if ppid == "1": why.append("orphan")
        if wd not in ("/", "?") and not os.path.isdir(wd): why.append("cwd-gone")
        if d >= 1: why.append(f"{d:.0f}d-old")
    score = 3 * ("orphan" in why) + 3 * ("cwd-gone" in why) + min(d, 7) / 7
    rows.append((score, pid, ppid, d, sorted(ps), args, wd, why, exe))

rows.sort(key=lambda r: -r[0])
if a.kill_list:
    print(" ".join(r[1] for r in rows if r[0] >= 3)); raise SystemExit
if a.each:
    for score, pid, ppid, d, ps, args, wd, why, exe in rows:
        pl = ",".join(map(str, ps[:4])) + (f" +{len(ps)-4}" if len(ps) > 4 else "")
        print(f"{pid:>6}  ppid {ppid:>6}  {d:5.1f}d  ports {pl:<22} {','.join(why) or '-':<22} {wd}")
        print(f"        {args[:140]}")
else:
    groups = defaultdict(list)
    for r in rows:
        tags = tuple(t for t in r[7] if not t.endswith("d-old"))
        groups[(r[6], r[8], tags)].append(r)
    for (wd, exe, tags), g in sorted(groups.items(), key=lambda kv: -max(r[0] for r in kv[1])):
        ps = sorted(p for r in g for p in r[4])
        pl = ",".join(map(str, ps[:3])) + (f" +{len(ps)-3}" if len(ps) > 3 else "")
        oldest = max(r[3] for r in g)
        print(f"{len(g):>4}x {exe:<12} {','.join(tags) or 'live':<16} oldest {oldest:4.1f}d  ports {pl:<20} {wd}")
        if tags: print(f"      kill {' '.join(r[1] for r in g[:12])}{' ...' if len(g) > 12 else ''}")

kill = [r[1] for r in rows if r[0] >= 3]
print(f"\n{len(rows)} dev processes. Suggested (orphan or cwd-gone): {len(kill)}")
print("Full kill list: sweep.py --kill-list")
