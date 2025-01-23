import { API_URLS, ROUTE_URLS } from './constants.js';
import { notificationService } from './services/notificationService.js';
import { authService } from './services/authService.js';

class EmployeeLogin {
  constructor() {
    this.form = document.getElementById('employeeLoginForm');
    if (this.form){
      this.setupEventListeners();
    }
  }

  setupEventListeners() {
    this.form.addEventListener('submit', this.handleSubmit.bind(this));
  }

  async handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this.form);
    const username = formData.get('username');
    const password = formData.get('password');

    try {
        const response = await fetch(API_URLS.AUTH.LOGIN_EMPLOYEE, {
            method: 'POST',
            headers: {
                'X-CSRFToken': authService.getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include',
        });

        const data = await response.json();
        console.log('Login response data:', data); 

        if (response.ok) {
            authService.setToken(data.token);
            authService.setUserType('employee');
            authService.setUsername(data.username);
            authService.setEmployeeId(data.employee_id); 
            notificationService.showNotification('Login successful', 'success');
            notificationService.connect();
            window.dispatchEvent(new Event('auth-change'));
            window.location.href = `${window.location.origin}${data.redirect}`;
        } else {
            notificationService.showNotification(data.error || 'Login failed', 'danger'); // 'error' yerine 'danger'
        }
    } catch (error) {
        console.error('Error:', error);
        notificationService.showNotification('An error occurred. Please try again.', 'danger'); // 'error' yerine 'danger'
    }
  }
}
document.addEventListener('DOMContentLoaded', () => {
  new EmployeeLogin();
});