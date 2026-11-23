import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.checkout_page import CheckoutPage


@pytest.mark.ui
def test_valid_login_loads_inventory(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)

    login.open()
    login.login("standard_user", "secret_sauce")
    inventory.expect_loaded()


@pytest.mark.ui
@pytest.mark.parametrize(
    "username,password,expected_error",
    [
        ("locked_out_user", "secret_sauce", "Sorry, this user has been locked out"),
        ("standard_user", "wrong_password", "Username and password do not match"),
        ("", "secret_sauce", "Username is required"),
    ],
)
def test_invalid_login_shows_expected_error(page, username, password, expected_error):
    login = LoginPage(page)
    login.open()
    login.login(username, password)
    login.expect_error_contains(expected_error)


@pytest.mark.ui
def test_inventory_price_sorting_low_to_high(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)

    login.open()
    login.login("standard_user", "secret_sauce")
    inventory.expect_loaded()

    inventory.sort_by("lohi")
    prices = inventory.get_all_prices()
    assert len(prices) > 0
    assert prices == sorted(prices), f"Expected ascending prices, got {prices}"


@pytest.mark.ui
def test_end_to_end_checkout_flow(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)
    checkout = CheckoutPage(page)

    login.open()
    login.login("standard_user", "secret_sauce")
    inventory.expect_loaded()

    inventory.add_item_by_slug("sauce-labs-backpack")
    inventory.add_item_by_slug("sauce-labs-bike-light")
    inventory.expect_cart_count(2)

    inventory.open_cart()
    checkout.proceed_from_cart()
    checkout.fill_customer_info("Sanidhya", "Agrawal", "452001")
    checkout.expect_subtotal_visible()
    checkout.finish_order()
    checkout.expect_order_confirmed()
