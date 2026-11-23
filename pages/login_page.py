from playwright.sync_api import Page, expect


class LoginPage:
    URL = "https://www.saucedemo.com/"

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator('[data-test="username"]')
        self.password_input = page.locator('[data-test="password"]')
        self.login_button = page.locator('[data-test="login-button"]')
        self.error_banner = page.locator('[data-test="error"]')

    def open(self) -> None:
        self.page.goto(self.URL, wait_until="domcontentloaded")

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def expect_error_contains(self, text: str) -> None:
        expect(self.error_banner).to_be_visible()
        expect(self.error_banner).to_contain_text(text)
