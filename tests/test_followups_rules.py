"""Доделки после аудита (R04): `finish --by-user` сдаёт «с оговорками», но строки манифеста не меняет."""

import os
import re
import unittest

import test_ap
from test_ap_audit import harness


def rows(text):
    return dict(re.findall(r"^\| (\w+) \|.*?\| ([\w-]+) \|", text, re.M))


class ByUserKeepsRows(unittest.TestCase):
    def test_finish_by_user_with_an_open_row_leaves_the_manifest_row_as_it_was(self):
        h = harness(self)
        h.ready_to_finish()
        path = os.path.join(h.dir, "manifest.md")
        text = test_ap.read(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace("| R02 | «складывает в таблицу» | done |", "| R02 | «складывает в таблицу» | in-spec |"))
        before = test_ap.read(path)
        self.assertEqual(rows(before)["R02"], "in-spec")
        code, out = h.ap("finish", "--result", "итог", "--by-user", "сдавай как есть")
        self.assertEqual(code, 0, out)
        landed = h.state()["landedWith"]
        self.assertEqual(landed["byUser"], "сдавай как есть")
        self.assertTrue(any("требования не закрыты: R02" in p for p in landed["problems"]), landed)
        after = test_ap.read(os.path.join(h.a, h.state()["dir"], "manifest.md"))   # папка прогона переименована
        # любая команда сверяет открытую строку с таском (in-spec -> in-ticket); finish её не закрывает и не снимает
        self.assertIn(rows(after)["R02"], ("in-spec", "in-ticket"))
        self.assertEqual({k: v for k, v in rows(after).items() if k != "R02"},
                         {k: v for k, v in rows(before).items() if k != "R02"})


if __name__ == "__main__":
    unittest.main()
