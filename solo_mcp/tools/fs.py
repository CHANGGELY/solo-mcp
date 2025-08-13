from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from ..config import SoloConfig


class FsTool:
    def __init__(self, config: SoloConfig):
        self.config = config

    def _resolve(self, path: str | None) -> Path:
        base = self.config.root
        p = Path(path) if path else base
        if not p.is_absolute():
            p = base / p
        return p.resolve()

    def read(self, path: str) -> dict[str, Any]:
        p = self._resolve(path)
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(str(p))
        return {"path": str(p), "content": p.read_text(encoding="utf-8")}

    def list_dir(self, path: str | None = None) -> dict[str, Any]:
        p = self._resolve(path)
        if not p.exists() or not p.is_dir():
            raise NotADirectoryError(str(p))
        items = []
        for child in sorted(p.iterdir()):
            items.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "type": "dir" if child.is_dir() else "file",
                }
            )
        return {"path": str(p), "items": items}

    def safe_write(self, path: str, content: str) -> dict[str, Any]:
        p = self._resolve(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():
            # soft delete to .ai_memory/trash
            trash_dir = self.config.ai_memory_dir / "trash"
            trash_dir.mkdir(exist_ok=True)
            backup = trash_dir / f"{p.name}.bak"
            shutil.copy2(p, backup)
        p.write_text(content, encoding="utf-8")
        return {"path": str(p), "bytes": len(content.encode("utf-8"))}
