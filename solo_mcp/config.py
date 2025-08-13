from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SoloConfig:
    root: Path
    ai_memory_dir: Path
    enable_vector_search: bool = False
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_context_tokens: int = 8000
    # simple credit counter
    credits_path: Path | None = None

    @staticmethod
    def load(
        root: Path | None = None, enable_vector: bool | None = None
    ) -> "SoloConfig":
        base = Path(root or Path.cwd()).resolve()
        mem = base / ".ai_memory"
        mem.mkdir(exist_ok=True)
        credits = mem / "credits.json"
        return SoloConfig(
            root=base,
            ai_memory_dir=mem,
            enable_vector_search=(
                bool(enable_vector) if enable_vector is not None else False
            ),
            credits_path=credits,
        )
