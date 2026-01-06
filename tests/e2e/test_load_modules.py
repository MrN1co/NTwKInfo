# tests/e2e/test_load_modules.py
from playwright.sync_api import Page, expect

def test_load_modules(page:Page, e2e_server):
    page.goto(f"{e2e_server}/")
    page.get_by_role("link", name="Wiadomości").click()
    expect(page).to_have_url(f"{e2e_server}/news/news") # dodana linia
    expect(page.get_by_role("heading", name="Wiadomości")).to_be_visible() # dodana linia
    page.get_by_role("link", name="Pogoda").click()
    expect(page).to_have_url(f"{e2e_server}/weather/pogoda") # dodana linia
    #expect(page.get_by_role("heading", name="Pogoda")).to_be_visible() # dodana linia, brak taga <h1>
    page.get_by_role("link", name="Strona główna").click()
    page.goto(f"{e2e_server}/")
    expect(page).to_have_url(f"{e2e_server}/") # dodana linia
    page.get_by_role("button", name="Zaloguj się").click()
    expect(page).to_have_url(f"{e2e_server}/") # dodana linia
    page.get_by_role("textbox", name="Podaj nazwę użytkownika lub").click()
    page.get_by_role("textbox", name="Podaj nazwę użytkownika lub").fill("user")
    page.get_by_role("textbox", name="Wpisz hasło").click()
    page.get_by_role("textbox", name="Wpisz hasło").fill("user123")
    page.get_by_role("button", name="Potwierdź ↗").click()
    page.get_by_role("link", name="🏠 Strona główna").click()
    page.goto(f"{e2e_server}/")
    page.get_by_role("link", name="user").click()
    page.get_by_role("link", name="📰 Wiadomości").click()
    page.get_by_role("link", name="user").click()
    page.get_by_role("link", name="🚪 Wyloguj się").click()
    page.goto(f"{e2e_server}/?logout=success")
    expect(page).to_have_url(f"{e2e_server}/?logout=success") # dodana linia
    page.screenshot(path="test_gen2.png") #dodana linia

