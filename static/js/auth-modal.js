// Handle AJAX form submission for login/register modals
document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.querySelector('#loginForm form');
  const registerForm = document.querySelector('#registerForm form');
  
  // Helper function to display error in modal
  function showError(form, message) {
    // Remove existing error if any
    const existingError = form.querySelector('.auth-error');
    if (existingError) {
      existingError.remove();
    }
    
    // Create and insert error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'auth-error';
    errorDiv.textContent = message;
    form.insertBefore(errorDiv, form.firstChild);
  }
  
  // Helper function to clear errors
  function clearError(form) {
    const existingError = form.querySelector('.auth-error');
    if (existingError) {
      existingError.remove();
    }
  }
  
  // Handle login form submission
  if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(loginForm);
      
      fetch('/auth/login', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        return response.json().then(data => {
          if (response.ok && data.success) {
            // Successful login
            clearError(loginForm);
            // Redirect after brief delay to show success state
            setTimeout(() => {
              window.location.href = data.redirect;
            }, 500);
          } else {
            // Show error in modal (handles both 401 and success:false cases)
            showError(loginForm, data.message);
          }
        });
      })
      .catch(error => {
        showError(loginForm, 'Błędny login lub hasło. Proszę spróbuj ponownie.');
        console.error('Error:', error);
      });
    });
  }
  
  // Handle register form submission
  if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(registerForm);
      
      fetch('/auth/register', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => {
        return response.json().then(data => {
          if (response.ok && data.success) {
            // Successful registration
            clearError(registerForm);
            // Show success message and redirect to login
            showError(registerForm, '✓ ' + data.message);
            setTimeout(() => {
              window.location.href = data.redirect;
            }, 1000);
          } else {
            // Show error in modal (handles HTTP error status codes)
            showError(registerForm, data.message);
          }
        });
      })
      .catch(error => {
        showError(registerForm, 'Wystąpił błąd. Proszę spróbuj ponownie.');
        console.error('Error:', error);
      });
    });
  }
});
