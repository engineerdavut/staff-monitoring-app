import { notificationService } from './services/notificationService.js';
import { authService } from './services/authService.js';
import { attendanceService } from './services/attendanceService.js';
import { leaveService } from './services/leaveService.js';
import { API_URLS, ROUTE_URLS, TIME_CONSTANTS } from './constants.js';

class EmployeeDashboard {
    constructor() {
        this.elements = this.getElementReferences();
        this.currentEmployeeId = authService.getEmployeeId();
        console.log(`Current Employee ID: ${this.currentEmployeeId}`); // Ek log
        this.init();
    }

    getElementReferences() {
        return {
            checkInBtn: document.getElementById('checkInBtn'),
            checkOutBtn: document.getElementById('checkOutBtn'),
            leaveRequestForm: document.getElementById('leaveRequestForm'),
            myLeaveRequestsTable: document.getElementById('myLeaveRequestsTable'),
            remainingLeaveText: document.getElementById('remainingLeaveText'),
            remainingLeaveIndicator: document.getElementById('remainingLeaveIndicator'),
            startDateInput: document.getElementById('startDate'),
            endDateInput: document.getElementById('endDate'),
            attendanceStatus: document.getElementById('attendanceStatus'),
            notificationContainer: document.getElementById('notification-container'),
            latenessDisplay: document.getElementById('latenessDisplay'),
            remainingLeaveDisplay: document.getElementById('remainingLeaveDisplay'),
            welcomeMessage: document.getElementById('welcomeMessage')
        };
    }

    init() {
        if (!authService.isAuthenticated()) {
            window.location.href = ROUTE_URLS.EMPLOYEE.LOGIN;
            return;
        }
        this.currentEmployeeId = authService.getEmployeeId();
        console.log(`Current Employee ID after auth check: ${this.currentEmployeeId}`); // Ek log
        this.setupWebSocket();
        this.setupEventListeners();
        this.setupNotificationListeners();
        this.refreshData();
        this.startPeriodicRefresh();
        this.updateWelcomeMessage();
        this.setMinStartDate();
    }

    updateWelcomeMessage() {
        const username = authService.getUsername();
        if (this.elements.welcomeMessage && username) {
            this.elements.welcomeMessage.textContent = `Welcome, ${username}!`;
        }
    }

    setupWebSocket() {
        const wsUrl = API_URLS.WEBSOCKET.EMPLOYEE_ATTENDANCE;
        this.socket = new WebSocket(wsUrl);

        this.socket.onmessage = this.handleWebSocketMessage.bind(this);
        this.socket.onclose = this.handleWebSocketClose.bind(this);
        this.socket.onerror = this.handleWebSocketError.bind(this);
    }

    handleWebSocketMessage(event) {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        console.log("yurururruru "+this.currentEmployeeId + "  dfgdfhgd  "+data.id)
        console.log("Type of currentEmployeeId:", typeof this.currentEmployeeId, "Type of data.id:", typeof data.id);
    
        // data.id'yi number'a çeviriyoruz
        const currentEmployeeIdNumber = Number(this.currentEmployeeId);
        console.log("Converted data.id to number:", currentEmployeeIdNumber, "Type:", typeof currentEmployeeIdNumber);
        if (data.event_type === 'employee_realtime_attendance_update' && data.id === currentEmployeeIdNumber) {
            console.log("bu ife girmiyor.")
            const message = data.data;

            if ( message.remaining_leave && message.lateness) {

                this.updateRemainingLeaveDisplay(message.remaining_leave);
                this.updateLatenessDisplay(message.lateness);

            } else {
                console.warn('Received incomplete message:', message);
            }
        }
    }

    handleWebSocketClose() {
        console.log('WebSocket connection closed. Trying to reconnect...');
        setTimeout(() => this.setupWebSocket(), 5000);
    }

    handleWebSocketError(error) {
        console.error('WebSocket error:', error);
    }

    setupEventListeners() {
        this.elements.checkInBtn?.addEventListener('click', () => this.performAttendanceAction('check_in'));
        this.elements.checkOutBtn?.addEventListener('click', () => this.performAttendanceAction('check_out'));
        this.elements.leaveRequestForm?.addEventListener('submit', this.handleEmployeeLeaveRequest.bind(this));
        this.elements.startDateInput?.addEventListener('change', this.handleStartDateChange.bind(this));
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
            this.showNotification('Start date cannot be before tomorrow.', 'danger'); // 'danger' olarak göster
            this.elements.startDateInput.value = ''; // Geçersiz tarihi temizle
            return;
        }
    
