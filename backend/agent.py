"""The LLM chooses a tool, not facts, queries, or approval decisions."""
from __future__ import annotations

import json
import os
import re
import time
import httpx

TOOLS = ["investigate", "compare_depth", "explain_path", "history"]


def requested_lot(question: str, selected_lot: str) -> str:
    # Entity identity is deterministic even when the model chooses the tool.
    # Support both LOT-SM-2407 and transformation IDs such as MIX-091.
    candidates = re.findall(r"\b(?:LOT|MIX)-[A-Z0-9]+(?:-[A-Z0-9]+)*\b", question.upper())
    return candidates[0] if candidates else selected_lot


def select_tool(question: str, selected_lot: str) -> dict:
    start = time.perf_counter()
    target_lot = requested_lot(question, selected_lot)
    endpoint = os.environ.get("LOTLINE_PLANNER_URL")
    if endpoint:
        try:
            headers = {"Content-Type": "application/json", "User-Agent": "Lotline/1.0"}
            key = os.environ.get("LOTLINE_PLANNER_KEY")
            if key:
                headers["Authorization"] = f"Bearer {key}"
            with httpx.Client(timeout=22) as client:
                response = client.post(endpoint, json={"question": question, "selected_lot": selected_lot}, headers=headers)
                response.raise_for_status()
                plan = response.json()
            if plan.get("tool") not in TOOLS:
                raise ValueError("Unsupported tool")
            lot = plan.get("lot_id", selected_lot)
            if not isinstance(lot, str) or len(lot) > 64:
                raise ValueError("Invalid lot")
            return {"tool": plan["tool"], "lot_id": target_lot, "mode": "llm", "model": plan.get("model", "Workers AI"), "duration_ms": round((time.perf_counter()-start)*1000), "reason": "The language model selected a validated graph tool. The requested lot is bound independently; scope and claims are computed from graph rows."}
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
            reason = "The language model is unavailable. A local intent router selected the tool; all evidence still comes from FalkorDB."
    else:
        reason = "Local intent router. Configure LOTLINE_PLANNER_URL to enable language-model tool selection. All evidence comes from FalkorDB."
    lower = question.lower()
    tool = "compare_depth" if any(word in lower for word in ["compare", "one hop", "one-hop", "depth", "direct"]) else "history" if any(word in lower for word in ["history", "previous decision", "past decision"]) else "explain_path" if any(word in lower for word in ["why", "explain", "path to"]) else "investigate"
    return {"tool": tool, "lot_id": target_lot, "mode": "local_router", "model": None, "duration_ms": round((time.perf_counter()-start)*1000), "reason": reason}
