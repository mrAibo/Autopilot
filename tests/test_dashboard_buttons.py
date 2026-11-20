"""Dashboard confirm buttons (R34, R35): the block for the waits briefing/spec/plan/accept and the copy-only commands.
The template's JS runs in node; the server is a fetch stub that follows the POST /.ap-act contract of interfaces.md."""
import html as htmllib
import json
import pathlib
import re
import subprocess
import tempfile
import unittest

from test_dashboard_designs import PRE
from test_dashboard_views import DESIGN_IDS, NODE, TEMPLATE, _fixtures

# env() of the shared harness hard-codes file:; the buttons need http: with and without a token.
PRE_HTTP = PRE.replace("protocol: 'file:'", "protocol: opts.protocol || 'file:'")
assert PRE_HTTP != PRE

DRIVER = r"""
const F = input.fixtures, out = {};
const TOKEN = '?t=abc123';
const wait = () => new Promise(r => setTimeout(r, 5));
// page(): state + waiting -> env on http: (token or not), a fetch stub answering with `reply` (a status, or 'down')
function page(state, waiting, o) {
  o = o || {};
  const s = JSON.parse(JSON.stringify(state));
  if (waiting) s.waiting = waiting; else delete s.waiting;
  const e = env(s, {}, false, 0, {search: o.search, protocol: o.protocol || 'http:'});
  e.calls = [];
  e.clock = {t: 1e6};                                   // a fake clock: the second click must come later than ACT_ARM_MS
  const RD = e.ctx.Date; e.ctx.Date = class extends RD { static now() { return e.clock.t; } };
  e.ctx.fetch = (url, opts) => { e.calls.push({url, opts}); return o.reply === 'down' ? Promise.reject(new Error('down')) : Promise.resolve({status: o.reply || 200}); };
  run(e, "render('en')");
  return e;
}
const btn = a => ({dataset: {}, hasAttribute: n => n === a});
const click = (e, a, gap) => { e.clock.t += gap === undefined ? 1000 : gap; return e.app.listeners.click({target: {closest: () => btn(a)}}); };
const type = (e, v) => e.app.listeners.input({target: {closest: s => s === '[data-act-answer]' ? {value: v} : null}});
const W = kind => ({kind, since: '2026-11-03T08:15:00Z', note: 'n'});
const body = e => (e.calls[0] ? JSON.parse(e.calls[0].opts.body) : null);

// every kind: block, one click arms, the second sends
out.kinds = {};
for (const kind of ['briefing', 'spec', 'plan', 'accept']) {
  const e = page(F.running, W(kind), {search: TOKEN});
  const r = {first: e.app.innerHTML};
  if (kind === 'briefing') { click(e, 'data-act'); r.emptyCalls = e.calls.length; r.emptyHtml = e.app.innerHTML; type(e, 'use postgres'); }
  click(e, 'data-act'); r.armed = e.app.innerHTML; r.callsAfterFirst = e.calls.length;
  click(e, 'data-act'); await wait(); r.callsAfterSecond = e.calls.length; r.call = e.calls[0]; r.sent = e.app.innerHTML;
  out.kinds[kind] = r;
}
// a double click inside a fraction of a second is one gesture: it arms, it does not send
{ const e = page(F.running, W('plan'), {search: TOKEN}); click(e, 'data-act'); click(e, 'data-act', 100); await wait(); out.fastCalls = e.calls.length;
  click(e, 'data-act', 700); await wait(); out.slowCalls = e.calls.length; }
// typing after arming drops the arming
{ const e = page(F.running, W('briefing'), {search: TOKEN}); type(e, 'a'); click(e, 'data-act'); type(e, 'ab'); out.rearm = e.app.innerHTML; }
// the server says no: the button is back, a line says why, nothing throws
out.errors = {};
for (const reply of [403, 409, 413, 503, 500, 'down']) {
  const e = page(F.running, W('plan'), {search: TOKEN, reply});
  click(e, 'data-act'); click(e, 'data-act'); await wait();
  out.errors[reply] = e.app.innerHTML;
}
// no token / file:, no waiting, action and stop
out.noTokenHttp = page(F.running, W('spec'), {}).app.innerHTML;
out.noTokenFile = page(F.running, W('spec'), {protocol: 'file:', search: TOKEN}).app.innerHTML;
out.noWait = page(F.finished, null, {search: TOKEN}).app.innerHTML;
out.noWaitNoToken = page(F.finished, null, {}).app.innerHTML;
out.action = page(F.nodone, W('action'), {search: TOKEN}).app.innerHTML;
out.stop = page(F.running, W('stop'), {search: TOKEN}).app.innerHTML;
out.failedNoWait = page(F.running, null, {search: TOKEN}).app.innerHTML;
out.failedNoToken = page(F.running, null, {}).app.innerHTML;
// the same block in every design
out.designs = {};
for (const id of input.ids) {
  const e = page(F.running, W('briefing'), {search: TOKEN});
  run(e, `applyDesign(${JSON.stringify(id)}); render('en')`);
  out.designs[id] = e.app.innerHTML;
}
console.log(JSON.stringify(out));
"""


def block(h):
    """The confirm block of a rendered page ('' when there is none)."""
    m = re.search(r'<section class="actblock".*?</section>', h, re.S)
    return m.group(0) if m else ""


def text(h):
    return htmllib.unescape(re.sub(r"<[^>]+>", " ", h))


