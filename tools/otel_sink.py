"""Local OTLP/HTTP-JSON sink: appends every POST body to <dir>/<signal>.jsonl.

Usage: python otel_sink.py --dir otel [--port 4318]   (binds 127.0.0.1 only, stdlib only)
Point Claude Code at it with OTEL_EXPORTER_OTLP_PROTOCOL=http/json (see docs/autopilot/measuring-cost.md).
"""
import argparse
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


def make_server(out_dir, port=4318):
    os.makedirs(out_dir, exist_ok=True)

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            sig = "".join(c for c in (self.path.rstrip("/").rsplit("/", 1)[-1] or "unknown") if c.isalnum()) or "unknown"
            ctype = self.headers.get("Content-Type", "")
            with open(os.path.join(out_dir, sig + ".jsonl"), "a", encoding="utf-8") as f:
                if "json" in ctype:
                    # compact to one line so each POST is exactly one JSONL record
                    try:
                        f.write(json.dumps(json.loads(body), separators=(",", ":")) + "\n")
                    except ValueError:
                        f.write(json.dumps({"_invalid_json": True, "bytes": len(body)}) + "\n")
                else:  # protobuf/gzip: keep a marker so the problem is visible
                    f.write(json.dumps({"_nonjson": ctype, "bytes": len(body)}) + "\n")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"{}")
            print(time.strftime("%H:%M:%S"), self.path, len(body), "bytes", ctype, flush=True)

        def log_message(self, *a):
            pass

    return HTTPServer(("127.0.0.1", port), H)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", default="otel")
    ap.add_argument("--port", type=int, default=4318)
    a = ap.parse_args()
    srv = make_server(a.dir, a.port)
    print("OTLP sink on http://127.0.0.1:%d -> %s" % (srv.server_port, os.path.abspath(a.dir)), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
