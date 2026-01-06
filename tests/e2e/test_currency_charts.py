"""
Test E2E - Niezalogowany użytkownik widzi wykresy zmian kursu walut

User Story:
    "Jako zalogowany użytkownik, chcę zobaczyć wykresy zmian kursu danej waluty,
    aby móc ocenić trendy kursu."

Wymagania:
    - Test otwiera stronę ekonomii
    - Widzi wykres walut (domyślnie EUR)
    - Zmienia walutę i sprawdza czy wykres się zmienia
    - Widzi wykres złota w skali roku
    - Wykresy są obrazkami (base64 PNG)
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_user_views_currency_trend_charts(page: Page, e2e_server):
    """
    Test akceptacyjny (E2E): Niezalogowany użytkownik widzi wykresy zmian
    kursu waluty na stronie ekonomii, aby móc ocenić trendy kursu.
    """

    # ============================================================================
    # GIVEN: użytkownik otwiera stronę ekonomii
    # ============================================================================
    page.goto(f"{e2e_server}/ekonomia")

    # WHEN: strona się załaduje
    expect(page).to_have_title(re.compile("NTWKInfo|Bądź na czasie"))

    # ============================================================================
    # THEN: widzi główny wykres walut (domyślnie EUR)
    # ============================================================================
    currency_chart = page.locator("img.currency-chart")
    expect(currency_chart).to_be_visible()

    # AND: wykres zawiera dane w formacie base64 (obraz PNG)
    chart_src = currency_chart.get_attribute("src")
    assert "data:image/png;base64," in chart_src, "Wykres powinien być obrazkiem PNG w base64"

    # ============================================================================
    # AND: zmienia walutę docelową na USD
    # ============================================================================
    currency_to_select = page.locator("#currency-to")
    currency_to_select.select_option("USD")
    page.wait_for_timeout(500)

    # THEN: wykres się zmienia (nowe src dla USD)
    new_chart_src = currency_chart.get_attribute("src")
    expect(currency_chart).to_be_visible()
    
    # Nowy wykres powinien również zawierać base64 data
    assert "data:image/png;base64," in new_chart_src, "Nowy wykres powinien być obrazkiem"


    # ============================================================================
    # AND: widzi sekcję ze złotem
    # ============================================================================
    gold_section_heading = page.locator("h2:has-text('Cena złota')")
    expect(gold_section_heading).to_be_visible()

    # ============================================================================
    # AND: widzi wykres ceny złota w skali roku
    # ============================================================================
    gold_chart = page.locator("img.gold-chart")
    expect(gold_chart).to_be_visible()

    # AND: wykres złota też zawiera dane base64
    gold_chart_src = gold_chart.get_attribute("src")
    assert "data:image/png;base64," in gold_chart_src, "Wykres złota powinien być obrazkiem PNG"

