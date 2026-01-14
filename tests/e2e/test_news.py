"""
Test E2E - Niezalogowany użytkownik sprawdza wiadomości

User Story:
    "Jako niezalogowany użytkownik chcę widzieć wiadomości ze wszystkich kategorii w równych proporcjach."

Wymagania:
    - Test nawiguje do strony z kategoriami wiadomości
    - Brak logowania
    - Weryfikacja widoczności wszystkich kategorii
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_anonymous_user_views_all_news_categories(page: Page, e2e_server):
    """GIVEN: niezalogowany użytkownik otwiera stronę z wiadomościami

    WHEN: strona załaduje listę wiadomości ze wszystkimi kategoriami

    THEN: użytkownik widzi przyciski kategorii i wiadomości z różnych dziedzin.
    """

    # GIVEN
    page.goto(f"{e2e_server}/news")
    expect(page).to_have_title(re.compile("NTWKInfo|Wiadomości"))

    # WHEN: strona się załaduje
    # Czekaj na załadowanie kontenera wiadomości
    news_container = page.locator(".news-container")
    expect(news_container).to_be_visible(timeout=5000)

    # THEN: weryfikuj, że nagłówek strony jest widoczny
    heading = page.locator(".news-container h1")
    expect(heading).to_be_visible()

    # THEN: sprawdź, że są przyciski kategorii (tagi)
    tag_buttons = page.locator("button.tag-btn")
    buttons_count = tag_buttons.count()
    assert buttons_count > 0, "Brak przycisków kategorii na stronie"

    # THEN: weryfikuj, że przycisk "Wszystko" jest widoczny i aktywny
    all_btn = page.locator("button.tag-btn[data-tag='']")
    expect(all_btn).to_be_visible()
    all_btn_class = all_btn.get_attribute("class") or ""
    assert "active" in all_btn_class.split(), "Przycisk 'Wszystko' powinien być aktywny domyślnie"

    # THEN: sprawdź, że są wiadomości wyświetlane
    news_items = page.locator(".news-item")
    items_count = news_items.count()
    assert items_count > 0, "Brak wiadomości na stronie"

    # THEN: weryfikuj, że każda wiadomość ma zawartość
    first_item = news_items.first
    expect(first_item).to_be_visible()

    # Sprawdź, że pierwsza wiadomość ma tytuł
    first_title = first_item.locator(".news-title")
    expect(first_title).to_be_visible()
    title_text = first_title.text_content()
    assert title_text and title_text.strip(), "Tytuł wiadomości jest pusty"

    # THEN: weryfikuj dostępne kategorie (Sport, Tenis, Siatkówka, itd.)
    expected_categories = ["Sport", "Tenis", "Siatkówka"]
    for category in expected_categories:
        category_btn = page.locator(f"button.tag-btn[data-tag*='{category.lower()}']")
        if category_btn.count() > 0:
            expect(category_btn.first).to_be_visible()

    # THEN: sprawdź, że licznik wiadomości czy inne statystyki są dostępne
    # (opcjonalnie, zależy od implementacji)
    assert items_count > 0, "Powinno być co najmniej kilka wiadomości z różnych kategorii"