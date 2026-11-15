"""Dashboard boards of the page "Now": ticket board, requirement board, ticket side panel, "your answer is needed" (runs the template's JS in node)."""
import copy
import json
import pathlib
import re
import subprocess
import tempfile
import unittest

from test_dashboard_views import HARNESS, NODE, TEMPLATE, _fixtures

# The env() of the shared harness (a vm with a DOM stub); the document stub is patched to remember its listeners (Esc).
HEAD = HARNESS.split("const run = ")[0]
PATCHED = HEAD.replace("addEventListener() {}, createElement", "addEventListener(n, f) { (this.ls = this.ls || {})[n] = f; }, createElement")
if PATCHED == HEAD:
    raise AssertionError("the shared harness changed: the document stub no longer matches")

SCRIPT = PATCHED + r"""
const run = (e, code) => vm.runInContext(code, e.ctx);
const click = (e, ds, attrs) => e.app.listeners.click({target: {closest: () => ({dataset: ds || {}, hasAttribute: n => (attrs || []).includes(n)})}});
const show = (e, tab, lang) => { run(e, "UI.tab = '" + tab + "'; render('" + lang + "')"); return e.app.innerHTML; };
const out = {pages: {}};
(async () => {
  for (const [name, st] of Object.entries(input.fixtures)) for (const tab of ['now', 'req', 'sum']) for (const lang of ['en', 'ru'])
    out.pages[name + '/' + tab + '/' + lang] = show(env(st, {}, false), tab, lang);
  // the mode switch of the requirement board: remembered in localStorage, a denied storage does not break it
  const store = {}, t = env(input.fixtures.boards, store, false);
  out.toggle = {first: show(t, 'req', 'en')};
  click(t, {rbmode: 'tk'});
  out.toggle.tk = t.app.innerHTML; out.toggle.saved = store['autopilot-boardmode'];
  out.toggle.reload = show(env(input.fixtures.boards, store, false), 'req', 'en');
  out.toggle.denied = show(env(input.fixtures.boards, {}, true), 'req', 'en');
  // the side panel: open by click, close by button and by Esc, focus goes back to the card
  const p = env(input.fixtures.boards, {}, false), focused = [];
  const node = (attr, val, name) => ({tagName: 'BUTTON', hasAttribute: n => n === attr, getAttribute: n => n === attr ? val : null, focus() { focused.push(name); }});
  p.app.querySelectorAll = sel => sel === 'button' ? [node('data-pclose', '', 'close'), node('data-card', 'T03', 'card T03'), node('data-card', 'T01', 'card T01')] : [];
  show(p, 'now', 'en');
  out.panel = {before: p.app.innerHTML};
  click(p, {card: 'T03'}); out.panel.open = p.app.innerHTML; out.panel.f1 = focused.slice();
  click(p, {}, ['data-pclose']); out.panel.closed = p.app.innerHTML; out.panel.f2 = focused.slice();
  click(p, {card: 'T01'}); out.panel.done = p.app.innerHTML;
  const key = k => { const f = (p.ctx.document.ls || {}).keydown; if (f) f({key: k}); };
  key('Enter'); out.panel.enter = p.app.innerHTML.includes('class="tpanel"');
  key('Escape'); out.panel.esc = p.app.innerHTML.includes('class="tpanel"'); out.panel.f3 = focused.slice();
  click(p, {card: 'T01'}); run(p, "STATE.tickets = STATE.tickets.filter(x => x.id !== 'T01'); render('en')");
  out.panel.gone = p.app.innerHTML.includes('class="tpanel"');
  // ask: the favicon, the title, the notification button, one notification per question; requestPermission only by click
  const mkLink = () => { const l = {}; return l; };
  const a = env(input.fixtures.ask, {}, false), link = mkLink(), made = [];
  a.ctx.document.querySelector = () => link;
  out.ask = {plain: show(a, 'now', 'en'), icon: link.href, title: a.ctx.document.title};
  let asked = 0;
  class N { constructor(title, o) { made.push([title, o]); }
    static requestPermission() { asked++; N.permission = 'granted'; return Promise.resolve('granted'); } }
  N.permission = 'default';
  a.ctx.Notification = N;
  out.ask.askedAfterRender = asked; show(a, 'now', 'en');
  out.ask.button = a.app.innerHTML; out.ask.askedAfterRender2 = asked; out.ask.madeBefore = made.length;
  click(a, {}, ['data-notify']);
  await new Promise(r => setImmediate(r));
  out.ask.asked = asked; out.ask.made = made.length; out.ask.note = made[0];
  out.ask.after = show(a, 'now', 'en'); out.ask.madeAfterRerender = made.length;
  run(a, "STATE.waiting = Object.assign({}, STATE.waiting, {since: '2026-11-03T08:20:00Z'}); render('en')");
  out.ask.madeNewQuestion = made.length;
  N.permission = 'denied'; show(env(input.fixtures.ask, {}, false), 'now', 'en');
  const d = env(input.fixtures.ask, {}, false); d.ctx.Notification = N; out.ask.denied = show(d, 'now', 'en');
  const r = env(input.fixtures.running, {}, false), rl = mkLink(); r.ctx.document.querySelector = () => rl;
  r.ctx.Notification = N; N.permission = 'granted'; show(r, 'now', 'en');
  out.dur = run(r, 'fmtDur(98)');
  out.ask.runIcon = rl.href; out.ask.runMade = made.length; out.ask.runTitle = r.ctx.document.title;
  console.log(JSON.stringify(out));
})().catch(err => { console.error(err && err.stack || err); process.exit(1); });
"""


