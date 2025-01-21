import { API_URLS, ROUTE_URLS } from './constants.js';
import { notificationService } from './services/notificationService.js';
import { authService } from './services/authService.js';

class AuthorizedLogin {
  constructor() {
    this.form = document.getElementById('authorizedLoginForm');
    if (this.form) {
      this.setupEventListeners();
    } else {
      console.error('Authorized login form not found');
    }
  }

  setupEventListeners() {
    this.form.addEventListener('submit', this.handleSubmit.bind(this));
  }

  async handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this.form);

    try {
      const response = await fetch(API_URLS.AUTH.LOGIN_AUTHORIZED, {
        method: 'POST',
        headers: {
          'X-CSRFToken': authService.getCookie('csrftoken'),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(Object.fromEntries(formData)),
         credentials: 'include',
      });

      const data = await response.json();

      if (response.ok) {
          authService.setToken(data.token);
          authService.setUserType('authorized');
          authService.setUsername(data.username);
          notificationService.showNotification('Login successful', 'success');
          notificationService.connect(); 
          window.dispatchEvent(new Event('auth-change'));
        window.location.href = `${window.location.origin}${data.redirect}`;
      } else {
        notificationService.showNotification(data.error || 'Login failed', 'error');
      }
    } catch (error) {
      console.error('Error:', error);
      notificationService.showNotification('An error occurred. Please try again.', 'error');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new AuthorizedLogin();
});

