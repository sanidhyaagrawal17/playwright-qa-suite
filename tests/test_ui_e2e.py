import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.checkout_page import CheckoutPage


@pytest.mark.ui
def test_valid_login_loads_complete_catalog_and_images(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)

    login.open()
    login.login("standard_user", "secret_sauce")
    inventory.expect_loaded()

    names = inventory.get_all_names()
    prices = inventory.get_all_prices()
    assert len(names) == 6 and all(len(n) > 0 for n in names)
    assert len(prices) == 6 and all(p > 0 for p in prices)

    # Verify product images actually decoded (catches broken image URLs like problem_user)
    broken_images = page.evaluate(
        """() => Array.from(document.querySelectorAll('.inventory_item_img img'))
            .filter(img => !img.complete || img.naturalWidth === 0)
            .map(img => img.src)"""
    )
    assert broken_images == [], f"Broken product images detected: {broken_images}"


@pytest.mark.ui
@pytest.mark.parametrize(
    "username,password,expected_error",
    [
        pytest.param(
            "locked_out_user",
            "secret_sauce",
            "Sorry, this user has been locked out",
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "Confirmed SauceDemo defect: rejects login UI with error banner "
                    "but still sets session-username=locked_out_user cookie, allowing "
                    "direct /inventory.html navigation."
                ),
            ),
        ),
        ("standard_user", "wrong_password", "Username and password do not match"),
        ("", "secret_sauce", "Username is required"),
        ("standard_user", "", "Password is required"),
    ],
)
def test_invalid_login_blocks_access_and_sets_no_session_cookie(
    page, username, password, expected_error
):
    login = LoginPage(page)
    login.open()
    login.login(username, password)

    login.expect_error_contains(expected_error)
    expect(page).to_have_url("https://www.saucedemo.com/")
    cookies = page.context.cookies()
    assert not any(c["name"] == "session-username" for c in cookies)


@pytest.mark.ui
def test_inventory_sorting_prices_and_names_both_directions(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)

    login.open()
    login.login("standard_user", "secret_sauce")
    inventory.expect_loaded()

    inventory.sort_by("lohi")
    prices_asc = inventory.get_all_prices()
    assert len(set(prices_asc)) > 1, "Catalog prices must not all be identical"
    assert prices_asc == sorted(prices_asc)

    inventory.sort_by("hilo")
    prices_desc = inventory.get_all_prices()
    assert prices_desc == sorted(prices_desc, reverse=True)
    assert prices_asc[0] < prices_desc[0]

    inventory.sort_by("za")
    names_desc = inventory.get_all_names()
    assert names_desc == sorted(names_desc, reverse=True)


@pytest.mark.ui
def test_checkout_validates_required_customer_fields(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)
    checkout = CheckoutPage(page)

    login.open()
    login.login("standard_user", "secret_sauce")
    inventory.add_item_by_slug("sauce-labs-backpack")
    inventory.open_cart()
    checkout.proceed_from_cart()

    checkout.fill_customer_info("", "Agrawal", "452001")
    checkout.expect_validation_error("First Name is required")

    checkout.fill_customer_info("Sanidhya", "Agrawal", "")
    checkout.expect_validation_error("Postal Code is required")


@pytest.mark.ui
def test_cart_mutation_and_exact_checkout_math_end_to_end(page):
    login = LoginPage(page)
    inventory = InventoryPage(page)
    checkout = CheckoutPage(page)

    login.open()
    login.login("standard_user", "secret_sauce")
    inventory.expect_loaded()

    backpack_price = inventory.get_item_price_by_name("Sauce Labs Backpack")
    bike_light_price = inventory.get_item_price_by_name("Sauce Labs Bike Light")
    fleece_price = inventory.get_item_price_by_name("Sauce Labs Fleece Jacket")

    # Add 3 items, remove 1 from cart, verify badge & item list stay in sync
    inventory.add_item_by_slug("sauce-labs-backpack")
    inventory.add_item_by_slug("sauce-labs-bike-light")
    inventory.add_item_by_slug("sauce-labs-fleece-jacket")
    inventory.expect_cart_count(3)

    inventory.open_cart()
    assert checkout.get_cart_item_names() == [
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Fleece Jacket",
    ]
    checkout.remove_item_from_cart("sauce-labs-fleece-jacket")
    inventory.expect_cart_count(2)
    assert checkout.get_cart_item_names() == [
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
    ]

    checkout.proceed_from_cart()
    checkout.fill_customer_info("Sanidhya", "Agrawal", "452001")

    # Verify exact item subtotal math & subtotal + tax == grand total
    expected_subtotal = round(backpack_price + bike_light_price, 2)
    assert expected_subtotal != round(backpack_price + bike_light_price + fleece_price, 2)
    subtotal, tax, total = checkout.get_summary_totals()
    assert subtotal == expected_subtotal, f"Expected subtotal {expected_subtotal}, got {subtotal}"
    assert tax > 0
    assert round(subtotal + tax, 2) == total, f"{subtotal} + {tax} != {total}"

    checkout.finish_order()
    checkout.expect_order_confirmed_and_cart_cleared()
