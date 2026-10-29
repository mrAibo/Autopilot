import re, subprocess, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"device ID\s*`?[0-9a-f]{8}-[0-9a-f]{4}-", re.I),
    # C:\Users\name\ ; placeholders <...> and generic fixture names allowed
    re.compile(r"[A-Za-z]:\\Users\\(?!<|demo\\|user\\|example\\)[A-Za-z0-9_.-]+\\"),
    re.compile(r"/(?:home|Users)/(?!<|demo/|user/|example/)[a-z0-9_.-]+/", re.I),
]

class NoMachineDataTests(unittest.TestCase):
    def test_tracked_text_files_have_no_machine_data(self):
        files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                               text=True, check=True).stdout.split()
        hits = []
        for name in files:
            if not name.endswith((".md", ".py", ".json", ".yml", ".txt")):
                continue
            if name == "tests/test_no_machine_data.py":
                continue
            text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
            for p in PATTERNS:
                for m in p.finditer(text):
                    hits.append(f"{name}: {m.group(0)}")
        self.assertEqual(hits, [], "\n".join(hits))
