from __future__ import annotations

from collections import defaultdict, deque
import hashlib
import hmac
import os
import re
import secrets
import time
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from backend import actions
from backend.agent import select_tool
from backend.database import DATA, ROOT, graph_for, snapshot
from backend.tools import compare_depth, decision_history, investigate

app = FastAPI(title="Lotline", description="Evidence-first recall investigation, synthetic sandbox", version="1.0.0")
_requests = defaultdict(deque)


class InvestigateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    question: str = Field(min_length=1, max_length=1200)
    lot_id: str = Field(min_length=1, max_length=64)
    depth: int = Field(default=6, ge=1, le=6)
    use_agent: bool = True


class PlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    lot_id: str = Field(min_length=1, max_length=64)


class CommitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    token: str = Field(min_length=10, max_length=6000)
    approved: bool


def csrf(workspace: str):
    return hmac.new(actions.SECRET, ("csrf:" + workspace).encode(), hashlib.sha256).hexdigest()


@app.middleware("http")
async def security_boundary(request: Request, call_next):
    if not request.url.path.startswith("/api/"):
        return await call_next(request)
    new = False
    workspace = None
    cookie = request.cookies.get("lotline_session")
    if cookie:
        try:
            payload = actions.verify(cookie)
            if payload.get("expires", 0) > time.time():
                workspace = payload.get("workspace")
        except actions.ActionError:
            pass
    if not workspace:
        if request.method != "GET":
            return JSONResponse({"detail": "Your workspace session expired. Reload the page before trying again."}, 401)
        workspace = secrets.token_hex(16)
        new = True
    request.state.workspace = workspace
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin and urlparse(origin).netloc != request.headers.get("host"):
            return JSONResponse({"detail": "Cross-origin changes are not allowed."}, 403)
        if not secrets.compare_digest(request.headers.get("x-lotline-csrf", ""), csrf(workspace)):
            return JSONResponse({"detail": "Refresh your workspace before making this change."}, 403)
        if len(await request.body()) > 8000:
            return JSONResponse({"detail": "Request is too large."}, 413)
        bucket = _requests[workspace]
        now = time.monotonic()
        while bucket and bucket[0] < now - 60:
            bucket.popleft()
        if len(bucket) >= 24:
            return JSONResponse({"detail": "Please wait a minute before running more requests."}, 429)
        bucket.append(now)
    try:
        response = await call_next(request)
    except Exception:
        response = JSONResponse({"detail": "The graph service is unavailable. Retry after it recovers. No result was inferred."}, 503)
    response.headers.update({"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin", "X-Frame-Options": "DENY"})
    if new:
        response.set_cookie("lotline_session", actions.sign({"workspace": workspace, "expires": int(time.time()) + 86400}), max_age=86400, httponly=True, secure=request.url.scheme == "https", samesite="strict", path="/")
    return response


@app.exception_handler(actions.ActionError)
async def action_error(request: Request, error: actions.ActionError):
    return JSONResponse({"detail": error.message}, error.status)


@app.get("/api/health")
def health(request: Request):
    graph = graph_for(request.state.workspace)
    result = graph.ro_query("RETURN 1 AS ok").result_set
    return {"status": "ok" if result == [[1]] else "error", "database": "FalkorDB", "dataset": DATA["version"], "synthetic": True, "persistence": "managed" if os.environ.get('FALKORDB_URL') else "ephemeral_demo"}


@app.get("/api/workspace")
def workspace(request: Request):
    graph = graph_for(request.state.workspace)
    return {"scenarios": DATA["scenarios"], "graph": snapshot(graph), "history": decision_history(graph), "csrf": csrf(request.state.workspace), "synthetic": True, "dataset": DATA["version"], "database": "FalkorDB", "persistence": "managed" if os.environ.get('FALKORDB_URL') else "ephemeral_demo"}


@app.post("/api/investigate")
def investigate_endpoint(body: InvestigateRequest, request: Request):
    graph = graph_for(request.state.workspace)
    plan = select_tool(body.question, body.lot_id) if body.use_agent else {"tool": "investigate", "lot_id": body.lot_id, "mode": "direct_tool", "model": None, "duration_ms": 0, "reason": "You chose a fixed traversal depth. FalkorDB ran the parameterised scope tool directly."}
    lot = plan["lot_id"]
    if plan["tool"] == "history":
        result = investigate(graph, lot, body.depth)
        result["history"] = decision_history(graph)
        result["summary"] = f"{len(result['history'])} reviewed decisions are recorded in this sandbox workspace."
    elif plan["tool"] == "compare_depth":
        result = compare_depth(graph, lot)
    else:
        result = investigate(graph, lot, body.depth)
        if plan["tool"] == "explain_path":
            match = re.search(r"\bSH-[0-9]{3}\b", body.question.upper())
            matches = [s for s in result["confirmed"] + result["uncertain"] if match and s["id"] == match.group()]
            if matches:
                item = matches[0]
                result["summary"] = f"{item['id']} is connected through " + " → ".join(item["path"]) + f". Evidence status: {item['confidence'].replace('_', ' ')}. Source records: " + ", ".join(item["source_ids"]) + "."
            elif match:
                result["summary"] = f"No path from {lot} to {match.group()} is present in this graph. No connection was inferred."
            elif result["outcome"] != "unknown_lot":
                result["summary"] = "Name a shipment ID, for example SH-106, to inspect its exact path and records."
    result["planner"] = plan
    result["graph"] = snapshot(graph)
    return result


@app.post("/api/plan")
def prepare_plan(body: PlanRequest, request: Request):
    return actions.prepare(graph_for(request.state.workspace), request.state.workspace, body.lot_id)


@app.post("/api/commit")
def commit_plan(body: CommitRequest, request: Request):
    return actions.commit(graph_for(request.state.workspace), request.state.workspace, body.token, body.approved)


@app.get("/api/history")
def history(request: Request):
    return {"decisions": decision_history(graph_for(request.state.workspace))}


@app.get("/api/export")
def export(request: Request, lot_id: str = "LOT-SM-2407"):
    if len(lot_id) > 64:
        raise HTTPException(400, "Lot ID is too long")
    graph = graph_for(request.state.workspace)
    result = investigate(graph, lot_id, 6)
    result.update(history=decision_history(graph), synthetic=True)
    return JSONResponse(result, headers={"Content-Disposition": 'attachment; filename="lotline-evidence.json"'})


DIST = ROOT / "dist"
if (DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")


@app.get("/favicon.svg")
def favicon():
    return FileResponse(ROOT / "web/public/favicon.svg")


@app.get("/{path:path}")
def frontend(path: str):
    if path.startswith("api/"):
        raise HTTPException(404, "API route not found")
    if (DIST / "index.html").exists():
        return FileResponse(DIST / "index.html", headers={"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY"})
    return JSONResponse({"message": "Run npm install and npm run build, then reopen Lotline."}, 503)
