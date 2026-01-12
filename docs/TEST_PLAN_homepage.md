# Test Plan for 'Strona główna' (Homepage) ✅

## Overview
This plan covers Unit, Integration and E2E tests for the homepage module per project test policy.

---

## Unit tests (2–3) ✅
| Test ID | Target | Description | Acceptance |
|---|---|---|---|
| U1 | helpers.select_featured_article | Returns first article or None when empty | Correct item returned / None on empty
| U2 | helpers.summarize | Trims long summaries and adds ellipsis | Output length <= max and ends with "..."
| U3 | helpers.format_published_date | Parses ISO/`YYYY-MM-DD` date and returns "DD Mon YYYY" | Known formats parsed, invalid returns empty

---
## Integration tests (HTML endpoints) ✅
| Test ID | Endpoint | Description | Acceptance |
|---|---:|---|---|
| I1 | GET / | Renders homepage with mocked news & rates | 200 OK + news titles and rates in HTML
| I2 | GET / | Renders fallback for empty news list | 200 OK + "Brak wiadomości" visible
| I3 | GET /news, /pogoda, /ekonomia | Route redirects / calls correct view | Expected redirect or response

Notes: external dependencies are mocked via monkeypatch to avoid HTTP/broken APIs.

---
## E2E tests (Playwright, 1 per User Story) ✅
For each User Story listed by the product owner there is one E2E test.

| Story ID | Story Summary | E2E test description |
|---|---|---|
| S1 | Admin: create/update/delete users | Register a user via UI, verify user exists via test admin API; update via saved tags API; cleanup DB
| S2 | Logged-in personalization | Login, call `/auth/api/user/tags` to save tags and verify they are persisted
| S3 | Register + Login | Register (modal), then login and reach dashboard
| S4 | Unified UI | Check presence of core header/footer and base CSS class names
| S5 | Date info on homepage | Ensure calendar shows date/day and server-supplied facts (mock holidays feed)
| S6 | Calendar facts | Intercept holidays fetch and verify fact text is displayed
| S7 | Responsiveness | Verify key elements render on mobile and desktop viewport sizes
| S8 | Anonymous access to info | As anonymous user open homepage and verify general information and CTA to login

Implementation notes:
- Playwright tests run against a short-lived test server (`e2e_server` fixture) started during test runtime.
- e2e tests use a small testing-only blueprint (`/test/api/users/...`) for existence checks and cleanup.

---
## Test artifacts and locations
- Unit tests: `tests/unit/main/test_helpers.py`
- Integration tests: `modules/main/tests/test_main_integration.py`
- E2E tests: `tests/e2e/test_homepage_user_stories.py` (+ `tests/e2e/conftest.py`)
- Test plan (this file): `docs/TEST_PLAN_homepage.md`

---
## How to run
- Unit & Integration: `pytest tests/unit tests/modules/main/tests` (ensure pytest and pytest-flask installed)
- E2E (requires Playwright): `pytest tests/e2e --headed` and ensure Playwright and browsers are installed. See README for Playwright installation.
