# Lotline UX contract

Business source: SPEC.md and app.py request schemas. Visual source: DESIGN.md, generated tokens.css. English, UTC timestamps displayed with explicit local date formatting. Only synthetic sandbox operations.

Canonical controls: Button, Notice and Modal in web/src/components.tsx. Native select for cases and filters. Native semantic tables for shipments and history. No table selection. Dates are read-only ISO timestamps. The global stylesheet owns scrolling and focus. API helper owns error mapping and CSRF. App owns route/tab, case and result state.

Investigation: choose a case, edit the question, run. Pending button shows progress. Success replaces only the current case result. Failure preserves question and displays a retry action. A request sequence prevents stale responses from replacing a newer case. One-hop/full-chain uses fixed tool calls with an explicit depth label. Case switching is disabled while a request is pending. Changing cases clears the old scope and action plan. The displayed result keeps its original question when the composer is edited. Lot identity, source alert, fixed-depth controls and export follow the actual result, including a lot explicitly named outside the selected case.

Review: review plan request recomputes the full graph scope. Modal shows exact shipments, unit totals, excluded unverified stock and sandbox boundary. Approval checkbox starts unchecked. Commit is pessimistic and disables repeated clicks. Successful commit stays on the current investigation and shows the recorded decision. Cancel returns focus. A version conflict requires generating a new review. A failed commit retains the token for safe retry. Backend replay is idempotent.

Sources: open a named source, read the synthetic original record and close. No external private documents, uploads or customer records.

Dataset navigation: finite fixture of 11 shipments. Scope table includes explicit confirmed/needs-review filters and counts. History is bounded to 30 decisions by the API. This is a sandbox without a production pagination claim. Tab and case selection persist in URL parameters. The question and reviewed plan stay transient. Export downloads actual graph-supported JSON with synthetic flag.

Async: loading labels and stable workspace footprint. No optimistic stock status. Planner failure is labelled as local router, never as LLM success. Database failure produces a service error. Session expiry asks for page reload. Connection failures change the visible graph status and requests time out after 45 seconds. Incomplete scope is visibly partial and offers no action. Embedded demo decisions may reset on a cold start or after one hour without activity; managed FalkorDB is the persistence option. No claim of durable multitenancy for embedded hosting.

Accessibility: visible focus, correct button labels, live notifications, native checkbox and select, modal focus trap, Escape dismissal, focus restoration, reduced motion, no colour-only meaning. Diagram has table/path alternatives. Product is checked at phone, laptop and 1080p desktop sizes.
