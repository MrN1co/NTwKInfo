"""
Test E2E - Niezalogowany użytkownik sprawdza tabele lig

User Story:
    "Jako użytkownik chcę przeglądać tabele wybranych lig sportowych."

Wymagania:
    - Test nawiguje do strony z tabelami lig sportowych
    - Brak logowania
    - Weryfikacja widoczności wszystkich tabel lig
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_anonymous_user_views_sports_tables(page: Page, e2e_server):
    """GIVEN: niezalogowany użytkownik otwiera stronę z tabelami sportowymi

    WHEN: strona się załaduje z wyborem lig i tabelą wyników

    THEN: użytkownik widzi formularz do wyboru ligi i tabelę wyników.
    """

    # GIVEN
    page.goto(f"{e2e_server}/news/tables")
    expect(page).to_have_title(re.compile("Wyniki|NTWKInfo"))

    # WHEN: strona się załaduje
    # Czekaj na pojawienie się nagłówka
    heading = page.locator("h1")
    expect(heading).to_be_visible(timeout=5000)

    # THEN: weryfikuj, że istnieje selektor lig
    competition_select = page.locator("select#competition")
    expect(competition_select).to_be_visible()

    # THEN: sprawdź, że selektor ma opcje
    competition_options = page.locator("select#competition option")
    options_count = competition_options.count()
    assert options_count > 0, "Selektor lig nie ma żadnych opcji"

    # THEN: weryfikuj, że istnieje tabela
    table = page.locator("table")
    expect(table).to_be_visible()

    # THEN: sprawdź nagłówki tabeli
    table_headers = page.locator("table thead th")
    headers_count = table_headers.count()
    assert headers_count > 0, "Tabela nie ma nagłówków"

    # THEN: sprawdź, że tabela ma wiersze
    table_rows = page.locator("table tbody tr")
    rows_count = table_rows.count()
    assert rows_count > 0, "Tabela nie ma wierszy danych"

    # THEN: sprawdź zawartość pierwszego wiersza
    first_row = table_rows.first
    expect(first_row).to_be_visible()

    # THEN: weryfikuj, że są komórki w wierszu
    cells = first_row.locator("td")
    cells_count = cells.count()
    assert cells_count > 0, "Wiersz tabeli nie ma komórek"

    # THEN: sprawdź, czy istnieje informacja o aktualizacji
    info = page.locator(".info, .update-time")
    if info.count() > 0:
        expect(info.first).to_be_visible()

    # THEN: można zmienić ligę poprzez selektor
    # Pobierz pierwszą opcję (poza aktualnie wybraną)
    all_options = page.locator("select#competition option")
    assert all_options.count() > 1, "Powinno być co najmniej 2 opcje lig do wybrania"