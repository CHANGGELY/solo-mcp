from __future__ import annotations

import asyncio
from typing import Any

from ..config import SoloConfig


class ProcTool:
    def __init__(self, config: SoloConfig):
        self.config = config

    async def exec(self, command: str | None) -> dict[str, Any]:
        if not command:
            return {"ok": False, "error": "EMPTY_COMMAND"}
        # PowerShell-aware execution; use ; to chain
        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=str(self.config.root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        out, _ = await proc.communicate()
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "output": out.decode("utf-8", errors="ignore"),
        }
