import { notificationService } from './services/notificationService.js';
import { authService } from './services/authService.js';
import { API_URLS, ROUTE_URLS } from './constants.js';
import { leaveService } from './services/leaveService.js';

class AuthorizedDashboard {
  constructor() {
    this.elements = {
      employeeOverviewTable: $('#employeeOverviewTable').DataTable({
        columns: [
          { data: 'username', title: 'Employee Name' },
          { data: 'status', title: 'Status' },
          { data: 'last_action_time', title: 'Last Action Time' },
          { data: 'lateness', title: 'Lateness (min)' },
          { data: 'work_duration', title: 'Total Work Duration' },
          { data: 'remaining_leave', title: 'Remaining Leave' },
          { data: 'annual_leave', title: 'Annual Leave' }
        ],
        data: [], 
        rowId: 'id', 
        responsive: true, 
        autoWidth: false 
      }),
      leaveRequestsTable: document.getElementById('leaveRequestsTable'),
      leaveRequestsTableBody: document.getElementById('leaveRequestsTable')?.getElementsByTagName('tbody')[0],
      addLeaveForm: document.getElementById('addLeaveForm'),
      updateLeaveBalanceForm: document.getElementById('updateLeaveBalanceForm'),
      employeeSelect: document.getElementById('employeeSelect'),
      employeeForLeaveBalance: document.getElementById('employeeForLeaveBalance'),
      selectedEmployeeName: document.getElementById('selectedEmployeeName'),
      notificationsContainer: document.getElementById('notificationsContainer'),
      notificationCount: document.getElementById('notificationCount'),
      detailedMonthlyReportBtn: document.getElementById('detailedMonthlyReportBtn'),
      startDateInput: document.getElementById('startDate'),
      endDateInput: document.getElementById('endDate')
    };

    // Event Listener'lar
    this.setupEventListeners();
    this.setupNotificationListeners();
    this.loadInitialData();
    this.setupWebSocketListeners(); 
    this.setMinStartDate();
  }

  // Yeni showNotification Metodu
  showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    this.elements.notificationsContainer.prepend(notification);

    let count = parseInt(this.elements.notificationCount.textContent, 10);
    count += 1;
    this.elements.notificationCount.textContent = count;

