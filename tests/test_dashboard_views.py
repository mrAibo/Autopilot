"""Dashboard themes (views): template strings plus, when node exists, a real run of its JS."""
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills/autopilot/phases/dashboard-template.html"
LOGO = ROOT / "assets/autopilot-logo-light.svg"
VIEW_IDS = ["overview", "timeline", "requirements", "resources", "summary", "classic"]
NODE = shutil.which("node")

# Runs the template's own <script> in a vm with a tiny DOM stub; prints JSON.
HARNESS = r"""
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const src = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1])
  .find(s => s.includes('const STAGE_IDS'));
function env(state, store, denied) {
  const app = {innerHTML: '', listeners: {}, classList: {add() {}, remove() {}},
    addEventListener(n, f) { this.listeners[n] = f; }, contains() { return false; },
    querySelectorAll() { return []; }};
  const doc = {getElementById: id => id === 'app' ? app : null, querySelectorAll: () => [],
    addEventListener() {}, createElement: () => ({remove() {}}), head: {appendChild() {}},
    documentElement: {setAttribute() {}, removeAttribute() {}}, activeElement: null, title: ''};
  const ls = {
    getItem: k => { if (denied) throw new Error('denied'); return k in store ? store[k] : null; },
    setItem: (k, v) => { if (denied) throw new Error('denied'); store[k] = String(v); },
    removeItem: k => { delete store[k]; }};
  const ctx = {document: doc, localStorage: ls, navigator: {language: 'en'}, location: {protocol: 'file:'},
    matchMedia: () => ({matches: false, addEventListener() {}}), setTimeout() { return 0; },
    clearTimeout() {}, setInterval() { return 0; }, addEventListener() {}, scrollTo() {}, scrollY: 0,
    STATE: state, Intl, Date, Math, JSON, console};
  ctx.window = ctx;
  vm.createContext(ctx);
  vm.runInContext(src, ctx);
  return {ctx, app, store};
}
const run = (e, code) => vm.runInContext(code, e.ctx);
const out = {renders: {}, stored: {}, click: {}, i18n: {}};
const ids = JSON.parse(JSON.stringify(input.ids));
for (const [name, state] of Object.entries(input.fixtures)) {
  const e = env(state, {}, false);
  for (const id of ids) for (const lang of ['ru', 'en']) {
    const key = name + '/' + id + '/' + lang;
    try {
      run(e, 'VIEW = ' + JSON.stringify(id) + '; render(' + JSON.stringify(lang) + ');');
      out.renders[key] = {html: e.app.innerHTML};
    } catch (err) { out.renders[key] = {error: String(err && err.stack || err)}; }
  }
}
const probe = (store, denied) => run(env(input.fixtures.running, store, denied), 'storedView()');
out.stored = {
  none: probe({}, false), saved: probe({'autopilot-view': 'timeline'}, false),
  bogus: probe({'autopilot-view': 'bogus'}, false), denied: probe({}, true)};
const c = env(input.fixtures.running, {}, false);
const press = view => c.app.listeners.click({target: {closest: () => ({dataset: {view}, hasAttribute: () => false})}});
out.click.first = run(c, 'VIEW');
press('summary');
out.click.after = run(c, 'VIEW');
out.click.saved = c.store['autopilot-view'];
out.click.html = c.app.innerHTML;
press('nonsense');
out.click.unknown = run(c, 'VIEW');
out.click.reload = run(env(input.fixtures.running, c.store, false), 'VIEW');
const L = run(c, 'I18N'), keys = o => Object.keys(o).sort();
out.i18n = {top: [keys(L.ru), keys(L.en)], vw: [keys(L.ru.vw), keys(L.en.vw)],
  views: [keys(L.ru.views), keys(L.en.views)], label: [L.ru.viewLabel, L.en.viewLabel]};
console.log(JSON.stringify(out));
"""


