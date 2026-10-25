#!/usr/bin/env python3
"""Syntax-check every inline JavaScript block inside Dashboard 3.0."""
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGE = ROOT / "skills" / "autopilot" / "phases" / "dashboard-template.html"


def main():
    html = PAGE.read_text(encoding="utf-8")
    if "const opsBlock" not in html or "const resourceBlock" not in html:
        print("Dashboard 3.0 sections missing", file=sys.stderr)
        return 2
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", html, re.I | re.S)
    source = [s for s in scripts if s.strip()]
    if not source:
        print("Dashboard has no inline scripts", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="autopilot-js-") as tmp:
        for i, js in enumerate(source):
            output = pathlib.Path(tmp) / ("inline-%s.js" % i)
            output.write_text(js, encoding="utf-8")
            r = subprocess.run(["node", "--check", str(output)], capture_output=True, text=True)
            if r.returncode:
                print("%s: %s" % (output.name, r.stderr), file=sys.stderr)
                return r.returncode
    print("Dashboard JS syntax OK (%d inline scripts)" % len(source))
    return 0


if __name__ == "__main__":
    sys.exit(main())
