from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    remaining_leave_display = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 
            'user', 
            'annual_leave', 
            'remaining_leave', 
            'total_lateness', 
            'total_work_duration', 
            'remaining_leave_display'
        ]

    def get_remaining_leave_display(self, obj):
        service = self.context.get('service')
        if service:
            return service.get_remaining_leave_display(obj)
        return "0d 0h 0m"  

class EmployeeOverviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    status = serializers.CharField()
    last_action_time = serializers.CharField()
    lateness = serializers.CharField()
    work_duration = serializers.CharField()
    remaining_leave = serializers.CharField()
    annual_leave = serializers.IntegerField()
    
class EmployeeListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')  

    class Meta:
        model = Employee
        fields = ['id', 'username']  