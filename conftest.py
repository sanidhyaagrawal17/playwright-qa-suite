import os
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path(__file__).parent / "artifacts" / "screenshots"
TRACES_DIR = Path(__file__).parent / "artifacts" / "traces"


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    # Use bundled Chromium in CI, or fall back to local Chrome if headless shell isn't installed
    launch_kwargs = {"headless": True}
    channel = os.getenv("PW_CHANNEL")
    if channel:
        launch_kwargs["channel"] = channel
    try:
        browser = playwright_instance.chromium.launch(**launch_kwargs)
    except Exception:
        browser = playwright_instance.chromium.launch(headless=True, channel="chrome")
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser, request):
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    yield page
    # Automatically capture a screenshot and Playwright trace if the test failed
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        TRACES_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = request.node.name.replace("[", "_").replace("]", "").replace("/", "_")
        page.screenshot(path=str(ARTIFACTS_DIR / f"{safe_name}.png"), full_page=True)
        context.tracing.stop(path=str(TRACES_DIR / f"{safe_name}.zip"))
    else:
        context.tracing.stop()
    context.close()


@pytest.fixture(scope="session")
def api_context(playwright_instance):
    ctx = playwright_instance.request.new_context(
        base_url="https://jsonplaceholder.typicode.com",
        extra_http_headers={"Accept": "application/json"},
    )
    yield ctx
    ctx.dispose()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
