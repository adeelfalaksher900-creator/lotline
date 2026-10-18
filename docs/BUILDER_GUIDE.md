# Explain Lotline in five minutes

For Adeel Falak Sher. Read this and run the example flow before final submission. Automated tests do not establish the participant's own technical understanding.

## The problem
A supplier lot is rarely the final product ID. Mixing, new batches, repacking and rework change identifiers. The investigation has to follow the chain. A language model should not guess which downstream shipments were affected.

## The model
- Lot nodes represent ingredients, mixes, batches, repacks and rework. Each has an ID and kind.
- INPUT_TO edges mean material from one lot was used in another lot. Each edge has a source record and evidence status.
- DISPATCHED connects a lot to a Shipment with a unit count and stock status.
- DELIVERED_TO connects each shipment to a destination.
- Document nodes contain the fictional source records. ABOUT links source alerts to a lot.
- Decision nodes link via HOLDS to the exact shipments reviewed by the operator.
- Meta stores the fixture version and a revision counter.

## The important query

```cypher
MATCH p=(root:Lot {id:$lot_id})-[:INPUT_TO*0..6]->(lot:Lot)
OPTIONAL MATCH (lot)-[:DISPATCHED]->(shipment:Shipment)-[:DELIVERED_TO]->(site:Site)
RETURN lot.id, [n IN nodes(p) | n.id],
       [r IN relationships(p) | r.source_id],
       [r IN relationships(p) | r.evidence],
       properties(shipment), properties(site)
```

`$lot_id` is a bound parameter. The model never writes this query. The six-hop bound comes from a fixed catalogue, not arbitrary user text. The same query returns the affected shipment and its path. We do not ask a model to manufacture an explanation afterward.

## What the agent does
The language model selects investigate, compare_depth, explain_path or history. The backend checks the selected tool and arguments. FalkorDB resolves the lot, traverses the graph and supplies the records. Result prose is assembled from those returned rows. If the LLM is unavailable, the interface identifies the local intent router. If the graph is unavailable, no scope is inferred.

The read-only MCP server exposes the same graph tools for an external MCP host. The website calls the validated Python tool functions directly. Do not say the web agent uses MCP transport: MCP is a tested optional integration.

## Why the sesame demo matters
At one transformation hop there are two signed mixes and one unverified batch, but zero confirmed dispatch units. Full traversal reaches 1,180 confirmed units, including mini packs and reworked stock. The 300 units connected only by an unsigned note remain in review. The separate 450-unit shipment is not linked in this fixture; that is not a safety finding.

## Why hold approval is separate
The LLM has no write or approval tool. The server recomputes the full scope, signs the exact shipment IDs, workspace, revision and ten-minute expiry, and shows that list in a review dialog. Commit checks the signature, workspace, approval, expiry and graph revision, rechecks scope, then creates a decision and updates shipment state in one conditional graph write. Replaying a completed token returns its original receipt. Nothing contacts a real supplier or warehouse.

## Hosting choice
FalkorDB is the primary graph database. Supabase is not required for this small sandbox. Local setup runs the official FalkorDBLite engine over loopback TCP. A managed FALKORDB_URL replaces the embedded connection without changing the graph queries. The hosted embedded graph is ephemeral; a cold start can reset its data. A signed session secret does not make the embedded database durable.

## Try explaining these yourself
1. Why does a simple source-lot lookup miss the repack and rework shipments?
2. Why is an unverified edge not the same as no edge?
3. Where does the 1,180 number come from, and how are duplicate paths handled?
4. What happens when the model names LOT-NOT-REAL?
5. Why must a changed graph invalidate a review token?
6. Which part writes the hold, and why is the LLM unable to approve it?
7. What resets on serverless cold start, and which deployment option gives persistence?

## AI disclosure
OpenAI Codex assisted with research, implementation, test design, documentation and demo preparation. The runtime planner uses a language model through Cloudflare Workers AI. Narration uses ElevenLabs. Do not claim manual authorship, operator studies, or personal verification that did not occur.
