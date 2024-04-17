from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Unit, Equipment, Transaction, CartItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'uic']

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'nsn', 'lin', 'unit', 'serial_number', 'status', 'location']

class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    equipment = serializers.SlugRelatedField(queryset=Equipment.objects.all(), slug_field='name')
    
    class Meta:
        model = Transaction
        fields = ['user', 'equipment', 'checkout_date', 'return_date', 'status']

class CartItemSerializer(serializers.ModelSerializer):
    equipment_name = serializers.ReadOnlyField(source='equipment.name')
    equipment_id = serializers.ReadOnlyField(source='equipment.id')
    nsn = serializers.ReadOnlyField(source='equipment.nsn')
    status = serializers.ReadOnlyField(source='equipment.status')
    transaction = TransactionSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'equipment_id', 'equipment_name', 'nsn', 'status', 'quantity', 'transaction']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)
    cart_items = CartItemSerializer(many=True, read_only=True)  

    class Meta:
        model = UserProfile
        fields = ['user', 'rank', 'unit', 'cart_items']  

class UserRegistrationSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'profile')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    # Additional fields can be added if necessary

    # unit_id = serializers.IntegerField()
    # Alternatively, if you want to use UIC as a reference:
    # unit_uic = serializers.SlugRelatedField(slug_field='uic', queryset=Unit.objects.all(), source='unit', allow_null=True)        




