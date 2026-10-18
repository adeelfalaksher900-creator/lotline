# Lotline product demonstration

Delivery: one natural, calm young male English voice, as a student explaining a working project. Conversational, clear, no sales performance. Narration is synthetic and disclosed.

Hi, I'm Adeel Falak Sher. This is Lotline, a recall investigation agent built with FalkorDB.

A supplier has flagged a sesame lot. The difficult question is where that lot went after mixing, repacking, and rework. Every record in this demo is fictional.

First, I'll run a one-hop lookup. It finds the immediate production relationships, but zero confirmed dispatch units. Stopping here would miss downstream stock.

Now I'll ask the agent to compare that with the full chain. The language model selects a bounded graph tool. FalkorDB follows the actual relationships and returns one thousand, one hundred and eighty units across six confirmed shipments.

Here is the important part. Repacked mini crackers still inherit the original lot. So does this reworked batch of seed bites. A new identifier does not remove the connection.

I'll open a shipment. The path and source records come from the same database query as the result. This is evidence you can inspect, rather than an explanation generated afterward.

There is also an unsigned shift note. Those three hundred units stay in evidence review. Lotline does not turn a possible connection into a confirmed finding, and a missing path is never a safety certificate.

The trace shows the selected tool, query, returned rows and timing. The model does not write Cypher. Its arguments are validated before the graph runs.

Next, I'll review the hold plan. It lists the exact confirmed shipments and excludes the uncertain stock. The review is signed, tied to this workspace and graph revision, and expires after ten minutes.

Only after I approve does Lotline record a sandbox hold. The decision log keeps the shipment IDs, units and receipt. No real warehouse or customer is contacted.

Finally, I'll ask about a lot that does not exist. The graph returns an honest unknown result, with no invented scope.

The public repository includes the graph model, essential queries, setup, tests and a read-only MCP server. This prototype uses an embedded graph, so hosted state can reset on a cold start. A managed FalkorDB connection provides the persistent deployment option.

Lotline keeps the evidence attached to the action.
