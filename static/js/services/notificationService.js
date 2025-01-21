// services/notificationService.js

import { API_URLS, TIME_CONSTANTS, ROUTE_URLS } from '../constants.js';
import { authService } from './authService.js';

class NotificationService {
    constructor() {
        this.socket = null;
        this.listeners = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = TIME_CONSTANTS.WEBSOCKET_RECONNECT_INTERVAL;
    }

    connect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error("Max reconnection attempts reached. Stopping reconnection.");
            return;
        }

        try {
            this.socket = new WebSocket(API_URLS.WEBSOCKET.NOTIFICATIONS);
            this.socket.onopen = this.handleOpen.bind(this);
            this.socket.onmessage = this.handleMessage.bind(this);
            this.socket.onclose = this.handleClose.bind(this);
            this.socket.onerror = this.handleError.bind(this);
        } catch (error) {
            console.error("Failed to establish WebSocket connection:", error);
            this.reconnect();
        }
    }

    handleOpen() {
        console.log("WebSocket connected");
        this.reconnectAttempts = 0;
    }

    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'authentication_required') {
                this.handleAuthenticationRequired();
            } else {
                this.notifyListeners(data.type, data);
                this.showNotification(data.message, data.type);
            }
        } catch (error) {
            console.error("Error parsing WebSocket message:", error);
        }
    }

    handleAuthenticationRequired() {
        console.log('User is not authenticated. Redirecting to login page.');
        window.location.href = ROUTE_URLS.EMPLOYEE.LOGIN;
    }

    handleClose(event) {
        if (event.wasClean) {
            console.log(`WebSocket closed cleanly, code=${event.code}, reason=${event.reason}`);
        } else {
            console.error("WebSocket connection died");
        }
        this.reconnect();
    }

    handleError(error) {
        console.error("WebSocket error:", error);
    }

    reconnect() {
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), this.reconnectInterval);
    }

    addListener(type, callback) {
        if (!this.listeners.has(type)) {
            this.listeners.set(type, new Set());
        }
        this.listeners.get(type).add(callback);
    }

    removeListener(type, callback) {
        if (this.listeners.has(type)) {
            this.listeners.get(type).delete(callback);
        }
    }

    notifyListeners(type, data) {
        if (this.listeners.has(type)) {
            this.listeners.get(type).forEach(callback => callback(data));
        }
    }

    showNotification(message, type = 'info') {
        const notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            console.warn("No notification container found in DOM.");
            return;
        }

        // Map 'error' to 'danger'
        const alertType = type === 'error' ? 'danger' : type;

        const notification = document.createElement('div');
        notification.className = `alert alert-${alertType} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        notificationContainer.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, TIME_CONSTANTS.NOTIFICATION_DURATION);
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}

export const notificationService = new NotificationService();
