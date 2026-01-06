"""
Test E2E - Niezalogowany użytkownik sprawdza aktualną cenę złota

User Story:
    "Jako niezalogowany użytkownik chcę zobaczyć aktualną cenę złota (w PLN),
    aby znać jej wartość w czasie rzeczywistym."

Wymagania:
    - Test nawiguje do strony ekonomii
    - Weryfikuje widoczność ceny złota w PLN
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_anonymous_user_views_gold_price(page: Page, e2e_server):
    """
    Test akceptacyjny (E2E): Niezalogowany użytkownik widzi aktualną
    cenę złota na stronie ekonomii.
    """

    # GIVEN: użytkownik niezalogowany otwiera stronę ekonomii
    page.goto(f"{e2e_server}/ekonomia")

    # WHEN: strona ekonomii się załaduje
    expect(page).to_have_title(re.compile("NTWKInfo|Bądź na czasie"))

    # THEN: widzi nagłówek sekcji ze złotem
    expect(page.locator("h2:has-text('Cena złota')")).to_be_visible()

    # AND: widzi cenę złota (wyrażoną w oz - uncje troy)
    gold_price = page.locator("p.gold-price")
    expect(gold_price).to_be_visible()

    # AND: cena zawiera wartość numeryczną i oznaczenie [oz]
    expect(gold_price).to_contain_text("[oz]")

    # AND: widzi wykres ceny złota (w skali roku)
    expect(page.locator("h2:has-text('skali roku')")).to_be_visible()
    expect(page.locator("img.gold-chart")).to_be_visible()
