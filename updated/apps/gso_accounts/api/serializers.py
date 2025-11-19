from rest_framework import serializers
from ..models import User, Unit, Department, Position, EmploymentStatus

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']

class EmploymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentStatus
        fields = ['id', 'employment_status']

class UnitSerializer(serializers.ModelSerializer):
    unit_head = serializers.StringRelatedField()  # Show full name of the unit head
    class Meta:
        model = Unit
        fields = ['id', 'name', 'unit_head']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    position = PositionSerializer(read_only=True)
    employment_status = EmploymentStatusSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'account_status',
            'unit', 'department', 'position', 'employment_status'
        ]

class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password',
            'role', 'account_status',
            'unit', 'department', 'position', 'employment_status'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
