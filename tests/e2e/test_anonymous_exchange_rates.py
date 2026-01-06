"""
Test E2E - Niezalogowany użytkownik sprawdza kursy walut

User Story:
    "Jako niezalogowany użytkownik chcę zobaczyć aktualne dzienne kursy walut:
    dolara amerykańskiego (USD) oraz euro (EUR),
    aby móc szybko sprawdzić najważniejsze waluty bez logowania."

Wymagania:
    - Test nawiguje do strony z kursami walut
    - Brak logowania
    - Weryfikacja widoczności kursów USD i EUR
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_anonymous_user_views_daily_exchange_rates(page: Page, e2e_server):
    """
    Test akceptacyjny (E2E): Niezalogowany użytkownik widzi kursy walut
    bez konieczności logowania.
    """

    # GIVEN: użytkownik niezalogowany otwiera stronę
    page.goto(f"{e2e_server}/ekonomia")

    # WHEN: strona ekonomii się załaduje
    expect(page).to_have_title(re.compile("NTWKInfo"))

    # THEN: widzi kurs EUR (euro)
    eur_locator = page.locator("div.currency-title", has_text="EUR")
    expect(eur_locator).to_be_visible()

    # AND: widzi kurs USD (dolar amerykański)
    usd_locator = page.locator("div.currency-title", has_text="USD")
    expect(usd_locator).to_be_visible()

    # BONUS: widzi kurs CHF (frank szwajcarski)
    chf_locator = page.locator("div.currency-title", has_text="CHF")
    expect(chf_locator).to_be_visible()
