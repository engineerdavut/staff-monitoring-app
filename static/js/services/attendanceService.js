import { API_URLS } from '../constants.js';
import { authService } from './authService.js';
import { notificationService } from './notificationService.js';

class AttendanceService {
  async updateAttendanceStatus() {
    if (!authService.isAuthenticated()) {
      console.error('No token found');
      notificationService.showNotification('Please log in again.', 'danger');
      return Promise.reject('No token found');
    }

    try {
      const userType = authService.getUserType();
      const response = await authService.authenticatedFetch(API_URLS.ATTENDANCE.STATUS, {}, userType);
      return response;
    } catch (error) {
      if (error.message === 'Unauthorized') {
        notificationService.showNotification('Your session has expired. Please log in again.', 'danger');
      } else {
        notificationService.showNotification('Failed to update attendance status. Please try again.', 'danger');
      }
      throw error;
    }
  }
async checkIn() {
     try {
        const userType = authService.getUserType();
        const response = await authService.authenticatedFetch(API_URLS.ATTENDANCE.CHECK_IN, {
            method: 'POST',
          },userType);
        return response;
      }
    catch (error) {
        notificationService.showNotification(`Failed to check in. Please try again.`, 'danger');
      throw error;
  }
  }

async checkOut() {
  try {
         const userType = authService.getUserType();
        const response = await authService.authenticatedFetch(API_URLS.ATTENDANCE.CHECK_OUT, {
            method: 'POST',
          },userType);
        return response;
      }
      catch (error) {
         notificationService.showNotification(`Failed to check out. Please try again.`, 'danger');
        throw error;
    }
}


  async getAttendanceStatus() {
    return this.updateAttendanceStatus();
  }
}

export const attendanceService = new AttendanceService();