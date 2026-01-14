import pytest

# These tests require pytest-playwright (or Playwright's pytest integration).
# They rely on the `page` fixture (Playwright) and the `e2e_server` fixture defined in conftest.


@pytest.mark.usefixtures('e2e_server')
class TestHomepageUserStories:
    def test_register_and_login(self, page, e2e_server):
        server = e2e_server
        page.goto(server)
        # Wait for header and open auth modal
        page.wait_for_selector('.header__cta-button', timeout=5000)
        page.click('.header__cta-button')

        # switch to register and wait for inputs
        page.wait_for_selector('#showRegister', timeout=2000)
        page.click('#showRegister')
        username = 'e2e_user'
        page.wait_for_selector('#registerForm', timeout=4000, state='visible')
        page.wait_for_selector('#registerForm input[name="username"]', timeout=4000, state='visible')
        page.fill('#registerForm input[name="username"]', username)
        page.fill('#registerForm input[name="email"]', f'{username}@example.com')
        page.fill('#registerForm input[name="password"]', 'P@ssw0rd123')
        page.fill('#registerForm input[name="password_confirm"]', 'P@ssw0rd123')

        # Submit registration and assert user exists using test admin API
        page.click('#registerForm .auth-submit')
        page.wait_for_timeout(500)  # small pause for server processing
        exists_resp = page.request.get(f'{server}/test/api/users/{username}/exists')
        assert exists_resp.ok
        assert exists_resp.json()['exists'] is True

        # Now login: open modal, fill and submit
        page.wait_for_selector('.header__cta-button', timeout=2000)
        page.click('.header__cta-button')
        page.wait_for_selector('#loginForm', timeout=4000, state='visible')
        page.wait_for_selector('#loginForm input[name="username"]', timeout=4000, state='visible')
        page.fill('#loginForm input[name="username"]', username)
        page.fill('#loginForm input[name="password"]', 'P@ssw0rd123')
        page.click('#loginForm .auth-submit')

        # Wait for user button to appear
        page.wait_for_selector('.header__user-button', timeout=3000)
        assert page.query_selector('.header__user-button') is not None

        # Cleanup: remove user via test admin API
        r = page.request.post(f'{server}/test/api/users/{username}/delete')
        assert r.status == 200

    def test_personalization_and_saved_tags(self, page, e2e_server):
        server = e2e_server
        username = 'tags_user'
        # Create & login first via direct register (reuse UI)
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

        # Login
        page.wait_for_selector('.header__cta-button', timeout=2000)
        page.click('.header__cta-button')
        page.wait_for_selector('#loginForm input[name="username"]', timeout=2000)
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', 'Password123')
        page.click('#loginForm .auth-submit')
        page.wait_for_selector('.header__user-button', timeout=3000)

        # Save tags via JS fetch to /auth/api/user/tags
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

        # Verify saved tags via GET
        tags_ok = page.evaluate("""async () => {
            const r = await fetch('/auth/api/user/tags', {credentials:'same-origin'});
            const j = await r.json();
            return j.success && j.tags && j.tags.length === 2;
        }""")
        assert tags_ok is True

        # Cleanup
        r = page.request.post(f'{server}/test/api/users/{username}/delete')
        assert r.status == 200

    def test_calendar_date_and_facts(self, page, e2e_server):
        server = e2e_server
        # Intercept holidays fetch and return a mock JSON
        def route_handler(route, request):
            route.fulfill(status=200, content_type='application/json', body='[{"name":"Dzień Testowy"}]')

        # Pattern used by script-calendar.js: https://pniedzwiedzinski.github.io/kalendarz-swiat-nietypowych/<month>/<day>.json
        page.route('https://pniedzwiedzinski.github.io/kalendarz-swiat-nietypowych/*/*', route_handler)

        page.goto(server)
        # Wait for calendar JS to run
        page.wait_for_selector('#calendarDate', timeout=5000)
        page.wait_for_selector('#calendarFact', timeout=5000)
        date_text = page.eval_on_selector('#calendarDate', 'el => el.textContent')
        fact_text = page.eval_on_selector('#calendarFact', 'el => el.textContent')
        assert date_text and date_text != 'Ładuję...'
        assert 'Dzień Testowy' in fact_text

    def test_responsiveness(self, page, e2e_server):
        server = e2e_server
        # Desktop
        page.set_viewport_size({'width': 1280, 'height': 800})
        page.goto(server)
        page.wait_for_selector('.left-column', timeout=3000)
        assert page.query_selector('.left-column') is not None

        # Mobile
        page.set_viewport_size({'width': 375, 'height': 667})
        page.goto(server)
        # ensure calendar exists and nav still present or togglable
        page.wait_for_selector('.calendar-widget', timeout=3000)
        assert page.query_selector('.calendar-widget') is not None

    def test_anonymous_access(self, page, e2e_server):
        server = e2e_server
        page.goto(server)
        page.wait_for_selector('.header__cta-button', timeout=3000)
        # As anonymous: login button visible, no user button
        assert page.query_selector('.header__cta-button') is not None
        assert page.query_selector('.header__user-button') is None

    def test_ui_consistency(self, page, e2e_server):
        server = e2e_server
        page.goto(server)
        # Wait and check header and footer exist and base CSS loaded
        page.wait_for_selector('.header', timeout=3000)
        page.wait_for_selector('.footer', timeout=3000)
        assert page.query_selector('.header') is not None
        assert page.query_selector('.footer') is not None
        # Check presence of main article classes used as pattern for other devs
        page.wait_for_selector('.main-article__title', timeout=3000)
        assert page.query_selector('.main-article__title') is not None
