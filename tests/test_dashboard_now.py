"""Dashboard page "Now" and the fixes of the feed, stage minutes, header and wording (runs the template's JS in node)."""
import json
import pathlib
import re
import subprocess
import tempfile
import unittest

from test_dashboard_views import GX_CASES, HARNESS, NODE, TEMPLATE, VIEW_IDS, _fixtures


def text_of(html):
    return re.sub(r"<[^>]*>", " ", html)


@unittest.skipUnless(NODE, "node is not installed")
class NowPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            harness = pathlib.Path(tmp) / "harness.js"
            harness.write_text(HARNESS, encoding="utf-8")
            done = subprocess.run(
                [NODE, str(harness), str(TEMPLATE)], capture_output=True, encoding="utf-8", timeout=120,
                input=json.dumps({"ids": VIEW_IDS, "fixtures": _fixtures(), "gxCases": GX_CASES}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)
        cls.page = lambda self, name, view="now", lang="en": cls.out["renders"]["%s/%s/%s" % (name, view, lang)]["html"]

    def test_now_is_the_first_view_with_four_tabs_in_both_languages(self):
        self.assertEqual(VIEW_IDS[0], "now")
        self.assertEqual(self.out["now"]["view"], "now")  # nothing saved: the page opens on "Now"
        for lang, names in (("ru", ["Сейчас", "Требования", "Итог", "Подробности"]),
                            ("en", ["Now", "Requirements", "Summary", "Details"])):
            tabs = re.search(r'<div class="ntabs".*?</div>', self.page("running", lang=lang), re.S).group(0)
            self.assertEqual(re.findall(r'data-ntab="(\w+)"', tabs), ["now", "req", "sum", "det"])
            self.assertEqual([x.strip() for x in re.findall(r">([^<]+)</button>", tabs)], names)

    def test_now_picks_its_content_by_the_state_of_the_build(self):
        ask, run, fin = self.page("ask"), self.page("running"), self.page("finished")
        self.assertIn('data-mode="ask"', ask)
        bar = re.search(r'<section class="askbar".*?</section>', ask, re.S).group(0)
        self.assertIn("Approve the spec? &lt;b&gt;x&lt;/b&gt;", bar)  # the question itself, escaped
        self.assertIn("data-since=", bar)  # how long it has waited
        self.assertLess(ask.index('class="askbar"'), ask.index('class="ntabs"'))  # pinned above everything
        self.assertIn('data-mode="dev"', run)
        self.assertNotIn("askbar", run)
        for title in ("Ticket 2", "Ticket 6"):  # development: the tickets are listed
            self.assertIn(title, run)
        self.assertIn('data-mode="done"', fin)
        self.assertNotIn("askbar", fin)
        self.assertIn("Built it", fin)

    def test_tabs_hold_requirements_summary_with_gantt_and_slots_for_details(self):
        tabs = self.out["now"]["tabs"]
        self.assertEqual(tabs["req"].count('class="mx-row"'), 10)  # the requirements matrix
        self.assertIn('class="gx"', tabs["sum"])  # the Gantt and the summary cards
        self.assertIn('class="kcards"', tabs["sum"])
        self.assertEqual(re.findall(r'data-slot="(\w+)"', tabs["det"]), ["models", "spend", "checks", "history"])
        for name, html in tabs.items():
            for junk in ("undefined", "NaN", "[object"):
                self.assertNotIn(junk, html, name)
            self.assertIn('data-ntab="%s" aria-selected="true"' % name, html)

    def test_old_themes_sit_under_more_and_the_logo_stays(self):
        closed = self.page("running")
        self.assertIn('class="vlist" hidden', closed)
        self.assertNotIn('data-views-more aria-expanded="true"', closed)
        opened = self.out["now"]["more"]
        self.assertIn('data-views-more aria-expanded="true"', opened)
        self.assertNotIn('class="vlist" hidden', opened)
        under = re.search(r'<span class="vlist".*?</span>', closed, re.S).group(0)
        self.assertEqual(re.findall(r'data-view="(\w+)"', under), VIEW_IDS[1:])  # the eight old themes, in order
        for view in VIEW_IDS[1:]:  # a chosen old theme keeps its list open
            self.assertNotIn('class="vlist" hidden', self.page("running", view))
        for view in VIEW_IDS:
            self.assertEqual(self.page("running", view).count('class="brandmark"'), 2, view)  # header and rail

    def test_narrow_window_folds_by_matchmedia(self):
        self.assertEqual(self.out["now"]["narrow"], ["1", None])
        html = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("matchMedia('(max-width: 699px)')", html)
        self.assertRegex(html, r"html\[data-narrow\] :is\(\.cols,\.ov3,\.tl2\)\{grid-template-columns:minmax\(0,1fr\)\}")

    def test_state_js_is_asked_with_the_token_from_the_page_address(self):
        with_token, without = self.out["now"]["url"]
        self.assertRegex(with_token, r"^state\.js\?t=abc123&_=\d+$")
        self.assertRegex(without, r"^state\.js\?_=\d+$")  # file://: no token, nothing else asked of it

    def test_plan_changed_reset_is_one_plain_line_and_never_undefined(self):
        for lang, line, card in (("ru", "Проверка сброшена: план изменился", "сброшена: план изменился"),
                                 ("en", "Check reset: the plan changed", "reset: the plan changed")):
            for view in ("overview", "timeline", "classic", "compact"):
                html = self.page("gated", view, lang)
                with self.subTest(view=view, lang=lang):
                    if view != "compact":
                        self.assertEqual(html.count("<span>%s</span><em" % line), 6)  # six records, six feed rows (the hero note says it once more)
                    self.assertIn(card, html)
                    self.assertNotRegex(text_of(html), r"undefined|NaN")
            gates = self.page("gated", "classic", lang)
            self.assertEqual(gates.count('class="gs">' + card), 3)  # G1, G2, G4 are reset; G3 is not
            self.assertNotIn("0 открытых" if lang == "ru" else "0 open questions", gates)  # not shown as passed
        for lang in ("ru", "en"):
            for view in VIEW_IDS:
                self.assertNotRegex(text_of(self.page("gated", view, lang)), r"undefined|NaN|\[object")

    def test_stage_minutes_are_the_sum_of_segments_not_first_start_to_last_end(self):
        for view in ("overview", "timeline"):
            route = re.search(r'<ol class="route">.*?</ol>', self.page("returned", view), re.S).group(0)
            mins = [int(m) for m in re.findall(r'<li class="rs done".*?<span class="rs-sub">(\d+) min', route, re.S)]
            self.assertEqual(mins, [10, 10], view)  # 5 + 5 each; the old start..end said 15 and 15
            self.assertLessEqual(sum(mins), 20)  # the build lasted 20 minutes

    def test_finished_build_says_done_at_not_updated_ago(self):
        for lang, word, old in (("ru", "сдано", "обновлено"), ("en", "done", "updated")):
            for view in VIEW_IDS:
                if view == "classic":
                    continue
                top = re.search(r'<header class="top">.*?</header>', self.page("finished", view, lang), re.S).group(0)
                upd = re.search(r'<span class="upd">.*?(?=<div class="tools">)', top, re.S).group(0)
                with self.subTest(view=view, lang=lang):
                    self.assertRegex(upd, word + r" \d\d:\d\d|" + word + r" \d")
                    self.assertNotIn(old, upd)
                    self.assertNotIn("data-ago", upd)
                    running = re.search(r'<span class="upd">.*?(?=<div class="tools">)', self.page("running", view, lang), re.S).group(0)
                    self.assertIn("data-ago", running)  # a running build still counts "N ago"

    def test_classic_shows_the_redo_counter_of_a_ticket_in_progress(self):
        classic = self.page("running", "classic")
        row = re.search(r'<span class="tl-id on">T02</span>.*?(?=<div class="tl">|</section>)', classic, re.S).group(0)
        self.assertIn("1 repair", row)  # T02 is in progress with one repair

    def test_stage_strip_items_are_list_items(self):
        classic = self.page("running", "classic")
        self.assertEqual(classic.count('role="list"'), 1)
        items = re.findall(r'<div class="s-(?:done|now|pend|skip|fail)"[^>]*>', classic)
        self.assertEqual(len(items), 8)
        self.assertTrue(all('role="listitem"' in x for x in items), items)

    def test_human_route_replaces_the_service_string(self):
        hr = self.out["hr"]
        self.assertEqual(hr["risky"], "Sonnet, усиленный режим: таск трогает подписи и ключи")
        self.assertEqual(hr["riskyEn"], "Sonnet, reinforced mode: the ticket touches signatures and keys")
        self.assertEqual(hr["plain"], "Haiku: простой таск")
        self.assertEqual(hr["premium"], "Opus, включён по твоему подтверждению")
        self.assertEqual(hr["string"], "an ordinary ticket")  # no model in a bare string: the phrase alone
        self.assertEqual(hr["foreign"], "chosen by hand")  # not the service string: kept, on one line
        self.assertEqual(hr["none"], "")
        for line in hr.values():
            self.assertNotRegex(line, r"score=|profile=|high-risk|\n")

    def test_service_strings_and_gate_codes_stay_out_of_the_main_text(self):
        for name in ("running", "finished", "gated", "ask", "empty"):
            for lang in ("ru", "en"):
                html = self.page(name, "now", lang)
                with self.subTest(fixture=name, lang=lang):
                    self.assertNotRegex(text_of(html), r"\bG[1-4]\b")
                    self.assertNotIn("score=", html)
        self.assertNotRegex(text_of(self.out["now"]["tabs"]["det"]), r"\bG[1-4]\b")  # not in the details either


if __name__ == "__main__":
    unittest.main()
