from rest_framework import serializers
from .models import Leave
from datetime import timedelta 
from django.utils import timezone
from employee.models import Employee  

class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.username', read_only=True)

    class Meta:
        model = Leave
        fields = [
            'id', 
            'employee', 
            'employee_name',
            'start_date', 
            'end_date', 
            'reason', 
            'status', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'status', 'employee', 'created_at', 'updated_at']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date > end_date:
            raise serializers.ValidationError("End date must be after start date.")

        tomorrow = timezone.now().date() + timedelta(days=1)
        if start_date < tomorrow:
            raise serializers.ValidationError("Start date cannot be before tomorrow.")

        return data

class AuthorizedLeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.username', read_only=True)
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    class Meta:
        model = Leave
        fields = [
            'id', 
            'employee', 
            'employee_name',
            'start_date', 
            'end_date', 
            'reason', 
            'status', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date > end_date:
            raise serializers.ValidationError("End date must be after start date.")

        tomorrow = timezone.now().date() + timedelta(days=1)
        if start_date < tomorrow:
            raise serializers.ValidationError("Start date cannot be before tomorrow.")

        # Diğer validasyonlar serviste yapılıyor
        return data