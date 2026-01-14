# Zasady pracy i kontrybucji (`contribution.md`) — TEMPLATE

---

## 1. Workflow Git

- main — stabilna wersja
- develop — integracja
- feature/* — prace zespołów

---

## 2. Commity

- krótkie, opisowe
- powiązane z ID z Jiry (np. US-123)

---

## 3. Pull Requesty

Każdy PR musi:
- przechodzić testy
- mieć opis zmian
- być powiązany z User Story

---

## 4. Definition of Done

- kod działa
- testy przechodzą
- dokumentacja zaktualizowana
- brak błędów statycznej analizy kodu

---


## 5 Statyczna analiza kodu (Linting)

W projekcie obowiązuje statyczna analiza kodu:
- Python: `flake8` (PEP 8),
- JavaScript: `eslint`.

Wymagania oraz sposób uruchamiania opisano w: `doc/testing.md` (sekcja „Statyczna analiza kodu”).

Statyczna analiza kodu jest **elementem Definition of Done**.

---

## 6. Code Review

- minimum 1 osoba
- brak komentarzy krytycznych

