import contextlib
import importlib.util
import io
import json
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def A(**kw):
    return [{"key": k, "value": {"stringValue" if isinstance(v, str) else "doubleValue": v}} for k, v in kw.items()]


def metric(name, dps):
    return {"resourceMetrics": [{"scopeMetrics": [{"metrics": [{"name": name, "sum": {"dataPoints": dps}}]}]}]}


def dp(val, **attrs):
    return {"asDouble": val, "attributes": A(**attrs)}


def event(**attrs):
    return {"resourceLogs": [{"scopeLogs": [{"logRecords": [{"attributes": A(**{"event.name": "api_request", **attrs})}]}]}]}


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = Path(self.tmp.name)
        sub = dict(query_source="subagent", model="claude-haiku", effort="low")
        main = dict(query_source="main", model="claude-sonnet", effort="medium")
        metrics = [
            metric("claude_code.token.usage", [dp(100, type="input", **sub), dp(40, type="output", **sub),
                                               dp(7, type="cacheRead", **sub), dp(3, type="cacheCreation", **sub),
                                               dp(500, type="input", **main)]),
            metric("claude_code.cost.usage", [dp(0.25, **sub), dp(0.75, **main)]),
        ]
        (d / "metrics.jsonl").write_text("\n".join(json.dumps(m) for m in metrics) + "\n", encoding="utf-8")
        ev_sub = dict(model="claude-haiku", effort="low", input_tokens="10", output_tokens="5",
                      cache_read_tokens="2", cache_creation_tokens="1", cost_usd="0.5")
        events = [event(query_source="agent:custom", **ev_sub),
                  event(query_source="sdk", **{**ev_sub, "model": "claude-sonnet", "cost_usd": "1.5"})]
        (d / "logs.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
        self.mod = load("otel_summary")
        self.dir = str(d)

    def run_main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            import sys
            old, sys.argv = sys.argv, ["otel_summary", "--dir", self.dir, *argv]
            try:
                self.mod.main()
            finally:
                sys.argv = old
        return out.getvalue()

    def test_metrics_aggregate(self):
        met, _ = self.mod.collect(self.dir)
        self.assertEqual(met[("subagent", "claude-haiku", "low")], [100, 40, 7, 3, 0.25])
        self.assertEqual(met[("main", "claude-sonnet", "medium")][4], 0.75)

    def test_sdk_event_is_main_not_subagent(self):
        _, ev = self.mod.collect(self.dir)
        self.assertEqual(ev[("subagent", "claude-haiku", "low")][4], 0.5)
        self.assertEqual(ev[("main", "claude-sonnet", "low")][4], 1.5)
        self.assertNotIn(("subagent", "claude-sonnet", "low"), ev)

    def test_default_output_subagent_only_with_share(self):
        out = self.run_main()
        self.assertIn("claude-haiku", out)
        self.assertNotIn("claude-sonnet", out)
        self.assertIn("main 75.0%", out)  # metrics: 0.75 of 1.00
        self.assertIn("subagent 25.0%", out)

    def test_all_shows_main(self):
        self.assertIn("claude-sonnet", self.run_main("--all"))


class SinkTests(unittest.TestCase):
    def test_post_writes_one_line(self):
        sink = load("otel_sink")
        with tempfile.TemporaryDirectory() as d:
            srv = sink.make_server(d, 0)
            self.assertEqual(srv.server_address[0], "127.0.0.1")
            t = threading.Thread(target=srv.serve_forever, daemon=True)
            t.start()
            try:
                body = json.dumps({"resourceMetrics": []}, indent=2).encode()
                req = urllib.request.Request("http://127.0.0.1:%d/v1/metrics" % srv.server_port, data=body,
                                             headers={"Content-Type": "application/json"})
                self.assertEqual(urllib.request.urlopen(req, timeout=5).status, 200)
            finally:
                srv.shutdown()
                srv.server_close()
            lines = (Path(d) / "metrics.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(json.loads(lines[0]), {"resourceMetrics": []})
            self.assertEqual(len(lines), 1)


if __name__ == "__main__":
    unittest.main()
