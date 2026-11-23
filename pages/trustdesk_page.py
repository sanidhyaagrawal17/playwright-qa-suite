import re
from playwright.sync_api import Locator, Page, expect


class TrustDeskPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.untrusted_btn = page.get_by_role("button", name="Untrusted (Public)")
        self.trusted_btn = page.get_by_role("button", name="Trusted (Internal)")
        self.bearer_input = page.get_by_label("Trusted channel Bearer token")
        self.query_input = page.get_by_label("Ask a loan question")
        self.send_btn = page.get_by_role("button", name="Send query")
        self.telemetry_btn = page.get_by_role(
            "button", name="Runtime Telemetry - open diagnostics drawer"
        )
        self.user_messages = page.locator('article[aria-label="User message"]')
        self.assistant_messages = page.locator(
            'article[aria-label="TrustDesk assistant response"]'
        )

    def open(self) -> None:
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        expect(self.untrusted_btn).to_be_visible()

    def switch_to_trusted(self) -> None:
        self.trusted_btn.click()
        expect(self.trusted_btn).to_have_attribute("aria-pressed", "true")
        expect(self.bearer_input).to_be_visible()

    def switch_to_untrusted(self) -> None:
        self.untrusted_btn.click()
        expect(self.untrusted_btn).to_have_attribute("aria-pressed", "true")
        expect(self.bearer_input).to_be_hidden()

    def send_query_and_wait_for_stream(self, text: str, expected_status: int = 200) -> Locator:
        prev_count = self.assistant_messages.count()
        self.query_input.fill(text)
        with self.page.expect_response(
            lambda r: "/api/chat/stream" in r.url and r.request.method == "POST",
            timeout=15000,
        ) as resp_info:
            self.send_btn.click()

        response = resp_info.value
        assert response.status == expected_status, (
            f"Expected POST /api/chat/stream HTTP {expected_status}, got {response.status}"
        )
        if expected_status == 200:
            assert "text/event-stream" in response.headers.get("content-type", "")

        expect(self.assistant_messages).to_have_count(prev_count + 1, timeout=15000)
        # Wait until streaming finishes (input re-enables and blinking cursor disappears)
        expect(self.query_input).to_be_enabled(timeout=15000)
        latest = self.assistant_messages.nth(prev_count)
        expect(latest.locator("span.animate-pulse")).to_have_count(0, timeout=15000)
        return latest

    @staticmethod
    def extract_trace_id(assistant_article: Locator) -> str:
        trace_el = assistant_article.locator('[title="Trace ID (recorded in audit log)"]')
        expect(trace_el).to_be_visible(timeout=10000)
        trace_id = trace_el.inner_text().strip()
        assert re.match(r"^trace-[a-f0-9]+$", trace_id), f"Invalid trace_id format: {trace_id!r}"
        return trace_id

    def open_telemetry_drawer(self) -> None:
        self.telemetry_btn.click()
        expect(self.page.get_by_role("heading", name="Runtime Telemetry")).to_be_visible()
