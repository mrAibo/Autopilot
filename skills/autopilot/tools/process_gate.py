#!/usr/bin/env python3
"""Fixed offline worker start gate: never execute before job assignment."""
import os
from pathlib import Path
import subprocess
import sys


def main(argv):
    if len(argv) < 2:
        return 2
    script = Path(argv[1])
    if (script.name != "offline_fixture_worker.py" or script.is_symlink()
            or not script.is_file() or
            script.resolve().parent != Path(__file__).resolve().parent):
        return 3
    # No uncontained worker may run. The supervisor owns the pipe, assigns
    # us to a kill-on-close job first, then emits the exact one-time token.
    if sys.stdin.readline() != "START\n":
        return 4
    if sys.stdin.read(1):
        return 5
    cmd = [sys.executable, "-B", str(script.resolve()), *argv[2:]]
    result = subprocess.run(cmd, cwd=Path.cwd(), stdin=subprocess.DEVNULL,
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace")
    sys.stdout.write(result.stdout[-2048:])
    sys.stderr.write(result.stderr[-2048:])
    return result.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
