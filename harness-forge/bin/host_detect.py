#!/usr/bin/env python3
"""host_detect.py — detect which agentic host harness this process runs inside.

Catalog-wide host-harness awareness for nonoun-plugins (ROADMAP Track 5, increment 3). A plugin's
install/wiring (harness-forge's wire.py) + advisory hooks should know whether they're under Claude Code,
Codex, OpenCode, Gemini CLI, Pi, Hermes, or an unknown host — so they can adapt the integration or degrade
gracefully rather than assume Claude Code.

THE ONE LAW HERE — a host is detected from the PROCESS ENVIRONMENT, never the filesystem. Proven on a dev
machine: every host's config dir (~/.claude, ~/.codex, ~/.opencode, ~/.gemini, ~/.pi, ~/.hermes) and every
binary can ALL be present at once while exactly one host is live. A filesystem/PATH marker proves
*installed*, never *active*. Each live host sets a purpose-built env marker on the subprocesses it spawns;
those are the only positive signals. Filesystem is an opt-in weak tiebreaker that can never, alone, name a
host or raise confidence above "low". Shipping "unknown" is always correct over a wrong positive.

Env markers (source-verified against each host's source + GitHub's `gh` CLI agent-detector, which reads the
same set, so we inherit an externally-maintained contract):
  claude-code  CLAUDECODE=1                                                 high
  opencode     OPENCODE=1                                                   high
  gemini-cli   GEMINI_CLI=1                                                 high
  hermes       HERMES_SESSION_ID set                                        high
  codex        CODEX_SANDBOX=seatbelt | CODEX_SANDBOX_NETWORK_DISABLED=1    medium (only fires inside the sandbox)
  pi           — (no env marker by design → unknown unless --with-fs hints) —
  <generic>    AI_AGENT=<host>_<ver>_agent                                  low (emerging cross-vendor convention)

Usage:
  host-detect              # JSON for the current process env
  host-detect --host       # just the id (claude-code|codex|opencode|gemini-cli|hermes|pi|unknown)
  host-detect --explain    # JSON incl. every candidate considered
  host-detect --with-fs    # opt-in filesystem tiebreaker (returned at low confidence, explicitly labelled)
  host-detect selftest     # prove the detector
Exit: 0 identified · 3 unknown · 1 selftest fail · 2 usage. Stdlib only; Python 3.8+; zero non-stdlib imports
(so it vendors into a plugin's bin/ as a pure file copy — the corpus-reader pattern).
"""
import json
import os
import sys


def _eq(k, v):
    return lambda e: e.get(k) == v


def _set(k):
    return lambda e: bool(e.get(k))


# Ordered host rules — the FIRST matching host wins a multi-match tie: a more-specific INNER host (codex/
# gemini/opencode/hermes) before claude-code, whose CLAUDECODE + the generic AI_AGENT are the most-inherited
# and would otherwise mask an inner host (mirrors `gh`'s ordering). Each rule: (host, conf, label, predicate).
HOST_RULES = [
    ("codex",       "medium", "CODEX_SANDBOX=seatbelt",             _eq("CODEX_SANDBOX", "seatbelt")),
    ("codex",       "medium", "CODEX_SANDBOX_NETWORK_DISABLED=1",   _eq("CODEX_SANDBOX_NETWORK_DISABLED", "1")),
    ("gemini-cli",  "high",   "GEMINI_CLI=1",                       _eq("GEMINI_CLI", "1")),
    ("opencode",    "high",   "OPENCODE=1",                         _eq("OPENCODE", "1")),
    ("hermes",      "high",   "HERMES_SESSION_ID",                  _set("HERMES_SESSION_ID")),
    ("claude-code", "high",   "CLAUDECODE=1",                       _eq("CLAUDECODE", "1")),
]
_CONF_RANK = {"high": 3, "medium": 2, "low": 1}
_AI_AGENT_HOSTS = {"claude-code", "codex", "opencode", "gemini-cli", "gemini", "hermes", "pi"}
# Opt-in filesystem tiebreaker (NEVER a live verdict): <home-relative dir> -> host.
_FS_DIRS = {".claude": "claude-code", ".codex": "codex", ".opencode": "opencode",
            ".gemini": "gemini-cli", ".pi": "pi", ".hermes": "hermes"}

