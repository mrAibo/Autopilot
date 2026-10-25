#!/usr/bin/env python3
"""Test-only process: deterministic local file edit, never contacts a provider."""
import argparse
from pathlib import Path
import sys
import time

FIXTURES = {
    "calc-add": ("src/core/calc.py",
                 "def add(a, b):\n    return a - b\n",
                 "def add(a, b):\n    return a + b\n"),
    "calc-mul": ("src/bot/calc.py",
                 "def mul(a, b):\n    return a + b\n",
                 "def mul(a, b):\n    return a * b\n"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, required=True)
    parser.add_argument("--fixture", choices=sorted(FIXTURES), required=True)
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--fail", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.delay <= 20:
        return 2
    # The parent supervisor validates the ticket/zone and temporary Git root.
    # This worker accepts only the two exact baseline examples above.
    relative, old, new = FIXTURES[args.fixture]
    target = args.worktree.resolve()
    path = target / relative
    if (not path.is_file() or path.is_symlink() or
            not path.resolve().is_relative_to(target)):
        return 3
    if path.read_text(encoding="utf-8") != old:
        return 4
    print("offline-worker-started", flush=True)
    time.sleep(args.delay)
    if args.fail:
        return 17
    path.write_text(new, encoding="utf-8")
    print("offline-worker-edited-known-fixture", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
