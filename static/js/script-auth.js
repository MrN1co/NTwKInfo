// LOGIKA LOGOWANIA I REJESTRACJI
const loginBtn = document.querySelector(".header__cta-button");
const userBtn = document.querySelector(".header__user-button");
const overlay = document.getElementById("authOverlay");
const modal = document.getElementById("authModal");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const closeButtons = document.querySelectorAll(".auth-close");

const showRegister = document.getElementById("showRegister");
const showLogin = document.getElementById("showLogin");

// Helper function to open modal
function openModal(form = 'login') {
  overlay.classList.remove("hidden");
  modal.classList.remove("hidden");
  if (form === 'register') {
    loginForm.classList.add("hidden");
    registerForm.classList.remove("hidden");
  } else {
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
  }
}

// Helper function to close modal
function closeModal() {
  overlay.classList.add("hidden");
  modal.classList.add("hidden");
}

// Disabled auto-opening modal on page load - only open when button clicked
// function checkAuthParam() {
//   const params = new URLSearchParams(window.location.search);
//   const authParam = params.get('auth');
//   if (authParam === 'login' || authParam === 'register') {
//     openModal(authParam);
//   }
// }

// No auto-opening on page load
// document.addEventListener('DOMContentLoaded', checkAuthParam);

// Handle login button (shows modal when not logged in)
if (loginBtn && overlay && modal) {
  loginBtn.addEventListener("click", () => {
    openModal('login');
  });

  closeButtons.forEach(btn => btn.addEventListener("click", closeModal));
  overlay.addEventListener("click", closeModal); 

  // Przejście do rejestracji
  if (showRegister) {
    showRegister.addEventListener("click", (e) => {
      e.preventDefault();
      openModal('register');
    });
  }

  // Przejście do logowania
  if (showLogin) {
    showLogin.addEventListener("click", (e) => {
      e.preventDefault();
      openModal('login');
    });
  }
}

// Handle user button (redirects to dashboard when logged in) - no additional JS needed
// The href attribute in the template handles the redirect
