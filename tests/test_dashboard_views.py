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
VIEW_IDS = ["overview", "timeline", "requirements", "resources", "summary", "classic", "compact", "quality"]
NAMES = {"overview": "Overview", "timeline": "Timeline", "requirements": "Requirements", "resources": "Resources",
         "summary": "Summary", "classic": "Classic", "compact": "Compact", "quality": "Quality"}
# The rail link that stands for each theme (the anchor its main block carries).
HOME = {"overview": "mission", "timeline": "tasks", "requirements": "quality", "resources": "models",
        "summary": "quality", "classic": "mission", "compact": "mission", "quality": "quality"}
NODE = shutil.which("node")

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
function env(state, store, denied, width) {
  const app = {innerHTML: '', listeners: {}, classList: {add() {}, remove() {}},
    addEventListener(n, f) { this.listeners[n] = f; }, contains() { return false; },
    querySelectorAll() { return []; }};
  const doc = {getElementById: id => id === 'app' ? app : null, querySelectorAll: () => [],
    addEventListener() {}, createElement: () => ({remove() {}}), head: {appendChild() {}},
    documentElement: {attrs: {}, setAttribute(n, v) { this.attrs[n] = v; }, removeAttribute() {}}, activeElement: null, title: ''};
  const ls = {
    getItem: k => { if (denied) throw new Error('denied'); return k in store ? store[k] : null; },
    setItem: (k, v) => { if (denied) throw new Error('denied'); store[k] = String(v); },
    removeItem: k => { delete store[k]; }};
  const ctx = {document: doc, localStorage: ls, navigator: {language: 'en'}, location: {protocol: 'file:'},
    matchMedia: () => ({matches: false, addEventListener() {}}), setTimeout() { return 0; },
    clearTimeout() {}, setInterval() { return 0; }, addEventListener() {}, scrollTo() {}, scrollY: 0,
    STATE: state, Intl, Date: FixedDate, Math, JSON, console};
  if (width) ctx.innerWidth = width;
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
      out.renders[key] = {html: e.app.innerHTML, rootView: e.ctx.document.documentElement.attrs['data-view']};
    } catch (err) { out.renders[key] = {error: String(err && err.stack || err)}; }
  }
}
const probe = (store, denied, width) => run(env(input.fixtures.running, store, denied, width), 'storedView()');
out.stored = {
  none: probe({}, false), saved: probe({'autopilot-view': 'timeline'}, false),
  bogus: probe({'autopilot-view': 'bogus'}, false), denied: probe({}, true),
  narrow: probe({}, false, 440), narrowEdge: probe({}, false, 520), justWider: probe({}, false, 521),
  narrowSaved: probe({'autopilot-view': 'timeline'}, false, 440), narrowDenied: probe({}, true, 440),
  legacyFocus: probe({'autopilot-view': 'focus'}, false), legacyFocusNarrow: probe({'autopilot-view': 'focus'}, false, 1400)};
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
const x = env(input.fixtures.notes, {}, false);
out.expanded = run(x, "VIEW = 'timeline'; UI.open['nt:T05'] = true; render('en'); document.getElementById('app').innerHTML");
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
    return {"notes": notes, "empty": empty, "running": running, "finished": done, "nodone": nodone, "old": old, "oldfin": oldfin}


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
        self.assertEqual(len(self.out["renders"]), 7 * len(VIEW_IDS) * 2)
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
        for view in [v for v in VIEW_IDS if v != "classic"]:  # classic is the old layout, unchanged
            for lang, text in (("ru", "ещё нет"), ("en", "none yet")):
                with self.subTest(view=view, lang=lang):
                    self.assertIn(text, self.out["renders"]["empty/%s/%s" % (view, lang)]["html"])

    def test_views_show_the_composition_from_the_spec(self):
        page = lambda view, name="running": self.out["renders"]["%s/%s/en" % (name, view)]["html"]
        for needle in ('class="ring"', 'class="route"', 'class="gx"', "G1", "G4", "Models & resources", "Retries: "):
            with self.subTest(view="overview", needle=needle):
                self.assertIn(needle, page("overview"))
        self.assertIn("Build timeline", page("timeline"))
        self.assertIn('data-more="feed"', page("timeline"))
        self.assertIn('data-filter="all"', page("requirements"))
        self.assertIn('data-more="words"', page("requirements"))
        self.assertIn("<table", page("resources"))
        self.assertIn("Model routing", page("resources"))
        self.assertIn("What the summary has", page("summary", "empty"))
        self.assertIn("Built it", page("summary", "finished"))
        self.assertIn("class=\"spotlight\"", page("classic"))

    def test_overview_shows_every_block_classic_shows_and_no_duplicate_ids(self):
        heads = lambda html: set(re.findall(r'<h3 class="wt">(?:<i>.*?</i>)?(.*?)</h3>', html))
        for name in ("empty", "running", "finished"):
            for lang in ("ru", "en"):
                over = self.out["renders"]["%s/overview/%s" % (name, lang)]["html"]
                classic = self.out["renders"]["%s/classic/%s" % (name, lang)]["html"]
                with self.subTest(fixture=name, lang=lang):
                    self.assertTrue(heads(classic))
                    # the wave list ("Build progress") is not repeated in the overview: the Gantt carries its content
                    self.assertLessEqual(heads(classic) - heads(over), {"Ход сборки" if lang == "ru" else "Build progress"})
                    if 'class="gx-row"' in over:
                        self.assertIn("Волна" if lang == "ru" else "Wave", re.search(r'<div class="gx">.*', over, re.S).group(0))
                    for block in ("mission", "tasks", "models", "quality"):
                        self.assertEqual(over.count(' id="%s"' % block), 1, block)

    def test_overview_shows_pending_tickets_and_their_wave(self):
        for lang, wave in (("en", "Wave 3"), ("ru", "Волна 3")):
            page = self.out["renders"]["running/overview/" + lang]["html"]
            with self.subTest(lang=lang):
                self.assertIn(wave, page)
                for title in ("Ticket 6", "Ticket 7"):  # the two pending tickets of the fixture
                    self.assertIn(title, page)

    def test_overview_does_not_repeat_blocks(self):
        for name in ("empty", "running", "finished"):
            for lang in ("ru", "en"):
                page = self.out["renders"]["%s/overview/%s" % (name, lang)]["html"]
                with self.subTest(fixture=name, lang=lang):
                    self.assertLessEqual(page.count('class="route"'), 1)  # one stage route; no second stage card
                    self.assertNotIn("Requirements summary", page)  # the requirements tile already says it
                    self.assertNotIn("Сводка требований", page)
                    heads = re.findall(r'<h3 class="wt">(.*?)</h3>', page)
                    self.assertEqual(len(heads), len(set(heads)), heads)
                    self.assertNotIn('class="tl-id', page)  # the wave list is gone: the Gantt is the only task list
                    for tid in re.findall(r'class="gx-id">(T\d+)<', page):
                        self.assertEqual(len(re.findall(r'class="gx-id">%s<' % tid, page)), 1, tid)
        fin = self.out["renders"]["finished/overview/en"]["html"]
        self.assertEqual(len(re.findall(r'class="gx-id">T\d+<', fin)), 7)

    def test_overview_names_each_ticket_once_outside_the_models_block(self):
        for name, n in (("running", 7), ("finished", 7), ("nodone", 7), ("old", 7)):
            for lang in ("ru", "en"):
                page = self.out["renders"]["%s/overview/%s" % (name, lang)]["html"]
                lists = page.split(' id="models"')[0]  # the routing block lists the same tickets by model: another question
                with self.subTest(fixture=name, lang=lang):
                    for i in range(1, n + 1):
                        self.assertEqual(lists.count("<b>Ticket %d</b>" % i), 1, i)
                    self.assertEqual(lists.count('class="gx-row"'), n)
                    self.assertNotIn(">Build progress<" if lang == "en" else ">Ход сборки<", page)

    def test_rail_version_is_the_skill_version_from_state(self):
        rail = lambda key: re.search(r'<aside class="cockpit-rail".*?</aside>', self.out["renders"][key]["html"], re.S).group(0)
        for view in VIEW_IDS:
            for lang in ("ru", "en"):
                self.assertIn("9.9", rail("running/%s/%s" % (view, lang)))
                self.assertIn("9.9", rail("finished/%s/%s" % (view, lang)))
                no_version = rail("empty/%s/%s" % (view, lang))
                self.assertNotIn("2.3", no_version)
                self.assertNotIn("/ <", no_version)  # no dangling separator

    def test_rail_highlights_the_theme_own_item_in_every_theme(self):
        for key, res in self.out["renders"].items():
            name, view, lang = key.split("/")
            page = res["html"]
            marked = re.findall(r'<a data-focus-key="nav-[a-z]+" href="#([a-z]+)" aria-current="page">(.*?)</a>', page)
            with self.subTest(key=key):
                self.assertEqual(len(marked), 1, marked)
                self.assertEqual(marked[0][0], HOME[view])
                if lang == "en":
                    self.assertTrue(marked[0][1].endswith(NAMES[view]), marked[0][1])
        timeline = self.out["renders"]["running/timeline/en"]["html"]
        self.assertNotRegex(timeline, r'aria-current="page">[^<]*<span[^>]*>[^<]*</span>Overview')

    def test_new_themes_compose_the_blocks_from_the_spec(self):
        page = lambda view, name="running", lang="en": self.out["renders"]["%s/%s/%s" % (name, view, lang)]["html"]
        focus = page("compact")
        for needle in ('class="ring', "Ticket 2", "Ticket 6", 'class="ev"'):
            with self.subTest(view="compact", needle=needle):
                self.assertIn(needle, focus)
        for tiled in ("<table", 'class="tiles"', "Models & resources"):
            self.assertNotIn(tiled, focus)
        fin = page("quality", "finished")
        for needle in ("G1", "G4", "Blind acceptance", "R03", "Review notes", "Requirement 1", "Leftovers", 'data-filter="all"'):
            with self.subTest(view="quality", needle=needle):
                self.assertIn(needle, fin)
        for lang, text in (("en", "none yet"), ("ru", "ещё нет")):
            self.assertIn(text, page("quality", "empty", lang))
            self.assertIn(text, page("compact", "empty", lang))
        rail = lambda html: re.findall(r'<a data-focus-key="nav-[a-z]+" href="#([a-z]+)"', html)
        self.assertEqual(rail(fin), ["quality"])  # only anchors this theme really has
        self.assertEqual(rail(focus), ["mission", "tasks", "quality"])

    def test_every_theme_has_at_most_one_of_each_anchor(self):
        for key, res in self.out["renders"].items():
            for block in ("mission", "tasks", "models", "quality"):
                with self.subTest(key=key, block=block):
                    self.assertLessEqual(res["html"].count(' id="%s"' % block), 1)

    def test_selected_view_is_stored_unknown_and_denied_storage_give_overview(self):
        stored = self.out["stored"]
        self.assertEqual((stored["none"], stored["saved"], stored["bogus"], stored["denied"]),
                         ("overview", "timeline", "overview", "overview"))

    def test_click_on_view_button_stores_and_rerenders(self):
        click = self.out["click"]
        self.assertEqual((click["first"], click["after"], click["saved"]), ("overview", "summary", "summary"))
        self.assertIn('data-view="summary" aria-pressed="true"', click["html"])
        self.assertEqual(click["unknown"], "summary")
        self.assertEqual(click["reload"], "summary")

    def test_skip_link_and_rail_links_lead_to_existing_blocks_in_every_theme(self):
        for key, res in self.out["renders"].items():
            page = res["html"]
            ids = set(re.findall(r' id="([^"]+)"', page))
            skip = re.search(r'class="skip-link"[^>]*href="#([^"]+)"', page)
            rail = re.findall(r'<a data-focus-key="nav-[a-z]+" href="#([a-z]+)"', page)
            with self.subTest(key=key):
                self.assertIn(skip.group(1), ids)
                self.assertTrue(rail, "rail has no links at all")
                for target in rail:
                    self.assertIn(target, ids)

    def test_overview_has_ring_forecast_route_and_gantt(self):
        page = lambda name, lang="en": self.out["renders"]["%s/overview/%s" % (name, lang)]["html"]
        run = page("running")
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
        gantt = re.search(r'<div class="gx">.*', run, re.S).group(0)
        bars = re.findall(r'<span class="gx-bar gx-(\w+)[^"]*"[^>]*>(.*?)</span>', gantt, re.S)
        self.assertEqual({kind for kind, _ in bars}, {"done", "now", "rev", "fix", "bad", "wait"})
        for kind, text in bars:  # every state has words, not only a colour
            self.assertTrue(re.sub(r"<[^>]*>", "", text).strip(), kind)
        self.assertIn('class="gx-nowline"', run)
        ru = page("running", "ru")
        self.assertIn("требований закрыто", ru)
        self.assertRegex(ru, r"вероятно \d+–\d+ мин")

    def test_forecast_needs_finished_tickets_with_times_and_empty_or_finished_builds_draw(self):
        for name in ("nodone", "empty", "finished"):
            for view in ("overview", "compact"):
                with self.subTest(fixture=name, view=view):
                    self.assertNotIn("≈", self.out["renders"]["%s/%s/en" % (name, view)]["html"])
        empty = self.out["renders"]["empty/overview/en"]["html"]
        self.assertNotIn('class="gx"', empty)  # no tickets, no chart
        self.assertIn('class="ring"', empty)
        self.assertIn("no requirements yet", empty)
        fin = self.out["renders"]["finished/overview/en"]["html"]
        self.assertIn("3", re.search(r'<div class="ring"[^>]*aria-label="([^"]*)"', fin).group(1))
        self.assertNotIn("gx-bar gx-wait", fin)

    def test_compact_is_one_column_with_the_blocks_from_the_spec(self):
        page = lambda name, lang="en": self.out["renders"]["%s/compact/%s" % (name, lang)]["html"]
        run = page("running")
        for needle in ('class="ring', "≈", 'class="ctile"', "Tests", "Work time", "Tokens", 'class="cstrip"',
                       'class="gx mini"', "API_KEY", "G1", 'class="gchip', 'class="ev"', "Stage 6 of 8"):
            with self.subTest(needle=needle):
                self.assertIn(needle, run)
        for banned in ('class="cols"', 'class="ov3"', "<table", 'class="tiles"', 'class="hero'):
            self.assertNotIn(banned, run)
        empty = page("empty")
        self.assertNotIn('class="ctile"', empty)  # no data, no tile
        self.assertNotIn('class="gx mini"', empty)
        self.assertIn("Этап 6 из 8", page("running", "ru"))

    def test_root_carries_the_view_so_the_palette_can_skip_classic(self):
        for key, res in self.out["renders"].items():
            self.assertEqual(res["rootView"], key.split("/")[1], key)

    def test_narrow_window_defaults_to_compact_and_saved_choice_wins(self):
        stored = self.out["stored"]
        self.assertEqual((stored["narrow"], stored["narrowEdge"], stored["justWider"]), ("compact", "compact", "overview"))
        self.assertEqual((stored["narrowSaved"], stored["narrowDenied"]), ("timeline", "compact"))
        self.assertEqual((stored["legacyFocus"], stored["legacyFocusNarrow"]), ("compact", "compact"))

    def test_requirements_matrix_shows_each_phrase_by_stage_from_statuses_tickets_and_blind(self):
        page = lambda name, lang="en": self.out["renders"]["%s/requirements/%s" % (name, lang)]["html"]
        run = page("running")
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
        fin = page("finished")
        self.assertEqual(cells(fin, "R03")[6], "bad")  # blind acceptance disagreed on R03
        self.assertEqual(cells(fin, "R00")[6], "done")
        empty = page("empty")
        self.assertNotIn("mx-row", empty)
        self.assertNotIn("mx-head", empty)

    def test_summary_gives_a_verdict_per_requirement_and_a_mismatch_block_without_actions(self):
        page = lambda name, lang="en": self.out["renders"]["%s/summary/%s" % (name, lang)]["html"]
        fin = page("finished")
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
        ru = page("finished", "ru")
        for head in ("Что делать дальше", "Нужно от вас", "Расхождение по R03"):
            self.assertIn(head, ru)
        for name in ("empty", "running"):  # nothing finished: no steps, no mismatch
            for lang in ("ru", "en"):
                html = page(name, lang)
                self.assertNotIn('class="steps"', html)
                self.assertNotIn('class="card w mis"', html)
        self.assertNotIn("vd-row", page("empty"))

    def test_timeline_keeps_the_detailed_gantt_and_overview_the_short_one(self):
        timeline = self.out["renders"]["running/timeline/en"]["html"]
        overview = self.out["renders"]["running/overview/en"]["html"]
        self.assertEqual(timeline.count('class="gx-row"'), 7)  # every ticket
        self.assertIn('class="wave"', timeline)  # the detailed chart tells waves apart, the short one only names them per row
        self.assertNotIn('class="wave"', overview)
        self.assertIn('class="gx-mdl"><span class="mchip"', timeline)
        self.assertIn('class="gx-nowline"', timeline)
        self.assertIn("Wave 3", re.search(r'<div class="gx">.*', timeline, re.S).group(0))  # waves are told apart
        self.assertEqual(timeline.count('class="route"'), 1)
        self.assertIn("Build timeline", self.out["renders"]["empty/timeline/en"]["html"])  # no tickets: an empty card, not a blank

    def test_tickets_without_time_marks_stay_in_timeline_and_compact_without_a_false_empty_caption(self):
        false_caption = {"ru": "Таски появятся после спецификации", "en": "Tickets appear after the spec"}
        for name in ("old", "oldfin"):
            for lang in ("ru", "en"):
                for view in ("timeline", "compact", "overview"):
                    page = self.out["renders"]["%s/%s/%s" % (name, view, lang)]["html"]
                    with self.subTest(fixture=name, view=view, lang=lang):
                        self.assertNotIn(false_caption[lang], page)  # there are 7 tickets
                        rows = page.count('class="gx-row"')
                        self.assertEqual(rows, 7, "every ticket has its row")
                        if view != "overview":
                            for n in range(1, 8):
                                self.assertIn("Ticket %d" % n, page)
                            self.assertIn("нет отметок времени" if lang == "ru" else "no time marks", page)
        # a ticket with marks keeps its bar; one without gets the note instead of a bar
        mixed = self.out["renders"]["running/timeline/en"]["html"]
        self.assertNotIn("no time marks", mixed)
        # no tickets at all: the caption is true
        self.assertIn(false_caption["en"], self.out["renders"]["empty/timeline/en"]["html"])
        self.assertIn(false_caption["en"], self.out["renders"]["empty/compact/en"]["html"])

    def test_resources_table_has_status_model_chip_and_tokens_per_ticket(self):
        run = self.out["renders"]["running/resources/en"]["html"]
        table = re.search(r'<table class="routes">.*?</table>', run, re.S).group(0)
        self.assertIn('class="mchip"', table)
        self.assertIn("pill", table)  # ticket state in words
        self.assertIn("1,200", table)  # T01: 1000 in + 200 out, from usageEvents[].ticket
        self.assertIn("<th>Tokens</th>", table)
        nodata = self.out["renders"]["oldfin/resources/en"]["html"]
        self.assertNotIn("<table", nodata)  # nothing routed, nothing waiting, no usage: no table at all

    def test_timeline_has_hero_five_kpis_right_column_and_words_below_the_detailed_gantt(self):
        page = lambda name, lang="en": self.out["renders"]["%s/timeline/%s" % (name, lang)]["html"]
        run = page("running")
        hero = re.search(r'<section class="card ovh tlh[^"]*".*?</section>', run, re.S).group(0)
        self.assertIn("<h2>", hero)
        self.assertIn("≈", hero)  # the forecast sits in the hero
        self.assertRegex(hero, r"likely \d+–\d+ min")
        self.assertEqual(hero.count('class="route"'), 1)
        tiles = re.findall(r'<section class="card tile w"><span class="tk">(.*?)</span>', run)
        self.assertEqual(tiles, ["Requirements", "Tickets", "Tests", "Tokens", "Working time"])
        self.assertIn('class="tiles t5"', run)
        body = run.split('class="tl2"')[1]
        right = body.split('id="quality"')[1]
        order = [right.index(x) for x in ("Needed from you", "Checks", "All events")]
        self.assertEqual(order, sorted(order))
        self.assertLess(body.index('class="gx"'), body.index('id="quality"'))  # the chart stays in the left column
        self.assertGreater(run.index("Your words"), run.index('data-more="feed"'))  # the words close the page
        self.assertEqual(run.count('class="gx-row"'), 7)
        ru = page("running", "ru")
        for text in ("Понадобится от тебя", "Проверки", "Все события", "Твои слова"):
            self.assertIn(text, ru)
        for name in ("empty", "nodone", "old"):  # no data, no block
            html = page(name)
            with self.subTest(fixture=name):
                self.assertNotIn("≈", html)
        self.assertEqual(len(re.findall(r'<section class="card tile w">', page("old"))), 3)  # requirements, tickets, tests: no tokens, no start
        self.assertNotIn('class="card tile w"', page("empty"))
        self.assertNotIn("Your words", page("empty"))

    def test_compact_in_a_narrow_panel_has_no_models_and_isolation_and_a_short_markup(self):
        for name in ("running", "finished", "old"):
            for lang, words in (("en", ("Models & resources", "Isolation & recovery", "Worktree:")),
                                ("ru", ("Модели и ресурсы", "Изоляция и восстановление", "Рабочая копия:"))):
                page = self.out["renders"]["%s/compact/%s" % (name, lang)]["html"]
                for word in words:
                    with self.subTest(fixture=name, lang=lang, word=word):
                        self.assertNotIn(word, page)
        run = self.out["renders"]["running/compact/en"]["html"]
        # one column, no models, no tables (the task notes sit in both Gantt charts and weigh the same in each)
        self.assertLess(len(run), 0.55 * len(self.out["renders"]["running/overview/en"]["html"]))
        self.assertIn("API_KEY", run)  # the keys the user must give stay
        self.assertNotIn("Decisions made for you", run)  # the long assumptions list goes to Summary and Overview

    def test_summary_hero_has_kpi_cards_without_commits(self):
        page = lambda name, lang="en": self.out["renders"]["%s/summary/%s" % (name, lang)]["html"]
        fin = page("finished")
        cards = re.search(r'<div class="kcards">.*?</div>\s*</section>', fin, re.S).group(0)
        self.assertEqual(re.findall(r'<span class="kk">(.*?)</span>', cards), ["Work time", "Tests", "Tokens"])
        self.assertIn("12", cards)  # tests passed
        self.assertIn("1k", cards)  # 1200 tokens
        for word in ("ommit", "оммит"):
            self.assertNotIn(word, fin + page("finished", "ru"))
        for name in ("old", "oldfin"):  # no start time, no usage events: only the tests card has data
            self.assertEqual(re.findall(r'<span class="kk">(.*?)</span>', page(name)), ["Tests"], name)
        self.assertNotIn('class="kcards"', page("empty"))

    def test_header_says_updated_n_seconds_ago_live_and_only_with_updatedat(self):
        for view in VIEW_IDS:
            for lang, word in (("en", "updated"), ("ru", "обновлено")):
                top = re.search(r'<header class="top">.*?</header>', self.out["renders"]["running/%s/%s" % (view, lang)]["html"], re.S).group(0)
                with self.subTest(view=view, lang=lang):
                    if view == "classic":
                        self.assertNotIn('class="upd"', top)  # the classic header stays as it was
                        continue
                    upd = re.search(r'<span class="upd">(.*?)</span></span>', top, re.S).group(0)
                    self.assertIn(word, upd)
                    self.assertIn('data-ago="2026-11-03T08:20:00Z"', upd)  # the same live mechanism as the footer
                    self.assertNotIn('class="upd"', re.search(r'<header class="top">.*?</header>', self.out["renders"]["empty/%s/%s" % (view, lang)]["html"], re.S).group(0))

    def test_resources_list_waiting_tickets_without_routing(self):
        for lang, none, tree in (("en", "not created", "Worktree"), ("ru", "не создана", "Рабочая копия")):
            page = self.out["renders"]["old/resources/%s" % lang]["html"]
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
        run = self.out["renders"]["running/resources/en"]["html"]
        self.assertNotIn("not created", run)  # tickets that have a worktree or a route keep their own rows

    def test_resources_tokens_say_zero_only_where_zero_is_known(self):
        def cells(page, tid):
            row = re.search(r'<tr><td>%s · .*?</tr>' % tid, page, re.S).group(0)
            return re.findall(r'<td>(.*?)</td>', row, re.S)
        run = self.out["renders"]["running/resources/en"]["html"]
        self.assertIn("1,200", cells(run, "T01")[5])  # events exist: the real sum
        for tid in ("T02", "T03", "T04"):  # no usage event for the ticket: not recorded, not zero
            self.assertEqual(cells(run, tid)[5], "—", tid)
        old = self.out["renders"]["old/resources/en"]["html"]
        for tid in ("T06", "T07"):  # waiting, no route: nothing can have been spent
            self.assertEqual(cells(old, tid)[5], "0", tid)

    @staticmethod
    def _row(page, tid):
        return next(r for r in page.split('class="gx-row"')[1:] if '<span class="gx-id">%s</span>' % tid in r)

    def test_gantt_rows_carry_the_ticket_notes_classic_had_alone(self):
        for view in ("overview", "timeline", "compact"):
            for lang, rev, back, redo in (("en", "Reviewed on its own: ", "Review sent back: ", "1 repair · 1 retry"),
                                          ("ru", "Проверяется отдельно: ", "Ревью вернуло: ", "1 ремонт · 1 повтор")):
                page = self.out["renders"]["notes/%s/%s" % (view, lang)]["html"]
                row = lambda tid: self._row(page, tid)
                with self.subTest(view=view, lang=lang):
                    self.assertIn(rev + "check the edges", row("T03"))  # a ticket in review: the review remark
                    self.assertIn(back + "a.py:3 - last finding", row("T04"))  # in repair: the last of repairFindings
                    self.assertNotIn("first finding", row("T04"))
                    self.assertIn("db.py:9 - cannot connect; long", row("T05"))  # failed: why
                    for tid, cls in (("T03", "rev"), ("T04", "fix"), ("T05", "bad")):
                        self.assertIn('class="tl-note gx-note %s"' % cls, row(tid))
                    self.assertIn(redo, row("T01"))  # counts only where they are not zero
                    self.assertIn(redo.split(" · ")[0], row("T04"))  # T04: one repair, no retry
                    self.assertNotIn(redo.split(" · ")[1], row("T04"))

    def test_no_notes_and_no_counts_means_no_note_block(self):
        for name in ("old", "oldfin", "empty"):
            for view in ("overview", "timeline", "compact"):
                for lang in ("ru", "en"):
                    with self.subTest(fixture=name, view=view, lang=lang):
                        self.assertNotIn("gx-note", self.out["renders"]["%s/%s/%s" % (name, view, lang)]["html"])

    def test_note_text_from_state_is_escaped_in_every_view(self):
        for view in VIEW_IDS:
            for lang in ("ru", "en"):
                page = self.out["renders"]["notes/%s/%s" % (view, lang)]["html"]
                with self.subTest(view=view, lang=lang):
                    self.assertNotIn("<img", page)
                    self.assertNotIn("<b>x</b>", page)
        for view in ("overview", "timeline", "compact"):
            page = self.out["renders"]["notes/%s/en" % view]["html"]
            self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)
            self.assertIn("&lt;b&gt;x&lt;/b&gt;", page)

    def test_long_note_is_cut_with_a_show_more_button_and_expands(self):
        for view in ("overview", "timeline", "compact"):
            for lang, more in (("en", "Show more"), ("ru", "Показать ещё")):
                row = self._row(self.out["renders"]["notes/%s/%s" % (view, lang)]["html"], "T05")
                with self.subTest(view=view, lang=lang):
                    self.assertIn('data-more="nt:T05"', row)
                    self.assertIn(more, row)
                    self.assertNotIn("THE-END", row)  # the cut text; nothing hidden in an attribute either
                    self.assertLess(len(row), 1500)
        self.assertNotIn('data-more="nt:T03"', self._row(self.out["renders"]["notes/timeline/en"]["html"], "T03"))  # short notes have no button
        row = self._row(self.out["expanded"], "T05")
        self.assertIn("THE-END", row)
        self.assertIn('data-more="nt:T05"', row)
        self.assertIn("Collapse", row)

    def test_old_project_state_without_new_fields_draws_every_view_in_both_languages(self):
        for name in ("old", "oldfin"):
            for view in VIEW_IDS:
                for lang in ("ru", "en"):
                    res = self.out["renders"]["%s/%s/%s" % (name, view, lang)]
                    with self.subTest(fixture=name, view=view, lang=lang):
                        self.assertNotIn("error", res)
                        for junk in ("undefined", "NaN", "[object"):
                            self.assertNotIn(junk, res["html"])

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
                     "const VIEW_IDS = ['overview','timeline','requirements','resources','summary','classic','compact','quality']",
                     "function storedView()", "let VIEW = storedView()", "const VIEWS = {"):
            self.assertIn(text, self.html)
        for view in VIEW_IDS:
            self.assertRegex(self.html, r"\n  %s: c =>" % view)
        views = self.html.split("const VIEWS = {")[1].split("\nfunction render(")[0]
        self.assertNotRegex(views, r"\bSTATE\b")  # layout only: no state fields, no new data

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

    PALETTE = {  # role: (light, dark) from section 4 of the handoff
        "bg": ("#EDF4F0", "#0B1220"), "card": ("#FFFFFF", "#121B2E"), "line": ("#D6E4DC", "#22304D"),
        "tx": ("#0F2A22", "#E8EEF8"), "tx2": ("#3F5A50", "#C5D2E8"), "mut": ("#5A7268", "#9FB0CC"),
        "done": ("#0A7D5A", "#34D399"), "done-soft": ("#DDF3EA", "#0F3D31"), "done-tx": ("#075E44", "#6EE7B7"),
        "now": ("#E8742A", "#FB923C"), "now-soft": ("#FDEBDD", "#4A2508"), "now-tx": ("#A8470F", "#FDBA74"),
        "rev": ("#1B6FB8", "#60A5FA"), "rev-soft": ("#E1EFFB", "#12294A"), "rev-tx": ("#145A96", "#93C5FD"),
        "warn-bg": ("#FDF1E6", "#2A1A0B"), "warn-bd": ("#F0C9A6", "#6B4A12"), "warn-tx": ("#7A3A0C", "#FCD34D"),
        "bad-tx": ("#B42318", "#F97066"), "bad-soft": ("#FDECEA", "#3A1512")}
    SCOPE = ':root[data-view]:not([data-view="classic"])'
    DARK_ATTR = ':root[data-theme="dark"][data-view]:not([data-view="classic"])'
    DARK_AUTO = ':root:not([data-theme])[data-view]:not([data-view="classic"])'

    def _palette(self, selector):
        body = re.search(re.escape(selector) + r"\{([^}]*)\}", self.html)
        self.assertTrue(body, selector)
        return {k: v.upper() for k, v in re.findall(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})\b", body.group(1))}

    def test_palette_tokens_are_variables_scoped_away_from_classic(self):
        for selector, side in ((self.SCOPE, 0), (self.DARK_ATTR, 1), (self.DARK_AUTO, 1)):
            got = self._palette(selector)
            for name, pair in self.PALETTE.items():
                with self.subTest(selector=selector, token=name):
                    self.assertEqual(got.get(name), pair[side])
        self.assertEqual(self.html.count("#EDF4F0"), 1)  # the light palette lives only in the scoped rule
        for old in ("--bg:#F5F7FB;--card:#fff", "--bg:#0E1729;--card:#19253C"):  # classic keeps its own colours
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

    def test_view_buttons_are_44px_and_say_pressed_without_colour(self):
        heights = [int(h) for rule in re.findall(r"\.views button\{([^}]*)\}", self.html)
                   for h in re.findall(r"(?:min-)?height:(\d+)px", rule)]
        self.assertTrue(heights)
        self.assertGreaterEqual(min(heights), 44)
        # later than the narrow-panel `.tabs button{height:30px}`, so it wins at equal specificity
        self.assertGreater(self.html.rfind(".views button{"), self.html.rfind(".tabs button{height"))
        self.assertIn('.views button[aria-pressed="true"]::before{content:"✓"', self.html)

    def test_focus_is_renamed_to_compact_everywhere_but_the_legacy_storage_value(self):
        self.assertNotRegex(self.html, r"\bfocus:\s*(?:c =>|['\"])")
        self.assertIn('compact:"Компактный"', self.html)
        self.assertIn('compact:"Compact"', self.html)
        self.assertEqual(self.html.count("'focus'"), 1)  # the old saved value is read as compact

    def test_template_has_no_web_addresses_at_all(self):
        self.assertNotRegex(self.html, r"https?://")  # the page was offline before and stays offline

    def test_docs_and_changelog_match_the_current_views(self):
        doc = (ROOT / "docs/autopilot/dashboard-views.md").read_text(encoding="utf-8")
        for view in VIEW_IDS:
            self.assertIn("| `%s` |" % view, doc)
        self.assertNotIn("| `focus` |", doc)
        self.assertNotIn("tasksCard", doc)  # the example of "Add a view" names blocks that exist
        for block in re.findall(r"`c\.(\w+)`", doc):
            self.assertIn(block, self.html, block)
        log = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8").split("## 2.6.0")[0]
        for word in ("compact", "palette", "Requirements", "Summary", "Timeline"):
            self.assertIn(word, log)
        self.assertNotIn("focus and quality", log)

    def test_no_network_requests_and_no_external_fonts(self):
        for bad in ("<link", "@import", "googleapis", "gstatic", "fetch(", "XMLHttpRequest", "@font-face", "WebSocket"):
            self.assertNotIn(bad, self.html)
        self.assertNotRegex(self.html, r"""(?:src|href)=["']https?://""")

    def test_narrow_header_rule_does_not_touch_classic(self):
        narrow = self.html.rsplit("@media(max-width:520px){", 1)[1].split("</style>")[0]
        for line in narrow.splitlines():
            if ".views" in line:
                self.assertIn('html:not([data-view="classic"]) .tools .views', line)

    def test_narrow_compact_trims_header_title_and_chart_and_the_header_has_the_updated_line(self):
        narrow = self.html.rsplit("@media(max-width:520px){", 1)[1].split("</style>")[0]
        for rule in ('html[data-view="compact"] .title .meta', 'html[data-view="compact"] .title:before', ".gx.mini .gx-lane{height:26px}", ".cmp .need{"):
            self.assertIn(rule, narrow)
        self.assertIn('<span class="upd">', self.html)
        self.assertRegex(self.html, r"VIEW !== 'classic' && toMs\(S\.updatedAt\) != null")  # classic header unchanged; no updatedAt, no line
        self.assertEqual(self.html.count("data-ago="), 3)  # feed card, header, footer: one live mechanism for all

    def test_narrow_panel_wraps_theme_buttons_instead_of_hiding_them(self):
        rules = re.findall(r"\.views\{([^}]*)\}", self.html)
        self.assertTrue(rules)
        self.assertTrue(any("flex-wrap:wrap" in r for r in rules))
        for rule in rules:  # a scroll strip hides "Summary"/"Classic" at ~400 px and resets on re-render
            self.assertNotRegex(rule, r"overflow(-x)?:(auto|scroll|hidden)")


if __name__ == "__main__":
    unittest.main()
