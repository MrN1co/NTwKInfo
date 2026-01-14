# Prowadzenie projektu (`project_management.md`)

> **Plik informacyjny – dokumentuje sposób realizacji projektu**  

---

## 1. Kontekst akademicki projektu

Projekt został zrealizowany w ramach **zajęć laboratoryjnych z przedmiotu _Inżynieria Oprogramowania_**,  
prowadzonych na kierunku **Nowoczesne Technologie w Kryminalistyce** na **V semestrze studiów (rok akademicki 2025/2026)**  
w **Akademii Górniczo-Hutniczej im. Stanisława Staszica w Krakowie**.

Celem projektu było praktyczne zastosowanie zasad inżynierii oprogramowania,
w szczególności pracy zespołowej, metodyki Scrum, projektowania architektury
oraz tworzenia dokumentacji technicznej aplikacji webowej.

---

## 2. Metodologia prowadzenia projektu

Projekt był realizowany zgodnie z metodyką **Scrum**, z iteracyjnym podejściem do rozwoju oprogramowania.

- wymagania funkcjonalne zapisywane jako **User Stories**
- planowanie pracy w **sprintach**
- regularne przeglądy postępów
- podział odpowiedzialności pomiędzy zespoły modułowe

Metodyka Scrum pozwoliła na stopniowe rozwijanie funkcjonalności aplikacji
oraz ciągłą weryfikację postępów prac.

---

## 3. User Stories

Wymagania funkcjonalne projektu zostały zapisane w postaci **User Stories** w narzędziu Jira.

### Przykładowa User Story

> **US-101**  
> Jako użytkownik niezalogowanychcę zobaczyć informacje o temperaturze, opadach i ciśnieniu dla domyślnej lokalizacji,<br>
> aby od razu mieć dostęp do podstawowych danych pogodowych bez konieczności podejmowania akcji.

Każda User Story posiadała:
- jednoznaczny opis funkcjonalności
- kryteria akceptacji
- powiązane zadania techniczne (taski)
- przypisanie do sprintu

User Stories stanowiły podstawę zarówno do implementacji funkcji,
jak i do tworzenia **testów akceptacyjnych (Playwright)**.

---

## 4. Sprinty

Projekt został podzielony na sprinty, zgodnie z poniższym harmonogramem.

Poniższa tabela prezentuje **plan i realizację sprintów** projektu:

| Sprint   | Cel / Kamień milowy                     | Opis                                                                 | Zależność       | Start       | Koniec      | Zajęcia |
|---------:|-----------------------------------------|----------------------------------------------------------------------|-----------------|-------------|-------------|---------|
| Sprint 0 | Planowanie                              | Zdefiniowanie wymagań i harmonogramu.<br>Zapis Epików i User Stories | brak            | 09.10.2025  | 16.10.2025  | 2,3     |
| Sprint 1 | Analiza wymagań,<br>Projektowanie aplikacji | Zdefiniowanie architektury, dobór bibliotek, analiza dostępności serwisów.<br>Stworzenie środowiska pracy grupowej. | Od Sprintu 0    | 16.10.2025  | 30.10.2025  | 4,5     |
| Sprint 2 | Prototyp                                | Stworzenie podstawowej struktury aplikacji i bibliotek wspólnych     | Od Sprintu 1    | 30.10.2025  | 13.11.2025  |  6,7     |
| Sprint 3 | Implementacja                           | Pełna implementacja modułów aplikacji                                | Od Sprintu 2    | 13.11.2025  | 27.11.2025  |  8,9     |
| Sprint 4 | Integracja i testowanie                 | Testy modułów i całości aplikacji                                    | Od Sprintu 3    | 27.11.2025  | 18.12.2025  |  10,11   |
| Sprint 5 | Finalizacja i dokumentacja              | Ostateczne poprawki i przygotowanie dokumentacji                     | Od Sprintu 4    | 18.12.2025  | 15.01.2026  |  12,13   |



Sprinty umożliwiły zespołom stopniowe dostarczanie funkcjonalności,
a także ocenę postępów i wprowadzanie korekt w kolejnych iteracjach.

---

## 5. Narzędzie Jira

Do zarządzania projektem wykorzystano narzędzie **Jira**, do którego dostęp
posiadali wszyscy członkowie zespołu projektowego oraz prowadzący.

W Jira prowadzono:
- backlog produktu
- listę User Stories
- sprinty
- taski techniczne
- śledzenie postępów prac

Projekt Jira: **TU UZUPEŁNIĆ LINK**

---

## 6. Podział zespołów projektowych

Zespół projektowy został podzielony na cztery podzespoły,
z których każdy odpowiadał za jeden moduł aplikacji:

- **Zespół A** – Strona główna aplikacji
- **Zespół B** – Moduł pogodowy
- **Zespół C** – Moduł ekonomiczny
- **Zespół D** – Moduł wiadomości

Taki podział umożliwił równoległą realizację prac
oraz wyraźne przypisanie odpowiedzialności.

---

## 7. Repozytorium i hosting

Kod źródłowy projektu był przechowywany w repozytorium **GitHub**,
z wykorzystaniem pull requestów oraz code review.

- Repozytorium GitHub: **TU UZUPEŁNIĆ LINK**
- Hosting aplikacji: **Amazon Web Services (AWS)**

Aplikacja była wdrażana na środowisku chmurowym,
co umożliwiło dostęp do wersji demonstracyjnej projektu.

---

## 8. Zasady organizacyjne

- wszyscy członkowie zespołu mieli dostęp do Jiry i repozytorium
- prace były realizowane zgodnie z podziałem na zespoły modułowe
- zmiany w kodzie przechodziły przez pull requesty
- dokumentacja była integralną częścią Definition of Done

Plik ten stanowi formalny opis sposobu prowadzenia projektu
i jest punktem odniesienia dla pozostałej dokumentacji.
