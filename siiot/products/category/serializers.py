from rest_framework import serializers, exceptions

from mypage.models import Accounts
from products.category.models import FirstCategory, SecondCategory, Size, Color, Bank
from products.models import Product


class FirstCategorySerializer(serializers.ModelSerializer):
    child = serializers.SerializerMethodField()

    class Meta:
        model = FirstCategory
        fields = ['id', 'name', 'child']

    def get_child(self, obj):
        if obj.second_categories.exists():
            return True
        return False


class SecondCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondCategory
        fields = ['name', 'id']


class SizeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Size
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.size_name


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'color', 'color_code']


class AccountsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Accounts
        fields = '__all__'


class BankListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'bank']


class CategorySearchSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = SecondCategory
        fields = ['id', 'name', 'count']

    def get_count(self, obj):
        count = Product.objects.filter(category=obj).count()
        return count
