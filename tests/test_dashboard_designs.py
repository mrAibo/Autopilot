"""Dashboard designs: the registry, the combobox in the header, the stored choice, the theme buttons, the rail (runs the template's JS in node)."""
import json
import pathlib
import re
import subprocess
import tempfile
import unittest

from test_dashboard_views import DESIGN_IDS, HARNESS, NODE, SECTIONS, TEMPLATE, _fixtures

# The harness of test_dashboard_views up to its own driver: env(), run(), the DOM stub; the driver below is ours.
PRE = HARNESS.split("const out = {renders")[0]

DRIVER = r"""
const F = input.fixtures.running, out = {};
const key = (e, k) => { let stopped = false;
  e.app.listeners.keydown({target: {closest: s => s === '[data-dcombo]' ? {} : null}, key: k, preventDefault() {}, stopPropagation() { stopped = true; }});
  return stopped; };
const attrOf = (html, name) => (html.match(new RegExp(name + '="([^"]*)"')) || [])[1] || null;
// the registry and the constants
let e = env(F, {}, false);
out.registry = JSON.parse(run(e, 'JSON.stringify(DESIGNS)'));
out.consts = run(e, '[DESIGN_IDS, DESIGN_KEY, DEFAULT_DESIGN]');
// storage: empty, known, unknown, denied
out.stored = [[{}, false], [{'autopilot-design': 'editorial'}, false], [{'autopilot-design': 'nope<>'}, false], [{'autopilot-design': 'bento'}, true]]
  .map(([store, denied]) => run(env(F, store, denied), 'storedDesign()'));
// the first draw already puts data-design (and the scheme's theme) on <html>
out.first = ['terminal', 'blueprint', 'aurora', 'junk'].map(id => { const x = env(F, {'autopilot-design': id}, false);
  return [x.ctx.document.documentElement.attrs['data-design'], x.ctx.document.documentElement.attrs['data-theme'] || null]; });
// selectDesign: stores, sets the attribute, redraws; a denied storage does not break it
e = env(F, {}, false); run(e, "render('en')");
const before = e.app.innerHTML;
run(e, "selectDesign('blueprint')");
out.select = {store: e.store['autopilot-design'], attr: e.ctx.document.documentElement.attrs['data-design'],
  theme: e.ctx.document.documentElement.attrs['data-theme'], html: e.app.innerHTML, before};
e = env(F, {}, true); run(e, "render('en')");
try { run(e, "selectDesign('terminal')"); out.denied = {attr: e.ctx.document.documentElement.attrs['data-design']}; }
catch (err) { out.denied = {error: String(err)}; }
e = env(F, {}, false); run(e, "render('en'); selectDesign('nope')");
out.unknownSelect = {store: e.store['autopilot-design'] || null, attr: e.ctx.document.documentElement.attrs['data-design']};
// search
out.search = Object.fromEntries(['', '  ', 'чертёж', 'Чертёж', 'blueprint', '05', '5', 'mono', 'light', 'aurora', 'АВРОРА', 'report', 'dark', 'zzz'].map(q => [q, run(e, `comboList(${JSON.stringify(q)})`)]));
// keys
e = env(F, {}, false); run(e, "render('ru')");
out.keys = {};
out.keys.closedDown = key(e, 'ArrowDown');
out.keys.openedByDown = run(e, 'UI.combo.open');
const st = () => run(e, 'UI.combo.i');
out.keys.start = st();
key(e, 'ArrowDown'); out.keys.down = st();
key(e, 'ArrowUp'); key(e, 'ArrowUp'); out.keys.upWraps = st();
run(e, "render('ru')");
out.keys.active = attrOf(e.app.innerHTML, 'aria-activedescendant');
out.keys.role = /role="combobox"/.test(e.app.innerHTML);
key(e, 'Escape'); out.keys.escape = [run(e, 'UI.combo.open'), run(e, 'DESIGN')];
run(e, "comboOpen(true); UI.combo.q = 'mono'; UI.combo.i = 0");
key(e, 'Enter');
out.keys.enter = [run(e, 'UI.combo.open'), run(e, 'DESIGN'), e.store['autopilot-design']];
run(e, "comboOpen(true); UI.combo.q = 'zzz'");
run(e, "render('ru')");
out.keys.none = [/dlistbox-none"(?! hidden)/.test(e.app.innerHTML), e.app.innerHTML.includes('ничего не найдено')];
run(e, "render('en')");
out.keys.noneEn = e.app.innerHTML.includes('nothing found');
// the theme buttons and the sections, per design
out.pages = {};
for (const id of input.ids) {
  const x = env(F, {}, false); run(x, `applyDesign(${JSON.stringify(id)}); render('en')`);
  out.pages[id] = {themeButtons: (x.app.innerHTML.match(/<button[^>]*data-theme=/g) || []).length,
    ids: [...x.app.innerHTML.matchAll(/ id="([^"]+)"/g)].map(m => m[1]).filter(v => !v.startsWith('dopt-')),
    theme: x.ctx.document.documentElement.attrs['data-theme'] || null};
}
// the rail: the link of the section nearest to the top gets aria-current="page"
const r = env(F, {}, false);
const mk = (id, top) => ({id, top, getBoundingClientRect() { return {top: this.top}; }});
const link = id => ({href: '#' + id, cur: null, getAttribute(n) { return n === 'href' ? this.href : this.cur; },
  setAttribute(n, v) { this.cur = v; }, removeAttribute() { this.cur = null; }});
const ids = ['mission', 'reqs', 'tasks', 'quality'], links = ['mission', 'tasks', 'quality'].map(link);
const secs = ids.map((id, i) => mk(id, i * 300));
r.app.querySelectorAll = s => s === '.rail-nav a' ? links : s === 'details.sec' ? secs : [];
const cur = () => links.map(l => l.cur);
run(r, 'railSync()'); out.rail0 = cur();
secs.forEach((s, i) => s.top = (i - 2) * 300 + 50); run(r, 'railSync()'); out.rail2 = cur();   // tasks is at 50 px, reqs above it
secs.forEach((s, i) => s.top = (i - 1) * 300 + 100); run(r, 'railSync()'); out.railReqs = cur(); // reqs at 100 px, it has no link: the one above stays
out.pick = [run(r, 'railPick([-500, -200, 30, 400], 120)'), run(r, 'railPick([10, 200], 120)'), run(r, 'railPick([300, 600], 120)')];
// the slots and the status words: the same page text for every design, only the CSS shows a slot
out.dx = {};
for (const name of ['empty', 'running', 'finished', 'gated']) for (const lang of ['en', 'ru']) {
  const x = env(input.fixtures[name], {}, false); run(x, `applyDesign('editorial'); render('${lang}')`);
  out.dx[name + '/' + lang] = x.app.innerHTML;
}
console.log(JSON.stringify(out));
"""

