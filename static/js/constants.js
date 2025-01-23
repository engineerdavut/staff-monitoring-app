const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsHost = window.location.host;

export const TIME_CONSTANTS = {
  REFRESH_INTERVAL: 300000, // 5 minutes in milliseconds
  NOTIFICATION_DURATION: 5000 // 5 seconds in milliseconds
};

export const API_URLS = {
  ATTENDANCE: {
    STATUS: '/api/v1/attendance/status/',
    CHECK_IN: '/api/v1/attendance/check-in/',
    CHECK_OUT: '/api/v1/attendance/check-out/',
    MONTHLY_REPORT: (year, month) => `/api/v1/attendance/monthly-report/${year}/${month}/`
  },
  LEAVE: {
    EMPLOYEE_REQUESTS: '/api/v1/leave/employee/list/',
    AUTHORIZED_REQUESTS: '/api/v1/leave/authorized/list/',
    ACTION: '/api/v1/leave/',
    ALL: '/api/v1/leave/authorized/list/',
    EMPLOYEE_CREATE: '/api/v1/leave/employee/create/',
    AUTHORIZED_CREATE: '/api/v1/leave/authorized/create/',
    CANCEL : '/api/v1/leave/cancel/'
  },
  EMPLOYEE: {
    REMAINING_LEAVE: '/employee/api/remaining-leave/',
    OVERVIEW: '/employee/api/employees/overview/',
    LIST:'/employee/api/employees/list/',
    UPDATE_LEAVE_BALANCE: '/employee/api/update-leave-balance/',
  },
  AUTH: {
    LOGIN_EMPLOYEE: '/auth/api/login/employee/',
    LOGIN_AUTHORIZED: '/auth/api/login/authorized/',
    REGISTER_EMPLOYEE: '/auth/api/register/employee/',
    REGISTER_AUTHORIZED: '/auth/api/register/authorized/',
    LOGOUT: '/auth/logout/'
  },
  WEBSOCKET_NOTIFICATIONS: `ws://${window.location.host}/ws/notification/`,
  WEBSOCKET: {
    NOTIFICATIONS: `${wsProtocol}//${wsHost}/ws/notifications/`,
    ATTENDANCE: `${wsProtocol}//${wsHost}/ws/attendance/`,
    EMPLOYEE_ATTENDANCE: `${wsProtocol}//${wsHost}/ws/employee_attendance/`,
    AUTHORIZED_ATTENDANCE: `${wsProtocol}//${wsHost}/ws/authorized_attendance/`,
    AUTHORIZED_NOTIFICATIONS: `${wsProtocol}//${wsHost}/ws/authorized_notifications/`,
  }
};

export const ROUTE_URLS = {
  EMPLOYEE: {
    DASHBOARD: '/employee/employee-dashboard/',
    LOGIN: '/auth/login/employee/',
    REGISTER: '/auth/register/employee/',
  },
  AUTHORIZED: {
    DASHBOARD: '/employee/authorized-dashboard/',
    LOGIN: '/auth/login/authorized/',
    REGISTER: '/auth/register/authorized/',
    MONTHLY_REPORT:'/api/v1/attendance/detailed-monthly-report/',
  },
  HOME: '/',
};