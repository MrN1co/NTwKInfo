from playwright.sync_api import Page, expect

def test_anonymous_user_weather(page:Page, e2e_server):
    # GIVEN: użytkownik niezalogowany
    page.goto(f"{e2e_server}/weather/pogoda")

    # THEN: widzi podstawowe dane pogodowe
    expect(page.locator("#currentTemp")).to_be_visible()
    expect(page.locator("#currentPressure")).to_be_visible()
    expect(page.locator("#currentPrecip")).to_be_visible()

    # AND: widzi nazwę domyślnej lokalizacji
    expect(page.locator("text=Kraków")).to_be_visible()
