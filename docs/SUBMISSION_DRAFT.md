# Lotline submission draft

**Status: prepared for participant review; do not submit automatically.** The inspected WeMakeDevs form has no separate Save draft control. Populated fields remain an unsent browser form, not a confirmed server-saved submission.

## Project title
Lotline — Evidence before action

## Description
Lotline helps an operations analyst investigate a flagged ingredient lot through mixing, repacking and rework, then review the exact shipments that need a sandbox hold.

Its agent uses FalkorDB paths as evidence. In the same fictional case, one transformation hop finds zero confirmed dispatch units; the full chain finds 1,180 units across six shipments. Another 300 units have unsigned evidence and stay outside the hold plan. Each shipment opens its material path and source records. Unknown lots return unknown, without invented lineage.

A language model selects bounded tools; it cannot generate Cypher or approve a hold. The operator reviews the precise shipment list before a signed, expiring plan records a graph-backed decision receipt. Replay returns the same receipt.

Built by Adeel Falak Sher, solo. All business data is synthetic. AI assistance covered research, implementation, design, tests, documentation and synthetic demo narration. The repository includes reproducible checks and a technical explanation guide.

## Track
Agents That Act on Connected Data

## Repository
https://github.com/adeelfalaksher900-creator/lotline

## Demo video
Pending the final rendered video's public or unlisted YouTube URL. Do not insert a placeholder into the required form field.

## Live deployment
https://lotline-eight-indol.vercel.app

## How did you use FalkorDB in your project?
FalkorDB is the connected context and action store. The graph models lots, transformations, shipments, destinations, suppliers, source records and reviewed decisions. Parameterised Cypher follows INPUT_TO paths up to a fixed six-hop limit, reaches DISPATCHED shipments, and returns each path, source-record IDs and evidence status alongside the result. The backend deduplicates shipments and keeps unsigned paths out of the actionable scope.

The agent selects validated investigate, compare-depth, explain-path and history tools. The website invokes those Python tools directly; an optional read-only MCP server exposes the same capabilities. The UI displays the actual query trace, paths and documents.

A reviewed hold binds workspace, exact shipment IDs, revision, graph epoch and a ten-minute expiry. Commit re-queries scope and uses a conditional graph write to create a Decision with HOLDS relationships and update sandbox shipment status. Repeat intent returns the original receipt. Without FalkorDB, investigation and action planning are unavailable; the fixture JSON is ingestion input, not a fallback engine.

The public deployment uses actual FalkorDBLite, with a documented native compatibility adapter. Embedded state may reset at a cold start; complete local setup and a persistent FalkorDB connection option are included. No real stock service is contacted.

## Blog link
https://github.com/adeelfalaksher900-creator/lotline/blob/main/docs/BLOG.md

## What did you like about FalkorDB?
Cypher's variable-length path match made the key product behavior concise: the shipment result could include its transformation path and source IDs in one query. That let the UI show why repacked and reworked stock belonged in the scope, rather than asking a language model to invent an explanation. Named graphs also gave each demo workspace a simple isolated context, and the Python client worked with the embedded engine and the optional MCP tool server.

## What improvements would you like to see in FalkorDB?
A clearer, version-specific native compatibility matrix for FalkorDBLite across hosted Python runtimes would help. Deploying this prototype required isolating newer native libraries, including the OpenMP dependency, in the graph child process. An official serverless deployment recipe or clearer guidance on when to choose a managed connection would reduce that setup work. More end-to-end examples of read-only agent tools paired with signed, human-reviewed graph mutations would also be useful.

## YouTube metadata
**Title:** Lotline | FalkorDB Recall Investigation Agent | Graph Hacks 2026

**Description:**
A working demonstration of Lotline by Adeel Falak Sher, solo participant in Graph Hacks: Context for AI Agents.

Track: Agents That Act on Connected Data.

Live app: https://lotline-eight-indol.vercel.app
Source and setup: https://github.com/adeelfalaksher900-creator/lotline
Build write-up: https://github.com/adeelfalaksher900-creator/lotline/blob/main/docs/BLOG.md

The demo uses fictional data and actual React, FastAPI, FalkorDB and Workers AI tool selection. It shows one-hop versus full-chain scope, repack/rework paths, source evidence, uncertain stock, explicit hold review, a sandbox decision receipt and an unknown lot. Embedded hosted state may reset on a cold start; a persistent connection option and complete local instructions are documented.

AI assistance: research, implementation, design, tests, documentation and demo preparation were AI-assisted. Narration is synthetic ElevenLabs audio. This is a sandbox prototype; no real warehouse or supplier service is contacted.

Chapters:
0:00 The investigation workspace
0:17 One hop versus full context
0:40 Repack and rework lineage
0:51 Source evidence
1:02 Unverified stock
1:14 Actual query trace
1:23 Review before action
1:38 Sandbox hold and receipt
1:46 Unknown input
1:54 Code, setup and limits
