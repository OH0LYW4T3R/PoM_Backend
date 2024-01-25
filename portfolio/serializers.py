from .models import User, EnterpriseUser, Enterprise, Category, Portfolio
from rest_framework import serializers

class SummarySerializer(serializers.Serializer):
    topic = serializers.CharField()
    summary = serializers.CharField()
    thumb_nail_url = serializers.CharField()

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer(many=True, read_only=True, source="portfolio")

    class Meta:
        model = Category
        fields = ["id", "user_id", "category", "portfolio"]

class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class EnterpriseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    enterprise_visible = EnterpriseSerializer(many=True, read_only=True, source="enterprise_visible")
    category = CategorySerializer(many=True, read_only=True, source="category")

    class Meta:
        model = User
        fields = ["id", "name", "department", "enterprise_visible", "category"]