"""Human-written, bounded Cypher tools. The model never writes queries."""
from __future__ import annotations

import time
from .database import rows, revision, snapshot

QUERIES = {
    "resolve_lot": "MATCH (l:Lot {id:$lot_id}) RETURN properties(l) AS lot",
    "documents": "MATCH (d:Document) WHERE d.id IN $ids RETURN properties(d) AS document ORDER BY d.id",
    "history": "MATCH (d:Decision) RETURN properties(d) AS decision ORDER BY d.at DESC LIMIT 30",
    "dispatch_sources": "MATCH (l:Lot)-[e:DISPATCHED]->(s:Shipment) WHERE s.id IN $ids RETURN s.id AS id,e.source_id AS source_id",
    "source_alert": "MATCH (d:Document)-[:ABOUT]->(l:Lot {id:$lot_id}) RETURN d.id AS source_id",
}
for depth in range(1, 7):
    QUERIES[f"scope_{depth}"] = f"""
MATCH p=(root:Lot {{id:$lot_id}})-[:INPUT_TO*0..{depth}]->(lot:Lot)
OPTIONAL MATCH (lot)-[:DISPATCHED]->(shipment:Shipment)-[:DELIVERED_TO]->(site:Site)
RETURN lot.id AS lot_id, lot.name AS lot_name,
       [n IN nodes(p) | n.id] AS path,
       [r IN relationships(p) | r.source_id] AS source_ids,
       [r IN relationships(p) | r.evidence] AS evidence,
       length(p) AS hops,
       properties(shipment) AS shipment,
       properties(site) AS site
ORDER BY hops, lot_id
LIMIT 501
""".strip()


def call(graph, tool: str, params: dict, trace: list):
    start = time.perf_counter()
    result = rows(graph, QUERIES[tool], params)
    trace.append({"tool": tool, "arguments": params, "duration_ms": round((time.perf_counter()-start)*1000, 2), "rows": len(result), "query": QUERIES[tool]})
    return result


def investigate(graph, lot_id: str, depth: int = 6) -> dict:
    if type(depth) is not int or not 1 <= depth <= 6:
        raise ValueError("Depth must be an integer from 1 to 6")
    trace: list = []
    resolved = call(graph, "resolve_lot", {"lot_id": lot_id}, trace)
    if not resolved:
        return {"outcome": "unknown_lot", "lot_id": lot_id, "summary": f"{lot_id} is not in this graph. No scope or action was inferred.", "trace": trace, "confirmed": [], "uncertain": [], "documents": [], "totals": {"units": 0, "shipments": 0, "sites": 0, "review_units": 0, "lots": 0}}
    result = call(graph, f"scope_{depth}", {"lot_id": lot_id}, trace)
    shipments: dict = {}
    lot_ids = set()
    source_ids = set()
    source_ids.update(r["source_id"] for r in call(graph, "source_alert", {"lot_id": lot_id}, trace))
    for row in result:
        lot_ids.add(row["lot_id"])
        source_ids.update(row["source_ids"])
        shipment = row["shipment"]
        if not shipment:
            continue
        valid = all(value == "confirmed" for value in row["evidence"])
        item = {**shipment, "lot_id": row["lot_id"], "lot_name": row["lot_name"], "path": row["path"], "source_ids": sorted(set(row["source_ids"])), "hops": row["hops"], "site": row["site"], "confidence": "confirmed" if valid else "needs_review"}
        current = shipments.get(shipment["id"])
        # A shipment counts exactly once. A verified route wins over an
        # unverified alternative, then the shortest actual route is displayed.
        if not current or (valid and current["confidence"] != "confirmed") or (item["confidence"] == current["confidence"] and item["hops"] < current["hops"]):
            shipments[shipment["id"]] = item
    confirmed = sorted((s for s in shipments.values() if s["confidence"] == "confirmed"), key=lambda s:s["id"])
    uncertain = sorted((s for s in shipments.values() if s["confidence"] != "confirmed"), key=lambda s:s["id"])
    # Dispatch provenance is itself a graph edge, not a prose-only claim.
    if shipments:
        evidence_rows = call(graph, "dispatch_sources", {"ids": list(shipments)}, trace)
        for record in evidence_rows:
            source_ids.add(record["source_id"])
            shipments[record["id"]]["source_ids"] = sorted(set(shipments[record["id"]]["source_ids"] + [record["source_id"]]))
    documents = call(graph, "documents", {"ids": sorted(source_ids)}, trace) if source_ids else []
    totals = {"units": sum(s["units"] for s in confirmed), "shipments": len(confirmed), "sites": len({s["site"]["id"] for s in confirmed}), "review_units": sum(s["units"] for s in uncertain), "lots": max(0, len(lot_ids)-1)}
    incomplete = len(result) >= 501
    summary = f"{totals['units']:,} dispatch units across {len(confirmed)} shipments have a confirmed path from {lot_id}."
    if uncertain:
        summary += f" Another {totals['review_units']:,} units need evidence review and are excluded from the hold plan."
    if not shipments:
        summary = f"No shipments are reachable within {depth} transformation hop{'s' if depth != 1 else ''}. This is a depth-limited result, not a safety finding."
    return {"outcome": "scope_incomplete" if incomplete else "answered_with_paths", "lot_id": lot_id, "lot": resolved[0]["lot"], "depth": depth, "revision": revision(graph), "confirmed": confirmed, "uncertain": uncertain, "documents": [r["document"] for r in documents], "totals": totals, "summary": summary, "trace": trace, "truncated": incomplete}


def compare_depth(graph, lot_id: str):
    shallow = investigate(graph, lot_id, 1)
    deep = investigate(graph, lot_id, 6)
    deep["comparison"] = {"one_hop": shallow["totals"], "full_chain": deep["totals"], "extra_units": deep["totals"]["units"] - shallow["totals"]["units"], "one_hop_trace": shallow["trace"]}
    return deep


def decision_history(graph):
    return [r["decision"] for r in rows(graph, QUERIES["history"])]
