from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "products_count")


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "category")


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "text", "stars", "product")

    def validate_stars(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("stars must be between 1 and 5")
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