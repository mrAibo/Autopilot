#!/usr/bin/env python3
"""Discover actual account-visible Codex model/effort pairs (no model calls).

Codex desktop and CLI can have different sessions/catalogs. This file only
advertises the account-visible CLI selection for the current local client;
it does NOT attest the model actually used by the inference service.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from codex_dispatch import choose_binary

EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
MODEL_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{1,99}")


class CatalogError(ValueError):
    pass


def parse_catalog(raw):
    try:
        catalog = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise CatalogError("Codex returned invalid catalog JSON") from exc
    models = catalog.get("models") if isinstance(catalog, dict) else None
    if not isinstance(models, list) or not models:
        raise CatalogError("Resolved Codex catalog is missing or empty")
    result = {}
    for model in models:
        if not isinstance(model, dict):
            continue
        name = model.get("slug")
        if not isinstance(name, str) or not MODEL_ID.fullmatch(name):
            continue
        levels = model.get("supported_reasoning_levels") or []
        if not isinstance(levels, list):
            continue
        efforts = sorted({entry.get("effort") for entry in levels
                         if isinstance(entry, dict) and entry.get("effort") in EFFORTS})
        if efforts:
            result[name] = efforts
    if not result:
        raise CatalogError("Resolved catalog has no usable model/effort pairs")
    return result


def discover(exe, timeout=30):
    if not 5 <= timeout <= 60:
        raise CatalogError("Timeout must be between 5 and 60 seconds")
    # No '--bundled': only the resolved account catalog may authorize a route.
    proc = subprocess.run([exe, "debug", "models"], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if proc.returncode != 0:
        raise CatalogError("Could not retrieve account-visible Codex model catalog")
    return parse_catalog(proc.stdout)


def save_capabilities(root, models, binary, overwrite=False):
    root = Path(root).resolve()
    ap = root / ".autopilot"
    if not ap.is_dir():
        raise CatalogError("Initialize Autopilot first; .autopilot/ must exist")
    dest = ap / "model-capabilities.json"
    if dest.is_symlink():
        raise CatalogError("Refusing capability file symlink")
    if dest.exists() and not overwrite:
        raise CatalogError("Capabilities file exists; pass --overwrite after reviewing")
    if dest.exists():
        try:
            old = json.loads(dest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise CatalogError("Existing capabilities are not readable JSON")
        if old.get("provider") not in (None, "openai"):
            raise CatalogError("Refusing to overwrite another provider's capabilities")
    payload = {"provider": "openai", "model_selection": True,
               "models": models, "source": "codex-cli-resolved-catalog",
               "verified_execution": False,
               "retrieved_at": datetime.now(timezone.utc).isoformat(),
               "client_path": str(binary)}
    temp = dest.with_suffix(".json.tmp")
    try:
        with temp.open("x", encoding="utf-8", newline="\n") as writer:
            json.dump(payload, writer, ensure_ascii=False, indent=2)
            writer.write("\n")
        os.replace(temp, dest)
    finally:
        if temp.exists():
            temp.unlink()
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--codex-exe", type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--write", action="store_true",
                        help="Write discovered catalog into .autopilot/model-capabilities.json")
    parser.add_argument("--overwrite", action="store_true",
                        help="Permit refreshing an existing OpenAI capability catalog")
    args = parser.parse_args(argv)
    try:
        exe = choose_binary(args.codex_exe)
        models = discover(exe, args.timeout)
        result = {"status": "ready", "source": "codex-cli-resolved-catalog",
                  "model_selection": True, "verified_execution": False,
                  "models": models}
        if args.write:
            save_capabilities(args.root, models, exe, args.overwrite)
            result["saved"] = ".autopilot/model-capabilities.json"
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (CatalogError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)[:250]},
                         ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
