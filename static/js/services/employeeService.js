import { API_URLS } from '../constants.js';
import { authService } from './authService.js';

class EmployeeService {
  async loadRemainingLeave() {
    const userType = authService.getUserType();
    return authService.authenticatedFetch(API_URLS.EMPLOYEE.REMAINING_LEAVE, {}, userType);
  }

  async fetchCurrentDate() {
    const userType = authService.getUserType();
    const response = await authService.authenticatedFetch(API_URLS.CURRENT_DATE, {}, userType);
    return new Date(response.current_date);
  }
}

export const employeeService = new EmployeeService();




