"""FalkorDB is the sole source of connected context and decisions."""
from __future__ import annotations

import atexit
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import threading
import time
import redis

from falkordb import FalkorDB

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/scenario.json").read_text())
LOCK = threading.RLock()
_db = None
_process = None
_initialized: set[str] = set()


def connection():
    global _db, _process
    with LOCK:
        if _db is not None:
            _db.connection.ping()
            return _db
        url = os.environ.get("FALKORDB_URL")
        if url:
            _db = FalkorDB.from_url(url, socket_timeout=8, socket_connect_timeout=8)
        else:
            # The official Lite wheel provides the actual Redis server and
            # FalkorDB module. Use loopback TCP, not Lite's Unix socket wrapper.
            import redislite

            binaries = Path(redislite.__file__).parent / "bin"
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            folder = Path(tempfile.mkdtemp(prefix="lotline-"))
            log = (folder / "server.log").open("w")
            _process = subprocess.Popen(
                [str(binaries / "redis-server"), "--loadmodule", str(binaries / "falkordb.so"),
                 "THREAD_COUNT", "2", "--bind", "127.0.0.1", "--port", str(port),
                 "--dir", str(folder), "--save", "", "--appendonly", "no",
                 "--protected-mode", "yes"],
                stdout=log, stderr=log,
            )
            client = redis.Redis(host="127.0.0.1", port=port, socket_timeout=1)
            for _ in range(50):
                try:
                    client.ping()
                    _db = FalkorDB(host="127.0.0.1", port=port, socket_timeout=8)
                    break
                except Exception:
                    if _process.poll() is not None:
                        raise RuntimeError("Embedded FalkorDB did not start. Use a supported Linux environment or FALKORDB_URL.")
                    time.sleep(0.1)
            else:
                raise RuntimeError("FalkorDB startup timed out.")
        _db.connection.ping()
        return _db


def close():
    if _process and _process.poll() is None:
        _process.terminate()


atexit.register(close)


def graph_for(workspace: str):
    if not re.fullmatch(r"[a-f0-9]{32}", workspace):
        raise ValueError("Invalid workspace")
    name = f"lotline_{workspace}"
    with LOCK:
        graph = connection().select_graph(name)
        if name not in _initialized:
            existing = graph.ro_query("MATCH (m:Meta {id: 'dataset'}) RETURN m.version").result_set if connection().connection.exists(name) else []
            if not existing:
                seed(graph)
            _initialized.add(name)
        return graph


def seed(graph):
    for item in DATA["nodes"]:
        kind = item["kind"]
        # Labels and relationship types come only from our checked-in fixture.
        label = "Document" if kind == "Document" else "Shipment" if kind == "Shipment" else "Site" if kind == "Site" else "Supplier" if kind == "Supplier" else "Lot"
        graph.query(f"CREATE (n:{label}) SET n = $props", {"props": item})
    for item in DATA["edges"]:
        graph.query(
            f"MATCH (a {{id:$source}}), (b {{id:$target}}) CREATE (a)-[r:{item['kind']}]->(b) SET r = $props",
            {"source": item["source"], "target": item["target"], "props": item},
        )
    graph.query("CREATE (:Meta {id:'dataset', version:$version, revision:0})", {"version": DATA["version"]})


def rows(graph, query: str, params: dict | None = None, write=False):
    result = (graph.query if write else graph.ro_query)(query, params or {}, timeout=3000)
    headers = [header[1] for header in result.header]
    return [dict(zip(headers, row)) for row in result.result_set]


def revision(graph) -> int:
    return rows(graph, "MATCH (m:Meta {id:'dataset'}) RETURN m.revision AS revision")[0]["revision"]


def snapshot(graph):
    ns = rows(graph, "MATCH (n) WHERE n.kind IS NOT NULL RETURN properties(n) AS node")
    es = rows(graph, "MATCH (a)-[r]->(b) WHERE a.kind IS NOT NULL AND b.kind IS NOT NULL RETURN properties(r) AS edge")
    return {"nodes": [r["node"] for r in ns], "edges": [r["edge"] for r in es]}
