from playwright.sync_api import Page, expect


class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.locator('[data-test="title"]')
        self.sort_dropdown = page.locator('[data-test="product-sort-container"]')
        self.inventory_items = page.locator('[data-test="inventory-item"]')
        self.item_names = page.locator('[data-test="inventory-item-name"]')
        self.item_prices = page.locator('[data-test="inventory-item-price"]')
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')
        self.cart_link = page.locator('[data-test="shopping-cart-link"]')

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url("https://www.saucedemo.com/inventory.html")
        expect(self.title).to_have_text("Products")
        expect(self.inventory_items).to_have_count(6)

    def sort_by(self, option_value: str) -> None:
        self.sort_dropdown.select_option(option_value)

    def get_all_prices(self) -> list[float]:
        raw = self.item_prices.all_text_contents()
        return [float(p.replace("$", "").strip()) for p in raw]

    def get_all_names(self) -> list[str]:
        return [t.strip() for t in self.item_names.all_text_contents()]

    def get_item_price_by_name(self, name: str) -> float:
        card = self.inventory_items.filter(has_text=name)
        expect(card).to_have_count(1)
        price_text = card.locator('[data-test="inventory-item-price"]').inner_text()
        return float(price_text.replace("$", "").strip())

    def add_item_by_slug(self, slug: str) -> None:
        self.page.locator(f'[data-test="add-to-cart-{slug}"]').click()

    def remove_item_by_slug(self, slug: str) -> None:
        self.page.locator(f'[data-test="remove-{slug}"]').click()

    def expect_cart_count(self, count: int) -> None:
        if count == 0:
            expect(self.cart_badge).to_be_hidden()
        else:
            expect(self.cart_badge).to_have_text(str(count))

    def open_cart(self) -> None:
        self.cart_link.click()
