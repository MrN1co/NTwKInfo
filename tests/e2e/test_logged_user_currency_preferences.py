"""
Test E2E - Użytkownik korzysta z kalkulatora walut

User Story:
    "Jako użytkownik chcę móc wybrać walutę źródłową i docelową w kalkulatorze,
    aby przeliczać kwoty między różnymi walutami w szybki i prosty sposób."

Wymagania:
    - Test nawiguje do strony ekonomii
    - Weryfikuje widoczność kalkulatora walut
    - Zmienia walutę źródłową
    - Zmienia walutę docelową
    - Testuje obliczanie przeliczenia
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_user_converts_currencies_in_calculator(page: Page, e2e_server):
    """
    Test akceptacyjny (E2E): Użytkownik korzysta z kalkulatora walut
    i widzi prawidłowy przelicznik między walutami.
    """

    # ============================================================================
    # GIVEN: użytkownik otwiera stronę ekonomii
    # ============================================================================
    page.goto(f"{e2e_server}/ekonomia")

    # WHEN: strona się załaduje
    expect(page).to_have_title(re.compile("NTWKInfo|Bądź na czasie"))

    # ============================================================================
    # THEN: widzi kalkulator walut z polami wejścia i wyborem walut
    # ============================================================================
    expect(page.locator("#amount")).to_be_visible()
    expect(page.locator("#result")).to_be_visible()
    expect(page.locator("#currency-from")).to_be_visible()
    expect(page.locator("#currency-to")).to_be_visible()

    # ============================================================================
    # AND: wpisuje kwotę do pola wejścia
    # ============================================================================
    amount_input = page.locator("#amount")
    amount_input.fill("100")
    
    # Czekaj na obliczenie
    page.wait_for_timeout(300)

    # ============================================================================
    # AND: zmienia walutę źródłową na EUR
    # ============================================================================
    currency_from_select = page.locator("#currency-from")
    currency_from_select.select_option("EUR")
    
    # Czekaj na aktualizację przelicznika
    page.wait_for_timeout(300)

    # ============================================================================
    # AND: zmienia walutę docelową na USD
    # ============================================================================
    currency_to_select = page.locator("#currency-to")
    currency_to_select.select_option("USD")
    
    # Czekaj na aktualizację przelicznika
    page.wait_for_timeout(300)

    # ============================================================================
    # THEN: weryfikuje że wybrane waluty są poprawne
    # ============================================================================
    expect(currency_from_select).to_have_value("EUR")
    expect(currency_to_select).to_have_value("USD")

    # ============================================================================
    # AND: wynik zawiera liczbę (przeliczenie zostało wykonane)
    # ============================================================================
    result_input = page.locator("#result")
    expect(result_input).to_have_value(re.compile(r"\d+"))
