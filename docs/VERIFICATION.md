# Verification evidence

Updated during the build on 18 October 2026. Only completed checks are marked passed.

| Check | Result | Evidence |
| --- | --- | --- |
| Native FalkorDB engine runs locally | Passed | Official Lite Redis/FalkorDB binaries, TCP connection and actual Cypher queries |
| Graph and action integration suite | Passed, 13 tests | python3 -m pytest tests -q |
| Repack and rework scope | Passed | 1,180 units, six exact shipment IDs and a three-transformation rework path |
| Unverified edge boundary | Passed | 300 units excluded from the confirmed hold |
| Unknown and injection inputs | Passed | No invented scope, source graph still intact |
| Reviewed action | Passed | Exact shipment set, idempotent replay, expired/tampered/stale and cross-workspace rejection |
| API request boundary | Passed | CSRF, full Origin, strict depth validation, bounded chunked bodies and token-purpose separation |
| Read-only MCP protocol | Passed | Four tools listed, comparison and unknown-lot calls executed |
| Actual language-model tool selection | Passed | Workers AI returned compare_depth for the explicit comparison question |
| TypeScript / production frontend build | Passed | npm run build |
| Design token structure | Passed with warnings | 0 errors; component metadata warnings were corrected; semantic tokens are consumed by generated CSS |
| Hosted graph and action workflow | Passed | Actual deployed LLM selection, FalkorDB scope, unknown input, reviewed hold and idempotent replay; see live-verification.json |
| Desktop/mobile browser checks | Passed | Six current axe scans reported zero violations for WCAG A/AA rule tags; focus restored, no mobile page overflow, no page errors |
| 1080p narrated demo | Passed | 133 seconds, 1920×1080, 30fps, H.264 video and normalized synthetic narration; representative exported frames reviewed |
| Docker Compose | Not run | Docker is unavailable; official image default entrypoint is preserved |

## Limits
No real customer data, ERP connection, operator study, formal penetration-test certification, production load test or enterprise tenancy assessment. No numerical judging rubric was published on the inspected official pages.

The automated accessibility checks are a scoped check, not a claim of complete accessibility conformance. Strix authentication repeatedly failed to become available, so no external Strix penetration scan is claimed. Review coverage comes from the documented integration and API boundary checks.

## Fresh public checkout

A clean clone of public commit `dae5e9a82416612658fe36ad1a6d970aa7e94b32` was installed in a new Python 3.12 virtual environment. Its five real-FalkorDB integration tests, `npm ci`, production build and read-only MCP protocol verification all passed. This independently checks the published source rather than only the build worktree. A Starlette TestClient deprecation warning remains; no test failed.

The final source-only Vercel deployment also passed hosted verification. Its build runs npm ci, the production frontend build and the native runtime preparation, so a prebuilt dist directory is not needed in the repository.

## Final focused review, 18 October
The current worktree passes 13 tests against real FalkorDB, including unverified dispatch/delivery exclusion, independent lot binding despite a mismatched model response, embedded-workspace capacity without eviction, idle TTL, packaged favicon serving, and refusal to act on a 501-row partial scope. The earlier fresh-checkout five-test result remains historical evidence for that published commit. This pass is a focused source and regression review, not an exhaustive independent security audit or availability assessment.

The final UI regression pass covered six states with zero axe violations: start, cross-lot result, full-chain result, review, unknown lot and mobile result. It also checked the correct milk source record, stable displayed question, disabled case switching during requests, a visible logo, dialog fit, focus restoration and no mobile page overflow. See final-ui-review.json.

Dependency review upgraded Vite 7.1.12 to 7.3.7 after npm reported dev-server advisories. The patched lockfile reports zero known npm vulnerabilities. The Python verification environment initially flagged its old pip installer; upgrading that tooling to pip 26.2.1 left zero known findings in the installed-environment audit. These are advisory database checks, not proof that every dependency or the host is vulnerability-free. See npm-dependency-audit.json and python-dependency-audit.json.

The final deployed frontend was also opened and exercised in the connected Chrome browser at the immutable deployment URL. Its full-chain result and updated evidence copy were confirmed visually. That tested build URL is used in the README and submission draft; the browser had retained older asset references at the original alias.

## Submission confirmation
WeMakeDevs displayed Submitted for Lotline — Evidence before action, Solo entry, filed by Adeel Falak Sher (@adeel) at Oct 18, 2026, 8:25 PM Pakistan time. All ten form fields were complete, including the final YouTube demo, repository, live deployment, track and blog. The public YouTube oEmbed endpoint returned HTTP 200 with the Lotline demo title and Adeel Falak Sher as author.
