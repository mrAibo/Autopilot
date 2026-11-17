"""Доделки после аудита (R05, R01.1): «Сейчас» одной строкой, свёртка колонки «Принято», подсказка без токена."""
import copy
import json
import pathlib
import re
import subprocess
import tempfile
import unittest

from test_dashboard_views import HARNESS, NODE, TEMPLATE, _fixtures

HEAD = HARNESS.split("const run = ")[0]
HEAD = (HEAD.replace("protocol: 'file:'", "protocol: opts.protocol || 'file:'")
        .replace("navigator: {language: 'en'}", "navigator: {language: opts.lang || 'en'}"))
if "opts.protocol" not in HEAD or "opts.lang" not in HEAD:
    raise AssertionError("the shared harness changed: env() no longer matches")

SCRIPT = HEAD + r"""
const run = (e, code) => vm.runInContext(code, e.ctx);
const click = (e, attrs) => e.app.listeners.click({target: {closest: () => ({dataset: {}, hasAttribute: n => (attrs || []).includes(n)})}});
const show = (e, tab, lang, view) => { run(e, "VIEW = '" + (view || 'now') + "'; UI.tab = '" + tab + "'; render('" + lang + "')"); return e.app.innerHTML; };
const out = {pages: {}, boards: {}, hint: {}};
for (const [name, st] of Object.entries(input.fixtures)) for (const tab of ['now', 'req']) for (const lang of ['en', 'ru'])
  out.pages[name + '/' + tab + '/' + lang] = show(env(st, {}, false), tab, lang);
const rr = (reason, lang) => run(env(input.fixtures.running, {}, false), `humanRoute(${JSON.stringify({model: 'sonnet', reason})}, I18N.${lang})`);
out.route = {withWhy: rr('score=62; profile=strong; high-risk=True; class=сложный; risk=высокий; why=запись в общий кэш', 'en'),
  without: rr('score=30; profile=balanced; high-risk=False', 'en'), classOnly: rr('score=30; profile=balanced; high-risk=False; class=обычный; risk=обычный', 'ru')};
out.pages.classic = show(env(input.fixtures.running, {}, false), 'now', 'en', 'classic');
out.pages.overview = show(env(input.fixtures.running, {}, false), 'now', 'en', 'overview');
for (const name of ['many', 'few']) {
  const e = env(input.fixtures[name], {}, false);
  out.boards[name] = {folded: show(e, 'req', 'en')};
  click(e, ['data-rbok']); out.boards[name].open = e.app.innerHTML;
  click(e, ['data-rbok']); out.boards[name].again = e.app.innerHTML;
  out.boards[name].ru = show(env(input.fixtures[name], {}, false), 'req', 'ru');
}
for (const [key, o] of Object.entries({
    noTokenEn: {protocol: 'http:', search: ''}, noTokenRu: {protocol: 'http:', search: '', lang: 'ru'},
    withToken: {protocol: 'http:', search: '?t=abc'}, file: {protocol: 'file:', search: ''}}))
  out.hint[key] = env(null, {}, false, 0, o).app.innerHTML;
// R20: the poll timers still armed (10 s ones), the next round fired by hand, a failed or loaded state.js by hand.
const polls = e => e.timers.filter(t => !t.off && t.ms === 10000).length;
const fire = e => { const t = e.timers.find(t => !t.off && t.ms === 10000); t.off = true; t.f(); };
const answer = (e, i, kind) => e.scripts[i][kind]();
const tk = {};
const bad = env(null, {}, false, 0, {protocol: 'http:', search: '?t=bad'});
tk.boot = {polls: polls(bad), hint: bad.app.innerHTML.includes('tokhint')};
fire(bad); answer(bad, 0, 'onerror');
tk.one = {polls: polls(bad), hint: bad.app.innerHTML.includes('tokhint'), pulls: bad.scripts.length};
fire(bad); answer(bad, 1, 'onerror');
tk.two = {polls: polls(bad), html: bad.app.innerHTML, pulls: bad.scripts.length};
run(bad, 'refreshNow()'); answer(bad, 2, 'onerror');
tk.refreshFailed = {polls: polls(bad), pulls: bad.scripts.length, hints: bad.app.innerHTML.split('tokhint').length - 1};
run(bad, 'refreshNow()'); bad.ctx.STATE = input.fixtures.running; answer(bad, 3, 'onload');
tk.refreshLoaded = {polls: polls(bad), hint: bad.app.innerHTML.includes('tokhint'), html: bad.app.innerHTML};
const none = env(null, {}, false, 0, {protocol: 'http:', search: ''});
tk.noToken = {polls: polls(none), hint: none.app.innerHTML.includes('tokhint')};
const live = env(input.fixtures.running, {}, false, 0, {protocol: 'http:', search: '?t=abc'});
fire(live); answer(live, 0, 'onerror'); fire(live); answer(live, 1, 'onerror');
tk.lost = {polls: polls(live), hint: live.app.innerHTML.includes('tokhint'), misses: run(live, 'misses')};
out.token = tk;
console.log(JSON.stringify(out));
"""