HOSTS = ("claude-code", "codex", "opencode", "gemini-cli", "hermes", "pi", "unknown")


def host_detect(env=None, *, allow_filesystem=False, root=None):
    """Detect the live host from the process ENVIRONMENT. Returns
    {"host", "confidence", "signals", "candidates"}. Fail-safe default: unknown/low. Pure function of `env`
    (defaults to os.environ) — injectable for tests."""
    e = os.environ if env is None else env
    order, by_host = [], {}
    for host, conf, label, pred in HOST_RULES:
        if pred(e):
            if host not in by_host:
                by_host[host] = {"host": host, "confidence": conf, "signals": [label]}
                order.append(host)
            else:
                by_host[host]["signals"].append(label)
                if _CONF_RANK[conf] > _CONF_RANK[by_host[host]["confidence"]]:
                    by_host[host]["confidence"] = conf
    # AI_AGENT — emerging cross-vendor convention; its leading token names the host. Corroborates a matched
    # host (added to its signals, confidence unchanged) or, alone, names one at low confidence.
    ai = (e.get("AI_AGENT") or "").strip()
    if ai:
        tok = ai.split("_", 1)[0].lower()
        tok = "gemini-cli" if tok == "gemini" else tok
        if tok in _AI_AGENT_HOSTS:
            if tok in by_host:
                by_host[tok]["signals"].append("AI_AGENT=" + ai)
            else:
                by_host[tok] = {"host": tok, "confidence": "low", "signals": ["AI_AGENT=" + ai]}
                order.append(tok)
    candidates = [by_host[h] for h in order]
    if candidates:
        win = candidates[0]
        return {"host": win["host"], "confidence": win["confidence"],
                "signals": list(win["signals"]), "candidates": candidates}
    # opt-in filesystem tiebreaker — installed != active; only a single unambiguous dir, always low + labelled.
    if allow_filesystem:
        home = root if root is not None else (e.get("HOME") or os.path.expanduser("~"))
        present = [(_FS_DIRS[d], d) for d in sorted(_FS_DIRS) if os.path.isdir(os.path.join(home, d))]
        if len(present) == 1:
            h, d = present[0]
            sig = "~/{} exists (installed, not necessarily active)".format(d)
            return {"host": h, "confidence": "low", "signals": [sig],
                    "candidates": [{"host": h, "confidence": "low", "signals": [sig]}]}
    return {"host": "unknown", "confidence": "low", "signals": [], "candidates": []}


def current_host(env=None):
    return host_detect(env)["host"]


def is_claude_code(env=None):
    return current_host(env) == "claude-code"


def selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    cases = [
        ({"CLAUDECODE": "1"},                            "claude-code", "high",   "CLAUDECODE=1"),
        ({"OPENCODE": "1"},                              "opencode",    "high",   "OPENCODE=1"),
        ({"GEMINI_CLI": "1"},                            "gemini-cli",  "high",   "GEMINI_CLI=1"),
        ({"HERMES_SESSION_ID": "abc-123"},               "hermes",      "high",   "HERMES_SESSION_ID"),
        ({"CODEX_SANDBOX": "seatbelt"},                  "codex",       "medium", "CODEX_SANDBOX=seatbelt"),
        ({"CODEX_SANDBOX_NETWORK_DISABLED": "1"},        "codex",       "medium", "CODEX_SANDBOX_NETWORK_DISABLED=1"),
        ({"AI_AGENT": "claude-code_2-1-175_agent"},      "claude-code", "low",    "AI_AGENT="),
        ({},                                             "unknown",     "low",    None),
        # must-NOT-false-positive: user inputs / config overrides / shared conventions are not host markers.
        ({"GEMINI_API_KEY": "sk-x"},                     "unknown",     "low",    None),
        ({"GEMINI_SANDBOX": "true"},                     "unknown",     "low",    None),
        ({"CODEX_HOME": "/home/u/.codex"},               "unknown",     "low",    None),
        ({"AGENTS_MD": "1"},                             "unknown",     "low",    None),
    ]
    for env, host, conf, sig in cases:
        r = host_detect(env=env)
        expect(r["host"] == host, "env {} → host {} (expected {})".format(env, r["host"], host))
        expect(r["confidence"] == conf, "env {} → confidence {} (expected {})".format(env, r["confidence"], conf))
        if sig:
            expect(any(sig in s for s in r["signals"]), "env {} → signals {} missing {}".format(env, r["signals"], sig))
    # AMBIGUITY (the load-bearing case): outer Claude + inner Codex → the inner host wins, both surfaced.
    amb = host_detect(env={"CLAUDECODE": "1", "CODEX_SANDBOX": "seatbelt"})
    expect(amb["host"] == "codex", "ambiguous (Claude+Codex) did not resolve to the inner host: {}".format(amb["host"]))
    expect(len(amb["candidates"]) == 2, "ambiguity not reported as 2 candidates: {}".format(amb["candidates"]))
    # CORROBORATION: AI_AGENT agreeing with a HIGH marker stays high + adds the signal.
    corr = host_detect(env={"CLAUDECODE": "1", "AI_AGENT": "claude-code_2-1-175_agent"})
    expect(corr["host"] == "claude-code" and corr["confidence"] == "high", "corroboration changed the verdict: {}".format(corr))
    expect(any("AI_AGENT" in s for s in corr["signals"]), "corroborating AI_AGENT not added to signals")
    # FILESYSTEM IS NEVER A LIVE VERDICT: three hosts' dirs present + empty env → never high, env-only stays unknown.
    with tempfile.TemporaryDirectory() as home:
        for d in (".codex", ".opencode", ".gemini"):
            os.makedirs(os.path.join(home, d))
        fs = host_detect(env={"HOME": home}, allow_filesystem=True, root=home)
        expect(fs["confidence"] != "high", "filesystem yielded a high-confidence verdict (forbidden): {}".format(fs))
        expect(fs["host"] == "unknown", "ambiguous filesystem (3 dirs) was not unknown: {}".format(fs["host"]))
        expect(host_detect(env={"HOME": home})["host"] == "unknown", "env-only on an empty env was not unknown")
        # a SINGLE installed dir is a low-confidence HINT only.
        with tempfile.TemporaryDirectory() as home1:
            os.makedirs(os.path.join(home1, ".gemini"))
            one = host_detect(env={"HOME": home1}, allow_filesystem=True, root=home1)
            expect(one["host"] == "gemini-cli" and one["confidence"] == "low", "single-dir fs hint wrong: {}".format(one))

    if fails:
        sys.stderr.write("host-detect selftest: FAIL\n")
        for f in fails:
            sys.stderr.write("  - {}\n".format(f))
        return 1
    print("host-detect selftest: OK (6 env-marker hosts + AI_AGENT fallback + the unknown default; 4 non-host "
          "negatives; the ambiguity case resolves to the inner host with both candidates surfaced; AI_AGENT "
          "corroborates without changing a HIGH verdict; filesystem is NEVER a live verdict — coexisting dirs → "
          "unknown, a single dir → low-confidence hint only)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    flags = [a for a in argv if a.startswith("--")]
    bad = [f for f in flags if f not in ("--host", "--explain", "--with-fs")]
    if bad or [a for a in argv if not a.startswith("--")]:
        print("usage: host-detect [--host | --explain | --with-fs] | selftest", file=sys.stderr)
        return 2
    r = host_detect(allow_filesystem="--with-fs" in flags)
    if "--host" in flags:
        print(r["host"])
    elif "--explain" in flags:
        print(json.dumps(r, indent=2))
    else:
        print(json.dumps({k: r[k] for k in ("host", "confidence", "signals")}))
    return 0 if r["host"] != "unknown" else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
