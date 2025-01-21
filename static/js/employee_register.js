import { API_URLS, ROUTE_URLS } from './constants.js';
import { notificationService } from './services/notificationService.js';
import { authService } from './services/authService.js';

class EmployeeRegister {
  constructor() {
    this.form = document.getElementById('employeeRegisterForm');
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

    try {
      const response = await fetch(API_URLS.AUTH.REGISTER_EMPLOYEE, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': authService.getCookie('csrftoken')
        }
      });

      const data = await response.json();

      if (response.ok) {
          authService.setToken(data.token);
           authService.setUserType('employee');
           authService.setUsername(data.username);
          notificationService.showNotification('Employee registered successfully', 'success');
           notificationService.connect();  
           window.dispatchEvent(new Event('auth-change'));
        window.location.href = ROUTE_URLS.EMPLOYEE.DASHBOARD;
      } else {
        notificationService.showNotification(data.error || 'Registration failed', 'error');
      }
    } catch (error) {
      console.error('Error:', error);
      notificationService.showNotification('An error occurred. Please try again.', 'error');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new EmployeeRegister();
});