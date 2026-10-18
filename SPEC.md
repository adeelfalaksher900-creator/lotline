# Lotline

Adeel Falak Sher, solo. Graph Hacks 2026, Agents That Act on Connected Data.

## Objective
A food operations analyst investigates a suspect ingredient lot, follows mixing and repacking to dispatched stock, reads the evidence, and approves a sandbox hold. The agent must not infer safety from missing data.

## Capabilities and build order
1. graph-context: FalkorDB stores lots, transformations, shipments, sites, source documents and hold decisions. Parameterised Cypher is the only impact-query implementation.
2. investigate: an LLM selects a typed tool; server validates arguments and assembles only graph-supported results. Depends on graph-context.
3. review-action: signed, expiring plans bind the exact affected shipment set and graph revision. An explicit user review applies an idempotent sandbox hold. Depends on investigate.
4. workspace: responsive investigation interface with evidence paths, depth comparison, trace, sources and decision history. Depends on investigate and review-action.
5. submission: public repository, reproducible setup, test evidence, 1080p actual product demonstration with ElevenLabs narration, and populated unsubmitted form.

## Architecture
React + TypeScript + Vite frontend. FastAPI backend. FalkorDB official Python client. Embedded official FalkorDB binaries for a zero-account local sandbox, or FALKORDB_URL for a managed instance. The embedded binary listens on loopback TCP because this environment does not allow Unix sockets. Cloudflare Workers AI supplies constrained tool selection. No Supabase dependency is required because FalkorDB owns the graph and decision state.

## Commands
Build: npm run build
Backend: python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
Tests: python3 -m pytest tests -q
Typecheck: npm run typecheck

## Structure
backend/ database adapter, typed tools and action validation
web/src/ application and shared controls
data/ deterministic fictional scenario
queries/ essential Cypher
tests/ meaningful graph, action and API negative tests
docs/ architecture, research, judging evidence and setup
media/ Hyperframes source, narration script and demo assets

## Style
Use typed request models, bounded inputs and a fixed query catalogue. Small named functions. Example: resolve_lot(graph, lot_id) checks the graph before traversing. The LLM never writes Cypher or approves actions.

## Success criteria
- Actual FalkorDB execution produces every impact result. Removing the database causes a visible service error, never a JSON fallback answer.
- One-hop and full-chain scopes differ, with the same real paths shown to the user.
- Reworked stock and merged lots do not double count shipment units.
- Unverified paths appear separately, and never become confirmed holds.
- Unknown lots yield an explicit unknown outcome, not an invented answer.
- The planner uses an actual LLM when available and labels any deterministic fallback.
- Review includes exact shipments and sources. Commit is session-bound, expiring, idempotent and rejects stale graph revisions.
- Workspaces isolate writable decision graphs. Cookies and origins protect state-changing requests.
- Tests cover graph scope, ambiguity, unknowns, injection strings, stale plans, idempotency and cross-workspace actions.
- UI is usable on desktop and phone, with keyboard focus, loading/error/empty states and reduced motion.
- No real supply-chain data, credentials, personal customer records or unsupported benchmark claims are published.
- Draft is prepared for Adeel only. Final submission is never triggered.

## Boundaries
Always: verify graph execution, disclose AI assistance accurately, label synthetic data and sandbox actions.
Ask first: paid upgrades, final hackathon submission, irreversible external actions.
Never: publish secrets, claim a guaranteed prize, fake LLM/database use, claim production recall authority, or fabricate participant testing/understanding.
