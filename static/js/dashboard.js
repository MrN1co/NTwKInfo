function showChangePasswordModal() {
  document.getElementById('changePasswordModal').classList.remove('hidden');
}

function closeChangePasswordModal() {
  document.getElementById('changePasswordModal').classList.add('hidden');
}

function showEditProfileModal() {
  alert('Funkcja w przygotowaniu');
}

function showPreferencesModal() {
  alert('Funkcja w przygotowaniu');
}

// Handle change password form
document.getElementById('changePasswordForm').addEventListener('submit', function(e) {
  e.preventDefault();

  const formData = new FormData(this);
  const newPassword = formData.get('new_password');
  const confirmPassword = formData.get('confirm_password');

  if (newPassword !== confirmPassword) {
    alert('Nowe hasła nie są identyczne');
    return;
  }

  // TODO: Implement password change via AJAX
  alert('Funkcja zmiany hasła w przygotowaniu');
});

function testWeatherAlerts() {
  fetch('/weather/api/test-email', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then(response => response.json())
  .then(data => {
    if (data.success !== false) {
      alert('Test alertów pogodowych wykonany. Sprawdź konsolę serwera.');
    } else {
      alert('Błąd: ' + data.message);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Wystąpił błąd podczas testowania alertów.');
  });
}
