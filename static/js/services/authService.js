import { API_URLS, ROUTE_URLS } from '../constants.js';
import { notificationService } from './notificationService.js';

class AuthService {
    constructor() {
        this.TOKEN = 'token';
        this.AUTH_TOKEN = 'auth_token';
        this.USER_TYPE_KEY = 'user_type';
        this.USERNAME_KEY = 'username';
        this.EMPLOYEE_ID_KEY = 'employee_id'; 
    }

    setToken(token) {
        if (token) {
            localStorage.setItem(this.TOKEN, token);
            localStorage.setItem(this.AUTH_TOKEN, token);
            console.log('Authentication token set in localStorage:', token);
        } else {
            console.warn('Attempted to set null or undefined token');
        }
    }

    getToken() {
        const token = localStorage.getItem(this.TOKEN);
        const auth_token = localStorage.getItem(this.AUTH_TOKEN);
        console.log('Getting authentication token from localStorage:', token);
        if (!token) {
            console.warn('No authentication token found in localStorage');
        }
        return token;
    }

    setUserType(userType) {
        localStorage.setItem(this.USER_TYPE_KEY, userType);
    }

    getUserType() {
        return localStorage.getItem(this.USER_TYPE_KEY);
    }

    setUsername(username) {
        localStorage.setItem(this.USERNAME_KEY, username);
    }

    getUsername() {
        return localStorage.getItem(this.USERNAME_KEY);
    }

    setEmployeeId(employeeId) {
        if (employeeId) {
            localStorage.setItem(this.EMPLOYEE_ID_KEY, employeeId);
        } else {
            console.warn('Attempted to set null or undefined employee_id');
        }
    }

    getEmployeeId() {
        const employeeId = localStorage.getItem(this.EMPLOYEE_ID_KEY);
        if (!employeeId) {
            console.warn('No employee_id found in localStorage');
        }
        return employeeId;
    }

    clearAuth() {
        localStorage.removeItem(this.TOKEN);
        localStorage.removeItem(this.AUTH_TOKEN);
        localStorage.removeItem(this.USER_TYPE_KEY);
        localStorage.removeItem(this.USERNAME_KEY);
        localStorage.removeItem(this.EMPLOYEE_ID_KEY);
        console.log('Authentication tokens, user type, username, and employee_id removed from localStorage');
    }

    isAuthenticated() {
        const isLoggedIn = !!this.getToken();
        console.log('Is user logged in?', isLoggedIn);
        return isLoggedIn;
    }

    isEmployee() {
        return this.getUserType() === 'employee';
    }

    isAuthorized() {
        return this.getUserType() === 'authorized';
    }

    setAuthHeader(headers = {}) {
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Token ${token}`;
            console.log('Authorization header set:', headers['Authorization']);
        } else {
            console.warn('No token available for Authorization header');
        }
        return headers;
    }

    async authenticatedFetch(url, options = {}, userType = null) {
        let headers = this.setAuthHeader(options.headers || {});
        
        const csrftoken = this.getCookie('csrftoken');
        if (csrftoken) {
            headers['X-CSRFToken'] = csrftoken;
        }
    
        const mergedOptions = { ...options, headers };
    
        try {
            const response = await fetch(url, mergedOptions);
        
            if (response.status === 401) {
                this.clearAuth();
                const loginRoute = userType === 'authorized' ? ROUTE_URLS.AUTHORIZED.LOGIN : ROUTE_URLS.EMPLOYEE.LOGIN;
                window.location.href = loginRoute;
                throw new Error('Unauthorized');
            }
    
            if (!response.ok) {
                let errorData = {};
                try {
                    errorData = await response.json();
                } catch(jsonError) {
                    throw new Error(`An error occurred but no JSON could be parsed: ${response.statusText}`);
                }
    
                // Hem 'error' hem de 'message' alanlarını kontrol edin
                let errorMessage = '';
                if (errorData.error) {
                    errorMessage = Array.isArray(errorData.error) ? errorData.error.join(' ') : errorData.error;
                } else if (errorData.message) {
                    errorMessage = Array.isArray(errorData.message) ? errorData.message.join(' ') : errorData.message;
                } else {
                    errorMessage = `An error occurred: ${response.statusText}`;
                }
    
                console.log('AuthenticatedFetch Error Message:', errorMessage); 
    
                throw new Error(errorMessage || `An error occurred: ${response.statusText}`);
            }
    
            return response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }
    

    async logout() {
        try {
            const response = await fetch(API_URLS.AUTH.LOGOUT, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${this.getToken()}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                this.clearAuth();
                notificationService.disconnect(); // Close WebSocket connection
                notificationService.showNotification('Logout successful', 'success');
                window.location.href = ROUTE_URLS.HOME;
            } else {
                throw new Error('Logout failed');
            }
        } catch (error) {
            console.error('Logout error:', error);
            notificationService.showNotification('Logout failed. Please try again.', 'danger');
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

export const authService = new AuthService();