def _boards():
    t = lambda m: "2026-11-03T08:%02d:00Z" % m
    st = copy.deepcopy(_fixtures()["running"])
    route = {"provider": "anthropic", "model": "sonnet", "effort": "high", "score": 62,
             "reason": "score=62; profile=strong; high-risk=True"}
    tk = lambda i, status, **kw: dict({"id": "T%02d" % i, "title": "Ticket %d" % i, "status": status, "wave": 1, "blockedBy": [],
                                       "startedAt": t(7 + i), "retries": 0, "repairs": 0, "requirements": []}, **kw)
    st["tickets"] = [
        tk(1, "done", title="Do <i>first</i>", finishedAt=t(12), requirements=["R06"], routing=route, commit="abc1234def56",
           tests={"passed": 6, "failed": 0}, zone=["src/a.py", "tests/test_a.py"]),
        tk(2, "in-progress", requirements=["R03"], retries=1, routing=dict(route, model="haiku", effort="low")),
        tk(3, "review", requirements=["R04"], repairs=1, review="да — check the edges", repairFindings=["x.py:1 - naming"], routing=route),
        tk(4, "repair", requirements=["R05"], repairs=2, repairFindings=["a.py:3 - old", "b.py:9 - last <b>x</b>"]),
        tk(5, "failed", title="Fail <b>x</b>", requirements=["R10"], concerns=["db.py:9 - cannot connect"]),
        tk(6, "pending", requirements=["R02"], blockedBy=["T02"], startedAt=None),
        tk(7, "pending", requirements=["R01"], startedAt=None)]
    st["reqList"] = [{"id": "R%02d" % i, "text": "Requirement %d <u>x</u>" % i, "status": s} for i, s in enumerate(
        ["open", "in-spec", "in-ticket", "in-ticket", "in-ticket", "in-ticket", "done", "placeholder", "deferred", "dropped", "in-ticket"])]
    st["log"] = [{"k": "ticket", "act": a, "ids": ["T03"], "t": t(m), **kw} for a, m, kw in
                 (("start", 9, {}), ("review", 11, {}), ("repair", 13, {"note": "naming"}), ("review", 15, {}))]
    st["log"].append({"k": "ticket", "act": "start", "ids": ["T01"], "t": t(8)})
    return st


def _fix():
    f = _fixtures()
    return {"boards": _boards(), "finished": f["finished"], "empty": f["empty"], "running": f["running"], "ask": f["ask"]}


def col(html, name):
    return re.search(r'<section class="bd-col" data-col="%s".*?</section>' % name, html, re.S).group(0)


def ids(html):
    return re.findall(r'data-card="(\w+)"', html)


def text_of(html):
    return re.sub(r"<[^>]*>", " ", html)


