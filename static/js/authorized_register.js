import { API_URLS, ROUTE_URLS } from './constants.js';
import { notificationService } from './services/notificationService.js';
import { authService } from './services/authService.js';

class AuthorizedRegister {
    constructor() {
        this.form = document.getElementById('authorizedRegisterForm');
        if (this.form) {
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
            const response = await fetch(API_URLS.AUTH.REGISTER_AUTHORIZED, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': authService.getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (response.ok) {
                authService.setToken(data.token);
                authService.setUserType('authorized');
                authService.setUsername(data.username);
                notificationService.showNotification('Authorized user registered successfully', 'success');
                notificationService.connect(); 
                window.dispatchEvent(new Event('auth-change'));
                window.location.href = `${window.location.origin}${data.redirect}`;
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
    new AuthorizedRegister();
});