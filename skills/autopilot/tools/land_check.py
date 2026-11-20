"""Проверка перед влитием таска: уход цели, чужие коммиты в зоне, соседние таски. Репозиторий не меняет."""
import os
import subprocess


def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def head(root):
    out = _git(root, "rev-parse", "HEAD")
    return out.strip() if out else None


def _covers(paths, path):
    return any(path == p.rstrip("/") or path.startswith(p.rstrip("/") + "/") for p in paths)


def _norm(p):
    return os.path.normcase(os.path.realpath(p))


def _overlap(a, b):
    """Пути зон a и b, пересекающиеся как префиксы; пустой список, если зоны не пересекаются."""
    found = []
    for x in a:
        for y in b:
            xs, ys = x.rstrip("/") + "/", y.rstrip("/") + "/"
            if xs.startswith(ys) or ys.startswith(xs):
                found.append(x if len(x) >= len(y) else y)
    return found


def _own(subject, ticket, trailers=""):
    """Коммит этого таска: тема начинается с id (`T02:`, `T02 `, `F1:`) или трейлер `Autopilot-Ticket` с этим id."""
    words = subject.split(None, 1)
    first = words[0].rstrip(":") if words else ""
    tid = "T" + ticket if ticket[:1] != "F" else ticket
    return first == tid or ticket in [t.strip() for t in trailers.split(",")]


def _foreign_files(root, start_head, ticket):
    """Файлы (относительно root), тронутые после start_head коммитами не этого таска; merge — против первого родителя."""
    log = _git(root, "log", "--format=%H%x1f%P%x1f%s%x1f%(trailers:key=Autopilot-Ticket,valueonly,separator=%x2c)%x1e",
               "%s..HEAD" % start_head)
    found = set()
    for rec in (log or "").split("\x1e"):
        parts = rec.strip("\n").split("\x1f")
        if len(parts) < 4:
            continue
        sha, parents, subject, trailers = parts[0], parts[1].split(), parts[2], parts[3]
        if _own(subject, ticket, trailers.replace("\n", "")):
            continue
        if len(parents) > 1:
            names = _git(root, "diff", "--name-only", "-z", "--relative", sha + "^1", sha)
        else:
            names = _git(root, "show", "--name-only", "--format=", "-z", "--relative", sha)
        found.update(n for n in (names or "").split("\0") if n and not n.startswith(".autopilot/"))
    return found



def preflight(root, start_head, base_commit, zone, ticket, active_zones, files=None):
    """-> {"ahead", "foreign_files", "neighbors", "unsupported"}. Только чтение: rev-list, log, show.
    `files` — вливаемые файлы (пути проекта): с ними чужие коммиты и соседи считаются только по ним."""
    report = {"ahead": 0, "foreign_files": [], "neighbors": [], "unsupported": None}
    if _git(root, "rev-parse", "--show-toplevel") is None:
        report["unsupported"] = "не поддержано: git не отвечает, проверка перед влитием пропущена"
        return report
    zone = [z.replace("\\", "/") for z in zone]
    prefix = (_git(root, "rev-parse", "--show-prefix") or "").strip()      # проект в подпапке репозитория
    mine = None if files is None else {f.replace("\\", "/")[len(prefix):] if f.startswith(prefix) else f for f in files}
    count = _git(root, "rev-list", "--count", "%s..HEAD" % base_commit) if base_commit else None
    report["ahead"] = int(count) if count and count.strip().isdigit() else 0
    if start_head:
        touched = _foreign_files(root, start_head, ticket)
        report["foreign_files"] = sorted(f for f in touched if (f in mine if mine is not None else _covers(zone, f)))
    for other, zones in sorted((active_zones or {}).items()):
        if other == ticket:
            continue
        theirs = [z.replace("\\", "/") for z in zones]
        both = _overlap(zone, theirs) if mine is None else [f for f in mine if _covers(theirs, f)]
        if both:
            report["neighbors"].append({"ticket": other, "files": sorted(set(both))})
    return report


def problems(report, ticket="NN"):
    """Готовые отказы с командой «что делать»; пусто — можно вливать."""
    out = []
    if report.get("foreign_files"):
        out.append("после старта таска чужие коммиты тронули файлы зоны: %s. что делать: дождись, пока автор закончит, "
                   "и сверь файлы / влей без них — `ticket %s land --zone <путь без этих файлов>` / реши с пользователем"
                   % (", ".join(report["foreign_files"][:5]), ticket))
    for n in report.get("neighbors") or []:
        out.append("таск %s в работе и пишет в те же пути (%s). что делать: дождись его `ticket %s done`, "
                   "либо влей свой с `--zone` без общих путей / реши с пользователем"
                   % (n["ticket"], ", ".join(n["files"][:3]), n["ticket"]))
    return out


def tracked_files(root):
    """Отслеживаемые git файлы (для проверки «существующий тест»)."""
    out = _git(root, "ls-files", "-z")
    return set(n for n in (out or "").split("\0") if n)


def diff_text(root, files, untracked):
    """Дифф файлов таска против HEAD; новые (untracked) файлы — как добавленные строки. Индекс не трогает."""
    parts = []
    known = [f for f in files if f not in untracked]
    if known:
        parts.append(_git(root, "diff", "HEAD", "--", *known) or "")
    for f in untracked:
        try:
            with open(os.path.join(root, f), encoding="utf-8", errors="replace") as stream:
                parts.append("\n".join("+" + line for line in stream.read().splitlines()))
        except OSError:
            pass
    return "\n".join(parts)