EXPECTED = [  # id, no, accent, scheme, tags: the registry of mockups/dashboard-2026/designs.js plus the schemes of the spec
    ("aurora", "01", "#4df0be", "both", ["dark", "glass"]),
    ("editorial", "02", "#bf3a1e", "light", ["light", "serif"]),
    ("brutal", "03", "#d8ff3e", "light", ["lime", "brutal"]),
    ("terminal", "04", "#70ff9a", "dark", ["dark", "mono"]),
    ("blueprint", "05", "#1849a9", "light", ["light", "technical"]),
    ("bento", "06", "#5a4bdb", "light", ["light", "soft"]),
]


class _Slots:
    def test_empty_build_draws_no_slot_at_all(self):
        for lang in ("en", "ru"):
            html = self.out["dx"]["empty/" + lang]
            for needle in ("dx-stamp", "dx-dim", "dx-ring"):
                self.assertNotIn(needle, html)

    def test_stamp_only_on_a_finished_build_with_the_word_and_the_date(self):
        for name in ("running", "gated"):
            self.assertNotIn("dx-stamp", self.out["dx"][name + "/en"])
        en, ru = self.out["dx"]["finished/en"], self.out["dx"]["finished/ru"]
        self.assertRegex(en, r'class="dx-stamp"[^>]*><b>Done</b>[^<]*<small>[^<]*2026')
        self.assertRegex(ru, r'class="dx-stamp"[^>]*><b>Сдано</b>[^<]*<small>[^<]*2026')

    def test_dimension_lines_carry_the_minutes_of_work_only_when_there_is_time(self):
        for name in ("running", "finished"):
            self.assertRegex(self.out["dx"][name + "/en"], r'class="dx-dim"[^>]*>.*?\d+ min')

    def test_ring_is_the_share_of_done_tickets_with_percent_in_the_centre(self):
        # running: 1 of 7 tickets is done -> 14 %; finished: 7 of 7 -> 100 %
        self.assertRegex(self.out["dx"]["running/en"], r'class="dx-ring"[^>]*aria-label="[^"]*1 of 7[^"]*".*?<b>14<small>%</small>')
        self.assertRegex(self.out["dx"]["finished/en"], r'class="dx-ring".*?<b>100<small>%</small>')

    def test_every_status_element_has_a_word_or_an_icon(self):
        for key, html in self.out["dx"].items():
            for m in re.finditer(r'<(span|p|li)[^>]*class="(?:pill |rs )[^"]*"[^>]*>(.*?)</>', html, re.S):
                with self.subTest(page=key, el=m.group(0)[:60]):
                    inner = m.group(2)
                    self.assertTrue(re.sub(r"<[^>]*>", "", inner).strip() or "<svg" in inner or "<i" in inner, m.group(0)[:120])


