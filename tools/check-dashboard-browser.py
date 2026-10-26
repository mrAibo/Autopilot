#!/usr/bin/env python3
"""Headless Chrome smoke test of Dashboard 3.1 with synthetic state.

Creates independent full-width and narrow screenshots; no external services.
On CI, set AUTOPILOT_SCREENSHOT_DIR to preserve screenshots as artifacts.
"""
from html import unescape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
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
    aliases = ("google-chrome", "google-chrome-stable", "chromium",
               "chromium-browser", "chrome", "msedge")
    found = next((candidate for name in aliases
                  if (candidate := shutil.which(name))), None)
    if found:
        return found
    # Official browser install paths on Windows, without changing host PATH.
    if os.name == "nt":
        for variable, relative in (
            ("PROGRAMFILES", "Google/Chrome/Application/chrome.exe"),
            ("PROGRAMFILES", "Microsoft/Edge/Application/msedge.exe"),
            ("PROGRAMFILES(X86)", "Microsoft/Edge/Application/msedge.exe"),
            ("LOCALAPPDATA", "Google/Chrome/Application/chrome.exe"),
        ):
            base = os.getenv(variable)
            if base:
                path = Path(base) / relative
                if path.is_file():
                    return str(path)
    return None


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
        for label, dimensions, lang, theme in (
                ("desktop", "1440,1800", "ru", "light"),
                ("narrow", "460,2100", "ru", "dark"),
                ("mobile", "390,2100", "en", "light"),
                ("mobile-dark", "390,2100", "en", "dark"),
        ):
            probe = """
<script>
try {
  render(%(lang)s);
  applyTheme(%(theme)s);
  // Exercise the real delegated language-click rerender and a later refresh.
  const targetLang = %(lang)s === 'ru' ? 'en' : 'ru';
  const languageButton = document.querySelector('#app button[data-lang="' + targetLang + '"]');
  languageButton.focus();
  languageButton.click();
  const language_click_kept_focus = document.activeElement?.getAttribute('data-lang') === targetLang;
  render(%(lang)s);
  const refresh_kept_focus = document.activeElement?.getAttribute('data-lang') === targetLang;
  const skip = document.querySelector('#app .skip-link');
  const skip_labelled = !!skip && skip.textContent.trim() ===
    (%(lang)s === 'ru' ? 'Перейти к содержимому' : 'Skip to main content');
  const skip_target = !!document.querySelector('#mission[tabindex="-1"]');
  if (skip) {skip.focus(); render(%(lang)s);}
  const skip_kept_focus = !!skip && document.activeElement?.getAttribute('data-focus-key') === 'skip';
  const navLink = document.querySelector('#app a[data-focus-key="nav-models"]');
  let nav_kept_focus = true;
  if (navLink && getComputedStyle(document.querySelector('.cockpit-rail')).display !== 'none') {
    navLink.focus();
    render(%(lang)s);
    nav_kept_focus = document.activeElement?.getAttribute('data-focus-key') === 'nav-models';
  }
  const external = document.createElement('button');
  external.textContent = 'External focus';
  document.body.appendChild(external);
  external.focus();
  render(%(lang)s);
  const outside_focus_preserved = document.activeElement === external;
  external.remove();
  const html = document.documentElement;
  const rail = document.querySelector('.cockpit-rail');
  const app = document.getElementById('app');
  const visible = app ? app.innerText : '';
  const controls = [...document.querySelectorAll('#app button')];
  const css = getComputedStyle(html);
  const variable = name => css.getPropertyValue(name).trim();
  const luminosity = hex => {
    const rgb = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16) / 255)
      .map(v => v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
    return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
  };
  const contrast = (fg, bg) => {
    const a = luminosity(fg), b = luminosity(bg);
    return Math.round(((Math.max(a,b)+0.05)/(Math.min(a,b)+0.05)) * 100)/100;
  };
  const result = {
    width: window.innerWidth,
    client: html.clientWidth,
    document_width: html.scrollWidth,
    body_width: document.body.scrollWidth,
    lang: html.lang,
    theme: html.getAttribute('data-theme'),
    rail_visible: !!rail && getComputedStyle(rail).display !== 'none',
    background: variable('--bg'),
    muted_contrast_on_inset: contrast(variable('--mut'), variable('--inset')),
    quiet_contrast_on_inset: contrast(variable('--quiet'), variable('--inset')),
    focusable_controls: document.querySelectorAll('#app button, #app a[href]').length,
    language_click_kept_focus, refresh_kept_focus, skip_kept_focus,
    skip_labelled, skip_target, nav_kept_focus, outside_focus_preserved,
    unlabeled_buttons: controls.filter(b => !b.innerText.trim() &&
      !(b.getAttribute('aria-label') || b.getAttribute('title'))).length,
    main_landmark: !!document.querySelector('main.cockpit-content'),
    has_mission: !!document.getElementById('mission'),
    has_tasks: !!document.getElementById('tasks'),
    has_models: !!document.getElementById('models'),
    has_quality: !!document.getElementById('quality'),
    has_resources: !!document.querySelector('.resource-card'),
    has_isolation: visible.includes('Изоляция и восстановление') ||
                   visible.includes('Isolation & recovery'),
    has_model_name: visible.includes('haiku'),
    has_models_title: visible.includes('Модели и ресурсы') ||
                      visible.includes('Models & resources'),
  };
  const output = document.createElement('pre');
  output.id = 'autopilot-layout-probe';
  output.hidden = true;
  output.textContent = JSON.stringify(result);
  document.body.appendChild(output);
} catch (e) {
  const output = document.createElement('pre');
  output.id = 'autopilot-layout-probe';
  output.textContent = JSON.stringify({error: String(e)});
  document.body.appendChild(output);
}
</script>
""" % {"lang": json.dumps(lang), "theme": json.dumps(theme)}
            child = Path(temp) / ("dashboard-" + label + ".html")
            child.write_text(rendered.replace("</body>", probe + "</body>"), encoding="utf-8")
            # Headless Chrome clamps top-level windows to around 500 CSS px.
            # A fixed-width same-origin iframe is an actual 390/460 CSS px
            # viewport, so its own media queries and horizontal overflow are real.
            use_frame = label != "desktop"
            if use_frame:
                requested_width = int(dimensions.split(",")[0])
                loader = """<!doctype html><html><head><meta charset="utf-8"></head>
<body style="margin:0">
<iframe id="dashboard-frame" src="%(src)s"
  style="border:0;width:%(width)spx;height:2100px;display:block"></iframe>
<script>
const repeat = setInterval(() => {
  try {
    const child = document.getElementById('dashboard-frame').contentDocument;
    const source = child && child.getElementById('autopilot-layout-probe');
    if (!source) return;
    const mirror = document.createElement('pre');
    mirror.id = 'autopilot-layout-probe';
    mirror.hidden = true;
    mirror.textContent = source.textContent;
    document.body.appendChild(mirror);
    clearInterval(repeat);
  } catch (e) {
    const mirror = document.createElement('pre');
    mirror.id = 'autopilot-layout-probe';
    mirror.textContent = JSON.stringify({error: String(e)});
    document.body.appendChild(mirror);
    clearInterval(repeat);
  }
}, 50);
</script></body></html>""" % {"src": child.name, "width": requested_width}
                page.write_text(loader, encoding="utf-8")
            else:
                page.write_text(child.read_text(encoding="utf-8"), encoding="utf-8")
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
            if not use_frame:
                needed = ('class="cockpit-rail"', 'class="cockpit-content"',
                          'id="mission"', 'id="tasks"', 'id="models"',
                          'id="quality"', 'href="#models"', 'class="spotlight"')
                missing = [part for part in needed if part not in proc.stdout]
                if missing:
                    print("Command center missing: " + label + " " +
                          repr(missing), file=sys.stderr)
                    return 1
            match = re.search(r'<pre id="autopilot-layout-probe"[^>]*>(.*?)</pre>',
                              proc.stdout, flags=re.DOTALL)
            if not match:
                print("Browser layout probe absent: " + label, file=sys.stderr)
                return 1
            metrics = json.loads(unescape(match.group(1)))
            print("Dashboard layout probe:", label, metrics)
            if metrics.get("error"):
                print("Browser layout probe failed: " + metrics["error"], file=sys.stderr)
                return 1
            expected_width = int(dimensions.split(",")[0])
            if use_frame and (metrics.get("width") != expected_width or
                              metrics.get("client") != expected_width):
                print("False narrow viewport: " + label + " " + repr(metrics),
                      file=sys.stderr)
                return 1
            if metrics["document_width"] > metrics["client"] + 2 or (
                    metrics["body_width"] > metrics["client"] + 2):
                print("Horizontal overflow: " + label + " " + repr(metrics),
                      file=sys.stderr)
                return 1
            # AA contrast threshold for normal-sized panel labels.
            # The inset surface is the lower-contrast case versus the card.
            if (metrics["muted_contrast_on_inset"] < 4.5 or
                    metrics["quiet_contrast_on_inset"] < 4.5):
                print("Panel label contrast below 4.5:1: " + label + " " +
                      repr(metrics), file=sys.stderr)
                return 1
            if (metrics["lang"] != lang or metrics["theme"] != theme or
                    metrics["rail_visible"] != (label == "desktop") or
                    metrics["focusable_controls"] < 5 or
                    metrics["unlabeled_buttons"] != 0 or
                    not all(metrics.get(k) for k in (
                        "language_click_kept_focus", "refresh_kept_focus",
                        "skip_kept_focus", "skip_labelled", "skip_target",
                        "nav_kept_focus", "outside_focus_preserved"))):
                print("Accessibility/theme/layout assertion failed: " + label +
                      " " + repr(metrics), file=sys.stderr)
                return 1
            required = ("main_landmark", "has_mission", "has_tasks", "has_models", "has_quality",
                        "has_resources", "has_isolation",
                        "has_model_name", "has_models_title")
            if not all(metrics.get(x) for x in required):
                print("Dashboard sections/text missing: " + label + " " +
                      repr(metrics), file=sys.stderr)
                return 1
            if not use_frame:
                parsed = RenderedDOM()
                parsed.feed(proc.stdout)
                if not any("ops" in cls.split() for cls in parsed.sections):
                    print("Mission control not rendered: " + label, file=sys.stderr)
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
