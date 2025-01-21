import django_tables2 as tables
from .models import Employee
from employee_tracking_system.utils.time_utils import TimeCalculator

class EmployeeOverviewTable(tables.Table):
    user = tables.Column(accessor='user.username', verbose_name="User")
    annual_leave = tables.Column(verbose_name="Annual Leave")
    remaining_leave_display = tables.Column(verbose_name="Remaining Leave")
    total_lateness = tables.Column(verbose_name="Total Lateness")
    total_work_duration = tables.Column(verbose_name="Total Work Duration")

    class Meta:
        model = Employee
        template_name = "django_tables2/bootstrap4.html"
        fields = ['user', 'annual_leave', 'remaining_leave_display', 'total_lateness', 'total_work_duration']

    def render_remaining_leave_display(self, value):
        return value 

    def render_total_lateness(self, value):
        return TimeCalculator.timedelta_to_hhmm(value)

    def render_total_work_duration(self, value):
        return TimeCalculator.timedelta_to_hhmm(value)