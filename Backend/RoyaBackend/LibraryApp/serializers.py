from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Borrow

# Serializer for User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']  # Fields to include in the serialization
        extra_kwargs = {'password': {'write_only': True}}  # Password should not be readable

    def create(self, validated_data):
        """
        Create a new user with the provided validated data.
        This method uses the create_user method to ensure the password is hashed.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user

# Serializer for Book model
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'  # Serialize all fields of the Book model

# Serializer for Borrow model
class BorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['id', 'user', 'book', 'borrowed_date', 'returned_date']  # Specify fields to serialize
