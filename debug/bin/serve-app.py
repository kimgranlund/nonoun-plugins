#!/usr/bin/env python3
"""Serve a SHIPPED app from a debug run — the dev-factory builds `capability/app/` (a real UI) plus the sibling
capability modules it imports via `../`. Document root = the run's `capability/` dir so `/app/index.html`'s
relative imports (`./main.mjs`, `../leaderboard/index.mjs`, …) resolve. `.mjs` is served as a JS MIME
(http.server's default is octet-stream, which browsers refuse for ES modules).

    python3 debug/bin/serve-app.py <run-name> [PORT]   ->   http://127.0.0.1:PORT/app/index.html
"""
import http.server
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402


def main(argv):
    if not argv:
        print("usage: serve-app.py <run-name> [PORT]", file=sys.stderr)
        return 2
    name = argv[0]
    port = int(argv[1]) if len(argv) > 1 else 8900
    root = os.path.join(C.instance_dir(name), "capability")
    if not os.path.isdir(root):
        print(f"no capability/ dir in run '{name}' — nothing shipped to serve ({root})", file=sys.stderr)
        return 1

    class H(http.server.SimpleHTTPRequestHandler):
        extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                          ".mjs": "text/javascript", ".js": "text/javascript", ".css": "text/css"}

        def __init__(self, *a, **k):
            super().__init__(*a, directory=root, **k)

        def log_message(self, *a):
            pass

    print(f"serving {root}")
    print(f"  ▶ http://127.0.0.1:{port}/app/index.html")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