@unittest.skipUnless(NODE, "node is not installed")
class DesignRuns(_Slots, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            harness = pathlib.Path(tmp) / "harness.js"
            harness.write_text(PRE + DRIVER, encoding="utf-8")
            done = subprocess.run(
                [NODE, str(harness), str(TEMPLATE)], capture_output=True, encoding="utf-8", timeout=120,
                input=json.dumps({"ids": DESIGN_IDS, "fixtures": _fixtures()}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)

    def test_registry_has_six_designs_in_order_with_every_field(self):
        reg = self.out["registry"]
        self.assertEqual([(d["id"], d["no"], d["accent"], d["scheme"], d["tags"]) for d in reg], EXPECTED)
        for d in reg:
            for field in ("name", "tagline"):
                self.assertEqual(sorted(d[field]), ["en", "ru"])
                self.assertTrue(all(d[field].values()), d["id"])
        self.assertEqual(self.out["consts"], [[e[0] for e in EXPECTED], "autopilot-design", "aurora"])
        self.assertEqual(DESIGN_IDS, [e[0] for e in EXPECTED])  # the test module reads the ids from the template

    def test_stored_design_is_aurora_unless_the_storage_holds_a_known_id(self):
        # empty, known, unknown, storage throws (even with a known id inside)
        self.assertEqual(self.out["stored"], ["aurora", "editorial", "aurora", "aurora"])

    def test_first_draw_puts_the_stored_design_and_its_scheme_on_html(self):
        self.assertEqual(self.out["first"], [["terminal", "dark"], ["blueprint", "light"], ["aurora", None], ["aurora", None]])

    def test_select_design_stores_applies_and_redraws(self):
        s = self.out["select"]
        self.assertEqual((s["store"], s["attr"], s["theme"]), ("blueprint", "blueprint", "light"))
        self.assertNotEqual(s["html"], s["before"])
        self.assertRegex(s["html"], r'data-dopt="blueprint"[^>]*aria-selected="true"')
        self.assertRegex(s["html"], r'value="Blueprint"')
        self.assertEqual(self.out["denied"], {"attr": "terminal"})  # a failed write does not break the page
        self.assertEqual(self.out["unknownSelect"], {"store": None, "attr": "aurora"})

    def test_search_finds_by_name_in_both_languages_number_id_and_tag(self):
        q = self.out["search"]
        self.assertEqual(q[""], DESIGN_IDS)
        self.assertEqual(q["  "], DESIGN_IDS)
        for query in ("чертёж", "Чертёж", "blueprint", "05", "5"):
            self.assertEqual(q[query], ["blueprint"], query)
        self.assertEqual(q["mono"], ["terminal"])
        self.assertEqual(q["light"], ["editorial", "blueprint", "bento"])
        self.assertEqual(q["dark"], ["aurora", "terminal"])
        self.assertEqual((q["aurora"], q["АВРОРА"], q["report"]), (["aurora"], ["aurora"], ["editorial"]))
        self.assertEqual(q["zzz"], [])

    def test_keys_arrows_enter_escape_and_the_aria_of_the_combobox(self):
        k = self.out["keys"]
        self.assertFalse(k["closedDown"])               # the list is closed: the handler on #app opens it instead of comboKey
        self.assertTrue(k["openedByDown"])
        self.assertEqual((k["start"], k["down"], k["upWraps"]), (0, 1, 5))  # aurora is the current one; two Up from 1 wrap to the last
        self.assertEqual(k["active"], "dopt-bento")
        self.assertTrue(k["role"])
        self.assertEqual(k["escape"], [False, "aurora"])                     # Esc closes without choosing
        self.assertEqual(k["enter"], [False, "terminal", "terminal"])        # the filtered list "mono": Enter picks its first
        self.assertEqual(k["none"], [True, True])                            # junk query: the message in Russian
        self.assertTrue(k["noneEn"])

    def test_theme_buttons_exist_only_for_the_design_with_both_schemes(self):
        for design, (_, _, _, scheme, _) in zip(DESIGN_IDS, EXPECTED):
            with self.subTest(design=design):
                self.assertEqual(self.out["pages"][design]["themeButtons"], 2 if scheme == "both" else 0)
                self.assertEqual(self.out["pages"][design]["theme"], {"both": None}.get(scheme, scheme))

    def test_every_design_draws_the_same_sections_and_anchors(self):
        base = self.out["pages"]["aurora"]["ids"]
        for sec in SECTIONS:
            self.assertIn(sec, base)
        for design in DESIGN_IDS:
            with self.subTest(design=design):
                self.assertEqual(self.out["pages"][design]["ids"], base)

    def test_rail_marks_the_link_of_the_section_nearest_the_top(self):
        self.assertEqual(self.out["rail0"], ["page", None, None])      # first section at the top
        self.assertEqual(self.out["rail2"], [None, "page", None])      # tasks scrolled to 50 px; one link at a time
        self.assertEqual(self.out["railReqs"], ["page", None, None])   # reqs has no link: the section above keeps it
        self.assertEqual(self.out["pick"], [2, 0, 0])

    def test_scroll_and_hash_change_move_the_rail_mark(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        self.assertRegex(html, r"addEventListener\('scroll', railSync")
        self.assertRegex(html, r"addEventListener\('hashchange', railSync")
        self.assertRegex(html, r"gxFit\(app\);\s*railSync\(\);")


def _lum(hex_):
    hex_ = hex_.strip()
    if len(hex_) == 4:
        hex_ = "#" + "".join(c * 2 for c in hex_[1:])
    ch = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


LIGHT = ("editorial", "blueprint", "bento")
TOKENS = ("bg card inset soft line line2 tx tx2 mut quiet hero hero-shadow sh sh-raised done done-soft done-tx on-done now now-soft now-tx now-on hatch "
          "rev rev-soft rev-tx on-rev fix fix-soft fix-tx on-fix bad bad-soft bad-tx on-bad idle accent warn-bg warn-bd warn-tx").split()


class DesignPalettes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = TEMPLATE.read_text(encoding="utf-8")
        cls.css = cls.html.split("<style>")[1].split("</style>")[0]

    def block(self, design):
        m = re.search(r'html\[data-design="%s"\]\[data-theme="light"\]\[lang\]:not\(\[hidden\]\)\{([^}]*)\}' % design, self.css)
        self.assertTrue(m, design + ": no token block")
        return dict(re.findall(r"--([\w-]+):\s*([^;}]+)", m.group(1)))

    def test_each_light_design_sets_every_shared_token(self):
        for design in LIGHT:
            with self.subTest(design=design):
                self.assertEqual([t for t in TOKENS if t not in self.block(design)], [])

    def test_text_and_filled_status_colours_reach_4_5_to_1(self):
        for design in LIGHT:
            tok = self.block(design)
            for ground in ("card", "bg"):
                for name in ("tx", "tx2", "mut", "quiet"):
                    with self.subTest(design=design, token=name, ground=ground):
                        self.assertGreaterEqual(contrast(tok[name], tok[ground]), 4.5)
            for fill, on in (("done", "on-done"), ("rev", "on-rev"), ("fix", "on-fix"), ("bad", "on-bad"), ("now", "now-on")):
                with self.subTest(design=design, fill=fill):
                    self.assertGreaterEqual(contrast(tok[on], tok[fill]), 4.5)

    def test_the_three_designs_left_the_aurora_fallback_list_and_use_system_stacks(self):
        for m in re.finditer(r"html:is\(([^)]*)\)", self.css):
            for design in LIGHT if "terminal" in m.group(1) else ():  # the fallback list; my own :is() lists are fine
                self.assertNotIn('[data-design="%s"]' % design, m.group(1))
        mine = "".join(re.findall(r'html\[data-design="(?:editorial|blueprint|bento)"\][^{]*\{[^}]*\}', self.css))
        for bad in ("http://", "https://", "@import", "@font-face", "url("):
            self.assertNotIn(bad, mine)
        self.assertNotIn("<link", self.html)
        self.assertIn("Georgia", mine)

    def test_common_css_hides_each_slot_and_each_design_shows_its_own(self):
        for slot in ("dx-stamp", "dx-dim", "dx-ring"):
            self.assertIn(".%s" % slot, self.css)
        self.assertIn(".dx-stamp,.dx-dim,.dx-ring{display:none}", self.css)
        for design, slot in (("editorial", "dx-stamp"), ("blueprint", "dx-dim"), ("bento", "dx-ring")):
            self.assertRegex(self.css, r'\[data-design="%s"\][^{]*\.%s\{[^}]*display:' % (design, slot))

    def test_targets_are_44px_and_motion_respects_the_reduced_motion_query(self):
        self.assertRegex(self.css, r'html:is\(\[data-design="editorial"\],\[data-design="blueprint"\],\[data-design="bento"\]\) :is\([^)]*summary[^)]*\.vopt[^)]*button[^)]*\)\{[^}]*min-height:44px')
        blocks = self.css.split("prefers-reduced-motion: reduce")[1:]
        self.assertTrue(any(".dx-stamp" in b and "animation:none" in b for b in blocks), "no reduced-motion rule for the new elements")


class DesignStrings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = TEMPLATE.read_text(encoding="utf-8")
        cls.css = cls.html.split("<style>")[1].split("</style>")[0]

    def test_tokens_live_under_the_data_design_selector_and_the_old_layer_stays_as_the_fallback(self):
        self.assertIn('<html lang="ru" data-design="aurora">', self.html)
        self.assertNotIn("data-skin", self.html)
        # the five designs without a palette yet take the aurora tokens through :is(); the fallback layers are untouched
        for design in DESIGN_IDS:
            self.assertIn('[data-design="%s"]' % design, self.css)
        self.assertIn("--bg:#F2F2F4; --card:#fff", self.css)          # :root, the colours of the unknown data-design
        self.assertIn(":root[lang]:not([hidden]){", self.css)

    def test_each_design_sets_its_accent_from_the_registry_over_the_shared_tokens(self):
        for design, _, accent, _, _ in EXPECTED[1:]:
            with self.subTest(design=design):
                self.assertIn('html[data-design="%s"][lang]:not([hidden]):not([data-theme="none"]){--accent:%s}' % (design, accent), self.css)

    def test_combobox_and_options_are_44px_targets(self):
        for rule in (r"\.dcombo\{[^}]*min-height:44px", r"\.dopt\{[^}]*min-height:44px", r"\.dcombo-btn\{[^}]*width:44px;height:44px"):
            self.assertRegex(self.css, rule)

    def test_no_second_design_mechanism_is_left(self):
        for gone in ("data-skin", "data-vcombo", "VIEW_IDS", "selectView"):
            self.assertNotIn(gone, self.html)
        self.assertEqual(len(re.findall(r"const DESIGNS = \[", self.html)), 1)


if __name__ == "__main__":
    unittest.main()
