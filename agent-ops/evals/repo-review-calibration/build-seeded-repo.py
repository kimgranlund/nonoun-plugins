#!/usr/bin/env python3
"""build-seeded-repo.py <dir> — write a synthetic repo with PLANTED architectural smells.

The repo-review calibration fixture. Where council-calibration tests the agentic *council*, this tests
the `repo-review` *skill* (the surface the 2026-06-11 real-repo audit flagged as having zero
behavioral coverage — its own P0-1). The fixture is a small, deliberately-flawed codebase that a
healthy repo-review pass must surface in its cascade-ranked backlog. Built on demand (never committed)
so the catalog never ships intentional-vulnerability files, and so it stays inert (never run/imported).

Six planted smells, each mapping to a rubric dimension repo-review tailors + a check.py key:
  S1  god module            — app.py does parsing + db + http + rendering in one ~file (no separation)
  S2  naming drift          — camelCase and snake_case mixed in the same module
  S3  declared-vs-actual    — README claims "stdlib only, no dependencies"; app.py imports `requests`
  S4  duplicated logic      — the same _is_valid_email copy-pasted in two files (drift risk)
  S5  command injection      — deploy.py shells out with an unsanitized input (trust-boundary smell)
  S6  no agent memory/tests  — no AGENTS.md/CLAUDE.md, no CHANGELOG, no tests at all

A healthy repo-review must name all six (in some tier). A miss is a real finding about the instrument.
Stdlib only.
"""
import os
import sys


def _w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build(d):
    # README declares a contract the code breaks (S3) + advertises "well-tested" (S6 contradiction)
    _w(os.path.join(d, "README.md"),
       "# Widget Service\n\n"
       "A small service. **Zero dependencies — stdlib only.** Clean, well-tested, production-ready.\n\n"
       "Run: `python3 app.py`\n")

    # S1 god module: parsing + db + http + rendering in one place. S2 naming drift (camelCase + snake_case).
    # S3: imports `requests` despite the README's stdlib-only claim. S4: _is_valid_email lives here too.
    _w(os.path.join(d, "app.py"),
       "import sqlite3\n"
       "import http.server\n"
       "import requests  # external dependency — the README says stdlib only\n\n"
       "def getUserData(userId):            # camelCase\n"
       "    conn = sqlite3.connect('app.db')\n"
       "    return conn.execute('select * from users where id=' + str(userId)).fetchall()\n\n"
       "def render_user_page(user_rows):    # snake_case — naming drifts within one module\n"
       "    return '<html>' + str(user_rows) + '</html>'\n\n"
       "def _is_valid_email(s):             # duplicated verbatim in validate.py (S4)\n"
       "    return '@' in s and '.' in s.split('@')[-1]\n\n"
       "def fetchRemote(url):               # camelCase again; also the http surface, all in one file\n"
       "    return requests.get(url).text\n\n"
       "class Handler(http.server.BaseHTTPRequestHandler):\n"
       "    def do_GET(self):\n"
       "        self.wfile.write(render_user_page(getUserData(self.path)).encode())\n\n"
       "if __name__ == '__main__':\n"
       "    http.server.HTTPServer(('', 8000), Handler).serve_forever()\n")

    # S4 duplicated logic: the same validator, copy-pasted (will drift)
    _w(os.path.join(d, "validate.py"),
       "def _is_valid_email(s):             # copy-pasted from app.py — no single source of truth\n"
       "    return '@' in s and '.' in s.split('@')[-1]\n\n"
       "def validate_signup(form):\n"
       "    return _is_valid_email(form.get('email', ''))\n")

    # S5 command injection / trust boundary: unsanitized input flows into a shell
    _w(os.path.join(d, "deploy.py"),
       "import os\n"
       "import sys\n\n"
       "def deploy(branch):\n"
       "    # branch comes straight from argv (untrusted) and is interpolated into a shell command\n"
       "    os.system('git push origin ' + branch)        # command injection: `main; rm -rf /`\n\n"
       "if __name__ == '__main__':\n"
       "    deploy(sys.argv[1])\n")

    # S6: there is deliberately NO AGENTS.md, NO CLAUDE.md, NO CHANGELOG, NO tests/ — the README's
    # "well-tested" claim is false, and there is zero agent-facing memory. (Nothing to write here.)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: build-seeded-repo.py <target-dir>", file=sys.stderr)
        sys.exit(2)
    build(sys.argv[1])
    print(f"built repo-review fixture `seeded-smell-repo` at {sys.argv[1]} "
          f"(6 planted smells: god-module · naming-drift · declared-vs-actual · dup-logic · cmd-injection · no-memory/tests)")
