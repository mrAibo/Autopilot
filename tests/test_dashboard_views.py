"""Dashboard page (one page, layout A "Lenta"): template strings plus, when node exists, a real run of its JS."""
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
# The design ids come from the registry in the template itself, in its order.
_TPL = TEMPLATE.read_text(encoding="utf-8").replace("\r\n", "\n")
DESIGN_IDS = re.findall(r"\{id:'(\w+)', no:", re.search(r"const DESIGNS = \[(.*?)\n\];", _TPL, re.S).group(1))
# The sections of the page, top to bottom: each one is a <details class="sec"> and its id is the anchor.
SECTIONS = ["mission", "reqs", "tasks", "quality", "models", "gates", "feed"]
NODE = shutil.which("node")
# Gantt label variants, longest first: full, short, number, icon (px the text needs, padding included); a bar this wide (px).
GX_NEED = [140, 70, 34, 32]
GX_CASES = [[GX_NEED, w] for w in (0, 8, 31, 32, 33, 34, 60, 69, 70, 139, 140, 400)]

# Runs the template's own <script> in a vm with a tiny DOM stub; prints JSON.
HARNESS = r"""
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const src = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1])
  .find(s => s.includes('const STAGE_IDS'));
// The fixtures live on 2026-11-03: freeze "now" ten minutes after the last of them so the chart does not grow with the calendar.
const NOW = Date.parse('2026-11-03T08:30:00Z');
class FixedDate extends Date {
  constructor(...a) { if (a.length) super(...a); else super(NOW); }
  static now() { return NOW; }
}
function env(state, store, denied, width, opts) {
  opts = opts || {};
  // scripts: every <script> the page made to pull state.js (a test calls its onload/onerror); timers: what setTimeout got.
  const scripts = [], timers = [];
  const app = {innerHTML: '', listeners: {}, classList: {add() {}, remove() {}},
    addEventListener(n, f) { this.listeners[n] = f; }, contains() { return false; },
    querySelectorAll() { return []; }};
  const link = {hidden: true, textContent: '', parentNode: {hidden: true}};   // the "server is gone" strip, #link
  const doc = {getElementById: id => id === 'app' ? app : id === 'link' ? link : null, querySelectorAll: () => [],
    addEventListener() {}, createElement: () => { const s = {remove() {}}; scripts.push(s); return s; }, head: {appendChild() {}},
    documentElement: {attrs: {}, setAttribute(n, v) { this.attrs[n] = v; }, removeAttribute() {}}, activeElement: null, title: ''};
  const ls = {
    getItem: k => { if (denied) throw new Error('denied'); return k in store ? store[k] : null; },
    setItem: (k, v) => { if (denied) throw new Error('denied'); store[k] = String(v); },
    removeItem: k => { delete store[k]; }};
  const ctx = {document: doc, localStorage: ls, navigator: {language: 'en'}, location: {protocol: 'file:', search: opts.search},
    matchMedia: q => ({matches: String(q).includes('699') ? !!opts.narrow : false, addEventListener() {}}), setTimeout(f, ms) { timers.push({f, ms, off: false}); return timers.length; },
    clearTimeout(id) { if (timers[id - 1]) timers[id - 1].off = true; }, setInterval() { return 0; }, addEventListener() {}, scrollTo() {}, scrollY: 0,
    STATE: state, Intl, Date: FixedDate, Math, JSON, console};
  if (width) ctx.innerWidth = width;
  ctx.window = ctx;
  vm.createContext(ctx);
  vm.runInContext(src, ctx);
  return {ctx, app, store, scripts, timers, link};
}
const run = (e, code) => vm.runInContext(code, e.ctx);
const out = {renders: {}, legacy: {}, sec: {}, i18n: {}};
const ids = JSON.parse(JSON.stringify(input.ids));
for (const [name, state] of Object.entries(input.fixtures)) {
  const e = env(state, {}, false);
  for (const id of ids) for (const lang of ['ru', 'en']) {
    const key = name + '/' + id + '/' + lang;
    try {
      run(e, 'applyDesign(' + JSON.stringify(id) + '); render(' + JSON.stringify(lang) + ');');
      out.renders[key] = {html: e.app.innerHTML};
    } catch (err) { out.renders[key] = {error: String(err && err.stack || err)}; }
  }
}
// Old settings in storage ("autopilot-view", "autopilot-boardmode") are not read: the page is drawn the same; denied storage too.
const shown = (store, denied) => { const e = env(input.fixtures.running, store, denied); run(e, "render('en')"); return e.app.innerHTML; };
out.legacy = {base: shown({}, false), denied: shown({}, true), runs: [
  {'autopilot-view': 'classic'}, {'autopilot-view': 'focus'}, {'autopilot-view': 'junk<>\u0000'}, {'autopilot-boardmode': 'tk'},
  {'autopilot-view': 'timeline', 'autopilot-boardmode': 'tk'}].map(store => shown(store, false))};
// Sections remember what the user opened or folded across a redraw (the toggle event does not bubble: it is caught on #app).
const tg = env(input.fixtures.running, {}, false);
out.sec.before = tg.app.innerHTML;
const toggle = (id, open, sec) => tg.app.listeners.toggle({target: {classList: {contains: c => sec && c === 'sec'}, id, open}});
toggle('models', true, true); toggle('mission', false, true); toggle('stray', true, false);
run(tg, "render('en')");
out.sec.after = tg.app.innerHTML;
// Gantt bar labels: the pure rule, and the fitter on a fake DOM (no layout in node: the widths are given).
out.gx = {};
try {
  const g = env(input.fixtures.running, {}, false);
  out.gx.pick = input.gxCases.map(([need, avail]) => run(g, `gxPick(${JSON.stringify(need)}, ${avail})`));
  const el = o => { const cl = new Set(o.cls || []);
    return Object.assign({children: [], dataset: {}, parentElement: null, nextElementSibling: null, cl,
      classList: {toggle(n, f) { (f === undefined ? !cl.has(n) : f) ? cl.add(n) : cl.delete(n); }, add: n => cl.add(n),
        remove: n => cl.delete(n), contains: n => cl.has(n)}}, o); };
  const bar = (cls, w, left, widths, d, laneW, tailW) => {
    const lane = el({clientWidth: laneW});
    const b = el({cls: [cls], clientWidth: w, offsetWidth: w, offsetLeft: left, parentElement: lane,
      children: widths.map((x, i) => el({cls: i === d ? ['gl', 'd'] : ['gl'], offsetWidth: x}))});
    if (tailW) b.nextElementSibling = el({cls: ['gx-tail'], offsetLeft: left + w + 4, offsetWidth: tailW});
    return b;
  };
  const cases = {wide: bar('gx-bar', 200, 10, [110, 50, 16, 14], 1, 600), mid: bar('gx-bar', 60, 10, [110, 50, 16, 14], 1, 600),
    tiny: bar('gx-bar', 7, 20, [110, 50, 16, 14], 1, 600), tinyRight: bar('gx-bar', 7, 520, [110, 50, 16, 14], 1, 600),
    tinyTail: bar('gx-bar', 7, 520, [110, 50, 16, 14], 1, 600, 60), tailShort: bar('gx-tail', 40, 100, [48, 30], 0, 600),
    tailLong: bar('gx-tail', 90, 100, [48, 30], 0, 600)};
  const g2 = env(input.fixtures.running, {}, false);
  g2.ctx.getComputedStyle = () => ({paddingLeft: '9px'});
  g2.ctx.root = {querySelectorAll: () => Object.values(cases)};
  run(g2, 'gxFit(root)');
  out.gx.fit = Object.fromEntries(Object.entries(cases).map(([k, b]) => [k,
    {on: b.children.findIndex(x => x.cl.has('on')), out: b.cl.has('out'), side: b.dataset.side || null, fit: b.cl.has('fit')}]));
} catch (err) { out.gx.error = String(err && err.stack || err); }
// The expanded note of a Gantt row, the address of state.js with and without the token, humanRoute.
const x = env(input.fixtures.notes, {}, false);
out.expanded = run(x, "UI.open['nt:T05'] = true; render('en'); document.getElementById('app').innerHTML");
const c = env(input.fixtures.running, {}, false);
out.now = {url: [run(env(input.fixtures.running, {}, false, 0, {search: '?t=abc123'}), 'stateUrl()'),
  run(env(input.fixtures.running, {}, false), 'stateUrl()')]};
const hr = (route, lang) => run(c, `humanRoute(${JSON.stringify(route)}, I18N.${lang})`);
out.hr = {
  risky: hr({model: 'sonnet', reason: 'score=62; profile=strong; high-risk=True'}, 'ru'),
  riskyEn: hr({model: 'sonnet', reason: 'score=62; profile=strong; high-risk=True'}, 'en'),
  plain: hr({model: 'claude-haiku-4-5', reason: 'score=12; profile=cheap; high-risk=False'}, 'ru'),
  premium: hr({model: 'opus', reason: 'score=70; profile=strong; high-risk=True; premium tier'}, 'ru'),
  string: hr('score=30; profile=balanced; high-risk=False', 'en'),
  foreign: hr({model: 'sonnet', reason: 'chosen by hand' + String.fromCharCode(10) + 'second line'}, 'ru'),
  none: hr({}, 'ru')};
const L = run(c, 'I18N'), keys = o => Object.keys(o).sort();
out.i18n = {top: [keys(L.ru), keys(L.en)], vw: [keys(L.ru.vw), keys(L.en.vw)], sec: [keys(L.ru.sec), keys(L.en.sec)]};
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
    for tk, reqs in zip(tickets, (["R00"], ["R01"], ["R05"], ["R02"], ["R03.1"], ["R04"], ["R06"])):
        tk["requirements"] = reqs
        if tk["status"] == "done":
            tk["tests"] = {"passed": 6, "failed": 0}
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
               "usageEvents": [{"ticket": "T01", "input": 1000, "output": 200, "cacheRead": 5, "cacheWrite": 1}],
               "tests": {"passed": 29, "failed": 0}, "budgetTokens": 5000, "skillVersion": "9.9"}
    done = dict(running, title="Finished build", finishedAt=t(40), result="Built it",
                stages=[dict(s, status="done", finishedAt=t(30)) for s in stages + [{"id": "build", "startedAt": t(6)}]],
                tickets=[dict(x, status="done", finishedAt=t(30)) for x in tickets],
                tests={"passed": 12, "failed": 0}, coverage={"found": 1, "fixed": 1, "deferred": 0},
                blind={"matched": 9, "checked": 10, "mismatches": ["R03 - differs"]},
                report=["q1"], concerns=["f.py:1 - note"], additions=["extra"],
                gates={g: {"ok": True} for g in ("G1", "G2", "G3", "G4")})
    # nothing finished yet: no durations to forecast from
    nodone = dict(running, title="Nothing done", tickets=[
        dict(x, status="in-progress" if i == 0 else "pending", finishedAt=None) for i, x in enumerate(tickets)])
    # an old project: none of blind, debt, usageEvents, startedAt, requirement links
    bare = lambda st: {k: v for k, v in st.items() if k not in (
        "blind", "debt", "usageEvents", "startedAt", "budgetTokens", "skillVersion", "coverage")}
    old_tickets = [{k: v for k, v in x.items() if k in ("id", "title", "status", "wave", "blockedBy")} for x in tickets]
    old = dict(bare(running), title="Old build", tickets=old_tickets)
    oldfin = dict(bare(done), title="Old finished build", tickets=[dict(x, status="done") for x in old_tickets])
    # notes: the same build with what the dashboard used to show only in Classic (and a hostile line)
    notes = json.loads(json.dumps(running))
    notes["title"] = "Notes build"
    notes["tickets"][2]["review"] = "да — check the edges <img src=x onerror=alert(1)>"
    notes["tickets"][3]["repairFindings"] = ["first finding", "a.py:3 - last finding <b>x</b>"]
    notes["tickets"][4]["concerns"] = ["db.py:9 - cannot connect", "long " * 60 + "THE-END"]
    landed = dict(json.loads(json.dumps(done)), landedWith={"problems": ["G4: <b>hole</b> in R02"], "byUser": "ship it"})
    opus = dict(json.loads(json.dumps(running)), opusApproval={
        "tickets": ["03"], "roles": ["repair"], "quotes": [{"at": "2026-11-03T08:00:00Z", "quote": "ok, opus for 03"}], "sig": None})
    # the page "Now": waiting for an answer; a stage sent back (two segments each); six plan-changed resets in the feed
    ask = dict(json.loads(json.dumps(running)), waiting={"kind": "spec", "since": t(15), "note": "Approve the spec? <b>x</b>"})
    returned = json.loads(json.dumps(running))
    returned.update(title="Returned stage", finishedAt=t(20), startedAt=t(0), updatedAt=t(20), result="ok")
    returned["stages"] = [
        {"id": "spec", "status": "done", "startedAt": t(0), "finishedAt": t(15),
         "segments": [{"startedAt": t(0), "finishedAt": t(5)}, {"startedAt": t(10), "finishedAt": t(15)}]},
        {"id": "plan", "status": "done", "startedAt": t(5), "finishedAt": t(20),
         "segments": [{"startedAt": t(5), "finishedAt": t(10)}, {"startedAt": t(15), "finishedAt": t(20)}]}]
    gated = json.loads(json.dumps(running))
    gated["title"] = "Gated build"
    gated["gates"] = {"G1": {"ok": False, "reason": "plan-changed"}, "G2": {"ok": False, "reason": "plan-changed"},
                      "G3": {"ok": True, "total": 10}, "G4": {"ok": False, "reason": "plan-changed"}}
    gated["log"] = [{"k": "gate", "g": g, "ok": False, "reason": "plan-changed", "t": t(10 + i)}
                    for i, g in enumerate(("G1", "G2", "G4", "G1", "G2", "G4"))]
    return {"ask": ask, "returned": returned, "gated": gated, "notes": notes, "empty": empty, "running": running, "finished": done, "nodone": nodone, "old": old, "oldfin": oldfin,
            "landed": landed, "opus": opus}


def forbidden_network(html):
    """Network calls the page must not make: any `fetch` except `fetch('/.ap-act' + location.search,`, plus XHR, sockets, beacons."""
    return re.findall(r"""(?<!\.)\bfetch\b(?!\(\s*'/\.ap-act'\s*\+\s*location\.search\s*,)|\.fetch\b|XMLHttpRequest|WebSocket|EventSource|sendBeacon""", html)


@unittest.skipUnless(NODE, "node is not installed")
class TemplateRuns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            harness = pathlib.Path(tmp) / "harness.js"
            harness.write_text(HARNESS, encoding="utf-8")
            done = subprocess.run(
                [NODE, str(harness), str(TEMPLATE)], capture_output=True, encoding="utf-8", timeout=120,
                input=json.dumps({"ids": DESIGN_IDS, "fixtures": _fixtures(), "gxCases": GX_CASES}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)

    def page(self, name, lang="en", design="aurora"):
        return self.out["renders"]["%s/%s/%s" % (name, design, lang)]["html"]

    def test_every_fixture_renders_in_both_languages_without_exceptions(self):
        self.assertEqual(len(self.out["renders"]), 12 * len(DESIGN_IDS) * 2)
        for key, res in self.out["renders"].items():
            with self.subTest(key=key):
                self.assertNotIn("error", res)
                page = res["html"]
                self.assertGreater(len(page), 2000)
                for gone in ("data-view=", "data-ntab", "data-views-more", 'class="tabs views"'):
                    self.assertNotIn(gone, page)
                for junk in ("undefined", "NaN", "[object"):
                    self.assertNotIn(junk, page)

    def test_page_is_seven_sections_top_to_bottom_in_the_order_of_the_brief(self):
        titles = {"en": ["Stage route", "Requirements", "Tickets", "Checks and tests", "Spend and models", "Gates", "Event feed"],
                  "ru": ["Маршрут этапов", "Требования", "Таски", "Проверки и тесты", "Расход и модели", "Гейты", "Лента событий"]}
        for name in ("empty", "running", "finished", "old"):
            for lang in ("en", "ru"):
                page = self.page(name, lang)
                with self.subTest(fixture=name, lang=lang):
                    self.assertEqual(re.findall(r'<details class="sec" id="(\w+)"', page), SECTIONS)
                    self.assertEqual(re.findall(r'<details class="sec"[^>]*><summary>([^<]*)<', page), titles[lang])
                    self.assertLess(page.index('class="ring"'), page.index('id="mission"'))  # the hero stands above the sections

    def test_sections_fold_with_details_and_the_first_three_start_open(self):
        opened = dict(re.findall(r'<details class="sec" id="(\w+)" tabindex="-1"( open)?>', self.page("running")))
        self.assertEqual([k for k, v in opened.items() if v], ["mission", "reqs", "tasks"])
        self.assertEqual(len(opened), 7)
        self.assertNotIn("role=\"tablist\"", self.page("running"))

    def test_sections_remember_what_the_user_opened_or_folded_across_a_redraw(self):
        before, after = self.out["sec"]["before"], self.out["sec"]["after"]
        state = lambda html: [k for k, v in re.findall(r'<details class="sec" id="(\w+)" tabindex="-1"( open)?>', html) if v]
        self.assertEqual(state(before), ["mission", "reqs", "tasks"])
        self.assertEqual(state(after), ["reqs", "tasks", "models"])  # models opened, mission folded; a stray element changed nothing

    def test_waiting_strip_is_a_pinned_status_only_while_waiting(self):
        ask = self.page("ask")
        bar = re.search(r'<section class="askbar" role="status">.*?</section>', ask, re.S).group(0)
        self.assertIn("Approve the spec? &lt;b&gt;x&lt;/b&gt;", bar)  # the question itself, escaped
        self.assertIn("data-since=", bar)  # how long it has waited
        self.assertLess(ask.index('class="askbar"'), ask.index('class="ring"'))  # above the hero and every section
        self.assertIn("Нужен твой ответ", self.page("ask", "ru"))
        for name in ("running", "finished", "empty", "old", "returned"):
            self.assertNotIn("askbar", self.page(name))

    def test_hero_and_the_four_tiles_come_before_the_sections(self):
        run = self.page("running")
        tiles = re.search(r'<div class="tiles">.*?</div>\s*(?=<details)', run, re.S).group(0)
        self.assertEqual(re.findall(r'<section class="card tile w"><span class="tk">(.*?)</span>', tiles),
                         ["Requirements", "Tickets", "Tests", "Working time"])
        self.assertIn("Built it", self.page("finished"))

    def test_needed_from_you_stands_above_the_first_section_and_leaves_no_empty_frame(self):
        for name in ("running", "ask", "notes", "finished", "landed"):  # keys, stubs and assumptions in the state
            ru = "Нужно от вас" if name in ("finished", "landed") else "Понадобится от тебя"  # the title of a build in progress differs
            for lang, head in (("en", "Needed from you"), ("ru", ru)):
                page = self.page(name, lang)
                with self.subTest(fixture=name, lang=lang):
                    self.assertEqual(page.count('<div class="ask-card">'), 1)  # one block, not repeated inside a section
                    top = page[:page.index('<details class="sec"')]
                    self.assertIn('<div class="ask-card">', top)
                    self.assertIn(head, top)
                    self.assertIn("API_KEY", top)  # the empty variables the user must give
                    self.assertGreater(page.index('class="ask-card"'), page.index('class="ring"'))  # under the hero
        for name in ("empty", "old", "oldfin"):  # no debt in the state: no block, no empty frame
            for lang in ("en", "ru"):
                with self.subTest(fixture=name, lang=lang):
                    self.assertNotIn("ask-card", self.page(name, lang))
                    self.assertNotIn("Needed from you" if lang == "en" else "Понадобится от тебя", self.page(name, lang))

    def test_landed_with_caveats_header_lists_problems_and_plain_finish_keeps_old_header(self):
        for lang, text in (("en", "Landed with caveats"), ("ru", "Сдано с оговорками")):
            with self.subTest(lang=lang):
                html = self.page("landed", lang)
                self.assertIn(text, html)
                self.assertIn("G4: &lt;b&gt;hole&lt;/b&gt; in R02", html)  # escaped
                self.assertNotIn("Landed with caveats", self.page("finished", "en"))
                self.assertNotIn("Сдано с оговорками", self.page("finished", "ru"))

    def test_models_section_shows_opus_line_only_with_approval(self):
        html = self.page("opus")
        self.assertIn("Opus enabled", html)
        self.assertIn("ok, opus for 03", html)
        self.assertIn("measure-run.py", html)
        self.assertNotIn("Opus enabled", self.page("running"))
        self.assertIn("Opus включён", self.page("opus", "ru"))

    def test_empty_state_says_nothing_yet_instead_of_blank(self):
        for lang, text in (("ru", "ещё нет"), ("en", "none yet")):
            with self.subTest(lang=lang):
                self.assertIn(text, self.page("empty", lang))

    def test_page_shows_the_composition_from_the_spec(self):
        run = self.page("running")
        for needle in ('class="ring"', 'class="route"', 'class="gx"', "G1", "G4", 'data-more="feed"', 'data-filter="all"',
                       'data-more="words"', "<table", "Model routing", 'class="bd-cols"', 'data-rcol="doing"', 'class="mx-row"'):
            with self.subTest(needle=needle):
                self.assertIn(needle, run)
        for needle in ("Blind acceptance", "R03", "Review notes", "Requirement 1", "Needed from you"):
            with self.subTest(fixture="finished", needle=needle):
                self.assertIn(needle, self.page("finished"))
        self.assertIn("Built it", self.page("finished"))

    def test_every_section_anchor_is_unique_and_ids_never_repeat(self):
        for key, res in self.out["renders"].items():
            ids = re.findall(r' id="([^"]+)"', res["html"])
            with self.subTest(key=key):
                self.assertEqual(len(ids), len(set(ids)), sorted(i for i in ids if ids.count(i) > 1))
                for block in SECTIONS:
                    self.assertEqual(ids.count(block), 1, block)

    def test_rail_version_is_the_skill_version_from_state(self):
        rail = lambda key: re.search(r'<aside class="cockpit-rail".*?</aside>', self.out["renders"][key]["html"], re.S).group(0)
        for lang in ("ru", "en"):
            self.assertIn("9.9", rail("running/aurora/%s" % lang))
            self.assertIn("9.9", rail("finished/aurora/%s" % lang))
            no_version = rail("empty/aurora/%s" % lang)
            self.assertNotIn("2.3", no_version)
            self.assertNotIn("/ <", no_version)  # no dangling separator

    def test_rail_links_only_to_anchors_the_page_has_and_all_four_are_there(self):
        for key, res in self.out["renders"].items():
            page = res["html"]
            rail = re.findall(r'<a data-focus-key="nav-[a-z]+" href="#([a-z]+)"', page)
            with self.subTest(key=key):
                self.assertEqual(rail, ["mission", "tasks", "models", "quality"])
                self.assertNotIn('aria-current="page"', page)  # one page: no item stands for "the current view"
                for target in rail:
                    self.assertIn(' id="%s"' % target, page)

    def test_skip_link_leads_to_the_content(self):
        for key, res in self.out["renders"].items():
            page = res["html"]
            skip = re.search(r'class="skip-link"[^>]*href="#([^"]+)"', page)
            with self.subTest(key=key):
                self.assertIn(' id="%s"' % skip.group(1), page)

    def test_old_settings_in_storage_are_ignored_and_never_raise(self):
        legacy = self.out["legacy"]
        for store, html in zip(("classic", "focus", "junk", "boardmode", "timeline+boardmode"), legacy["runs"]):
            with self.subTest(store=store):
                self.assertEqual(html, legacy["base"])  # drawn exactly the same
        self.assertEqual(legacy["denied"], legacy["base"])  # storage that throws: the same page
        self.assertGreater(len(legacy["base"]), 2000)

    def test_both_boards_stand_on_the_page_without_a_mode_switch(self):
        run = self.page("running")
        self.assertIn('data-rcol="read"', run)  # the requirement board
        self.assertIn('data-col="wait"', run)  # the ticket board
        self.assertNotIn("rbmode", run)

    def test_page_shows_pending_tickets_and_their_wave(self):
        for lang, wave in (("en", "Wave 3"), ("ru", "Волна 3")):
            page = self.page("running", lang)
            with self.subTest(lang=lang):
                self.assertIn(wave, page)
                for title in ("Ticket 6", "Ticket 7"):  # the two pending tickets of the fixture
                    self.assertIn(title, page)

    def test_page_has_ring_forecast_route_and_gantt(self):
        run = self.page("running")
        ring = re.search(r'<div class="ring"[^>]*aria-label="([^"]*)"', run)
        self.assertTrue(ring, "no ring")
        for part in ("3", "10", "requirements closed"):
            self.assertIn(part, ring.group(1))
        self.assertIn("≈", run)  # tickets are done with start and finish times: a forecast exists
        self.assertRegex(run, r"likely \d+–\d+ min")
        route = re.search(r'<ol class="route">.*?</ol>', run, re.S).group(0)
        self.assertEqual(route.count('<li class="rs '), 8)
        self.assertIn("4 min", route)  # stage minutes
        self.assertIn("ahead", route)
        self.assertEqual(run.count('class="route"'), 1)  # one stage route, no second stage card
        gantt = re.search(r'<div class="gx">.*', run, re.S).group(0)
        bars = re.findall(r'<span class="gx-bar gx-(\w+)[^"]*"[^>]*>(.*?)</span>', gantt, re.S)
        self.assertEqual({kind for kind, _ in bars}, {"done", "now", "rev", "fix", "bad", "wait"})
        for kind, text in bars:  # every state has words, not only a colour
            self.assertTrue(re.sub(r"<[^>]*>", "", text).strip(), kind)
        self.assertIn('class="gx-nowline"', run)
        self.assertEqual(run.count('class="gx-row"'), 7)  # every ticket, one chart
        self.assertIn('class="wave"', run)  # the chart tells waves apart
        self.assertIn('class="gx-mdl"><span class="mchip"', run)
        ru = self.page("running", "ru")
        self.assertIn("требований закрыто", ru)
        self.assertRegex(ru, r"вероятно \d+–\d+ мин")

    def test_forecast_needs_finished_tickets_with_times_and_empty_or_finished_builds_draw(self):
        for name in ("nodone", "empty", "finished"):
            with self.subTest(fixture=name):
                self.assertNotIn("≈", self.page(name))
        empty = self.page("empty")
        self.assertNotIn('class="gx"', empty)  # no tickets, no chart
        self.assertIn("Build timeline", empty)  # an empty card instead of a blank
        self.assertIn('class="ring"', empty)
        self.assertIn("no requirements yet", empty)
        fin = self.page("finished")
        self.assertIn("3", re.search(r'<div class="ring"[^>]*aria-label="([^"]*)"', fin).group(1))
        self.assertNotIn("gx-bar gx-wait", fin)

    def test_requirements_matrix_shows_each_phrase_by_stage_from_statuses_tickets_and_blind(self):
        run = self.page("running")
        self.assertEqual(run.count('class="mx-row"'), 10)
        self.assertEqual(run.count('class="mx-c '), 70)  # seven stages for every row
        head = re.search(r'<div class="mx-head">.*?</div>', run, re.S).group(0)
        for stage in ("Written", "the spec", "ticket", "Code", "Tests", "Review", "Blind acceptance"):
            self.assertIn(stage, head)

        def cells(html, rid):
            row = re.search(r'<div class="mx-row"><div class="mx-req"><span class="rid">%s</span>.*?(?=<div class="mx-row">|<div class="mx-sum">|<div class="more">)' % rid, html, re.S).group(0)
            found = re.findall(r'<div class="mx-c (\w+)"', row)
            self.assertEqual(len(found), 7, rid)
            return found
        self.assertEqual(cells(run, "R00"), ["done"] * 6 + ["wait"])  # done requirement, done ticket; blind comes at the end
        self.assertEqual(cells(run, "R01"), ["done", "done", "done", "now", "wait", "wait", "wait"])  # ticket in progress
        self.assertEqual(cells(run, "R05")[3:6], ["done", "wait", "now"])  # ticket in review: code is in, review is going
        self.assertEqual(cells(run, "R07"), ["done", "wait", "wait", "wait", "wait", "wait", "wait"])  # still "open"
        self.assertIn("at the end", run)  # acceptance has not happened yet
        for label in re.findall(r'<span class="mx-t">(.*?)</span>', run):  # a state is a word, not only a colour
            self.assertTrue(label.strip())
        total = re.search(r'<div class="mx-sum">.*', run, re.S).group(0)
        self.assertIn("10 / 10", total)  # "how many reached the stage": everyone is written
        self.assertIn('data-filter="all"', run)  # the filters of the word list stay
        fin = self.page("finished")
        self.assertEqual(cells(fin, "R03")[6], "bad")  # blind acceptance disagreed on R03
        self.assertEqual(cells(fin, "R00")[6], "done")
        empty = self.page("empty")
        self.assertNotIn("mx-row", empty)
        self.assertNotIn("mx-head", empty)

    def test_checks_section_gives_a_verdict_per_requirement_and_a_mismatch_block_without_actions(self):
        fin = self.page("finished")
        rows = fin.split('<div class="vd-row">')[1:]
        self.assertEqual(len(rows), 10)
        by_id = {re.search(r'rid">(R\d+)<', r).group(1): r for r in rows}
        self.assertIn("p-bad", by_id["R03"])  # blind acceptance disagrees
        self.assertIn("p-done", by_id["R00"])
        mis = re.search(r'<section class="card w mis">.*?</section>', fin, re.S).group(0)
        self.assertIn("R03", mis)
        self.assertIn("differs", mis)
        self.assertNotIn("<button", mis)  # no action buttons: the dashboard only reads
        for head in ("What to do next", "Needed from you", "Review notes"):
            self.assertIn(head, fin)
        self.assertIn("f.py:1", fin)
        steps = re.search(r'<ol class="steps">.*?</ol>', fin, re.S).group(0)
        self.assertEqual(steps.count("<li><b>"), 4)  # keys, stubs, mismatch, decisions
        for absent in ("finding", "before", "after", "decision"):  # fields state.js does not have: no such blocks
            self.assertNotIn('class="%s' % absent, fin)
        ru = self.page("finished", "ru")
        for head in ("Что делать дальше", "Нужно от вас", "Расхождение по R03"):
            self.assertIn(head, ru)
        for name in ("empty", "running"):  # nothing finished: no steps, no mismatch
            for lang in ("ru", "en"):
                html = self.page(name, lang)
                self.assertNotIn('class="steps"', html)
                self.assertNotIn('class="card w mis"', html)
        self.assertNotIn("vd-row", self.page("empty"))

    def test_tickets_without_time_marks_keep_their_rows_without_a_false_empty_caption(self):
        false_caption = {"ru": "Таски появятся после спецификации", "en": "Tickets appear after the spec"}
        for name in ("old", "oldfin"):
            for lang in ("ru", "en"):
                page = self.page(name, lang)
                with self.subTest(fixture=name, lang=lang):
                    self.assertNotIn(false_caption[lang], page)  # there are 7 tickets
                    self.assertEqual(page.count('class="gx-row"'), 7, "every ticket has its row")
                    for n in range(1, 8):
                        self.assertIn("Ticket %d" % n, page)
                    self.assertIn("нет отметок времени" if lang == "ru" else "no time marks", page)
        self.assertNotIn("no time marks", self.page("running"))  # a ticket with marks keeps its bar
        self.assertIn(false_caption["en"], self.page("empty"))  # no tickets at all: the caption is true

    def test_routes_table_has_status_model_chip_and_tokens_per_ticket(self):
        run = self.page("running")
        table = re.search(r'<table class="routes">.*?</table>', run, re.S).group(0)
        self.assertIn('class="mchip"', table)
        self.assertIn("pill", table)  # ticket state in words
        self.assertIn("1,200", table)  # T01: 1000 in + 200 out, from usageEvents[].ticket
        self.assertIn("<th>Tokens</th>", table)
        self.assertNotIn("<table", self.page("oldfin"))  # nothing routed, nothing waiting, no usage: no table at all

    def test_planned_routes_carry_their_anchor_only_when_there_are_proposals(self):
        self.assertIn('id="planned-model-routes"', self.page("running"))  # T07 has a blocked plan, no route
        self.assertNotIn('id="planned-model-routes"', self.page("oldfin"))

    def test_header_says_updated_n_seconds_ago_live_and_only_with_updatedat(self):
        for lang, word in (("en", "updated"), ("ru", "обновлено")):
            top = re.search(r'<header class="top">.*?</header>', self.page("running", lang), re.S).group(0)
            with self.subTest(lang=lang):
                upd = re.search(r'<span class="upd">(.*?)</span></span>', top, re.S).group(0)
                self.assertIn(word, upd)
                self.assertIn('data-ago="2026-11-03T08:20:00Z"', upd)  # the same live mechanism as the footer
                self.assertNotIn('class="upd"', re.search(r'<header class="top">.*?</header>', self.page("empty", lang), re.S).group(0))

    def test_routes_list_waiting_tickets_without_routing(self):
        for lang, none, tree in (("en", "not created", "Worktree"), ("ru", "не создана", "Рабочая копия")):
            page = self.page("old", lang)
            table = re.search(r'<table class="routes">.*?</table>', page, re.S).group(0)
            rows = re.findall(r'<tr><td>.*?</tr>', table, re.S)
            with self.subTest(lang=lang):
                self.assertEqual(len(rows), 2)  # T06 and T07 are waiting and have no route
                for row, tid in zip(rows, ("T06", "T07")):
                    self.assertIn(tid, row)
                    self.assertIn(none, row)
                    self.assertIn("<td>0</td>", row)  # nothing spent yet
                    self.assertIn("<td></td>", row)  # no data, no "why"
                self.assertIn("<th>%s</th>" % tree, table)
        self.assertNotIn("not created", self.page("running"))  # tickets that have a worktree or a route keep their own rows

    def test_tokens_say_zero_only_where_zero_is_known(self):
        def cells(page, tid):
            row = re.search(r'<tr><td>%s · .*?</tr>' % tid, page, re.S).group(0)
            return re.findall(r'<td>(.*?)</td>', row, re.S)
        run = self.page("running")
        self.assertIn("1,200", cells(run, "T01")[5])  # events exist: the real sum
        for tid in ("T02", "T03", "T04"):  # no usage event for the ticket: not recorded, not zero
            self.assertEqual(cells(run, tid)[5], "—", tid)
        old = self.page("old")
        for tid in ("T06", "T07"):  # waiting, no route: nothing can have been spent
            self.assertEqual(cells(old, tid)[5], "0", tid)

    @staticmethod
    def _row(page, tid):
        return next(r for r in page.split('class="gx-row"')[1:] if '<span class="gx-id">%s</span>' % tid in r)

    def test_gantt_rows_carry_the_ticket_notes(self):
        for lang, rev, back, redo in (("en", "Reviewed on its own: ", "Review sent back: ", "1 repair · 1 retry"),
                                      ("ru", "Проверяется отдельно: ", "Ревью вернуло: ", "1 ремонт · 1 повтор")):
            page = self.page("notes", lang)
            row = lambda tid: self._row(page, tid)
            with self.subTest(lang=lang):
                self.assertIn(rev + "check the edges", row("T03"))  # a ticket in review: the review remark
                self.assertIn(back + "a.py:3 - last finding", row("T04"))  # in repair: the last of repairFindings
                self.assertNotIn("first finding", row("T04"))
                self.assertIn("db.py:9 - cannot connect; long", row("T05"))  # failed: why
                for tid, cls in (("T03", "rev"), ("T04", "fix"), ("T05", "bad")):
                    self.assertIn('class="tl-note gx-note %s"' % cls, row(tid))
                self.assertIn(redo, row("T01"))  # counts only where they are not zero
                self.assertIn(redo.split(" · ")[0], row("T04"))  # T04: one repair, no retry
                self.assertNotIn(redo.split(" · ")[1], row("T04"))

    def test_in_progress_ticket_shows_its_redo_counter_in_the_gantt(self):
        self.assertIn("1 repair", self._row(self.page("running"), "T02"))  # T02 is in progress with one repair

    def test_no_notes_and_no_counts_means_no_note_block(self):
        for name in ("old", "oldfin", "empty"):
            for lang in ("ru", "en"):
                with self.subTest(fixture=name, lang=lang):
                    self.assertNotIn("gx-note", self.page(name, lang))

    def test_note_text_from_state_is_escaped_everywhere(self):
        for lang in ("ru", "en"):
            page = self.page("notes", lang)
            with self.subTest(lang=lang):
                self.assertNotIn("<img", page)
                self.assertNotIn("<b>x</b>", page)
        page = self.page("notes")
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", page)

    def test_long_note_is_cut_with_a_show_more_button_and_expands(self):
        for lang, more in (("en", "Show more"), ("ru", "Показать ещё")):
            row = self._row(self.page("notes", lang), "T05")
            with self.subTest(lang=lang):
                self.assertIn('data-more="nt:T05"', row)
                self.assertIn(more, row)
                self.assertNotIn("THE-END", row)  # the cut text; nothing hidden in an attribute either
                self.assertLess(len(row), 1800)  # the row's bar carries its label variants too
        self.assertNotIn('data-more="nt:T03"', self._row(self.page("notes"), "T03"))  # short notes have no button
        row = self._row(self.out["expanded"], "T05")
        self.assertIn("THE-END", row)
        self.assertIn('data-more="nt:T05"', row)
        self.assertIn("Collapse", row)

    def test_bar_label_rule_picks_the_longest_variant_that_fits_whole(self):
        self.assertNotIn("error", self.out["gx"], self.out["gx"].get("error"))
        for (need, avail), i in zip(GX_CASES, self.out["gx"]["pick"]):
            with self.subTest(width=avail):
                if i < 0:  # nothing fits: the label leaves the bar, it is never cut
                    self.assertTrue(all(n > avail for n in need))
                else:
                    self.assertLessEqual(need[i], avail)  # whole and inside the bar
                    self.assertTrue(all(n > avail for n in need[:i]))  # and the fullest one that does
        self.assertEqual(self.out["gx"]["pick"], [-1, -1, -1, 3, 3, 2, 2, 2, 1, 1, 0, 0])

    def test_bar_fitter_shows_one_variant_or_puts_the_label_beside_the_bar(self):
        fit = self.out["gx"]["fit"]
        self.assertEqual(fit["wide"], {"on": 0, "out": False, "side": None, "fit": True})
        self.assertEqual(fit["mid"], {"on": 2, "out": False, "side": None, "fit": True})  # the number, no unit
        self.assertEqual(fit["tiny"], {"on": 1, "out": True, "side": "r", "fit": True})  # the short label, beside the bar
        self.assertEqual(fit["tinyRight"]["side"], "l")  # no room to the right of a bar at the end of the scale
        self.assertEqual(fit["tinyTail"]["side"], "l")  # the forecast tail takes the right side
        self.assertEqual(fit["tailLong"]["on"], 0)
        self.assertEqual(fit["tailShort"], {"on": -1, "out": False, "side": None, "fit": True})  # no room: no text, the title keeps it

    def test_every_gantt_bar_carries_whole_label_variants_longest_first(self):
        for lang, state, unit in (("en", "Done", "min"), ("ru", "Сдан", "мин")):
            gantt = re.search(r'<div class="gx.*', self.page("running", lang), re.S).group(0)
            bars = re.findall(r'<span class="gx-bar gx-done[^"]*"[^>]*>((?:<span class="gl[^"]*">.*?</span>)+)</span>', gantt, re.S)
            with self.subTest(lang=lang):
                self.assertTrue(bars)
                for bar in bars:
                    texts = [re.sub(r"<[^>]*>", "", x).strip() for x in re.findall(r'<span class="gl[^"]*">(.*?)</span>', bar, re.S)]
                    self.assertEqual(len(texts), 4, texts)
                    self.assertRegex(texts[0], r"^(%s · )?\d+ %s$" % (state.lower(), unit))  # a whole label ...
                    self.assertRegex(texts[-2], r"^\d+$")  # ... down to a bare number
                    self.assertEqual(texts[-1], "")  # and the icon alone
                    self.assertEqual(bar.count(" d\">"), 1)  # exactly one is the label that goes beside the bar

    def test_old_project_state_without_new_fields_draws_the_whole_page_in_both_languages(self):
        for name in ("old", "oldfin"):
            for lang in ("ru", "en"):
                res = self.out["renders"]["%s/aurora/%s" % (name, lang)]
                with self.subTest(fixture=name, lang=lang):
                    self.assertNotIn("error", res)
                    self.assertEqual(re.findall(r'<details class="sec" id="(\w+)"', res["html"]), SECTIONS)
                    for junk in ("undefined", "NaN", "[object"):
                        self.assertNotIn(junk, res["html"])

    def test_both_locales_have_same_keys_including_section_titles(self):
        i18n = self.out["i18n"]
        for pair in i18n["top"], i18n["vw"], i18n["sec"]:
            self.assertEqual(pair[0], pair[1])
        self.assertEqual(i18n["sec"][0], sorted(["mission", "reqs", "tasks", "quality", "models", "gates", "feed"]))
        for gone in ("views", "viewLabel", "viewSearch", "viewNone", "ntabs", "ntabsLabel", "moreViews"):
            self.assertNotIn(gone, i18n["top"][0])


class TemplateStrings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = TEMPLATE.read_text(encoding="utf-8")
        cls.css = cls.html.split("<style>")[1].split("</style>")[0]

    def test_no_views_registry_tabs_or_view_settings_are_left(self):
        for gone in ("VIEWS", "VIEW_IDS", "VIEW_HOME", "VIEW_KEY", "UI.tab", "data-ntab", 'class="tabs views"', "data-views-more",
                     "storedView", "selectView", "data-view", ".ntabs", ".rbmode", "data-rbmode", "RB_KEY"):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, self.html)
        # the old keys are neither read nor written, so a saved value cannot change or break the page
        self.assertNotRegex(self.html, r"(?:get|set|remove)Item\(\s*['\"]autopilot-(?:view|boardmode)")
        self.assertEqual(self.html.count("const page = c =>"), 1)
        self.assertRegex(self.html, r"const pageHtml = page\(")

    def test_page_function_only_glues_blocks_and_never_names_state(self):
        text = self.html.split("const page = c =>")[1].split("\nfunction render(")[0]
        self.assertNotRegex(text, r"\bSTATE\b")  # layout only: no state fields, no new data
        for section in SECTIONS:
            self.assertIn("sec('%s'" % section, text)

    def test_strings_other_files_read_stay_in_the_template(self):
        self.assertEqual(self.html.count("/*STATE-BEGIN*/window.STATE=null;/*STATE-END*/"), 1)
        for needle in ("skip-link", "cockpit-content", "cockpit-rail", "planned-model-routes", "sequential-host-notice",
                       "no child agent is created"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.html)

    def test_focus_survives_a_redraw_for_the_controls_of_the_page(self):
        attrs = re.search(r"focusAttrs = \[([^\]]*)\]", self.html).group(1)
        for name in ("data-focus-key", "data-lang", "data-theme", "data-filter", "data-more", "data-refresh", "data-card", "data-pclose"):
            self.assertIn("'%s'" % name, attrs)
        for gone in ("data-view", "data-ntab", "data-rbmode", "data-vcombo-input"):
            self.assertNotIn(gone, attrs)
        self.assertIn("summary')]", self.html)  # a focused section title is found again after the redraw
        self.assertRegex(self.html, r"addEventListener\('toggle'[\s\S]{0,200}UI\.sec\[d\.id\]")

    def test_page_column_is_centred_to_1100px_and_the_waiting_strip_sticks(self):
        self.assertRegex(self.css, r"\.cockpit-content\{width:100%;max-width:1100px;margin:0 auto\}")
        self.assertRegex(self.css, r"\.askbar\{position:sticky;top:0;")
        self.assertIn('role="status"', self.html.split("const askBar = waiting")[1].split("</section>")[0])

    def test_every_section_title_is_a_44px_target_and_says_open_or_folded_by_a_mark(self):
        rule = re.search(r"\.sec>summary\{([^}]*)\}", self.css).group(1)
        self.assertGreaterEqual(int(re.search(r"min-height:(\d+)px", rule).group(1)), 44)
        self.assertIn('.sec>summary::before{content:"▸"', self.css)
        self.assertIn('.sec[open]>summary::before{content:"▾"', self.css)

    def test_narrow_rule_is_the_last_in_the_css_and_makes_one_column(self):
        marker = "@media(max-width:520px){"
        # the last rule by width; @media print and prefers-reduced-motion may stand after it
        self.assertEqual(max(m.start() for m in re.finditer(r"@media\s*\((?:max|min)-width", self.css)), self.css.rfind(marker))
        narrow = self.css.rsplit(marker, 1)[1]
        self.assertIn("grid-template-columns:minmax(0,1fr)", narrow)
        self.assertIn(".cockpit-content{max-width:none}", narrow)
        self.assertNotIn("data-view", narrow)

    def test_template_carries_the_aurora_design_and_the_scoped_palette(self):
        self.assertIn('<html lang="ru" data-design="aurora">', self.html)
        self.assertNotIn("data-skin", self.html)
        self.assertRegex(self.html, r'html:is\([^)]*\[data-design="aurora"\][^)]*\):not\(\[hidden\]\):not\(\[data-theme="light"\]\)')
        self.assertRegex(self.html, r'html:is\([^)]*\[data-design="aurora"\][^)]*\)\[data-theme="light"\]\[lang\]:not\(\[hidden\]\)')
        for token in ("--aurora-mint", "--aurora-sky", "--aurora-violet", "--aurora-sheen"):
            self.assertIn(token, self.html)

    def test_locale_blocks_have_section_titles(self):
        ru, en = self.html.split("\n  en:{lang:")
        for part in (ru, en):
            self.assertRegex(part, r"sec:\{mission:")
        self.assertIn("Маршрут этапов", ru)
        self.assertIn("Spend and models", en)

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

    PALETTE = {  # role: (light, dark) from section 4 of the handoff
        "bg": ("#EDF4F0", "#0B1220"), "card": ("#FFFFFF", "#121B2E"), "line": ("#D6E4DC", "#22304D"),
        "tx": ("#0F2A22", "#E8EEF8"), "tx2": ("#3F5A50", "#C5D2E8"), "mut": ("#5A7268", "#9FB0CC"),
        "done": ("#0A7D5A", "#34D399"), "done-soft": ("#DDF3EA", "#0F3D31"), "done-tx": ("#075E44", "#6EE7B7"),
        "now": ("#E8742A", "#FB923C"), "now-soft": ("#FDEBDD", "#4A2508"), "now-tx": ("#A8470F", "#FDBA74"),
        "rev": ("#1B6FB8", "#60A5FA"), "rev-soft": ("#E1EFFB", "#12294A"), "rev-tx": ("#145A96", "#93C5FD"),
        "warn-bg": ("#FDF1E6", "#2A1A0B"), "warn-bd": ("#F0C9A6", "#6B4A12"), "warn-tx": ("#7A3A0C", "#FCD34D"),
        "bad-tx": ("#B42318", "#F97066"), "bad-soft": ("#FDECEA", "#3A1512")}
    # `[lang]:not([hidden])` is always true on <html>: it only keeps the specificity the rules had with the old view switch.
    SCOPE = ':root[lang]:not([hidden])'
    DARK_ATTR = ':root[data-theme="dark"][lang]:not([hidden])'
    DARK_AUTO = ':root:not([data-theme])[lang]:not([hidden])'

    def _palette(self, selector):
        body = re.search(re.escape(selector) + r"\{([^}]*)\}", self.html)
        self.assertTrue(body, selector)
        return {k: v.upper() for k, v in re.findall(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})\b", body.group(1))}

    def test_palette_tokens_are_variables_in_the_scoped_rules(self):
        for selector, side in ((self.SCOPE, 0), (self.DARK_ATTR, 1), (self.DARK_AUTO, 1)):
            got = self._palette(selector)
            for name, pair in self.PALETTE.items():
                with self.subTest(selector=selector, token=name):
                    self.assertEqual(got.get(name), pair[side])
        self.assertEqual(self.html.count("#EDF4F0"), 1)  # the light palette lives only in the scoped rule
        for old in ("--bg:#F5F7FB;--card:#fff", "--bg:#0E1729;--card:#19253C"):  # the base layer keeps its own colours as the fallback
            self.assertIn(old, self.html)

    def test_text_contrast_is_at_least_4_5_in_both_themes(self):
        def lum(hex_):
            ch = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            ch = [c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4 for c in ch]
            return .2126 * ch[0] + .7152 * ch[1] + .0722 * ch[2]
        ratio = lambda a, b: (max(lum(a), lum(b)) + .05) / (min(lum(a), lum(b)) + .05)
        pairs = [(t, b) for t in ("tx", "tx2", "mut") for b in ("card", "bg")] + [
            ("done-tx", "done-soft"), ("now-tx", "now-soft"), ("rev-tx", "rev-soft"), ("warn-tx", "warn-bg"),
            ("bad-tx", "bad-soft")]
        for selector in (self.SCOPE, self.DARK_ATTR, self.DARK_AUTO):
            got = self._palette(selector)
            for fg, bg in pairs:
                with self.subTest(selector=selector, fg=fg, bg=bg):
                    self.assertGreaterEqual(ratio(got[fg], got[bg]), 4.5)

    def test_template_has_no_web_addresses_at_all(self):
        self.assertNotRegex(self.html, r"https?://")  # the page was offline before and stays offline

    def test_network_guard_lets_only_the_own_act_post_through(self):
        ok = "p = fetch('/.ap-act' + location.search, {method: 'POST'});"
        self.assertEqual(forbidden_network(ok), [])
        for bad in ("fetch('/other')", "fetch(location.href)", "window.fetch.call(window, '/x')", "fetch('https://x')",
                    "fetch('/.ap-act')", "fetch('/.ap-act2' + location.search, {})", "window.fetch('/.ap-act' + location.search, {})",
                    "const f = fetch; f('/x')", "navigator.sendBeacon('/x')"):
            with self.subTest(bad=bad):
                self.assertTrue(forbidden_network(bad))

    def test_no_network_requests_and_no_external_fonts(self):
        for bad in ("<link", "@import", "googleapis", "gstatic", "@font-face"):
            self.assertNotIn(bad, self.html)
        self.assertEqual(forbidden_network(self.html), [])
        self.assertEqual(self.html.count("fetch('/.ap-act' + location.search,"), 1)  # the one allowed call
        self.assertNotRegex(self.html, r"""(?:src|href)=["']https?://""")

    def test_header_has_one_live_updated_line_and_one_mechanism_for_all_ages(self):
        self.assertIn('<span class="upd">', self.html)
        self.assertRegex(self.html, r"\$\{toMs\(S\.updatedAt\) != null \?")  # no updatedAt, no line
        self.assertEqual(self.html.count("data-ago="), 2)  # header and footer: one live mechanism for both

    def test_bar_labels_are_fitted_after_every_draw_and_on_resize_with_one_rule(self):
        self.assertEqual(self.html.count("function gxFit("), 1)
        self.assertEqual(self.html.count("const gxPick ="), 1)
        self.assertRegex(self.html, r"app\.innerHTML = `\s*<a class=\"skip-link\"[\s\S]*?</main>`;\s*gxFit\(app\);")
        self.assertRegex(self.html, r"addEventListener\('resize'.*gxFit\(")
        self.assertIn(".gx-bar.out{overflow:visible}", self.html)  # the label beside the bar is not clipped by it
        self.assertEqual(len(re.findall(r'class="gl\b', self.html)), 1)  # one place builds the variants for all three charts


if __name__ == "__main__":
    unittest.main()
