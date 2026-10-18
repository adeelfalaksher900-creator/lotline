# Research and product decision

Research date: 18 October 2026. Scope: official hackathon material, FalkorDB documentation, primary traceability standards, research papers and existing product descriptions. This is desk research, not a user-interview study or a novelty proof.

## Why Track 1
A recall investigation is a relationship problem with an observable action. A suspect source is mixed into a new batch, repacked under another identifier and reused in rework. A plain direct lookup misses descendants. FalkorDB returns each actual path and the agent uses that connected scope to propose a shipment hold.

Track: Agents That Act on Connected Data. Do not enter the memory track: the embedded hosted sandbox is intentionally ephemeral, and multi-agent coordination is not implemented.

## What the sources establish

| Primary source | Finding | Product implication |
| --- | --- | --- |
| [Hackathon rules](https://www.wemakedevs.org/hackathons/falkordb/rules) | FalkorDB must support a central product capability. A decorative visualization does not qualify. Public/synthetic data and AI-assistance disclosure are required. | All impact scope and decision state live in FalkorDB. The fixture is fictional. AI assistance is disclosed. |
| [Organiser technical guide](https://www.wemakedevs.org/blogs/how-to-build-an-agent-that-reasons-over-a-graph) | Fixed parameterised tools, real paths, depth comparison and honest unknown results are concrete demonstration advice. | The demo contrasts one hop with full traversal, opens the returned path and tests an unknown lot. |
| [GS1 EPCIS](https://www.gs1.org/standards/epcis) | Traceability is organized around visibility events and business context. Transformation events preserve input/output relationships. | Model input lots, output lots, dispatches and source record IDs as explicit relationships. This fixture is inspired by event traceability. It is not an EPCIS-conformant importer. |
| [Jing and Li, 2024](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2024.1389945/full), doi:10.3389/fsufs.2024.1389945 | Knowledge graphs integrate fragmented agricultural information and support batch tracing. The paper describes a carrots traceability case. | Use a graph for evidence-linked lineage. The paper does not establish this prototype's accuracy, safety, speed or commercial impact. |
| [Extending FKG.in, 2025](https://arxiv.org/abs/2508.16117) | Proposes a Food Claim-Traceability Network over food knowledge. | Sources and claims should remain distinguishable. We do not reproduce or claim its research results. |
| [FalkorDBLite](https://github.com/FalkorDB/FalkorDBLite) | The official package embeds the actual graph module and Redis server. | Offer a zero-account reproducible local sandbox, with managed FalkorDB as the persistence option. |

## Existing solutions and the proposed gap
Existing tools already provide forward/backward traceability and recall workflows. Examples inspected include [FeedTrace](https://feedtrace.ca/), [ClarityComply](https://www.clarity-comply.app/features/traceability), and [TraceR2C](https://tracer2c.com/). Their public descriptions are vendor claims and do not prove missing features.

Lotline's differentiator for this hackathon is the combination of a typed agent tool catalogue, transformation-level evidence paths, explicit unverified connections, one-hop/full-chain comparison, and a signed review of the exact shipment set before a sandbox action. This is a scoped design choice, not a claim that no competing product offers it.

## Dataset and claims
46 fictional domain nodes, 43 domain relationships, 17 lots, 11 shipments, 5 destinations, 3 suppliers and 10 source records. The sesame fixture has 1,180 confirmed dispatch units and 300 review units. A separate 450-unit shipment has no path from the flagged lot in the supplied graph. That is not proof of product safety.

The numbers are deterministic fixture facts, not customer results or a performance benchmark. No recall regulations, clinical decisions, real supplier accusations or private customer records are modeled.

## Judging interpretation
The official pages inspected do not give weighted numerical judging scores. The project should be assessed on observable evidence: useful connected reasoning, FalkorDB centrality, an actual action boundary, source/path transparency, honest unknowns and reproducibility. No prize is guaranteed.

## Scope limits
No real ERP/WMS integration, certified recall decision process, authenticated enterprise roles, complete EPCIS import, independent operator study, or production-scale benchmark. The public embedded instance may reset on cold starts. Its operational decisions are fictional. The local setup and managed-URL option are documented separately.
