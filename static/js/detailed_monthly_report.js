import { API_URLS } from './constants.js';
import { notificationService } from './services/notificationService.js';
import { authService } from './services/authService.js';

class MonthlyReport {
    constructor() {
        console.log('Initializing MonthlyReport class');
        this.reportForm = document.getElementById('reportForm');
        this.reportData = document.getElementById('reportData');
        this.currentYear = new Date().getFullYear();
        this.currentMonth = new Date().getMonth() + 1; // January is 0, so add 1

        console.log(`Current Year: ${this.currentYear}, Current Month: ${this.currentMonth}`);

        this.initializeDataTable();

        this.setupEventListeners();
        this.setInitialMonthAndYear();
    }

    initializeDataTable() {
        console.log('Initializing DataTable');
        this.reportDataTable = $('#reportDataTable').DataTable({
            columns: [
                { data: 'employee', title: 'Employee' },
                { data: 'total_hours', title: 'Total Hours' },
                { data: 'total_lateness', title: 'Total Lateness' },
                { data: 'avg_daily_hours', title: 'Avg Daily Hours' },
                { data: 'days_worked', title: 'Days Worked' },
                { data: 'days_late', title: 'Days Late' },
            ],
            order: [[0, 'asc']],
            ajax: {
                url: API_URLS.ATTENDANCE.MONTHLY_REPORT(this.currentYear, this.currentMonth),
                type: 'GET',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`,
                    'X-CSRFToken': authService.getCookie('csrftoken')
                },
                dataSrc: '', // JSON yanıtınız doğrudan bir dizi olduğu için boş bırakıyoruz
                beforeSend: () => {
                    console.log(`Making AJAX request to: ${API_URLS.ATTENDANCE.MONTHLY_REPORT(this.currentYear, this.currentMonth)}`);
                },
                success: (data) => {
                    console.log('AJAX request successful. Data received:', data);
                    // DataTables'a veriyi ekle ve tabloyu yeniden çiz
                    this.reportDataTable.clear();
                    this.reportDataTable.rows.add(data);
                    this.reportDataTable.draw();
                },
                error: (xhr, error, thrown) => {
                    console.error('Error loading report data:', error);
                    console.error('XHR response:', xhr);
                    this.renderErrorMessage();
                }
            },
            initComplete: () => {
                console.log('DataTable initialization complete');
            },
            drawCallback: () => {
                console.log('DataTable draw callback triggered');
            }
        });
    }

    setInitialMonthAndYear() {
        console.log('Setting initial month and year in form');
        document.getElementById('year').value = this.currentYear;
        document.getElementById('month').value = this.currentMonth;
    }

    setupEventListeners() {
        console.log('Setting up event listeners');
        if (this.reportForm) {
            this.reportForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        notificationService.addListener('REPORT_GENERATED', this.handleReportGenerated.bind(this));
        notificationService.addListener('REPORT_ERROR', this.handleReportError.bind(this));
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        const year = document.getElementById('year').value;
        const month = document.getElementById('month').value;

        console.log(`Form submitted. Year: ${year}, Month: ${month}`);

        const url = API_URLS.ATTENDANCE.MONTHLY_REPORT(year, month);
        console.log(`Updating DataTables AJAX URL to: ${url}`);

        if ($.fn.DataTable.isDataTable('#reportDataTable')) {
            console.log('Destroying existing DataTable instance');
            $('#reportDataTable').DataTable().clear().destroy();
        }

        this.reportDataTable = $('#reportDataTable').DataTable({
            columns: [
                { data: 'employee', title: 'Employee' },
                { data: 'total_hours', title: 'Total Hours' },
                { data: 'total_lateness', title: 'Total Lateness' },
                { data: 'avg_daily_hours', title: 'Avg Daily Hours' },
                { data: 'days_worked', title: 'Days Worked' },
                { data: 'days_late', title: 'Days Late' },
            ],
            order: [[0, 'asc']],
            ajax: {
                url: url,
                type: 'GET',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`,
                    'X-CSRFToken': authService.getCookie('csrftoken')
                },
                dataSrc: '', // JSON yanıtınız doğrudan bir dizi olduğu için boş bırakıyoruz
                beforeSend: () => {
                    console.log(`Making AJAX request to: ${url}`);
                },
                success: (data) => {
                    console.log('AJAX request successful. Data received:', data);
                    this.reportDataTable.clear();
                    this.reportDataTable.rows.add(data);
                    this.reportDataTable.draw();
                },
                error: (xhr, error, thrown) => {
                    console.error('Error loading report data:', error);
                    console.error('XHR response:', xhr);
                    this.renderErrorMessage();
                }
            },
            initComplete: () => {
                console.log('DataTable initialization complete after form submit');
            },
            drawCallback: () => {
                console.log('DataTable draw callback triggered after form submit');
            }
        });

        // DataTables'ın AJAX isteğinden sonra yanıtı almak için event listener ekleyelim
        this.reportDataTable.on('xhr', function () {
            const json = this.ajax.json();
            console.log('DataTables AJAX response:', json);
        });
    }

    renderErrorMessage() {
        console.log('Rendering error message in table');
        this.reportData.innerHTML = '<tr><td colspan="6">Error loading report data. Please try again.</td></tr>';
        notificationService.showNotification('Failed to load report data. Please try again.', 'error');
    }

    handleReportGenerated(data) {
        console.log('Report generated successfully:', data);
        notificationService.showNotification('Monthly report has been generated successfully.', 'success');
        // İsteğe bağlı olarak, raporu yeniden yükleyebilirsiniz
        this.handleFormSubmit(new Event('submit'));
    }

    handleReportError(data) {
        console.error('Error generating report:', data);
        notificationService.showNotification('Error generating monthly report. Please try again.', 'error');
    }
}

// Initialize the MonthlyReport when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');
    new MonthlyReport();
});

