import { API_URLS } from '../constants.js';
import { authService } from './authService.js';

class LeaveService {
  async loadMyLeaveRequests() {
    const userType = authService.getUserType();
    return authService.authenticatedFetch(API_URLS.LEAVE.EMPLOYEE_REQUESTS, {}, userType);
  }

  async handleLeaveAction(leaveId, action) {
    const userType = authService.getUserType();
    const url = action === 'cancel'
      ? `${API_URLS.LEAVE.CANCEL}${leaveId}/`
      : `${API_URLS.LEAVE.ACTION}${leaveId}/${action}/`;

    return authService.authenticatedFetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    }, userType).then(response => {
      if (typeof response === 'string' && response.startsWith('<!DOCTYPE html>')) {
        throw new Error('Server returned an HTML page instead of JSON. Check the URL or server configuration.');
      }
      return response;
    });
  }

  async submitEmployeeLeaveRequest(leaveData) {
    const userType = authService.getUserType();
    return authService.authenticatedFetch(API_URLS.LEAVE.EMPLOYEE_CREATE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(leaveData)
    }, userType);
  }

  async getMyLeaveRequests() {
    return this.loadMyLeaveRequests();
  }

  async getRemainingLeave() {
    const userType = authService.getUserType();
    return authService.authenticatedFetch(API_URLS.EMPLOYEE.REMAINING_LEAVE, {}, userType);
  }

  async cancelLeaveRequest(leaveId) {
    return this.handleLeaveAction(leaveId, 'cancel');
  }

  async actionLeaveRequest(leaveId, action) {
    return this.handleLeaveAction(leaveId, action);
  }

  async getAllLeaves() {
    return authService.authenticatedFetch(API_URLS.LEAVE.AUTHORIZED_REQUESTS, {}, authService.getUserType());
  }
}

export const leaveService = new LeaveService();