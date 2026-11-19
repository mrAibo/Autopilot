"""Dashboard page: the waiting strip, the sections and the fixes of the feed, stage minutes, header and wording (runs the template's JS in node)."""
import json
import pathlib
import re
import subprocess
import tempfile
import unittest

from test_dashboard_views import DESIGN_IDS, GX_CASES, HARNESS, NODE, TEMPLATE, _fixtures


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
                input=json.dumps({"ids": DESIGN_IDS, "fixtures": _fixtures(), "gxCases": GX_CASES}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)
        cls.page = lambda self, name, lang="en": cls.out["renders"]["%s/aurora/%s" % (name, lang)]["html"]

    def test_page_picks_its_content_by_the_state_of_the_build(self):
        ask, run, fin = self.page("ask"), self.page("running"), self.page("finished")
        bar = re.search(r'<section class="askbar".*?</section>', ask, re.S).group(0)
        self.assertIn("Approve the spec? &lt;b&gt;x&lt;/b&gt;", bar)  # the question itself, escaped
        self.assertIn("data-since=", bar)  # how long it has waited
        self.assertLess(ask.index('class="askbar"'), ask.index('<details class="sec"'))  # pinned above every section
        self.assertNotIn("askbar", run)
        for title in ("Ticket 2", "Ticket 6"):  # development: the tickets are listed
            self.assertIn(title, run)
        self.assertNotIn("askbar", fin)
        self.assertIn("Built it", fin)

    def test_sections_hold_the_matrix_the_gantt_and_slots_for_the_details(self):
        run = self.page("running")
        self.assertEqual(run.count('class="mx-row"'), 10)  # the requirements matrix
        self.assertIn('class="gx"', run)  # the Gantt
        self.assertEqual(re.findall(r'data-slot="(\w+)"', run), ["models", "spend", "history"])
        for junk in ("undefined", "NaN", "[object"):
            self.assertNotIn(junk, run)

    def test_brand_mark_stands_in_the_header_and_the_rail(self):
        self.assertEqual(self.page("running").count('class="brandmark"'), 2)

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
            html = self.page("gated", lang)
            with self.subTest(lang=lang):
                self.assertEqual(html.count("<span>%s</span><em" % line), 6)  # six records, six feed rows
                self.assertIn(card, html)
                self.assertNotRegex(text_of(html), r"undefined|NaN")
                self.assertEqual(html.count('class="gs">' + card), 3)  # G1, G2, G4 are reset; G3 is not
                self.assertNotIn("0 открытых" if lang == "ru" else "0 open questions", html)  # not shown as passed
        for lang in ("ru", "en"):
            self.assertNotRegex(text_of(self.page("gated", lang)), r"undefined|NaN|\[object")

    def test_stage_minutes_are_the_sum_of_segments_not_first_start_to_last_end(self):
        route = re.search(r'<ol class="route">.*?</ol>', self.page("returned"), re.S).group(0)
        mins = [int(m) for m in re.findall(r'<li class="rs done".*?<span class="rs-sub">(\d+) min', route, re.S)]
        self.assertEqual(mins, [10, 10])  # 5 + 5 each; the old start..end said 15 and 15
        self.assertLessEqual(sum(mins), 20)  # the build lasted 20 minutes

    def test_finished_build_says_done_at_not_updated_ago(self):
        for lang, word, old in (("ru", "сдано", "обновлено"), ("en", "done", "updated")):
            top = re.search(r'<header class="top">.*?</header>', self.page("finished", lang), re.S).group(0)
            upd = re.search(r'<span class="upd">.*?(?=<div class="tools">)', top, re.S).group(0)
            with self.subTest(lang=lang):
                self.assertRegex(upd, word + r" \d\d:\d\d|" + word + r" \d")
                self.assertNotIn(old, upd)
                self.assertNotIn("data-ago", upd)
                running = re.search(r'<span class="upd">.*?(?=<div class="tools">)', self.page("running", lang), re.S).group(0)
                self.assertIn("data-ago", running)  # a running build still counts "N ago"

    def test_stage_strip_of_the_route_is_a_list_of_eight_items(self):
        route = re.search(r'<ol class="route">.*?</ol>', self.page("running"), re.S).group(0)
        self.assertEqual(route.count('<li class="rs '), 8)

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

    def test_service_strings_stay_out_of_the_page_and_gate_codes_stay_in_the_gates_section(self):
        for name in ("running", "finished", "gated", "ask", "empty"):
            for lang in ("ru", "en"):
                html = self.page(name, lang)
                with self.subTest(fixture=name, lang=lang):
                    self.assertNotIn("score=", html)
                    hero = html.split('<details class="sec"')[0]
                    self.assertNotRegex(text_of(hero), r"\bG[1-4]\b")  # the hero and the strip speak plain words
        self.assertRegex(text_of(self.page("running").split('id="gates"')[1]), r"\bG1\b")


if __name__ == "__main__":
    unittest.main()
