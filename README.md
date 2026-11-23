# Playwright QA Automation Suite (Python + pytest)

End-to-end **UI automation** and **REST API contract testing** suite built with **Python**, **Playwright**, and **pytest**, structured using the **Page Object Model (POM)** with automatic failure screenshots and **GitHub Actions CI**.

## What This Suite Covers
- **UI End-to-End Tests (`tests/test_ui_e2e.py`)** against [SauceDemo](https://www.saucedemo.com/):
  - Positive login and inventory page state verification
  - Parametrized negative login tests (locked-out user, wrong password, blank username)
  - Price sorting validation (low-to-high numeric order check)
  - Full checkout workflow (add items to cart, badge count check, customer form, order confirmation)
- **REST API Contract Tests (`tests/test_api_contracts.py`)** using Playwright's `APIRequestContext`:
  - `GET /posts/1` status (`200`) and response schema validation
  - `POST /posts` creation (`201`) and payload echo check
  - `PUT` / `DELETE` lifecycle validation
  - Negative `404` error-path check
- **CI/CD & Failure Triage:**
  - `conftest.py` captures full-page screenshots automatically on any UI test failure into `artifacts/screenshots/`
  - `.github/workflows/qa-tests.yml` runs the full suite headlessly on every push/PR

## Project Structure
```text
playwright-qa-suite/
├── conftest.py                  # Session browser/API fixtures + screenshot-on-failure hook
├── pytest.ini                   # Pytest config & ui/api test markers
├── pages/
│   ├── login_page.py            # Login Page Object
│   ├── inventory_page.py        # Product listing, sorting & cart badge Page Object
│   └── checkout_page.py         # Cart & checkout flow Page Object
├── tests/
│   ├── test_ui_e2e.py           # 6 Playwright browser E2E tests
│   └── test_api_contracts.py    # 4 Playwright API contract tests
└── .github/workflows/qa-tests.yml
```

## Run Locally
```bash
pip install -r requirements.txt
playwright install chromium

# Run full suite (UI + API)
pytest

# Run only UI or only API tests
pytest -m ui
pytest -m api
```
