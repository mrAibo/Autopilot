"""Dashboard models section: spend by role/model/ticket, build history and comparison, incomplete-log badge, escalated ticket label
(runs the template's JS in node)."""
import copy
import json
import pathlib
import re
import subprocess
import tempfile
import unittest

from test_dashboard_views import HARNESS, NODE, TEMPLATE, _fixtures

HEAD = HARNESS.split("const run = ")[0]
SCRIPT = HEAD + r"""
const run = (e, code) => vm.runInContext(code, e.ctx);
const show = (e, lang, panel) => {
  run(e, "UI.panel = " + JSON.stringify(panel || null) + "; render('" + lang + "')");
  return e.app.innerHTML; };
const out = {};
for (const [name, st] of Object.entries(input.fixtures)) for (const lang of ['en', 'ru']) {
  const e = env(st, {}, false);
  out[name + '/page/' + lang] = show(e, lang);
  out[name + '/panel/' + lang] = show(e, lang, 'T02');
}
console.log(JSON.stringify(out));
"""


def _states():
    t = lambda m: "2026-11-03T08:%02d:00Z" % m
    base = copy.deepcopy(_fixtures()["finished"])  # 7 tickets, 1 repair each, 08:00 - 08:40
    base["usageEvents"] = []
    base.pop("spend", None)
    spend = {
        "byRole": {"executor": {"n": 30, "input": 3000, "output": 900, "tokens": 3900},
                   "reviewer": {"n": 8, "input": 800, "output": 200, "tokens": 1000}},
        "byModel": {"sonnet": {"n": 20, "input": 2000, "output": 500, "tokens": 2500},
                    "не указана": {"n": 18, "input": 1800, "output": 600, "tokens": 2400}},
        "byTicket": {"02": {"n": 4, "input": 400, "output": 100, "tokens": 500},
                     "F1": {"n": 2, "input": 40, "output": 10, "tokens": 50}}}
    hist = lambda i, **kw: dict({"dir": "2026-10-%02d-old" % i, "title": "Old build %d <b>x</b>" % i, "startedAt": t(0),
                                 "finishedAt": t(30), "minutes": 30, "tickets": 4, "repairs": 1, "tokens": 1000, "result": "ok"}, **kw)
    spent = dict(base, spend=spend)
    withhist = dict(spent, history=[hist(1), hist(2, minutes=90, tickets=6, repairs=3, tokens=0), hist(3, minutes=None, tokens=3000)])
    esc = copy.deepcopy(spent)
    esc["tickets"][1]["escalatedFrom"] = "claude-haiku-4-5"
    esc["tickets"][1]["routing"]["model"] = "sonnet"
    junk = dict(base, spend={"byRole": {"x": {"n": "many", "tokens": None}, "y": None}, "byModel": "bad", "byTicket": []},
                history=[None, 5, {"title": None}], logFailures="3")
    return {"empty": dict(base, history=[], logFailures=0),
            "spend": dict(spent, logFailures=3),  # a 38-row log, three rows lost
            "hist": withhist,
            "many": dict(spent, history=[hist(i) for i in range(1, 26)]),
            "esc": esc,
            "budget": dict(spent, budgetTokens=10000),   # лимит есть, usageEvents пусты — расход из журнала
            "nobudget": dict(spent, budgetTokens=None),
            "junk": junk,
            "running": dict(copy.deepcopy(_fixtures()["running"]), usageEvents=[])}


def text_of(html):
    return re.sub(r"<[^>]*>", " ", html)


