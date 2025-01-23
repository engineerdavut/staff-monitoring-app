import { API_URLS } from '../constants.js';
import { authService } from './authService.js';

class EmployeeService {
  async loadRemainingLeave() {
    const userType = authService.getUserType();
    return authService.authenticatedFetch(API_URLS.EMPLOYEE.REMAINING_LEAVE, {}, userType);
  }
}

export const employeeService = new EmployeeService();