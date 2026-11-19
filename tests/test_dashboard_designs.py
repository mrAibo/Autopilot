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
// the old requirements ring and the new one, per design, on an empty build and on one with tickets
out.ring = {};
for (const id of input.ids) for (const name of ['empty', 'running']) {
  const x = env(input.fixtures[name], {}, false); run(x, `applyDesign(${JSON.stringify(id)}); render('en')`);
  const h = x.app.innerHTML;
  out.ring[id + '/' + name] = {oldInHero: (h.match(/<section class="card ovh[^>]*>\s*<div class="ring"/g) || []).length,
    old: (h.match(/class="ring"/g) || []).length, dx: (h.match(/class="dx-ring"/g) || []).length};
}
console.log(JSON.stringify(out));
"""


def registry():
    """The designs as the template declares them: [{id, no, accent, scheme, tags}] in registry order (a seventh design appears here by itself)."""
    block = TEMPLATE.read_text(encoding="utf-8").split("const DESIGNS = [", 1)[1].split("\n];", 1)[0]
    return [{"id": m[0], "no": m[1], "accent": m[2], "scheme": m[3], "tags": re.findall(r"'([^']+)'", m[4])}
            for m in re.findall(r"\{id:'(\w+)', no:'(\d+)'.*?accent:'(#\w+)', scheme:'(\w+)', tags:\[([^\]]*)\]", block, re.S)]


REG = registry()
SCHEME = {d["id"]: d["scheme"] for d in REG}
LIGHT = tuple(d["id"] for d in REG if d["scheme"] == "light")
HALF = {"both": None, "light": "light", "dark": "dark"}   # what applyDesign puts in data-theme: both leaves the choice to the user
GOLDEN = [  # id, no, accent, scheme, tags: the registry of mockups/dashboard-2026/designs.js plus the schemes of the spec; the template may only grow after these six
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

    def test_ticker_runs_the_stage_progress_tests_and_time_and_is_hidden_from_readers(self):
        run = self.out["dx"]["running/en"]
        self.assertRegex(run, r'<div class="dx-ticker" aria-hidden="true">')
        ticker = re.search(r'<div class="dx-ticker".*?</div></div>', run, re.S).group(0)
        for part in ("Development", "1/7", "29", "min"):  # active stage, done/total tickets, passed tests, time
            self.assertIn(part, ticker)
        self.assertRegex(self.out["dx"]["running/ru"], r'class="dx-ticker"[^>]*>.*?Разработка')

    def test_ascii_bars_show_stages_requirements_and_tickets_with_label_and_value(self):
        html = self.out["dx"]["running/en"]
        block = re.search(r'<div class="dx-ascii".*?</div></div>', html, re.S).group(0)
        # 5 of 8 stages -> 13 of 20 cells (JS rounds 12.5 up); 3 of 10 requirements -> 6; 1 of 7 tickets -> 3
        for bar, value in (("█" * 13 + "░" * 7, "5/8"), ("█" * 6 + "░" * 14, "3/10"), ("█" * 3 + "░" * 17, "1/7")):
            self.assertIn("[%s]" % bar, block)
            self.assertIn("<b>%s</b>" % value, block)
        for label in ("stages", "requirements", "tickets"):
            self.assertIn(label, block)
        self.assertIn("требования", self.out["dx"]["running/ru"])

    def test_empty_build_has_neither_ticker_nor_ascii_block(self):
        for lang in ("en", "ru"):
            for needle in ("dx-ticker", "dx-ascii"):
                self.assertNotIn(needle, self.out["dx"]["empty/" + lang])

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

    def test_registry_keeps_the_golden_six_first_and_every_entry_has_every_field(self):
        reg = self.out["registry"]
        got = [(d["id"], d["no"], d["accent"], d["scheme"], d["tags"]) for d in reg]
        self.assertEqual(got[:len(GOLDEN)], GOLDEN)               # a seventh design may follow, the six do not move
        self.assertEqual(got, [(d["id"], d["no"], d["accent"], d["scheme"], d["tags"]) for d in REG])  # the page and the test parser agree
        for d in reg:
            for field in ("name", "tagline"):
                self.assertEqual(sorted(d[field]), ["en", "ru"])
                self.assertTrue(all(d[field].values()), d["id"])
        self.assertEqual(self.out["consts"], [[d["id"] for d in REG], "autopilot-design", "aurora"])
        self.assertEqual(DESIGN_IDS, [d["id"] for d in REG])  # the test module reads the ids from the template

    def test_stored_design_is_aurora_unless_the_storage_holds_a_known_id(self):
        # empty, known, unknown, storage throws (even with a known id inside)
        self.assertEqual(self.out["stored"], ["aurora", "editorial", "aurora", "aurora"])

    def test_first_draw_puts_the_stored_design_and_its_scheme_on_html(self):
        self.assertEqual(self.out["first"], [["terminal", HALF[SCHEME["terminal"]]], ["blueprint", HALF[SCHEME["blueprint"]]], ["aurora", None], ["aurora", None]])

    def test_select_design_stores_applies_and_redraws(self):
        s = self.out["select"]
        self.assertEqual((s["store"], s["attr"], s["theme"]), ("blueprint", "blueprint", HALF[SCHEME["blueprint"]]))
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
        for tag in ("mono", "light", "dark"):                      # by tag: the designs of the registry that carry it
            self.assertEqual(q[tag], [d["id"] for d in REG if tag in d["tags"]], tag)
        self.assertEqual((q["aurora"], q["АВРОРА"], q["report"]), (["aurora"], ["aurora"], ["editorial"]))
        self.assertEqual(q["zzz"], [])

    def test_keys_arrows_enter_escape_and_the_aria_of_the_combobox(self):
        k = self.out["keys"]
        self.assertFalse(k["closedDown"])               # the list is closed: the handler on #app opens it instead of comboKey
        self.assertTrue(k["openedByDown"])
        self.assertEqual((k["start"], k["down"], k["upWraps"]), (0, 1, len(REG) - 1))  # aurora is the current one; two Up from 1 wrap to the last
        self.assertEqual(k["active"], "dopt-" + REG[-1]["id"])
        self.assertTrue(k["role"])
        self.assertEqual(k["escape"], [False, "aurora"])                     # Esc closes without choosing
        self.assertEqual(k["enter"], [False, "terminal", "terminal"])        # the filtered list "mono": Enter picks its first
        self.assertEqual(k["none"], [True, True])                            # junk query: the message in Russian
        self.assertTrue(k["noneEn"])

    def test_theme_buttons_exist_only_for_the_design_with_both_schemes(self):
        for design, scheme in SCHEME.items():
            with self.subTest(design=design):
                self.assertEqual(self.out["pages"][design]["themeButtons"], 2 if scheme == "both" else 0)
                self.assertEqual(self.out["pages"][design]["theme"], HALF[scheme])

    def test_every_design_draws_the_same_sections_and_anchors(self):
        base = self.out["pages"]["aurora"]["ids"]
        for sec in SECTIONS:
            self.assertIn(sec, base)
        for design in DESIGN_IDS:
            with self.subTest(design=design):
                self.assertEqual(self.out["pages"][design]["ids"], base)

    def test_old_ring_sits_where_the_hide_rule_reaches_it_and_never_next_to_the_new_one(self):
        # the CSS side (.ovh>.ring{display:none} for every design) is held by AllDesignLimits; here: the markup the rule meets
        for design in DESIGN_IDS:
            for name in ("empty", "running"):
                got = self.out["ring"][design + "/" + name]
                with self.subTest(design=design, build=name):
                    self.assertEqual((got["old"], got["oldInHero"]), (1, 1))          # one old ring, a direct child of the hero: hidden
                    self.assertLessEqual(got["dx"], 0 if name == "empty" else 1)      # no tickets: no new ring, so no empty frame; else at most one

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

    def test_motion_respects_the_reduced_motion_query(self):
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
        for d in REG[1:]:  # the first design (the default) sets its accent inside its own token halves
            with self.subTest(design=d["id"]):
                self.assertIn('html[data-design="%s"][lang]:not([hidden]):not([data-theme="none"]){--accent:%s}' % (d["id"], d["accent"]), self.css)

    def test_combobox_and_options_are_44px_targets(self):
        for rule in (r"\.dcombo\{[^}]*min-height:44px", r"\.dopt\{[^}]*min-height:44px", r"\.dcombo-btn\{[^}]*width:44px;height:44px"):
            self.assertRegex(self.css, rule)

    def test_no_second_design_mechanism_is_left(self):
        for gone in ("data-skin", "data-vcombo", "VIEW_IDS", "selectView"):
            self.assertNotIn(gone, self.html)
        self.assertEqual(len(re.findall(r"const DESIGNS = \[", self.html)), 1)


# The ceiling of the whole template (bytes): if a design does not fit, the design is cut, the ceiling stays.
TEMPLATE_CEILING = 450 * 1024


class AllDesignLimits(unittest.TestCase):
    """The brief's points, checked for every one of the six designs."""

    @classmethod
    def setUpClass(cls):
        cls.html = TEMPLATE.read_text(encoding="utf-8")
        cls.css = cls.html.split("<style>")[1].split("</style>")[0]

    def halves(self, design):
        sel = {"aurora": ['html:is([data-design="aurora"]):not([hidden]):not([data-theme="light"])',
                          'html:is([data-design="aurora"])[data-theme="light"][lang]:not([hidden])']}.get(design) or [
            'html[data-design="%s"][data-theme="%s"][lang]:not([hidden])' % (design, half)
            for half in (("dark", "light") if SCHEME[design] == "both" else (SCHEME[design],))]  # a new design: one block per scheme half
        out = []
        for s in sel:
            m = re.search(re.escape(s) + r"\{([^}]*)\}", self.css)
            self.assertTrue(m, "no token block: " + s)
            out.append(dict(re.findall(r"--([\w-]+):\s*([^;}]+)", m.group(1))))
        return out

    def test_every_design_sets_every_shared_token_in_each_half(self):
        for design in DESIGN_IDS:
            halves = self.halves(design)
            self.assertEqual(len(halves), 2 if SCHEME[design] == "both" else 1)
            for tok in halves:
                with self.subTest(design=design):
                    self.assertEqual([t for t in TOKENS if t not in tok], [])

    def test_contrast_is_4_5_to_1_in_every_half_of_every_design(self):
        for design in DESIGN_IDS:
            for tok in self.halves(design):
                for ground in ("card", "bg"):
                    for name in ("tx", "tx2", "mut", "quiet"):
                        with self.subTest(design=design, token=name, ground=ground):
                            self.assertGreaterEqual(contrast(tok[name], tok[ground]), 4.5)
                for fill, on in (("done", "on-done"), ("rev", "on-rev"), ("fix", "on-fix"), ("bad", "on-bad"), ("now", "now-on")):
                    with self.subTest(design=design, fill=fill):
                        self.assertGreaterEqual(contrast(tok[on], tok[fill]), 4.5)

    def test_no_design_borrows_the_aurora_tokens_any_more(self):
        for m in re.finditer(r"html:is\(([^)]*)\)[^{]*\{[^}]*(?:--aurora-mint|--bg:)", self.css):  # the blocks that carry tokens
            self.assertNotIn('[data-design="brutal"]', m.group(1))
            self.assertNotIn('[data-design="terminal"]', m.group(1))

    def test_nothing_external_and_the_template_fits_the_ceiling(self):
        for bad in ("http://", "https://", "<link", "@import", "@font-face", "fetch("):
            self.assertNotIn(bad, self.html)
        self.assertLessEqual(len(self.html.encode("utf-8")), TEMPLATE_CEILING)

    def test_every_design_is_covered_by_motion_and_print_rules(self):
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertEqual(sorted(SCHEME), sorted(DESIGN_IDS))
        self.assertRegex(self.css, r"@media print\{")
        reduced = self.css.split("prefers-reduced-motion")
        self.assertTrue(any(".dx-ticker-track{animation:none" in b for b in reduced), "the ticker still runs under reduced motion")

    def rule(self, selector_part, body_part):
        """The selectors (split by comma) of every rule whose body holds body_part and one selector holds selector_part."""
        return [sel.strip() for m in re.finditer(r"([^{}]+)\{([^}]*)\}", re.sub(r"/\*.*?\*/", "", self.css, flags=re.S)) if body_part in m.group(2)
                for sel in re.split(r",(?![^()]*\))", m.group(1)) if selector_part in sel]

    def test_targets_are_44px_in_every_design_aurora_included(self):
        general = self.rule(":is(summary,.vopt,button)", "min-height:44px")
        self.assertEqual(general, ["html:not([hidden]) :is(summary,.vopt,button)"])   # one rule, no design in it
        for design in DESIGN_IDS:                                                     # so it reaches the chips (36 px) and soft buttons (38 px) of each
            with self.subTest(design=design):
                self.assertNotIn("data-design", general[0])
        self.assertNotRegex(self.css, r"html:is\(\[data-design[^{]*:is\(summary")   # the old per-design lists (aurora was missing) are gone

    def test_the_old_requirements_ring_is_never_drawn_visible(self):
        hide = self.rule(".ring", "display:none")
        self.assertIn(".ovh>.ring", hide)
        self.assertTrue(all("data-design" not in h for h in hide), hide)               # not bound to a design: Aurora included
        shown = [sel for sel in self.rule(".ring", "display:") if not re.search(r"\.ring-|\.dx-ring|\.ovh>\.ring$", sel)]
        self.assertEqual(shown, [".ring"])                                             # the only other display rule is the base one (weaker than .ovh>.ring)

    def test_accent_as_text_has_4_5_to_1_on_the_ground_and_the_card_or_falls_back_to_the_text_colour(self):
        for design in DESIGN_IDS:
            for tok in self.halves(design):
                for ground in ("bg", "card"):
                    if contrast(tok["accent"], tok[ground]) >= 4.5:
                        continue
                    for el in (".wordmark b", '.dopt[aria-selected="true"]'):         # the accent as text colour: header mark and the chosen option
                        with self.subTest(design=design, ground=ground, el=el):
                            own = [x for x in self.rule(el, "color:var(--tx)") if 'data-design="%s"' % design in x and ".rail-brand" not in x]
                            self.assertTrue(own, "the accent is too pale on the %s and %s has no own colour" % (ground, el))
                            self.assertGreaterEqual(contrast(tok["tx"], tok[ground]), 4.5)

    def test_the_rail_takes_the_hero_colour_in_every_design_but_aurora_and_its_text_stays_readable(self):
        self.assertIn('html[data-design]:not([data-design="aurora"]) .cockpit-rail{background:var(--hero);border-right-color:var(--line2)}', self.css)
        light_on_dark = set(re.findall(r"--rail-(?:tx|accent):(#\w+)", self.css))
        for m in re.finditer(r"([^{}]+)\{([^}]*)\}", self.css):
            sel = m.group(1).strip()
            if (sel.startswith(".rail-") or sel.startswith(".cockpit-rail")) and not sel.startswith(".rail-symbol"):
                light_on_dark.update(re.findall(r"(?<![-\w])color:(#\w+)", m.group(2)))
        self.assertGreaterEqual(len(light_on_dark), 6)
        for design in DESIGN_IDS:
            if design == "aurora":
                continue
            hero = self.halves(design)[0]["hero"]
            for colour in sorted(light_on_dark):
                with self.subTest(design=design, colour=colour):
                    self.assertGreaterEqual(contrast(colour, hero), 4.5)

        for pseudo in ("before", "after"):
            self.assertRegex(self.css, r'html\[data-design="terminal"\][^{]*body:%s\{' % pseudo)
            self.assertNotRegex(self.css, r'html\[data-design="(?!terminal)\w+"\][^{]*body:%s\{' % pseudo)
        self.assertEqual(self.halves("terminal")[0]["bg"].lower()[:2], "#0")  # dark half
        self.assertRegex(self.css, r'html\[data-design="terminal"\]\[data-theme="dark"\]\[lang\]')

    def test_each_special_slot_has_its_design_and_the_others_hide_it(self):
        self.assertIn(".dx-ticker,.dx-ascii{display:none}", self.css)
        self.assertRegex(self.css, r'\[data-design="brutal"\][^{]*\.dx-ticker\{[^}]*display:')
        self.assertRegex(self.css, r'\[data-design="terminal"\][^{]*\.dx-ascii\{[^}]*display:')

    def test_hero_has_no_fixed_height_when_it_stacks_into_a_column(self):
        # Root cause of the 400 px gap: .ovh-main{flex:1 1 400px} became a 400 px HEIGHT once .ovh turned flex-direction:column.
        css = re.sub(r"/\*.*?\*/", "", self.css, flags=re.S)
        stacked = [m.start() for m in re.finditer(r"[^{}]*\.ovh\{[^}]*flex-direction:column", css)]
        self.assertGreaterEqual(len(stacked), 2)                                  # the data-narrow rule and the 520 px rule
        reset = [m.start() for m in re.finditer(r"\.ovh>:is\(\.ovh-main,\.ovh-side\)\{[^}]*flex:0 0 auto", css)]
        self.assertEqual(len(reset), len(stacked), "a stacked hero keeps the row flex-basis of its children")
        self.assertGreater(min(reset), min(stacked))
        self.assertGreater(max(reset), max(stacked))                              # the last word of each
        self.assertNotRegex(css, r"\.ovh(?:-main|-side)?\{[^}]*(?<![-\w])(?:min-)?height:\d")   # no fixed or minimal height on the hero itself

    def test_print_hides_chrome_opens_every_details_and_turns_the_page_light(self):
        css = self.css.split("@media print{")[1]
        css = css[:css.index("\n  }\n")]
        for hidden in (".cockpit-rail", ".askbar", ".dx-ticker", "button"):
            self.assertRegex(css, r"[^}]*%s[^{]*\{[^}]*display:none" % re.escape(hidden))
        self.assertRegex(css, r"details[^{]*>[^{]*\{[^}]*display:block")        # the body of a folded section is shown
        self.assertIn("content-visibility:visible", css)
        self.assertRegex(css, r"--bg:#fff!important")
        self.assertRegex(css, r"--tx:#000!important")
        self.assertRegex(css, r"html\[data-design\]\[lang\]\{[^}]*color-scheme:light!important[^}]*background:#fff!important")  # a dark design left black page edges in the PDF
        self.assertRegex(css, r"body:before,body:after\{display:none")          # no CRT layers on paper
        self.assertRegex(css, r"\.dx-row code\{[^}]*color:#000!important")      # the accent code of the ASCII bars is black on paper
        for part in (r"\.dx-ring", r"\.seg i"):                                  # the ring and the progress segments keep their fills
            self.assertRegex(css, part + r"[^{]*\{[^}]*-webkit-print-color-adjust:exact")
        self.assertNotRegex(css, r"\.sec[,{][^{]*\{[^}]*break-inside:avoid")     # a whole section never jumps to the next sheet (a 9-page PDF with half-empty pages)
        self.assertRegex(css, r"\.card\{break-inside:avoid")                    # but a card is not split
        self.assertRegex(css, r"title:before[^{]*\{[^}]*color:#\w+!important")   # the pale eyebrow gets a dark colour on paper
        self.assertGreaterEqual(contrast("#000", "#fff"), 4.5)


if __name__ == "__main__":
    unittest.main()
