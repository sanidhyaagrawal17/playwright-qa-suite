from playwright.sync_api import Page, expect


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.checkout_btn = page.locator('[data-test="checkout"]')
        self.first_name = page.locator('[data-test="firstName"]')
        self.last_name = page.locator('[data-test="lastName"]')
        self.postal_code = page.locator('[data-test="postalCode"]')
        self.continue_btn = page.locator('[data-test="continue"]')
        self.finish_btn = page.locator('[data-test="finish"]')
        self.complete_header = page.locator('[data-test="complete-header"]')
        self.subtotal_label = page.locator('[data-test="subtotal-label"]')

    def proceed_from_cart(self) -> None:
        expect(self.page).to_have_url("https://www.saucedemo.com/cart.html")
        self.checkout_btn.click()

    def fill_customer_info(self, first: str, last: str, zip_code: str) -> None:
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.postal_code.fill(zip_code)
        self.continue_btn.click()

    def expect_subtotal_visible(self) -> None:
        expect(self.subtotal_label).to_be_visible()

    def finish_order(self) -> None:
        self.finish_btn.click()

    def expect_order_confirmed(self) -> None:
        expect(self.complete_header).to_have_text("Thank you for your order!")
