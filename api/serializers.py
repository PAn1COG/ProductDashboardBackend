from rest_framework import serializers
from .models import Item, Category
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    # category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Item
        # SKU, name, category, tags, stock status, and available stock 
        fields = ('SKU', 'name', 'category', 'tags', 'stock_status', 'available_stock')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']