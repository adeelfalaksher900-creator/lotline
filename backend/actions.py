"""Review-first, signed, idempotent decisions inside a fictional workspace."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime, timezone

from .database import LOCK, revision, rows, epoch
from .tools import investigate

SECRET = os.environ.get("LOTLINE_SESSION_SECRET", secrets.token_hex(32)).encode()


class ActionError(Exception):
    def __init__(self, message, status=409):
        self.message, self.status = message, status


def sign(payload: dict, purpose: str) -> str:
    data = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).decode().rstrip("=")
    digest = hmac.new(SECRET, f"{purpose}:{data}".encode(), hashlib.sha256).hexdigest()
    return f"{data}.{digest}"


def verify(token: str, purpose: str) -> dict:
    try:
        if not isinstance(token, str) or len(token) > 6000:
            raise ValueError()
        data, digest = token.rsplit(".", 1)
        expected = hmac.new(SECRET, f"{purpose}:{data}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, digest):
            raise ValueError()
        payload = json.loads(base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)))
        if not isinstance(payload, dict):
            raise ValueError()
        return payload
    except (ValueError, TypeError, json.JSONDecodeError):
        raise ActionError("The review token is invalid. Generate a new plan.", 403)


def prepare(graph, workspace: str, lot_id: str, now: int | None = None):
    scope = investigate(graph, lot_id, 6)
    eligible = [s for s in scope["confirmed"] if s.get("status") != "held"]
    if scope["outcome"] != "answered_with_paths" or not eligible:
        raise ActionError("No complete, confirmed, unheld shipments are available for this plan.")
    payload = {"workspace": workspace, "lot_id": lot_id, "shipments": sorted(s["id"] for s in eligible), "revision": scope["revision"], "epoch": epoch(graph), "expires": (now if now is not None else int(time.time())) + 600, "id": secrets.token_hex(12)}
    return {"token": sign(payload, "review"), "id": payload["id"], "expires_at": payload["expires"], "revision": payload["revision"], "lot_id": lot_id, "shipments": eligible, "units": sum(s["units"] for s in eligible), "excluded": scope["uncertain"], "sandbox": True}


def commit(graph, workspace: str, token: str, approved: bool, now: int | None = None):
    if approved is not True:
        raise ActionError("Review and approve the exact sandbox shipment list first.", 400)
    payload = verify(token, "review")
    if payload.get("workspace") != workspace:
        raise ActionError("This plan belongs to a different workspace.", 403)
    with LOCK:
        existing = rows(graph, "MATCH (d:Decision {id:$id}) RETURN properties(d) AS decision", {"id": payload["id"]})
        if existing:
            return {"decision": existing[0]["decision"], "replayed": True}
        if payload.get("expires", 0) < (now if now is not None else int(time.time())):
            raise ActionError("This plan expired. Generate a new plan.")
        if revision(graph) != payload["revision"] or epoch(graph) != payload.get("epoch"):
            raise ActionError("The graph changed after this review. Refresh the scope and review again.")
        fresh = investigate(graph, payload["lot_id"], 6)
        actual = sorted(s["id"] for s in fresh["confirmed"] if s.get("status") != "held")
        if fresh["truncated"] or actual != payload["shipments"]:
            raise ActionError("The affected shipment list changed. Review a new plan.")
        at = datetime.now(timezone.utc).isoformat()
        decision = {"id": payload["id"], "lot_id": payload["lot_id"], "at": at, "shipment_ids": actual, "units": sum(s["units"] for s in fresh["confirmed"] if s["id"] in actual), "action": "sandbox_hold", "note": "Reviewed in Lotline sandbox. No external stock system was contacted."}
        # One graph query creates the decision, links its exact shipment set,
        # updates stock state and advances the revision as a single write.
        written = rows(graph, """
MATCH (m:Meta {id:'dataset'})
WHERE m.revision=$expected_revision AND m.epoch=$expected_epoch
OPTIONAL MATCH (previous:Decision {id:$decision_id})
WITH m,previous WHERE previous IS NULL
CREATE (d:Decision) SET d = $decision
WITH m,d
MATCH (s:Shipment) WHERE s.id IN $ids
CREATE (d)-[:HOLDS]->(s)
SET s.status='held'
WITH DISTINCT m,d
SET m.revision=m.revision+1
RETURN properties(d) AS decision
""", {"decision": decision, "ids": actual, "expected_revision": payload["revision"], "expected_epoch": payload["epoch"], "decision_id": payload["id"]}, write=True)
        if not written:
            existing = rows(graph, "MATCH (d:Decision {id:$id}) RETURN properties(d) AS decision", {"id": payload["id"]})
            if existing:
                return {"decision": existing[0]["decision"], "replayed": True}
            raise ActionError("The graph changed while applying this review. Generate a new plan.")
        return {"decision": decision, "replayed": False}
