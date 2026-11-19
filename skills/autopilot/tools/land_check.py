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


def preflight(root, start_head, base_commit, zone, ticket, active_zones):
    """-> {"ahead", "foreign_files", "neighbors", "unsupported"}. Только чтение: rev-list, diff --name-only."""
    report = {"ahead": 0, "foreign_files": [], "neighbors": [], "unsupported": None}
    top = _git(root, "rev-parse", "--show-toplevel")
    if top is None or _norm(top.strip()) != _norm(root):
        report["unsupported"] = "не поддержано: проект не в корне репозитория, проверка перед влитием пропущена"
        return report
    zone = [z.replace("\\", "/") for z in zone]
    count = _git(root, "rev-list", "--count", "%s..HEAD" % base_commit) if base_commit else None
    report["ahead"] = int(count) if count and count.strip().isdigit() else 0
    if start_head:
        names = _git(root, "diff", "--name-only", "-z", start_head, "HEAD")
        files = [n for n in (names or "").split("\0") if n and not n.startswith(".autopilot/")]
        report["foreign_files"] = sorted(f for f in files if _covers(zone, f))
    for other, zones in sorted((active_zones or {}).items()):
        if other == ticket:
            continue
        both = _overlap(zone, [z.replace("\\", "/") for z in zones])
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