    notification.addEventListener('closed.bs.alert', () => {
      count -= 1;
      this.elements.notificationCount.textContent = count;
    });
  }

  setupWebSocketListeners() {
    const wsUrl = API_URLS.WEBSOCKET.AUTHORIZED_ATTENDANCE;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('WebSocket connection established');
      socket.send(JSON.stringify({ action: 'join', group: 'authorized_attendance' }));
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      console.log('data.message:', data.message); 
      console.log('data.data:', data.data);       
      if (data.type === 'realtime_attendance_update') {
          this.updateEmployeeOverviewWithWebSocketData(data.data); 
      }
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  setupEventListeners() {
    if (this.elements.addLeaveForm) {
      this.elements.addLeaveForm.addEventListener('submit', this.handleAddLeave.bind(this));
    }

    if (this.elements.updateLeaveBalanceForm) {
      this.elements.updateLeaveBalanceForm.addEventListener('submit', this.handleUpdateLeaveBalance.bind(this));
      this.elements.employeeForLeaveBalance.addEventListener('change', this.handleEmployeeSelectionChange.bind(this));
    }

    if (this.elements.detailedMonthlyReportBtn) {
      this.elements.detailedMonthlyReportBtn.addEventListener('click', this.handleDetailedMonthlyReport.bind(this));
    }

    // "Update Leave" butonları kaldırıldığı için bu event listener'ları kaldırdık
  }

  setupNotificationListeners() {
    notificationService.addListener('EMPLOYEE_CHECK_IN', this.handleEmployeeCheckIn.bind(this));
    notificationService.addListener('EMPLOYEE_CHECK_OUT', this.handleEmployeeCheckOut.bind(this));
    notificationService.addListener('LEAVE_REQUEST', this.handleLeaveRequest.bind(this));
    notificationService.addListener('LOW_LEAVE_BALANCE', this.handleLowLeaveBalance.bind(this));
    notificationService.addListener('EMPLOYEE_LATE', this.handleEmployeeLate.bind(this));
    notificationService.addListener('NO_CHECK_IN', this.handleNoCheckIn.bind(this));
  }

  loadInitialData() {
    this.loadEmployeeOverview();
    this.loadLeaveRequests();
    this.loadEmployees();
  }

  loadEmployeeOverview() {
    authService.authenticatedFetch(API_URLS.EMPLOYEE.OVERVIEW, {
      headers: {
        'Authorization': `Token ${authService.getToken()}`
      }
    })
    .then(data => {
      console.log('Employee Overview Data:', data);
      this.renderEmployeeOverview(data);
    })
    .catch(error => {
      console.error('Error loading employee overview:', error);
      this.showNotification('Failed to load employee overview', 'danger');
    });
  }

  renderEmployeeOverview(data) {
    if (!Array.isArray(data)) {
      console.error('Data is not an array:', data);
      this.showNotification('Failed to load employee overview', 'danger');
      return;
    }

    // DataTables'ın mevcut verisini temizleyip yeni veriyi ekleyin
    this.elements.employeeOverviewTable.clear();
    this.elements.employeeOverviewTable.rows.add(data);
    this.elements.employeeOverviewTable.draw();

    // "Update Leave" butonları kaldırıldığı için event listener eklemeye gerek yok
  }

  updateEmployeeOverviewWithWebSocketData(message) {
    const table = this.elements.employeeOverviewTable;
    const employeeId = message.id; // 'id' alanını kullanın

    if (!employeeId) {
      console.warn('id is undefined in the message:', message);
      return;
    }

    const row = table.row(`#${employeeId}`); // DataTables rowId kullanarak satırı buluyoruz

    if (row.any()) {
      // Mevcut satırı güncelleyin
      const rowData = row.data();
      rowData.remaining_leave = message.remaining_leave;
      rowData.lateness = message.lateness;
      rowData.work_duration = message.work_duration;
      rowData.status = message.status;
      rowData.last_action_time = message.last_action_time; // 'last_action_time''ı 'check_in_time' olarak güncelleyin
      table.row(row).data(rowData).draw(false);
    } else {
      console.warn(`Row for employee_id ${employeeId} not found. Cannot update existing row.`);
      // Yeni satır eklemek istemiyorsanız, burada bir şey yapmanıza gerek yok
    }
  }


  loadLeaveRequests() {
    leaveService.getAllLeaves()
    .then(data => this.renderLeaveRequests(data))
    .catch(error => {
      console.error('Error loading leave requests:', error);
      this.showNotification('Failed to load leave requests', 'danger');
    });
  }

  renderLeaveRequests(data) {
    if (!Array.isArray(data)) {
      console.error('Data is not an array:', data);
      this.showNotification('Failed to load leave requests', 'danger');
      return;
    }

    if (this.elements.leaveRequestsTableBody) {
      this.elements.leaveRequestsTableBody.innerHTML = data.map(request => `
          <tr data-id="${request.id}">
              <td>${request.employee_name}</td>
              <td>${request.start_date}</td>
              <td>${request.end_date}</td>
              <td>${request.reason}</td>
              <td class="leave-status">${request.status}</td>
              <td>
                  ${request.status.toUpperCase() === 'PENDING' ? `
                      <button type="button" class="btn btn-sm btn-success approve-leave" data-id="${request.id}">Approve</button>
                      <button type="button" class="btn btn-sm btn-danger reject-leave" data-id="${request.id}">Reject</button>
                  ` : ''}
              </td>
          </tr>
      `).join('');

      // DataTables'ı yeniden başlatma
      if ($.fn.DataTable.isDataTable('#leaveRequestsTable')) {
        $('#leaveRequestsTable').DataTable().destroy();
      }
      $('#leaveRequestsTable').DataTable();
    } else {
      console.error('leaveRequestsTableBody element not found');
      this.showNotification('Failed to render leave requests', 'danger');
    }
  }

  async handleLeaveAction(leaveId, action) {
    console.log(`AuthorizedDashboard: handleLeaveAction called with leaveId=${leaveId}, action=${action}`);
    try {
      const response = await leaveService.actionLeaveRequest(leaveId, action);
      
      console.log('Leave Action Response:', response);
      
      if (response.leave.status.toUpperCase() === 'REJECTED') {
        this.showNotification(response.message, 'warning');
        this.updateLeaveRequestRow(leaveId, 'Rejected');
      } else if (response.leave.status.toUpperCase() === 'APPROVED') {
        this.showNotification(response.message, 'success');
        this.updateLeaveRequestRow(leaveId, 'Approved');
      } else {
        this.showNotification('Unknown response status.', 'danger');
      }
    } catch (error) {
      console.error(`AuthorizedDashboard: Error in handleLeaveAction:`, error);
      this.showNotification(`Failed to ${action} leave request: ${error.message}`, 'danger');
    }
  }

  updateLeaveRequestRow(leaveId, newStatus) {
    const row = this.elements.leaveRequestsTableBody.querySelector(`tr[data-id="${leaveId}"]`);
    if (row) {
      const statusCell = row.querySelector('.leave-status');
      if (statusCell) {
        statusCell.textContent = newStatus;
      }

      // Approve ve Reject butonlarını kaldırın
      const actionCell = row.querySelector('td:last-child');
      if (actionCell) {
        actionCell.innerHTML = ''; // Butonları tamamen kaldır
      }
    }
  }

  loadEmployees() {
    authService.authenticatedFetch(API_URLS.EMPLOYEE.LIST, {
      headers: {
        'Authorization': `Token ${authService.getToken()}`
      }
    })
    .then(data => this.renderEmployees(data))
    .catch(error => {
      console.error('Error loading employees:', error);
      this.showNotification('Failed to load employees', 'danger');
    });
  }

  renderEmployees(data) {
    if (!Array.isArray(data)) {
      console.error('Data is not an array:', data);
      this.showNotification('Failed to load employees', 'danger');
      return;
    }

    const options = data.map(employee => `<option value="${employee.id}">${employee.username}</option>`);
    const defaultOption = `<option value="" disabled selected>Select an employee</option>`;

    console.log('Rendering employees for both forms');

    if (this.elements.employeeSelect) {
      this.elements.employeeSelect.innerHTML = defaultOption + options.join('');
      console.log('employeeSelect populated successfully');
    } else {
      console.error('employeeSelect element not found');
      this.showNotification('Failed to load employee selection list for Add Leave form', 'danger');
    }

    if (this.elements.employeeForLeaveBalance) {
      this.elements.employeeForLeaveBalance.innerHTML = defaultOption + options.join('');
      console.log('employeeForLeaveBalance populated successfully');
    } else {
      console.error('employeeForLeaveBalance element not found');
      this.showNotification('Failed to load employee selection list for Update Leave Balance form', 'danger');
    }
  }

  async handleAddLeave(e) {
    e.preventDefault();
    const formData = new FormData(this.elements.addLeaveForm);

    console.log('FormData entries for addLeaveForm:');
    for (let pair of formData.entries()) {
      console.log(`${pair[0]}: ${pair[1]}`);
    }

    const employeeValue = formData.get('employee');
    const employeeId = parseInt(employeeValue, 10); 
    console.log('employeeValue:', employeeValue);
    console.log('employeeId:', employeeId);
    if (isNaN(employeeId)) {
      this.showNotification('Invalid employee selected.', 'danger');
      return;
    }

    const startDate = formData.get('start_date');
    const endDate = formData.get('end_date');
    const reason = formData.get('reason');

    console.log('Submitting leave data:', {
      employee: employeeId,
      start_date: startDate,
      end_date: endDate,
      reason: reason
    });

    // Frontend Validasyonları
    const today = new Date();
    const selectedStartDate = new Date(startDate);
    const selectedEndDate = new Date(endDate);

    // 1. Start Date yarından itibaren olmalı
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    if (selectedStartDate < tomorrow) {
      this.showNotification('Start date must be tomorrow or later.', 'danger');
      return;
    }

    // 2. End Date, Start Date'den büyük olmalı
    if (selectedEndDate <= selectedStartDate) {
      this.showNotification('End date must be after start date.', 'danger');
      return;
    }

    // 3. Start Date ve End Date arasında en fazla 15 hafta içi gün olmalı
    const weekdaysCount = this.countWeekdays(selectedStartDate, selectedEndDate);
    if (weekdaysCount > 15) {
      this.showNotification('Leave request cannot exceed 15 weekdays.', 'danger');
      return;
    }

    // Tüm validasyonlardan geçtiyse API çağrısını yap
    const leaveData = {
      employee: employeeId, // Tam sayı olarak gönderiliyor
      start_date: startDate,
      end_date: endDate,
      reason: reason
    };

    try {
      const response = await fetch(API_URLS.LEAVE.AUTHORIZED_CREATE, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${authService.getToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(leaveData)
      });

      // JSON beklediğinizi doğrulayın
      const contentType = response.headers.get("Content-Type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("The server did not return JSON.");
      }

      const data = await response.json();

      console.log('API Response:', data); // Debug

      if (response.ok && data.message) {
        this.showNotification(data.message, 'success');
        this.elements.addLeaveForm.reset();
        this.loadLeaveRequests();
        this.loadEmployeeOverview();
      } else if (data.error) {
        // Backend'den gelen hata mesajını göster
        const errorMessage = Array.isArray(data.error) ? data.error.join(' ') : data.error;
        this.showNotification(`Error: ${errorMessage}`, 'danger');
      } else {
        throw new Error('An unknown error occurred.');
      }
    } catch (error) {
      console.error('Error adding leave:', error);
      this.showNotification(`Failed to add leave: ${error.message}`, 'danger');
    }
  }

  countWeekdays(startDate, endDate) {
    let count = 0;
    const current = new Date(startDate);
    while (current <= endDate) {
      const day = current.getDay();
      if (day !== 0 && day !== 6) { // Pazar=0, Cumartesi=6
        count++;
      }
      current.setDate(current.getDate() + 1);
    }
    return count;
  }

  setMinStartDate() {
    const startDateInput = this.elements.startDateInput;
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    startDateInput.min = this.formatDate(tomorrow);
  }

  formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  handleStartDateChange(event){
    const startDate = new Date(event.target.value);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    // Sadece tarih bileşenlerini karşılaştırmak için saatleri sıfırlıyoruz
    const startDateOnly = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
    const tomorrowOnly = new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate());

    // Başlangıç tarihinin yarından itibaren olması gerektiğini kontrol et
    if(startDateOnly < tomorrowOnly){
      this.showNotification('Start date cannot be before tomorrow.', 'danger');
      this.elements.startDateInput.value = ''; // Geçersiz tarihi temizle
      return;
    }

    if(this.elements.endDateInput.value){
      const endDate = new Date(this.elements.endDateInput.value);
      const endDateOnly = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
      if(endDateOnly < startDateOnly){
        this.elements.endDateInput.value = null;
        this.showNotification('End date cannot be before the start date.', 'danger');
      }
    }
    this.elements.endDateInput.min = this.formatDate(startDateOnly);
  }

  async handleUpdateLeaveBalance(e) {
    e.preventDefault();
    const formData = new FormData(this.elements.updateLeaveBalanceForm);
    const data = Object.fromEntries(formData);

    // Doğrulama ekleyin
    const change = parseInt(data.change, 10);
    if (isNaN(change)) {
      this.showNotification('Invalid change value.', 'danger');
      return;
    }

    try {
      const response = await fetch(API_URLS.EMPLOYEE.UPDATE_LEAVE_BALANCE, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${authService.getToken()}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employee_id: data.employee,  // 'employee' alanını 'employee_id' olarak gönderin
          change: change
        })
      });

      // JSON beklediğinizi doğrulayın
      const contentType = response.headers.get("Content-Type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("The server did not return JSON.");
      }

      const responseData = await response.json();

      console.log('API Response:', responseData); // Debug

      if (response.ok && responseData.message) {
        this.showNotification(responseData.message, 'success'); // responseData.message kullanıldı
        this.elements.updateLeaveBalanceForm.reset();
        this.elements.selectedEmployeeName.textContent = '';  // Seçilen çalışan adını temizle
        this.loadEmployeeOverview();
      } else if (responseData.error) {
        const errorMessage = Array.isArray(responseData.error) ? responseData.error.join(' ') : responseData.error;
        this.showNotification(`Error: ${errorMessage}`, 'danger');
      } else {
        throw new Error('An unknown error occurred.');
      }
    } catch (error) {
      console.error('Error updating leave balance:', error);
      this.showNotification(`Failed to update leave balance: ${error.message}`, 'danger');
    }
}

  // Notification handlers
  handleEmployeeCheckIn(data) {
    this.showNotification(`${data.employee} checked in at ${data.time}`, 'info');
    this.loadEmployeeOverview();
  }

  handleEmployeeCheckOut(data) {
    this.showNotification(`${data.employee} checked out at ${data.time}`, 'info');
    this.loadEmployeeOverview();
  }

  handleLeaveRequest(data) {
    this.showNotification(`New leave request from ${data.employee}`, 'info');
    this.loadLeaveRequests();
  }

  handleLowLeaveBalance(data) {
    this.showNotification(`${data.employee}'s leave balance is below 3 days`, 'warning');
    this.loadEmployeeOverview();
  }

  handleEmployeeLate(data) {
    this.showNotification(`${data.employee} was late by ${data.minutes} minutes`, 'warning');
    this.loadEmployeeOverview();
  }

  handleNoCheckIn(data) {
    this.showNotification(`${data.employee} has not checked in today`, 'warning');
    this.loadEmployeeOverview();
  }

  handleDetailedMonthlyReport(event) {
    event.preventDefault();
    window.location.href = ROUTE_URLS.AUTHORIZED.MONTHLY_REPORT;
  }

  // Yeni eklenen metod
  handleEmployeeSelectionChange(event) {
    const selectedEmployeeId = event.target.value;
    const selectedOption = event.target.options[event.target.selectedIndex];
    const selectedEmployeeName = selectedOption.text;

    if (this.elements.selectedEmployeeName) {
      this.elements.selectedEmployeeName.textContent = selectedEmployeeName;
    }
  }

  // Helper method to update a specific row in DataTables
  updateRowInDataTable(employeeId, updatedData) {
    const table = this.elements.employeeOverviewTable;
    const row = table.row(`#${employeeId}`); // rowId kullanarak buluyoruz

    if (row.any()) {
      // Mevcut satırı güncelle
      const rowData = row.data();
      Object.assign(rowData, updatedData);
      row.data(rowData).draw(false);
    } else {
      console.warn(`Row for employee_id ${employeeId} not found.`);
      // Eğer isterseniz, burada yeni bir satır ekleyebilirsiniz
      // Ancak, username gibi bilgilerin eksik olabileceğini unutmayın
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM fully loaded and parsed');
  new AuthorizedDashboard();
});