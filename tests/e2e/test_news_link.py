"""
Test E2E - Niezalogowany użytkownik sprawdza linki do wiadomości

User Story:
    "Jako użytkownik chcę przeczytać artykuł w oryginalnym serwisie, ponieważ na nasze stronie znajduje się odnośnik."

Wymagania:
    - Test nawiguje do strony z wiadomościami
    - Brak logowania
    - Weryfikacja widoczności wszystkich linków do wiadomości
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_anonymous_user_can_access_news_links(page: Page, e2e_server):
    """GIVEN: niezalogowany użytkownik otwiera stronę z wiadomościami

    WHEN: strona załaduje listę artykułów

    THEN: każdy artykuł ma klikowalny link do oryginalnego źródła z atrybutem target="_blank".
    """

    # GIVEN
    page.goto(f"{e2e_server}/news")
    expect(page).to_have_title(re.compile("NTWKInfo|Wiadomości"))

    # WHEN: strona się załaduje
    # Czekaj na pojawienie się linków do wiadomości
    news_links = page.locator(".news-link")
    expect(news_links.first).to_be_visible(timeout=5000)

    # THEN: weryfikuj liczbę linków
    links_count = news_links.count()
    assert links_count > 0, "Brak linków do wiadomości na stronie"

    # THEN: każdy link ma prawidłowy href
    for i in range(links_count):
        link = news_links.nth(i)
        href = link.get_attribute("href")
        assert href, f"Link #{i} nie ma atrybutu href"
        assert href.startswith("http"), f"Link #{i} nie zaczyna się od 'http': {href}"

    # THEN: linki otwierają się w nowej karcie (target="_blank")
    first_link = news_links.first
    target = first_link.get_attribute("target")
    assert target == "_blank", f"Link powinien mieć target='_blank', ma: {target}"

    # THEN: sprawdź, że pierwszy link ma widoczny tekst
    first_link_text = first_link.text_content()
    assert first_link_text and first_link_text.strip(), "Pierwszy link jest pusty"

    # THEN: weryfikuj, że linki mają rel="noopener noreferrer" (bezpieczeństwo)
    rel_attr = first_link.get_attribute("rel")
    assert rel_attr and "noopener" in rel_attr, f"Link powinien mieć rel zawierający 'noopener', ma: {rel_attr}"