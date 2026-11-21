"""Уроки (R06): формы абсолютных путей и параллельная запись под state.lock."""
import os
import unittest
from concurrent.futures import ThreadPoolExecutor

from test_speed_lessons import Cli

import lessons  # sys.path уже задан test_speed_lessons

BS = chr(92)
FORMS = {"тильда": "лежит в ~/proj", "слеш вперёд": "лежит в C:/work/x",
         "UNC": "лежит в " + BS * 2 + "server" + BS + "share" + BS + "x",
         "folders": "см. /var/fol" "ders/ab/x",
         "Users": "см. /Us" "ers/a/b", "home": "см. /ho" "me/a/b", "диск": "C:" + BS + "Users" + BS + "a"}


class PathForms(unittest.TestCase):
    def test_every_absolute_form_is_refused(self):
        for name, text in FORMS.items():
            with self.subTest(name):
                self.assertEqual(lessons.check_text(text), "абсолютный путь вне проекта")

    def test_project_relative_text_passes(self):
        self.assertIsNone(lessons.check_text("правь tests/x.py и ~ как знак, а не путь a/b"))


class RoutesPass(unittest.TestCase):
    def test_web_routes_are_not_paths(self):
        for text in ("GET /root/ route отдаёт 200", "redirect to /root/dashboard после входа",
                     "роут /private/ закрыт логином, см. /private/area"):
            with self.subTest(text):
                self.assertIsNone(lessons.check_text(text))


class ParallelAdd(Cli):
    def test_two_parallel_adds_keep_both_lines(self):
        self.init()
        with ThreadPoolExecutor(2) as pool:
            codes = list(pool.map(lambda t: self.ap("lessons", "add", t, "--no-serve")[0], ["урок-раз", "урок-два"]))
        self.assertEqual(codes, [0, 0])
        text = open(os.path.join(self.a, "lessons.md"), encoding="utf-8").read()
        self.assertEqual(sorted(x.split(" — ", 1)[1] for x in text.splitlines()), ["урок-два", "урок-раз"])
        seen = open(os.path.join(self.a, "lessons.md.seen"), encoding="utf-8").read().split()
        self.assertEqual(len(seen), 2)


if __name__ == "__main__":
    unittest.main()
