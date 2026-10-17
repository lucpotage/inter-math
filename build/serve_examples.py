#!/usr/bin/env python3
"""
The examples, served from the repository's root, never cached (a page shows
the package as `pnpm dist` last built it): http://127.0.0.1:3153/examples/

    pnpm examples
"""

import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 3153


class NoCache(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    print(f"http://127.0.0.1:{PORT}/examples/")
    ThreadingHTTPServer(("127.0.0.1", PORT), functools.partial(NoCache, directory=str(ROOT))).serve_forever()
