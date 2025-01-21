from rest_framework import serializers
from .models import Attendance
from django.utils import timezone

class AttendanceSerializer(serializers.ModelSerializer):
    formatted_check_in = serializers.SerializerMethodField()
    formatted_check_out = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'check_in', 'check_out', 'lateness', 'status', 'formatted_check_in', 'formatted_check_out']

    def get_formatted_check_in(self, obj):
        if obj.check_in:
            local_time = timezone.localtime(obj.check_in)
            return local_time.strftime('%Y-%m-%d %H:%M')
        return 'N/A'

    def get_formatted_check_out(self, obj):
        if obj.check_out:
            local_time = timezone.localtime(obj.check_out)
            return local_time.strftime('%Y-%m-%d %H:%M')
        return 'N/A'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['employee'] = instance.employee.user.username
        return representation

class AttendanceReportSerializer(serializers.Serializer):
    employee = serializers.CharField()
    total_hours = serializers.CharField()
    total_lateness = serializers.CharField()
    avg_daily_hours = serializers.CharField()
    days_worked = serializers.IntegerField()
    days_late = serializers.IntegerField()