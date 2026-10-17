#!/usr/bin/env python3
"""
The build, run again, changed no tracked file: what a release checks. A WOFF2
counts as unchanged when its tables are the committed file's, byte for byte:
Brotli doesn't compress the same on every platform (Linux x86 and ARM differ
on a file now and then), and the font is what has to stay the same. Such a
file is put back as committed; any other change is listed, and the exit code
is 1.

    build/.venv/bin/python build/check_build.py
"""

import io
import subprocess
import sys

from fontTools.ttLib import TTFont


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def same_font(path: str) -> bool:
    committed, built = TTFont(io.BytesIO(git("show", f"HEAD:{path}"))), TTFont(path)
    tags = set(committed.reader.keys())
    return tags == set(built.reader.keys()) and all(committed.getTableData(t) == built.getTableData(t) for t in tags)


if __name__ == "__main__":
    changed = []
    for line in git("status", "--porcelain").decode().splitlines():
        status, path = line[:2], line[3:]
        if status == " M" and path.endswith(".woff2") and same_font(path):
            print(f"{path}: the committed font, compressed otherwise (put back)")
            git("checkout", "--", path)
        else:
            changed.append(line)
    if changed:
        print("the build changed tracked files:", *changed, sep="\n  ")
        sys.exit(1)
