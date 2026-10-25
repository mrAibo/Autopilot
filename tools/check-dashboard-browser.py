#!/usr/bin/env python3
"""Headless Chrome smoke test of Dashboard 3.0 with synthetic state.

Creates independent full-width and narrow screenshots; no external services.
On CI, set AUTOPILOT_SCREENSHOT_DIR to preserve screenshots as artifacts.
"""
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills" / "autopilot" / "phases" / "dashboard-template.html"


class RenderedDOM(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = []
        self.content = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if not self.hidden and tag == "section":
            self.sections.append(dict(attrs).get("class", ""))

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.content.append(data)


def fixture():
    return {
        "version": 2, "title": "Autopilot Dashboard UI Check",
        "slug": "dashboard-ui-check", "dir": "2026-10-25-dashboard-ui-check--wip",
        "mode": "semi", "depth": "normal", "tier": "T1",
        "startedAt": "2026-10-25T10:00:00+00:00",
        "updatedAt": "2026-10-25T10:04:00+00:00",
        "finishedAt": None, "rev": 3,
        "stages": [{"id": "preflight", "status": "done"},
                   {"id": "manifest", "status": "done"},
                   {"id": "briefing", "status": "done"},
                   {"id": "spec", "status": "done"},
                   {"id": "plan", "status": "done"},
                   {"id": "build", "status": "active", "startedAt": "2026-10-25T10:02:00+00:00"}],
        "requirements": {"total": 2, "done": 1, "inTicket": 1,
                         "inSpec": 0, "placeholder": 0, "deferred": 0, "dropped": 0},
        "tickets": [
            {"id": "01", "title": "Landing page", "wave": 1, "status": "done",
             "blockedBy": [], "zone": ["web/"], "requirements": ["R01"],
             "worktree": {"status": "released", "sourceCommit": "fedcba123"},
             "routing": {"provider": "anthropic", "model": "haiku", "effort": "low",
                         "score": 15, "reason": "Small fixed-layout UI task"}},
            {"id": "02", "title": "API and validation", "wave": 2, "status": "in-progress",
             "blockedBy": ["01"], "zone": ["api/"], "requirements": ["R02"],
             "startedAt": "2026-10-25T10:02:00+00:00",
             "worktree": {"status": "prepared"}, "retries": 1, "repairs": 0,
             "retryAdvice": {"category": "tests", "why": "fix failed assertions"},
             "routing": {"provider": "openai", "model": "gpt-6.1-sol",
                         "effort": "high", "score": 70, "reason": "Authentication risk"}}
        ],
        "tests": {"passed": 24, "failed": 0},
        "gates": {"G1": {"ok": True}, "G2": {"ok": True},
                  "G3": {"ok": True}},
        "reqList": [
            {"id": "R01", "text": "Readable landing page", "status": "done"},
            {"id": "R02", "text": "Validate input", "status": "in-ticket"}
        ],
        "usageEvents": [{"callId": "model:001", "ticket": "01", "source": "host-reported",
                         "input": 1400, "output": 600, "cacheRead": 300, "cacheWrite": 100}],
        "budgetTokens": 10000, "log": [], "beats": [], "waits": [],
        "concerns": [], "report": [], "additions": [], "debt": {},
        "waiting": None, "blind": None,
    }


def chrome_browser():
    return next((candidate for name in ("google-chrome", "google-chrome-stable",
                                        "chromium", "chromium-browser")
                 if (candidate := shutil.which(name))), None)


def main():
    browser = chrome_browser()
    if not browser:
        print("Chrome/Chromium not installed (browser test requires headless Chrome)", file=sys.stderr)
        return 2
    template = TEMPLATE.read_text(encoding="utf-8")
    anchor = "/*STATE-BEGIN*/window.STATE=null;/*STATE-END*/"
    if anchor not in template:
        print("Expected embedded dashboard state anchor missing", file=sys.stderr)
        return 2
    embedded = ("/*STATE-BEGIN*/window.STATE=" +
                json.dumps(fixture(), ensure_ascii=False).replace("</", "<\\/") +
                ";/*STATE-END*/")
    rendered = template.replace(anchor, embedded)
    output_dir = os.environ.get("AUTOPILOT_SCREENSHOT_DIR")
    with tempfile.TemporaryDirectory(prefix="dashboard-browser-") as temp:
        page = Path(temp) / "dashboard.html"
        page.write_text(rendered, encoding="utf-8")
        for label, dimensions in (("desktop", "1440,1800"), ("narrow", "460,2100")):
            arguments = [
                browser, "--headless=new", "--no-sandbox",
                "--disable-gpu", "--disable-dev-shm-usage",
                "--allow-file-access-from-files", "--hide-scrollbars",
                "--window-size=" + dimensions, "--virtual-time-budget=2000",
            ]
            proc = subprocess.run(arguments + ["--dump-dom", page.as_uri()],
                                  capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=45)
            if proc.returncode:
                print("Chrome smoke failed: " + proc.stderr[-1000:], file=sys.stderr)
                return 1
            parsed = RenderedDOM()
            parsed.feed(proc.stdout)
            visible = " ".join(parsed.content)
            if not any("ops" in cls.split() for cls in parsed.sections):
                print("Mission control not rendered: " + label, file=sys.stderr)
                return 1
            if not any("resource-card" in cls.split() for cls in parsed.sections):
                print("Resources panel not rendered: " + label, file=sys.stderr)
                return 1
            if not ("Изоляция и восстановление" in visible or "Isolation & recovery" in visible):
                print("Isolation/recovery panel not rendered: " + label, file=sys.stderr)
                return 1
            if ("haiku" not in visible or
                not ("Модели и ресурсы" in visible or "Models & resources" in visible)):
                print("Agent model text not visible: " + label, file=sys.stderr)
                return 1
            if output_dir:
                dest = Path(output_dir)
                dest.mkdir(parents=True, exist_ok=True)
                png = dest / ("dashboard-" + label + ".png")
                grab = subprocess.run(arguments + ["--screenshot=" + str(png), page.as_uri()],
                                      capture_output=True, text=True,
                                      encoding="utf-8", errors="replace", timeout=45)
                if grab.returncode or not png.is_file() or png.stat().st_size < 1000:
                    print("Screenshot failed: " + label + " " + grab.stderr[-500:], file=sys.stderr)
                    return 1
            print("Dashboard browser DOM OK: " + label)
    return 0


if __name__ == "__main__":
    sys.exit(main())
