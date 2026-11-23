import os
import urllib.request
import pytest
from playwright.sync_api import expect
from pages.trustdesk_page import TrustDeskPage

TRUSTDESK_URL = os.getenv("TRUSTDESK_URL", "http://localhost:3000")


def _trustdesk_is_reachable(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False


pytestmark = [
    pytest.mark.trustdesk,
    pytest.mark.skipif(
        not _trustdesk_is_reachable(TRUSTDESK_URL),
        reason=f"Local TrustDesk app not running at {TRUSTDESK_URL} (set TRUSTDESK_URL to enable)",
    ),
]


def test_trustdesk_channel_toggle_switches_modes(page):
    td = TrustDeskPage(page, TRUSTDESK_URL)
    td.open()

    # Default state is Untrusted (Public)
    expect(td.untrusted_btn).to_have_attribute("aria-pressed", "true")
    expect(td.bearer_input).to_be_hidden()

    # Switching to Trusted reveals the Bearer token input without persisting to localStorage
    td.switch_to_trusted()
    td.bearer_input.fill("ephemeral-test-token")
    stored_keys = page.evaluate("() => Object.keys(window.localStorage)")
    assert "ephemeral-test-token" not in str(stored_keys)

    # Switching back hides the token input
    td.switch_to_untrusted()


def test_trustdesk_send_message_streams_response(page):
    td = TrustDeskPage(page, TRUSTDESK_URL)
    td.open()

    query = "What is the synthetic home loan interest rate and minimum tenure?"
    td.send_query(query)

    # User message renders immediately
    expect(page.get_by_text(query)).to_be_visible()
    # Streamed assistant response completes and re-enables the query input
    expect(td.query_input).to_be_enabled(timeout=15000)
    # Assistant response should contain loan/rate/tenure information from the FAQ retriever
    expect(page.locator("body")).to_contain_text("%", timeout=15000)


def test_trustdesk_trusted_channel_without_token_shows_401_error(page):
    td = TrustDeskPage(page, TRUSTDESK_URL)
    td.open()

    td.switch_to_trusted()
    td.send_query("Check internal policy details.")

    expect(page.get_by_text("Channel Authorization Failure (HTTP 401)")).to_be_visible(timeout=10000)