def _fixtures():
    t = lambda m: "2026-11-03T08:%02d:00Z" % m
    empty = {"title": "Empty build", "slug": "empty", "stages": [], "tickets": [], "log": [],
             "requirements": {}, "reqList": [], "usageEvents": []}
    stages = [{"id": s, "status": "done", "startedAt": t(1), "finishedAt": t(5)}
              for s in ("preflight", "manifest", "briefing", "spec", "plan")]
    stages.append({"id": "build", "status": "active", "startedAt": t(6)})
    states = ["done", "in-progress", "review", "repair", "failed", "pending", "pending"]
    tickets = [{"id": "T%02d" % i, "title": "Ticket %d" % i, "status": s, "wave": 1 + i // 3,
                "blockedBy": [] if i < 3 else ["T01"], "startedAt": t(7 + i),
                "finishedAt": t(9 + i) if s == "done" else None, "retries": i % 2, "repairs": 1,
                "routing": {"model": "sonnet", "provider": "anthropic", "effort": "medium", "score": 40, "reason": "x"},
                "worktree": {"status": "clean"}} for i, s in enumerate(states, 1)]
    tickets[-1]["plannedRouting"] = {"model": "haiku", "status": "blocked"}
    del tickets[-1]["routing"]
    log = [{"k": "ticket", "act": "start", "ids": ["T%02d" % (i % 7 + 1)], "t": t(i)} for i in range(25)]
    req_list = [{"id": "R%02d" % i, "text": "Requirement %d" % i, "why": "w",
                 "status": ["done", "in-ticket", "placeholder", "open"][i % 4]} for i in range(10)]
    running = {"title": "Running build", "slug": "run", "tier": "T1", "mode": "full", "depth": "normal",
               "startedAt": t(0), "updatedAt": t(20), "stages": stages, "tickets": tickets, "log": log,
               "requirements": {"total": 10, "done": 3, "inTicket": 3, "placeholder": 2, "dropped": 0},
               "reqList": req_list, "gates": {"G1": {"ok": True, "total": 10}},
               "debt": {"emptyEnv": ["API_KEY"], "placeholders": ["a.py:3 - x"], "assumptions": ["y"]},
               "usageEvents": [{"input": 1000, "output": 200, "cacheRead": 5, "cacheWrite": 1}],
               "budgetTokens": 5000, "skillVersion": "9.9"}
    done = dict(running, title="Finished build", finishedAt=t(40), result="Built it",
                stages=[dict(s, status="done", finishedAt=t(30)) for s in stages + [{"id": "build", "startedAt": t(6)}]],
                tickets=[dict(x, status="done", finishedAt=t(30)) for x in tickets],
                tests={"passed": 12, "failed": 0}, coverage={"found": 1, "fixed": 1, "deferred": 0},
                blind={"matched": 9, "checked": 10, "mismatches": ["R03 - differs"]},
                report=["q1"], concerns=["f.py:1 - note"], additions=["extra"],
                gates={g: {"ok": True} for g in ("G1", "G2", "G3", "G4")})
    return {"empty": empty, "running": running, "finished": done}


