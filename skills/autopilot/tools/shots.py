#!/usr/bin/env python3
"""Прототип R28a (за флагом AUTOPILOT_BLIND_SHOTS=1, docs/adr/0030): снимок страницы в headless Chrome/Edge.

`shots.py --url URL --out DIR [--width N --height N]`; код 0 — файлы записаны, пути по строке на файл;
код 2 — нет Chrome/Edge (строка причины в stderr) или не вышло снять. Только стандартная библиотека.
`--url` может быть путём к файлу или адресом; для папки со статикой `serve_dir` поднимает сервер на свободном порту.
"""
import argparse
import functools
import http.server
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import threading


def find_browser():
    """Chrome/Chromium/Edge из PATH, на Windows ещё из обычных мест установки; нет — None."""
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    if os.name == "nt":
        for variable, relative in (("PROGRAMFILES", "Google/Chrome/Application/chrome.exe"),
                                   ("PROGRAMFILES", "Microsoft/Edge/Application/msedge.exe"),
                                   ("PROGRAMFILES(X86)", "Microsoft/Edge/Application/msedge.exe"),
                                   ("LOCALAPPDATA", "Google/Chrome/Application/chrome.exe")):
            base = os.getenv(variable)
            if base and (Path(base) / relative).is_file():
                return str(Path(base) / relative)
    return None


def free_port():
    """Свободный порт на 127.0.0.1 (ядро выбирает сам; порт может занять другой процесс до bind — узкое окно)."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve_dir(directory):
    """Статика из `directory` на свободном порту; возвращает (сервер, порт). Остановить: server.shutdown()."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    handler.log_message = lambda *a, **k: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", free_port()), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def parse_args(argv):
    p = argparse.ArgumentParser(prog="shots.py", description=__doc__.splitlines()[0])
    p.add_argument("--url", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--width", type=int, default=1440)
    p.add_argument("--height", type=int, default=2000)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    browser = find_browser()
    if not browser:
        print("нет Chrome/Edge: скриншоты не сняты", file=sys.stderr)
        return 2
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    url = args.url
    if "://" not in url:
        if not Path(url).is_file():
            print("нет файла: " + url, file=sys.stderr)
            return 2
        url = Path(url).resolve().as_uri()
    png = out / ("shot-%dx%d.png" % (args.width, args.height))
    done = subprocess.run([browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                           "--hide-scrollbars", "--virtual-time-budget=2000",
                           "--window-size=%d,%d" % (args.width, args.height), "--screenshot=" + str(png), url],
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    if done.returncode or not png.is_file() or png.stat().st_size < 1000:
        print("снимок не вышел: " + done.stderr[-300:], file=sys.stderr)
        return 2
    print(png)
    return 0


if __name__ == "__main__":
    sys.exit(main())
