"""
Test E2E - widoczność głównych walut na stronie ekonomia

User Story:
    "Jako zalogowany użytkownik, chce mieć dostęp do dziennego kursu walut, aby mieć możliwość być na bieżąco z aktualnymi cenami."

Wymagania:
    - Test otwiera stronę /ekonomia
    - Sprawdza widoczność walut USD, EUR i CHF w górnej części strony
    - Użycie expect(...) z Playwright
    - Given / When / Then
"""

from playwright.sync_api import Page, expect
import re

def test_main_currencies_visible_on_economia(page: Page, e2e_server):
    """Sprawdza, że USD, EUR i CHF są widoczne w górnej części strony ekonomia."""

    # GIVEN: użytkownik otwiera stronę ekonomii
    page.goto(f"{e2e_server}/ekonomia")

    # WHEN: strona się załaduje
    expect(page).to_have_title(re.compile("NTWKInfo|Bądź na czasie"))

    # THEN: główne waluty są widoczne
    for currency in ["USD", "EUR", "CHF"]:
        locator = page.locator("div.currency-title", has_text=currency)
        expect(locator).to_be_visible()
