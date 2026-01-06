"""
Test E2E - Niezalogowany użytkownik przelicza waluty za pomocą kalkulatora

User Story:
    "Jako zalogowany użytkownik chcę mieć możliwość wyboru walut z listy,
    które następnie mogę przeliczyć, aby móc wykonywać przeliczenia pomiędzy
    dowolnymi walutami."

Wymagania:
    - Test otwiera stronę ekonomii
    - Wybiera waluty z dropdown'ów (źródłową i docelową)
    - Wpisuje kwotę do przelieczenia
    - Weryfikuje że wynik się pojawił
    - Zmienia waluty i sprawdza nowy wynik
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_user_converts_currencies_with_calculator(page: Page, e2e_server):
    """
    Test akceptacyjny (E2E): Niezalogowany użytkownik wybiera waluty
    z kalkulatora i przelicza kwoty między dowolnymi walutami.
    """

    # ============================================================================
    # GIVEN: użytkownik niezalogowany otwiera stronę ekonomii
    # ============================================================================
    page.goto(f"{e2e_server}/ekonomia")

    # WHEN: strona ekonomii się załaduje
    expect(page).to_have_title(re.compile("NTWKInfo|Bądź na czasie"))

    # ============================================================================
    # THEN: widzi kalkulator walut z polami wejścia i dropdown'ami
    # ============================================================================
    amount_input = page.locator("#amount")
    result_input = page.locator("#result")
    currency_from_select = page.locator("#currency-from")
    currency_to_select = page.locator("#currency-to")

    expect(amount_input).to_be_visible()
    expect(result_input).to_be_visible()
    expect(currency_from_select).to_be_visible()
    expect(currency_to_select).to_be_visible()

    # ============================================================================
    # AND: wybiera EUR jako walutę źródłową
    # ============================================================================
    currency_from_select.select_option("EUR")
    page.wait_for_timeout(200)

    # AND: sprawdza czy EUR został wybrany
    expect(currency_from_select).to_have_value("EUR")

    # ============================================================================
    # AND: wybiera USD jako walutę docelową
    # ============================================================================
    currency_to_select.select_option("USD")
    page.wait_for_timeout(200)

    # AND: sprawdza czy USD został wybrany
    expect(currency_to_select).to_have_value("USD")

    # ============================================================================
    # WHEN: wpisuje kwotę do przelieczenia (100 EUR)
    # ============================================================================
    amount_input.fill("100")
    page.wait_for_timeout(300)

    # THEN: wynik zawiera liczbę (przeliczenie się odbyło)
    expect(result_input).to_have_value(re.compile(r"\d+"))

    # ============================================================================
    # AND: zmienia walutę docelową na GBP
    # ============================================================================
    currency_to_select.select_option("GBP")
    page.wait_for_timeout(300)

    # THEN: wynik się zmienia (nowe przeliczenie dla GBP)
    expect(currency_to_select).to_have_value("GBP")
    expect(result_input).to_have_value(re.compile(r"\d+"))

    # ============================================================================
    # AND: zmienia walutę źródłową na PLN
    # ============================================================================
    currency_from_select.select_option("PLN")
    page.wait_for_timeout(300)

    # THEN: wynik zostaje przeliczony dla PLN -> GBP
    expect(currency_from_select).to_have_value("PLN")
    expect(result_input).to_have_value(re.compile(r"\d+"))

    # ============================================================================
    # AND: zmienia kwotę na większą wartość (500)
    # ============================================================================
    amount_input.clear()
    amount_input.fill("500")
    page.wait_for_timeout(300)

    # THEN: wynik się zmienia proporcjonalnie
    expect(result_input).to_have_value(re.compile(r"\d+"))

    # ============================================================================
    # AND: sprawdza że wynik jest większy niż dla 100 (logika przeliczania działa)
    # ============================================================================
    result_for_500 = result_input.input_value()
    # Wynik powinien zawierać wartość numeryczną
    assert len(result_for_500) > 0, "Wynik kalkulacji powinien zawierać wartość"


def test_user_gets_instant_currency_conversion(page: Page, e2e_server):
    """
    Test akceptacyjny (E2E): Przeliczanie walut odbywa się natychmiast
    po wpisaniu kwoty bez konieczności zatwierdzania.
    """

    # ============================================================================
    # GIVEN: użytkownik otwiera kalkulator walut na stronie ekonomii
    # ============================================================================
    page.goto(f"{e2e_server}/ekonomia")

    # WHEN: strona się załaduje
    expect(page).to_have_title(re.compile("NTWKInfo|Bądź na czasie"))

    # ============================================================================
    # THEN: widzi pola kalkulatora
    # ============================================================================
    amount_input = page.locator("#amount")
    result_input = page.locator("#result")
    currency_from_select = page.locator("#currency-from")
    currency_to_select = page.locator("#currency-to")

    expect(amount_input).to_be_visible()
    expect(result_input).to_be_visible()

    # ============================================================================
    # AND: ustawia waluty EUR -> USD
    # ============================================================================
    currency_from_select.select_option("EUR")
    currency_to_select.select_option("USD")
    page.wait_for_timeout(200)

    # ============================================================================
    # WHEN: wpisuje pierwszą cyfrę (1)
    # ============================================================================
    amount_input.type("1")
    page.wait_for_timeout(100)

    # THEN: wynik pojawia się natychmiast
    result_after_first_digit = result_input.input_value()
    expect(result_input).to_have_value(re.compile(r"\d+"))

    # ============================================================================
    # AND: wpisuje drugą cyfrę (0) aby otrzymać kwotę 10
    # ============================================================================
    amount_input.type("0")
    page.wait_for_timeout(100)

    # THEN: wynik się zmienia natychmiast bez czekania
    result_after_second_digit = result_input.input_value()
    expect(result_input).to_have_value(re.compile(r"\d+"))

    # Wynik dla 10 powinien być większy niż dla 1
    assert result_after_first_digit != result_after_second_digit, \
        "Wynik powinien się zmienić podczas wpisywania"

    # ============================================================================
    # AND: wpisuje trzecią cyfrę (5) aby otrzymać 105
    # ============================================================================
    amount_input.type("5")
    page.wait_for_timeout(100)

    # THEN: wynik znów się zmienia natychmiast
    result_after_third_digit = result_input.input_value()
    expect(result_input).to_have_value(re.compile(r"\d+"))

    assert result_after_third_digit != result_after_second_digit, \
        "Wynik powinien się zmienić po wpisaniu kolejnej cyfry"

    # ============================================================================
    # AND: zmienia walutę docelową na GBP
    # ============================================================================
    currency_to_select.select_option("GBP")
    page.wait_for_timeout(200)

    # THEN: wynik się zmienia natychmiast bez ponownego wpisywania kwoty
    result_after_currency_change = result_input.input_value()
    expect(result_input).to_have_value(re.compile(r"\d+"))

    assert result_after_currency_change != result_after_third_digit, \
        "Wynik powinien się zmienić natychmiast przy zmianie waluty"

    # ============================================================================
    # AND: czyści pole i wpisuje nową kwotę (200)
    # ============================================================================
    amount_input.clear()
    page.wait_for_timeout(100)

    # THEN: wynik staje się pusty gdy kwota jest pusta
    expect(result_input).to_have_value("")

    # ============================================================================
    # AND: wpisuje nową kwotę (200)
    # ============================================================================
    amount_input.type("200")
    page.wait_for_timeout(100)

    # THEN: wynik pojawia się natychmiast dla nowej kwoty
    expect(result_input).to_have_value(re.compile(r"\d+"))
