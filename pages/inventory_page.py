from playwright.sync_api import Page, expect


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.locator('[data-test="title"]')
        self.sort_dropdown = page.locator('[data-test="product-sort-container"]')
        self.item_prices = page.locator('[data-test="inventory-item-price"]')
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')
        self.cart_link = page.locator('[data-test="shopping-cart-link"]')

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url("https://www.saucedemo.com/inventory.html")
        expect(self.title).to_have_text("Products")

    def sort_by(self, option_value: str) -> None:
        self.sort_dropdown.select_option(option_value)

    def get_all_prices(self) -> list[float]:
        raw = self.item_prices.all_text_contents()
        return [float(p.replace("$", "").strip()) for p in raw]

    def add_item_by_slug(self, slug: str) -> None:
        self.page.locator(f'[data-test="add-to-cart-{slug}"]').click()

    def expect_cart_count(self, count: int) -> None:
        expect(self.cart_badge).to_have_text(str(count))

    def open_cart(self) -> None:
        self.cart_link.click()
