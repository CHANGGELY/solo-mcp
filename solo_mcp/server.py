from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
import time

from .config import SoloConfig
from .tools.credits import CreditsManager
from .tools.fs import FsTool
from .tools.index import IndexTool
from .tools.memory import MemoryTool
from .tools.context import ContextTool
from .tools.roles import RolesTool
from .tools.orchestrator import OrchestratorTool
from .tools.proc import ProcTool

# Placeholder MCP server shim to expose tools as functions callable via MCP.
# To keep the codebase minimal and stable, we implement a lightweight async RPC loop
# and leave official MCP server integration as a thin layer to be expanded later.


class SoloServer:
    def __init__(self, config: SoloConfig):
        self.config = config
        self.credits = CreditsManager(config)
        self.fs = FsTool(config)
        self.memory = MemoryTool(config)
        self.index = IndexTool(config)
        self.context = ContextTool(config)
        self.roles = RolesTool(config)
        self.orchestrator = OrchestratorTool(config)
        self.proc = ProcTool(config)
        self.logs_dir = self.config.ai_memory_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.events_path = self.logs_dir / "events.jsonl"

    def _log_event(
        self,
        tool: str,
        params: dict[str, Any],
        start: float,
        end: float,
        ok: bool,
        result_size: int,
        error: str | None,
    ) -> None:
        entry = {
            "ts": time.time(),
            "tool": tool,
            "latency_ms": (end - start) * 1000.0,
            "ok": ok,
            "result_size": result_size,
            "error": error,
            "params_keys": sorted(list(params.keys())) if params else [],
        }
        try:
            with self.events_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def get_statistics(self, limit: int = 200) -> dict[str, Any]:
        if not self.events_path.exists():
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "by_tool": {},
                "recent": [],
            }
        lines = self.events_path.read_text(encoding="utf-8").splitlines()
        if not lines:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "by_tool": {},
                "recent": [],
            }
        tail = lines[-limit:]
        events: list[dict[str, Any]] = []
        for line in tail:
            try:
                events.append(json.loads(line))
            except Exception:
                continue
        total = len(events)
        success = sum(1 for e in events if e.get("ok"))
        failed = total - success
        success_rate = (success / total) * 100.0 if total else 0.0
        latencies = [float(e.get("latency_ms", 0.0)) for e in events]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        p95 = 0.0
        if latencies:
            s = sorted(latencies)
            idx = max(0, min(len(s) - 1, int(round(0.95 * (len(s) - 1)))))
            p95 = s[idx]
        by_tool: dict[str, int] = {}
        for e in events:
            t = str(e.get("tool", ""))
            by_tool[t] = by_tool.get(t, 0) + 1
        recent = [
            {
                "tool": e.get("tool"),
                "ok": e.get("ok"),
                "latency_ms": e.get("latency_ms"),
                "result_size": e.get("result_size"),
                "error": e.get("error"),
            }
            for e in events[-10:]
        ]
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": success_rate,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": p95,
            "by_tool": by_tool,
            "recent": recent,
        }

    async def handle(self, request: dict[str, Any]) -> dict[str, Any]:
        tool = request.get("tool")
        params = request.get("params", {})
        # credit check (lightweight)
        if tool not in {"credits.get", "credits.add"}:
            ok = self.credits.consume(1)
            if not ok:
                return {"error": "INSUFFICIENT_CREDITS"}
        start = time.perf_counter()
        try:
            if tool == "fs.read":
                ret = {"result": self.fs.read(params["path"])}
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(ret["result"], ensure_ascii=False)), None)
                return ret
            if tool == "fs.write":
                ret = {"result": self.fs.safe_write(params["path"], params["content"])}
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(ret["result"], ensure_ascii=False)), None)
                return ret
            if tool == "fs.list":
                ret = {"result": self.fs.list_dir(params.get("path"))}
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(ret["result"], ensure_ascii=False)), None)
                return ret
            if tool == "memory.store":
                ret = {
                    "result": await self.memory.store(
                        params.get("key"), params.get("data")
                    )
                }
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(ret["result"], ensure_ascii=False)), None)
                return ret
            if tool == "memory.load":
                res = await self.memory.load(params.get("key"))
                ret = {"result": res}
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(res, ensure_ascii=False)), None)
                return ret
            if tool == "memory.summarize":
                res = await self.memory.summarize(params.get("key"))
                ret = {"result": res}
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(res, ensure_ascii=False)), None)
                return ret
            if tool == "index.build":
                res = await self.index.build()
                ret = {"result": res}
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(res, ensure_ascii=False)), None)
                return ret
            if tool == "index.search":
                res = await self.index.search(
                    params.get("query"), k=params.get("k", 10)
                )
                ret = {
                    "result": await self.index.search(
                        params.get("query"), k=params.get("k", 10)
                    )
                }
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(res, ensure_ascii=False)), None)
                return ret
            if tool == "context.collect":
                res = await self.context.collect(
                    params.get("query"), limit=params.get("limit", 8000)
                )
                ret = {
                    "result": await self.context.collect(
                        params.get("query"), limit=params.get("limit", 8000)
                    )
                }
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(res, ensure_ascii=False)), None)
                return ret
            if tool == "roles.evaluate":
                res = self.roles.evaluate(
                    params.get("goal"), params.get("stack", [])
                )
                ret = {
                    "result": self.roles.evaluate(
                        params.get("goal"), params.get("stack", [])
                    )
                }
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(res, ensure_ascii=False)), None)
                return ret
            if tool == "orchestrator.run_round":
                res = await self.orchestrator.run_round(
                    params.get("mode", "collab"), params.get("state", {})
                )
                ret = {
                    "result": await self.orchestrator.run_round(
                        params.get("mode", "collab"), params.get("state", {})
                    )
                }
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(res, ensure_ascii=False)), None)
                return ret
            if tool == "proc.exec":
                res = await self.proc.exec(params.get("command"))
                ret = {"result": res}
                self._log_event(tool, params, start, time.perf_counter(), True, len(json.dumps(res, ensure_ascii=False)), None)
                return ret
            if tool == "credits.get":
                res = self.credits.get_balance()
                ret = {"result": res}
                self._log_event(tool, params, start, time.perf_counter(), True, len(str(res)), None)
                return ret
            if tool == "credits.add":
                res = self.credits.add(params.get("amount", 0))
                ret = {"result": res}
                self._log_event(tool, params, start, time.perf_counter(), True, len(str(res)), None)
                return ret
        except Exception as e:
            self._log_event(tool or "", params, start, time.perf_counter(), False, 0, str(e))
            return {"error": str(e)}
        self._log_event(tool or "", params, start, time.perf_counter(), False, 0, "Unknown tool")
        return {"error": f"Unknown tool: {tool}"}


async def main() -> None:
    config = SoloConfig.load()
    server = SoloServer(config)
    # Very simple stdin/stdout JSON-RPC like loop to be MCP-compatible via a shim
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, input)
        if not line:
            continue
        try:
            request = json.loads(line)
        except Exception:
            print(json.dumps({"error": "INVALID_JSON"}))
            continue
        resp = await server.handle(request)
        print(json.dumps(resp, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
