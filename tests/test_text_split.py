"""R06: обычный путь навыка короче — режимы вынесены дословно, указатели на месте."""
import hashlib
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "autopilot")

# Обычный прогон на Claude Code читает эти файлы (без audit, 5-host-codex, 0-resume, rationalizations, 2-adversarial и вынесенных).
NORMAL_PATH = (["SKILL.md"]
               + ["phases/%s.md" % n for n in ("0-modes", "0-preflight", "0-memory", "0-instruments", "1-manifest",
                                               "2-briefing", "3-spec", "4-plan", "5-subagents", "5-host-claude",
                                               "5-repair", "6-review", "8-final", "9-memory")]
               + ["prompts/executor.md", "prompts/review.md"])
# Фактический размер после переноса (окончания строк LF) + 5 %; до переноса было 191 540 байт.
NORMAL_PATH_LIMIT = 193114

# Файл-получатель -> основной файл фазы, который обязан на него ссылаться.
EXTRACTED = {"4-plan-strict.md": "4-plan.md", "4-plan-opus.md": "4-plan.md",
             "5-strict.md": "5-subagents.md", "5-sequential-host.md": "5-subagents.md"}

# (файл, sha256 строки, её начало): строки, вынесенные из 4-plan.md и 5-subagents.md версии до таска.
MOVED_LINES = [
    ('4-plan-strict.md', '3fccfb9a2a01ed1b61bd27ca5876ba2c2307c17464df9c6ef0771f2910334849', '- The applied route is an authorized **c'),
    ('4-plan-strict.md', 'beb00227264636af196b42ed906a1f7d32044aa21d977ddc6c0263216b21385c', '## Strict Claude Code run — register the'),
    ('4-plan-strict.md', '481fe8d04dd9bfc52886d8b4dcb787835253a84831b5a0fb2755cf71120fadfc', 'Claude Code reads `.claude/agents/` and '),
    ('4-plan-strict.md', '262b67450225970ae7b753b462d3455535070914cf3c23591b34afa8a3755aec', '1. Write `.autopilot/model-capabilities.'),
    ('4-plan-strict.md', 'f530a94a099fc52339e8c5087f1bb0086f052dd4f54c9f6ee79be0203a9be0e4', '2. Both hooks: `python3 .autopilot/claud'),
    ('4-plan-strict.md', '5be85912698963684d69165367f27753447639d791336e6ee288f74eafb99506', '3. No new commit — `.claude/` and the ro'),
    ('4-plan-strict.md', '097d58871e0004599b600ad850f1de1b1020f784001444c3a50ea072b66f7e69', '   «Агенты сборки зарегистрированы, но C'),
    ('4-plan-strict.md', '34f5cb87527f8f7fbd6e6e95091c9c200a35efe0c923d2decd742b99983533bf', 'In every mode, full included, this is a '),
    ('4-plan-opus.md', '3de380f291b48124030e884739a66e380db59cce923fd7c7491f7a6f137ab4d7', "- **Opus is the user's call, never the r"),
    ('5-sequential-host.md', '650c2562b8da4fb859a16e8f1f6485c2eb197d1aca66bc9885e48d70a0df391e', '**Explicit R03 exception when native nam'),
    ('5-strict.md', 'be79651ddd63d3c16ad44043391bb29bc64b3410734b692344a16b162f43d1ec', '**Strict isolated test evidence (mandato'),
    ('5-strict.md', '6d63f75cfb3c3581b973d0763a3f733a859c4a2a415158c3cbd4a92740e3200c', '**Provider-neutral model routing (mandat'),
    ('5-strict.md', '5420b10aba0d996cd6f488c6da314440eb178eb7f2d1550b9b5a40c7c5b3a9f9', '**Bounded safe host controller (availabl'),
    ('5-strict.md', '6268e2f49752c6af482a0c88c96da4c9332a832f766f85f30f69367f0af22ff3', '**Isolated checkout lifecycle (opt-in, e'),
]


def read(*parts):
    with open(os.path.join(SKILL, *parts), "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def line_hashes(*parts):
    return {hashlib.sha256(x.encode()).hexdigest() for x in read(*parts).decode("utf-8").split("\n")}


class TextSplit(unittest.TestCase):
    def test_every_moved_line_is_verbatim_in_its_new_file(self):
        found = {n: line_hashes("phases", n) for n in EXTRACTED}
        for name, digest, start in MOVED_LINES:
            self.assertIn(digest, found[name], "%s: строка «%s…» потеряна или изменена" % (name, start))

    def test_moved_lines_are_gone_from_the_normal_path(self):
        found = {n: line_hashes("phases", n) for n in set(EXTRACTED.values())}
        for name, digest, start in MOVED_LINES:
            self.assertNotIn(digest, found[EXTRACTED[name]], "%s осталась в %s" % (start, EXTRACTED[name]))

    def test_each_extracted_file_is_named_by_its_phase_and_the_skill_table(self):
        table = read("SKILL.md").decode("utf-8")
        for name, owner in EXTRACTED.items():
            self.assertIn(name, read("phases", owner).decode("utf-8"), owner)
            self.assertIn("phases/" + name, table, "SKILL.md")

    def test_normal_path_stays_under_its_size_limit(self):
        total = sum(len(read(*n.split("/"))) for n in NORMAL_PATH)
        self.assertLessEqual(total, NORMAL_PATH_LIMIT, "обычный путь %d байт, порог %d" % (total, NORMAL_PATH_LIMIT))


if __name__ == "__main__":
    unittest.main()
