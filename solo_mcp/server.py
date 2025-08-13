from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

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
        self.context = ContextTool(config, self.index, self.memory)
        self.roles = RolesTool(config)
        self.orchestrator = OrchestratorTool(config)
        self.proc = ProcTool(config)

    async def handle(self, request: dict[str, Any]) -> dict[str, Any]:
        tool = request.get("tool")
        params = request.get("params", {})
        # credit check (lightweight)
        if tool not in {"credits.get", "credits.add"}:
            ok = self.credits.consume(1)
            if not ok:
                return {"error": "INSUFFICIENT_CREDITS"}
        try:
            if tool == "fs.read":
                return {"result": self.fs.read(params["path"])}
            if tool == "fs.write":
                return {"result": self.fs.safe_write(params["path"], params["content"])}
            if tool == "fs.list":
                return {"result": self.fs.list_dir(params.get("path"))}
            if tool == "memory.store":
                return {
                    "result": await self.memory.store(
                        params.get("key"), params.get("data")
                    )
                }
            if tool == "memory.load":
                return {"result": await self.memory.load(params.get("key"))}
            if tool == "memory.summarize":
                return {"result": await self.memory.summarize(params.get("key"))}
            if tool == "index.build":
                return {"result": await self.index.build()}
            if tool == "index.search":
                return {
                    "result": await self.index.search(
                        params.get("query"), k=params.get("k", 10)
                    )
                }
            if tool == "context.collect":
                return {
                    "result": await self.context.collect(
                        params.get("query"), limit=params.get("limit", 8000)
                    )
                }
            if tool == "roles.evaluate":
                return {
                    "result": self.roles.evaluate(
                        params.get("goal"), params.get("stack", [])
                    )
                }
            if tool == "orchestrator.run_round":
                return {
                    "result": await self.orchestrator.run_round(
                        params.get("mode", "collab"), params.get("state", {})
                    )
                }
            if tool == "proc.exec":
                return {"result": await self.proc.exec(params.get("command"))}
            if tool == "credits.get":
                return {"result": self.credits.get_balance()}
            if tool == "credits.add":
                return {"result": self.credits.add(params.get("amount", 0))}
        except Exception as e:
            return {"error": str(e)}
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
