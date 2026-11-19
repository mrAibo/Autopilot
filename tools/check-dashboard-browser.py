#!/usr/bin/env python3
"""Headless Chrome smoke test of Dashboard 3.1 with synthetic state.

Creates independent full-width and narrow screenshots; no external services.
On CI, set AUTOPILOT_SCREENSHOT_DIR to preserve screenshots as artifacts.

`--designs [DIR]` instead takes one screenshot of each of the six designs at 1440 and 400 px
(default DIR: docs/autopilot/dashboard-designs/); without Chrome it prints a note and exits 0.
`--print [DIR]` prints each design on the `finished` fixture to DIR/<design>-print.pdf (`--print-to-pdf`) and,
when `pdftotext` is on PATH, checks the text: no rail, bar, ticker or buttons, every section open.
"""
from html import unescape
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


def design_ids(template):
    return re.search(r"const DESIGN_IDS = DESIGNS\.map", template) and re.findall(
        r"\{id:'(\w+)', no:'\d\d'", template)


def shoot_designs(browser, out_dir):
    """Six designs x 1440 and 400 px; the 400 px page sits in a same-origin iframe (headless Chrome clamps windows to ~500 px)."""
    template = TEMPLATE.read_text(encoding="utf-8")
    anchor = "/*STATE-BEGIN*/window.STATE=null;/*STATE-END*/"
    ids = design_ids(template)
    if anchor not in template or len(ids) != 6:
        print("Dashboard template: state anchor or six designs missing", file=sys.stderr)
        return 2
    state = fixture()
    state["finishedAt"] = None
    embedded = "/*STATE-BEGIN*/window.STATE=" + json.dumps(state, ensure_ascii=False).replace("</", "<\\/") + ";/*STATE-END*/"
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dashboard-designs-") as temp:
        for design in ids:
            probe = ("<script>['mission','reqs','tasks','quality','models','gates','feed'].forEach(id => { UI.sec[id] = true; });"
                     "applyDesign(%s); render('ru');</script>" % json.dumps(design))
            child = Path(temp) / ("dashboard-%s.html" % design)
            child.write_text(template.replace(anchor, embedded).replace("</body>", probe + "</body>"), encoding="utf-8")
            for width, height in ((1440, 2600), (400, 3600)):
                page = child
                if width == 400:
                    page = Path(temp) / ("frame-%s.html" % design)
                    page.write_text('<!doctype html><meta charset="utf-8"><body style="margin:0"><iframe src="%s" '
                                    'style="border:0;width:400px;height:%dpx;display:block"></iframe>' % (child.name, height), encoding="utf-8")
                png = out_dir / ("%s-%d.png" % (design, width))
                done = subprocess.run([browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                                       "--allow-file-access-from-files", "--hide-scrollbars", "--virtual-time-budget=2000",
                                       "--window-size=%d,%d" % (max(width, 500), height), "--screenshot=" + str(png), page.as_uri()],
                                      capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
                if done.returncode or not png.is_file() or png.stat().st_size < 1000:
                    print("Screenshot failed: %s %d %s" % (design, width, done.stderr[-500:]), file=sys.stderr)
                    return 1
                print("Design screenshot:", png)
    return 0


def finished_fixture():
    state = fixture()
    state["finishedAt"] = "2026-10-25T10:30:00+00:00"
    for stage in state["stages"]:
        stage.update(status="done", startedAt=stage.get("startedAt", state["startedAt"]), finishedAt=state["finishedAt"])
    state["tickets"][1].update(status="done", finishedAt=state["finishedAt"])
    state["requirements"].update(done=2, inTicket=0)
    state["reqList"][1]["status"] = "done"
    return state


# Lower-case English texts (the PDF is printed in en: pdftotext does not map the Cyrillic of these fonts): chrome that paper must not carry,
# and headings of the sections that open closed (all seven are folded by default).
PRINT_GONE = ("project sections", "control center", "autopilot engine", "skip to main content", "models & tokens", "quality checks", "2/2 tickets 24 tests")
PRINT_OPEN = ("stage route", "requirements", "tickets", "checks and tests", "spend and models", "gates", "event feed")


def print_text(pdf):
    """Text of a PDF through pdftotext, or None when the tool is absent (the check is then 'не проверено')."""
    tool = shutil.which("pdftotext")
    if not tool:
        return None
    done = subprocess.run([tool, "-layout", str(pdf), "-"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    return done.stdout if done.returncode == 0 else None


def print_designs(browser, out_dir):
    """Six designs on the finished fixture, window.print equivalent: PDF per design; sections stay as the page opens them (closed ones must still print)."""
    template = TEMPLATE.read_text(encoding="utf-8")
    anchor = "/*STATE-BEGIN*/window.STATE=null;/*STATE-END*/"
    ids = design_ids(template)
    if anchor not in template or len(ids) != 6:
        print("Dashboard template: state anchor or six designs missing", file=sys.stderr)
        return 2
    embedded = "/*STATE-BEGIN*/window.STATE=" + json.dumps(finished_fixture(), ensure_ascii=False).replace("</", "<\\/") + ";/*STATE-END*/"
    out_dir.mkdir(parents=True, exist_ok=True)
    bad = 0
    with tempfile.TemporaryDirectory(prefix="dashboard-print-") as temp:
        for design in ids:
            page = Path(temp) / ("dashboard-%s.html" % design)
            page.write_text(template.replace(anchor, embedded).replace("</body>", "<script>applyDesign(%s); render('en');</script></body>" % json.dumps(design)), encoding="utf-8")
            pdf = out_dir / ("%s-print.pdf" % design)
            done = subprocess.run([browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--allow-file-access-from-files",
                                   "--no-pdf-header-footer", "--virtual-time-budget=2000", "--print-to-pdf=" + str(pdf), page.as_uri()],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
            if done.returncode or not pdf.is_file() or pdf.stat().st_size < 1000:
                print("Print failed: %s %s" % (design, done.stderr[-500:]), file=sys.stderr)
                return 1
            text = print_text(pdf)
            if text is None:
                print("Design print: %s (текст PDF не проверен: нет pdftotext)" % pdf)
                continue
            flat = " ".join(text.split()).lower()
            problems = [("есть лишнее", w) for w in PRINT_GONE if w in flat] + [("нет раздела", w) for w in PRINT_OPEN if w not in flat]
            print("Design print:", pdf, "OK" if not problems else ascii(problems))
            bad += bool(problems)
    return 1 if bad else 0


def main():
    browser = chrome_browser()
    if "--print" in sys.argv:
        if not browser:
            print("не проверено: нет Chrome")
            return 0
        rest = [a for a in sys.argv[2:] if not a.startswith("-")]
        return print_designs(browser, Path(rest[0]).resolve() if rest else ROOT / "docs" / "autopilot" / "dashboard-designs")
    if "--designs" in sys.argv:
        if not browser:
            print("не проверено: нет Chrome")
            return 0
        rest = [a for a in sys.argv[2:] if not a.startswith("-")]
        return shoot_designs(browser, Path(rest[0]).resolve() if rest else ROOT / "docs" / "autopilot" / "dashboard-designs")
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
  if (%(sequential)s) window.STATE.sequentialHost = true;
  if (%(planned)s) {
    const ticket = window.STATE.tickets[1];
    delete ticket.routing;
    ticket.plannedRouting = {provider:'openai', model:'gpt-6-luna',
      effort:'low', profile:'cheap', score:12,
      status:'blocked', error:'No verified host capabilities'};
  }
  // Страница одна; секции, где лежат проверяемые блоки, свёрнуты по умолчанию — раскрываем их до отрисовки (innerText не видит свёрнутое).
  ['quality', 'models', 'gates', 'feed'].forEach(id => { UI.sec[id] = true; });
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
  const targetIds = ['mission','tasks','models','quality'];
  const landmark_targets_focusable = targetIds.every(id =>
    document.getElementById(id)?.getAttribute('tabindex') === '-1');
  const mission = document.getElementById('mission');
  mission.focus();
  render(%(lang)s);
  const mission_focus_preserved = document.activeElement?.id === 'mission';
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
    landmark_targets_focusable, mission_focus_preserved,
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
    has_models_title: visible.includes('Расход и модели') ||
                      visible.includes('Spend and models'),
    has_sequential_notice: !!document.getElementById('sequential-host-notice') &&
      visible.includes(%(sequential_warning)s),
    has_planned_route: !!document.getElementById('planned-model-routes') &&
      visible.toLowerCase().includes(%(planned_label)s) &&
      visible.includes('No verified host capabilities'),
    has_blocked_notice: !!document.getElementById('model-routing-blocked-notice') &&
      visible.includes(%(blocked_label)s) && visible.includes(%(blocked_action)s),
    has_runtime_notice: !!document.getElementById('model-routing-runtime-notice') &&
      visible.includes(%(runtime_notice)s),
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
""" % {"lang": json.dumps(lang), "theme": json.dumps(theme),
       "sequential": json.dumps(label == "mobile-dark"),
       "planned": json.dumps(label in ("narrow", "mobile")),
       "planned_label": json.dumps(
           "blocked" if lang == "en" else "заблокировано"),
       "blocked_label": json.dumps(
           "BLOCKED: 1" if lang == "en" else "БЛОКИРОВКА: 1"),
       "blocked_action": json.dumps(
           "Do not spawn subagents" if lang == "en" else
           "До проверки не запускайте субагентов"),
       "sequential_warning": json.dumps(
           "no child agent is created" if lang == "en" else
           "субагент не создаётся"),
       "runtime_notice": json.dumps(
           "A recorded route or saved profile" if lang == "en" else
           "Записанный маршрут или сохранённый профиль")}
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
                          'id="quality"', 'id="reqs"', 'id="gates"', 'id="feed"',
                          'href="#models"', 'class="sec"')
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
                        "nav_kept_focus", "outside_focus_preserved",
                        "landmark_targets_focusable", "mission_focus_preserved"))):
                print("Accessibility/theme/layout assertion failed: " + label +
                      " " + repr(metrics), file=sys.stderr)
                return 1
            if (metrics["has_planned_route"] != (label in ("narrow", "mobile")) or
                    metrics["has_blocked_notice"] != (label in ("narrow", "mobile")) or
                    not metrics["has_runtime_notice"]):
                print("Incorrect blocked-plan/runtime disclosure: " + label + " " +
                      repr(metrics), file=sys.stderr)
                return 1
            if metrics["has_sequential_notice"] != (label == "mobile-dark"):
                print("Incorrect sequential-host warning: " + label + " " +
                      repr(metrics), file=sys.stderr)
                return 1
            required = ("main_landmark", "has_mission", "has_tasks", "has_models", "has_quality",
                        "has_resources", "has_isolation",
                        "has_model_name", "has_models_title")
            if not all(metrics.get(x) for x in required):
                print("Dashboard sections/text missing: " + label + " " +
                      repr(metrics), file=sys.stderr)
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