@unittest.skipUnless(NODE, "node is not installed")
class Boards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            harness = pathlib.Path(tmp) / "harness.js"
            harness.write_text(SCRIPT, encoding="utf-8")
            done = subprocess.run([NODE, str(harness), str(TEMPLATE)], capture_output=True, encoding="utf-8", timeout=120,
                                  input=json.dumps({"fixtures": _fix()}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)
        cls.page = lambda self, name, tab="now", lang="en": cls.out["pages"]["%s/%s/%s" % (name, tab, lang)]

    # ---- the ticket board
    def test_columns_hold_tickets_by_state_and_the_failed_one_is_a_red_card_on_top(self):
        for lang, names in (("ru", ["Ждёт", "Пишется", "Проверяется", "Сдан"]), ("en", ["Waiting", "Writing", "In review", "Done"])):
            page = self.page("boards", lang=lang)
            heads = re.findall(r'<section class="bd-col" data-col="\w+" aria-label="[^"]*"><h4>(\D+?) <span>', page)
            self.assertEqual(heads, names)
        page = self.page("boards")
        self.assertEqual([ids(col(page, c)) for c in ("wait", "write", "check", "done")],
                         [["T06", "T07"], ["T02"], ["T03", "T04"], ["T01"]])
        top = page[:page.index('class="bd-cols"')]
        self.assertEqual(ids(top), ["T05"])  # not in any column, above all of them
        self.assertRegex(top, r'class="tcard fail"')
        self.assertIn("db.py:9 - cannot connect", top)  # the reason
        self.assertNotIn("T05", "".join(col(page, c) for c in ("wait", "write", "check", "done")))

    def test_card_shows_number_title_requirements_model_timer_attempts_and_the_why_line(self):
        page = self.page("boards")
        card = lambda tid: re.search(r'<button type="button" class="tcard[^"]*" data-card="%s".*?</button>' % tid, page, re.S).group(0)
        c3 = card("T03")
        for needle in ("T03", "Ticket 3", "R04", "sonnet", "returned ×1", "attempt 2", "Reviewed on its own: check the edges"):
            self.assertIn(needle, c3)
        self.assertIn("returned ×2", card("T04"))  # two returns from the review
        self.assertIn("Review sent back: b.py:9 - last &lt;b&gt;x&lt;/b&gt;", card("T04"))  # the last finding, escaped
        self.assertIn("data-live", card("T02"))  # a running ticket has a ticking timer
        self.assertIn("haiku", card("T02"))
        self.assertIn("attempt 2", card("T02"))  # one retry
        self.assertIn("waits for ticket T02", card("T06"))  # why it waits
        self.assertIn("ready, waits for its turn", card("T07"))
        self.assertNotIn("attempt", card("T07"))  # nothing was tried yet
        self.assertNotIn("returned", card("T02"))
        self.assertIn("Do &lt;i&gt;first&lt;/i&gt;", card("T01"))  # state text goes through esc()
        self.assertIn("6 tests, all green", card("T01"))
        self.assertNotIn("<i>first", page)
        self.assertIn("Fail &lt;b&gt;x&lt;/b&gt;", page)

    def test_cards_are_buttons_with_labels_so_enter_and_space_open_them(self):
        for name in ("boards", "finished"):
            page = self.page(name, "sum" if name == "finished" else "now")
            cards = re.findall(r'<button type="button" class="tcard[^"]*" data-card="\w+"[^>]*>', page)
            self.assertTrue(cards)
            for c in cards:
                self.assertRegex(c, r'aria-label="T\d+\. [^"]+"')
        label = re.search(r'data-card="T03"[^>]*aria-label="([^"]*)"', self.page("boards")).group(1)
        self.assertIn("returned ×1", label)

    def test_empty_board_says_no_tickets_yet(self):
        self.assertIn("no tickets yet", self.page("empty"))
        self.assertIn("тасков ещё нет", self.page("empty", lang="ru"))
        self.assertNotIn("bd-col", self.page("empty"))

    def test_finished_build_has_the_board_in_summary_with_the_gantt_and_every_card_done(self):
        page = self.page("finished", "sum")
        self.assertIn('class="gx"', page)
        self.assertLess(page.index('class="gx"'), page.index('class="bd-cols"'))
        self.assertEqual(len(ids(col(page, "done"))), 7)
        for c in ("wait", "write", "check"):
            self.assertEqual(ids(col(page, c)), [])
        self.assertNotIn('class="tcard fail"', page)
        self.assertNotIn("bd-col", self.page("finished", "now"))  # "Now" of a finished build stays the summary
        self.assertNotIn("bd-col", self.page("running", "sum"))  # the board of a running build is on "Now"
        self.assertIn("bd-col", self.page("running", "now"))

    # ---- the requirement board
    def test_requirement_board_columns_strip_and_stages_from_the_matrix(self):
        page = self.page("boards", "req")
        for lang, cols, strip in (("ru", ["Разбирается", "В плане", "Делается", "Проверяется", "Принято"], ["Нужны твои данные", "Отложено", "Снято"]),
                                  ("en", ["Being read", "In the plan", "Being built", "In review", "Accepted"], ["Your data needed", "Deferred", "Dropped"])):
            html = self.page("boards", "req", lang)
            self.assertEqual(re.findall(r'<section class="bd-col" data-rcol="\w+"[^>]*><h4>(\D+?) <span>', html), cols)
            self.assertEqual(re.findall(r'<section class="bd-strip" data-rstrip="\w+"[^>]*><h4>(\D+?) <span>', html), strip)
        reqs = lambda kind, name: re.findall(r'data-req="(\w+)"', re.search(r'<section class="bd-(?:col|strip)" data-%s="%s".*?</section>' % (kind, name), page, re.S).group(0))
        self.assertEqual([reqs("rcol", c) for c in ("read", "plan", "doing", "check", "ok")],
                         [["R00"], ["R01", "R02"], ["R03", "R10"], ["R04", "R05"], ["R06"]])  # hand-checked against the matrix rules
        self.assertEqual([reqs("rstrip", c) for c in ("ph", "def", "drop")], [["R07"], ["R08"], ["R09"]])
        self.assertIn("Requirement 3 &lt;u&gt;x&lt;/u&gt;", page)
        self.assertEqual(page.count('class="mx-row"'), 11)  # the matrix is still there, below the board

    def test_switch_by_requirements_by_tickets_is_remembered_in_local_storage(self):
        tg = self.out["toggle"]
        self.assertIn('data-rbmode="req" aria-pressed="true"', tg["first"])  # requirements first
        self.assertNotIn('data-card="T03"', tg["first"])
        self.assertIn('data-rbmode="tk" aria-pressed="true"', tg["tk"])
        self.assertEqual(len(ids(tg["tk"])), 7)  # the ticket board
        self.assertNotIn('data-rcol=', tg["tk"])
        self.assertEqual(tg["saved"], "tk")
        self.assertIn('data-rbmode="tk" aria-pressed="true"', tg["reload"])  # after a reload
        self.assertIn('data-rbmode="req" aria-pressed="true"', tg["denied"])  # no storage: the default, no crash
        self.assertEqual(re.findall(r'data-rbmode="\w+"[^>]*>([^<]+)<', self.page("boards", "req", "ru")), ["По требованиям", "По таскам"])

    # ---- the side panel
    def test_click_opens_the_panel_with_what_to_do_requirements_zone_model_events_tests_commit_and_review(self):
        html = self.out["panel"]["done"]
        panel = re.search(r'<aside class="tpanel".*?</aside>', html, re.S).group(0)
        self.assertRegex(panel, r'role="dialog"[^>]*aria-label="T01')
        for head in ("What to do", "Requirements", "Zone", "Model and why", "Events", "Tests", "Commit", "Review notes"):
            self.assertIn(">%s<" % head, panel)
        for needle in ("Do &lt;i&gt;first&lt;/i&gt;", "R06", "Requirement 6 &lt;u&gt;x&lt;/u&gt;", "<code>src/a.py</code>", "<code>tests/test_a.py</code>",
                       "Sonnet, reinforced mode: the ticket touches signatures and keys",  # humanRoute, not "score=…"
                       "Ticket T01 started", "6 tests, all green", "abc1234def56"):
            self.assertIn(needle, panel)
        self.assertNotRegex(panel, r"score=|profile=|\bG[1-4]\b")
        self.assertIn("Ticket T03 started", self.out["panel"]["open"])
        # the event strip of a returned ticket: started → review → back for repair → review again
        events = re.search(r'<aside class="tpanel".*?</aside>', self.out["panel"]["open"], re.S).group(0)
        order = [events.index(x) for x in ("Ticket T03 started", "Ticket T03 in review", "Ticket T03 back for repair: naming")]
        self.assertEqual(order, sorted(order))
        for needle in ("check the edges", "x.py:1 - naming"):  # what the review said
            self.assertIn(needle, events)
        for junk in ("undefined", "NaN", "[object"):
            self.assertNotIn(junk, html)

    def test_panel_closes_by_button_and_esc_and_the_focus_goes_back_to_the_card(self):
        p = self.out["panel"]
        self.assertNotIn('class="tpanel"', p["before"])
        self.assertIn('class="tpanel"', p["open"])
        self.assertEqual(p["f1"], ["close"])  # opened: the close button takes the focus
        self.assertNotIn('class="tpanel"', p["closed"])
        self.assertEqual(p["f2"], ["close", "card T03"])  # closed by the button: back to the card
        self.assertTrue(p["enter"])  # any other key leaves it open
        self.assertFalse(p["esc"])
        self.assertEqual(p["f3"][-1], "card T01")  # the card it was opened from
        self.assertFalse(p["gone"])  # a ticket that vanished from the state takes its panel with it
        self.assertRegex(p["open"], r'<button type="button" class="tp-close" data-pclose[^>]*aria-label="Close')

    # ---- "your answer is needed"
    def test_ask_bar_favicon_and_title_exist_without_notifications(self):
        a = self.out["ask"]
        bar = re.search(r'<section class="askbar".*?</section>', a["plain"], re.S).group(0)
        self.assertIn("Approve the spec? &lt;b&gt;x&lt;/b&gt;", bar)
        self.assertIn("data-since=", bar)
        self.assertNotIn("data-notify", bar)  # no Notification in this browser: no button, but the bar stays
        self.assertIn('id="wait"', __import__("urllib.parse", fromlist=["unquote"]).unquote(a["icon"]))  # the tab icon says "waiting"
        self.assertIn("Waiting for you", a["title"])
        self.assertNotIn('id="wait"', __import__("urllib.parse", fromlist=["unquote"]).unquote(self.out["ask"]["runIcon"]))
        self.assertNotIn("Waiting for you", self.out["ask"]["runTitle"])

    def test_notification_asks_only_by_click_and_notifies_once_per_question(self):
        a = self.out["ask"]
        self.assertIn('data-notify', a["button"])
        self.assertIn("Turn on notifications", a["button"])
        self.assertEqual((a["askedAfterRender"], a["askedAfterRender2"], a["madeBefore"]), (0, 0, 0))  # rendering never asks
        self.assertEqual(a["asked"], 1)  # the click asked once
        self.assertEqual(a["made"], 1)  # and granting it notified
        self.assertIn("Approve the spec?", a["note"][1]["body"])
        self.assertEqual(a["madeAfterRerender"], 1)  # the same question: not again
        self.assertNotIn("data-notify", a["after"])  # granted: no button
        self.assertEqual(a["madeNewQuestion"], 2)  # a new question: once more
        self.assertNotIn("data-notify", a["denied"])  # denied: no button, the bar stays
        self.assertIn('class="askbar"', a["denied"])
        self.assertEqual(a["runMade"], 2)  # nothing to answer: no notification

    def test_request_permission_is_called_only_from_the_click_handler(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        calls = [m.start() for m in re.finditer(r"requestPermission", html)]
        self.assertEqual(len(calls), 1)
        start = html.index("document.getElementById('app').addEventListener('click'")
        end = html.index("let savedLang")
        self.assertTrue(start < calls[0] < end)
        self.assertRegex(html[start:end], r"data-notify'\)\) \{[^}]*Notification\.requestPermission")

    # ---- both themes, narrow window
    def test_board_css_uses_palette_variables_and_folds_when_narrow(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        css = html[html.index("/* Доски страницы"):html.index("</style>")]
        self.assertNotRegex(css, r"#[0-9a-fA-F]{3,8}\b")  # no fixed colours: light and dark come from the palette
        for var in ("--bad-soft", "--bad-tx", "--inset", "--card", "--tx"):
            self.assertIn("var(%s)" % var, css)
        self.assertIn("html[data-narrow] :is(.bd-cols", css)
        self.assertIn("min-height:44px", css)

    def test_long_durations_are_hours_not_an_object(self):
        # regression: the route phrases once shared the key "hr" with the hours unit, so 98 minutes printed "1 [object Object] 38 min"
        self.assertEqual(self.out["dur"], "1 h 38 min")

    def test_no_junk_text_in_any_board_page(self):
        for key, page in self.out["pages"].items():
            for junk in ("undefined", "NaN", "[object"):
                self.assertNotIn(junk, text_of(page), key)
            self.assertNotRegex(text_of(page), r"score=|\bG[1-4]\b" if key.startswith("boards") else r"score=")


if __name__ == "__main__":
    unittest.main()