def fixtures():
    f = _fixtures()
    base = copy.deepcopy(f["running"])
    many = copy.deepcopy(base)
    many["reqList"] = [{"id": "R%02d" % i, "text": "Requirement %d" % i, "status": "done" if i < 9 else "in-ticket"} for i in range(13)]
    few = copy.deepcopy(base)
    few["reqList"] = [{"id": "R%02d" % i, "text": "Requirement %d" % i, "status": "done" if i < 6 else "in-ticket"} for i in range(9)]
    landed = copy.deepcopy(f["finished"])
    landed["landedWith"] = {"byUser": "ship it", "problems": ["no full test run"]}
    return {"running": base, "finished": f["finished"], "landed": landed, "many": many, "few": few}


def okcol(html):
    return re.search(r'<section class="bd-col" data-rcol="ok".*?</section>', html, re.S).group(0)


def rcols(html, name):
    return re.search(r'<section class="bd-col" data-rcol="%s".*?</section>' % name, html, re.S).group(0)


def hero(html):
    return re.search(r'<section class="card nowh w.*?</section>', html, re.S).group(0)


@unittest.skipUnless(NODE, "node is not installed")
class CompactDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            script = pathlib.Path(tmp) / "harness.js"
            script.write_text(SCRIPT, encoding="utf-8")
            done = subprocess.run([NODE, str(script), str(TEMPLATE)], capture_output=True, encoding="utf-8", timeout=120,
                                  input=json.dumps({"fixtures": fixtures()}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)

    def page(self, name, tab="now", lang="en"):
        return self.out["pages"]["%s/%s/%s" % (name, tab, lang)]

    # ---- the hero of "Now" is one line
    def test_running_hero_is_one_line_with_a_small_ring_a_titled_heading_time_and_tests(self):
        for lang in ("en", "ru"):
            h = hero(self.page("running", lang=lang))
            self.assertEqual(h.count("<h2"), 1)
            self.assertRegex(h, r'<div class="ring sm"')
            self.assertRegex(h, r'<h2 title="[^"]+">')
            self.assertIn("kv", h)
            self.assertIn("29", h)                      # the tests, next to the title
            self.assertNotIn('class="lead"', h)
            self.assertNotIn("ovh-main", h)
            self.assertNotIn("undefined", h)

    def test_finished_hero_is_one_line_and_a_landing_with_caveats_keeps_its_list(self):
        h = hero(self.page("finished"))
        self.assertRegex(h, r'<div class="ring sm"')
        self.assertIn("Built it", h)
        self.assertNotIn("nowh-note", h)
        landed = hero(self.page("landed"))
        self.assertIn("nowh-note", landed)
        self.assertIn("no full test run", landed)

    def test_the_ring_of_the_hero_is_smaller_than_the_old_one(self):
        css = TEMPLATE.read_text(encoding="utf-8")
        small = int(re.search(r"\.nowh \.ring\.sm\{--rs:(\d+)px", css).group(1))
        old = int(re.search(r"\.ring\.sm\{--rs:(\d+)px", css).group(1))
        self.assertLess(small, old)
        self.assertLessEqual(small, 72)

    def test_model_routes_show_the_planners_phrase(self):
        r = self.out["route"]
        self.assertEqual(r["withWhy"], "Sonnet, reinforced mode: the ticket touches signatures and keys — запись в общий кэш")
        self.assertEqual(r["without"], "Sonnet: an ordinary ticket")
        self.assertEqual(r["classOnly"], "Sonnet: обычный таск")

    def test_other_views_keep_their_heroes(self):
        self.assertNotIn("nowh", self.out["pages"]["classic"])
        self.assertIn("ovh-main", self.out["pages"]["overview"])

    def test_the_logo_stays_in_the_header_and_the_rail(self):
        self.assertGreaterEqual(self.page("running").count("ap-mark"), 2)

    # ---- the "Accepted" column
    def test_accepted_shows_six_cards_and_a_show_all_button(self):
        b = self.out["boards"]["many"]
        col = okcol(b["folded"])
        self.assertEqual(col.count('class="rcard"'), 6)
        self.assertIn("<span>9</span>", col)             # the header still counts all of them
        self.assertRegex(col, r"<button[^>]*data-rbok[^>]*>Show all 9")
        self.assertIn("Показать все 9", okcol(b["ru"]))

    def test_show_all_opens_the_column_and_collapse_folds_it_back(self):
        b = self.out["boards"]["many"]
        opened = okcol(b["open"])
        self.assertEqual(opened.count('class="rcard"'), 9)
        self.assertRegex(opened, r"<button[^>]*data-rbok[^>]*>Collapse")
        self.assertEqual(okcol(b["again"]).count('class="rcard"'), 6)

    def test_six_or_fewer_cards_have_no_button_and_other_columns_are_untouched(self):
        b = self.out["boards"]["few"]
        self.assertNotIn("data-rbok", b["folded"])
        self.assertEqual(okcol(b["folded"]).count('class="rcard"'), 6)
        many = self.out["boards"]["many"]["folded"]
        self.assertNotIn("data-rbok", rcols(many, "doing") + rcols(many, "check") + rcols(many, "read") + rcols(many, "plan"))
        self.assertEqual(many.count("data-rbok"), 1)

    # ---- the page without a token
    def test_http_without_a_token_shows_one_hint_line_in_both_languages(self):
        en, ru = self.out["hint"]["noTokenEn"], self.out["hint"]["noTokenRu"]
        self.assertIn("ap.py url", en)
        self.assertIn("ap.py url", ru)
        self.assertIn("Run data opens at the address with the token", en)
        self.assertIn("токеном", ru)
        for page in (en, ru):
            self.assertEqual(page.count("<p>"), 1)
            self.assertNotIn("undefined", page)
            self.assertIn("ap-mark", page)

    def test_with_a_token_or_from_a_file_the_old_boot_message_stays(self):
        self.assertNotIn("ap.py url", self.out["hint"]["withToken"])
        self.assertNotIn("ap.py url", self.out["hint"]["file"])
        self.assertIn("Dashboard has no state yet", self.out["hint"]["file"])

    # ---- a wrong or missing token (R20.1): one hint, then the page stops asking
    def test_a_wrong_token_shows_the_hint_once_after_two_failed_pulls_and_stops_polling(self):
        t = self.out["token"]
        self.assertEqual(t["boot"], {"polls": 1, "hint": False})        # the boot message and a poll, as before
        self.assertEqual(t["one"], {"polls": 1, "hint": False, "pulls": 1})   # one miss is a half-written file
        self.assertEqual((t["two"]["polls"], t["two"]["pulls"]), (0, 2))
        self.assertEqual(t["two"]["html"].count("tokhint"), 1)
        self.assertIn("ap.py url", t["two"]["html"])

    def test_refresh_resumes_a_stopped_page_and_a_loaded_state_starts_polling_again(self):
        t = self.out["token"]
        self.assertEqual((t["refreshFailed"]["pulls"], t["refreshFailed"]["polls"]), (3, 0))    # asked again, still wrong
        self.assertEqual(t["refreshFailed"]["hints"], 1)
        self.assertEqual(t["refreshLoaded"]["polls"], 1)
        self.assertFalse(t["refreshLoaded"]["hint"])
        self.assertNotEqual(t["refreshLoaded"]["html"], "")

    def test_no_token_at_all_never_polls_and_a_live_page_keeps_polling_through_misses(self):
        t = self.out["token"]
        self.assertEqual(t["noToken"], {"polls": 0, "hint": True})
        self.assertEqual(t["lost"], {"polls": 1, "hint": False, "misses": 2})      # state is loaded: that is "lost", not the hint


class Styles(unittest.TestCase):
    css = TEMPLATE.read_text(encoding="utf-8")

    @staticmethod
    def lum(hexcolor):
        c = [int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
        return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]

    def ratio(self, a, b):
        la, lb = sorted((self.lum(a), self.lum(b)), reverse=True)
        return (la + .05) / (lb + .05)

    def test_new_elements_use_text_colors_with_enough_contrast_on_the_card(self):
        palettes = []
        for body in re.findall(r"\{[^{}]*\}", self.css):
            got = [re.search(r"--%s:\s*(#[0-9A-Fa-f]{6})" % n, body) for n in ("card", "tx", "tx2")]
            if all(got):
                palettes.append(tuple(m.group(1) for m in got))
        self.assertGreaterEqual(len(palettes), 2)
        for card, tx, tx2 in palettes:
            self.assertGreaterEqual(self.ratio(tx, card), 4.5, (card, tx))
            self.assertGreaterEqual(self.ratio(tx2, card), 4.5, (card, tx2))
        block = re.search(r"\.nowh\{.*?\.bd-more \.btn-soft\{[^}]*\}", self.css, re.S).group(0)
        colors = set(re.findall(r"color:(var\(--[\w-]+\))", block))
        self.assertLessEqual(colors, {"var(--tx2)"})      # only the already checked text colour

    def test_the_hero_wraps_on_a_narrow_screen_and_asks_for_no_wide_minimum(self):
        block = re.search(r"\.nowh\{[^}]*\}", self.css).group(0)
        self.assertIn("flex-wrap:wrap", block)
        h2 = re.search(r"\.nowh h2\{[^}]*\}", self.css).group(0)
        self.assertIn("white-space:nowrap", h2)
        self.assertIn("min-width:0", h2)
        widest = max(int(n) for n in re.findall(r"flex:1 1 (\d+)px", h2))
        self.assertLess(widest, 400)


if __name__ == "__main__":
    unittest.main()
