# Verification evidence

Updated during the build on 18 October 2026. Only completed checks are marked passed.

| Check | Result | Evidence |
| --- | --- | --- |
| Native FalkorDB engine runs locally | Passed | Official Lite Redis/FalkorDB binaries, TCP connection and actual Cypher queries |
| Graph and action integration suite | Passed, 5 tests | python3 -m pytest tests -q |
| Repack and rework scope | Passed | 1,180 units, six exact shipment IDs and a three-transformation rework path |
| Unverified edge boundary | Passed | 300 units excluded from the confirmed hold |
| Unknown and injection inputs | Passed | No invented scope, source graph still intact |
| Reviewed action | Passed | Exact shipment set, idempotent replay, expired/tampered/stale and cross-workspace rejection |
| API request boundary | Passed | CSRF, Origin and strict depth validation |
| Read-only MCP protocol | Passed | Four tools listed, comparison and unknown-lot calls executed |
| Actual language-model tool selection | Passed | Workers AI returned compare_depth for the explicit comparison question |
| TypeScript / production frontend build | Passed | npm run build |
| Design token structure | Passed with warnings | 0 errors; component metadata warnings were corrected; semantic tokens are consumed by generated CSS |
| Hosted graph and action workflow | Passed | Actual deployed LLM selection, FalkorDB scope, unknown input, reviewed hold and idempotent replay; see live-verification.json |
| Desktop/mobile browser checks | Passed | Four axe scans reported zero violations for WCAG A/AA rule tags; focus restored, no mobile page overflow, no page errors |
| 1080p narrated demo | In progress | Actual working website recording with existing ElevenLabs narration |
| Docker Compose | Not run | Docker is unavailable; official image default entrypoint is preserved |

## Limits
No real customer data, ERP connection, operator study, formal penetration-test certification, production load test or enterprise tenancy assessment. No numerical judging rubric was published on the inspected official pages.

The automated accessibility checks are a scoped check, not a claim of complete accessibility conformance. Strix authentication repeatedly failed to become available, so no external Strix penetration scan is claimed. Review coverage comes from the documented integration and API boundary checks.
