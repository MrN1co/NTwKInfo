import pytest

@pytest.mark.usefixtures('e2e_server')
class TestHomepageUserStories:
    """
    Klasa testowa zawierająca testy end-to-end dla strony głównej aplikacji.
    
    Testuje scenariusze użytkownika dotyczące:
    - Rejestracji i logowania użytkownika
    - Personalizacji i zapisywania tagów użytkownika
    - Kalendarza i faktów dnia
    - Responsywności interfejsu
    - Dostępu dla użytkowników anonimowych
    - Spójności interfejsu użytkownika
    
    Wykorzystuje fixture 'e2e_server' do uruchamiania testowego serwera oraz
    fixture 'page' z biblioteki Playwright do interakcji z przeglądarką.
    """
    def test_register_and_login(self, page, e2e_server):
        """
        Test E2E scenariusza: Rejestracja i zalogowanie użytkownika.
        
        Kroki testu:
        1. Otwiera stronę główną
        2. Otwiera modal autoryzacji (przycisk CTA w nagłówku)
        3. Przechodzi do formularza rejestracji
        4. Wypełnia formularz rejestracji danymi testowymi
        5. Wysyła formularz
        6. Weryfikuje że użytkownik został stworzony (via API testowego)
        7. Otwiera modal autoryzacji ponownie
        8. Przechodzi do formularza logowania
        9. Wypełnia formularz logowania
        10. Weryfikuje że pojawił się przycisk użytkownika (logged in)
        11. Czyści dane - usuwa testowego użytkownika
        
        Args:
            page: Fixture Playwright - obiekt strony przeglądarki
            e2e_server: Fixture - URL testowego serwera
        """
        server = e2e_server
        page.goto(server)
   
        page.wait_for_selector('.header__cta-button', timeout=5000)
        page.click('.header__cta-button')

       
        page.wait_for_selector('#showRegister', timeout=2000)
        page.click('#showRegister')
        username = 'e2e_user'
        page.wait_for_selector('#registerForm', timeout=4000, state='visible')
        page.wait_for_selector('#registerForm input[name="username"]', timeout=4000, state='visible')
        page.fill('#registerForm input[name="username"]', username)
        page.fill('#registerForm input[name="email"]', f'{username}@example.com')
        page.fill('#registerForm input[name="password"]', 'P@ssw0rd123')
        page.fill('#registerForm input[name="password_confirm"]', 'P@ssw0rd123')

  
        page.click('#registerForm .auth-submit')
        page.wait_for_timeout(500)  # small pause for server processing
        exists_resp = page.request.get(f'{server}/test/api/users/{username}/exists')
        assert exists_resp.ok
        assert exists_resp.json()['exists'] is True

        
        page.wait_for_selector('.header__cta-button', timeout=2000)
        page.click('.header__cta-button')
        page.wait_for_selector('#loginForm', timeout=4000, state='visible')
        page.wait_for_selector('#loginForm input[name="username"]', timeout=4000, state='visible')
        page.fill('#loginForm input[name="username"]', username)
        page.fill('#loginForm input[name="password"]', 'P@ssw0rd123')
        page.click('#loginForm .auth-submit')

      
        page.wait_for_selector('.header__user-button', timeout=3000)
        assert page.query_selector('.header__user-button') is not None

        
        r = page.request.post(f'{server}/test/api/users/{username}/delete')
        assert r.status == 200

    def test_personalization_and_saved_tags(self, page, e2e_server):
        """
        Test E2E scenariusza: Personalizacja użytkownika i zapisywanie tagów.
        
        Kroki testu:
        1. Tworzy nowego użytkownika poprzez formularz rejestracji
        2. Loguje się jako ten użytkownik
        3. Wysyła żądanie POST do /auth/api/user/tags z tagami ['sport','weather']
        4. Weryfikuje że tagi zostały zapisane wykonując GET do /auth/api/user/tags
        5. Sprawdza że zwrócone dane zawierają dokładnie 2 tagi
        6. Czyści dane - usuwa testowego użytkownika
        
        Test sprawdza funkcjonalność personalizacji strony poprzez zapisywane preferencje.
        
        Args:
            page: Fixture Playwright - obiekt strony przeglądarki
            e2e_server: Fixture - URL testowego serwera
        """
        server = e2e_server
        username = 'tags_user'

        page.goto(server)
        page.wait_for_selector('.header__cta-button', timeout=5000)
        page.click('.header__cta-button')
        page.wait_for_selector('#showRegister', timeout=2000)
        page.click('#showRegister')
        page.wait_for_selector('#registerForm', timeout=4000, state='visible')
        page.wait_for_selector('#registerForm input[name="username"]', timeout=4000, state='visible')
        page.fill('#registerForm input[name="username"]', username)
        page.fill('#registerForm input[name="email"]', f'{username}@example.com')
        page.fill('#registerForm input[name="password"]', 'Password123')
        page.fill('#registerForm input[name="password_confirm"]', 'Password123')
        page.click('#registerForm .auth-submit')
        page.wait_for_timeout(500)

     
        page.wait_for_selector('.header__cta-button', timeout=2000)
        page.click('.header__cta-button')
        page.wait_for_selector('#loginForm input[name="username"]', timeout=2000)
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', 'Password123')
        page.click('#loginForm .auth-submit')
        page.wait_for_selector('.header__user-button', timeout=3000)

        resp = page.evaluate("""async () => {
            const r = await fetch('/auth/api/user/tags', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'same-origin',
                body: JSON.stringify({tags: ['sport','weather']})
            });
            return r.ok;
        }""")
        assert resp is True

        
        tags_ok = page.evaluate("""async () => {
            const r = await fetch('/auth/api/user/tags', {credentials:'same-origin'});
            const j = await r.json();
            return j.success && j.tags && j.tags.length === 2;
        }""")
        assert tags_ok is True

       
        r = page.request.post(f'{server}/test/api/users/{username}/delete')
        assert r.status == 200

    def test_calendar_date_and_facts(self, page, e2e_server):
        """
        Test E2E scenariusza: Wyświetlanie kalendarza i faktów dnia.
        
        Kroki testu:
        1. Konfiguruje przechwyty żądań HTTP (route handler) aby mockować 
           zewnętrzne API faktów dnia z kalendarza
        2. Otwiera stronę główną
        3. Czeka aż elementy kalendarza będą widoczne (#calendarDate, #calendarFact)
        4. Pobiera tekst z elementu daty kalendarza
        5. Pobiera tekst z elementu faktów kalendarza
        6. Weryfikuje że data nie zawiera tekstu "Ładuję..." (wskazuje na załadowanie)
        7. Weryfikuje że fakt zawiera mock'owany tekst "Dzień Testowy"
        
        Test sprawdza że skrypt kalendarza się poprawnie załadował i renderuje dane.
        
        Args:
            page: Fixture Playwright - obiekt strony przeglądarki
            e2e_server: Fixture - URL testowego serwera
        """
        server = e2e_server
        
        def route_handler(route, request):
            """Handler do przechwytu żądań do API faktów dnia"""
            route.fulfill(status=200, content_type='application/json', body='[{"name":"Dzień Testowy"}]')

   
        page.route('https://pniedzwiedzinski.github.io/kalendarz-swiat-nietypowych/*/*', route_handler)

        page.goto(server)
      
        page.wait_for_selector('#calendarDate', timeout=5000)
        page.wait_for_selector('#calendarFact', timeout=5000)
        date_text = page.eval_on_selector('#calendarDate', 'el => el.textContent')
        fact_text = page.eval_on_selector('#calendarFact', 'el => el.textContent')
        assert date_text and date_text != 'Ładuję...'
        assert 'Dzień Testowy' in fact_text

    def test_responsiveness(self, page, e2e_server):
        """
        Test E2E scenariusza: Responsywność interfejsu na różnych rozmiarach ekranu.
        
        Kroki testu:
        1. Ustawia viewport na rozmiar pulpitu (1280x800)
        2. Otwiera stronę główną
        3. Weryfikuje że element `.left-column` istnieje (layout desktop)
        4. Zmienia viewport na rozmiar mobilny (375x667)
        5. Otwiera stronę głównie ponownie
        6. Weryfikuje że widżet kalendarza istnieje (widoczny na mobile)
        
        Test sprawdza że strona odpowiada prawidłowo na różne rozmiary ekranu
        i że elementy są dostępne zarówno na pulpicie jak i na urządzeniach mobilnych.
        
        Args:
            page: Fixture Playwright - obiekt strony przeglądarki
            e2e_server: Fixture - URL testowego serwera
        """
        server = e2e_server
   
        page.set_viewport_size({'width': 1280, 'height': 800})
        page.goto(server)
        page.wait_for_selector('.left-column', timeout=3000)
        assert page.query_selector('.left-column') is not None

    
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto(server)
      
        page.wait_for_selector('.calendar-widget', timeout=3000)
        assert page.query_selector('.calendar-widget') is not None

    def test_anonymous_access(self, page, e2e_server):
        """
        Test E2E scenariusza: Dostęp do strony głównej jako użytkownik anonimowy.
        
        Kroki testu:
        1. Otwiera stronę główną bez logowania
        2. Czeka aż przycisk CTA (call-to-action - zaloguj się) będzie widoczny
        3. Weryfikuje że przycisk logowania istnieje
        4. Weryfikuje że przycisk użytkownika NIE istnieje (nie zalogowany)
        
        Test sprawdza że interfejs prawidłowo wyświetla opcje dla użytkownika anonimowego
        (logowanie zamiast profilu).
        
        Args:
            page: Fixture Playwright - obiekt strony przeglądarki
            e2e_server: Fixture - URL testowego serwera
        """
        server = e2e_server
        page.goto(server)
        page.wait_for_selector('.header__cta-button', timeout=3000)
       
        assert page.query_selector('.header__cta-button') is not None
        assert page.query_selector('.header__user-button') is None

    def test_ui_consistency(self, page, e2e_server):
        """
        Test E2E scenariusza: Spójność interfejsu użytkownika.
        
        Kroki testu:
        1. Otwiera stronę główną
        2. Czeka aż nagłówek będzie widoczny i weryfikuje jego istnienie
        3. Czeka aż stopka będzie widoczna i weryfikuje jej istnienie
        4. Czeka aż tytuł artykułu (main-article__title) będzie widoczny
        5. Weryfikuje że tytuł artykułu istnieje
        
        Test sprawdza podstawową strukturę HTML strony i że główne komponenty
        (header, footer, artykuły) są prawidłowo renderowane. 
        
        Klasy CSS używane w tym teście (np. main-article__title) są wzorem 
        dla innych deweloperów pracujących nad modułami.
        
        Args:
            page: Fixture Playwright - obiekt strony przeglądarki
            e2e_server: Fixture - URL testowego serwera
        """
        server = e2e_server
        page.goto(server)
   
        page.wait_for_selector('.header', timeout=3000)
        page.wait_for_selector('.footer', timeout=3000)
        assert page.query_selector('.header') is not None
        assert page.query_selector('.footer') is not None

        page.wait_for_selector('.main-article__title', timeout=3000)
        assert page.query_selector('.main-article__title') is not None
