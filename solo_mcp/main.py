from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from . import __version__


def _print_version() -> None:
    print(f"solo-mcp {__version__}")


def _load_config(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(str(p))
    if p.suffix.lower() == ".json":
        import json

        return json.loads(p.read_text(encoding="utf-8"))
    if p.suffix.lower() in {".toml", ".tml"}:
        import tomllib

        return tomllib.loads(p.read_text(encoding="utf-8"))
    raise ValueError("Unsupported config format")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="solo-mcp")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--server", action="store_true")
    parser.add_argument("--mode", choices=["fastmcp", "shim"], default="fastmcp")
    parser.add_argument("--config")
    args = parser.parse_args(argv)

    if args.version and not args.server:
        _print_version()
        return 0

    cfg = {}
    try:
        cfg = _load_config(args.config)
    except Exception:
        cfg = {}

    if args.server:
        if args.mode == "fastmcp":
            from .mcp_server import run_server

            run_server()
            return 0
        if args.mode == "shim":
            from .server import main as shim_main

            asyncio.run(shim_main())
            return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