@unittest.skipUnless(NODE, "node is not installed")
class Details(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            harness = pathlib.Path(tmp) / "harness.js"
            harness.write_text(SCRIPT, encoding="utf-8")
            done = subprocess.run([NODE, str(harness), str(TEMPLATE)], capture_output=True, encoding="utf-8", timeout=120,
                                  input=json.dumps({"fixtures": _states()}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)

    def page(self, name, kind="page", lang="en"):
        return self.out["%s/%s/%s" % (name, kind, lang)]

    def slot(self, html, name):
        return re.search(r'data-slot="%s">(.*?)</div><div class="det-slot"|data-slot="%s">(.*)' % (name, name), html, re.S).group(0)

    def test_spend_by_role_model_ticket_with_unknown_model_and_ticket_title(self):
        spend = self.slot(self.page("spend"), "spend")
        for head in ("By role", "By model", "What a ticket cost"):
            self.assertIn(head, spend)
        text = text_of(spend)
        for expect in ("executor", "reviewer", "3,900", "1,000", "4,900", "sonnet"):  # 3900 + 1000 tokens in all
            self.assertIn(expect, text)
        self.assertIn("not specified", text)  # the row without a model
        self.assertNotIn("не указана", spend)
        self.assertIn("02 · Ticket 2", text)  # the ticket title from the board
        self.assertIn("F1", text)  # a ticket the board does not know stays as it is
        ru = text_of(self.slot(self.page("spend", lang="ru"), "spend"))
        self.assertIn("не указана", ru)
        self.assertIn("Сколько стоил таск", ru)

    def test_token_limit_sits_next_to_log_spend_when_no_usage_events(self):
        html = self.page("budget")
        self.assertIn("4,900 / 10,000", text_of(html))   # 3900 + 1000 из журнала
        self.assertIn('aria-valuenow="4900"', html)
        self.assertIn("width:49%", html)
        spend = self.slot(self.page("budget"), "spend")
        self.assertIn("resource-budget", spend)                     # рядом с карточкой расхода
        self.assertNotIn("resource-budget", self.page("nobudget"))  # нет лимита — нет строки

    def test_no_spend_says_not_yet_with_one_reason(self):
        spend = self.slot(self.page("empty"), "spend")
        self.assertRegex(text_of(spend), r"none yet — the spend log was not kept or has no model recorded")
        self.assertNotIn("<table", spend)
        self.assertIn("ещё нет — журнал расхода не вёлся", text_of(self.slot(self.page("empty", lang="ru"), "spend")))

    def test_models_section_does_not_say_tokens_none_when_the_log_has_rows(self):
        res = self.page("spend")
        kpi = re.search(r'<section class="card tile w"><span class="tk">Tokens</span><span class="tv[^"]*">([^<]*)</span><span class="ts">([^<]*)</span>', res)
        self.assertEqual((kpi.group(1), kpi.group(2)), ("4,900", "in 3,800 · out 1,100"))
        self.assertNotIn("Token telemetry: no data yet", res)
        self.assertNotIn("Token telemetry: no data yet", self.page("spend"))
        bare = re.search(r'<span class="tk">Tokens</span><span class="tv dim">—</span><span class="ts">none yet</span>', self.page("empty"))
        self.assertTrue(bare)  # no rows, no usage events: still "none yet"

    def test_history_rows_comparison_and_cap(self):
        hist = self.slot(self.page("hist"), "history")
        rows = re.findall(r"<tr><td>(Old build[^<]*)</td>", hist)
        self.assertEqual(len(rows), 3)
        self.assertIn("Old build 1 &lt;b&gt;x&lt;/b&gt;", rows[0])  # escaped
        cmp = re.search(r'data-compare>.*?</table>', hist, re.S).group(0)
        cells = [[x.strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r)] for r in re.findall(r"<tr>(.*?)</tr>", cmp, re.S)]
        self.assertEqual(cells[1:], [["Duration", "40 min", "1 h 00 min"],   # this build 08:00-08:40, past 30 and 90 (no minutes: skipped)
                                     ["Tickets", "7", "5"], ["Repairs", "7", "2"],  # past 4/6/4 and 1/3/1: rounded mean
                                     ["Tokens", "4,900", "2,000"]])  # a past build with 0 tokens has no log: skipped
        self.assertNotIn("undefined", hist)
        many = self.slot(self.page("many"), "history")
        self.assertEqual(len(re.findall(r"<tr><td>Old build", many)), 20)  # 25 given, 20 shown

    def test_no_history_has_no_comparison(self):
        hist = self.slot(self.page("empty"), "history")
        self.assertIn("no past builds yet", text_of(hist))
        self.assertNotIn("data-compare", hist)
        self.assertNotIn("<table", hist)
        self.assertIn("прошлых сборок ещё нет", text_of(self.slot(self.page("empty", lang="ru"), "history")))

    def test_log_badge_only_when_rows_were_lost(self):
        html = self.page("spend")  # one badge, under the hero, visible with every section folded
        self.assertEqual(html.count("log incomplete: 3 lines not written"), 1)
        self.assertLess(html.index("logbadge"), html.index('<details class="sec"'))
        self.assertIn("журнал неполный: 3 строк не записано", self.page("spend", lang="ru"))
        for name in ("empty", "hist", "running", "junk"):  # 0, missing, and a non-number ("3")
            self.assertNotIn("logbadge", self.page(name), name)

    def test_escalated_ticket_is_labelled_on_the_card_and_in_the_panel(self):
        card = re.search(r'<button type="button" class="tcard[^>]*data-card="T02".*?</button>', self.page("esc"), re.S).group(0)
        self.assertIn('<span class="tc-esc">started on Haiku, finished on Sonnet</span>', card)
        self.assertIn("started on Haiku, finished on Sonnet", re.search(r'aria-label="([^"]*)"', card).group(1))
        panel = re.search(r'<aside class="tpanel".*?</aside>', self.page("esc", "panel"), re.S).group(0)
        self.assertIn('<p class="tp-esc">started on Haiku, finished on Sonnet</p>', panel)
        ru = self.page("esc", "panel", "ru")
        self.assertEqual(re.search(r'<aside class="tpanel".*?</aside>', ru, re.S).group(0).count("начат на Haiku, доделан на Sonnet"), 1)
        self.assertEqual(ru.count("начат на Haiku, доделан на Sonnet"), 3)  # the panel once, the card twice (label and line)
        self.assertEqual(self.page("esc").count('class="tc-esc"'), 1)  # one card only: the others are not escalated
        self.assertNotIn("tc-esc", self.page("spend"))

    def test_hostile_and_broken_data_never_prints_undefined_or_nan(self):
        for key, html in self.out.items():
            for junk in ("undefined", "NaN", "[object"):
                self.assertNotIn(junk, html, key)
        self.assertNotIn("<table", self.slot(self.page("junk"), "spend"))  # nothing usable: the empty card


if __name__ == "__main__":
    unittest.main()
