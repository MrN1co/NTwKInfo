"""
Test E2E - Niezalogowany użytkownik filtruje wiadomości po kategorii

User Story:
    "Jako użytkownik chcę wybrać kategorię (np. Sport),
    aby widzieć tylko wiadomości z wybranej kategorii."

Wymagania:
    - Test nawiguje do strony z wiadomości (`/news`)
    - Brak logowania
    - Weryfikacja, że kliknięcie przycisku kategorii powoduje filtrowanie
    - Użycie `expect(...)` oraz asercji Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_anonymous_user_filters_news_by_category(page: Page, e2e_server):
    """GIVEN: niezalogowany użytkownik otwiera stronę z wiadomościami

    WHEN: kliknie przycisk kategorii (np. "Sport")

    THEN: przycisk otrzymuje klasę aktywną, a widoczne elementy `.news-item`
    zawierają wybraną kategorię w atrybucie `data-tags`.
    """

    # GIVEN
    page.goto(f"{e2e_server}/news")
    expect(page).to_have_title(re.compile("NTWKInfo|Wiadomości"))

    # Upewnij się, że przyciski tagów są widoczne
    tag_button = page.locator("button.tag-btn", has_text="Sport")
    expect(tag_button).to_be_visible()

    # WHEN: klikamy kategorię 'Sport'
    tag_button.click()

    # THEN: przycisk powinien mieć klasę 'active'
    btn_class = tag_button.get_attribute("class") or ""
    assert "active" in btn_class.split(), "Przycisk kategorii nie otrzymał klasy 'active'"

    # Sprawdź wszystkie widoczne elementy .news-item — muszą zawierać tag 'sport'
    items = page.locator(".news-item")
    count = items.count()

    visible_found = False
    for i in range(count):
        item = items.nth(i)
        if item.is_visible():
            visible_found = True
            tags_raw = (item.get_attribute("data-tags") or "").lower()
            assert "sport" in tags_raw.split(",") or "sport" in tags_raw, (
                f"Widoczny element nie zawiera tagu 'sport': {tags_raw}"
            )

    assert visible_found, "Brak widocznych elementów wiadomości po zastosowaniu filtra 'Sport'"
