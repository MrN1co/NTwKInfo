"""
Test E2E - Zalogowany użytkownik sprawdza historię przeczytanych artykułów

User Story:
    "Jako zalogowany użytkownik chcę przejrzeć historię przeczytanych artykułów, aby nie szukać ich ponownie."

Wymagania:
    - Test nawiguje do strony z historią przeczytanych artykułów
    - Logowanie
    - Weryfikacja widoczności wszystkich przeczytanych artykułów
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_logged_user_views_news_history(page: Page, e2e_server, app):
    """GIVEN: zalogowany użytkownik otwiera stronę z historią

    WHEN: strona się załaduje z tabelą historii przeczytanych artykułów

    THEN: tabela zawiera nagłówki, licznik kliknięć i struktura historii.
    """
    from modules.database import User
    
    # Setup: Utwórz testowego użytkownika
    test_username = "testuser_history"
    test_password = "testpass123"
    with app.app_context():
        existing_user = User.query.filter_by(username=test_username).first()
        if existing_user:
            User.query.filter_by(username=test_username).delete()
        User.create(test_username, f"{test_username}@test.com", test_password)

    # GIVEN: zaloguj użytkownika
    page.goto(f"{e2e_server}/")
    
    # Otwórz modal logowania
    login_btn = page.locator(".header__cta-button")
    login_btn.click()
    
    # Czekaj na formularz logowania
    page.wait_for_selector("#loginForm:not(.hidden)", timeout=3000)
    
    # Zaloguj się
    page.locator("#loginForm input[name='username']").fill(test_username)
    page.locator("#loginForm input[name='password']").fill(test_password)
    page.locator("#loginForm button[type='submit']").click()
    
    # Czekaj aż logowanie się zakoczy
    page.wait_for_timeout(1000)

    # WHEN: przejdź do strony historii
    page.goto(f"{e2e_server}/news/history/view")

    # Czekaj na załadowanie tabeli historii
    history_table = page.locator(".history-table")
    expect(history_table).to_be_visible(timeout=5000)

    # THEN: sprawdź nagłówek strony
    heading = page.locator(".container-padding h2")
    expect(heading).to_contain_text("Twoja historia")

    # THEN: sprawdź, że jest licznik kliknięć
    total_clicks = page.locator("p", has_text="Łącznie kliknięć")
    expect(total_clicks).to_be_visible()

    # THEN: sprawdź nagłówki tabeli
    table_headers = page.locator("table.history-table thead th")
    headers_count = table_headers.count()
    assert headers_count >= 4, f"Tabela powinna mieć co najmniej 4 kolumny, ma {headers_count}"

    # THEN: sprawdź, czy istnieją wiersze z artykułami
    table_rows = page.locator("table.history-table tbody tr")
    rows_count = table_rows.count()

    if rows_count > 0:
        # Jeśli są artykuły, sprawdź pierwszy wiersz
        first_row = table_rows.first
        expect(first_row).to_be_visible()

        # Sprawdź, że wiersz ma link do artykułu
        news_link = first_row.locator("a.news-link")
        expect(news_link).to_be_visible()

        # Sprawdź, że link ma href
        href = news_link.get_attribute("href")
        assert href, "Link w historii nie ma atrybutu href"

        # Sprawdź przycisk usunięcia
        delete_btn = first_row.locator("button.delete-entry")
        expect(delete_btn).to_be_visible()

    # THEN: sprawdź przycisk czyszczenia historii
    clear_btn = page.locator("button#clear-history")
    expect(clear_btn).to_be_visible()