        if(this.elements.endDateInput.value){
            const endDate = new Date(this.elements.endDateInput.value);
            const endDateOnly = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
            if(endDateOnly < startDateOnly){
                this.elements.endDateInput.value = null;
                this.showNotification('End date cannot be before the start date.', 'danger'); // 'danger' olarak göster
            }
        }
        this.elements.endDateInput.min = this.formatDate(startDateOnly);
    }
    

    setupNotificationListeners() {
        const notificationHandlers = {
            CHECK_IN: this.handleCheckInNotification,
            CHECK_OUT: this.handleCheckOutNotification,
            DAILY_WORK_SUMMARY: this.handleDailyWorkSummaryNotification,
            LEAVE_REQUEST: this.handleLeaveRequestNotification,
            LEAVE_REQUEST_INSUFFICIENT: this.handleLeaveInsufficientNotification,
            LEAVE_REQUEST_APPROVED: this.handleLeaveApprovedNotification,
            LEAVE_REQUEST_REJECTED: this.handleLeaveRejectedNotification,
            LEAVE_BALANCE_UPDATED: this.handleLeaveBalanceUpdatedNotification,
            LEAVE_REQUEST_CONFLICT: this.handleLeaveConflictNotification,
            EMPLOYEE_LATE: this.handleEmployeeLateNotification,
            NO_CHECK_IN: this.handleNoCheckInNotification,
            LEAVE_REQUEST_CANCELLED: this.handleLeaveCancelledNotification
        };

        Object.entries(notificationHandlers).forEach(([event, handler]) => {
            notificationService.addListener(event, handler.bind(this));
        });
    }

    startPeriodicRefresh() {
        setInterval(() => this.refreshData(), TIME_CONSTANTS.REFRESH_INTERVAL);
    }

    async refreshData() {
        console.log('Starting refreshData');
        try {
            await Promise.all([
                this.updateAttendanceStatus(),
                this.loadMyLeaveRequests(),
                this.loadRemainingLeave()
            ]);
            console.log('refreshData completed successfully');
            this.showNotification('Dashboard data refreshed successfully', 'success');
        } catch (error) {
            console.error('Error in refreshData:', error);
            this.handleError(error, 'Failed to refresh dashboard data');
        }
    }

    async updateAttendanceStatus() {
        try {
            const data = await attendanceService.getAttendanceStatus();
            this.updateAttendanceDisplay(data);
        } catch (error) {
            this.handleError(error, 'Failed to update attendance status');
        }
    }

    updateAttendanceDisplay(data) {
        this.elements.attendanceStatus.textContent = `Status: ${this.getStatusText(data.status)}`;

        if (data.check_ins && data.check_ins.length > 0) {

            const checkInStr = data.check_ins[data.check_ins.length - 1];
            const checkInDate = checkInStr ? new Date(checkInStr) : null;
            if (checkInDate && !isNaN(checkInDate)) {
                this.elements.attendanceStatus.textContent += 
                    ` | Check-in: ${this.formatDateTime(checkInStr)}`;
            } else {
                this.elements.attendanceStatus.textContent += " | Check-in: N/A";
            }
        } else {
            this.elements.attendanceStatus.textContent += " | Check-in: N/A";
        }
        if (data.check_outs && data.check_outs.length > 0) {
            const checkOutStr = data.check_outs[data.check_outs.length - 1];
            const checkOutDate = checkOutStr ? new Date(checkOutStr) : null;
            if (checkOutDate && !isNaN(checkOutDate)) {
                this.elements.attendanceStatus.textContent += 
                    ` | Check-out: ${this.formatDateTime(checkOutStr)}`;
            } else {
                this.elements.attendanceStatus.textContent += " | Check-out: N/A";
            }
        } else {
            this.elements.attendanceStatus.textContent += " | Check-out: N/A";
        }
        this.updateLatenessDisplay(data.lateness);
        this.updateRemainingLeaveDisplay(data.remaining_leave);
        this.updateAttendanceButtons(data.status);
    }

    updateLatenessDisplay(lateness) {
        if (this.elements.latenessDisplay && lateness !== undefined) {
            // Lateness'i doğru şekilde göster
            this.elements.latenessDisplay.textContent = lateness === "0m"
                ? "Lateness: No lateness"
                : `Lateness: ${lateness}`;
                console.log("latenessDisplay1");
        }
    }

    updateRemainingLeaveDisplay(remainingLeave) {
        if (this.elements.remainingLeaveDisplay && remainingLeave !== undefined) {
            this.elements.remainingLeaveDisplay.textContent = `Remaining Leave: ${remainingLeave}`;
            this.elements.remainingLeaveText.textContent = remainingLeave;
    
            // remaining_leave string'ini parse et
            const leaveParts = remainingLeave.match(/(\d+)d (\d+)h (\d+)m/);
            if (leaveParts) {
                const days = parseInt(leaveParts[1], 10);
                const hours = parseInt(leaveParts[2], 10);
                const minutes = parseInt(leaveParts[3], 10);
                this.updateLeaveIndicator(days, hours, minutes);
            } else {
                console.error('Invalid remaining_leave format:', remainingLeave);
            }
        }
    }
    getStatusText(status) {
        const statusTexts = {
            not_working_day: 'Not working day',
            not_working_hour : 'Not working hour',
            checked_out: 'Checked out',
            checked_in: 'Checked in',
            not_checked_in: 'Not Checked in',
            on_leave:'On Leave'
        };
        return statusTexts[status] || 'Unknown';
    }

    formatDateTime(dateTimeString) {
        const date = new Date(dateTimeString);
        if (isNaN(date.getTime())) { // Doğru kontrol
            return "Invalid Date";
        }
        return date.toLocaleString('tr-TR', {
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
        });
    }

    updateAttendanceButtons(status) {
        if (this.elements.checkInBtn && this.elements.checkOutBtn) {
            const isWorkingHours = status !== 'not_working_hour' && status !== 'not_working_day'  && status !== 'on_leave';
            this.elements.checkInBtn.disabled = !isWorkingHours || status === 'checked_in';
            this.elements.checkOutBtn.disabled = !isWorkingHours || status !== 'checked_in';
            if (!isWorkingHours) {
                this.showNotification('You are out of office hours. You cannot check in/out.', 'warning');
            }
        }
    }

    async performAttendanceAction(action) {
        try {
            let data;
            if (action === 'check_in') {
                data = await attendanceService.checkIn();
            } else if (action === 'check_out') {
                data = await attendanceService.checkOut();
            } else {
                throw new Error('Invalid action');
            }
            this.showNotification(`Successfully ${action === 'check_in' ? 'checked in' : 'checked out'}`, 'success');
            await this.updateAttendanceStatus();
        } catch (error) {
            this.handleError(error, `Failed to ${action}`);
        }
    }

    async loadMyLeaveRequests() {
        console.log('Starting loadMyLeaveRequests');
        try {
            const requests = await leaveService.getMyLeaveRequests();
            console.log('Leave requests loaded successfully:', requests);
            this.renderLeaveRequests(requests);
            this.showNotification('Leave requests loaded successfully', 'success');
        } catch (error) {
            console.error('Error in loadMyLeaveRequests:', error);
            this.handleError(error, 'Failed to load leave requests');
        }
    }

    renderLeaveRequests(requests) {
        if (this.elements.myLeaveRequestsTable) {
            const tbody = this.elements.myLeaveRequestsTable.querySelector('tbody') || this.elements.myLeaveRequestsTable;
            tbody.innerHTML = requests.map(this.createLeaveRequestRow).join('');
            this.attachLeaveActionListeners();
        }
    }

    createLeaveRequestRow(request) {
        return `
            <tr data-id="${request.id}">
                <td>${request.start_date}</td>
                <td>${request.end_date}</td>
                <td>${request.reason}</td>
                <td class="leave-status">${request.status}</td>
                <td>
                    ${request.status === 'Pending' ? `
                        <button class="btn btn-sm btn-danger cancel-leave" data-id="${request.id}">Cancel</button>
                    ` : ''}
                </td>
            </tr>
        `;
    }

    attachLeaveActionListeners() {
        document.querySelectorAll('.cancel-leave').forEach(btn => {
            btn.addEventListener('click', () => this.handleLeaveAction(btn.getAttribute('data-id'), 'cancel'));
        });
    }


    async handleLeaveAction(leaveId, action) {
        try {
            await leaveService.cancelLeaveRequest(leaveId);
            this.showNotification('Leave request cancelled successfully', 'success');
            this.updateLeaveRequestRow(leaveId, 'Cancelled');
        } catch (error) {
            this.handleError(error, `Failed to ${action} leave request`);
        }
    }
    updateLeaveRequestRow(leaveId, newStatus) {
        // Tüm satırları kontrol edin ve belirtilen leaveId'ye sahip satırı bulun
        const rows = this.elements.myLeaveRequestsTable.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const cancelBtn = row.querySelector('.cancel-leave');
            const statusCell = row.querySelector('.leave-status'); // Durum hücresini bulmak için bir sınıf eklediğinizden emin olun
    
            // Satırın doğru leaveId'ye sahip olup olmadığını kontrol edin
            if (row.dataset.id === leaveId) {
                // Durum hücresini güncelleyin
                if (statusCell) {
                    statusCell.textContent = newStatus;
                }
    
                // Cancel butonunu kaldırın veya devre dışı bırakın
                if (cancelBtn) {
                    cancelBtn.remove(); // Butonu kaldırmak için
                    // veya
                    // cancelBtn.disabled = true; // Butonu devre dışı bırakmak için
                }
            }
        });
    }

    async loadRemainingLeave() {
        console.log('Starting loadRemainingLeave');
        try {
            const data = await leaveService.getRemainingLeave();
            console.log('Remaining leave loaded successfully:', data);
            this.updateRemainingLeaveDisplay(data.remaining_leave);
            this.showNotification('Remaining leave loaded successfully', 'success');
        } catch (error) {
            console.error('Error in loadRemainingLeave:', error);
            this.handleError(error, 'Failed to load remaining leave');
        }
    }

    updateLeaveIndicator(days, hours, minutes) {
        if (this.elements.remainingLeaveIndicator) {
            if (isNaN(days) || isNaN(hours) || isNaN(minutes)) {
                console.error('Invalid leave values:', days, hours, minutes);
                return;
            }
            let color, text;
            if (days >= 10) {
                color = 'bg-success';
                text = 'Good';
            } else if (days >= 5) {
                color = 'bg-warning';
                text = 'Moderate';
            } else {
                color = 'bg-danger';
                text = 'Low';
            }
            this.elements.remainingLeaveIndicator.className = `badge rounded-pill ${color}`;
            this.elements.remainingLeaveIndicator.textContent = text;
        }
    }

    async handleEmployeeLeaveRequest(e) {
        e.preventDefault();
        const formData = new FormData(this.elements.leaveRequestForm);
        const leaveData = {
            start_date: formData.get('start_date'),
            end_date: formData.get('end_date'),
            reason: formData.get('reason')
        };
        try {
            const response = await leaveService.submitEmployeeLeaveRequest(leaveData);
            if(response && response.message){
                this.showNotification(response.message, 'success');
                this.elements.leaveRequestForm.reset();
                if (response.data) {
                    this.addLeaveRequestToTable(response.data);
                }
            } else if (response && response.error) {
                // Hata mesajını kullanıcıya detaylı bir şekilde göster
                const errorMessage = Array.isArray(response.error) ? response.error.join(' ') : response.error;
                this.showNotification(`Error submitting leave request: ${errorMessage}`, 'danger');
            } else {
                throw new Error('An unknown error occurred');
            }
        } catch (error) {
            // Hata mesajını detaylandırarak göster
            this.showNotification(`Error submitting leave request: ${error.message || error}`, 'danger');
        }
    }
    addLeaveRequestToTable(leave) {
        if (this.elements.myLeaveRequestsTable) {
            const tbody = this.elements.myLeaveRequestsTable.querySelector('tbody') || this.elements.myLeaveRequestsTable;
            const row = this.createLeaveRequestRow(leave);
            tbody.insertAdjacentHTML('beforeend', row);
            this.attachLeaveActionListeners();
        }
    }

    showNotification(message, type) {
        if (this.elements.notificationContainer) {
            notificationService.showNotification(message, type);
        } else {
            console.warn('Notification container not found. Message:', message);
        }
    }

    handleError(error, message) {
        console.error(message, error);
        if (error.message) {
            // Hata mesajını detaylandırarak göster
            this.showNotification(`${message}: ${error.message}`, 'danger');
        }
        else {
            this.showNotification(message, 'danger');
        }
    }

    // Notification handlers
    handleCheckInNotification() { this.updateAttendanceStatus(); }
    handleCheckOutNotification() { this.updateAttendanceStatus(); }
    handleDailyWorkSummaryNotification(data) {
        this.showNotification(`Your total work hours today: ${data.hours}`, 'info');
    }
    handleLeaveRequestNotification() { this.loadMyLeaveRequests(); }
    handleLeaveInsufficientNotification() {
        this.showNotification('Your leave balance is insufficient for the requested leave.', 'warning');
    }
    handleLeaveApprovedNotification(data) {
        this.showNotification(`Your leave request from ${data.start_date} to ${data.end_date} has been approved.`, 'success');
        this.loadMyLeaveRequests();
        this.loadRemainingLeave();
    }
    handleLeaveRejectedNotification(data) {
        this.showNotification(`Your leave request from ${data.start_date} to ${data.end_date} has been rejected.`, 'danger');
        this.loadMyLeaveRequests();
    }
    handleLeaveBalanceUpdatedNotification(data) {
        this.showNotification(`Your leave balance has been updated. New balance: ${data.balance} days.`, 'info');
        this.loadRemainingLeave();
    }
    handleLeaveConflictNotification(data) {
        this.showNotification(`Your leave request conflicts with existing requests for the following dates: ${data.dates}.`, 'warning');
    }
    handleEmployeeLateNotification(data) {
        this.showNotification(`You were late by ${data.minutes} minutes today.`, 'warning');
    }
    handleNoCheckInNotification() {
        this.showNotification('You have not checked in today.', 'warning');
    }
    handleLeaveCancelledNotification(data) {
        this.showNotification(`Leave request from ${data.start_date} to ${data.end_date} has been cancelled.`, 'info');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new EmployeeDashboard();
});
