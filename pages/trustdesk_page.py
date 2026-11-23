from playwright.sync_api import Page, expect


class TrustDeskPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.untrusted_btn = page.get_by_role("button", name="Untrusted (Public)")
        self.trusted_btn = page.get_by_role("button", name="Trusted (Internal)")
        self.bearer_input = page.get_by_label("Trusted channel Bearer token")
        self.query_input = page.get_by_label("Ask a loan question")
        self.send_btn = page.get_by_role("button", name="Send query")

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

    def send_query(self, text: str) -> None:
        self.query_input.fill(text)
        self.send_btn.click()