@unittest.skipUnless(NODE, "node is not installed")
class TemplateRuns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            harness = pathlib.Path(tmp) / "harness.js"
            harness.write_text(HARNESS, encoding="utf-8")
            done = subprocess.run(
                [NODE, str(harness), str(TEMPLATE)], capture_output=True, encoding="utf-8", timeout=120,
                input=json.dumps({"ids": VIEW_IDS, "fixtures": _fixtures()}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)

    def test_every_view_renders_every_fixture_without_exceptions(self):
        self.assertEqual(len(self.out["renders"]), 3 * len(VIEW_IDS) * 2)
        for key, res in self.out["renders"].items():
            with self.subTest(key=key):
                self.assertNotIn("error", res)
                page = res["html"]
                self.assertGreater(len(page), 2000)
                self.assertEqual(page.count("data-view="), len(VIEW_IDS))
                self.assertIn('data-view="%s" aria-pressed="true"' % key.split("/")[1], page)
                for junk in ("undefined", "NaN", "[object"):
                    self.assertNotIn(junk, page)

    def test_empty_state_says_nothing_yet_instead_of_blank(self):
        for view in VIEW_IDS[:-1]:  # classic is the old layout, unchanged
            for lang, text in (("ru", "ещё нет"), ("en", "none yet")):
                with self.subTest(view=view, lang=lang):
                    self.assertIn(text, self.out["renders"]["empty/%s/%s" % (view, lang)]["html"])

    def test_views_show_the_composition_from_the_spec(self):
        page = lambda view, name="running": self.out["renders"]["%s/%s/en" % (name, view)]["html"]
        for needle in ('class="hero', "Tokens", "Working now", "Worktrees", "Retries and repairs",
                       'class="track"', "G1", "G4", "Requirements summary"):
            with self.subTest(view="overview", needle=needle):
                self.assertIn(needle, page("overview"))
        self.assertIn("Task timeline", page("timeline"))
        self.assertIn('data-more="feed"', page("timeline"))
        self.assertIn('data-filter="all"', page("requirements"))
        self.assertIn('data-more="words"', page("requirements"))
        self.assertIn("<table", page("resources"))
        self.assertIn("Model routing", page("resources"))
        self.assertIn("What the summary has", page("summary", "empty"))
        self.assertIn("Built it", page("summary", "finished"))
        self.assertIn("class=\"spotlight\"", page("classic"))

    def test_selected_view_is_stored_unknown_and_denied_storage_give_overview(self):
        self.assertEqual(self.out["stored"], {"none": "overview", "saved": "timeline",
                                              "bogus": "overview", "denied": "overview"})

    def test_click_on_view_button_stores_and_rerenders(self):
        click = self.out["click"]
        self.assertEqual((click["first"], click["after"], click["saved"]), ("overview", "summary", "summary"))
        self.assertIn('data-view="summary" aria-pressed="true"', click["html"])
        self.assertEqual(click["unknown"], "summary")
        self.assertEqual(click["reload"], "summary")

    def test_both_locales_have_same_keys_including_view_names(self):
        i18n = self.out["i18n"]
        for pair in i18n["top"], i18n["vw"], i18n["views"]:
            self.assertEqual(pair[0], pair[1])
        self.assertEqual(i18n["views"][0], sorted(VIEW_IDS))
        self.assertTrue(all(i18n["label"]))


class TemplateStrings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = TEMPLATE.read_text(encoding="utf-8")

    def test_registry_and_storage_names(self):
        for text in ("const VIEW_KEY = 'autopilot-view'",
                     "const VIEW_IDS = ['overview','timeline','requirements','resources','summary','classic']",
                     "function storedView()", "let VIEW = storedView()", "const VIEWS = {"):
            self.assertIn(text, self.html)
        for view in VIEW_IDS:
            self.assertRegex(self.html, r"\n  %s: c =>" % view)

    def test_view_buttons_click_handler_and_focus(self):
        self.assertRegex(self.html, r"focusAttrs = \[[^\]]*'data-view'")
        self.assertRegex(self.html, r'data-view="\$\{[^}]+\}"[^>]*aria-pressed=')
        self.assertIn("b.dataset.view", self.html)
        self.assertRegex(self.html, r"localStorage\.setItem\(VIEW_KEY, VIEW\)[\s\S]{0,60}render\(CUR\.lang\)")

    def test_locale_blocks_have_view_names_and_group_label(self):
        ru, en = self.html.split("\n  en:{lang:")
        for part in (ru, en):
            self.assertRegex(part, r"views:\{overview:")
            self.assertIn("viewLabel:", part)
        self.assertIn("Обзор", ru)
        self.assertIn("Classic", en)

    def test_inline_logo_matches_the_svg_asset(self):
        svg = LOGO.read_text(encoding="utf-8")
        self.assertIn('<symbol id="ap-mark"', self.html)
        for shape in re.findall(r'<(?:circle|path)[^>]*/>', svg):
            self.assertIn(shape, self.html)
        self.assertIn('rx="28"', self.html)
        self.assertIn("#4F46E5", self.html)
        self.assertIn("#06B6D4", self.html)
        self.assertEqual(self.html.count('class="brandmark"'), 1)
        self.assertEqual(self.html.count('<div class="brand">${BRAND_MARK}'), 2)  # header and bootFail
        self.assertIn('<span class="wordmark"><span>auto</span><b>pilot</b></span>', self.html)
        rail = self.html.split('class="rail-brand"')[1].split("</div>")[0]
        self.assertIn("${BRAND_SVG}", rail)
        self.assertNotIn(">A</span>", rail)
        self.assertNotIn(".png", self.html)

    def test_narrow_panel_lets_switcher_wrap_or_scroll(self):
        self.assertRegex(self.html, r"\.views\{[^}]*overflow-x:auto")


if __name__ == "__main__":
    unittest.main()
