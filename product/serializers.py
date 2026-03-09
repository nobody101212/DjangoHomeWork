from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        min_length=2,
        max_length=255,
        allow_blank=False,
        trim_whitespace=True,
        validators=[
            UniqueValidator(queryset=Category.objects.all(), message="Category with this name already exists.")
        ],
        error_messages={
            "blank": "name cannot be empty.",
            "min_length": "name is too short.",
            "max_length": "name is too long.",
        }
    )

    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "products_count")


class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        min_length=2,
        max_length=255,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={"blank": "title cannot be empty."}
    )
    description = serializers.CharField(
        min_length=3,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={"blank": "description cannot be empty."}
    )
    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        error_messages={"min_value": "price must be greater than 0."}
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages={"does_not_exist": "category not found.", "incorrect_type": "category must be an integer id."}
    )

    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "category")

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("title cannot be empty.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    text = serializers.CharField(
        min_length=3,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={"blank": "text cannot be empty."}
    )
    stars = serializers.IntegerField(
        min_value=1,
        max_value=5,
        error_messages={
            "min_value": "stars must be between 1 and 5.",
            "max_value": "stars must be between 1 and 5.",
        }
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        error_messages={"does_not_exist": "product not found.", "incorrect_type": "product must be an integer id."}
    )

    class Meta:
        model = Review
        fields = ("id", "text", "stars", "product")

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("text cannot be empty.")
        return value


class ReviewNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "text", "stars")


class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewNestedSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "category", "rating", "reviews")