from playwright.sync_api import Page, expect
import modules.weather_app as weather_app

def login_user(page: Page):
    """Helper function to log in a test user via the modal."""
    # Click the login button to show modal
    page.click(".header__cta-button")
    
    # Fill the login form
    page.fill("[name='username']", "testuser")
    page.fill("[name='password']", "testpass")
    
    # Submit the form
    page.click("#loginForm button[type='submit']")
    
    # Wait for redirect or success
    page.wait_for_url("**/dashboard**")  # Assuming it redirects to dashboard

# userstory 1
def test_anonymous_user_weather(page:Page, e2e_server):
    # GIVEN: użytkownik niezalogowany
    page.goto(f"{e2e_server}/weather/pogoda")

    # THEN: widzi podstawowe dane pogodowe
    expect(page.locator("#currentTemp")).to_be_visible()
    expect(page.locator("#currentPressure")).to_be_visible()
    expect(page.locator("#currentPrecip")).to_be_visible()

    # AND: widzi nazwę domyślnej lokalizacji
    expect(page.locator("text=Kraków")).to_be_visible()

# userstory 2
def test_anonymous_user_can_search_location(page: Page, e2e_server):
    # GIVEN: użytkownik niezalogowany na stronie pogody
    page.goto(f"{e2e_server}/weather/pogoda")

    # WHEN: wpisuje miasto w pole wyszukiwania i klika szukaj
    page.fill("#cityInput", "Warszawa")
    page.click("#searchBtn")

    # THEN: wyświetla się pogoda dla Warszawy
    expect(page.locator("#cityName")).to_contain_text("Warszawa")

# userstory 3
def test_logged_in_user_sees_favorites_section(page: Page, e2e_server):
    # GIVEN: użytkownik zalogowany
    page.goto(f"{e2e_server}/")
    login_user(page)
    
    # WHEN: przechodzi do pogody
    page.goto(f"{e2e_server}/weather/pogoda")
    
    # THEN: sekcja ulubionych jest widoczna
    expect(page.locator("#favoritesSection")).to_be_visible()


def test_logged_in_user_can_add_and_view_favorite(page: Page, e2e_server):
    # GIVEN: użytkownik zalogowany
    page.goto(f"{e2e_server}/")
    login_user(page)
    page.goto(f"{e2e_server}/weather/pogoda")
    
    # WHEN: klika przycisk ulubionych dla aktualnego miasta
    page.click("#favoriteBtn")
    
    # THEN: miasto pojawia się w ulubionych
    expect(page.locator("#favoritesList")).to_contain_text("Kraków")
    
# userstory 4 i 5
def test_email_alerts_for_weather_conditions(page: Page, e2e_server):
    # GIVEN: użytkownik zalogowany z ulubioną lokalizacją
    page.goto(f"{e2e_server}/")
    login_user(page)
    
    # Dodaj Kraków do ulubionych
    page.goto(f"{e2e_server}/weather/pogoda")
    page.click("#favoriteBtn")  # Dodaj Kraków
    
    # WHEN: użytkownik klika przycisk testowania alertów pogodowych w dashboard
    page.goto(f"{e2e_server}/dashboard")
    # Zakładamy, że przycisk istnieje lub dodajemy go
    # Dla uproszczenia, wywołajmy endpoint bezpośrednio via fetch w przeglądarce
    page.evaluate("""
        fetch('/weather/api/test-email', { method: 'GET' })
        .then(response => response.json())
        .then(data => console.log('Email test result:', data))
    """)
    
    # THEN: email z alertami pogodowymi zostaje "wysłany" (w trybie testowym dodany do listy)
    # Sprawdź listę sent_emails
    assert len(weather_app.sent_emails) > 0, "Brak wysłanych e-maili"
    
    email = weather_app.sent_emails[-1]  # Ostatni e-mail
    assert email['to'] == 'test@example.com'
    assert 'Alert pogodowy' in email['subject']
    # Sprawdź, czy zawiera alert o opadach lub mrozie
    body = email['body'].lower()
    assert ('opady' in body or 'śnieg' in body or 'mróz' in body), f"Brak alertów w treści: {body}"
    

# userstory 6
def test_weather_icons_visible(page: Page, e2e_server):
    # GIVEN: użytkownik na stronie pogody
    page.goto(f"{e2e_server}/weather/pogoda")

    # THEN: widzi ikonę pogody
    expect(page.locator("#currentIcon")).to_be_visible()

# userstory 7
def test_7_day_forecast_visible(page: Page, e2e_server):
    # GIVEN: użytkownik na stronie pogody
    page.goto(f"{e2e_server}/weather/pogoda")

    # THEN: widzi prognozę na 7 dni (sprawdza obecność kart dni)
    expect(page.locator(".day-card")).to_have_count(7)

# userstory 8
def test_charts_visible_for_anonymous_user(page: Page, e2e_server):
    # GIVEN: użytkownik niezalogowany na stronie pogody
    page.goto(f"{e2e_server}/weather/pogoda")

    # THEN: widzi wykresy (sprawdza obecność canvas lub img dla wykresów)
    chart_canvas = page.locator("#chartCanvas")
    chart_img = page.locator("#chartImg")
    if chart_canvas.is_visible():
        expect(chart_canvas).to_be_visible()
    elif chart_img.is_visible():
        expect(chart_img).to_be_visible()
    else:
        # Jeśli nie ma wykresu, sprawdź czy jest sekcja wykresów
        expect(page.locator(".card-chart")).to_be_visible()

