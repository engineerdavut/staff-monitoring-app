import { authService } from './services/authService.js';
import { notificationService } from './services/notificationService.js';
import { TIME_CONSTANTS, API_URLS, ROUTE_URLS } from './constants.js';

class App {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.htmlElement = document.documentElement;
        this.logoutBtn = document.getElementById('logoutBtn');
        this.notificationsContainer = document.getElementById('notifications');
        this.savedTheme = localStorage.getItem('theme') || 'light';
         this.navbarElements = {
           homeLink: document.getElementById('homeLink'),
           employeeDashboardLink: document.getElementById('employeeDashboardLink'),
           authorizedDashboardLink: document.getElementById('authorizedDashboardLink'),
           detailedMonthlyReportLink: document.getElementById('detailedMonthlyReportLink'),
           loginDropdown: document.getElementById('loginDropdown'),
           registerDropdown: document.getElementById('registerDropdown'),
           employeeLoginLink: document.getElementById('employeeLoginLink'),
           authorizedLoginLink: document.getElementById('authorizedLoginLink'),
           employeeRegisterLink: document.getElementById('employeeRegisterLink'),
           authorizedRegisterLink: document.getElementById('authorizedRegisterLink')
         };
       }


    init() {
        this.setupTheme();
        this.setupEventListeners();
        this.initializeApp();
        this.updateNavbar();
    }

    setupTheme() {
        this.htmlElement.setAttribute('data-bs-theme', this.savedTheme);
        this.updateThemeToggleIcon(this.savedTheme);
    }

    setupEventListeners() {
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', this.handleThemeToggle.bind(this));
        }
        if (this.logoutBtn) {
            this.logoutBtn.addEventListener('click', this.handleLogout.bind(this));
        }
        window.addEventListener('auth-change', this.updateNavbar.bind(this));
    }

    handleThemeToggle() {
        const currentTheme = this.htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.htmlElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateThemeToggleIcon(newTheme);
    }

    updateThemeToggleIcon(theme) {
        if (this.themeToggle) {
            this.themeToggle.innerHTML = theme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        }
    }

    async handleLogout(e) {
        e.preventDefault();
        try {
            await authService.logout();
            window.location.href = ROUTE_URLS.HOME;
        } catch (error) {
            console.error('Logout error:', error);
            notificationService.showNotification('Logout failed. Please try again.', 'error');
        }
    }

    initializeApp() {
        if (authService.isAuthenticated()) {
            console.log('User is logged in.');
            this.setupDataRefresh();
        } else {
            console.log('User is not logged in.');
            this.hideAttendanceElements();
        }
        this.updateNavbar();
    }
      hideAttendanceElements() {
          const attendanceElements = document.querySelectorAll('.attendance-related');
          attendanceElements.forEach(el => el.style.display = 'none');
      }

      setupDataRefresh() {
        this.refreshData();
        setInterval(() => this.refreshData(), TIME_CONSTANTS.REFRESH_INTERVAL);
      }


    refreshData() {
        // Implement your data refresh logic here
          console.log('Refreshing data...');
    }

    updateNavbar() {
      const isLoggedIn = authService.isAuthenticated();
      const userType = authService.getUserType();
       console.log("Updating navbar - Is Logged In:", isLoggedIn, "User Type:", userType);
  
      this.setElementDisplay(this.navbarElements.homeLink, 'block');
      this.setElementDisplay(this.themeToggle, 'block');
  
      if (isLoggedIn) {
        this.updateNavbarForLoggedInUser(userType);
      } else {
        this.updateNavbarForLoggedOutUser();
      }
    }


    updateNavbarForLoggedInUser(userType) {
      console.log(userType);
        this.setElementDisplay(this.navbarElements.loginDropdown, 'none');
        this.setElementDisplay(this.navbarElements.registerDropdown, 'none');
        this.setElementDisplay(this.logoutBtn, 'block');
        this.setElementDisplay(this.navbarElements.employeeDashboardLink, userType === 'employee' ? 'block' : 'none');
        this.setElementDisplay(this.navbarElements.authorizedDashboardLink, userType === 'authorized' ? 'block' : 'none');
        this.setElementDisplay(this.navbarElements.detailedMonthlyReportLink, userType === 'authorized' ? 'block' : 'none');
    }
  
    updateNavbarForLoggedOutUser() {
          this.setElementDisplay(this.navbarElements.employeeDashboardLink, 'none');
          this.setElementDisplay(this.navbarElements.authorizedDashboardLink, 'none');
          this.setElementDisplay(this.navbarElements.detailedMonthlyReportLink, 'none');
          this.setElementDisplay(this.navbarElements.loginDropdown, 'block');
          this.setElementDisplay(this.navbarElements.registerDropdown, 'block');
          this.setElementDisplay(this.logoutBtn, 'none');
    }
    
     setElementDisplay(element, display) {
       if (element) {
         element.style.display = display;
         console.log(`Set ${element.id || element.className} display to ${display}`);
       } else {
         console.warn(`Element not found when trying to set display to ${display}`);
       }
     }
      setElementContent(element, content) {
         if (element) {
             element.textContent = content;
             console.log(`Set ${element.id || element.className} content to ${content}`);
         } else {
             console.warn(`Element not found when trying to set content to ${content}`);
         }
     }
}

document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});