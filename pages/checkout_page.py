import re
from playwright.sync_api import Page, expect


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.cart_item_names = page.locator('[data-test="inventory-item-name"]')
        self.checkout_btn = page.locator('[data-test="checkout"]')
        self.first_name = page.locator('[data-test="firstName"]')
        self.last_name = page.locator('[data-test="lastName"]')
        self.postal_code = page.locator('[data-test="postalCode"]')
        self.continue_btn = page.locator('[data-test="continue"]')
        self.error_banner = page.locator('[data-test="error"]')
        self.finish_btn = page.locator('[data-test="finish"]')
        self.complete_header = page.locator('[data-test="complete-header"]')
        self.subtotal_label = page.locator('[data-test="subtotal-label"]')
        self.tax_label = page.locator('[data-test="tax-label"]')
        self.total_label = page.locator('[data-test="total-label"]')
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')

    def get_cart_item_names(self) -> list[str]:
        expect(self.page).to_have_url("https://www.saucedemo.com/cart.html")
        return [t.strip() for t in self.cart_item_names.all_text_contents()]

    def remove_item_from_cart(self, slug: str) -> None:
        self.page.locator(f'[data-test="remove-{slug}"]').click()

    def proceed_from_cart(self) -> None:
        expect(self.page).to_have_url("https://www.saucedemo.com/cart.html")
        self.checkout_btn.click()
        expect(self.page).to_have_url("https://www.saucedemo.com/checkout-step-one.html")

    def fill_customer_info(self, first: str, last: str, zip_code: str) -> None:
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.postal_code.fill(zip_code)
        self.continue_btn.click()

    def expect_validation_error(self, expected_text: str) -> None:
        expect(self.page).to_have_url("https://www.saucedemo.com/checkout-step-one.html")
        expect(self.error_banner).to_be_visible()
        expect(self.error_banner).to_contain_text(expected_text)

    @staticmethod
    def _extract_amount(text: str) -> float:
        match = re.search(r"\$([0-9]+\.[0-9]{2})", text)
        assert match is not None, f"No dollar amount found in: {text!r}"
        return float(match.group(1))

    def get_summary_totals(self) -> tuple[float, float, float]:
        expect(self.page).to_have_url("https://www.saucedemo.com/checkout-step-two.html")
        subtotal = self._extract_amount(self.subtotal_label.inner_text())
        tax = self._extract_amount(self.tax_label.inner_text())
        total = self._extract_amount(self.total_label.inner_text())
        return subtotal, tax, total

    def finish_order(self) -> None:
        self.finish_btn.click()

    def expect_order_confirmed_and_cart_cleared(self) -> None:
        expect(self.page).to_have_url("https://www.saucedemo.com/checkout-complete.html")
        expect(self.complete_header).to_have_text("Thank you for your order!")
        expect(self.cart_badge).to_be_hidden()
