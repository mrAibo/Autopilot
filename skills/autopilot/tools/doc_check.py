"""`ap.py doc-check`: имена `ap.py <cmd>` и `--flag` из backticks в CHANGELOG (Unreleased) и ADR
должны существовать в ap.py. Только чтение; ловит только эти две формы имён, смысл слов не проверяет."""
import glob
import os
import re
import subprocess

SPAN = re.compile(r"`([^`\n]+)`")
CMD = re.compile(r"\bap\.py\s+([a-z][a-z0-9-]*)")
ABSENT = re.compile(r"(?<!\w)нет(?!\w)", re.I)
FOREIGN = re.compile(r"(?<!\w)git(?!\w)|(?<![\w.])(?!ap\.py)\w+\.py")
FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z0-9-]+)")
# ap.py: cmd == "x", cmd in ("a", "b"), opt.get("x"), opt["x"], "--x", докстринг `ap.py x`
K_CMD = re.compile(r"""\bcmd\s*==\s*["']([a-z][a-z0-9-]*)["']|\bap\.py\s+([a-z][a-z0-9-]*)""")
K_CMD_IN = re.compile(r"\bcmd\s+in\s*[(\[]([^)\]]*)[)\]]")
K_FLAG = re.compile(r"""opt(?:\.get)?[\[(]\s*["']([a-z][a-z0-9-]*)["']|["'](--[a-z][a-z0-9-]+)""")
K_FLAG_DOC = re.compile(r"(?<![\w-])--([a-z][a-z0-9-]+)")


def claimed(text):
    """Имена из backticks: `ap.py cmd` -> "ap.py cmd", `--flag` -> "--flag"."""
    out = set()
    lines = text.splitlines()
    for line in lines:
        if ABSENT.search(line):         # shortcut: строка со словом «нет» утверждает отсутствие — не проверяем
            continue
        foreign = FOREIGN.search(line)  # на строке чужая программа: её флаги не наши
        for span in SPAN.findall(line):
            out.update("ap.py " + m for m in CMD.findall(span))
            if "ap.py" in span or (span.startswith("--") and not foreign):
                out.update(FLAG.findall(span))
    if lines and ABSENT.search(lines[0]):   # заголовок «команды X нет»: X не заявлена и в остальном тексте
        out -= {"ap.py " + m for sp in SPAN.findall(lines[0]) for m in CMD.findall(sp)}
    return out


def known(ap_source):
    """(команды, флаги), которые знает исходник ap.py."""
    cmds = {a or b for a, b in K_CMD.findall(ap_source)}
    for grp in K_CMD_IN.findall(ap_source):
        cmds.update(re.findall(r"""["']([a-z][a-z0-9-]*)["']""", grp))
    flags = {"--" + a if a else b for a, b in K_FLAG.findall(ap_source)}
    flags.update("--" + f for f in K_FLAG_DOC.findall(ap_source))
    return cmds, flags


def _unreleased(text):
    m = re.search(r"^##\s*\[?Unreleased\]?.*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    return m.group(1) if m else ""


def changed_files(root, base):
    """Файлы, изменённые с base (коммиты и рабочая папка); нет base или git — None (значит все)."""
    if not base:
        return None
    try:
        r = subprocess.run(["git", "-C", root, "diff", "--name-only", base], capture_output=True, text=True)
        u = subprocess.run(["git", "-C", root, "ls-files", "-o", "--exclude-standard"], capture_output=True, text=True)
    except OSError:
        return None
    if r.returncode:
        return None
    return {x.strip().replace("\\", "/") for x in (r.stdout + u.stdout).splitlines() if x.strip()}


def run_files(root, base=None):
    """CHANGELOG.md и docs/adr/*.md, изменённые в прогоне (все, если base неизвестен)."""
    changed = changed_files(root, base)
    cand = ["CHANGELOG.md"] + sorted(
        os.path.relpath(p, root).replace("\\", "/") for p in glob.glob(os.path.join(glob.escape(root), "docs", "adr", "*.md")))
    return [f for f in cand if changed is None or f in changed]


def check(root, ap_path, files):
    """Строки расхождений `файл: ap.py <cmd> — такой команды нет` / `--flag — такого флага нет`."""
    with open(ap_path, encoding="utf-8") as f:
        cmds, flags = known(f.read())
    out = []
    for rel in files:
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        if os.path.basename(rel) == "CHANGELOG.md":
            text = _unreleased(text)
        for name in sorted(claimed(text)):
            if name.startswith("--"):
                if name not in flags:
                    out.append("%s: %s — такого флага нет" % (rel, name))
            elif name[len("ap.py "):] not in cmds:
                out.append("%s: %s — такой команды нет" % (rel, name))
    return out
