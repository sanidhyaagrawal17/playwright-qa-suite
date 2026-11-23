# Playwright QA Automation Suite (Python + pytest)

[![Playwright QA Automation Suite](https://github.com/sanidhyaagrawal17/playwright-qa-suite/actions/workflows/qa-tests.yml/badge.svg)](https://github.com/sanidhyaagrawal17/playwright-qa-suite/actions/workflows/qa-tests.yml)

End-to-end **UI automation** and **REST API contract testing** suite built with **Python**, **Playwright**, and **pytest**, structured using the **Page Object Model (POM)** with automatic failure screenshots, Playwright failure traces, and **GitHub Actions CI**.

## What This Suite Covers
- **6 UI End-to-End Tests (`tests/test_ui_e2e.py`)** against [SauceDemo](https://www.saucedemo.com/) *(a public QA practice site)*:
  - Positive login and inventory page state verification
  - 3 parametrized negative login cases (locked-out user, wrong password, blank username)
  - Price sorting validation (low-to-high numeric order check)
  - Full checkout workflow (add items to cart, badge count check, customer form, order confirmation)
- **4 REST API Contract Tests (`tests/test_api_contracts.py`)** against [JSONPlaceholder](https://jsonplaceholder.typicode.com) using Playwright's `APIRequestContext`:
  - `GET /posts/1` status (`200`) and response schema validation
  - `POST /posts` creation (`201`) and payload echo verification
  - `PUT /posts/1` & `DELETE /posts/1` lifecycle validation
  - Negative `404` error-path check (`GET /posts/999999`)
- **3 TrustDesk App E2E Tests (`tests/test_trustdesk_e2e.py`)** against my own full-stack [TrustDesk](https://github.com/sanidhyaagrawal17/trustdesk) app (when running locally at `TRUSTDESK_URL`, default `http://localhost:5173`; skipped automatically in CI when no local server is running):
  - Execution channel toggle (`Untrusted (Public)` ↔ `Trusted (Internal)`), ARIA state checks, and verifying the Bearer token is never persisted to `localStorage`
  - Sending a loan FAQ query and asserting the streamed SSE response renders in the chat UI
  - Verifying the `Channel Authorization Failure (HTTP 401)` error state when querying the Trusted channel without a Bearer token
- **CI/CD & Failure Triage:**
  - `conftest.py` captures full-page screenshots (`artifacts/screenshots/`) and Playwright traces (`artifacts/traces/`) automatically on any UI test failure
  - `.github/workflows/qa-tests.yml` runs all 10 tests headlessly on Ubuntu on every push/PR and uploads failure artifacts

## Design Decisions
- **Page Object Model (`pages/`):** Keeps `[data-test="..."]` locators and page actions decoupled from test assertions in `tests/`. If a UI selector changes, it is updated once in its Page Object instead of across multiple tests.
- **Session vs. Function Fixture Scoping (`conftest.py`):** The Chromium browser and `APIRequestContext` are `scope="session"` to avoid repeated browser startup overhead, while each test receives a fresh `scope="function"` `BrowserContext` so cookies, storage, and cart state never leak between tests.
- **No Fixed Sleeps (`time.sleep`):** All UI interactions and assertions rely on Playwright's built-in auto-waiting (`expect(locator).to_be_visible()`, `to_have_url()`, `to_have_text()`), which poll until the DOM reaches the expected state or hits a bounded timeout.
- **Flaky Test Triage:** On failure, `conftest.py` automatically saves a full-page screenshot and Playwright trace (`.zip` with DOM snapshots and network/console timeline) so CI-only failures can be inspected in Playwright Trace Viewer without reproducing blindly.

## Project Structure
```text
playwright-qa-suite/
├── conftest.py                  # Session browser/API fixtures + failure screenshot & trace hooks
├── pytest.ini                   # Pytest config & ui/api test markers
├── pages/
│   ├── login_page.py            # Login Page Object
│   ├── inventory_page.py        # Product listing, sorting & cart badge Page Object
│   └── checkout_page.py         # Cart & checkout flow Page Object
├── tests/
│   ├── test_ui_e2e.py           # 6 Playwright browser E2E tests (SauceDemo)
│   └── test_api_contracts.py    # 4 Playwright API contract tests (JSONPlaceholder)
└── .github/workflows/qa-tests.yml
```

## Run Locally
```bash
pip install -r requirements.txt
playwright install chromium

# Run full suite (6 UI + 4 API tests)
pytest

# Run only UI or only API tests
pytest -m ui
pytest -m api
```
