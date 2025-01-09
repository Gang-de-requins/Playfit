import django.contrib.auth.password_validation as validators
from rest_framework import serializers
from .models import *

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'username', 'password', 'date_of_birth', 'height', 'weight',
        ]

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            date_of_birth=validated_data['date_of_birth'],
            height=validated_data['height'],
            weight=validated_data['weight'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, value):
        user = CustomUser(
            email=value['email'],
            username=value['username'],
            date_of_birth=value['date_of_birth'],
            height=value['height'],
            weight=value['weight'],
        )
        password = value['password']
        errors = dict()
        try:
            validators.validate_password(password=password, user=user)
        except serializers.ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return value

class ProductSerializer(serializers.ModelSerializer):
    class Meta():
        model = Product
        fields = "__all__"