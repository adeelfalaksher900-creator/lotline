# A recall list needs a path behind every row

A supplier flags an ingredient lot. The finished product has a different lot number. Some stock was repacked; some returned to production as rework. Which shipments should an operations analyst review?

Lotline is a working answer to that problem, built for the **Agents That Act on Connected Data** track of Graph Hacks. Its dataset is fictional. The goal is to demonstrate an investigation and a reviewed action whose outcome depends on a graph.

[Try the workspace](https://lotline-27e8ldgam-adeelfalaksher900-creators-projects.vercel.app) · [Read the code and setup](../README.md) · [Inspect the Cypher tools](../queries)

## The trap in a shallow lookup

The demonstration starts with `LOT-SM-2407`, a sesame ingredient. It becomes `MIX-091`, then crackers `LOT-CR-118`. Those crackers have their own shipments, but they also become mini crackers through repacking and seed bites through rework. A second mix creates another finished batch.

One transformation hop reaches mixes without dispatches. It returns zero confirmed dispatch units. Following up to six transformation hops reaches **1,180 units across six shipments**, including repacked and reworked stock. These are reproducible fixture results, not claims about a real recall or a performance benchmark.

The difference is the useful part of the demo. A graph is valuable when a relationship changes the decision. A decorative network next to a hard-coded result would not establish that.

## Model the evidence with the connection

Lot nodes connect through `INPUT_TO` relationships. Dispatch relationships lead to shipments; shipments connect to destinations. Source records document the transformations. The material edges carry both a source-record ID and an evidence status. A shipment also needs confirmed dispatch and delivery edges before it can enter a hold.

That last choice matters. An unsigned shift note suggests another connection, reaching 300 units. Lotline shows them as requiring evidence and excludes them from the confirmed hold. A different source lot has 450 units with no path from the flagged source in the fixture. Neither a missing path nor a missing signature establishes that stock is safe.

The distinction is visible in the graph, the table, the source dialogs and the action review. It is not left to a language model's wording.

## Return the explanation with the result

The core query follows the actual material path:

```cypher
MATCH p=(root:Lot {id:$lot_id})-[:INPUT_TO*0..6]->(lot:Lot)
OPTIONAL MATCH (lot)-[:DISPATCHED]->(shipment:Shipment)-[:DELIVERED_TO]->(site:Site)
RETURN lot.id AS lot_id,
       [n IN nodes(p) | n.id] AS path,
       [r IN relationships(p) | r.source_id] AS source_ids,
       [r IN relationships(p) | r.evidence] AS evidence,
       properties(shipment) AS shipment,
       properties(site) AS site
```

The shipment and its path come from the same query. Supporting documents are then retrieved by the returned source IDs. A reviewer can open a shipment and inspect why it appears, rather than accepting an explanation invented after the answer.

The backend deduplicates shipments reached by several paths. Fixed query variants bound traversal depth to one through six hops, and a row cap prevents an incomplete response from silently becoming an actionable list.

## Give the agent a bounded job

Workers AI selects from four validated tools: investigate, compare depth, explain a shipment path and read history. It returns a tool name and a lot ID; the server independently binds the requested lot so a model cannot substitute another case. It does not generate Cypher or authorize mutations. The frontend can also invoke a fixed depth directly; the trace labels that mode honestly.

The Python tools query a real FalkorDB engine. The JSON scenario is only ingestion input. If the database cannot be reached, the API reports unavailability instead of substituting a JSON lookup and pretending graph execution succeeded. Unknown lot IDs return an unknown result without inferred lineage.

An optional read-only MCP server exposes the same tool capabilities. The website invokes the Python tools directly; it does not claim an MCP transport it does not use.

## Put an explicit boundary before action

The operator opens a review showing the six exact confirmed shipments and the excluded uncertain stock. A signed plan binds the workspace, lot, shipment IDs, graph revision, graph epoch, expiry and a unique intent ID.

Commit checks the signature, workspace and explicit approval, then queries the current scope again. A conditional graph write records the decision, links its shipments and updates their sandbox status. Repeating a completed intent returns the original receipt. Expired, altered, stale and cross-workspace plans are rejected.

No external warehouse, supplier or customer system is contacted. This is a working sandbox action, not a production recall integration.

## What the build exposed

Deploying a native graph engine inside a Python serverless runtime required more care than serving a conventional web API. The embedded package needed newer native libraries than the hosting image provided. Lotline uses checksum-verified, version-pinned libraries only for its graph child process. It never replaces host libraries. The repository documents this adapter and the simpler local or managed-database alternatives.

The embedded hosted graph is temporary and may reset on a cold start or after an hour without activity. That limit is explicit. A production extension would need persistent database hosting, authenticated roles, operational review and real integration validation.

## Evidence before confidence

Thirteen integration and boundary tests execute actual FalkorDB and cover transformation scope, ambiguity, unknown and injection inputs, exact holds, replay and request boundaries. Additional checks exercise the MCP protocol, deployed LLM planner and hosted action flow. Automated desktop/mobile accessibility checks found contrast and control-label issues, which were corrected before recording.

The remaining gap is equally important: no independent operator study or production-scale benchmark has been performed. The repository records both completed checks and limits.

Lotline's central idea is small: keep the evidence attached to the action. The graph finds the relationship; the tool returns the path; a person reviews the consequence.

---

**Builder:** Adeel Falak Sher, solo participant. **AI assistance:** research, implementation, design, testing, documentation and demo preparation were assisted by OpenAI Codex. The runtime planner uses Workers AI; the demo uses synthetic ElevenLabs narration. The builder guide supports participant review and explanation of the work.
