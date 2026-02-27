from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CustomerAdminSerializer(serializers.ModelSerializer):
    orders_count = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    last_order = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "first_name", "last_name", "email",
            "orders_count", "total_spent", "last_order",
        ]