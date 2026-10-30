#!/usr/bin/env python3
"""Active repo registry: .sdlc/fleet.json (fleet.json in the work root under a work_root line). No model call; reads and writes only that file.

Usage: fleet_config.py [--file PATH] show [--active] | add --path P --name N --factory C [--gh O/R]
       | exclude REPO --reason R | include REPO | selftest
Schema: docs/specs/sdlc/fleet-config.md. A malformed file exits 1 naming the line.
"""
import argparse, datetime, json, os, pathlib, re, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roots  # same scripts/ dir: the resolver that places fleet.json (T-0621)

DEFAULT = os.path.join(".sdlc", "fleet.json")
REQ = ("path", "name", "factory", "status")


class FleetError(Exception):
    pass


def default_path(top="."):
    """The default registry file of the repo at `top`: roots.py's fleet path (docs/work/fleet.json under a
    work_root line, else .sdlc/fleet.json). A config roots.py refuses keeps the .sdlc path, so show still reads."""
    state = pathlib.Path(top) / ".sdlc"
    try:
        return str(roots.resolve(state).fleet)
    except roots.Fail:
        return str(state / "fleet.json")


def _line_of(text, idx):
    """Line where the idx-th element of the top-level repos list starts (1 if not found)."""
    try:
        m = re.search(r'"repos"\s*:\s*\[', text)
        pos, dec = m.end(), json.JSONDecoder()
        for i in range(idx + 1):
            while text[pos] in " \t\r\n,":
                pos += 1
            if i == idx:
                return text.count("\n", 0, pos) + 1
            pos = dec.raw_decode(text, pos)[1]
    except (AttributeError, IndexError, ValueError):
        pass
    return 1


def load(path):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        raise FleetError("%s: %s" % (path, e.strerror))
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise FleetError("%s:%d: %s" % (path, e.lineno, e.msg))
    if not isinstance(data, dict) or not isinstance(data.get("repos"), list):
        raise FleetError("%s:1: top level must be an object with a repos list" % path)
    seen = set()
    for i, r in enumerate(data["repos"]):
        ln = _line_of(text, i)
        if not isinstance(r, dict):
            raise FleetError("%s:%d: repo entry must be an object" % (path, ln))
        for k in REQ:
            if not isinstance(r.get(k), str) or not r[k]:
                raise FleetError("%s:%d: repo %s missing %s" % (path, ln, r.get("name"), k))
        if r["status"] not in ("active", "excluded"):
            raise FleetError("%s:%d: status must be active or excluded" % (path, ln))
        if r["status"] == "excluded" and not (r.get("reason") and r.get("date")):
            raise FleetError("%s:%d: excluded repo %s needs reason and date" % (path, ln, r["name"]))
        if r["name"] in seen:
            raise FleetError("%s:%d: duplicate name %s" % (path, ln, r["name"]))
        seen.add(r["name"])
    return data


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def find(data, name):
    for r in data["repos"]:
        if r["name"] == name:
            return r
    raise FleetError("no repo named %s" % name)


def show(data, active_only):
    for r in data["repos"]:
        if active_only and r["status"] != "active":
            continue
        extra = " (%s, %s)" % (r.get("date"), r.get("reason")) if r["status"] == "excluded" else ""
        print("%-9s %-18s %-22s %s%s" % (r["status"], r["name"], r["factory"], r["path"], extra))


def selftest():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "fleet.json")
    save(p, {"version": 1, "repos": []})
    data = load(p)
    data["repos"] += [
        {"path": "/a", "name": "a", "factory": "ca", "status": "active"},
        {"path": "/b", "name": "b", "factory": "cb", "status": "excluded", "reason": "r", "date": "2026-10-06"}]
    save(p, data)
    data = load(p)
    act = [r["name"] for r in data["repos"] if r["status"] == "active"]
    assert act == ["a"] and len(data["repos"]) == 2, "active filter"
    open(p, "w").write('{\n "repos": [\n  {"name": "x",\n}\n ]\n}\n')
    try:
        load(p)
        raise AssertionError("malformed file loaded")
    except FleetError as e:
        assert ":4:" in str(e) or ":5:" in str(e), str(e)
    open(p, "w").write('{"repos": [\n{"path": "/a", "name": "a", "factory": "c"}\n]}\n')
    try:
        load(p)
        raise AssertionError("incomplete entry loaded")
    except FleetError as e:
        assert ":2:" in str(e) or ":1:" in str(e), str(e)
    for body, want in (('{"repos": [\n{"path": "/a", "name": "a", "factory": "c", "status": "active"},\n{"path": "/b"},\n5\n]}\n', ":3:"),
                       ('{"repos": [\n{"path": "/a", "name": "a", "factory": "c", "status": "active"},\n5\n]}\n', ":3:")):
        open(p, "w").write(body)
        try:
            load(p)
            raise AssertionError("bad entry loaded")
        except FleetError as e:
            assert want in str(e), str(e)
    top = os.path.join(d, "top")
    os.makedirs(os.path.join(top, ".sdlc"))
    assert default_path(top) == os.path.join(top, ".sdlc", "fleet.json"), "default without work_root"
    open(os.path.join(top, ".sdlc", "config"), "w").write("work_root: docs/work\n")
    assert default_path(top) == os.path.join(top, "docs", "work", "fleet.json"), "default under work_root"
    open(os.path.join(top, ".sdlc", "config"), "w").write("work_root: ../x\n")
    assert default_path(top) == os.path.join(top, ".sdlc", "fleet.json"), "refused config keeps the .sdlc path"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show"); s.add_argument("--active", action="store_true")
    a = sub.add_parser("add")
    for k in ("path", "name", "factory"):
        a.add_argument("--" + k, required=True)
    a.add_argument("--gh")
    e = sub.add_parser("exclude"); e.add_argument("repo"); e.add_argument("--reason", required=True)
    i = sub.add_parser("include"); i.add_argument("repo")
    sub.add_parser("selftest")
    args = ap.parse_args()
    args.file = args.file or default_path()
    try:
        if args.cmd == "selftest":
            return selftest()
        data = load(args.file)
        if args.cmd == "show":
            show(data, args.active)
            return
        if args.cmd == "add":
            if any(r["name"] == args.name for r in data["repos"]):
                raise FleetError("repo %s already present" % args.name)
            r = {"path": args.path, "name": args.name, "factory": args.factory, "status": "active"}
            if args.gh:
                r["gh"] = args.gh
            data["repos"].append(r)
        elif args.cmd == "exclude":
            r = find(data, args.repo)
            r.update(status="excluded", reason=args.reason, date=datetime.date.today().isoformat())
        elif args.cmd == "include":
            r = find(data, args.repo)
            r["status"] = "active"; r.pop("reason", None); r.pop("date", None)
        save(args.file, data)
        print("ok")
    except FleetError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    except AssertionError as ex:
        print("selftest FAILED: %s" % ex, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