@unittest.skipUnless(NODE, "node is not installed")
class DashboardButtons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            js = pathlib.Path(tmp) / "harness.js"
            js.write_text(PRE_HTTP + "(async () => {\n" + DRIVER + "\n})().catch(e => { console.error(e); process.exit(1); });",
                          encoding="utf-8")
            done = subprocess.run([NODE, str(js), str(TEMPLATE)], capture_output=True, encoding="utf-8", timeout=120,
                                  input=json.dumps({"ids": DESIGN_IDS, "fixtures": _fixtures()}))
        if done.returncode:
            raise AssertionError("node harness failed: " + done.stderr[-800:])
        cls.out = json.loads(done.stdout)

    def test_block_for_each_wait_kind_and_two_clicks_send_the_contract_body(self):
        want = {"briefing": "Send the answer", "spec": "Approve the spec", "plan": "Accept the plan", "accept": "Accept the delivery"}
        for kind, label in want.items():
            with self.subTest(kind=kind):
                r = self.out["kinds"][kind]
                self.assertEqual(block(r["first"]).count("data-act>"), 1)
                self.assertIn(label, text(block(r["first"])))
                self.assertIn("Sure? click again", text(block(r["armed"])))
                self.assertEqual(r["callsAfterFirst"], 0)
                self.assertEqual(r["callsAfterSecond"], 1)
                call = r["call"]
                self.assertEqual(call["url"], "/.ap-act?t=abc123")
                self.assertEqual(call["opts"]["method"], "POST")
                self.assertEqual(call["opts"]["headers"]["Content-Type"], "application/json")
                sent = json.loads(call["opts"]["body"])
                self.assertEqual(sent["kind"], kind)
                self.assertEqual(sent["since"], "2026-11-03T08:15:00Z")
                self.assertEqual(sent.get("answer"), "use postgres" if kind == "briefing" else None)
                self.assertNotIn("data-act>", block(r["sent"]))
                self.assertIn("Answer sent", text(block(r["sent"])))

    def test_a_double_click_does_not_skip_the_confirmation(self):
        self.assertEqual((self.out["fastCalls"], self.out["slowCalls"]), (0, 1))

    def test_briefing_has_an_answer_field_and_an_empty_answer_is_not_sent(self):
        r = self.out["kinds"]["briefing"]
        self.assertIn("data-act-answer", block(r["first"]))
        self.assertNotIn("data-act-answer", block(self.out["kinds"]["spec"]["first"]))
        self.assertEqual(r["emptyCalls"], 0)
        self.assertIn("empty", text(block(r["emptyHtml"])))
        self.assertNotIn("Sure?", text(block(r["emptyHtml"])))

    def test_editing_the_answer_after_arming_asks_again(self):
        self.assertNotIn("Sure?", text(block(self.out["rearm"])))

    def test_server_refusal_or_silence_returns_the_button_with_a_reason(self):
        for reply in ("403", "409", "413", "503", "500", "down"):
            with self.subTest(reply=reply):
                b = block(self.out["errors"][reply])
                self.assertEqual(b.count("data-act>"), 1)
                self.assertNotIn("Sure?", text(b))
                self.assertNotIn("Answer sent", text(b))
                self.assertRegex(b, r'role="alert"')
                self.assertTrue(re.search(r'role="alert">([^<]+)<', b).group(1).strip())
        self.assertIn("409", text(block(self.out["errors"]["409"])))
        self.assertNotEqual(block(self.out["errors"]["403"]), block(self.out["errors"]["503"]))

    def test_without_a_token_or_on_file_there_are_no_buttons_and_one_line_about_ap_py_url(self):
        for key in ("noTokenHttp", "noTokenFile"):
            with self.subTest(key=key):
                h = self.out[key]
                self.assertNotIn("data-act", h)
                self.assertEqual(text(block(h)).count("ap.py url"), 1)

    def test_no_wait_action_and_stop_have_no_confirm_buttons(self):
        for key in ("noWait", "noWaitNoToken", "action", "stop", "failedNoWait"):
            with self.subTest(key=key):
                self.assertNotIn("data-act>", self.out[key])
                self.assertNotIn("data-act-answer", self.out[key])
        self.assertNotIn("ap.py url", text(block(self.out["noWaitNoToken"])))

    def test_commands_with_the_users_words_are_copy_only(self):
        for key in ("action", "stop", "failedNoWait"):
            with self.subTest(key=key):
                h = self.out[key]
                cmds = re.findall(r'data-copy="([^"]*)"', h)
                joined = htmllib.unescape("\n".join(cmds))
                for need in ('finish --by-user "<цитата>"', 'opus approve --by-user "<цитата>"', "dropped"):
                    self.assertIn(need, joined)
                self.assertIn("manifest.md", text(h))
                self.assertIn("copy", text(h))
        self.assertIn('ticket 05 reset --by-user "<цитата>"', htmllib.unescape(self.out["failedNoWait"]))
        self.assertNotIn("data-copy", self.out["failedNoToken"])  # no token: read-only page

    def test_one_block_in_every_design(self):
        self.assertGreaterEqual(len(DESIGN_IDS), 6)
        first = block(self.out["designs"][DESIGN_IDS[0]])
        self.assertIn("data-act>", first)
        for id in DESIGN_IDS:
            with self.subTest(design=id):
                self.assertEqual(block(self.out["designs"][id]), first)

    def test_template_constants_and_touch_target(self):
        t = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn('const ACT_KINDS = ["briefing", "spec", "plan", "accept"]', t)
        self.assertRegex(t, r"\.actblock button\{[^}]*min-height:44px")
        self.assertIn("accept:", t.split("waitH2:")[1].split("waitHint")[0])
        self.assertIn("accept:", t.split("waitH2:")[2].split("waitHint")[0])


if __name__ == "__main__":
    unittest.main()
