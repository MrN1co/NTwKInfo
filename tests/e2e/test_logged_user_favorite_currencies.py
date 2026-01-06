"""
Test E2E - Zalogowany użytkownik zapisuje ulubione waluty

User Story:
    "Jako zalogowany użytkownik, chce mieć możliwość zapisać najczęściej 
    używane przeze mnie waluty, aby móc je szybko sprawdzać."

Wymagania:
    - Test loguje użytkownika
    - Nawiguje do strony ekonomii
    - Klika na karty walut aby otworzyć modal ulubionych
    - Zaznacza do 3 walut jako ulubione
    - Zapisuje ulubione waluty
    - Użycie expect(...) z Playwright
    - Struktura Given / When / Then
"""

from playwright.sync_api import Page, expect
import re


def test_logged_user_saves_favorite_currencies(page: Page, e2e_server, app):
    """
    Test akceptacyjny (E2E): Zalogowany użytkownik zapisuje ulubione waluty
    do szybkiego dostępu poprzez interfejs modalny.
    """
    from modules.database import User
    
    # Setup: Utwórz testowego użytkownika
    test_username = "testuser_fav"
    test_password = "testpass123"
    with app.app_context():
        existing_user = User.query.filter_by(username=test_username).first()
        if existing_user:
            User.query.filter_by(username=test_username).delete()
        User.create(test_username, f"{test_username}@test.com", test_password)
    
    # ============================================================================
    # GIVEN: zalogowany użytkownik otwiera stronę główną
    # ============================================================================
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

    # ============================================================================
    # WHEN: zalogowany użytkownik nawiguje do strony ekonomii
    # ============================================================================
    page.goto(f"{e2e_server}/ekonomia")

    # THEN: strona ekonomii się załaduje
    expect(page).to_have_title(re.compile("NTWKInfo|Bądź na czasie"))

    # ============================================================================
    # THEN: widzi karty z kursami walut
    # ============================================================================
    currency_boxes = page.locator("div.currency-box")
    expect(currency_boxes.first).to_be_visible()

    # ============================================================================
    # AND: klika na kartę EUR aby otworzyć modal ulubionych
    # ============================================================================
    eur_box = page.locator("div.currency-box[data-currency='EUR']")
    expect(eur_box).to_be_visible()
    eur_box.click()

    # AND: czeka na pojawienie się modalu z checkboxami
    page.wait_for_selector("#favoritesModal", timeout=3000)
    modal = page.locator("#favoritesModal")
    expect(modal).to_be_visible()

    # ============================================================================
    # AND: w modalu zaznacza EUR jako ulubioną
    # ============================================================================
    eur_checkbox = page.locator("#favoritesCheckboxes input[value='EUR']")
    expect(eur_checkbox).to_be_visible()
    if not eur_checkbox.is_checked():
        eur_checkbox.click()
    
    page.wait_for_timeout(200)

    # ============================================================================
    # AND: zaznacza USD jako ulubioną
    # ============================================================================
    usd_checkbox = page.locator("#favoritesCheckboxes input[value='USD']")
    if usd_checkbox.is_visible() and not usd_checkbox.is_checked():
        usd_checkbox.click()
    
    page.wait_for_timeout(200)

    # ============================================================================
    # THEN: klika przycisk "Zapisz"
    # ============================================================================
    save_btn = page.locator("#saveFavModal")
    expect(save_btn).to_be_visible()
    save_btn.click()

    page.wait_for_timeout(500)

    # ============================================================================
    # AND: przeładowuje stronę
    # ============================================================================
    page.reload()

    # THEN: najpopularniejsze waluty powinny być widoczne w currency-scroll
    eur_box_after_reload = page.locator(".currency-scroll div.currency-box[data-currency='EUR']")
    usd_box_after_reload = page.locator(".currency-scroll div.currency-box[data-currency='USD']")
    
    expect(eur_box_after_reload).to_be_visible()
    expect(usd_box_after_reload).to_be_visible()
