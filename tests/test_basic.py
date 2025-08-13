import json
from pathlib import Path

from solo_mcp.config import SoloConfig
from solo_mcp.server import SoloServer


def make_server(tmp_path: Path) -> SoloServer:
    cfg = SoloConfig.load(root=tmp_path)
    srv = SoloServer(cfg)
    return srv


def test_fs_and_memory(tmp_path: Path):
    srv = make_server(tmp_path)
    # write and read
    r = srv.fs.safe_write("a.txt", "hello")
    assert Path(r["path"]).exists()
    r2 = srv.fs.read("a.txt")
    assert r2["content"] == "hello"

    # memory
    srv.memory.store("test data", context={"key": "k", "data": {"a": 1}})
    result = srv.memory.load("test data")
    assert len(result) > 0 and result[0]["context"]["data"]["a"] == 1


def test_index_and_search(tmp_path: Path):
    srv = make_server(tmp_path)
    srv.fs.safe_write("code.py", "def add(a, b):\n    return a+b\n")
    import asyncio

    asyncio.run(srv.index.build())
    res = asyncio.run(srv.index.search("add a b", k=5))
    assert any("code.py" in h["path"] for h in res["hits"])
