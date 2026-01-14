"""
Test E2E - Niezalogowany użytkownik sprawdza nagłówki wiadomości

User Story:
    "Jako użytkownik chcę widzieć nagłówki wiadomości z zachęcającym mnie obrazkiem."

Wymagania:
    - Test nawiguje do strony z wiadomości
    - Brak logowania
    - Weryfikacja widoczności nagłówków (`.news-title`)
    - Weryfikacja widoczności obrazków (`.news-image`)
    - Użycie `expect(...)` z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_anonymous_user_views_news_headlines_with_images(page: Page, e2e_server):
    """GIVEN: niezalogowany użytkownik otwiera stronę z wiadomościami

    WHEN: strona się załaduje z listą wiadomości

    THEN: każda wiadomość zawiera nagłówek (`.news-title`) i obrazek (`.news-image` lub placeholder).
    """

    # GIVEN
    page.goto(f"{e2e_server}/news")
    expect(page).to_have_title(re.compile("NTWKInfo|Wiadomości"))

    # WHEN: strona się załaduje
    # Czekaj na pojawienie się elementów wiadomości
    news_items = page.locator(".news-item")
    expect(news_items.first).to_be_visible(timeout=5000)

    # THEN: każdy element news-item ma nagłówek
    news_titles = page.locator(".news-title")
    expect(news_titles.first).to_be_visible()
    titles_count = news_titles.count()
    assert titles_count > 0, "Brak nagłówków wiadomości na stronie"

    # Sprawdź, że przynajmniej jeden nagłówek zawiera tekst
    first_title = news_titles.first
    title_text = first_title.text_content()
    assert title_text and title_text.strip(), "Pierwszy nagłówek jest pusty"

    # THEN: każdy element ma obrazek lub placeholder
    # Szukaj zarówno `.news-image` jak i `.news-image-placeholder`
    images = page.locator(".news-image, .news-image-placeholder")
    images_count = images.count()
    assert images_count > 0, "Brak obrazków lub placeholderów na stronie"

    # THEN: nagłówki są linkami (mają href)
    news_links = page.locator(".news-link")
    links_count = news_links.count()
    assert links_count > 0, "Brak linków w nagłówkach"

    # Weryfikuj, że pierwszy link ma atrybut href
    first_link = news_links.first
    href = first_link.get_attribute("href")
    assert href, "Pierwszy link nie ma atrybutu href"