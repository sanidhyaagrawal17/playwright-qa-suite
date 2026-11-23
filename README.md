# Playwright QA Automation Suite (Python + pytest)

[![Playwright QA Automation Suite](https://github.com/sanidhyaagrawal17/playwright-qa-suite/actions/workflows/qa-tests.yml/badge.svg)](https://github.com/sanidhyaagrawal17/playwright-qa-suite/actions/workflows/qa-tests.yml)

End-to-end **UI automation**, **REST API contract testing**, and **full-stack UI-to-database verification** built with **Python**, **Playwright**, and **pytest** using the **Page Object Model (POM)**, automatic failure screenshots/traces, and **GitHub Actions CI**.

## Real Defects Caught by This Suite
1. **TrustDesk Frontend/Backend Contract Bug (Fixed):** Running `test_trustdesk_telemetry_drawer_matches_live_backend_request_count` against the live FastAPI + React stack exposed that `GET /api/metrics` wraps counters inside `{"metrics": {...}}`, while `MetricsDrawer.tsx` read `mData.total_requests` directly — causing the UI telemetry drawer to always display `0` even though backend unit tests passed. Fixed in `TrustDesk` with a matching Vitest envelope regression test.
2. **SauceDemo `locked_out_user` Session Cookie Leak (`xfail(strict=True)`):** While SauceDemo displays the locked-out error banner on `/`, it still sets `session-username=locked_out_user` in browser cookies, allowing direct navigation to `/inventory.html`. Rather than weakening the cookie assertion to fake a green test, this case is explicitly marked `xfail(strict=True)` so it flags `XPASS` if fixed upstream.

## What This Suite Covers (21 Tests Total)
- **8 UI End-to-End Tests (`tests/test_ui_e2e.py`)** against [SauceDemo](https://www.saucedemo.com/) *(a public QA practice site)*:
  - Catalog load + decoded image integrity (`naturalWidth > 0`) check
  - 4 parametrized negative login checks verifying URL lock and absence of `session-username` cookie (1 marked `xfail(strict=True)` for the upstream `locked_out_user` cookie leak)
  - Sorting in both price directions (`lohi`, `hilo`) + alphabetical descending (`za`) with non-triviality check
  - Checkout required-field validation (empty First Name & Postal Code)
  - Cart add/remove state sync + exact arithmetic verification (`subtotal == sum(item prices)`, `tax > 0`, `subtotal + tax == total`) + cart cleared after order confirmation
- **6 REST API Contract Tests (`tests/test_api_contracts.py`)** against [JSONPlaceholder](https://jsonplaceholder.typicode.com) using Playwright's `APIRequestContext`:
  - `Content-Type` header + exact key-set schema checks on `GET /posts/1`
  - Query-filter strict subset verification (`GET /posts?userId=1` returns only `userId == 1` with unique IDs)
  - Nested resource integrity (`GET /posts/1/comments` foreign key & email checks)
  - Stateless `POST` (`201`), `PATCH` (`200` preserving unmodified fields), and `DELETE` (`200`) contract checks
  - Parametrized `404` checks (`/posts/999999`, `/nonexistent-resource`) asserting empty `{}` JSON response
- **7 Full-Stack App E2E Tests (`tests/test_trustdesk_e2e.py`)** against my own full-stack [TrustDesk](https://github.com/sanidhyaagrawal17/trustdesk) app *(runs live against `TRUSTDESK_URL`, default `http://localhost:3000`; auto-skipped in CI when no local server is running)*:
  - Channel toggle (`Untrusted (Public)` ↔ `Trusted (Internal)`), full inspection of `localStorage` keys/values, `sessionStorage`, `document.cookie`, and page-reload state wipe
  - Live `POST /api/chat/stream` HTTP `200 text/event-stream` check, assistant `<article>` grounding/retriever badges, and cross-checking the rendered `trace_id` directly against SQLite `GET /api/audit/{trace_id}`
  - End-to-end PII masking verification proving raw Aadhaar & phone numbers never persist in the SQLite audit record
  - Prompt-injection refusal badge + `injection_detected=True` verified in backend audit record
  - Parametrized HTTP `401` enforcement (missing token & invalid token) on Trusted channel
  - Runtime Telemetry drawer `TOTAL CALLS` cross-checked against live `GET /api/metrics`

## Design Decisions
- **Page Object Model (`pages/`):** Decouples `[data-test="..."]` and semantic ARIA role/label locators from test assertions so DOM refactors stay isolated to one file.
- **Session vs. Function Fixture Scoping (`conftest.py`):** Browser and `APIRequestContext` are `scope="session"` for speed, while each test gets a fresh `scope="function"` `BrowserContext` so cookies and storage never leak across tests.
- **No Fixed Sleeps (`time.sleep`):** Uses Playwright's auto-waiting assertions (`expect(...)`) and network response hooks (`page.expect_response(...)`) instead of arbitrary sleeps.
- **Falsifiable Assertions & Failure Triage:** Assertions target scoped containers (e.g., assistant `<article>` + backend API cross-checks) rather than broad `body` matches, and `conftest.py` saves full-page screenshots (`artifacts/screenshots/`) plus Playwright `.zip` traces (`artifacts/traces/`) on failure for CI debugging.

## Run Locally
```bash
pip install -r requirements.txt
playwright install chromium

# Run public UI + API suite (14 tests; TrustDesk tests auto-skip unless running on :3000)
pytest

# Run only TrustDesk full-stack E2E tests (with TrustDesk backend :8000 + frontend :3000 running)
pytest -m trustdesk
```
