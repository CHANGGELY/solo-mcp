from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..config import SoloConfig


DEFAULT_CREDITS = 100


@dataclass
class CreditsManager:
    config: SoloConfig

    def _path(self) -> Path:
        assert self.config.credits_path is not None
        return self.config.credits_path

    def _load(self) -> dict:
        p = self._path()
        if not p.exists():
            return {"balance": DEFAULT_CREDITS}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {"balance": DEFAULT_CREDITS}

    def _save(self, data: dict) -> None:
        p = self._path()
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_balance(self) -> dict:
        return self._load()

    def add(self, amount: int) -> dict:
        if amount <= 0:
            return self._load()
        data = self._load()
        data["balance"] = int(data.get("balance", 0)) + int(amount)
        self._save(data)
        return data

    def consume(self, amount: int) -> bool:
        if amount <= 0:
            return True
        data = self._load()
        bal = int(data.get("balance", 0))
        if bal < amount:
            return False
        data["balance"] = bal - amount
        self._save(data)
        return True
