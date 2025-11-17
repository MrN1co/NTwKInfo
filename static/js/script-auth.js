// LOGIKA LOGOWANIA I REJESTRACJI
const loginBtn = document.querySelector(".header__cta-button");
const overlay = document.getElementById("authOverlay");
const modal = document.getElementById("authModal");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const closeButtons = document.querySelectorAll(".auth-close");

const showRegister = document.getElementById("showRegister");
const showLogin = document.getElementById("showLogin");

if (loginBtn && overlay && modal) {
  // Otwórz modal
  loginBtn.addEventListener("click", () => {
    overlay.classList.remove("hidden");
    modal.classList.remove("hidden");
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
  });

  // Zamknij modal
  function closeModal() {
    overlay.classList.add("hidden");
    modal.classList.add("hidden");
  }

  closeButtons.forEach(btn => btn.addEventListener("click", closeModal));
  overlay.addEventListener("click", closeModal);

  // Przejście do rejestracji
  if (showRegister) {
    showRegister.addEventListener("click", () => {
      loginForm.classList.add("hidden");
      registerForm.classList.remove("hidden");
    });
  }

  // Przejście do logowania
  if (showLogin) {
    showLogin.addEventListener("click", () => {
      registerForm.classList.add("hidden");
      loginForm.classList.remove("hidden");
    });
  }
}
