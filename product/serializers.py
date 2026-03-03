from rest_framework import serializers
from .models import Category, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "products_count")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "category", "category_name")


class ReviewSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "text", "stars", "product", "product_title")


class ReviewNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "text", "stars")


class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewNestedSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "category", "category_name", "rating", "reviews")

    def get_rating(self, obj):
        val = getattr(obj, "rating", None)
        return round(float(val), 2) if val is not None else 0