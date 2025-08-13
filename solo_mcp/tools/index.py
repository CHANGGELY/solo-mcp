from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import SoloConfig


@dataclass
class _Corpus:
    docs: list[list[str]]
    paths: list[str]


class _BM25Lite:
    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_freq: dict[str, int] = {}
        self.avgdl = sum(len(doc) for doc in corpus) / max(1, len(corpus))
        for doc in corpus:
            seen = set()
            for w in doc:
                if w in seen:
                    continue
                self.doc_freq[w] = self.doc_freq.get(w, 0) + 1
                seen.add(w)

    def _idf(self, term: str) -> float:
        import math

        n = len(self.corpus)
        df = self.doc_freq.get(term, 0) + 0.5
        return max(0.0, math.log((n - df + 0.5) / df))

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        scores: list[float] = []
        for doc in self.corpus:
            score = 0.0
            dl = len(doc)
            for q in query_tokens:
                tf = sum(1 for t in doc if t == q)
                if tf == 0:
                    continue
                idf = self._idf(q)
                denom = tf + self.k1 * (1 - self.b + self.b * dl / max(1, self.avgdl))
                score += idf * (tf * (self.k1 + 1)) / denom
            scores.append(score)
        return scores


class IndexTool:
    def __init__(self, config: SoloConfig):
        self.config = config
        self._bm25: _BM25Lite | None = None
        self._corpus: _Corpus | None = None

    def _iter_files(self) -> list[Path]:
        root = self.config.root
        files = []
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in {
                ".py",
                ".js",
                ".ts",
                ".json",
                ".md",
                ".txt",
                ".tsx",
                ".jsx",
            }:
                if str(p).startswith(str(self.config.ai_memory_dir)):
                    continue
                files.append(p)
        return files

    async def build(self) -> dict[str, Any]:
        files = self._iter_files()
        tokenized = []
        paths = []
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            tokens = [t for t in text.split() if t]
            tokenized.append(tokens)
            paths.append(str(p))
        if not tokenized:
            self._bm25 = None
            self._corpus = _Corpus([], [])
            return {"ok": True, "docs": 0}
        bm25 = _BM25Lite(tokenized)
        self._bm25 = bm25
        self._corpus = _Corpus(tokenized, paths)
        return {"ok": True, "docs": len(paths)}

    async def search(self, query: str | None, k: int = 10) -> dict[str, Any]:
        if not query:
            return {"ok": True, "hits": []}
        if not self._bm25 or not self._corpus:
            await self.build()
        if not self._bm25 or not self._corpus or not self._corpus.docs:
            return {"ok": True, "hits": []}
        tokens = [t for t in query.split() if t]
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k]
        hits = []
        for idx, score in ranked:
            path = self._corpus.paths[idx]
            try:
                preview = Path(path).read_text(encoding="utf-8", errors="ignore")[:500]
            except Exception:
                preview = ""
            hits.append({"path": path, "score": float(score), "preview": preview})
        return {"ok": True, "hits": hits}
