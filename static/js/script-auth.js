/**
 * OBSŁUGA MODALU LOGOWANIA I REJESTRACJI
 * 
 * Funkcjonalność:
 * - Otwarcie/zamknięcie modalu logowania i rejestracji
 * - Przełączanie pomiędzy formularzem logowania a rejestracją
 * - Obsługa klikania w overlay (tło) do zamknięcia modalu
 */

// ========== POBRANIE ELEMENTÓW DOM ==========
const loginBtn = document.querySelector(".header__cta-button");          // Przycisk "Zaloguj się"
const userBtn = document.querySelector(".header__user-button");          // Przycisk profilu użytkownika
const overlay = document.getElementById("authOverlay");                  // Overlay (tło zaciemniające)
const modal = document.getElementById("authModal");                      // Główny modal

const loginForm = document.getElementById("loginForm");                  // Formularz logowania
const registerForm = document.getElementById("registerForm");            // Formularz rejestracji

const closeButtons = document.querySelectorAll(".auth-close");           // Wszystkie przyciski zamknięcia (×)

const showRegister = document.getElementById("showRegister");            // Link "Zarejestruj się"
const showLogin = document.getElementById("showLogin");                  // Link "Zaloguj się"

// ========== FUNKCJE POMOCNICZE ==========

/**
 * Otwiera modal logowania lub rejestracji
 * @param {string} form - 'login' lub 'register' - określa który formularz pokazać
 */
function openModal(form = 'login') {
  overlay.classList.remove("hidden");    // Pokaż overlay
  modal.classList.remove("hidden");      // Pokaż modal
  
  // Ukryj/pokaż odpowiedni formularz
  if (form === 'register') {
    loginForm.classList.add("hidden");
    registerForm.classList.remove("hidden");
  } else {
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
  }
}

/**
 * Zamyka modal logowania/rejestracji
 */
function closeModal() {
  overlay.classList.add("hidden");       // Ukryj overlay
  modal.classList.add("hidden");         // Ukryj modal
}

// ========== OBSŁUGA ZDARZEŃ ==========

// Obsługa przycisku logowania (jeśli użytkownik nie jest zalogowany)
if (loginBtn && overlay && modal) {
  // Klik w przycisk "Zaloguj się" - otwarcie modalu
  loginBtn.addEventListener("click", () => {
    openModal('login');
  });

  // Klik w przycisk zamknięcia (×) - zamknięcie modalu
  closeButtons.forEach(btn => btn.addEventListener("click", closeModal));
  
  // Klik w overlay (tło) - zamknięcie modalu
  overlay.addEventListener("click", closeModal); 

  // ===== PRZEŁĄCZANIE MIĘDZY FORMULARZAMI =====
  
  // Link "Zarejestruj się" - przejście do formularza rejestracji
  if (showRegister) {
    showRegister.addEventListener("click", (e) => {
      e.preventDefault();
      openModal('register');
    });
  }

  // Link "Zaloguj się" - powrót do formularza logowania
  if (showLogin) {
    showLogin.addEventListener("click", (e) => {
      e.preventDefault();
      openModal('login');
    });
  }
}
