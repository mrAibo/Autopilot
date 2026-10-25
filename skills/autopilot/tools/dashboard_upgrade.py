#!/usr/bin/env python3
"""Safely refresh a project's copied Dashboard HTML without resetting its run.

The template belongs to the installed Autopilot skill. Project state.js is the
authority; no application source code or ticket ledger is modified.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile


class UpgradeError(ValueError):
    pass


ANCHOR = "/*STATE-BEGIN*/window.STATE=null;/*STATE-END*/"
SNAPSHOT = re.compile(r"/\*STATE-BEGIN\*/window\.STATE=(.*?);/\*STATE-END\*/", re.S)


def parse_project_state(data):
    if not data.startswith("window.STATE"):
        raise UpgradeError("Project state.js has an unexpected format")
    try:
        state = json.loads(data.split("=", 1)[1].strip().rstrip(";"))
    except (IndexError, ValueError) as exc:
        raise UpgradeError("Project state.js is not valid JSON") from exc
    if not isinstance(state, dict) or not isinstance(state.get("slug"), str):
        raise UpgradeError("Project state lacks a valid slug")
    return state


def prepare(project, template):
    root = Path(project).resolve()
    storage = root / ".autopilot"
    page = storage / "dashboard.html"
    state_path = storage / "state.js"
    if not storage.is_dir():
        raise UpgradeError("This project has no .autopilot folder")
    if page.is_symlink() or state_path.is_symlink():
        raise UpgradeError("Refusing symlinked project Dashboard/state")
    if not page.is_file() or not state_path.is_file():
        raise UpgradeError("Existing Dashboard and state.js are required")
    original = page.read_text(encoding="utf-8")
    found = SNAPSHOT.search(original)
    if not found or len(SNAPSHOT.findall(original)) != 1:
        raise UpgradeError("Existing Dashboard snapshot marker missing or ambiguous")
    try:
        old_state = json.loads(found.group(1))
    except ValueError as exc:
        raise UpgradeError("Existing Dashboard has invalid embedded snapshot") from exc
    current = parse_project_state(state_path.read_text(encoding="utf-8"))
    if (not isinstance(old_state, dict)
            or old_state.get("slug") != current["slug"]):
        raise UpgradeError("Dashboard belongs to a different project")
    source = Path(template)
    if not source.is_file():
        raise UpgradeError("Dashboard template was not found in skill installation")
    fresh = source.read_text(encoding="utf-8")
    if fresh.count(ANCHOR) != 1 or "cockpit-rail" not in fresh:
        raise UpgradeError("Skill template does not contain Dashboard 3.1")
    snapshot = json.dumps(current, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    output = fresh.replace(ANCHOR, "/*STATE-BEGIN*/window.STATE=" + snapshot + ";/*STATE-END*/")
    if output.count("/*STATE-BEGIN*/") != 1 or "cockpit-content" not in output:
        raise UpgradeError("Refreshed Dashboard failed snapshot validation")
    return page, original, output, current["slug"]


def upgrade(project, template, backup_dir=None, dry_run=False):
    page, original, content, slug = prepare(project, template)
    unchanged = content == original
    result = {"status": "unchanged" if unchanged else "would-upgrade" if dry_run else "upgraded",
              "project": slug, "dashboard": str(page), "backup": None}
    if dry_run or unchanged:
        return result
    folder = Path(backup_dir) if backup_dir else Path(tempfile.gettempdir()) / "autopilot-dashboard-backups"
    folder.mkdir(parents=True, exist_ok=True)
    if folder.is_symlink():
        raise UpgradeError("Backup folder must not be a symlink")
    digest = hashlib.sha256(original.encode("utf-8")).hexdigest()[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = folder / (re.sub(r"[^a-z0-9-]", "-", slug) + "-" + stamp + "-" + digest + ".html")
    with backup.open("x", encoding="utf-8", newline="\n") as saved:
        saved.write(original)
    result["backup"] = str(backup)
    # Fail closed if another process rewrote the Dashboard before replacement.
    if page.read_text(encoding="utf-8") != original:
        raise UpgradeError("Dashboard changed during upgrade; backup preserved")
    temporary = page.with_name("dashboard.html.new-" + digest)
    if temporary.exists() or temporary.is_symlink():
        raise UpgradeError("Temporary Dashboard file already exists")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, page)
    finally:
        if temporary.exists():
            temporary.unlink()
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".", help="Existing Autopilot project path")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--backup-dir", type=Path)
    args = p.parse_args(argv)
    template = Path(__file__).resolve().parents[1] / "phases" / "dashboard-template.html"
    try:
        result = upgrade(args.project, template, args.backup_dir, args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, UpgradeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
